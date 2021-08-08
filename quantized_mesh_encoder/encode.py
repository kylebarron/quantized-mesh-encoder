from struct import pack
from typing import Any, BinaryIO, Dict, Optional, Sequence, Tuple

import numpy as np

from .bounding_sphere import bounding_sphere
from .constants import HEADER, NP_STRUCT_TYPES, VERTEX_DATA, WGS84
from .ecef import to_ecef
from .ellipsoid import Ellipsoid
from .extensions import ExtensionBase
from .occlusion import occlusion_point
from .util import zig_zag_encode
from .util_cy import encode_indices

Bounds = Tuple[float, float, float, float]


def encode(
    f: BinaryIO,
    positions: np.ndarray,
    indices: np.ndarray,
    *,
    bounds: Optional[Bounds] = None,
    sphere_method: Optional[str] = None,
    ellipsoid: Ellipsoid = WGS84,
    extensions: Sequence[ExtensionBase] = ()
) -> None:
    """Create bounding sphere from positions

    Args:
        - f: a writable file-like object in which to write encoded bytes
        - positions: (ndarray[float]): either a 1D Numpy array or a 2D Numpy
          array of shape (-1, 3) containing 3D positions.
        - indices (ndarray[int]): either a 1D Numpy array or a 2D Numpy array of
          shape (-1, 3) indicating triples of coordinates from `positions` to
          make triangles. For example, if the first three values of `indices`
          are `0`, `1`, `2`, then that defines a triangle formed by the first 9
          values in `positions`, three for the first vertex (index `0`), three
          for the second vertex, and three for the third vertex.

    Kwargs:
        - bounds (List[float], optional): a list of bounds, `[minx, miny, maxx,
          maxy]`. By default, inferred as the minimum and maximum values of
          `positions`.
        - sphere_method: a string designating the algorithm to use for creating
          the bounding sphere. Must be one of `'bounding_box'`, `'naive'`,
          `'ritter'` or `None`.

          - bounding_box: Finds the bounding box of all positions, then defines
            the center of the sphere as the center of the bounding box, and
            defines the radius as the distance back to the corner. This method
            produces the largest bounding sphere, but is the fastest: roughly 70
            µs on my computer.
          - naive: Finds the bounding box of all positions, then defines the
            center of the sphere as the center of the bounding box. It then
            checks the distance to every other point and defines the radius as
            the maximum of these distances. This method will produce a slightly
            smaller bounding sphere than the `bounding_box` method when points
            are not in the 3D corners. This is the next fastest at roughly 160
            µs on my computer.
          - ritter: Implements the Ritter Method for bounding spheres. It first
            finds the center of the longest span, then checks every point for
            containment, enlarging the sphere if necessary. This _can_ produce
            smaller bounding spheres than the naive method, but it does not
            always, so often both are run, see next option. This is the slowest
            method, at roughly 300 µs on my computer.
          - None: Runs both the naive and the ritter methods, then returns the
            smaller of the two. Since this runs both algorithms, it takes around
            500 µs on my computer
        - ellipsoid: (`Ellipsoid`): ellipsoid defined by its semi-major `a`
          and semi-minor `b` axes. Default: WGS84 ellipsoid.
        - extensions: list of instances of the ExtensionBase class.
    """
    # Convert to ndarray
    positions = positions.reshape(-1, 3).astype(np.float32)
    indices = indices.reshape(-1, 3).astype(np.uint32)

    msg = 'ellipsoid must be an instance of the Ellipsoid class.'
    assert isinstance(ellipsoid, Ellipsoid), msg

    msg = 'extensions must be instances of the Extension class.'
    assert all(isinstance(ext, ExtensionBase) for ext in extensions), msg

    msg = 'extensions must have unique ids.'
    assert len({ext.id for ext in extensions}) == len(extensions), msg

    header = compute_header(positions, sphere_method, ellipsoid=ellipsoid)
    encode_header(f, header)

    # Linear interpolation to range u, v, h from 0-32767
    positions = interp_positions(positions, bounds=bounds)

    n_vertices = positions.shape[0]
    write_vertices(f, positions, n_vertices)

    write_indices(f, indices, n_vertices)

    write_edge_indices(f, positions, n_vertices)

    for ext in extensions:
        f.write(ext.encode())


def compute_header(
    positions: np.ndarray, sphere_method: Optional[str], *, ellipsoid: Ellipsoid = WGS84
) -> Dict[str, Any]:
    header = {}

    cartesian_positions = to_ecef(positions, ellipsoid=ellipsoid)

    ecef_min_x = cartesian_positions[:, 0].min()
    ecef_min_y = cartesian_positions[:, 1].min()
    ecef_min_z = cartesian_positions[:, 2].min()
    ecef_max_x = cartesian_positions[:, 0].max()
    ecef_max_y = cartesian_positions[:, 1].max()
    ecef_max_z = cartesian_positions[:, 2].max()

    header['centerX'] = (ecef_min_x + ecef_max_x) / 2
    header['centerY'] = (ecef_min_y + ecef_max_y) / 2
    header['centerZ'] = (ecef_min_z + ecef_max_z) / 2

    header['minimumHeight'] = positions[:, 2].min()
    header['maximumHeight'] = positions[:, 2].max()

    center, radius = bounding_sphere(cartesian_positions, method=sphere_method)
    header['boundingSphereCenterX'] = center[0]
    header['boundingSphereCenterY'] = center[1]
    header['boundingSphereCenterZ'] = center[2]
    header['boundingSphereRadius'] = radius

    occl_pt = occlusion_point(cartesian_positions, center, ellipsoid=ellipsoid)
    header['horizonOcclusionPointX'] = occl_pt[0]
    header['horizonOcclusionPointY'] = occl_pt[1]
    header['horizonOcclusionPointZ'] = occl_pt[2]

    return header


def encode_header(f: BinaryIO, data: Dict[str, Any]) -> None:
    """Encode header data

    Args:
        - f: Opened file descriptor for writing
        - data: dict of header data
    """
    f.write(pack(HEADER['centerX'], data['centerX']))
    f.write(pack(HEADER['centerY'], data['centerY']))
    f.write(pack(HEADER['centerZ'], data['centerZ']))

    f.write(pack(HEADER['minimumHeight'], data['minimumHeight']))
    f.write(pack(HEADER['maximumHeight'], data['maximumHeight']))

    f.write(pack(HEADER['boundingSphereCenterX'], data['boundingSphereCenterX']))
    f.write(pack(HEADER['boundingSphereCenterY'], data['boundingSphereCenterY']))
    f.write(pack(HEADER['boundingSphereCenterZ'], data['boundingSphereCenterZ']))
    f.write(pack(HEADER['boundingSphereRadius'], data['boundingSphereRadius']))

    f.write(pack(HEADER['horizonOcclusionPointX'], data['horizonOcclusionPointX']))
    f.write(pack(HEADER['horizonOcclusionPointY'], data['horizonOcclusionPointY']))
    f.write(pack(HEADER['horizonOcclusionPointZ'], data['horizonOcclusionPointZ']))


def interp_positions(
    positions: np.ndarray, bounds: Optional[Bounds] = None
) -> np.ndarray:
    """Rescale positions to be integers ranging from min to max

    TODO allow 6 input elements, for min/max elevation too?

    Args:
        - positions
        - bounds: If provided should be [minx, miny, maxx, maxy]

    Returns:
        ndarray of shape (-1, 3) and dtype np.int16
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

    u = np.interp(positions[:, 0], (minx, maxx), (0, 32767)).astype(np.int16)
    v = np.interp(positions[:, 1], (miny, maxy), (0, 32767)).astype(np.int16)
    h = np.interp(positions[:, 2], (minh, maxh), (0, 32767)).astype(np.int16)

    return np.vstack([u, v, h]).T


def write_vertices(f: BinaryIO, positions: np.ndarray, n_vertices: int) -> None:
    assert positions.ndim == 2, 'positions must be 2 dimensions'

    # Write vertex count
    f.write(pack(VERTEX_DATA['vertexCount'], n_vertices))

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
    f.write(pack(VERTEX_DATA['uVertexCount'], zig_zag_encode(u[0])))
    # Write array. Must be uint16
    f.write(u_zz.tobytes())

    # Write first value
    f.write(pack(VERTEX_DATA['vVertexCount'], zig_zag_encode(v[0])))
    # Write array. Must be uint16
    f.write(v_zz.tobytes())

    # Write first value
    f.write(pack(VERTEX_DATA['heightVertexCount'], zig_zag_encode(h[0])))
    # Write array. Must be uint16
    f.write(h_zz.tobytes())


def write_indices(f: BinaryIO, indices: np.ndarray, n_vertices: int) -> None:
    """Write indices to file"""
    # If more than 65536 vertices, index data must be uint32
    index_32 = n_vertices > 65536

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
        b = ('a' * n_bytes).encode('ascii')
        assert len(b) == n_bytes, 'Wrong number of bytes to pad'
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
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    u = positions[:, 0]
    v = positions[:, 1]

    # np.where returns a tuple for each dimension
    # Here we only care about the first
    left = np.where(u == 0)[0]
    bottom = np.where(v == 0)[0]
    right = np.where(u == 32767)[0]
    top = np.where(v == 32767)[0]

    return left, bottom, right, top


def write_edge_indices(f: BinaryIO, positions: np.ndarray, n_vertices: int) -> None:
    left, bottom, right, top = find_edge_indices(positions)

    # If more than 65536 vertices, index data must be uint32
    index_32 = n_vertices > 65536
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
