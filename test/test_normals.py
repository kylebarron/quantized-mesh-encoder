import numpy as np
import pytest
from quantized_mesh_tile.utils import octDecode, octEncode

from quantized_mesh_encoder.normals import oct_encode

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
