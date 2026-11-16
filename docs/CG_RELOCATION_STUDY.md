# CG Relocation Study — Hover CG onto the Thrust Line

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude (Claude Opus 5.5, Anthropic), 2026-10-27, per `AGENTS.md` §3
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Tool:** `tools/cg_relocation_study.py`

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation produced
> with this skill **must be independently reviewed and accepted by a properly
> qualified individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.** This skill informs
> engineering judgment; it does not replace it. It is reference material
> provided AS-IS (see LICENSE §5), is not an engineering service, and does not
> constitute a sealed, certified, or reviewed work product for any specific
> project.

## 1. Target and criterion

- **Target (owner, 2026-10-27):** the hover CG lies on the hover thrust line. That line is the nacelle tilt pivot at aircraft datum R2 Y 326.7 mm (12.86 in) (`tools/hull_datums.py` SPAR_Y).
- **Control reserve:** trim may consume no more than 50 % of the nominal pitch control moment, per MIL-F-83300 §3.4.4 and §3.2.3.3 (31 Dec 1970, Notice 2, 2019). That specification's scope is piloted military V/STOL, so it is adopted here as a self-imposed criterion. The spread of CG across configurations is what this criterion has to cover.

## 2. Mass basis

- Every item comes from `tools/auw_ledger.py`, which uses the same roll-up as the ledger.
- Cells: Tattu R-Line 6S 2200, 321 g (0.708 lbm) each. ORIGIN: PRC-domiciled maker, retained by owner decision on 2026-10-26.
- **Ledger gap:** the nose Observer is missing from the ledger. It is carried here as **ASSUMED 60 g (0.13 lbm)**, the ledger's own figure for the cargo Observer, placed at the pitched board's centroid (`head_layout_fit.observer_board()`).

## 3. Results

| Arrangement | Hover | Heaviest payload | Third cell |
| --- | --- | --- | --- |
| Rev H2 as handed over: Bay A Y 147, head cell Y 256, cell 2 middle/aft Y 541.7 | +29.7 mm (+1.17 in) | — | — |
| **Rail lever:** Bay A on the rail ceiling, stop Y 156, head cell Y 216, cell 2 cargo band Y 286–402 (ledger wire lump) | +16.8 mm (+0.66 in), AUW 13.38 lbm (6,071 g) | +17.4 mm, 13.88 lbm (6,298 g) | +17.4 mm, 13.91 lbm (6,311 g) |
| **Rail lever with the routed harness (current)** | **+16.3 mm (+0.64 in)**, AUW 13.74 lbm (6,232 g) | +17.0 mm, 14.24 lbm (6,459 g) | +17.0 mm, 14.27 lbm (6,472 g) |

The CG spread across the three configurations is **0.7 mm (0.03 in)**. Payload and third-cell changes therefore barely move the trim. The offset itself is what the control reserve has to absorb.

### 3.1 Rail lever (the move that works)

> **Superseded 2026-11-01 (layout only):** Bay A is now the Bay A forward layout — both pouches flat on the centreline, CN1 under the Observer, FC1 above it, twin tray at Y 163 (`docs/BAY_A_FWD_LAYOUT.md`). The rail-lever text below is kept as the study record.

Two Bay A pouches (CN1 + FC1, 58 × 37 × 22 mm), standing on edge either side of the centreline on top of the rail ceiling:

- **Position:** Y 100–158, Z 208.65–245.65.
- **Clearance:** zero 1–2 mm-near volume against both the head skin and the pitched Observer board, across 32 probed placements.

This lets the rail stop move forward from Y 196 to about Y 156. The band itself is clear from Y 150; the extra 6 mm allows for the stop plate and the catch leaf. The head cell then sits at Y 158–274, and the second cell fits the cargo band again at Y 286.2–402.2.

**Moment gained against Rev H2: about 78,000 g·mm.** That takes the hover offset from +29.7 mm to +16.8 mm.

**Open item (owner and coordinator):** the head cell's leads exit aft into a gap of about 10 mm before the second cell. Route them before this arrangement is adopted.

### 3.2 Equipment relocations — fine search (owner: "finer relocation search", 2026-10-27)

**Method: free-space map.**
- Fixed obstacles: every shell and collar, plus every `cargo_layout_fit`, `middle_layout_fit` and `head_layout_fit` envelope. That includes the nose sensor bay, the pitched Observer board, the pitot hose, Bay A on the rail ceiling, and the rail and band from Y 146 to Y 404.
- Moved candidates are taken out of the obstacle set.
- The obstacles are sliced by manifold3d every 4 mm in Z and rasterised at 1.5 × 1.5 mm in X and Y. Box placements are tested through a 3-D summed-area table with a 2 mm static gap.
- Search space: all six axis orders (90° rotations about each axis), any X across the section (lateral and off-centre), Y step 1.5 mm, Z step 4 mm. Node pairs were split into single pouches, which covers mirrored and split placements.
- The map's free volume is 4,892 cm³ (299 in³).

| Item | Mass | Station | Result |
| --- | --- | --- | --- |
| Flight Engineer (board + can + plate) | 225 g (0.50 lbm) | Y 467.7 | no clear placement forward. Its most-forward clear slot anywhere is Y 516.8 (rear section). |
| Simon CN4 + FC4, split | 2 × 59 g | Y 494.7 | no clear placement forward once the FE keeps its slot. Swapping the FE aft of Simon would move the CG **aft**. |
| Aft nodes FC2/FC3, split | 2 × 59 g | Y 416.2 | no clear placement forward. The most-forward clear slot for a single pouch anywhere is Y 447 (middle neck, the FE's space). |
| Cargo Observer | 60 g (0.13 lbm) | Y 424.2 | no clear placement forward. Its function also needs line of sight to the clamshell aperture. |

**Other items over 20 g aft of the pivot**, not relocatable by structure or function:

- rear, middle and cargo shells;
- gear frame and bays;
- wing panels and tilt motors, which sit on the pivot geometry;
- the winch (tied to the payload);
- Commo, ferrites and harness.

The harness (WIRE-6AWG/10AWG, 140 g at Y 395.7) is an estimate from the single-pack layout. It moves when the split-cell routes are drawn, but that is a ledger correction, not a relocation.

**Second cell pulled forward** to the head cell's tail (4 mm lead gap, centre Y 338.0): hover +16.5 mm, a gain of only 0.3 mm. A 4 mm gap is below any practical bend allowance for the cell leads, so this is not recommended.

**Verdict:** after the rail lever, no further equipment relocation is available at a 2 mm static gap. The rest has to come from a pivot move, ballast, or mass reduction aft of the pivot.

### 3.3 Owner inputs, 2026-10-27

**(1) Swap the FE forward into the cargo Observer slot, and the Observer aft into the FE's neck slot.**

- **Fit: does not fit.** The FE unit (can + plate, 75 × 36 × 94 mm) has no clear placement within ±25 mm of the Observer station (Y 424.2) in any of the six axis orders, even with both items removed from the free-space map. The Observer slot is 76.8 × 20 × 70.8 mm and sits under the aft nodes (Z 167–204). Its most-forward clear slot anywhere is Y 516.8.
- **Value if it did fit:** hover +16.3 → +14.3 mm, a gain of 2.0 mm (owner estimate 1.2 mm). The shorter feeder runs also save 54 g of wire.
- **Observer view from the neck slot (geometry check):**
  - A camera at the tray's top edge (Z ≈ 194) sees the ground under the hoist point (Y 361.2) through the clamshell aperture: the ray crosses the belly plane at Y ≈ 396, inside the aperture's aft edge at Y 413.7.
  - With the payload stowed, that ray passes through the payload box's aft face, but so does the ray from today's station. The view is therefore no worse than today.
  - Below a camera height of about Z 131 the belly skin aft of the aperture blocks the view.

**(2) Large-gauge harness as routed segments**, replacing the ledger's single lump of 140 g at Y 395.7.

- **Mass per length:**
  - AWG diameter from ASTM B258, d = 0.005 in × 92^((36 − n)/39). **REQUIRES VERIFICATION:** ASTM B258 is not yet catalogued in REFERENCES.md.
  - Copper at 8.89 g/cm³. **REQUIRES VERIFICATION:** source to be catalogued.
  - Silicone insulation adds 35 % (**ASSUMED**); routing slack is 10 % (**ASSUMED**).
  - Result: 6 AWG **160 g/m** (1.08 oz/ft); 10 AWG **63 g/m** (0.42 oz/ft).
- **Routes:**
  - a 6 AWG pair from each cell's aft face (head cell Y 274, cell 2 Y 402.2) to the FE entry plate;
  - a 10 AWG pair per ESC (four ESCs) from the FE to each nacelle pivot (Y 326.7), run along the centreline and then laterally along the spar.
- **Routed total: 301 g (0.66 lbm) at Y 357.8.** The centroid is 38 mm further forward than the lump, but the mass is 161 g more. The BOM's 140 g appears to undercount the ESC feeders (one 1 m red/black pair), so the BOM row needs reconciling.
- **Net effect:** the hover offset moves from +16.8 to **+16.3 mm**, and AUW rises to 13.74 lbm (6,232 g). The harness model shortens and moves with the FE whenever the FE moves; since the FE has no feasible forward slot, this only changes the baseline.

## 4. Residual

- Hover residual moment: **101,694 g·mm** (routed harness).
- **Nose ballast** at Y 15 to close it: **326 g (0.72 lbm)**. This is not recommended: T/W falls from 1.37 to about 1.30 with the routed harness.
- **Pivot move.** The nacelles (1,853 g, 4.08 lbm, ledger) move with the pivot, so the CG offset closes by Δ(1 − f), where f ≈ 0.31 is the nacelle mass fraction. Closing 16.3 mm therefore takes **Δ ≈ 23 mm (0.91 in) aft** (f 0.30 with the routed harness). This is an upper bound: including the wing panels in f lowers it. It reworks the spar carry-through, the cargo tilt actuators and the wing-root flanges.

## 5. Aft mass reduction (owner: "cut weight aft first", 2026-10-27)

Tool: `tools/cg_mass_reduction_study.py`. Baseline: rail lever (adopted, commit 3252b5a2) with the routed harness, hover +16.3 mm, 101,694 g·mm.

### 5.1 Wiring BOM reconciliation (proposed rows; the BOM files are not edited)

The BOM rows were written for the single 4000 mAh pack:

- WIRE-6AWG: 60 g, "200 mm each red/black".
- WIRE-10AWG: 80 g, "1 m each red/black".

Problems found:

- **The 10 AWG row is below its own physical minimum.** 2 m of bare 10 AWG copper weighs 94 g.
- **Runs the BOM omits:**
  - the head cell's long lead (about 0.45 m of pair);
  - the second cell's lead;
  - six of the eight ESC feeder conductors (four ESCs, one pair each);
  - the third-cell (J_BATT3) lead.

| Proposed row | Run | Length | Mass |
| --- | --- | --- | --- |
| WIRE-6AWG | head cell → FE (2 × 224 mm) + cell 2 → FE (2 × 83 mm) | 0.61 m | **98 g (3.5 oz)** |
| WIRE-10AWG | FE → four ESCs, 8 × 402 mm (along the centreline, then the spar to the pivots at X ±230.4) | 3.22 m | **203 g (7.2 oz)** |
| WIRE-6AWG-T3 (new) | third cell (payload bay) → FE J_BATT3, 2 × 130 mm | 0.26 m | **42 g (1.5 oz)**, extended configuration only |

Bases for these figures:

- 6 AWG at 160 g/m and 10 AWG at 63 g/m.
- **REQUIRES VERIFICATION:** the ASTM B258 diameter relation and copper at 8.89 g/cm³, both not yet catalogued.
- **ASSUMED:** +35 % insulation and 10 % routing slack.
- The route lengths come from the rail-lever stations with the FE at its ledger station. They change with the FE study.

### 5.2 Ranked cuts aft of the pivot (by moment saved)

| Rank | Cut | Mass | Moment | Basis | Counted |
| --- | --- | --- | --- | --- | --- |
| 1 | Rear shell wall 2.0 → 1.2 mm | −92.6 g (3.27 oz) | −24,070 g·mm | MEASURED 231.5 g, linear in wall (ASSUMED); skin deflection 0.250 mm vs 0.5 mm limit | alternative to rank 2 |
| 2 | **Rear shell wall 2.0 → 1.6 mm** | −46.3 g (1.63 oz) | −12,035 g·mm | as rank 1; deflection 0.105 mm | **yes** |
| 3 | Cargo Observer → remote camera head off the nose Observer | −55.0 g | −5,362 g·mm | 60 g ESTIMATE, head 5 g ASSUMED | no: functional change, owner decision |
| 4 | **Ferrites at their node sites** (ledger correction) | 0 g | −2,924 g·mm | 80 g BOM, now split equally over the four node sites | **yes** (bookkeeping) |
| 5 | **Middle shell skin panels 2.0 → 1.6 mm** | −18.3 g (0.65 oz) | −2,682 g·mm | MEASURED 183.1 g, 50 % panel area ASSUMED | **yes** |
| 6 | FE can 0.5 → 0.3 mm 6061 | −12.7 g | −1,794 g·mm | `can_mass()` 31.8 g | no: FE under study |
| 7 | FE entry plate brass → 6061-T6 | −13.7 g | −1,681 g·mm | plate 25 g ASSUMED, 80 % brass ASSUMED [REF-MAT-007, REF-MAT-009] | no: FE under study |

Notes on the table:

- **Skin deflection** scales as t⁻³ from the 2.0 mm skin's 0.054 mm at 28 m/s (2026-05-26 analysis, recorded in the `head_shell24.scad` header).
- **Rear and middle shells** keep 2.0 mm at the skid-rod channels, the ring pocket, the collar lands, the horseshoe legs and the hatch frame.
- **The 1.2 mm rear wall** means three perimeters, a handling and impact risk; print a trial first.
- **FE can options:** a printed shell plus 0.1 mm foil saves nothing (about 30 g). The 0.3 mm can halves low-frequency magnetic absorption again, so the FE-CAN-05 EMC pass must accept it.
- **Ferrites:** their quantity basis, "4 per cage", is obsolete now that the cages are foil pouches; the count is left for the EMC pass.
- **The ledger's FE-can label is stale:** it reads "1.0 mm", but `can_mass()` uses 0.5 mm.

**Not proposed:**

- **Harness gauge.** REFERENCES.md catalogues no ampacity source, and each 10 AWG feeder carries one ESC, 57.0 A at the QF2822 rated point [REF-EDF-003]. A smaller gauge cannot be justified on cited data, and 10 AWG at 57 A should itself be checked once an ampacity source (for example SAE AS50881) is catalogued.
- **Landing-gear aft items** (LG-LOADPATH is open).
- **Node boards, pouches and bond straps** (EMC).
- **CF ring, thwart and collars** (structural).

### 5.3 Cumulative

| Step | Hover offset | AUW |
| --- | --- | --- |
| Baseline | +16.3 mm | 6,232 g (13.74 lbm) |
| + rear shell 1.6 mm | +14.49 mm | 6,186 g |
| + ferrite ledger correction | +14.02 mm | 6,186 g |
| **+ middle shell panels 1.6 mm** | **+13.63 mm** | **6,167 g (13.60 lbm)** |
| (rear 1.2 mm instead of 1.6 mm) | (+11.77 mm) | |
| (+ cargo Observer remote head) | (+12.87 mm) | |
| (+ FE can and plate, under study) | (about +13.1 mm) | |

**Residual after the counted cuts: 84,052 g·mm.** Closing it would take 270 g (0.60 lbm) of nose ballast at Y 15, or a pivot move of about 19.5 mm aft. Cutting weight aft alone does not reach the thrust line; the best case with every option taken is about +10.4 mm.

## 6. Next relocation passes

1. A finer search (lateral, rotated, split pairs) for the FE and the aft nodes.
2. Put the nose Observer's real mass in the ledger once the board is populated.
3. Harness centroid: the ledger's WIRE-6AWG/10AWG station (Y 395.7) is an estimate from the single-pack layout. Re-derive it from the split-cell lead routes.
