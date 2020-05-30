import numpy as np


def bounding_sphere(positions):
    """
    Implements Ritter's algorithm

    1. Find points containing minimum and maximum of each dimension.
    2. Pick pair with maximum distance

    """
    # Find points containing smallest and largest component
    min_x_idx = np.where(positions[:, 0] == positions[:, 0].min())[0][0]
    min_y_idx = np.where(positions[:, 1] == positions[:, 1].min())[0][0]
    min_z_idx = np.where(positions[:, 2] == positions[:, 2].min())[0][0]
    max_x_idx = np.where(positions[:, 0] == positions[:, 0].max())[0][0]
    max_y_idx = np.where(positions[:, 1] == positions[:, 1].max())[0][0]
    max_z_idx = np.where(positions[:, 2] == positions[:, 2].max())[0][0]

    bbox = [
        positions[min_x_idx],
        positions[min_y_idx],
        positions[min_z_idx],
        positions[max_x_idx],
        positions[max_y_idx],
        positions[max_z_idx],
    ]

    # Pick the pair with the maximum point-to-point separation
    # (which could be greater than the maximum dimensional span)
    # First find which dimension this is in
    x_span = np.linalg.norm(bbox[0] - bbox[3])
    y_span = np.linalg.norm(bbox[1] - bbox[4])
    z_span = np.linalg.norm(bbox[2] - bbox[5])
    l = [x_span, y_span, z_span]
    max_idx = l.index(max(l))

    # Get the two bounding points with the selected dimension
    min_pt = bbox[max_idx]
    max_pt = bbox[max_idx + 3]

    center = (min_pt + max_pt) / 2
    radius = np.linalg.norm(max_pt - center)

    # TODO: loop through points a second time, testing for containment in sphere

    return center, radius
