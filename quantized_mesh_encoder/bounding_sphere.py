"""
Compute bounding spheres

Resources:
https://help.agi.com/AGIComponents/html/BlogBoundingSphere.htm#!
http://geomalgorithms.com/a08-_containers.html

C code for Ritter's algorithm:
http://www.realtimerendering.com/resources/GraphicsGems/gems/BoundSphere.c
"""
import numpy as np

from .util_cy import ritter_second_pass


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

    Slowest, but overall still quite fast: 304µs
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

    # Compute x-, y-, and z-spans (distances between each component's min. and
    # max.).
    x_span = np.linalg.norm(bbox[0] - bbox[3])
    y_span = np.linalg.norm(bbox[1] - bbox[4])
    z_span = np.linalg.norm(bbox[2] - bbox[5])

    # Find largest span
    l = [x_span, y_span, z_span]
    max_idx = l.index(max(l))

    # Get the two bounding points with the selected dimension
    min_pt = bbox[max_idx]
    max_pt = bbox[max_idx + 3]

    # Calculate the center and radius of the initial sphere found by Ritter's
    # algorithm
    center = (min_pt + max_pt) / 2
    radius = np.linalg.norm(max_pt - center)

    return ritter_second_pass(positions, center, radius)


def bounding_sphere_from_bounding_box(positions):
    """Create bounding sphere from axis aligned bounding box

    1. Find axis-aligned bounding box,
    2. Find center of box
    3. Radius is distance back to corner

    Fastest method; around 70 µs
    """
    bbox = axis_aligned_bounding_box(positions)
    center = np.average(bbox, axis=0)
    radius = np.linalg.norm(center - bbox[0, :])
    return center, radius


def bounding_sphere_naive(positions):
    """Create bounding sphere by checking all points

    1. Find axis-aligned bounding box,
    2. Find center of box
    3. Find distance from center of box to every position: radius is max

    Still very fast method, with tighter radius; around 160 µs
    """
    bbox = axis_aligned_bounding_box(positions)
    center = np.average(bbox, axis=0)
    radius = np.linalg.norm(center - positions, axis=1).max()
    return center, radius


def axis_aligned_bounding_box(positions):
    return np.vstack([np.amin(positions, 0), np.amax(positions, 0)])
