"""Reference ellipsoid used for mesh calculations."""

import attr


@attr.s
class Ellipsoid:
    """Ellipsoid used for mesh calculations.

    Attributes:
        a: Semi-major axis.
        b: Semi-minor axis.
        e2: Square of the first eccentricity, computed from `a` and `b`.

    """

    a: float = attr.ib()
    b: float = attr.ib()
    e2: float = attr.ib(init=False)

    def __attrs_post_init__(self) -> None:
        """Compute the squared eccentricity from the axes."""
        self.e2 = 1 - (self.b**2 / self.a**2)
