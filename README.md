# quantized-mesh-encoder

[![Build Status](https://travis-ci.org/kylebarron/quantized-mesh-encoder.svg?branch=master)](https://travis-ci.org/kylebarron/quantized-mesh-encoder)

A fast Python [Quantized Mesh][quantized_mesh_spec] encoder. Encodes a mesh with
100k coordinates and 180k triangles in 20ms. [Example viewer][example].

[![][image_url]][example]

[image_url]: https://raw.githubusercontent.com/kylebarron/quantized-mesh-encoder/master/assets/no-texture-example.jpg
[example]: https://kylebarron.dev/quantized-mesh-encoder

The Grand Canyon and Walhalla Plateau. The mesh is created using
[`pymartini`][pymartini], encoded using `quantized-mesh-encoder`, served
on-demand using [`dem-tiler`][dem-tiler], and rendered with
[deck.gl](https://deck.gl).

[pymartini]: https://github.com/kylebarron/pymartini
[dem-tiler]: https://github.com/kylebarron/dem-tiler

## Overview

[Quantized Mesh][quantized_mesh_spec] is a format to encode terrain meshes for
efficient client-side terrain rendering. Such files are supported in
[Cesium][cesium] and [deck.gl][deck.gl].

This library is designed to support performant server-side on-demand terrain
mesh generation.

[quantized_mesh_spec]: https://github.com/CesiumGS/quantized-mesh
[cesium]: https://github.com/CesiumGS/cesium
[deck.gl]: https://deck.gl/

## Install

```
pip install quantized-mesh-encoder
```

## Using

### API

#### `encode`

Parameters:

- `f`: a writable file-like object in which to write encoded bytes
- `positions`: (`array[float]`): a flat Numpy array of 3D positions.
- `indices` (`array[int]`): a flat Numpy array indicating triples of coordinates
  from `positions` to make triangles. For example, if the first three values of
  `indices` are `0`, `1`, `2`, then that defines a triangle formed by the first
  9 values in `positions`, three for the first vertex (index `0`), three for the
  second vertex, and three for the third vertex.
- `bounds` (`List[float]`, optional): a list of bounds, `[minx, miny, maxx, maxy]`. By default, inferred as the minimum and maximum values of `positions`.
- `sphere_method` (`str`, optional): As part of the header information when
  encoding Quantized Mesh, it's necessary to compute a [_bounding
  sphere_][bounding_sphere], which contains all positions of the mesh.
  `sphere_method` designates the algorithm to use for creating the bounding
  sphere. Must be one of `'bounding_box'`, `'naive'`, `'ritter'` or `None`.
  Default is `None`.
    - `'bounding_box'`: Finds the bounding box of all positions, then defines
      the center of the sphere as the center of the bounding box, and defines
      the radius as the distance back to the corner. This method produces the
      largest bounding sphere, but is the fastest: roughly 70 µs on my computer.
    - `'naive'`: Finds the bounding box of all positions, then defines the
      center of the sphere as the center of the bounding box. It then checks the
      distance to every other point and defines the radius as the maximum of
      these distances. This method will produce a slightly smaller bounding
      sphere than the `bounding_box` method when points are not in the 3D
      corners. This is the next fastest at roughly 160 µs on my computer.
    - `'ritter'`: Implements the Ritter Method for bounding spheres. It first
      finds the center of the longest span, then checks every point for
      containment, enlarging the sphere if necessary. This _can_ produce smaller
      bounding spheres than the naive method, but it does not always, so often
      both are run, see next option. This is the slowest method, at roughly 300
      µs on my computer.
    - `None`: Runs both the naive and the ritter methods, then returns the
      smaller of the two. Since this runs both algorithms, it takes around 500
      µs on my computer


[bounding_sphere]: https://en.wikipedia.org/wiki/Bounding_sphere

### Examples

#### Write to file

```py
from quantized_mesh_encoder import encode
with open('output.terrain', 'wb') as f:
    encode(f, positions, indices)
```

Quantized mesh files are usually saved gzipped. An easy way to create a gzipped
file is to use `gzip.open`:

```py
import gzip
from quantized_mesh_encoder import encode
with gzip.open('output.terrain', 'wb') as f:
    encode(f, positions, indices)
```

#### Write to buffer

It's also pretty simple to write to a buffer instead of a file

```py
from io import BytesIO
from quantized_mesh_encoder import encode
buf = BytesIO()
encode(buf, positions, indices)
```

To read the bytes out of the buffer, e.g. to gzip the buffer

```py
import zlib
buf.seek(0)
out_bytes = zlib.compress(buf.read())
```

#### Generating the mesh

To encode a mesh into a quantized mesh file, you first need a mesh! This project
was designed to be used with [`pymartini`][pymartini], a fast elevation
heightmap to terrain mesh generator.

```py
import quantized_mesh_encoder
from imageio import imread
from pymartini import decode_ele, Martini, rescale_positions
import mercantile

png = imread(png_path)
terrain = decode_ele(png, 'terrarium')
terrain = terrain.T
martini = Martini(png.shape[0] + 1)
tile = martini.create_tile(terrain)
vertices, triangles = tile.get_mesh(10)

# Use mercantile to find the bounds in WGS84 of this tile
bounds = mercantile.bounds(mercantile.Tile(x, y, z))

# Rescale positions to WGS84
rescaled = rescale_positions(
    vertices,
    terrain,
    bounds=bounds,
    flip_y=True
)

with BytesIO() as f:
    quantized_mesh_encoder.encode(f, rescaled, triangles)
    f.seek(0)
    return ("OK", "application/vnd.quantized-mesh", f.read())
```

You can also look at the source of
[`_mesh()`](https://github.com/kylebarron/dem-tiler/blob/5b50a216a014eb32febee84fe3063ca99e71c7f6/dem_tiler/handlers/app.py#L234)
in [`dem-tiler`][dem-tiler] for a working reference.

## License

Much of this code is ported or derived from
[`quantized-mesh-tile`][quantized-mesh-tile] in some way. `quantized-mesh-tile`
is also released under the MIT license.

[pymartini]: https://github.com/kylebarron/pymartini
[quantized-mesh-tile]: https://github.com/loicgasser/quantized-mesh-tile
