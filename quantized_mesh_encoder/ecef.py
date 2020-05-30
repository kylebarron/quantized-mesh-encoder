import numpy as np

# From https://github.com/loicgasser/quantized-mesh-tile/blob/master/quantized_mesh_tile/llh_ecef.py
# Constants taken from http://cesiumjs.org/2013/04/25/Horizon-culling/
radiusX = 6378137.0
radiusY = 6378137.0
radiusZ = 6356752.3142451793

# Stolen from https://github.com/bistromath/gr-air-modes/blob/master/python/mlat.py
# WGS84 reference ellipsoid constants
# http://en.wikipedia.org/wiki/Geodetic_datum#Conversion_calculations
# http://en.wikipedia.org/wiki/File%3aECEF.png
wgs84_a = radiusX  # Semi-major axis
wgs84_b = radiusZ  # Semi-minor axis
wgs84_e2 = 0.0066943799901975848  # First eccentricity squared
wgs84_a2 = wgs84_a ** 2  # To speed things up a bit
wgs84_b2 = wgs84_b ** 2


def to_ecef(positions):
    """Convert positions to earth-centered, earth-fixed coordinates

    Ported from
    https://github.com/loicgasser/quantized-mesh-tile/blob/master/quantized_mesh_tile/llh_ecef.py
    under the MIT license.

    Originally from
    https://github.com/bistromath/gr-air-modes/blob/9e2515a56609658f168f0c833a14ca4d2332713e/python/mlat.py#L73-L86
    under the BSD-3 clause license.

    Args:
        - positions: expected to be an ndarray with shape (-1, 3)
    from latitude-longitude-height to
    """

    lon = positions[:, 0]
    lat = positions[:, 1]
    alt = positions[:, 2]

    lat *= np.pi / 180
    lon *= np.pi / 180

    n = lambda arr: wgs84_a / np.sqrt(1 - wgs84_e2 * (np.square(np.sin(arr))))
    nlat = n(lat)

    x = (nlat + alt) * np.cos(lat) * np.cos(lon)
    y = (nlat + alt) * np.cos(lat) * np.sin(lon)
    z = (nlat * (1 - wgs84_e2) + alt) * np.sin(lat)

    # Do I need geoid correction?
    # https://github.com/bistromath/gr-air-modes/blob/9e2515a56609658f168f0c833a14ca4d2332713e/python/mlat.py#L88-L92
    return np.vstack([x, y, z]).T
