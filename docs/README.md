# DGGRID Create, user guide

DGGRID Create (QDGGS) is a QGIS plugin that generates Discrete Global Grid System (DGGS) cells as vector layers. It is a graphical frontend to DGGRID 9.1, the DGGS software by Kevin Sahr ([documentation](https://dggrid.readthedocs.io/)), and it creates Uber H3 cells with the `h3` Python package. Cells can be generated for an extent, for the polygons of a layer, for the whole earth, or from a list of cell ids. The step-by-step examples are in the [tutorial](TUTORIAL.md).

## Installation

The plugin requires QGIS 3.28 or newer. So far it has been tested with QGIS 3.44 on macOS; Windows and Linux are expected to work, but have not been tested yet.

To install the plugin from a zip file, open Plugins → Manage and Install Plugins → Install from ZIP, select the zip and press Install Plugin. The plugin is then available in the Plugins toolbar and under Plugins → DGGRID Create.

## First start

The plugin needs two external components, and it asks before it downloads or installs anything:

- the DGGRID executable: on first start, the plugin offers to download the portable DGGRID v9.1 build for your platform from [DGGRID_portables](https://github.com/allixender/DGGRID_portables/releases/tag/v9.1), checks it against the published SHA256 checksums and keeps it in the QGIS profile folder (`dggrid_portable/v9.1/`);
- the `h3` Python package: when you select UBER H3 for the first time, the plugin offers to install `h3` with the pip of the QGIS Python into the profile folder (`python/dggrid_deps/`).

Without DGGRID, the dialog still opens, but only UBER H3 can be selected. To use your own DGGRID build instead of the portable one, set the key `dggrid/executable` to the full path of the executable in Settings → Options → Advanced. The plugin uses DGGRID 9.1 parameters, so an older DGGRID (e.g. 8.x from a package manager) does not work.

## Grid types

The DGGS Type list contains the DGGRID presets and Uber H3. Only some of the grids have a hierarchical index, which the plugin needs for cell ids as input:

| DGGS Type | Cells | Cell ids |
|---|---|---|
| ISEA7H, IGEO7v2, FULLER7H | hexagons, aperture 7 | SEQNUM or Z7 |
| ISEA3H, FULLER3H | hexagons, aperture 3 | SEQNUM or Z3 |
| ISEA4H, FULLER4H | hexagons, aperture 4 | SEQNUM or ZORDER |
| ISEA43H, FULLER43H, SUPERFUND, PLANETRISK | hexagons, mixed aperture | SEQNUM |
| ISEA4T, FULLER4T | triangles, aperture 4 | SEQNUM |
| ISEA4D, FULLER4D | diamonds, aperture 4 | SEQNUM |
| UBER H3 | hexagons, aperture 7 | H3 index |

IGEO7v2 is the aperture 7 hexagon grid on the WGS84 ellipsoid with the Z7 index. As in every icosahedron-based hexagon grid, each resolution also contains 12 pentagons. The ISEA and FULLER prefixes refer to the projection that DGGRID uses to place the cells (Icosahedral Snyder Equal Area or Fuller/Dymaxion).

## Cell ids

By default, DGGRID numbers the cells of a resolution sequentially (SEQNUM), and the plugin stores this number as integer in the `global_id` field. For the grids with a hierarchical index, the checkbox Hier. index ids writes the Z7, Z3 or ZORDER index instead, as a digit string (e.g. `00010224545` for an IGEO7v2 cell at resolution 9 in Tartu). The first two digits are the base cell and every further digit is one resolution level, so the resolution of a cell is the length of the id minus two.

The tab Grid Cell From Cell Id generates cells from such ids. It accepts hierarchical ids and H3 ids only, because the plugin does not offer SEQNUM ids as input. The ids can be typed in, loaded from a text or CSV file, or taken from the selected cells of a layer that was generated with Hier. index ids.

## Output

The output is written to the Working Directory. If the field is left empty, the plugin uses the QGIS processing temporary folder, which QGIS deletes when it closes; for results that you want to keep, choose a folder (the plugin remembers it). The output format can be GPKG, SHP, KML, GEOJSON or GML, and with Add grid layer to map the result is loaded as layer, named after grid type and resolution (e.g. `dggrid_isea7h_r9`).

The number of cells grows quickly with the resolution, by the aperture per level (e.g. 1.2 million cells for the whole earth at ISEA7H resolution 6, and 8.2 million at resolution 7). Before a run with an estimated 1,000,000 cells or more, the plugin asks whether to continue.

## Troubleshooting

The plugin writes the full DGGRID output of every run to the QGIS log (View → Panels → Log Messages, tab DGGRID). If DGGRID fails, the error message shows the first FATAL lines of this log. Errors of the plugin itself appear in a QGIS Python error window or in the tab Python warning. Please include both when reporting a problem.
