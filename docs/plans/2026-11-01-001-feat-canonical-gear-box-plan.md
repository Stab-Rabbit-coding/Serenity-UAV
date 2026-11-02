# Canonical landing-gear box (cargo-flank rebuild) — plan

Status: **U1 done; U2 done; D1–D3 decided; U3 next.**  Started 2026-11-01.
Branch: `feat/canonical-gear-box` (off `feat/sls-migration` 57437edd).

## Problem

Owner, 2026-11-01: the Rev R6/A1B bays (`tools/generate_lg_bays.py`) are open
bolt frames on the 25° sponson panel.  The thigh hub hangs in free air below
each frame, which leaves a visible gap between the bottom of every leg support
and the hull.  The bays read as boxes added onto a different design
(build-guide card 08).

## Canonical form (Henning model, `docs/references/nick-henning/`)

- `nick-henning-uvdisplay-wing.jpg`: the stub wing is the top plate.  The gear
  box hangs under it as a faceted block: the outboard face leans in, the lower
  chine is bevelled, and the face carries recessed panels and an angled hatch.
- `nick-henning-close-gear-combine.jpg`: each thigh is sleeved in a square
  leg-support pillar that lands on the box, so the thigh emerges from the
  pillar mouth.
- `nick-henning-uvdisplay-gear.jpg`: the upper-leg housing is a square tube
  coaxial with the thigh.

## Measured envelope (R2, port; hull `head_cargo_shell24_2mm_merged.stl`)

| Item | Value |
|---|---|
| Belly plane | Z 80 |
| Lower flank half-width, Z < 95 | X 53–56 |
| Flank half-width, Z 95–150, Y 300–390 | X 84–89 |
| Wing root | Y 311.4–440.4, root Z about 135–160 (`SPAR_Z` 146.85) |
| Door aperture edge | X ±52.25–52.65 |
| Hips (`LG_CORNERS`) | fore (54.95, 289.70, 118), aft (77.61, 405.66, 118) |
| Cargo/middle collar | Y 434.7–436.7 |

## Units

- **U1 — concept envelope (DONE).**
  `airframe/openscad/fuselage/gear_box_canonical_concept.scad` defines the
  box at Z 80–133, X 56→96 at the top and 92 at the chine, over Y 262–433.
  Each pillar is a square sleeve coaxial with the static thigh, clipped to
  the box grown by 3 mm.  The swing slot is swept 0–26°.  Status:
  appearance only.
- **U2 — single source.**  Read the corner poses from `LG_CORNERS` /
  `CORNERS` (the concept copies them) and the datums from `hull_datums.py`.
- **U3 — hull rebuild from source.**  Per [[feedback_rebuild_from_source_builds]],
  fold the box into the cargo-shell build (`merge_cargo_interior.py`
  `lg_bay_features`), replacing the sponson rebate/collar instead of
  bolting a fairing onto the published STL.  The current bays become the
  internal structure inside the box (the pillar is the visible support).
- **U4 — enclose the A1B backbone.**  The CF backbone plates currently
  stand proud of the skin (visible in the renders).  The box shall contain
  them.
- **U5 — keep-outs and gates.**  Re-run the bay gates:
  `landing_gear_bay_function.py`, `landing_gear_wing_clearance.py`,
  `landing_gear_cowl_clearance.py`, `landing_gear_ground_clearance.py`, and
  the door swing, tilt bracket, TACCO pouch, chin shelf, hinge retention
  and collar checks.  Hold port/stbd exact-mirror symmetry
  [[feedback_local_informs_airframe_rules]].
- **U6 — structure and mass.**  Size the SLS PA12-CF wall
  (`/statics-and-dynamics` load path from the leg into the box, then the
  hull), roll the mass into the AUW ledger (14.19 lbm baseline), and check
  the CG effect against the thrust line Y 326.7.
- **U7 — docs and renders.**  Regenerate card 08 and the build guide, and
  add `REF-CAD-HENNING` usage to `REFERENCES.md`.  Regenerate WBS/TODO with
  `tools/gen_todo_from_wbs.py`.

## Owner decisions (2026-11-01)

- **D1 — size:** approved as drawn.
- **D2 — opening:** trapezoidal, as canon, and left as an OPEN slot.  The slot
  flares along the pin axis from 22 mm at the hip to 34 mm at 70 mm down the
  thigh (`SLOT_PIN_MOUTH`).
- **D3 — construction:** merged into the one-piece SLS forward hull.
- **Symmetry:** exact about the centreline.  Done in U2.
- **Structure:** if the CF insert plates don't fit by shape or by insertion,
  use PA12-CF with ribbing or lattice.  Manage weight and balance throughout.

## Findings (2026-11-01)

**U2 (done).** The starboard corner rows were literals mirrored about the
old R1 centreline, 0.1 mm off a true mirror.  They are now derived from the
port rows about `X_CL`:

- In the SCAD: `LG_FORE_PORT` / `LG_AFT_PORT` + `lg_mirror_row()`.
- In `merge_cargo_interior.py`: `_mirror_corner()`.
- `tools/lg_corners.py` is now the one parser, and
  `landing_gear_bay_function.parse_corners()` delegates to it.

`canonical_leg_r6_1_5in.scad` (retired bench gear) still carries -77.71.

**A1B CF backbone vs. the new box.**  `tools/lg_a1b_census.py` FAILS before
and after this branch:

| Corner | Hull clash (mm³) | Keep-out clash (mm³) |
|---|---|---|
| Fore cheeks | 252 | 0 |
| Fore members | 85–132 | 0 |
| Aft cheeks | 0 | 16.5 |

The fore cheeks rise to Z 179 and pierce the flank skin above the box.  So
the plates do not work in their current shape or position.

PA12-CF cannot replace them for the couple.  PA 602-CF publishes only XY
values: 85 MPa tensile, 7,900 MPa modulus, 1.10 g/cm³, and no Z or bearing
allowable (`airframe/datasheets/PA-602-CF-Data-Sheet-2021.pdf`).  The
anchor pin carries 4,593 N × 1.25 on Ø4 mm.  That needs ≥ 17 mm of bearing
wall at the full XY strength and ≥ 30 mm with any orientation knockdown.
This is the same verdict the CF-PETG option got (plan 2026-10-27-001).

**Recommended structure (U3/U6):**

- The couple stays in the CF (TC1225, 3.29 mm) / 6061-T6 backbone.
- The cheeks are re-shaped and re-sited to sit inside the pillar, which is
  canon's "rectangular housing on the hull flank" (plan 2026-10-27-001
  line 90).
- They slide up the pillar from its open mouth into printed guide slots.
  That is the insertion path a one-piece hull allows.
- The fore station (Y 290) is ahead of the wing LE (Y 311.4), so the fore
  pillar may rise above the box top to house the cheek.
- The PA12-CF pillar walls carry only the net foot load: 1,148 N crash ×
  1.25 through the hip pin, two walls, Ø8 mm 6061 spreaders.  That needs
  about 2.1 mm of wall at 0.5 × 85 MPa.  Use 4 mm walls plus ribs.
- The allowable is uncited for PA12-CF bearing, so it **requires
  verification** (coupon, as LG-11).

**Weight and balance (first pass, both sides, concept envelope):**

| Item | Value |
|---|---|
| Exposed box skin | 76,100 mm² |
| Skin mass, 1.5 / 2.0 mm SLS | 82 / 109 g |
| Plus 30 % ribs | 106 / 142 g |
| Replaced Rev R6 bays (4, solid) | 64 g |
| Net change | +42 to +78 g, before cutting away the hull skin buried inside the box |
| Box centroid | Y 353.1, 26 mm aft of the thrust line Y 326.7 |
| CG effect | ≈ +0.3 mm aft at 14.19 lbm AUW |

U6 shall replace this with the ledger (`--write`).

**Coordination hazard.**  Another session has uncommitted edits to
`merge_cargo_interior.py` on `claude/3d-print-material-scaling-66d85n`
(head+cargo shell regen held).  U3 edits the same file.  Sequence U3 after
that lands, or rebase onto it.

## Open owner decisions (superseded — see above)

1. **D1 — box depth.**  The concept puts the outboard face 3–7 mm proud of
   the flank, plus a 3 mm proud band on each pillar.  Is that more or less
   bulk than wanted?
2. **D2 — pillar slot.**  The swing slot leaves the pillar as an open
   U-channel on its outboard face.  Canon shows a closed sleeve, but a closed
   sleeve needs a flexible boot or a smaller stroke.
3. **D3 — box as hull vs. separate part.**  The box can be merged into the
   one-piece SLS forward hull (fewer joints, mass to be measured) or printed
   as a bolt-on per side (serviceable, adds a seam).
