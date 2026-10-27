---
artifact_contract: "ce-handoff/v1"
created_at: "2026-10-27T15:40:00Z"
title: "Head-section layout gate, Bay A / cell relocation, BOW-02"
summary: "tools/head_layout_fit.py built and passing for the head; owner moved the head cell aft (Bay A stays in Shepherd's bay) and the second cell to the middle/aft sections; swap access, Simon repack, CG and BOW-02 open."
keywords: ["head", "datum R2", "Bay A", "head cell", "rail", "BOW-02", "TFmini-S", "Simon", "CG", "swap"]
cwd: ".claude/worktrees/fuselage-reconcile"
resume_focus: "Owner decisions on second-cell swap access and Simon repack; then rail/catch SCAD + statics, ledger CG, BOW-02 cluster re-layout"
repository: "Serenity-UAV"
branch: "worktree-fuselage-reconcile"
head: "2ebe6410"
---

# Handoff: head-section layout (2026-10-27)

**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of
Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Supersedes, where they conflict:** `docs/handoffs/2026-10-26-split-battery-and-fe-pdb.md`
§3 and plan 2026-10-26-001 KTD5, R4, U6 step 1.

## 1. What exists now

`tools/head_layout_fit.py` (commit `2ebe6410`) is the single source of the
head stations in R2 and the head context gate. It writes
`airframe/openscad/fuselage/head_layout_params.scad`. Current result:
**PASS** (0 shell, 0 pair, 0 line-of-sight, 0 band), with BOW-02 registered.

| Item | R2 station | Notes |
| --- | --- | --- |
| Observer nose carrier (trapezoid 25.4→54 × 69.85) | Y 49–119, board Z 219 | Forward-most allowed until BOW-02 shrinks the sensor bodies (laser rear Y ≈ 47). Owner: the trapezoid exists to reach into the bow, so it stays forward. |
| Bay A CN1 + FC1 (two 58×37×22 pouches, on edge) | Y 121–179, Z 189–226, cable zone to Y 189 | Owner 2026-10-27: Bay A stays in Shepherd's bay. |
| Head cell + sled | stop Y 193, cell Y 195–311, Zc 187 | Cell mostly in the cargo section, on the rail. |
| Rail (inverted U with lips), stop, catch, saddles Y 200 / 218 | Y 189–243 (head piece) | Cargo rail piece not yet drawn. |
| Trunk | Observer → Bay A → CL above the rail ceiling → collar | 10 × 8 mm. |

## 2. Measured findings (not assumptions)

- **KTD5 is wrong at its low end.** The 40 × 36.5 band clears only at Zc 187.
  Zc 169 hits the head/cargo collar at Y 240; Zc 181/184 hit the chin nodes
  and the payload. At Zc 187 the band is clear from Y 150 aft to Y 402.2
  (aft nodes N2/N4 at Y 405.2 bound it).
- **Bay A has no head volume aft of a stop at Y 148.** Above, beside and below the rail
  all foul the skin (180–2,500 mm³). Hence the owner's move.
- **BOW-02 (registered).** The published bow cluster's camera, ToF and laser
  pockets overlap one another by 1.7–2.6 cm³, so the bodies cannot all be
  installed. The TFmini-S maker, Benewake (Beijing), fails the `AGENTS.md` §5
  sourcing rule. REF-SENSOR-002's "single 8 mm TX/RX lens" claim is
  unverified. The pitot keep-out sits in the same volume and moves with it.
- **Laser exit is 2.46 mm off the centreline** (head re-centre). This cannot be fixed
  without regenerating the head, which is not reproducible (R2 handoff).
  The offset is optically negligible; note it in BOW-02.

## 3. Second cell (owner: "use the middle and aft sections", "push Simon into the rear section, battery forward of that stack", "easily swapped between sorties")

- Fits directly aft of the FE can: **Y 483.7–599.7, Zc 136** (side or flat),
  zero 2 mm-near against the middle shell, rear shell, middle/rear collar and
  every remaining middle envelope. It crosses the bonded middle/rear joint.
- **Simon's stack (77 tall, 22 long, 68 wide) does not fit aft of the cell** within 60 mm; the rear
  tapers. It needs a repack (pair side by side, or flat).
- **Swap access is open, and it is the governing requirement.** The middle ventral
  hatch is sized for the FE can (~32 mm in Y) and cannot pass a 116 mm cell.
  A candidate is a rear-section belly hatch aft of the joint, with the cell sliding
  forward on a short rail to a stop at the FE aft plate (the same drawer pattern
  as the head cell). This must be checked against the rear belly shape. Phase 11
  aft-EDF reshuffling is accepted by the owner.
- **CG, rough estimate (needs `auw_ledger.py`):** head cell centre Y 253, second
  cell centre Y 541.7, against the hover thrust line Y 352.3. That puts the CG about
  +31 mm behind the thrust line, against the single-pack +22.6 mm and the
  original split's +14.3 mm. **An acceptable aft CG limit is not documented;** the
  hover trim authority must be confirmed before this layout is accepted.

## 4. Not done yet (plan 001 units)

- U1: the head shell SCAD R2 migration was deliberately not regenerated. The published head
  already carries the bow cuts and is not reproducible; head contents are separate
  bonded parts.
- U4/U5: rail and catch SCAD and STLs, and the statics section in `docs/BATTERY_MOUNT.md`.
  Worked figures so far, for 79.4 g on 0.341 kg (cell + sled) = 265.5 N limit, FOS 3.0:
  ceiling plate 2.4 mm over a 40 mm span gives 11.9 MPa against 77 MPa flexural
  [REF-MAT-002]. The leaf catch (L 40, W 20, t 1.6, tooth 2.5) runs 25 MPa at
  release against 77 MPa, with a ~5.3 N release force. Catch tension at ultimate is
  24.9 MPa against 39.23 MPa tensile [REF-MAT-001]. Tooth shear is ~10 MPa against
  ~22.6 MPa (distortion-energy estimate, order-of-magnitude only, the same
  treatment as DOOR-LATCH-1). There is no cited fatigue allowable for the flexure.
- U6/U7: the cargo rail piece, the cargo-cell removal from `cargo_layout_fit.py`,
  the second cell in `middle_layout_fit.py`, the ledger, the BOM and the WBS rows (SPLIT-BATT, BOW-02,
  BAYA, OBS-NOSE).
- BOW-02 ToF candidates (retailer data, VERIFY at the issuing body before
  REFERENCES.md):
  - LightWare SF000/B (South Africa): 22×34×21 mm, 0.2–50 m, 8.8 g, Class 1M.
  - Garmin LIDAR-Lite v4 LED: 10 m, so it fails the 15 m nose need.
  - Terabee Evo 15m: discontinued.

## 5. Traps

- Use `/usr/bin/python3`. `head_layout_fit.py` imports `merge_head_interior.py`
  builders, which are the single source of the pocket solids.
- Pre-commit regenerates the index files; let it.
