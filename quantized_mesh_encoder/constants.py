import numpy as np

from .ellipsoid import Ellipsoid

WGS84 = Ellipsoid(a=6378137.0, b=6356752.3142451793)

NP_STRUCT_TYPES = {np.float32: '<f', np.float64: '<d', np.uint16: '<H', np.uint32: '<I'}

HEADER = {
    'centerX': '<d',  # 8bytes
    'centerY': '<d',
    'centerZ': '<d',
    'minimumHeight': '<f',  # 4bytes
    'maximumHeight': '<f',
    'boundingSphereCenterX': '<d',
    'boundingSphereCenterY': '<d',
    'boundingSphereCenterZ': '<d',
    'boundingSphereRadius': '<d',
    'horizonOcclusionPointX': '<d',
    'horizonOcclusionPointY': '<d',
    'horizonOcclusionPointZ': '<d',
}

VERTEX_DATA = {
    # 4bytes -> determines the size of the 3 following arrays
    'vertexCount': '<I',
    'uVertexCount': '<H',  # 2bytes, unsigned short
    'vVertexCount': '<H',
    'heightVertexCount': '<H',
}

INDEX_DATA16 = {'triangleCount': '<I', 'indices': '<H'}

INDEX_DATA32 = {'triangleCount': '<I', 'indices': '<I'}

EDGE_INDICES16 = {
    'westVertexCount': '<I',
    'westIndices': '<H',
    'southVertexCount': '<I',
    'southIndices': '<H',
    'eastVertexCount': '<I',
    'eastIndices': '<H',
    'northVertexCount': '<I',
    'northIndices': '<H',
}

EDGE_INDICES32 = {
    'westVertexCount': '<I',
    'westIndices': '<I',
    'southVertexCount': '<I',
    'southIndices': '<I',
    'eastVertexCount': '<I',
    'eastIndices': '<I',
    'northVertexCount': '<I',
    'northIndices': '<I',
}

EXTENSION_HEADER = {'extensionId': '<B', 'extensionLength': '<I'}
