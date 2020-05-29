import gzip
import io
from struct import pack

# from . import cartesian3d as c3d

EPSILON6 = 0.000001


def pack_entry(type, value):
    return pack('<%s' % type, value)


def zig_zag_encode(n):
    """
    ZigZag-Encodes a number:
       -1 = 1
       -2 = 3
        0 = 0
        1 = 2
        2 = 4
    """
    return (n << 1) ^ (n >> 31)


def signNotZero(v):
    return -1.0 if v < 0.0 else 1.0


def gzipFileObject(data):
    compressed = io.BytesIO()
    gz = gzip.GzipFile(fileobj=compressed, mode='wb', compresslevel=5)
    gz.write(data.getvalue())
    gz.close()
    compressed.seek(0)
    return compressed


def getCoordsIndex(n, i):
    return i + 1 if n - 1 != i else 0


# Creates all the potential pairs of coords
def createCoordsPairs(l):
    coordsPairs = []
    for i in range(0, len(l)):
        coordsPairs.append([l[i], l[(i + 2) % len(l)]])
    return coordsPairs
