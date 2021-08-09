# quantized-mesh-encoder

[![Build Status](https://travis-ci.org/kylebarron/quantized-mesh-encoder.svg?branch=master)](https://travis-ci.org/kylebarron/quantized-mesh-encoder)

A fast Python [Quantized Mesh][quantized_mesh_spec] encoder. Encodes a mesh with
100k coordinates and 180k triangles in 20ms. [Example viewer][example].

[![][image_url]][example]

[image_url]: https://raw.githubusercontent.com/kylebarron/quantized-mesh-encoder/master/assets/no-texture-example.jpg
[example]: https://kylebarron.dev/quantized-mesh-encoder

The Grand Canyon and Walhalla Plateau. The mesh is created using
[`pydelatin`][pydelatin] or [`pymartini`][pymartini], encoded using
`quantized-mesh-encoder`, served on-demand using [`dem-tiler`][dem-tiler], and
rendered with [deck.gl](https://deck.gl).

[pymartini]: https://github.com/kylebarron/pymartini
[pydelatin]: https://github.com/kylebarron/pydelatin
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

With pip:

```
pip install quantized-mesh-encoder
```

or with Conda:

```
conda install -c conda-forge quantized-mesh-encoder
```

## Using

### API

#### `quantized_mesh_encoder.encode`

Arguments:

- `f`: a writable file-like object in which to write encoded bytes
- `positions`: (`array[float]`): either a 1D Numpy array or a 2D Numpy array of
  shape `(-1, 3)` containing 3D positions.
- `indices` (`array[int]`): either a 1D Numpy array or a 2D Numpy array of shape
  `(-1, 3)` indicating triples of coordinates from `positions` to make
  triangles. For example, if the first three values of `indices` are `0`, `1`,
  `2`, then that defines a triangle formed by the first 9 values in `positions`,
  three for the first vertex (index `0`), three for the second vertex, and three
  for the third vertex.

Keyword arguments:

- `bounds` (`List[float]`, optional): a list of bounds, `[minx, miny, maxx,
  maxy]`. By default, inferred as the minimum and maximum values of `positions`.
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
- `ellipsoid` (`quantized_mesh_encoder.Ellipsoid`, optional): ellipsoid defined by its semi-major `a`
   and semi-minor `b` axes.
   Default: WGS84 ellipsoid.
- extensions: list of extensions to encode in quantized mesh object. These must be `Extension` instances. See [Quantized Mesh Extensions](#quantized-mesh-extensions).


[bounding_sphere]: https://en.wikipedia.org/wiki/Bounding_sphere

#### `quantized_mesh_encoder.Ellipsoid`

Ellipsoid used for mesh calculations.

Arguments:

- `a` (`float`): semi-major axis
- `b` (`float`): semi-minor axis

#### `quantized_mesh_encoder.WGS84`

Default [WGS84 ellipsoid](https://en.wikipedia.org/wiki/World_Geodetic_System#1984_version). Has a semi-major axis `a` of 6378137.0 meters and semi-minor axis `b` of 6356752.3142451793 meters.

#### Quantized Mesh Extensions

There are a variety of [extensions](https://github.com/CesiumGS/quantized-mesh#extensions) to the Quantized Mesh spec.

##### `quantized_mesh_encoder.VertexNormalsExtension`

Implements the [Terrain Lighting](https://github.com/CesiumGS/quantized-mesh#terrain-lighting) extension. Per-vertex normals will be generated from your mesh data.

Keyword Arguments:

- `indices`: mesh indices
- `positions`: mesh positions
- `ellipsoid`: instance of Ellipsoid class, default: WGS84 ellipsoid

##### `quantized_mesh_encoder.WaterMaskExtension`

Implements the [Water Mask](https://github.com/CesiumGS/quantized-mesh#water-mask) extension.

Keyword Arguments:

- `data` (`Union[np.ndarray, np.uint8, int]`): Data for water mask.

##### `quantized_mesh_encoder.MetadataExtension`

Implements the [Metadata](https://github.com/CesiumGS/quantized-mesh#metadata) extension.

- `data` (`Union[Dict, bytes]`): Metadata data to encode. If a dictionary, `json.dumps` will be called to create bytes in UTF-8 encoding.

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

It's also pretty simple to write to an in-memory buffer instead of a file

```py
from io import BytesIO
from quantized_mesh_encoder import encode
with BytesIO() as bio:
    encode(bio, positions, indices)
```

Or to gzip the in-memory buffer:

```py
import gzip
from io import BytesIO
with BytesIO() as bio:
    with gzip.open(bio, 'wb') as gzipf:
        encode(gzipf, positions, indices)
```


#### Alternate Ellipsoid

By default, the [WGS84
ellipsoid](https://en.wikipedia.org/wiki/World_Geodetic_System#1984_version) is
used for all calculations. An alternate ellipsoid may be useful for non-Earth
planetary bodies.

```py
from quantized_mesh_encoder import encode, Ellipsoid

# From https://ui.adsabs.harvard.edu/abs/2010EM%26P..106....1A/abstract
mars_ellipsoid = Ellipsoid(3_395_428, 3_377_678)

with open('output.terrain', 'wb') as f:
    encode(f, positions, indices, ellipsoid=mars_ellipsoid)
```

#### Quantized Mesh Extensions

```py
from quantized_mesh_encoder import encode, VertexNormalsExtension, MetadataExtension

vertex_normals = VertexNormalsExtension(positions=positions, indices=indices)
metadata = MetadataExtension(data={'hello': 'world'})

with open('output.terrain', 'wb') as f:
    encode(f, positions, indices, extensions=(vertex_normals, metadata))
```

#### Generating the mesh

To encode a mesh into a quantized mesh file, you first need a mesh! This project
was designed to be used with [`pydelatin`][pydelatin] or
[`pymartini`][pymartini], fast elevation heightmap to terrain mesh generators.

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
