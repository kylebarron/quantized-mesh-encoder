import numpy as np


def zig_zag_encode(arr):
    """
    Input can be number or numpy array

    https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba
    (i >> bitlength-1) ^ (i << 1)
    So I right shift 15 because these arrays are int16

    Note: since I'm only right-shifting 15 places, this will fail for values >
    int16
    """
    return np.bitwise_xor(np.right_shift(arr, 15), np.left_shift(arr, 1))
