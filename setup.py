"""Build configuration for the `util_cy` Cython extension.

Project metadata lives in pyproject.toml. This file only declares the Cython
extension, which setuptools can't yet configure from pyproject.toml alone.
"""

import numpy as np
from Cython.Build import cythonize
from setuptools import Extension, setup

ext_modules = [
    Extension(
        "quantized_mesh_encoder.util_cy",
        ["quantized_mesh_encoder/util_cy.pyx"],
        # Compile against the numpy C headers
        include_dirs=[np.get_include()],
    ),
]

setup(ext_modules=cythonize(ext_modules, language_level=3))
