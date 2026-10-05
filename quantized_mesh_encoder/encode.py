"""Encode a mesh into the Quantized Mesh format."""

from __future__ import annotations

from struct import pack
from typing import TYPE_CHECKING, Any, BinaryIO

import numpy as np

from .bounding_sphere import bounding_sphere
from .constants import HEADER, NP_STRUCT_TYPES, VERTEX_DATA, WGS84
from .ecef import to_ecef
from .ellipsoid import Ellipsoid
from .extensions import ExtensionBase
from .occlusion import occlusion_point
from .util import zig_zag_encode
from .util_cy import encode_indices

if TYPE_CHECKING:
    from collections.abc import Sequence

Bounds = tuple[float, float, float, float]

# Quantized vertex coordinates range from 0 to this value
_MAX_QUANTIZED = 32767

# Meshes with more vertices than this must use 32-bit indices
_MAX_INDEX16_VERTICES = 65536


def encode(  # noqa: PLR0913
    f: BinaryIO,
    positions: np.ndarray,
    indices: np.ndarray,
    *,
    bounds: Bounds | None = None,
    sphere_method: str | None = None,
    ellipsoid: Ellipsoid = WGS84,
    extensions: Sequence[ExtensionBase] = (),
) -> None:
    """Encode a mesh into Quantized Mesh and write it to a file.

    Args:
        f: A writable file-like object in which to write encoded bytes.
        positions: Either a 1D Numpy array or a 2D Numpy array of shape (-1, 3)
            containing 3D positions.
        indices: Either a 1D Numpy array or a 2D Numpy array of shape (-1, 3)
            indicating triples of coordinates from `positions` to make
            triangles. For example, if the first three values of `indices` are
            `0`, `1`, `2`, then that defines a triangle formed by the first 9
            values in `positions`, three for the first vertex (index `0`),
            three for the second vertex, and three for the third vertex.

    Keyword Args:
        bounds: A list of bounds, `[minx, miny, maxx, maxy]`. By default,
            inferred as the minimum and maximum values of `positions`.
        sphere_method: A string designating the algorithm to use for creating
            the bounding sphere. Must be one of `'bounding_box'`, `'naive'`,
            `'ritter'` or `None`. See
            `quantized_mesh_encoder.bounding_sphere.bounding_sphere` for a
            description of each.
        ellipsoid: Ellipsoid defined by its semi-major `a` and semi-minor `b`
            axes. Default: WGS84 ellipsoid.
        extensions: A sequence of extension instances to encode after the mesh.

    """
    # Convert to ndarray
    positions = positions.reshape(-1, 3).astype(np.float32)
    indices = indices.reshape(-1, 3).astype(np.uint32)

    # Public API raises AssertionError; keep it for backwards compatibility
    msg = "ellipsoid must be an instance of the Ellipsoid class."
    assert isinstance(ellipsoid, Ellipsoid), msg  # noqa: S101

    msg = "extensions must be instances of the Extension class."
    assert all(isinstance(ext, ExtensionBase) for ext in extensions), msg  # noqa: S101

    msg = "extensions must have unique ids."
    assert len({ext.id for ext in extensions}) == len(extensions), msg  # noqa: S101

    header = compute_header(positions, sphere_method, ellipsoid=ellipsoid)
    encode_header(f, header)

    # Linear interpolation to range u, v, h from 0-32767
    positions = interp_positions(positions, bounds=bounds)

    n_vertices = positions.shape[0]
    write_vertices(f, positions, n_vertices)

    write_indices(f, indices, n_vertices)

    write_edge_indices(f, positions, n_vertices)

    # Only require a `write` method on `f`, not `writelines`
    for ext in extensions:  # noqa: FURB122
        f.write(ext.encode())


def compute_header(
    positions: np.ndarray, sphere_method: str | None, *, ellipsoid: Ellipsoid = WGS84
) -> dict[str, Any]:
    """Compute the Quantized Mesh header.

    Args:
        positions: An array of shape (-1, 3) of longitude, latitude, height
            positions.
        sphere_method: The bounding sphere algorithm. See
            `quantized_mesh_encoder.bounding_sphere.bounding_sphere`.

    Keyword Args:
        ellipsoid: Ellipsoid used to convert positions to ECEF coordinates.

    Returns:
        A dict of header values, keyed by the field names in the spec.

    """
    header = {}

    cartesian_positions = to_ecef(positions, ellipsoid=ellipsoid)

    ecef_min_x = cartesian_positions[:, 0].min()
    ecef_min_y = cartesian_positions[:, 1].min()
    ecef_min_z = cartesian_positions[:, 2].min()
    ecef_max_x = cartesian_positions[:, 0].max()
    ecef_max_y = cartesian_positions[:, 1].max()
    ecef_max_z = cartesian_positions[:, 2].max()

    header["centerX"] = (ecef_min_x + ecef_max_x) / 2
    header["centerY"] = (ecef_min_y + ecef_max_y) / 2
    header["centerZ"] = (ecef_min_z + ecef_max_z) / 2

    header["minimumHeight"] = positions[:, 2].min()
    header["maximumHeight"] = positions[:, 2].max()

    center, radius = bounding_sphere(cartesian_positions, method=sphere_method)
    header["boundingSphereCenterX"] = center[0]
    header["boundingSphereCenterY"] = center[1]
    header["boundingSphereCenterZ"] = center[2]
    header["boundingSphereRadius"] = radius

    occl_pt = occlusion_point(cartesian_positions, center, ellipsoid=ellipsoid)
    header["horizonOcclusionPointX"] = occl_pt[0]
    header["horizonOcclusionPointY"] = occl_pt[1]
    header["horizonOcclusionPointZ"] = occl_pt[2]

    return header


def encode_header(f: BinaryIO, data: dict[str, Any]) -> None:
    """Encode header data.

    Args:
        f: Opened file descriptor for writing.
        data: Dict of header data, as returned by `compute_header`.

    """
    f.write(pack(HEADER["centerX"], data["centerX"]))
    f.write(pack(HEADER["centerY"], data["centerY"]))
    f.write(pack(HEADER["centerZ"], data["centerZ"]))

    f.write(pack(HEADER["minimumHeight"], data["minimumHeight"]))
    f.write(pack(HEADER["maximumHeight"], data["maximumHeight"]))

    f.write(pack(HEADER["boundingSphereCenterX"], data["boundingSphereCenterX"]))
    f.write(pack(HEADER["boundingSphereCenterY"], data["boundingSphereCenterY"]))
    f.write(pack(HEADER["boundingSphereCenterZ"], data["boundingSphereCenterZ"]))
    f.write(pack(HEADER["boundingSphereRadius"], data["boundingSphereRadius"]))

    f.write(pack(HEADER["horizonOcclusionPointX"], data["horizonOcclusionPointX"]))
    f.write(pack(HEADER["horizonOcclusionPointY"], data["horizonOcclusionPointY"]))
    f.write(pack(HEADER["horizonOcclusionPointZ"], data["horizonOcclusionPointZ"]))


def interp_positions(positions: np.ndarray, bounds: Bounds | None = None) -> np.ndarray:
    """Rescale positions to be integers ranging from 0 to 32767.

    Args:
        positions: An array of shape (-1, 3) of 3D positions.
        bounds: If provided should be `[minx, miny, maxx, maxy]`. Heights are
            always rescaled from their minimum to their maximum.

    Returns:
        An array of shape (-1, 3) and dtype np.int16.

    """
    if bounds:
        minx, miny, maxx, maxy = bounds
    else:
        minx = positions[:, 0].min()
        maxx = positions[:, 0].max()
        miny = positions[:, 1].min()
        maxy = positions[:, 1].max()

    minh = positions[:, 2].min()
    maxh = positions[:, 2].max()

    u = np.interp(positions[:, 0], (minx, maxx), (0, _MAX_QUANTIZED)).astype(np.int16)
    v = np.interp(positions[:, 1], (miny, maxy), (0, _MAX_QUANTIZED)).astype(np.int16)
    h = np.interp(positions[:, 2], (minh, maxh), (0, _MAX_QUANTIZED)).astype(np.int16)

    return np.vstack([u, v, h]).T


def write_vertices(f: BinaryIO, positions: np.ndarray, n_vertices: int) -> None:
    """Write the vertex count and zig-zag delta encoded vertex data.

    Args:
        f: Opened file descriptor for writing.
        positions: Quantized positions, as returned by `interp_positions`.
        n_vertices: Number of vertices.

    """
    assert positions.ndim == 2, "positions must be 2 dimensions"  # noqa: PLR2004, S101

    # Write vertex count
    f.write(pack(VERTEX_DATA["vertexCount"], n_vertices))

    u = positions[:, 0]
    v = positions[:, 1]
    h = positions[:, 2]

    u_diff = u[1:] - u[:-1]
    v_diff = v[1:] - v[:-1]
    h_diff = h[1:] - h[:-1]

    # Zig zag encode
    u_zz = zig_zag_encode(u_diff).astype(np.uint16)
    v_zz = zig_zag_encode(v_diff).astype(np.uint16)
    h_zz = zig_zag_encode(h_diff).astype(np.uint16)

    # Write first value
    f.write(pack(VERTEX_DATA["uVertexCount"], zig_zag_encode(u[0])))
    # Write array. Must be uint16
    f.write(u_zz.tobytes())

    # Write first value
    f.write(pack(VERTEX_DATA["vVertexCount"], zig_zag_encode(v[0])))
    # Write array. Must be uint16
    f.write(v_zz.tobytes())

    # Write first value
    f.write(pack(VERTEX_DATA["heightVertexCount"], zig_zag_encode(h[0])))
    # Write array. Must be uint16
    f.write(h_zz.tobytes())


def write_indices(f: BinaryIO, indices: np.ndarray, n_vertices: int) -> None:
    """Write high-water mark encoded triangle indices.

    Args:
        f: Opened file descriptor for writing.
        indices: An array of shape (-1, 3) of triangle indices.
        n_vertices: Number of vertices, which determines the index size.

    """
    # If more than 65536 vertices, index data must be uint32
    index_32 = n_vertices > _MAX_INDEX16_VERTICES

    # Enforce proper byte alignment
    # > padding is added before the IndexData to ensure 2 byte alignment for
    # > IndexData16 and 4 byte alignment for IndexData32.
    required_offset = 4 if index_32 else 2
    remainder = f.tell() % required_offset
    if remainder:
        # number of bytes to add
        n_bytes = required_offset - remainder
        # Write required number of bytes
        # Not sure the best way to write empty bytes, so I'll just pad with
        # ascii letters for now
        b = ("a" * n_bytes).encode("ascii")
        assert len(b) == n_bytes, "Wrong number of bytes to pad"  # noqa: S101
        f.write(b)

    # Write number of triangles to file
    n_triangles = indices.shape[0]
    f.write(pack(NP_STRUCT_TYPES[np.uint32], n_triangles))

    # Encode indices using high water mark encoding
    encoded_ind = encode_indices(indices.flatten())

    # Write array. Must be either uint16 or uint32, depending on length of
    # vertices
    dtype = np.uint32 if index_32 else np.uint16
    encoded_ind = encoded_ind.astype(dtype)
    f.write(encoded_ind.tobytes())


def find_edge_indices(
    positions: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Find the indices of vertices on each edge of the tile.

    Args:
        positions: Quantized positions, as returned by `interp_positions`.

    Returns:
        A tuple of the indices of vertices on the west, south, east and north
        edges.

    """
    u = positions[:, 0]
    v = positions[:, 1]

    # np.where returns a tuple for each dimension
    # Here we only care about the first
    left = np.where(u == 0)[0]
    bottom = np.where(v == 0)[0]
    right = np.where(u == _MAX_QUANTIZED)[0]
    top = np.where(v == _MAX_QUANTIZED)[0]

    return left, bottom, right, top


def write_edge_indices(f: BinaryIO, positions: np.ndarray, n_vertices: int) -> None:
    """Write the indices of vertices on each edge of the tile.

    Args:
        f: Opened file descriptor for writing.
        positions: Quantized positions, as returned by `interp_positions`.
        n_vertices: Number of vertices, which determines the index size.

    """
    left, bottom, right, top = find_edge_indices(positions)

    # If more than 65536 vertices, index data must be uint32
    index_32 = n_vertices > _MAX_INDEX16_VERTICES
    dtype = np.uint32 if index_32 else np.uint16

    # No high-water mark encoding on edge indices
    left = left.astype(dtype)
    bottom = bottom.astype(dtype)
    right = right.astype(dtype)
    top = top.astype(dtype)

    f.write(pack(NP_STRUCT_TYPES[np.uint32], len(left)))
    f.write(left.tobytes())

    f.write(pack(NP_STRUCT_TYPES[np.uint32], len(bottom)))
    f.write(bottom.tobytes())

    f.write(pack(NP_STRUCT_TYPES[np.uint32], len(right)))
    f.write(right.tobytes())

    f.write(pack(NP_STRUCT_TYPES[np.uint32], len(top)))
    f.write(top.tobytes())
