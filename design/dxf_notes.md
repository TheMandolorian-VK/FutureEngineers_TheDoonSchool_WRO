# Cut File Notes: wooden_plate.dxf

The cut file [wooden_plate.dxf](wooden_plate.dxf) is the version-controlled 2D geometry for the laser-cut plywood decks. These notes document exactly what the file contains today, so nothing is implied that is not in the file.

## File facts

| Item | Value |
| --- | --- |
| Format | DXF, AC1021 (AutoCAD 2004) |
| Units | Millimetres (INSUNITS 4) |
| Geometry | One closed LWPOLYLINE rectangle |
| Rectangle corners | (216.5, 89.5) to (66.5, 209.5) |
| Rectangle size | 150 x 120 mm |
| Layers | Layer 0 / Layer_0, line type Continuous |

## What this means

The committed file currently carries a single rectangular test outline (150 x 120 mm). It is a placeholder for the cut geometry, not the full deck patterns. The full lower- and upper-deck patterns, cut layers, kerf compensation and power/speed settings live in the LightBurn project (`.lbrn`).

## Plan to make the file authoritative

1. Export the full lower- and upper-deck patterns from the LightBurn master into this DXF (or add the `.lbrn` to the repository alongside it).
2. Record the cutter power/speed settings and kerf compensation in the file notes so the decks re-cut identically.
3. Commit the updated file and reference the geometry from the [design overview](README.md).
4. Photograph the cut decks against the drawing for the [engineering journal](../docs/engineering_journal/README.md).

Until step 1 is done, treat this DXF as a placeholder: do not claim the chassis is reproducible from the repository alone.

## Related documents

- [Design overview](README.md), chassis section
- [Laser cutter setup](laser_cutter_setup.md)
- [Assembly guide](assembly_guide.md)
