# Canonical landing-gear box (cargo-flank rebuild) — plan

Status: **U1 done (concept); U2–U7 open.**  Started 2026-11-01.
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

## Open owner decisions

1. **D1 — box depth.**  The concept puts the outboard face 3–7 mm proud of
   the flank, plus a 3 mm proud band on each pillar.  Is that more or less
   bulk than wanted?
2. **D2 — pillar slot.**  The swing slot leaves the pillar as an open
   U-channel on its outboard face.  Canon shows a closed sleeve, but a closed
   sleeve needs a flexible boot or a smaller stroke.
3. **D3 — box as hull vs. separate part.**  The box can be merged into the
   one-piece SLS forward hull (fewer joints, mass to be measured) or printed
   as a bolt-on per side (serviceable, adds a seam).
