# quantized-mesh-encoder

[![Build Status](https://travis-ci.org/kylebarron/quantized-mesh-encoder.svg?branch=master)](https://travis-ci.org/kylebarron/quantized-mesh-encoder)

A fast Python Quantized Mesh encoder. Encodes a mesh with 100k coordinates and
180k triangles in 20ms.

## Overview

[Quantized Mesh][quantized_mesh_spec] is a format to encode terrain meshes for
efficient client-side terrain rendering. Such files are supported in
[Cesium][cesium] and [deck.gl][deck.gl] (as of release 8.2, expected July 2020.)

This library is designed to support performant server-side on-demand terrain
mesh generation.

[quantized_mesh_spec]: https://github.com/CesiumGS/quantized-mesh
[cesium]: https://github.com/CesiumGS/cesium
[deck.gl]: https://deck.gl/

## Install

```
pip install numpy Cython
pip install quantized-mesh-encoder
```

Cython is used internally, and currently only source builds are provided, so
you'll need to have Cython and a C compiler available during installation.
Additionally Numpy must already exist during install. Pull requests are welcome
to package as platform-specific wheels.

## Using

### API

#### `encode`

Parameters:

- `f`: a file object in which to write encoded bytes
- `positions`: (`array[float]`): a flat Numpy array of 3D positions.
- `indices` (`array[int]`): a flat Numpy array indicating triples of coordinates
  from `positions` to make triangles. For example, if the first three values of
  `indices` are `0`, `1`, `2`, then that defines a triangle formed by the first
  9 values in `positions`, three for the first vertex (index `0`), three for the
  second vertex, and three for the third vertex.
- `bounds` (`List[float]`, optional): a list of bounds, `[minx, miny, maxx, maxy]`. By default, inferred as the minimum and maximum values of `positions`.

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
martini = Martini(257)
# generate RTIN hierarchy from terrain data (an array of size^2 length)
tile = martini.create_tile(terrain)
# get a mesh (vertices and triangles indices) for a 10m error
vertices, triangles = tile.get_mesh(10)
buf = BytesIO()
encode(buf, vertices, triangles)
```

## License

Much of this code is ported or derived from
[`quantized-mesh-tile`][quantized-mesh-tile] in some way. `quantized-mesh-tile`
is also released under the MIT license.

[pymartini]: https://github.com/kylebarron/pymartini
[quantized-mesh-tile]: https://github.com/loicgasser/quantized-mesh-tile
