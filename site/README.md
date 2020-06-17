## Quantized Mesh Example

This folder contains a simple example and viewer of quantized mesh tiles that
are generated in a serverless AWS Lambda function.

It uses [`pymartini`][pymartini] for mesh generation, `quantized-mesh-encoder`
for encoding to quantized mesh, [`dem-tiler`][dem-tiler] for the serverless API,
and [`deck.gl`](https://deck.gl) for rendering. You can also easily overlay a
texture source, e.g. Mapbox Satellite tiles, with deck.gl.

[pymartini]: https://github.com/kylebarron/pymartini
[dem-tiler]: https://github.com/kylebarron/dem-tiler
