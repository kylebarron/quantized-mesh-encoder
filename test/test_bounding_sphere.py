import numpy as np
import pytest

from quantized_mesh_encoder.bounding_sphere import bounding_sphere


def test_bounding_sphere_unit_cube():
    """Test bounding sphere of the unit cube

    Here the naive implementation _does_ find the minimal bounding sphere.
    """
    positions = [
        -1, -1, -1,
        -1, -1, 1,
        -1, 1, -1,
        -1, 1, 1,
        1, -1, -1,
        1, -1, 1,
        1, 1, -1,
        1, 1, 1,
    ]  # fmt: skip

    cube = np.array(positions).reshape(-1, 3).astype(np.float32)
    center, radius = bounding_sphere(cube)
    assert np.isclose(np.array([0, 0, 0]), center).all(), 'Incorrect center'
    assert np.isclose(np.sqrt(3), radius), 'Incorrect radius'


# Each inner array must have a multiple of three positions
# fmt: off
BOUNDING_SPHERE_CONTAINMENT_CASES = [
    [
        0, 0, 0,
        1, 2, 3,
        4, 5, 6,
        20, -20, 10,
        -10, 30, 0,
        0, 30, 30,
    ]
]
# fmt: on


@pytest.mark.parametrize("positions", BOUNDING_SPHERE_CONTAINMENT_CASES)
def test_bounding_sphere_containment(positions):
    """
    For each input of positions, creates a bounding sphere and then makes sure
    that each point is inside the sphere.
    """
    positions = np.array(positions).reshape(-1, 3).astype(np.float32)
    center, radius = bounding_sphere(positions)

    # Distance from each point to the center
    distances = np.linalg.norm(positions - center, axis=1)

    # All distances to the center must be <= the radius
    assert (distances <= radius).all(), 'A position outside bounding sphere'


@pytest.mark.parametrize("positions", BOUNDING_SPHERE_CONTAINMENT_CASES)
def test_bounding_sphere_containment_ritter(positions):
    """
    For each input of positions, creates a bounding sphere and then makes sure
    that each point is inside the sphere.
    """
    positions = np.array(positions).reshape(-1, 3).astype(np.float32)
    center, radius = bounding_sphere(positions, method='ritter')

    # Distance from each point to the center
    distances = np.linalg.norm(positions - center, axis=1)

    # All distances to the center must be <= the radius
    assert (distances <= radius).all(), 'A position outside bounding sphere'
