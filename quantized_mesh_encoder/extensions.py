from dataclasses import dataclass

from .constants import QuantizedMeshExtensions


@dataclass
class ExtensionBase:
    extension_id: int


@dataclass
class VertexNormalsExtension(ExtensionBase):
    extension_id: str = QuantizedMeshExtensions.VERTEX_NORMALS
