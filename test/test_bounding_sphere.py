import numpy as np

from quantized_mesh_encoder.bounding_sphere import bounding_sphere


def test_bounding_sphere_cube():
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
    ] # yapf: disable

    cube = np.array(positions).reshape(-1, 3)
    center, radius = bounding_sphere(cube)
    assert np.isclose(np.array([0, 0, 0]), center).all(), 'Incorrect center'
    assert np.isclose(np.sqrt(3), radius), 'Incorrect radius'
