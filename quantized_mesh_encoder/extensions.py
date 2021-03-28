import abc
from dataclasses import dataclass, field
from enum import IntEnum
from struct import pack

import numpy as np

from .constants import EXTENSION_HEADER, WGS84
from .ellipsoid import Ellipsoid
from .normals import compute_vertex_normals, oct_encode


class ExtensionId(IntEnum):
    VERTEX_NORMALS = 1
    WATER_MASK = 2
    METADATA = 4


@dataclass
class ExtensionBase(metaclass=abc.ABCMeta):
    id: ExtensionId = field(init=False)

    @property
    @abc.abstractmethod
    def encode(self) -> bytes:
        """"Return the encoded extension data"""
        ...


@dataclass
class VertexNormalsExtension(ExtensionBase):
    id: ExtensionId = field(init=False, default=ExtensionId.VERTEX_NORMALS)
    indices: np.ndarray
    positions: np.ndarray
    ellipsoid: Ellipsoid = WGS84

    def encode(self) -> bytes:
        normals = compute_vertex_normals(self.positions, self.indices)
        encoded = oct_encode(normals).tobytes('C')

        buf = b''
        buf += pack(EXTENSION_HEADER['extensionId'], ExtensionId.VERTEX_NORMALS)
        buf += pack(EXTENSION_HEADER['extensionLength'], len(encoded))
        buf += encoded

        return buf
