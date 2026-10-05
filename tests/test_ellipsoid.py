import numpy as np

import quantized_mesh_encoder
from quantized_mesh_encoder import WGS84, Ellipsoid


def test_wgs84_eccentricity():
    # Square of the first eccentricity of the WGS84 ellipsoid
    assert np.isclose(WGS84.e2, 0.00669437999014)


def test_sphere_has_zero_eccentricity():
    assert Ellipsoid(1, 1).e2 == 0


def test_public_api():
    for name in quantized_mesh_encoder.__all__:
        assert hasattr(quantized_mesh_encoder, name)

    assert quantized_mesh_encoder.__version__ != "uninstalled"
