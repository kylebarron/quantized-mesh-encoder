import gzip
import io
from struct import pack
import numpy as np

# from . import cartesian3d as c3d

EPSILON6 = 0.000001


def pack_entry(fmt, value):
    return pack(fmt, value)


def zig_zag_encode(arr):
    """
    Input can be number or numpy array

    https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba
    (i >> bitlength-1) ^ (i << 1)
    So I right shift 15 because these arrays are int16
    """
    return np.bitwise_xor(np.right_shift(arr, 15), np.left_shift(arr, 1))
