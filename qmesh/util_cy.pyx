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
