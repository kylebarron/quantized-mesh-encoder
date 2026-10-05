from io import BytesIO
from numbers import Number
from struct import calcsize, unpack

import numpy as np
import pytest
from quantized_mesh_tile import TerrainTile

from quantized_mesh_encoder import WGS84, Ellipsoid, extensions
from quantized_mesh_encoder.ecef import to_ecef
from quantized_mesh_encoder.encode import (
    compute_header,
    encode,
    encode_header,
    find_edge_indices,
    interp_positions,
)
from quantized_mesh_encoder.normals import compute_vertex_normals


def test_compute_header():
    positions = np.array([0, 0, 0, 1, 1, 1, 0, 1, 4], dtype=np.float32).reshape(-1, 3)
    header = compute_header(positions, sphere_method=None)
    keys = [
        "centerX",
        "centerY",
        "centerZ",
        "minimumHeight",
        "maximumHeight",
        "boundingSphereCenterX",
        "boundingSphereCenterY",
        "boundingSphereCenterZ",
        "boundingSphereRadius",
        "horizonOcclusionPointX",
        "horizonOcclusionPointY",
        "horizonOcclusionPointZ",
    ]
    assert all(k in header for k in keys), "Header key missing"
    assert all(isinstance(v, Number) for v in header.values()), (
        "Header value not numeric"
    )


def test_encode_header():
    header = {
        "centerX": 6377169.5,
        "centerY": 55648.50390625,
        "centerZ": 55284.421875,
        "minimumHeight": 0.0,
        "maximumHeight": 4.0,
        "boundingSphereCenterX": 6377169.5,
        "boundingSphereCenterY": 55648.504,
        "boundingSphereCenterZ": 55284.42,
        "boundingSphereRadius": 78447.81,
        "horizonOcclusionPointX": 6378226.71931529,
        "horizonOcclusionPointY": 55657.731270568445,
        "horizonOcclusionPointZ": 55293.58686988714,
    }

    buf = BytesIO()
    encode_header(buf, header)
    buf.seek(0)
    b = buf.read()

    assert len(b) == 88, "Header incorrect number of bytes"


def test_encode_decode():

    positions = np.array(
        [0, 0, 0, 1, 1, 1, 0, 1, 4, 2, 3, 4, 8, 9, 10, 12, 13, 14], dtype=np.float32
    )
    triangles = np.array([0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5], dtype=np.uint32)
    cartesian_positions = to_ecef(positions.reshape(-1, 3))

    normals_ext = extensions.VertexNormalsExtension(
        positions=positions, indices=triangles
    )

    f = BytesIO()
    encode(f, positions, triangles, extensions=[normals_ext])

    f.seek(0)
    tile = TerrainTile()
    tile.fromBytesIO(f, hasLighting=True)

    assert np.array_equal(triangles, np.array(tile.indices, dtype=np.uint32)), (
        "Indices incorrect"
    )
    u, v, h = interp_positions(positions.reshape(-1, 3)).T

    assert np.array_equal(u, np.array(tile.u, dtype=np.uint32)), "Vertices incorrect"
    assert np.array_equal(v, np.array(tile.v, dtype=np.uint32)), "Vertices incorrect"
    assert np.array_equal(h, np.array(tile.h, dtype=np.uint32)), "Vertices incorrect"

    assert tile.westI == [0, 2]
    assert tile.southI == [0]
    assert tile.eastI == [5]
    assert tile.northI == [5]

    normals = compute_vertex_normals(cartesian_positions, triangles)

    # Can't test for exact equality with octencode/decode
    assert np.allclose(normals, tile.vLight, atol=0.01, rtol=0), (
        "VertexNormals incorrect"
    )


def test_encode_ellipsoid_numpy_scalars():
    """An Ellipsoid with numpy float64 axes encodes like one with Python floats.

    Under numpy 2's promotion rules (NEP 50), numpy scalars are no longer
    demoted to the array's dtype, so the ECEF positions come out as float64.
    """
    positions = np.array([0, 0, 0, 1, 1, 1, 0, 1, 4], dtype=np.float32)
    triangles = np.array([0, 1, 2], dtype=np.uint32)
    ellipsoid = Ellipsoid(np.float64(WGS84.a), np.float64(WGS84.b))

    expected = BytesIO()
    encode(expected, positions, triangles)

    f = BytesIO()
    encode(f, positions, triangles, ellipsoid=ellipsoid)

    # Header values may differ by float32 rounding; the rest must be identical
    header_format = "<3d2f4d3d"
    header_size = calcsize(header_format)
    assert np.allclose(
        unpack(header_format, f.getvalue()[:header_size]),
        unpack(header_format, expected.getvalue()[:header_size]),
    )
    assert f.getvalue()[header_size:] == expected.getvalue()[header_size:]


def test_vertex_normals_extension_index_dtype():
    """VertexNormalsExtension accepts any integer index dtype, like encode."""
    positions = np.array([0, 0, 0, 1, 1, 1, 0, 1, 4, 2, 3, 4], dtype=np.float32)
    triangles = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)

    expected = extensions.VertexNormalsExtension(
        positions=positions, indices=triangles
    ).encode()

    for dtype in [np.int32, np.int64, np.uint16]:
        ext = extensions.VertexNormalsExtension(
            positions=positions, indices=triangles.astype(dtype)
        )
        assert ext.encode() == expected, dtype


# Header (88 bytes) plus the vertex count (4 bytes)
VERTEX_DATA_OFFSET = 92


def triangle_strip(n_vertices: int) -> tuple[np.ndarray, np.ndarray]:
    """A mesh whose vertices appear in index order, as high-water marks need."""
    rng = np.random.default_rng(0)
    positions = np.column_stack(
        [
            rng.uniform(-122, -121, n_vertices),
            rng.uniform(37, 38, n_vertices),
            rng.uniform(0, 3000, n_vertices),
        ]
    ).astype(np.float32)
    first = np.arange(n_vertices - 2, dtype=np.uint32)
    triangles = np.column_stack([first, first + 1, first + 2])
    return positions, triangles


def encode_to_bytes(positions, indices, **kwargs: object) -> bytes:
    f = BytesIO()
    encode(f, positions, indices, **kwargs)
    return f.getvalue()


def test_encode_flat_and_2d_inputs_match():
    positions, triangles = triangle_strip(10)
    assert encode_to_bytes(positions, triangles) == encode_to_bytes(
        positions.flatten(), triangles.flatten()
    )


@pytest.mark.parametrize("sphere_method", [None, "bounding_box", "naive", "ritter"])
def test_encode_sphere_method(sphere_method):
    positions, triangles = triangle_strip(10)
    buf = encode_to_bytes(positions, triangles, sphere_method=sphere_method)

    tile = TerrainTile()
    tile.fromBytesIO(BytesIO(buf))
    center = [tile.header[f"boundingSphereCenter{axis}"] for axis in "XYZ"]
    radius = tile.header["boundingSphereRadius"]

    # Allow for float32 rounding of the ECEF positions
    cartesian_positions = to_ecef(positions)
    distances = np.linalg.norm(cartesian_positions - center, axis=1)
    assert (distances <= radius + 1).all()


def test_encode_rejects_non_ellipsoid():
    positions, triangles = triangle_strip(10)
    with pytest.raises(AssertionError):
        encode_to_bytes(positions, triangles, ellipsoid=(1, 1))


def test_encode_rejects_non_extension():
    positions, triangles = triangle_strip(10)
    with pytest.raises(AssertionError):
        encode_to_bytes(positions, triangles, extensions=[b"not an extension"])


def test_encode_rejects_duplicate_extensions():
    positions, triangles = triangle_strip(10)
    metadata = extensions.MetadataExtension(data={})
    with pytest.raises(AssertionError):
        encode_to_bytes(positions, triangles, extensions=[metadata, metadata])


def test_interp_positions():
    positions = np.array([[0, 10, 100], [5, 15, 150], [10, 20, 200]], np.float32)
    u, v, h = interp_positions(positions).T
    assert u.tolist() == [0, 16383, 32767]
    assert v.tolist() == [0, 16383, 32767]
    assert h.tolist() == [0, 16383, 32767]


def test_interp_positions_bounds():
    positions = np.array([[0, 10, 100], [5, 15, 150], [10, 20, 200]], np.float32)
    u, v, h = interp_positions(positions, bounds=(-10, 10, 10, 30)).T
    assert u.tolist() == [16383, 24575, 32767]
    assert v.tolist() == [0, 8191, 16383]
    # Heights always span their own range
    assert h.tolist() == [0, 16383, 32767]


def test_find_edge_indices():
    positions = np.array(
        [[0, 0, 0], [32767, 0, 0], [0, 32767, 0], [32767, 32767, 0], [5, 5, 0]],
        dtype=np.int16,
    )
    west, south, east, north = find_edge_indices(positions)
    assert west.tolist() == [0, 2]
    assert south.tolist() == [0, 1]
    assert east.tolist() == [1, 3]
    assert north.tolist() == [2, 3]


def test_encode_decode_32bit_indices():
    """Meshes with more than 65536 vertices use 32-bit indices."""
    positions, triangles = triangle_strip(70_000)
    buf = encode_to_bytes(positions, triangles)

    tile = TerrainTile()
    tile.fromBytesIO(BytesIO(buf))
    assert np.array_equal(np.array(tile.indices), triangles.flatten())

    u, v, _ = interp_positions(positions).T
    assert tile.westI == np.nonzero(u == 0)[0].tolist()
    assert tile.northI == np.nonzero(v == 32767)[0].tolist()


@pytest.mark.parametrize(
    ("n_vertices", "alignment"),
    [(10, 2), (11, 2), (70_000, 4), (70_001, 4)],
)
def test_encode_index_alignment(n_vertices, alignment):
    """Index data is padded to 2-byte (16-bit) or 4-byte (32-bit) alignment."""
    positions, triangles = triangle_strip(n_vertices)
    buf = encode_to_bytes(positions, triangles)

    # The vertex data has 3 uint16 values per vertex
    end_of_vertices = VERTEX_DATA_OFFSET + 6 * n_vertices
    offset = -(-end_of_vertices // alignment) * alignment
    (triangle_count,) = unpack("<I", buf[offset : offset + 4])
    assert triangle_count == len(triangles)


def test_encode_decode_water_mask():
    positions, triangles = triangle_strip(10)
    mask = np.zeros((256, 256), dtype=np.uint8)
    mask[:, :128] = 255
    exts = [
        extensions.VertexNormalsExtension(positions=positions, indices=triangles),
        extensions.WaterMaskExtension(data=mask),
    ]
    buf = encode_to_bytes(positions, triangles, extensions=exts)

    tile = TerrainTile()
    tile.fromBytesIO(BytesIO(buf), hasLighting=True, hasWatermask=True)
    assert np.array_equal(np.array(tile.watermask), mask)
