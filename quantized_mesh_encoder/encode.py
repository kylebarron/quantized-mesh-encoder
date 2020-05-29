import numpy as np
from .util import pack_entry, zig_zag_encode
from constants import VERTEX_DATA, HEADER
from util_cy import encode_indices

# triangles
# vertices
# positions[0]

# triangles
# indices = triangles


def encode(f, positions, indices):
    encode_header(f, data=None)

    # Convert to ndarray
    positions = positions_reshape(positions)

    # Linear interpolation to range u, v, h from 0-32767
    positions = interp_positions(positions)

    write_vertices(f, positions)

    write_indices(f, indices)


def encode_header(f, data):
    """Encode header data

    Args:
        - f: Opened file descriptor for writing
        - data: dict of header data
    """
    f.write(pack_entry(HEADER['centerX'], data['centerX']))
    f.write(pack_entry(HEADER['centerY'], data['centerY']))
    f.write(pack_entry(HEADER['centerZ'], data['centerZ']))

    f.write(pack_entry(HEADER['minimumHeight'], data['minimumHeight']))
    f.write(pack_entry(HEADER['maximumHeight'], data['maximumHeight']))

    f.write(
        pack_entry(
            HEADER['boundingSphereCenterX'], data['boundingSphereCenterX']))
    f.write(
        pack_entry(
            HEADER['boundingSphereCenterY'], data['boundingSphereCenterY']))
    f.write(
        pack_entry(
            HEADER['boundingSphereCenterZ'], data['boundingSphereCenterZ']))
    f.write(
        pack_entry(
            HEADER['boundingSphereRadius'], data['boundingSphereRadius']))

    f.write(
        pack_entry(
            HEADER['horizonOcclusionPointX'], data['horizonOcclusionPointX']))
    f.write(
        pack_entry(
            HEADER['horizonOcclusionPointY'], data['horizonOcclusionPointY']))
    f.write(
        pack_entry(
            HEADER['horizonOcclusionPointZ'], data['horizonOcclusionPointZ']))


def positions_reshape(positions):
    """Convert array to 3d ndarray"""
    return positions.reshape(-1, 3)


def interp_positions(positions, bounds=None):
    """Rescale positions to be integers ranging from min to max

    TODO allow 6 input elements, for min/max elevation too?

    Args:
        - positions
        - bounds: If provided should be [minx, miny, maxx, maxy]

    Returns:
        ndarray of shape (-1, 3) and dtype np.uint32
    """
    if bounds:
        minx, miny, maxx, maxy = bounds
    else:
        minx = positions[:, 0].min()
        maxx = positions[:, 0].max()
        miny = positions[:, 1].min()
        maxy = positions[:, 1].max()

    minh = positions[:, 2].min()
    maxh = positions[:, 2].max()

    u = np.interp(positions[:, 0], (minx, maxx), (0, 32767)).astype(np.int16)
    v = np.interp(positions[:, 1], (miny, maxy), (0, 32767)).astype(np.int16)
    h = np.interp(positions[:, 2], (minh, maxh), (0, 32767)).astype(np.int16)

    return np.vstack([u, v, h]).T


def write_vertices(f, positions):
    assert positions.ndim == 2, 'positions must be 2 dimensions'

    n_vertices = max(positions.shape)

    # Write vertex count
    f.write(pack_entry(VERTEX_DATA['vertexCount'], n_vertices))

    u = positions[:, 0]
    v = positions[:, 1]
    h = positions[:, 2]

    u_diff = u[1:] - u[:-1]
    v_diff = v[1:] - v[:-1]
    h_diff = h[1:] - h[:-1]

    # Zig zag encode
    # https://gist.github.com/mfuerstenau/ba870a29e16536fdbaba
    # (i >> bitlength-1) ^ (i << 1)
    # So I right shift 15 because these arrays are int16
    u_zz = np.bitwise_xor(np.right_shift(u_diff, 15), np.left_shift(
        u_diff, 1)).astype(np.uint16)
    v_zz = np.bitwise_xor(np.right_shift(v_diff, 15), np.left_shift(
        v_diff, 1)).astype(np.uint16)
    h_zz = np.bitwise_xor(np.right_shift(h_diff, 15), np.left_shift(
        h_diff, 1)).astype(np.uint16)

    # Write first value
    f.write(pack_entry(VERTEX_DATA['uVertexCount'], zig_zag_encode(u[0])))
    # Write array. Must be uint16
    f.write(u_zz.tobytes())

    # Write first value
    f.write(pack_entry(VERTEX_DATA['vVertexCount'], zig_zag_encode(v[0])))
    # Write array. Must be uint16
    f.write(v_zz.tobytes())

    # Write first value
    f.write(pack_entry(VERTEX_DATA['heightVertexCount'], zig_zag_encode(h[0])))
    # Write array. Must be uint16
    f.write(h_zz.tobytes())


def write_indices(f, indices):
    """Write indices to file

    """
    # TODO whether to use 16 or 32 bits
    indexData32 = True

    # Enforce proper byte alignment
    # > padding is added before the IndexData to ensure 2 byte alignment for
    # > IndexData16 and 4 byte alignment for IndexData32.
    required_offset = 4 if indexData32 else 2
    remainder = f.tell() % required_offset
    if remainder:
        # number of bytes to add
        n_bytes = required_offset - remainder
        # TODO write required number of bytes

    # Write number of triangles to file
    n_triangles = len(indices) / 3
    f.write(pack_entry(meta['triangleCount'], n_triangles))

    # Encode indices using high water mark encoding
    encoded_ind = encode_indices(indices)
    # Write array. Must be either uint16 or uint32, depending on length of
    # vertices
    if not indexData32:
        encoded_ind = encoded_ind.astype(np.uint16)
    f.write(encoded_ind.tobytes())

    meta = TerrainTile.EdgeIndices16
    if vertexCount > TerrainTile.BYTESPLIT:
        meta = TerrainTile.EdgeIndices32

    f.write(pack_entry(meta['westVertexCount'], len(self.westI)))
    for wi in self.westI:
        f.write(pack_entry(meta['westIndices'], wi))

    f.write(pack_entry(meta['southVertexCount'], len(self.southI)))
    for si in self.southI:
        f.write(pack_entry(meta['southIndices'], si))

    f.write(pack_entry(meta['eastVertexCount'], len(self.eastI)))
    for ei in self.eastI:
        f.write(pack_entry(meta['eastIndices'], ei))

    f.write(pack_entry(meta['northVertexCount'], len(self.northI)))
    for ni in self.northI:
        f.write(pack_entry(meta['northIndices'], ni))
