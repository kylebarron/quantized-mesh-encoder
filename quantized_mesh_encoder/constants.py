import numpy as np

# From https://github.com/loicgasser/quantized-mesh-tile/blob/master/quantized_mesh_tile/llh_ecef.py
# Constants taken from http://cesiumjs.org/2013/04/25/Horizon-culling/
RADIUS_X = 6378137.0
RADIUS_Y = 6378137.0
RADIUS_Z = 6356752.3142451793

# Stolen from https://github.com/bistromath/gr-air-modes/blob/master/python/mlat.py
# WGS84 reference ellipsoid constants
# http://en.wikipedia.org/wiki/Geodetic_datum#Conversion_calculations
# http://en.wikipedia.org/wiki/File%3aECEF.png
WGS84_A = RADIUS_X  # Semi-major axis
WGS84_B = RADIUS_Z  # Semi-minor axis
WGS84_E2 = 0.0066943799901975848  # First eccentricity squared
WGS84_A2 = WGS84_A ** 2  # To speed things up a bit
WGS84_B2 = WGS84_B ** 2

NP_STRUCT_TYPES = {
    np.float32: '<f',
    np.float64: '<d',
    np.uint16: '<H',
    np.uint32: '<I'}

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
    'horizonOcclusionPointZ': '<d'}

VERTEX_DATA = {
    # 4bytes -> determines the size of the 3 following arrays
    'vertexCount': '<I',
    'uVertexCount': '<H',  # 2bytes, unsigned short
    'vVertexCount': '<H',
    'heightVertexCount': '<H'}

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
    'northIndices': '<H'}

EDGE_INDICES32 = {
    'westVertexCount': '<I',
    'westIndices': '<I',
    'southVertexCount': '<I',
    'southIndices': '<I',
    'eastVertexCount': '<I',
    'eastIndices': '<I',
    'northVertexCount': '<I',
    'northIndices': '<I'}
