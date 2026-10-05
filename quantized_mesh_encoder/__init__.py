"""Top-level package for quantized_mesh_encoder."""

from importlib.metadata import PackageNotFoundError, version

from .constants import WGS84
from .ellipsoid import Ellipsoid
from .encode import encode
from .extensions import MetadataExtension, VertexNormalsExtension, WaterMaskExtension

try:
    __version__ = version("quantized-mesh-encoder")
except PackageNotFoundError:
    __version__ = "uninstalled"

__all__ = [
    "WGS84",
    "Ellipsoid",
    "MetadataExtension",
    "VertexNormalsExtension",
    "WaterMaskExtension",
    "__version__",
    "encode",
]
