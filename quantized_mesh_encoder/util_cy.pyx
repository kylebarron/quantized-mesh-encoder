import numpy as np
cimport numpy as np

def encode_indices(indices):
    """High-water mark encoding
    """
    cdef np.uint32_t[:] indices_view = indices
    cdef np.uint32_t[:] out_view
    cdef unsigned int highest, code
    cdef Py_ssize_t i
    cdef unsigned short idx

    out_view = np.zeros(len(indices), dtype=np.uint32)
    highest = 0
    for i in range(len(indices)):
        out_view[i] = highest - indices_view[i]
        if out_view[i] == 0:
            highest += 1

    return np.asarray(out_view, dtype=np.uint32)


def ritter_second_pass(
    np.ndarray[np.float32_t, ndim=2] positions,
    np.ndarray[np.float32_t, ndim=1] center,
    float radius):

    cdef np.float32_t[:] dP
    cdef float dist, dist2, mult
    cdef Py_ssize_t i
    cdef float radius2 = radius ** 2

    cdef float centerX = center[0]
    cdef float centerY = center[1]
    cdef float centerZ = center[2]

    cdef float x, y, z
    cdef float dPx, dPy, dPz

    # Next, each point P of S is tested for inclusion in the current ball (by
    # simply checking that its distance from the center is less than or equal to
    # the radius).
    for i in range(positions.shape[0]):
        x = positions[i, 0]
        y = positions[i, 1]
        z = positions[i, 2]

        dPx = x - centerX
        dPy = y - centerY
        dPz = z - centerZ

        dist2 = (dPx ** 2) + (dPy ** 2) + (dPz ** 2)

        if dist2 <= radius2:
            continue

        # Enlarge ball
        # This is done by drawing a line from Pk+1 to the current center Ck of
        # Bk and extending it further to intersect the far side of Bk.

        # enlarge radius just enough
        dist = np.sqrt(dist2)
        radius = (radius + dist) / 2
        radius2 = radius ** 2

        mult = (dist - radius) / dist
        centerX += (mult * dPx)
        centerY += (mult * dPy)
        centerZ += (mult * dPz)

    return np.array([centerX, centerY, centerZ], dtype=np.float32), radius


# Cython implementation of:
# vertex_normals = np.zeros(positions.shape, dtype=np.float32)
# for triangle, face_norm in zip(indices, weighted_face_normals):
#     for pos in triangle:
#         vertex_normals[pos] += face_norm
def add_vertex_normals(
    np.ndarray[np.uint32_t, ndim=2] indices,
    np.ndarray[np.float64_t, ndim=2] normals,
    np.ndarray[np.float64_t, ndim=2] out):

    cdef long long indices_length = indices.shape[0]
    cdef Py_ssize_t i, j, k
    cdef long long vertex

    for i in range(indices_length):
        for j in range(3):
            for k in range(3):
                vertex = indices[i, j]
                out[vertex, k] += normals[i, k]
