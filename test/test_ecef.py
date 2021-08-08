import numpy as np
import pytest

from quantized_mesh_encoder.ecef import to_ecef

# Conversion reference
# http://www.oc.nps.edu/oc2902w/coord/llhxyz.htm

# Test cases taken from
# https://github.com/loicgasser/quantized-mesh-tile/blob/master/tests/test_llh_ecef.py
# Compare against rounded integers
TO_ECEF_TEST_CASES = [
    ([0, 0, 0], [6378137, 0, 0]),
    ([7.43861, 46.951103, 552], [4325328, 564726.2, 4638459]),
    ([7.81512, 46.30447, 635.0], [4373351, 600250.4, 4589151]),
    ([7.81471, 46.306686, 635.0], [4373179, 600194.8, 4589321]),
]


@pytest.mark.parametrize("llh_positions,exp_positions", TO_ECEF_TEST_CASES)
def test_to_ecef(llh_positions, exp_positions):
    arr = np.array(llh_positions, dtype=np.float32).reshape(-1, 3)
    cart_positions = to_ecef(arr)

    assert np.isclose(round(cart_positions[0, 0], 1), exp_positions[0])
    assert np.isclose(round(cart_positions[0, 1], 1), exp_positions[1])
    assert np.isclose(round(cart_positions[0, 2], 1), exp_positions[2])
