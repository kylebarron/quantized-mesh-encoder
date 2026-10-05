import json
from struct import pack

import numpy as np
import pytest

from quantized_mesh_encoder import (
    MetadataExtension,
    VertexNormalsExtension,
    WaterMaskExtension,
)
from quantized_mesh_encoder.extensions import ExtensionId


def split_extension(buf: bytes) -> tuple[int, bytes]:
    """Split an encoded extension into its id and payload, checking the length."""
    extension_id = buf[0]
    (length,) = np.frombuffer(buf[1:5], dtype="<u4")
    payload = buf[5:]
    assert len(payload) == length
    return extension_id, payload


@pytest.mark.parametrize("data", [0, 1, 255, np.uint8(1)])
def test_water_mask_scalar(data):
    buf = WaterMaskExtension(data=data).encode()
    assert buf == pack("<BIB", ExtensionId.WATER_MASK, 1, int(data))


def test_water_mask_array():
    mask = np.zeros((256, 256), dtype=np.uint8)
    mask[:128] = 255

    extension_id, payload = split_extension(WaterMaskExtension(data=mask).encode())
    assert extension_id == ExtensionId.WATER_MASK
    assert payload == mask.tobytes()


def test_water_mask_array_cast_to_uint8():
    mask = np.ones((256, 256), dtype=bool)
    _, payload = split_extension(WaterMaskExtension(data=mask).encode())
    assert payload == mask.astype(np.uint8).tobytes()


def test_metadata_dict():
    data = {"hello": "world", "available": [[{"startX": 0}]]}
    extension_id, payload = split_extension(MetadataExtension(data=data).encode())
    assert extension_id == ExtensionId.METADATA
    # Output is minified JSON
    assert payload == b'{"hello":"world","available":[[{"startX":0}]]}'
    assert json.loads(payload) == data


def test_metadata_bytes():
    data = b"arbitrary bytes"
    extension_id, payload = split_extension(MetadataExtension(data=data).encode())
    assert extension_id == ExtensionId.METADATA
    assert payload == data


def test_vertex_normals():
    positions = np.array([0, 0, 0, 1, 1, 1, 0, 1, 4, 2, 3, 4], dtype=np.float32)
    triangles = np.array([0, 1, 2, 1, 2, 3], dtype=np.uint32)
    ext = VertexNormalsExtension(positions=positions, indices=triangles)

    extension_id, payload = split_extension(ext.encode())
    assert extension_id == ExtensionId.VERTEX_NORMALS
    # Two bytes per vertex
    assert len(payload) == 2 * 4


@pytest.mark.parametrize(
    "make_extension",
    [
        lambda: WaterMaskExtension(data="not a mask"),
        lambda: MetadataExtension(data=["not", "a", "dict"]),
        lambda: VertexNormalsExtension(positions=[0, 0, 0], indices=[0, 0, 0]),
        lambda: MetadataExtension(id=4, data={}),
    ],
)
def test_validation(make_extension):
    with pytest.raises(TypeError):
        make_extension()
