import numpy as np

from .constants import WGS84
from .ellipsoid import Ellipsoid


def squared_norm(positions: np.ndarray) -> np.ndarray:
    return (
        np.square(positions[:, 0])
        + np.square(positions[:, 1])
        + np.square(positions[:, 2])
    )


def compute_magnitude(positions: np.ndarray, bounding_center: np.ndarray) -> np.ndarray:
    magnitude_squared = squared_norm(positions)
    magnitude = np.sqrt(magnitude_squared)

    # Can make this cleaner by broadcasting division
    direction = positions.copy()
    direction[:, 0] /= magnitude
    direction[:, 1] /= magnitude
    direction[:, 2] /= magnitude

    magnitude_squared = np.maximum(magnitude_squared, 1)
    magnitude = np.maximum(magnitude, 1)

    cos_alpha = np.dot(direction, bounding_center.T)
    sin_alpha = np.linalg.norm(np.cross(direction, bounding_center), axis=1)
    cos_beta = 1 / magnitude
    sin_beta = np.sqrt(magnitude_squared - 1.0) * cos_beta

    return 1 / (cos_alpha * cos_beta - sin_alpha * sin_beta)


# https://cesiumjs.org/2013/05/09/Computing-the-horizon-occlusion-point/
def occlusion_point(
    positions: np.ndarray, bounding_center: np.ndarray, *, ellipsoid: Ellipsoid = WGS84
) -> np.ndarray:
    cartesian_ellipsoid = np.array([ellipsoid.a, ellipsoid.a, ellipsoid.b])
    # Scale positions relative to ellipsoid
    positions /= cartesian_ellipsoid

    # Scale center relative to ellipsoid
    bounding_center /= cartesian_ellipsoid

    # Find magnitudes necessary for each position to not be visible
    magnitudes = compute_magnitude(positions, bounding_center)

    # Multiply by maximum magnitude and rescale to ellipsoid surface
    return bounding_center * magnitudes.max() * cartesian_ellipsoid
