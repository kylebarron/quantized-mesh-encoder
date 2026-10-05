import numpy as np
import pytest
from quantized_mesh_tile.utils import octDecode, octEncode

from quantized_mesh_encoder.normals import compute_vertex_normals, oct_encode

AXES = [
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
]


@pytest.mark.parametrize("vec", AXES)
def test_oct_encode_axes(vec):
    """Unit vectors along each axis survive an encode/decode round trip."""
    encoded = oct_encode(np.array([vec], dtype=np.float64))
    decoded = octDecode(*encoded[0].tolist())
    assert np.allclose(decoded, vec, atol=0.01)


def test_oct_encode_matches_reference():
    """Matches the reference encoder in quantized-mesh-tile (ported from Cesium)."""
    rng = np.random.default_rng(0)
    vecs = rng.normal(size=(1000, 3))
    vecs /= np.linalg.norm(vecs, axis=1)[:, np.newaxis]

    expected = np.array([octEncode(vec.tolist()) for vec in vecs], dtype=np.uint8)
    assert np.array_equal(oct_encode(vecs), expected)


def test_compute_vertex_normals_flat():
    """A counterclockwise triangle in the xy plane has normals along +z."""
    positions = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float64)
    indices = np.array([[0, 1, 2]], dtype=np.uint32)
    normals = compute_vertex_normals(positions, indices)
    assert np.allclose(normals, [[0, 0, 1]] * 3)


def test_compute_vertex_normals_area_weighted():
    """Normals of shared vertices weight each face by its area."""
    # Two triangles sharing the edge from vertex 0 to vertex 1: a large one in
    # the xy plane (+z normal) and a small one in the xz plane (+y normal)
    positions = np.array(
        [[0, 0, 0], [1, 0, 0], [0, 10, 0], [0, 0, 1]], dtype=np.float64
    )
    indices = np.array([[0, 1, 2], [0, 3, 1]], dtype=np.uint32)
    normals = compute_vertex_normals(positions, indices)

    # Face normals are (0, 0, 10) and (0, 1, 0), each scaled by area (5, 0.5)
    expected = np.array([0, 0.5, 50]) / np.linalg.norm([0, 0.5, 50])
    assert np.allclose(normals[0], expected)
    assert np.allclose(normals[1], expected)
    assert np.allclose(normals[2], [0, 0, 1])
    assert np.allclose(normals[3], [0, 1, 0])
