# Serenity UAV — Airframe Migration from FDM CF-PETG to SLS (PA CF / PA11)

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-11-01
**Author:** Steve Griffing, PE(CSE) (Stab-Rabbit-coding). Analysis and edits by
Claude Opus 5.5 (Anthropic) under the author's direction.
**WBS:** §0.13
**Tools:** `tools/sls_dfm_audit.py` (rules check, every printed STL),
`tools/sls_materials.py` (single source of SLS allowables)

> [!WARNING]
> **ENGINEERING REVIEW REQUIRED.** The margins below use datasheet XY values
> with an ASSUMED 0.5 build-axis knockdown for PA CF. No PA CF Z data,
> compressive, bearing or fatigue allowable is published. The aircraft shall not
> fly on these margins until a qualified engineer reviews them and the Z data
> item in WBS §0.12 is closed.

## 1. Basis

- **Printer:** 3D Systems SLS 380, 15 × 13 × 18 in (381.0 × 330.2 ×
  457.2 mm). Owner, 2026-11-01; same envelope class as [REF-MFG-001 p. 17].
- **Stiffness-driven parts:** DuraForm PA CF. E_flex 1,010 ksi (7,000 MPa),
  flex strength 19.7 ksi (140 MPa), UTS 12.2 ksi (84 MPa), 3.8 % elongation,
  1.11 g/cm³ [REF-MAT-015].
- **Parts that shall yield, not break:** DuraForm PA11 Black. UTS 7.4 ksi
  (51 MPa), 52.6 % elongation, near-isotropic, 1.03 g/cm³ [REF-MAT-016].
- **Minimum wall:** 0.039 in (1.0 mm) [REF-MFG-001 pp. 14–15].
- **Powder escape:** a hole over 0.079 in (2.0 mm) at every blind or sealed
  cavity [REF-MFG-001 p. 6].
- **Moving-part clearance:** 0.012 in (0.3 mm) general, 0.008 in (0.2 mm)
  minimum [REF-MFG-001 pp. 3, 7, 12].
- **PA CF build-axis knockdown:** 0.5 on strength and modulus, **ASSUMED**
  (WBS §0.12).

**Material assignment.** PA CF is used wherever the part is sized for stiffness:
hull shells, splice collars, nacelle pods, brackets, gears, trays, wing skins,
and gear leg frames. PA11 is used wherever the part must absorb energy by
yielding: gear feet and skids (owner decision 2026-10-31), leaf or snap springs
strained past PA CF's 3.8 % elongation, and any living hinge. Each existing leaf
spring was checked. The head-cell catch leaf strains 0.5 %, so it stays PA CF.

**What changes from FDM.** SLS needs no supports, and walls are fully dense
instead of perimeter-limited. FDM-only geometry is no longer required: walls
sized as multiples of the 0.6 mm perimeter, support-avoiding chamfers, and
split-for-bed seams. Removing that geometry is a per-part owner decision (WBS
§0.13). It is not done blindly here, because many of those features also carry
load.

## 2. Envelope (R1)

Every printed part fits the SLS 380 in at least one axis-aligned orientation.
The tightest part is `head_cargo_shell24_2mm_merged.stl`:
194 × 435 × 202 mm. It fits only standing on end, with 0.88 in (22 mm) of
margin on the 18 in axis. The 2-section vs 4-section hull question in
`docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md` is therefore not envelope-bound at
the 24 in scale.

## 3. Defects found and fixed

- **`nacelle_nozzle_fixed`** (port and starboard use the same part), rule R3.
  The part had a sealed 14 cc housing void, designed to keep the FDM mesh
  watertight. In SLS it would fill with powder that can't be removed: about
  7 g of dead mass, and the part couldn't be inspected. Fix: 3 × Ø3 mm axial
  escape holes through the aft web at r 30 mm, between the ribs. The part was
  re-rendered as a single watertight body.
- **`lg_r6_3_0in_bay_{aft,fore}-stbd{,_print}`**, rules R3/R4. The four files
  were inside-out (volume −14.6 cc). `generate_lg_bays.py` called `invert()`
  after a reflection that trimesh 4 had already re-wound. Fix: invert only
  when the volume is negative, and raise if it is still non-positive. The four
  files were rewritten. The vertices are identical to the old files, and
  `validate_stls.py` passes all 113 STLs.

Margin tools re-pointed to `tools/sls_materials.py`:

- **`gen_head_cell_rail.py --statics`:** PASS. The minimum margin is 1.70
  (ridge shear-out). The catch leaf release force falls from 0.83 lbf to
  0.44 lbf (3.7 N to 1.9 N); bench-check it.
- **`lg_bellcrank_fbd.py`:** the flat-bearing spreader discs re-size from
  Ø13 to Ø14 mm (Option A) and from Ø17 to Ø18 mm (Option B). Option C0 (the
  printed clevis) was already failing and still fails.

## 4. Open: feather edges (R2)

These parts have median walls of 0.08–0.18 in (2–4.5 mm). Only 5–15 % of their
surface reads under 1 mm, all at tapered edges. SLS builds these edges, but they
are fragile in a 3.8 %-elongation material. Each one needs a decision: thicken
the edge, truncate it, or accept it. Full numbers are in
`docs/sls-study/sls_dfm_audit.json`.

- Conforming flange and cover lips: `nacelle_esc_cover_{port,stbd}_{a,b}`,
  `wing_root_flange_{port,stbd}`, `bow_sensor_faceplate`,
  `cargo_sect_shell24_2mm_repaired`, `middle_canonical_{shell24,edf_intake}`
- Gear tooth tips (accept; involute tips are normal): `tilt_actuator_worm`,
  `nacelle_nozzle_ring`
- Others: `nacelle_trunnion` (50 mm legacy), `nacelle_port_revs`,
  `cargo_drv8833_tray`, `tilt_brake_guide`, the port gear bays (thin
  pass-through slits, already logged as LG zero-area slits)

## 5. Open: remaining CF-PETG allowables in tools

These still use CF-PETG values [REF-MAT-001/-002]: `landing_gear_r6_sizing.py`,
`lg_thigh_variants.py`, `lg_couple_options.py`, `tilt_actuator_options.py`
(margins of 10× and above, so it is not critical), `nacelle_tilt_dynamics.py`,
`nacelle_esc_thermal.py`, `wing_spar_carrythrough.py`,
`aft_section_mass_audit.py`, and the SCAD headers of `battery_cradle`,
`nacelle_trunnion`, and `wing_tilt_pinion`. Re-point them one at a time, and
re-run each tool's own gate after each change.

## 6. Open: mesh (R4)

`nacelle_{port,stbd}_64mm` and `wing_root_flange_{port,stbd}` are not
watertight under the trimesh check, although `validate_stls.py` passes them.
Re-export them before submitting the build to 3D Systems.
