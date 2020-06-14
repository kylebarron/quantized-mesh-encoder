import numpy as np

indices = triangles
def compute_normals(positions, indices):
    # Make sure indices
    indices = indices.reshape(-1, 3)

    # Perform coordinate lookup in positions using indices
    # `coords` is then an array of shape (-1, 3, 3) where each block of (i, 3,
    # 3) represents all the coordinates of a single triangle
    coords = positions[indices]

    a = coords[:, 0, :]
    b = coords[:, 1, :]
    c = coords[:, 2, :]

    normal = np.cross(b - a, c - a)

    # How to aggregate triangles per vertex?
    # I essentially need to do: For every vertex, what are the indices of
    # `indices` that touch that vertex. This is basically a double for loop, or
    # at least a single for loop that does
    #     for i in range(indices.max()):
    #        (indices == i).any(axis=1)
    #
    # That's obviously slow, and I'm not sure how to broadcast, because I'd need
    # to broadcast arrays of two different sizes.
    #
    # https://stackoverflow.com/q/53631460
    # https://stackoverflow.com/q/8251541

    x = np.arange(indices.max())

    # # Pseudo-code
    # references = {}
    # for row in indices.rows():
    #     for value in row:
    #         references[value].append(row_index)
