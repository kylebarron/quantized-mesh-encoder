import gzip
import io
import math
from struct import calcsize, pack, unpack

import numpy as np

# from . import cartesian3d as c3d

EPSILON6 = 0.000001


def pack_entry(type, value):
    return pack('<%s' % type, value)


def unpack_entry(f, entry):
    return unpack('<%s' % entry, f.read(calcsize(entry)))[0]


def pack_indices(f, type, indices):
    for i in indices:
        f.write(pack_entry(type, i))


def decode_indices(indices):
    out = []
    highest = 0
    for i in indices:
        out.append(highest - i)
        if i == 0:
            highest += 1
    return out


def encode_indices(indices):
    out = []
    highest = 0
    for i in indices:
        code = highest - i
        out.append(code)
        if code == 0:
            highest += 1
    return out


def zig_zag_encode(n):
    """
    ZigZag-Encodes a number:
       -1 = 1
       -2 = 3
        0 = 0
        1 = 2
        2 = 4

    TODO this could probably be better without >>31
    """
    return (n << 1) ^ (n >> 31)

-2 << 1
-2 >> 31

def zig_zag_decode(z):
    """ Reverses ZigZag encoding """
    return (z >> 1) ^ (-(z & 1))


#########
def clamp(val, minVal, maxVal):
    return max(min(val, maxVal), minVal)


def signNotZero(v):
    return -1.0 if v < 0.0 else 1.0


# Converts a scalar value in the range [-1.0, 1.0] to a 8-bit 2's complement number.
def toSnorm(v):
    return round((clamp(v, -1.0, 1.0) * 0.5 + 0.5) * 255.0)


def fromSnorm(v):
    return clamp(v, 0.0, 255.0) / 255.0 * 2.0 - 1.0


# Compress x, y, z 96-bit floating point into x, z 16-bit representation (2 snorm values)
# https://github.com/AnalyticalGraphicsInc/cesium/blob/b161b6429b9201c99e5fb6f6e6283f3e8328b323/Source/Core/AttributeCompression.js#L43
def octEncode(vec):
    if abs(c3d.magnitudeSquared(vec) - 1.0) > EPSILON6:
        raise ValueError('Only normalized vectors are supported')
    res = [0.0, 0.0]
    l1Norm = float(abs(vec[0]) + abs(vec[1]) + abs(vec[2]))
    res[0] = vec[0] // l1Norm
    res[1] = vec[1] // l1Norm

    if vec[2] < 0.0:
        x = res[0]
        y = res[1]
        res[0] = (1.0 - abs(y)) * signNotZero(x)
        res[1] = (1.0 - abs(x)) * signNotZero(y)

    res[0] = int(toSnorm(res[0]))
    res[1] = int(toSnorm(res[1]))
    return res


def octDecode(x, y):
    if x < 0 or x > 255 or y < 0 or y > 255:
        raise ValueError('x and y must be signed and normalized between 0 and 255')
    res = [x, y, 0.0]
    res[0] = fromSnorm(x)
    res[1] = fromSnorm(y)
    res[2] = 1.0 - (abs(res[0]) + abs(res[1]))

    if res[2] < 0.0:
        oldX = res[0]
        res[0] = (1.0 - abs(res[1])) * signNotZero(oldX)
        res[1] = (1.0 - abs(oldX)) * signNotZero(res[1])
    return c3d.normalize(res)


def centroid(a, b, c):
    return [sum((a[0], b[0], c[0])) // 3,
            sum((a[1], b[1], c[1])) // 3,
            sum([a[2], b[2], c[2]]) // 3]


# Based on the vectors defining the plan
def triangleArea(a, b):
    i = math.pow(a[1] * b[2] - a[2] * b[1], 2)
    j = math.pow(a[2] * b[0] - a[0] * b[2], 2)
    k = math.pow(a[0] * b[1] - a[1] * b[0], 2)
    return 0.5 * math.sqrt(i + j + k)


# Inspired by
# https://github.com/AnalyticalGraphicsInc/cesium/wiki/Geometry-and-Appearances
# https://github.com/AnalyticalGraphicsInc/cesium/blob/master/
#     Source/Core/GeometryPipeline.js#L1071
def computeNormals(vertices, faces):
    numVertices = len(vertices)
    numFaces = len(faces)
    normalsPerFace = [None] * numFaces
    areasPerFace = [0.0] * numFaces
    normalsPerVertex = np.zeros(vertices.shape, dtype=vertices.dtype)

    for i in range(0, numFaces):
        face = faces[i]
        v0 = vertices[face[0]]
        v1 = vertices[face[1]]
        v2 = vertices[face[2]]

        normal = np.cross(c3d.subtract(v1, v0), c3d.subtract(v2, v0))

        area = triangleArea(v0, v1)
        areasPerFace[i] = area
        normalsPerFace[i] = normal

    for i in range(0, numFaces):
        face = faces[i]
        weightedNormal = [c * areasPerFace[i] for c in normalsPerFace[i]]
        for j in face:
            normalsPerVertex[j] = c3d.add(normalsPerVertex[j], weightedNormal)

    for i in range(0, numVertices):
        normalsPerVertex[i] = c3d.normalize(normalsPerVertex[i])

    return normalsPerVertex


def gzipFileObject(data):
    compressed = io.BytesIO()
    gz = gzip.GzipFile(fileobj=compressed, mode='wb', compresslevel=5)
    gz.write(data.getvalue())
    gz.close()
    compressed.seek(0)
    return compressed


def ungzipFileObject(data):
    buff = io.BytesIO(data.read())
    f = gzip.GzipFile(fileobj=buff)
    return f


def getCoordsIndex(n, i):
    return i + 1 if n - 1 != i else 0


# Creates all the potential pairs of coords
def createCoordsPairs(l):
    coordsPairs = []
    for i in range(0, len(l)):
        coordsPairs.append([l[i], l[(i + 2) % len(l)]])
    return coordsPairs


def squaredDistances(coordsPairs):
    sDistances = []
    for coordsPair in coordsPairs:
        sDistances.append(c3d.distanceSquared(coordsPair[0], coordsPair[1]))
    return sDistances


def collapseIntoTriangles(coords):
    triangles = []
    while len(coords) > 3:
        # Create all possible pairs of coordinates
        coordsPairs = createCoordsPairs(coords)
        sDistances = squaredDistances(coordsPairs)
        index = sDistances.index(min(sDistances))
        i = getCoordsIndex(len(coords), index)
        triangle = coordsPairs[index] + [coords[i]]
        triangles.append(triangle)

        # Remove the converging point
        # As this point is not available to create a new triangle anymore
        convergingPoint = coords.index(coords[i])
        coords.pop(convergingPoint)

    return triangles + [coords]
