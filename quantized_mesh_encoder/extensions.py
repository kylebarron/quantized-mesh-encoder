import abc
from dataclasses import dataclass, field
from enum import IntEnum
from struct import pack

import numpy as np

from .constants import EXTENSION_HEADER, WGS84
from .ecef import to_ecef
from .ellipsoid import Ellipsoid
from .normals import compute_vertex_normals, oct_encode


class ExtensionId(IntEnum):
    VERTEX_NORMALS = 1
    WATER_MASK = 2
    METADATA = 4


@dataclass
class ExtensionBase(metaclass=abc.ABCMeta):
    id: ExtensionId

    @property
    @abc.abstractmethod
    def encode(self) -> bytes:
        """"Return the encoded extension data"""
        ...


@dataclass
class VertexNormalsExtension(ExtensionBase):
    indices: np.ndarray
    positions: np.ndarray
    id: ExtensionId = ExtensionId.VERTEX_NORMALS
    ellipsoid: Ellipsoid = WGS84

    def encode(self) -> bytes:
        positions = self.positions.reshape(-1, 3)
        cartesian_positions = to_ecef(positions, self.ellipsoid)
        normals = compute_vertex_normals(cartesian_positions, self.indices)
        encoded = oct_encode(normals).tobytes('C')

        buf = b''
        buf += pack(EXTENSION_HEADER['extensionId'], ExtensionId.VERTEX_NORMALS)
        buf += pack(EXTENSION_HEADER['extensionLength'], len(encoded))
        buf += encoded

        return buf
