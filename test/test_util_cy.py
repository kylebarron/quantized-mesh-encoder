import numpy as np
import pytest

from quantized_mesh_encoder.util_cy import encode_indices


# From quantized_mesh_tile.utils
def decode_indices(indices):
    out = []
    highest = 0
    for i in indices:
        out.append(highest - i)
        if i == 0:
            highest += 1
    return out


ENCODE_INDICES_CASES = [[0, 1, 2, 1, 2, 3, 3, 4, 5, 2, 3, 4]]


@pytest.mark.parametrize("indices", ENCODE_INDICES_CASES)
def test_encode_indices(indices):
    arr = np.array(indices, dtype=np.uint32)
    out = decode_indices(encode_indices(arr))
    assert indices == out, 'Incorrect index encoding'
