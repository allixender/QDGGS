# QGIS - DGGS

DGGRID Create is a QGIS plugin (QGIS 3.28 or newer) that generates Discrete Global Grid System (DGGS) cells as vector layers. It is a frontend to [DGGRID](https://dggrid.readthedocs.io/) 9.1, which the plugin downloads as portable build on first start, and it creates Uber H3 cells with the `h3` Python package. Cells can be generated for an extent, for the polygons of a layer, for the whole earth or from a list of hierarchical cell ids (Z7, Z3, ZORDER or H3).

The documentation consists of two parts:

- [User guide](docs/README.md): installation, grid types, cell ids, output and troubleshooting;
- [Tutorial](docs/TUTORIAL.md): five worked examples, from a plain grid for the map extent to custom DGGRID metafiles.
