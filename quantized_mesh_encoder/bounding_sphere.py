"""
Compute bounding spheres

Resources:
https://help.agi.com/AGIComponents/html/BlogBoundingSphere.htm#!
http://geomalgorithms.com/a08-_containers.html

C code for Ritter's algorithm:
http://www.realtimerendering.com/resources/GraphicsGems/gems/BoundSphere.c
"""
import numpy as np


def bounding_sphere(positions, method='naive'):
    if method == 'naive':
        return bounding_sphere_naive(positions)

    if method == 'ritter':
        return bounding_sphere_ritter(positions)

    raise ValueError('Invalid bounding sphere method')


def bounding_sphere_ritter(positions):
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
        positions[max_z_idx], ]

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


def bounding_sphere_naive(positions):
    """Naive bounding sphere method

    1. Find axis-aligned bounding box,
    2. Find center of box
    3. Radius is distance back to corner
    """
    bbox = axis_aligned_bounding_box(positions)
    center = np.average(bbox, axis=0)
    radius = np.linalg.norm(center - bbox[0, :])
    return center, radius


def axis_aligned_bounding_box(positions):
    return np.vstack([np.amin(positions, 0), np.amax(positions, 0)])
