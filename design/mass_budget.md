# Mass Budget

Component masses to be measured once the vehicle is assembled. The rule limit is 1.5 kg (Rules 11.1-11.2).

## Budget (to be filled in with a scale)

| Component | Measured mass (g) | Notes |
| --- | --- | --- |
| Two plywood decks + brass standoffs | TBD | 3 mm plywood, 4-6 standoffs |
| 11 V 3S LiPo battery | TBD | Sole energy source |
| N20 6 V motor + gearbox | TBD | Rear drive |
| MG996R servo | TBD | Steering |
| Raspberry Pi 4B | TBD | Vision and decisions |
| Camera Module 3 Wide | TBD | Upper deck, forward |
| ESP32 dev board | TBD | Real-time control |
| TB6612FNG driver + wiring | TBD | Motor/servo driver |
| Four wheels (front ~40 mm, rear ~30 mm) | TBD | Rear wheels smaller |
| LEGO rails and mounting hardware | TBD | 8 mm grid mounting |
| Misc (screws, tie rods, connectors) | TBD | Hardware allowance |
| **Total** | **TBD** | Must be under 1.5 kg |

## Procedure

1. Weigh each component individually on a digital scale.
2. Record the value in this table.
3. Sum the total and confirm it is under 1.5 kg.
4. Log the result in the [engineering journal](../docs/engineering_journal/README.md).

## Centre of gravity

The CG is intended to sit low and slightly rearward:

- The battery sits on the lower deck at the rear, and the N20 motor is at the rear axle. Together they pull the CG rearward.
- The steering assembly (servo, knuckles, tie rod) is lighter than the drive end, so the front stays light.
- Lower-deck mass keeps the CG low, which limits body roll through corners.

Once built, the CG is checked by balancing the vehicle on a thin fulcrum fore and aft of the axles and recorded in the [engineering journal](../docs/engineering_journal/README.md).

## Related documents

- [Design overview](README.md), design targets and mass section
- [Mechanical BOM](bom_mechanical.md)
- [Rule compliance checklist](rules_checklist.md)
