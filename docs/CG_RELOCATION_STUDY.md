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
| **Rail lever:** Bay A on the rail ceiling, stop Y 156, head cell Y 216, cell 2 cargo band Y 286–402 | **+16.8 mm (+0.66 in)**, AUW 13.38 lbm (6,071 g) | +17.4 mm, 13.88 lbm (6,298 g) | +17.4 mm, 13.91 lbm (6,311 g) |

The CG spread across the three configurations is **0.7 mm (0.03 in)**. Payload and third-cell changes therefore barely move the trim. The offset itself is what the control reserve has to absorb.

### 3.1 Rail lever (the move that works)

Two Bay A pouches (CN1 + FC1, 58 × 37 × 22 mm), standing on edge either side of the centreline on top of the rail ceiling:

- **Position:** Y 100–158, Z 208.65–245.65.
- **Clearance:** zero 1–2 mm-near volume against both the head skin and the pitched Observer board, across 32 probed placements.

This lets the rail stop move forward from Y 196 to about Y 156. The band itself is clear from Y 150; the extra 6 mm allows for the stop plate and the catch leaf. The head cell then sits at Y 158–274, and the second cell fits the cargo band again at Y 286.2–402.2.

**Moment gained against Rev H2: about 78,000 g·mm.** That takes the hover offset from +29.7 mm to +16.8 mm.

**Open item (owner and coordinator):** the head cell's leads exit aft into a gap of about 10 mm before the second cell. Route them before this arrangement is adopted.

### 3.2 Equipment relocations (none found)

| Item | Mass | Station now | Result |
| --- | --- | --- | --- |
| Flight Engineer (board + can + plate) | 225 g (0.50 lbm) | Y 467.7 | no clear placement forward |
| Simon CN4 + FC4 (stack) | 118 g (0.26 lbm) | Y 494.7 | no clear placement forward |
| Aft nodes FC2/FC3 | 118 g (0.26 lbm) | Y 416.2 | no clear placement forward |
| Cargo Observer | 60 g (0.13 lbm) | Y 424.2 | no clear placement forward |

**Search limits** (so a later, finer pass can overturn these results):

- axis-aligned envelopes only, on the centreline (X 0);
- Y step 6 mm, Z step 8 mm;
- a 2 mm static gap against the post-merge cargo shell, both splice collars, the middle shell, every `cargo_layout_fit` and `middle_layout_fit` envelope, and the cell sliding band.

Lateral offsets, rotated placements, and splitting a node pair across sides were not searched.

## 4. Residual

- Hover residual moment: **101,785 g·mm**.
- **Nose ballast** at Y 15 to close it: **327 g (0.72 lbm)**. This is not recommended: T/W falls from 1.41 to about 1.33.
- **Pivot move.** The nacelles (1,853 g, 4.08 lbm, ledger) move with the pivot, so the CG offset closes by Δ(1 − f), where f ≈ 0.31 is the nacelle mass fraction. Closing 16.8 mm therefore takes **Δ ≈ 24 mm (0.95 in) aft**. This is an upper bound: including the wing panels in f lowers it. It reworks the spar carry-through, the cargo tilt actuators and the wing-root flanges.

## 5. Next relocation passes

1. A finer search (lateral, rotated, split pairs) for the FE and the aft nodes.
2. Put the nose Observer's real mass in the ledger once the board is populated.
3. Harness centroid: the ledger's WIRE-6AWG/10AWG station (Y 395.7) is an estimate from the single-pack layout. Re-derive it from the split-cell lead routes.
