"""Top-level package for quantized_mesh_encoder."""

__author__ = """Kyle Barron"""
__email__ = 'kylebarron2@gmail.com'
__version__ = '0.4.1'

from .constants import WGS84
from .ellipsoid import Ellipsoid
from .encode import encode
from .extensions import MetadataExtension, VertexNormalsExtension, WaterMaskExtension
