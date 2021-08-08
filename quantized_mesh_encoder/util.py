from typing import Union

import numpy as np


def zig_zag_encode(
    arr: Union[np.ndarray, int, np.number]
) -> Union[np.ndarray, np.uint16]:
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

    encoded = np.bitwise_xor(np.right_shift(arr, 15), np.left_shift(arr, 1))
    return encoded.astype(np.uint16)
