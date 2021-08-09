import attr


@attr.s
class Ellipsoid:
    """Ellipsoid used for mesh calculations

    Args:
        a (float): semi-major axis
        b (float): semi-minor axis
    """

    a: float = attr.ib()
    b: float = attr.ib()
    e2: float = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.e2 = 1 - (self.b ** 2 / self.a ** 2)
