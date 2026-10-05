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

# Always regenerate the C source. A C file generated in an earlier build may
# target a newer numpy than the one in this build environment (e.g. after
# building for another Python version), and Cython's timestamp check doesn't
# notice when numpy changes.
setup(ext_modules=cythonize(ext_modules, language_level=3, force=True))
