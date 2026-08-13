# Mass Budget

Component mass estimates for the WRO 2026 Future Engineers vehicle. All figures are **design estimates** from datasheets and quoted part weights. Nothing here is a weighed value; the whole budget is confirmed with a scale once the vehicle is assembled.

## Budget

| Component | Est. mass (g) | Notes |
| --- | --- | --- |
| Two plywood decks + brass standoffs | 120 | 3 mm plywood, 4-6 standoffs |
| 11 V 3S LiPo battery | 150 | Sole energy source |
| N20 6 V motor + gearbox | 30 | Rear drive |
| MG996R servo | 55 | Steering |
| Raspberry Pi 4B | 46 | Vision and decisions |
| Camera Module 3 Wide | 25 | Upper deck, forward |
| ESP32 dev board | 25 | Real-time control |
| TB6612FNG driver + wiring | 15 | Motor/servo driver |
| Four wheels (front ~40 mm, rear ~30 mm) | 60 | Rear wheels smaller |
| LEGO rails and mounting hardware | 150 | 8 mm grid mounting |
| Misc (screws, tie rods, connectors) | 100 | Hardware allowance |
| **Estimated total** | **776** | Under the 1.5 kg limit |

## Margin

The rule limit is 1.5 kg (1500 g). The estimate leaves roughly 720 g of margin, which is reserved for:

- wiring and cable ties not yet accounted for,
- the 3D-printed steering knuckles,
- the camera bracket and any brackets made during integration,
- spare-fastener weight during field repairs.

If the weighed total approaches 1.4 kg the first candidates to trim are the LEGO rail allowance and the hardware allowance, not the battery or the drive train.

## Centre of gravity

The CG is intended to sit low and slightly rearward:

- The battery sits on the lower deck at the rear, and the N20 motor is at the rear axle. Together they pull the CG rearward.
- The steering assembly (servo, knuckles, tie rod) is lighter than the drive end, so the front stays light.
- Lower-deck mass keeps the CG low, which limits body roll through corners.

A rear-biased low CG is a deliberate design choice for stability in the 90° corners, not an accident of layout. Once built, the CG is checked by balancing the vehicle on a thin fulcrum fore and aft of the axles and recorded in the [engineering journal](../docs/engineering_journal/README.md).

## Related documents

- [Design overview](README.md), design targets and mass section
- [Mechanical BOM](bom_mechanical.md)
- [Rule compliance checklist](rules_checklist.md)
