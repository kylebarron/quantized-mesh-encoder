import numpy as np

from .constants import RADIUS_X, RADIUS_Y, RADIUS_Z


def squared_norm(positions):
    return np.square(positions[:, 0]) + np.square(positions[:, 1]) + np.square(
        positions[:, 2])


def compute_magnitude(positions, bounding_center):
    magnitude_squared = squared_norm(positions)
    magnitude = np.sqrt(magnitude_squared)

    direction = positions.copy()
    direction[:, 0] /= magnitude
    direction[:, 1] /= magnitude
    direction[:, 2] /= magnitude

    magnitude_squared = np.maximum(magnitude_squared, 1)
    magnitude = np.maximum(magnitude, 1)

    cos_alpha = np.dot(direction, bounding_center.T)[:, 0]
    sin_alpha = np.linalg.norm(np.cross(direction, bounding_center), axis=1)
    cos_beta = 1 / magnitude
    sin_beta = np.sqrt(magnitude_squared - 1.0) * cos_beta

    return 1 / (cos_alpha * cos_beta - sin_alpha * sin_beta)


def scale_ellipsoid(positions):
    positions[:, 0] = positions[:, 0] / RADIUS_X
    positions[:, 1] = positions[:, 1] / RADIUS_Y
    positions[:, 2] = positions[:, 2] / RADIUS_Z

    return positions


# https://cesiumjs.org/2013/05/09/Computing-the-horizon-occlusion-point/
def fromPoints(positions, bounding_center):
    positions = scale_ellipsoid(positions)

    # Make sure bounding center is a 2d array, so it can be scaled with same fn
    bounding_center = bounding_center.reshape(-1, 3)
    bounding_center = scale_ellipsoid(bounding_center)

    # Coerce back to a 1d array
    bounding_center = bounding_center[0, :]

    magnitudes = compute_magnitude(positions, bounding_center)
    return bounding_center * magnitudes.max()
