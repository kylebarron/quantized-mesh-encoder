import numpy as np
import pytest

from quantized_mesh_encoder.util import zig_zag_encode

ZIG_ZAG_ENCODE_TEST_CASES = [
    (-1, 1),
    (-2, 3),
    (0, 0),
    (1, 2),
    (2, 4),
    (np.array([-1, -2], dtype=np.int16), np.array([1, 3], dtype=np.int16)),
]


@pytest.mark.parametrize("value,expected", ZIG_ZAG_ENCODE_TEST_CASES)
def test_zig_zag_encode(value, expected):
    if isinstance(value, np.ndarray) or isinstance(expected, np.ndarray):
        assert np.array_equal(zig_zag_encode(value), expected)
    else:
        assert zig_zag_encode(value) == expected
