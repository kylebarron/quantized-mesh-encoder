"""Quantized Mesh extensions."""

from __future__ import annotations

import abc
import json
from enum import IntEnum
from struct import pack

import attr
import numpy as np

from .constants import EXTENSION_HEADER, WGS84
from .ecef import to_ecef
from .ellipsoid import Ellipsoid
from .normals import compute_vertex_normals, oct_encode


class ExtensionId(IntEnum):
    """Extension identifiers defined by the Quantized Mesh spec."""

    VERTEX_NORMALS = 1
    WATER_MASK = 2
    METADATA = 4


@attr.s(kw_only=True)
class ExtensionBase(metaclass=abc.ABCMeta):
    """Base class for Quantized Mesh extensions.

    Attributes:
        id: Extension identifier.

    """

    id: ExtensionId = attr.ib(validator=attr.validators.instance_of(ExtensionId))

    @abc.abstractmethod
    def encode(self) -> bytes:
        """Return the encoded extension, including its header."""
        ...


@attr.s(kw_only=True)
class VertexNormalsExtension(ExtensionBase):
    """Vertex Normals (Terrain Lighting) extension.

    Per-vertex normals are computed from the mesh.

    Attributes:
        indices: Mesh indices.
        positions: Mesh positions.
        ellipsoid: Ellipsoid used to convert positions to ECEF coordinates.
            Default: WGS84 ellipsoid.

    """

    id: ExtensionId = attr.ib(
        ExtensionId.VERTEX_NORMALS, validator=attr.validators.instance_of(ExtensionId)
    )
    indices: np.ndarray = attr.ib(validator=attr.validators.instance_of(np.ndarray))
    positions: np.ndarray = attr.ib(validator=attr.validators.instance_of(np.ndarray))
    ellipsoid: Ellipsoid = attr.ib(
        WGS84, validator=attr.validators.instance_of(Ellipsoid)
    )

    def encode(self) -> bytes:
        """Return the encoded extension, including its header."""
        positions = self.positions.reshape(-1, 3)
        cartesian_positions = to_ecef(positions, ellipsoid=self.ellipsoid)
        normals = compute_vertex_normals(cartesian_positions, self.indices)
        encoded = oct_encode(normals).tobytes("C")

        buf = b""
        buf += pack(EXTENSION_HEADER["extensionId"], self.id.value)
        buf += pack(EXTENSION_HEADER["extensionLength"], len(encoded))
        buf += encoded

        return buf


@attr.s(kw_only=True)
class WaterMaskExtension(ExtensionBase):
    """Water Mask extension.

    Attributes:
        data: Either a numpy ndarray or an integer between 0 and 255.

    """

    id: ExtensionId = attr.ib(
        ExtensionId.WATER_MASK, validator=attr.validators.instance_of(ExtensionId)
    )
    data: np.ndarray | np.uint8 | int = attr.ib(
        validator=attr.validators.instance_of((np.ndarray, np.uint8, int))
    )

    def encode(self) -> bytes:
        """Return the encoded extension, including its header."""
        encoded: bytes
        if isinstance(self.data, np.ndarray):
            # Minify output
            encoded = self.data.astype(np.uint8).tobytes("C")
        elif isinstance(self.data, (np.uint8, int)):
            encoded = np.uint8(self.data).tobytes("C")

        buf = b""
        buf += pack(EXTENSION_HEADER["extensionId"], self.id.value)
        buf += pack(EXTENSION_HEADER["extensionLength"], len(encoded))
        buf += encoded

        return buf


@attr.s(kw_only=True)
class MetadataExtension(ExtensionBase):
    """Metadata extension.

    Attributes:
        data: Either a dictionary or bytes. If a dictionary, `json.dumps` will
            be called to create bytes in UTF-8 encoding.

    """

    id: ExtensionId = attr.ib(
        ExtensionId.METADATA, validator=attr.validators.instance_of(ExtensionId)
    )
    data: dict | bytes = attr.ib(validator=attr.validators.instance_of((dict, bytes)))

    def encode(self) -> bytes:
        """Return the encoded extension, including its header."""
        encoded: bytes
        if isinstance(self.data, dict):
            # Minify output
            encoded = json.dumps(self.data, separators=(",", ":")).encode()
        elif isinstance(self.data, bytes):
            encoded = self.data

        buf = b""
        buf += pack(EXTENSION_HEADER["extensionId"], self.id.value)
        buf += pack(EXTENSION_HEADER["extensionLength"], len(encoded))
        buf += encoded

        return buf
