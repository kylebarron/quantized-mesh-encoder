from typing import Union

import numpy as np


def zig_zag_encode(arr: Union[np.ndarray, int]) -> Union[np.ndarray, int]:
    """
    Input can be number or numpy array

    https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba
    (i >> bitlength-1) ^ (i << 1)
    So I right shift 15 because these arrays are int16

    Note: since I'm only right-shifting 15 places, this will fail for values >
    int16
    """
    if isinstance(arr, np.ndarray):
        assert arr.dtype == np.int16, 'zig zag encoding requires int16 input'

    return np.bitwise_xor(np.right_shift(arr, 15), np.left_shift(arr, 1))
