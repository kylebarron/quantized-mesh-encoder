from io import BytesIO
from numbers import Number

import numpy as np
from quantized_mesh_encoder.encode import (
    compute_header, encode, encode_header, interp_positions)
from quantized_mesh_tile import TerrainTile


def test_compute_header():
    positions = np.array([0, 0, 0, 1, 1, 1, 0, 1, 4], dtype=np.float32).reshape(
        -1, 3)

    header = compute_header(positions, sphere_method=None)
    keys = [
        'centerX', 'centerY', 'centerZ', 'minimumHeight', 'maximumHeight',
        'boundingSphereCenterX', 'boundingSphereCenterY',
        'boundingSphereCenterZ', 'boundingSphereRadius',
        'horizonOcclusionPointX', 'horizonOcclusionPointY',
        'horizonOcclusionPointZ']
    assert all(k in header.keys() for k in keys), 'Header key missing'
    assert all(
        isinstance(v, Number)
        for v in header.values()), 'Header value not numeric'


def test_encode_header():
    header = {
        'centerX': 6377169.5,
        'centerY': 55648.50390625,
        'centerZ': 55284.421875,
        'minimumHeight': 0.0,
        'maximumHeight': 4.0,
        'boundingSphereCenterX': 6377169.5,
        'boundingSphereCenterY': 55648.504,
        'boundingSphereCenterZ': 55284.42,
        'boundingSphereRadius': 78447.81,
        'horizonOcclusionPointX': 6378226.71931529,
        'horizonOcclusionPointY': 55657.731270568445,
        'horizonOcclusionPointZ': 55293.58686988714}

    buf = BytesIO()
    encode_header(buf, header)
    buf.seek(0)
    b = buf.read()

    assert len(b) == 88, 'Header incorrect number of bytes'


def test_encode_decode():
    positions = np.array(
        [0, 0, 0, 1, 1, 1, 0, 1, 4, 2, 3, 4, 8, 9, 10, 12, 13, 14],
        dtype=np.float32)
    triangles = np.array([0, 1, 2, 1, 2, 3, 2, 3, 4, 3, 4, 5], dtype=np.uint32)
    f = BytesIO()
    encode(f, positions, triangles)

    f.seek(0)
    tile = TerrainTile()
    tile.fromBytesIO(f)

    assert np.array_equal(
        triangles, np.array(tile.indices, dtype=np.uint32)), 'Indices incorrect'
    u, v, h = interp_positions(positions.reshape(-1, 3)).T

    assert np.array_equal(
        u, np.array(tile.u, dtype=np.uint32)), 'Vertices incorrect'
    assert np.array_equal(
        v, np.array(tile.v, dtype=np.uint32)), 'Vertices incorrect'
    assert np.array_equal(
        h, np.array(tile.h, dtype=np.uint32)), 'Vertices incorrect'

    assert tile.westI == [0, 2]
    assert tile.southI == [0]
    assert tile.eastI == [5]
    assert tile.northI == [5]
