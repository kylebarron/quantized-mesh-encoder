import numpy as np
import pytest

from quantized_mesh_encoder import WGS84
from quantized_mesh_encoder.ecef import to_ecef
from quantized_mesh_encoder.occlusion import occlusion_point


@pytest.mark.parametrize("llh_position", [[0, 0, 0], [7.4, 46.9, 0], [-120, -45, 0]])
def test_occlusion_point_surface(llh_position):
    """A single point on the ellipsoid surface is its own occlusion point."""
    position = to_ecef(np.array([llh_position], dtype=np.float64))
    # occlusion_point rescales its inputs in place
    point = occlusion_point(position.copy(), position[0].copy(), ellipsoid=WGS84)
    assert np.allclose(point, position[0])


def test_occlusion_point_above_surface():
    """Points above the surface push the occlusion point further out."""
    llh = np.array([[7.4, 46.9, 0], [7.5, 47.0, 0], [7.45, 46.95, 4000]])
    positions = to_ecef(llh)
    center = positions.mean(axis=0)

    point = occlusion_point(positions.copy(), center.copy())

    # The occlusion point lies along the direction of the center
    assert np.allclose(point / np.linalg.norm(point), center / np.linalg.norm(center))
    # And it is further from the origin than any of the positions
    assert np.linalg.norm(point) > np.linalg.norm(positions, axis=1).max()
