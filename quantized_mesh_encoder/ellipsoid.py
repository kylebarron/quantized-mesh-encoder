
from dataclasses import dataclass, field

@dataclass
class Ellipsoid:
    a: float
    b: float
    e2: float = field(init=False)

    def __post_init__(self):
        self.e2 = 1 - (self.b**2 / self.a**2)

