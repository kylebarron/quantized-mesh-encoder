## Install

Install the package, including its Cython extension, and the development dependencies:

```
uv sync
```

After changing the Cython source in `quantized_mesh_encoder/util_cy.pyx`, rebuild with:

```
uv sync --reinstall-package quantized-mesh-encoder
```

## Test

```
uv run pytest
```
