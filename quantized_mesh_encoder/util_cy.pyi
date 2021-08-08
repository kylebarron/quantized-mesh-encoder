# pylint: disable=unused-argument
from typing import Tuple

import numpy as np  # isort: skip

def encode_indices(indices: np.ndarray) -> np.ndarray: ...
def ritter_second_pass(
    positions: np.ndarray, center: np.ndarray, radius: float
) -> Tuple[np.ndarray, float]: ...
def add_vertex_normals(
    indices: np.ndarray, normals: np.ndarray, out: np.ndarray
) -> None: ...
