import numpy as np

from .constants import WGS84
from .ellipsoid import Ellipsoid


def to_ecef(positions: np.ndarray, *, ellipsoid: Ellipsoid = WGS84) -> np.ndarray:
    """Convert positions to earth-centered, earth-fixed coordinates

    Ported from
    https://github.com/loicgasser/quantized-mesh-tile/blob/master/quantized_mesh_tile/llh_ecef.py
    under the MIT license.

    Originally from
    https://github.com/bistromath/gr-air-modes/blob/9e2515a56609658f168f0c833a14ca4d2332713e/python/mlat.py#L73-L86
    under the BSD-3 clause license.

    Args:
        - positions: expected to be an ndarray with shape (-1, 3)
          from latitude-longitude-height to ecef

    Kwargs:
        - ellipsoid: (`Ellipsoid`): ellipsoid defined by its semi-major `a`
          and semi-minor `b` axes. Default: WGS84 ellipsoid.
    """
    msg = 'ellipsoid must be an instance of the Ellipsoid class'
    assert isinstance(ellipsoid, Ellipsoid), msg

    lon = positions[:, 0] * np.pi / 180
    lat = positions[:, 1] * np.pi / 180
    alt = positions[:, 2]

    n = lambda arr: ellipsoid.a / np.sqrt(1 - ellipsoid.e2 * (np.square(np.sin(arr))))
    nlat = n(lat)

    x = (nlat + alt) * np.cos(lat) * np.cos(lon)
    y = (nlat + alt) * np.cos(lat) * np.sin(lon)
    z = (nlat * (1 - ellipsoid.e2) + alt) * np.sin(lat)

    # Do I need geoid correction?
    # https://github.com/bistromath/gr-air-modes/blob/9e2515a56609658f168f0c833a14ca4d2332713e/python/mlat.py#L88-L92
    return np.vstack([x, y, z]).T
