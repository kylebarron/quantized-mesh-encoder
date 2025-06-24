# Changelog

## [0.5.0] - 2025-06-24

- Support numpy v2
- Refreshed wheel builds

## [0.4.3] - 2022-11-18

- PEP 518-compliant with `pyproject.toml` and `build-system`

## [0.4.2] - 2021-12-05

- Build wheels for Python 3.10
- Use `oldest-supported-numpy` in wheel builds for greatest compatibility

## [0.4.1] - 2021-08-08

- Fix wheel builds on CI

## [0.4.0] - 2021-08-08

- Add support for Terrain Lighting, Water Mask, and Metadata extensions
- Vertex normals computation as part of Terrain Lighting extension
- Configurable Ellipsoid support
- Improved mypy typing

## [0.3.1] - 2020-10-19

- Add pyx file to sdist
- Use Github Actions for CI testing

## [0.3.0] - 2020-10-05

- Allow 2D input for both `positions` and `indices`

## [0.2.2] - 2020-07-10

- Don't build wheels for PyPy. See https://github.com/joerick/cibuildwheel/issues/402

## [0.2.1] - 2020-07-09

- Try to rebuild wheels

## [0.2.0] - 2020-07-01

- New methods for creating a bounding sphere. #10

## [0.1.2] - 2020-06-01

- Try again to publish to PyPI directly

## [0.1.1] - 2020-06-01

- Try building wheels on CI with `cibuildwheel`

## [0.1.0] - 2020-05-30

- Initial release
