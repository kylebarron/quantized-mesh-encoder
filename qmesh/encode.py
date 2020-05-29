import numpy as np
from .util import pack_entry, zig_zag_encode
from constants import VERTEX_DATA

# triangles
# vertices
# positions[0]


def encode(positions):
    # Convert to ndarray
    positions = positions_reshape(positions)

    # Linear interpolation to range u, v, h from 0-32767
    positions = interp_positions(positions)

    pass


def encode_header(view, data, offset):
    """Encode header data
    /**
     * Encode header data
     *
     * @param  {DataView} view   DataView to fill
     * @param  {Object} data   Object with data to encode
     * @param  {Number} offset Offset in DataView
     * @return {[type]}        [description]
     */

    """
    centerX,
    centerY,
    centerZ,
    minimumHeight,
    maximumHeight,
    boundingSphereCenterX,
    boundingSphereCenterY,
    boundingSphereCenterZ,
    boundingSphereRadius,
    horizonOcclusionPointX,
    horizonOcclusionPointY,
    horizonOcclusionPointZ

    view.setFloat64(offset, centerX, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset, centerY, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset, centerZ, true)
    offset += Float64Array.BYTES_PER_ELEMENT

    view.setFloat32(offset + 24, minimumHeight, true)
    offset += Float32Array.BYTES_PER_ELEMENT
    view.setFloat32(offset + 28, maximumHeight, true)
    offset += Float32Array.BYTES_PER_ELEMENT

    view.setFloat64(offset + 32, boundingSphereCenterX, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset + 40, boundingSphereCenterY, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset + 48, boundingSphereCenterZ, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset + 56, boundingSphereRadius, true)
    offset += Float64Array.BYTES_PER_ELEMENT

    view.setFloat64(offset + 64, horizonOcclusionPointX, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset + 72, horizonOcclusionPointY, true)
    offset += Float64Array.BYTES_PER_ELEMENT
    view.setFloat64(offset + 80, horizonOcclusionPointZ, true)
    offset += Float64Array.BYTES_PER_ELEMENT

    return {view, offset}


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


def _write_header(f, header):
    # Header
    for k, v in TerrainTile.quantizedMeshHeader.items():
        f.write(pack_entry(v, self.header[k]))


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


def write_indices(f):
    # Indices
    meta = TerrainTile.indexData16
    if vertexCount > TerrainTile.BYTESPLIT:
        meta = TerrainTile.indexData32

    f.write(pack_entry(meta['triangleCount'], old_div(len(self.indices), 3)))
    ind = encodeIndices(self.indices)
    packIndices(f, meta['indices'], ind)

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


#
# /**
#  * Encode vertex data
#  * Creates an int describing length of data, plus three arrays of that length
#  *
#  * @param  {[type]} view   [description]
#  * @param  {[type]} data   [description]
#  * @param  {[type]} offset [description]
#  * @return {[type]}        [description]
#  */
# def encode_vertex_data(view, data, offset) {
#   var { bbox, positions } = data;
#   var interleaved = true;
#   offset = 0;
#
#   var vertexCount = positions.length / 3;
#   view.setUint32(offset, vertexCount, true);
#   offset += Uint32Array.BYTES_PER_ELEMENT;
#
#   if (interleaved) {
#     encodeInterleavedVertexData(view, data, offset, vertexCount);
#   } else {
#     encodeNonInterleavedVertexData(view, data, offset, vertexCount);
#   }
# }
#
# function encodeInterleavedVertexData(
#   view,
#   data,
#   offset,
#   positions,
#   vertexCount
# ) {
#   positions;
#   var [[minX, minY, minZ], [maxX, maxY, maxZ]] = bbox;
#
#   var prevX = 0;
#   // Loop over x, y, z separately to make zig-zag encoding easier
#   for (var i = 0; i < positions.length; i += 3) {
#     // Scale to integer
#     var ratio = (positions[i] - minX) / maxX;
#     var x = Math.round(ratio * 32767);
#
#     var diff = x - prevX;
#     var encoded = zig_zag_encode(diff);
#     view.setUint16(offset, encoded, true);
#     offset += Uint16Array.BYTES_PER_ELEMENT;
#     prevX = x;
#   }
#
#   var prevY = 0;
#   for (var i = 1; i < positions.length; i += 3) {
#     // Scale to integer
#     var ratio = (positions[i] - minY) / maxY;
#     var y = Math.round(ratio * 32767);
#
#     var diff = y - prevY;
#     var encoded = zig_zag_encode(diff);
#     view.setUint16(offset, encoded, true);
#     offset += Uint16Array.BYTES_PER_ELEMENT;
#     prevY = y;
#   }
#
#   var prevZ = 0;
#   for (var i = 2; i < positions.length; i += 3) {
#     // Scale to integer
#     var ratio = (positions[i] - minZ) / maxZ;
#     var z = Math.round(ratio * 32767);
#
#     var diff = z - prevZ;
#     var encoded = zig_zag_encode(diff);
#     view.setUint16(offset, encoded, true);
#     offset += Uint16Array.BYTES_PER_ELEMENT;
#     prevZ = z;
#   }
# }
#
# function encodeNonInterleavedVertexData(
#   view,
#   data,
#   offset,
#   positions,
#   vertexCount
# ) {
#   positions;
#   var [[minX, minY, minZ], [maxX, maxY, maxZ]] = bbox;
#
#   var prevX = 0;
#   // Loop over x, y, z separately to make zig-zag encoding easier
#   for (var i = 0; i < positions.length / 3; i++) {
#     // Scale to integer
#     var ratio = (positions[i] - minX) / maxX;
#     var x = Math.round(ratio * 32767);
#
#     var diff = x - prevX;
#     var encoded = zig_zag_encode(diff);
#     view.setUint16(offset, encoded, true);
#     offset += Uint16Array.BYTES_PER_ELEMENT;
#     prevX = x;
#   }
#
#   var prevY = 0;
#   for (var i = positions.length; i < (positions.length / 3) * 2; i++) {
#     // Scale to integer
#     var ratio = (positions[i] - minY) / maxY;
#     var y = Math.round(ratio * 32767);
#
#     var diff = y - prevY;
#     var encoded = zig_zag_encode(diff);
#     view.setUint16(offset, encoded, true);
#     offset += Uint16Array.BYTES_PER_ELEMENT;
#     prevY = y;
#   }
#
#   var prevZ = 0;
#   for (var i = positions.length * 2; i < positions.length; i++) {
#     // Scale to integer
#     var ratio = (positions[i] - minZ) / maxZ;
#     var z = Math.round(ratio * 32767);
#
#     var diff = z - prevZ;
#     var encoded = zig_zag_encode(diff);
#     view.setUint16(offset, encoded, true);
#     offset += Uint16Array.BYTES_PER_ELEMENT;
#     prevZ = z;
#   }
# }
#
# function getBufferLength(data) {
#   const { positions, indices, bbox } = data;
#   var [[minX, minY, _], [maxX, maxY, _]] = bbox;
#
#   let nBytes = 0;
#
#   // Header always 88 bytes
#   nBytes += 88;
#
#   // Vertex data
#   // vertexCount
#   nBytes += Uint32Array.BYTES_PER_ELEMENT;
#   // uint16 per position
#   var vertexCount = positions.length / 3;
#   nBytes += Uint16Array.BYTES_PER_ELEMENT * vertexCount * 3;
#
#   // Index data
#   var indexBytesPerElement =
#     vertexCount > 65536
#       ? Uint32Array.BYTES_PER_ELEMENT
#       : Uint16Array.BYTES_PER_ELEMENT;
#
#   // triangleCount
#   nBytes += Uint32Array.BYTES_PER_ELEMENT;
#   var triangleCount = indices.length / 3;
#   nBytes += indexBytesPerElement * triangleCount * 3;
#
#   // Edge vertices
#   var westVertexCount = 0;
#   var southVertexCount = 0;
#   var eastVertexCount = 0;
#   var northVertexCount = 0;
#
#   // Note: Assumes interleaved positions
#   for (var i = 0; i < positions.length; i += 3) {
#     var [x, y] = positions.subarray(i, i + 2);
#
#     if (x === minX) westVertexCount++;
#     if (x === maxX) eastVertexCount++;
#     if (y === minY) southVertexCount++;
#     if (y === maxY) northVertexCount++;
#   }
#
#   // count of each side
#   nBytes += Uint32Array.BYTES_PER_ELEMENT * 4;
#   nBytes += indexBytesPerElement * westVertexCount;
#   nBytes += indexBytesPerElement * southVertexCount;
#   nBytes += indexBytesPerElement * eastVertexCount;
#   nBytes += indexBytesPerElement * northVertexCount;
#
#   return nBytes;
# }
#
# export const TEST_EXPORTS = { encodeZigZag };
