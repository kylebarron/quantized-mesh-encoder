"""Zig-zag encoding."""

from __future__ import annotations

import numpy as np


def zig_zag_encode(
    arr: np.ndarray | int | np.number,
) -> np.ndarray | np.uint16:
    """Zig-zag encode a number or numpy array.

    https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba
    `(i >> bitlength-1) ^ (i << 1)`.
    So I right shift 15 because these arrays are int16.

    Note: since I'm only right-shifting 15 places, this will fail for values >
    int16.

    Args:
        arr: An int16 numpy array, or a single integer.

    Returns:
        The zig-zag encoded value(s), as uint16.

    """
    if isinstance(arr, np.ndarray):
        # Public API raises AssertionError; keep it for backwards compatibility
        assert arr.dtype == np.int16, "zig zag encoding requires int16 input"  # noqa: S101

    encoded = np.bitwise_xor(np.right_shift(arr, 15), np.left_shift(arr, 1))
    return encoded.astype(np.uint16)
