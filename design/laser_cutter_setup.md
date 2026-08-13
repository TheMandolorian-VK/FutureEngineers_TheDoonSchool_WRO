# Laser Cutter Setup

Procedure for cutting the plywood decks on the school laser cutter. Following this exactly is what makes the chassis reproducible (Criterion 5). The specific power/speed values are recorded in the LightBurn master and are copied here when they are confirmed on the school machine.

## Material

- 3 mm plywood, flat and dry, sheet slightly larger than the part.
- Check for knots or voids in the cut area before loading; they change the cut quality.

## Machine prep

1. Open the cutting file in LightBurn (the DXF geometry, or the `.lbrn` master when it is in the repo).
2. Confirm the file units are millimetres.
3. Set the origin to the lower-left of the sheet.
4. Run a focus and a small test cut on a scrap corner before the real cut.
5. Set the power/speed for 3 mm plywood (values recorded in the `.lbrn`); if not yet confirmed, do a kerf test first.

## Kerf

- Cut a short slot in scrap, measure the slot width, and set the kerf compensation in LightBurn so the parts come out at the drawn size.
- The kerf value is noted in the `.lbrn` and should be written here once measured on the school machine.

## Cutting

- Cut the lower deck and upper deck separately.
- Monitor the cut; plywood can flare if the speed is too low or the focus drifts.
- Let the parts cool before handling; the edges are hot.

## After the cut

1. Check the parts against the drawing dimensions with a ruler or callipers.
2. Fit check: parts should slide together without forcing and without play at the standoff holes.
3. Apply two thin coats of clear varnish to the cut edges (see [assembly guide](assembly_guide.md)).
4. Photograph the decks and the cutting setup into [images/testing/](../images/testing/README.md).
5. Note the measured kerf and power/speed in the [engineering journal](../docs/engineering_journal/README.md).

## Safety

- Keep the machine supervised for the whole cut.
- Keep the exhaust running; do not open the lid until the job ends.
- No flammable materials near the bed while cutting.

## Related documents

- [Cut file notes](dxf_notes.md)
- [Assembly guide](assembly_guide.md)
- [Design overview](README.md), chassis section
