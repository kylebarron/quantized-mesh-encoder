import numpy as np

from .util_cy import add_vertex_normals


def compute_vertex_normals(positions: np.ndarray, indices: np.ndarray) -> np.ndarray:
    # Make sure indices and positions are both arrays of shape (-1, 3)
    positions = positions.reshape(-1, 3).astype('float64')
    indices = indices.reshape(-1, 3)

    # Perform coordinate lookup in positions using indices
    # positions and indices are both arrays of shape (-1, 3)
    # `coords` is then an array of shape (-1, 3, 3) where each block of (i, 3,
    # 3) represents all the coordinates of a single triangle
    tri_coords = positions[indices]

    # a, b, and c represent a single vertex for every triangle
    a = tri_coords[:, 0, :]
    b = tri_coords[:, 1, :]
    c = tri_coords[:, 2, :]

    # This computes the normal for each triangle "face". So there's one normal
    # vector for each triangle.
    face_normals = np.cross(b - a, c - a)

    # The magnitude of the cross product of b - a and c - a is the area of the
    # parallellogram spanned by these vectors; the triangle has half the area
    # https://math.stackexchange.com/q/3103543
    tri_areas = np.linalg.norm(face_normals, axis=1) / 2

    # Multiply each face normal by the area of that triangle
    weighted_face_normals = np.multiply(face_normals, tri_areas[:, np.newaxis])

    # Sum up each vertex normal
    # According to the implementation this is ported from, since you weight the
    # face normals by the area, you can just sum up the vectors.
    vertex_normals = np.zeros(positions.shape, dtype=np.float64)
    add_vertex_normals(indices, weighted_face_normals, vertex_normals)

    # Normalize vertex normals by dividing by each vector's length
    normalized_vertex_normals = (
        vertex_normals / np.linalg.norm(vertex_normals, axis=1)[:, np.newaxis]
    )

    return normalized_vertex_normals


def sign_not_zero(arr: np.ndarray) -> np.ndarray:
    """A variation of np.sign that coerces 0 to 1"""
    return np.where(arr < 0.0, -1, 1)


def oct_encode(vec: np.ndarray) -> np.ndarray:
    """
    Compress x, y, z 96-bit floating point into x, z 16-bit representation (2 snorm values)
    https://github.com/AnalyticalGraphicsInc/cesium/blob/b161b6429b9201c99e5fb6f6e6283f3e8328b323/Source/Core/AttributeCompression.js#L43
    https://github.com/loicgasser/quantized-mesh-tile/blob/750125d3885fd89e3e12dce8fe075fbdc0adc323/quantized_mesh_tile/utils.py#L90-L108

    This assumes input vectors are normalized
    """

    l1_norm = np.linalg.norm(vec, ord=1, axis=1)
    result = vec[:, 0:2] / l1_norm[:, np.newaxis]

    negative = vec[:, 2] < 0.0
    x = np.copy(result[:, 0])
    y = np.copy(result[:, 1])
    result[:, 0] = np.where(negative, (1 - np.abs(y)) * sign_not_zero(x), result[:, 0])
    result[:, 1] = np.where(negative, (1 - np.abs(x)) * sign_not_zero(y), result[:, 1])

    # Converts a scalar value in the range [-1.0, 1.0] to a 8-bit 2's complement
    # number.
    oct_encoded = np.floor((np.clip(result, -1, 1) * 0.5 + 0.5) * 256).astype(np.uint8)

    return oct_encoded
