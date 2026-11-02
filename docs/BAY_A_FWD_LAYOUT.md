# Bay A Forward — Layout, Mounts, Routes, and Access

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (Claude Opus 5.5, Anthropic) under the
author's direction, 2026-11-01, per `AGENTS.md` §3. AI-generated and not yet
reviewed.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Plan:** `docs/plans/2026-11-01-001-feat-bay-a-forward-adoption-plan.md`
(R1–R6). The owner adopted this layout on 2026-11-01.

Stations are aircraft datum R2 coordinates in mm (X port +, Y aft +, Z up).
They are coordinate labels, not dimensions. Dimensions are in inches first,
with mm in parentheses.

## 1. Sources of truth

| Item | Owner |
| --- | --- |
| Stations, routes, gate | `tools/head_layout_fit.py` |
| Published head params | `airframe/openscad/fuselage/head_layout_params.scad` |
| Twin tray, gate | `tools/twin_head_pack_fit.py` |
| Published tray params | `twin_pack_tray_params.scad` (same folder) |
| Mounts and hatch | `tools/gen_bay_a_fwd_mounts.py` |
| Thermal | `docs/BAY_A_FWD_THERMAL.md` |

Do not copy numbers from this document into tools. Read them from the tools.

## 2. Layout

Both pouches lie flat on the centreline with the connector edge aft. Each
pouch is 1.46 × 2.28 × 0.87 in (37 × 58 × 22 mm).

| Item | Y | Z | Note |
| --- | --- | --- | --- |
| CN1 (TACCO + PB2-I) | 62–120 | 206–228 | 0.94 in (24 mm) under the Observer |
| FC1 (Pilot + PB2-I) | 88–146 | 230.5–252.5 | over CN1's aft end |
| Twin pack tray | 163–283 | 170.5–211.5 | stop plate Y 159–163 |

FC1 sits 0.47 in (12 mm) forward of and 0.06 in (1.5 mm) above the station
first tested. This puts it under the access hatch and makes room for the FC1
shelf floor.

## 3. Mount points

| Part | Kind | Fixing |
| --- | --- | --- |
| CN1 drawer | bonded | floor seats on the chin skin, Y 60–120 |
| CN1 gate | removable | snap bar across CN1's aft end, Z 206–209 |
| FC1 shelf | removable | 4 × M2.5 into the drawer wall tops |
| FC1 retention | removable | 2 cam straps (BATT-STRAP-CAM) |
| Hatch flange | bonded | 3 mm under the skin, sides aft of Y 90 |
| Hatch cover | removable | 8 × M2.5 inserts + forward tongue |
| PGND lugs | — | 2 × M2.5 on the drawer floor, Y 110 |

The FC1 cam straps pass through slot pairs at X ±(22–28), starting at
Y 96 and Y 122.

**Retention design load:** 30.5 lbf (135.5 N) per node in every direction
(79.4 g limit, FOS 3.0). The strap, snap, insert, and bond allowables are
not cited yet, so the statics are PROVISIONAL (WBS open item).

## 4. Access hatch (canonical)

The hatch is the bridge-roof panel at Y 60–137, X ±27. QMx Sheet Six
[REF-CAD-003] places the avionics bay forward of the pilot's station and an
escape hatch in the bridge roof. Henning's renders [REF-CAD-002] show that
roof as a riveted panel between the window-aft frame and a transverse frame.
On the merged hull those frames are at Y 60 and Y 137. The seam stations
require verification against a full-resolution Sheet Six.

- The cover is the cut skin, spikes included.
- A forward tongue tucks under the fixed skin at the window frame.
- The cut hull is
  `airframe/stls/fuselage/head_cargo_shell24_2mm_merged_hatch.stl`.
  The published merged hull is not modified.

**Service path** (stated in the generator header and checked by
`tools/tests/test_bay_a_fwd_mounts.py`):

1. Remove 8 screws. Lift the cover's aft edge and draw it aft.
2. Release the FC1 straps. Tilt FC1 out about its aft edge, which sits
   0.35 in (9 mm) under the Y 137 frame.
3. Remove the FC1 shelf (4 screws).
4. Unsnap the CN1 gate. Slide CN1 aft 1.02 in (26 mm) to clear the
   Observer, then tilt it out.

The Observer stays in place throughout.

## 5. Cable routes

| Route | Envelopes | Length |
| --- | --- | --- |
| Observer to CN1 | Observer drop | 1.0 in (25 mm) |
| CN1 to FC1 | CN1 zone, CN1 run, FC1 zone | 3.7 in (94 mm) |
| CN1 run to port channel | riser, crossover, link, channel | 7.9 in (200 mm) |
| Pitot to airspeed sensor | hose, hose turn | 1.2 in (30 mm) |

Lengths are conservative envelope lengths from `head_layout_fit.py`.

- **Contents.** The bundle carries the Ethernet ring, CAN-FD, RS-485, and
  the 5 V feed. The CN1 run also carries 3 TACCO MMCX coax leads. Antenna
  stations are not placed yet.
- **Drop to the port channel.** The bundle leaves the CN1 run at
  Y 148–158, forward of the tray stop plate. It drops on the centreline,
  crosses outboard at Z 197–205, and joins the port channel
  (X 38.5–48.5, Z 193–201) at Y 160. Nothing can pass over or beside the
  tray: its port rail wall meets the skin above Z 205, and the roof is at
  Z 216 by Y 280.
- **Bus stub.** CN1 is the bus start (120 Ω on board) and daisy-chains, so
  its harness stub is 0 mm. The CAN-FD and RS-485 stub limits are not cited
  yet, so the check is PROVISIONAL.
- **Pitot.** The hose rises from (−3.6, 50.5, 223.9) to the Observer
  underside at Z 236.8. The airspeed sensor itself is not selected.

## 6. Thermal routes

See `docs/BAY_A_FWD_THERMAL.md` §2 for the heat paths and §1 for the open
BLOCKER on the sustained transmit peak.

## 7. Gates (2026-11-01)

| Gate | Result |
| --- | --- |
| `head_layout_fit.py` (fwd, all parts) | PASS |
| `head_layout_fit.py --bay-a side` | PASS, read-only |
| `twin_head_pack_fit.py` (fwd) | PASS |
| `twin_head_pack_fit.py --bay-a side` | PASS, read-only |
| `tests/test_bay_a_fwd_routes.py` | 7/7 |
| `tests/test_bay_a_fwd_mounts.py` | 7/7 |
| `tests/test_bay_a_thermal_budget.py` | 8/8 |
| `bay_a_thermal_budget.py` | FAIL (blocker) |

## 8. CG

| Change | CG shift |
| --- | --- |
| Twin tray 0.35 in (9 mm) forward | −0.9 to −1.2 mm |
| CN1 moved 1.5 in (38 mm) forward | about −0.35 mm |
| FC1 moved 0.47 in (12 mm) forward | about −0.11 mm |

These are ledger estimates (tool output for the tray). Together they move
the CG about 0.06 in (1.4–1.7 mm) forward. The hatch, mounts, and any fan
add mass that the ledger does not yet carry.
