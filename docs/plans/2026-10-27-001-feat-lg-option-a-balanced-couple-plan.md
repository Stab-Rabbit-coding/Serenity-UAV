---
title: Landing Gear Option A (Balanced Couple) - Plan
type: feat
date: 2026-10-27
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
product_contract_source: ce-plan-bootstrap
execution: code
---

# Landing Gear Option A (Balanced Couple) - Plan

**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Source study:** `docs/LG_BELLCRANK_LOAD_PATH_STUDY.md` §4.3 (Option A), §6 (fuse), §7 (assumptions); `tools/lg_bellcrank_fbd.py`; `tools/lg_fuse_material.py`.

## Goal Capsule

- **Objective.** Build the landing-gear thigh as a balanced couple, so the hip pin carries only the foot force (crash 258 lbf / 1,148 N instead of 3,221 lbf / 14.3 kN).
- **Owner decisions.** Option A selected 2026-10-27 (LG-LOADPATH closed). Ductile fuse is 6061-T6 in axial tension (2026-10-26). Material preference order applies (`feedback_material_preference_order`).
- **Stop condition.** If no crank azimuth pair keeps both bosses inside the bay outline (U1), stop and return to the owner with the best near-miss before changing any geometry.

## Requirements

- R1. Each row has one member on each side of the hip pin, with antiparallel lines of action, so the row forms a pure couple.
- R2. The ductile row is a pair of straight 6061-T6 tension fuses: Ø4.60 mm, gauge length 33.9 mm, 4,593 N plateau per link [REF-MAT-007].
- R3. The spring row is a pair of opposed bowed spring wires, re-sized to the 10 mm crank.
- R4. Crank radius 10 mm. Hip pin is 6061-T6 Ø4 mm in double shear, with 6061-T6 clevis ear liners 2 × 1.5 mm.
- R5. Every printed bearing face that carries a wire or link end has a 6061 spreader. Per study §7, spreaders go one size up from Ø13 × 1.5 mm.
- R6. Both boss clusters stay inside the canonical bay outline at every corner, at rest and at full flex. This is the gate.
- R7. Failure hierarchy holds: fuse < leg < bay, checked by `tools/lg_bellcrank_fbd.py` at the as-built geometry.
- R8. The mass ledger and BOM reflect the change (about +32 g per aircraft before the tension-fuse change, recomputed).

## Implementation Units

- **U1. Packaging screen (gate).** Extend `tools/lg_wire_layout_study.py` with a balanced-couple mode: r 10, opposed members per row, a straight-link model for the tension row. Screen azimuth pairs for every corner. Output the surviving pairs and the boss-cluster azimuths. Files: `tools/lg_wire_layout_study.py`.
- **U2. Sizing.** Update `tools/landing_gear_r6_sizing.py` to size from the couple (no 2P through the pin), the tension fuse and the re-sized spring wires. Retire its superseded pin and boss checks (study §7). Files: `tools/landing_gear_r6_sizing.py`, `tools/lg_bellcrank_fbd.py`.
- **U3. Leg geometry.** Set the SCAD parameters for crank, azimuths, pin, liners, link seats and spreader pockets. Files: `airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad`.
- **U4. 3-D census and bays.** Run `tools/landing_gear_bay_function.py` and `tools/generate_lg_bays.py`, fix the bays, and resolve the fore-corner loose-body failures found 2026-10-26. Regenerate the STLs. Files: `tools/generate_lg_bays.py`, `airframe/stls/fuselage/landing-gear/`.
- **U5. BOM, ledger, docs.** BOM rows for the 6061 pin, liners, spreaders and tension links. Regenerate the ledger. Update the study, `docs/LANDING_GEAR_ANALYSIS.md` and the WBS. Files: `current-specification/bom_revT.csv`, `current-specification/bom_revT.json`, `WBS.md`.

## Verification

- U1 reports at least one surviving azimuth pair per corner, or the stop condition fires.
- `tools/lg_bellcrank_fbd.py` worst margin is at least 1.0 at the as-built geometry.
- `tools/validate_stls.py` passes. The bay generator reports `PASS`. The symmetry and datum gates pass.
- BOM CSV/JSON parity holds, and `tools/gen_todo_from_wbs.py --check` passes.

> **WARNING**
>
> The tension-fuse plateau ends at necking, and no cited source gives uniform
> elongation for 6061-T6. A bench firing (LG-15) shall confirm the stroke before
> the gear is flown.

## Findings 2026-10-27 (owner questions)

**Couple form (A1b selected for analysis).** `tools/lg_couple_options.py`: push-pull pair of two identical 6061-T6 tension fuses, the push side inside a 6061 reversing sleeve (the canonical jack barrel, QMx Sheet 5 [REF-CAD-003], Henning [REF-CAD-002]). Pin 258 lbf (1,148 N), worst margin 1.36. A1 (bowed compression side) fails at its hinges; A2 does not fit the bay window; A3 needs a 224 mm fuse.

**Reaction path (owner question).** The hip pin's clevis ears and the absorber bosses are both on the separate printed bay part (`tools/generate_lg_bays.py:138-140`), which is bolted to the hull by 4 x M3. The couple therefore closes inside the bay part or a backbone bolted to it; the hull sees only the net foot force through the four bolts.

**Backbone plate material** (anchor pin 4,593 N, hip pin at hierarchy 2,466 N, O4 pins, 1.25 factor, single-shear plate bearing):

| Material | Bearing limit | Plate thickness | Mass per leg (70 x 45 mm) | Verdict |
| --- | --- | --- | --- | --- |
| CF-PETG printed [REF-MAT-001] | 47 MPa (bulk compression; no cited bearing) | 30.5 mm | 125 g | **not viable** for the anchors |
| 6061-T6 [REF-MAT-007] | 276 MPa | 5.2 mm (stock 2 x 1/8 in cheeks) | 44 g (54 g stock) | viable, fully cited |
| CF plate, quasi-iso [REF-MAT-011] | 384 MPa proxy (compressive; units inferred) | 3.7 mm (stock 2 x 1/8 in cheeks) | 18 g (30 g stock) | lightest; allowable requires verification |

Printed CF-PETG stays as the non-structural liner/fairing only. Recommended: CF plate backbone (owner material order), with 6061-T6 as the fully cited fallback until the CF bearing coupon (LG-11) is run.

**Packaging gate, anchors on a backbone** (hip region masked; members may be outside the hull, as the canonical exposed jack):
- Aft corners: strut az 154 deg, reach 55 mm, inboard: 12 mm^3 (tilt bracket). Passes after anchor-boss shaping.
- Fore corners: inboard blocked by TACCO CN2 + chin shelf (about 2,000 mm^3). Outboard-up az 60 deg, reach 65 mm: no keep-out clash; 400-450 mm^3 hull wall + 19 mm^3 swept leg. Open: confirm whether that wall overlap is the open well region of the source mesh or real skin around the window.
