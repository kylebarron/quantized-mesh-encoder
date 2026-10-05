"""Compute bounding spheres.

Resources:
https://help.agi.com/AGIComponents/html/BlogBoundingSphere.htm#!
http://geomalgorithms.com/a08-_containers.html

C code for Ritter's algorithm:
http://www.realtimerendering.com/resources/GraphicsGems/gems/BoundSphere.c

Math.gl:
https://github.com/uber-web/math.gl/blob/master/modules/culling/src/algorithms/bounding-sphere-from-points.js
"""

from __future__ import annotations

import numpy as np

from .util_cy import ritter_second_pass


def bounding_sphere(
    positions: np.ndarray, *, method: str | None = None
) -> tuple[np.ndarray, float]:
    """Create bounding sphere from positions.

    Args:
        positions: An array of shape (-1, 3) and of dtype np.float32 with 3D
            positions.

    Keyword Args:
        method: A string designating the algorithm to use for creating the
            bounding sphere. Must be one of `'bounding_box'`, `'naive'`,
            `'ritter'` or `None`.

            - `'bounding_box'`: Finds the bounding box of all positions, then
              defines the center of the sphere as the center of the bounding
              box, and defines the radius as the distance back to the corner.
              This method produces the largest bounding sphere, but is the
              fastest: roughly 70 µs on my computer.
            - `'naive'`: Finds the bounding box of all positions, then defines
              the center of the sphere as the center of the bounding box. It
              then checks the distance to every other point and defines the
              radius as the maximum of these distances. This method will
              produce a slightly smaller bounding sphere than the
              `bounding_box` method when points are not in the 3D corners.
              This is the next fastest at roughly 160 µs on my computer.
            - `'ritter'`: Implements the Ritter Method for bounding spheres. It
              first finds the center of the longest span, then checks every
              point for containment, enlarging the sphere if necessary. This
              _can_ produce smaller bounding spheres than the naive method, but
              it does not always, so often both are run, see next option. This
              is the slowest method, at roughly 300 µs on my computer.
            - `None`: Runs both the naive and the ritter methods, then returns
              the smaller of the two. Since this runs both algorithms, it takes
              around 500 µs on my computer.

    Returns:
        A tuple of `(center, radius)`, where `center` is a Numpy array of
        length 3 representing the center of the bounding sphere, and `radius`
        is a float representing the radius of the bounding sphere.

    """
    if method == "bounding_box":
        return bounding_sphere_from_bounding_box(positions)

    if method == "naive":
        return bounding_sphere_naive(positions)

    if method == "ritter":
        return bounding_sphere_ritter(positions)

    # Defaults to both ritter and naive, and choosing the one with smaller
    # radius
    naive_center, naive_radius = bounding_sphere_naive(positions)
    ritter_center, ritter_radius = bounding_sphere_ritter(positions)

    if naive_radius < ritter_radius:
        return naive_center, naive_radius

    return ritter_center, ritter_radius


def bounding_sphere_ritter(positions: np.ndarray) -> tuple[np.ndarray, float]:
    """Create bounding sphere with Ritter's algorithm.

    1. Find points containing minimum and maximum of each dimension.
    2. Pick pair with maximum distance.

    Slowest, but overall still quite fast: 304 µs.

    Args:
        positions: An array of shape (-1, 3) with 3D positions.

    Returns:
        A tuple of `(center, radius)` of the bounding sphere.

    """
    # The Cython second pass only accepts float32. Positions may be float64,
    # e.g. ECEF positions computed with an Ellipsoid holding numpy float64
    # scalars, which numpy 2 no longer demotes to float32.
    positions = positions.astype(np.float32, copy=False)

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

    # Compute x-, y-, and z-spans (distances between each component's min. and
    # max.).
    x_span = np.linalg.norm(bbox[0] - bbox[3])
    y_span = np.linalg.norm(bbox[1] - bbox[4])
    z_span = np.linalg.norm(bbox[2] - bbox[5])

    # Find largest span
    spans = [x_span, y_span, z_span]
    max_idx = spans.index(max(spans))

    # Get the two bounding points with the selected dimension
    min_pt = bbox[max_idx]
    max_pt = bbox[max_idx + 3]

    # Calculate the center and radius of the initial sphere found by Ritter's
    # algorithm
    center = (min_pt + max_pt) / 2
    radius = np.linalg.norm(max_pt - center)

    return ritter_second_pass(positions, center, radius)


def bounding_sphere_from_bounding_box(
    positions: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Create bounding sphere from axis aligned bounding box.

    1. Find axis-aligned bounding box.
    2. Find center of box.
    3. Radius is distance back to corner.

    Fastest method; around 70 µs.

    Args:
        positions: An array of shape (-1, 3) with 3D positions.

    Returns:
        A tuple of `(center, radius)` of the bounding sphere.

    """
    bbox = axis_aligned_bounding_box(positions)
    center = np.average(bbox, axis=0)
    radius = np.linalg.norm(center - bbox[0, :])
    return center, radius


def bounding_sphere_naive(positions: np.ndarray) -> tuple[np.ndarray, float]:
    """Create bounding sphere by checking all points.

    1. Find axis-aligned bounding box.
    2. Find center of box.
    3. Find distance from center of box to every position: radius is max.

    Still very fast method, with tighter radius; around 160 µs.

    Args:
        positions: An array of shape (-1, 3) with 3D positions.

    Returns:
        A tuple of `(center, radius)` of the bounding sphere.

    """
    bbox = axis_aligned_bounding_box(positions)
    center = np.average(bbox, axis=0)
    radius = np.linalg.norm(center - positions, axis=1).max()
    return center, radius


def axis_aligned_bounding_box(positions: np.ndarray) -> np.ndarray:
    """Compute the axis-aligned bounding box of positions.

    Args:
        positions: An array of shape (-1, 3) with 3D positions.

    Returns:
        An array of shape (2, 3), where the first row holds the minimum of each
        dimension and the second row the maximum.

    """
    return np.vstack([np.amin(positions, 0), np.amax(positions, 0)])
