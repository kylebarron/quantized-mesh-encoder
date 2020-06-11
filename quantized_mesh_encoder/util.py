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


def is_ccw(positions, indices):
    """For each triangle, determine if in counter-clockwise winding order

    Implements algorithm from here:
    https://stackoverflow.com/a/1165943

    NOTE: this algorithm is reversed if the origin is the top left (i.e. as in a
    PNG), rather than the standard origin of the bottom left.

    Args:
        positions: numpy array of shape (-1, 3) defining positions. Each row is a single coordinate
        indices: numpy array either flat or of shape (-1, 3) defining triangles

    Returns:
        1d numpy array where each value represents a single triangle formed by a
        triple within `indices`. The value is `True` if the triangle is
        counter-clockwise or `False` if clockwise.
    """
    # Make sure indices
    indices = indices.reshape(-1, 3)

    # Perform coordinate lookup in positions using indices
    # `coords` is then an array of shape (-1, 3, 3) where each block of (i, 3,
    # 3) represents all the coordinates of a single triangle
    coords = positions[indices]

    # x2 - x1 for every edge of every triangle
    x2x1 = np.roll(coords[:, :, 0], -1, axis=1) - coords[:, :, 0]

    # y2 + y1 for every edge of every triangle
    y2y1 = np.roll(coords[:, :, 1], -1, axis=1) + coords[:, :, 1]

    # Sum edge weights for each triangle
    axissum = (x2x1 * y2y1).sum(axis=1)

    # Values <0 represent counter-clockwise triangles
    return axissum < 0
