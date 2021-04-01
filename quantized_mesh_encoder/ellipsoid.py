import attr


@attr.s
class Ellipsoid:
    a: float = attr.ib()
    b: float = attr.ib()
    e2: float = attr.ib(init=False)

    def __attrs_post_init__(self):
        self.e2 = 1 - (self.b ** 2 / self.a ** 2)
