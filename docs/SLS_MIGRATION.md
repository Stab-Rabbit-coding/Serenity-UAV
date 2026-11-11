# Serenity UAV — Airframe Migration from FDM CF-PETG to SLS (PA CF / PA11)

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-11-01
**Author:** Steve Griffing, PE(CSE) (Stab-Rabbit-coding). Analysis and edits by
Claude Opus 5.5 (Anthropic) under the author's direction.
**WBS:** §0.13
**Tools:** `tools/sls_dfm_audit.py` (rules check, every printed STL),
`tools/sls_materials.py` (single source of SLS allowables)

> [!CAUTION]
> **ENGINEERING REVIEW REQUIRED.** The margins below use datasheet XY values.
> PA CF build-axis factors are now 0.44 (strength) and 0.35 (modulus), replacing
> the 0.5 ASSUMED knockdown on 2026-11-11 (`tools/sls_materials.py`;
> `reports/SLS Z axis strength.md`). They are ESTIMATES from 33 % CF-PA12 proxy
> data, not DuraForm PA CF. Margins written before that change still use 0.5.
> No PA CF compressive, bearing or fatigue allowable is published. The aircraft
> shall not fly on these margins until a qualified engineer reviews them and the
> Z data item in WBS §0.12 is closed by coupon test (`docs/MATSPEC_SLS_PA_CF.md` §8).

## 1. Basis

- **Printers:** 3D Systems SLS 380 at 15 × 13 × 18 in (381.0 × 330.2 ×
  457.2 mm), sPro 140 at 22 × 22 × 18 in, and sPro 230 at 22 × 22 × 30 in.
  All available (owner, 2026-11-01); same figures as [REF-MFG-001 p. 17].
  Final machine and build orientation are agreed with 3D Systems
  (`docs/SLS_PRINT_ORIENTATION.md` §0).
- **Stiffness-driven parts:** DuraForm PA CF. E_flex 1,010 ksi (7,000 MPa),
  flex strength 19.7 ksi (140 MPa), UTS 12.2 ksi (84 MPa), 3.8 % elongation,
  1.11 g/cm³ [REF-MAT-015].
- **Parts that shall yield, not break:** DuraForm PA11 Black. UTS 7.4 ksi
  (51 MPa), 52.6 % elongation, near-isotropic, 1.03 g/cm³ [REF-MAT-016].
- **Minimum wall:** 0.039 in (1.0 mm) [REF-MFG-001 p. 15].
- **Powder escape:** a hole over 0.079 in (2.0 mm) at every blind or sealed
  cavity [REF-MFG-001 p. 6].
- **Moving-part clearance:** 0.012 in (0.3 mm) general, 0.008 in (0.2 mm)
  minimum [REF-MFG-001 pp. 4, 7, 12].
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

Every current printed part fits the SLS 380 in at least one axis-aligned
orientation. The longest part is the forward hull section (head+cargo in one
piece; the hull is two sections joined at the cargo/middle collar),
`head_cargo_shell24_2mm_merged.stl` (194 × 435 × 202 mm, commit `d92c4f14`). It
fits the SLS 380 only standing on end, and the sPro 140 lying down, which is its
strength orientation (`docs/SLS_PRINT_ORIENTATION.md`). Retired parts are
excluded from both tools (`tools/sls_retired_parts.py`).

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

- **`gen_head_cell_rail.py --statics`:** PASS, minimum margin 1.70. The
  head-cell rail is **retired** (twin pack tray, `d92c4f14`), so this result
  is historical only. The twin pack tray's gate and catch statics are still
  open (`docs/BATTERY_TRIM_ENDURANCE_OPTIONS.md` open items) and shall be run
  on PA CF.
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

## 7. Design review against the 3D Systems SLS Design Guide

Each rule in [REF-MFG-001] that applies to Serenity was checked against the
repo on 2026-11-01. Page numbers are the guide's printed page numbers. They
were checked page by page against the committed PDF; two earlier citations
(p. 3 and pp. 14–15) were corrected to p. 4 and p. 15. The guide dates from
June 2019 and predates DuraForm PA CF (2023). It's general SLS-nylon
guidance, not PA CF-specific.

- **p. 4, axles:** 0.3 mm running clearance; 2 mm+ and air ports for powder
  removal. **Complies.** No printed-in-place axles. Pivots use metal pins or
  ball bearings, which the guide recommends for demanding duty (p. 4 → p. 5).
- **p. 4, baffles:** "Always apply generous fillets to baffles to prevent
  side walls of ducts from splitting." **Open.** The stator-vane roots
  (`edf_stator_sleeve`, generated by `blender_stator_gen.py`) and the
  spider-arm roots (`edf_aft_spider_sleeve.scad`) have no fillets. Root
  fillets reduce the duct's flow area, so size them with a thrust/flow check
  first (WBS §0.13).
- **p. 6, blind bosses:** add a >2 mm hole at the base for bead-blast exit.
  **Partly checked.** Fully sealed voids are checked automatically (audit R3),
  and the one found, in the fixed nozzle, is fixed. The blind heat-set-insert
  and screw bosses (about 70 mentions across the SCAD sources) aren't checked
  automatically. Ask 3D Systems whether their bead-blast reaches them, or add
  vents (WBS §0.13).
- **pp. 7, 12, clearance:** 0.3 mm general, 0.2 mm minimum. **Fixed:**
  `tilt_brake` pin bore, 0.15 → 0.3 mm per side (a safety brake pin); both
  guides re-rendered, and the `cargo_bulkhead_context.py` clash set is
  unchanged apart from the guide's existing worm-swept overlap shrinking
  (1657.6 → 1655.3 mm³). **At the minimum, accepted:** the nacelle servo pocket
  0.2 mm (purchased servo) and the iris flap shingle 0.2 mm (deferred
  source). **Open:** the ESC cover in its pod rebate, 0.25 mm per side.
  Raising it to 0.3 means regenerating both 64 mm nacelles, so it's held
  for that re-export (WBS §0.13). The legacy trunnion `MAG_FIT` 0.2 mm is a
  bond line, not a running fit.
- **p. 13, living hinges:** avoid in SLS. **Complies.** There are none in the
  airframe.
- **p. 13, build orientation:** "avoid stair steps coinciding with the
  tensile surface". **Complies in intent.** This is the basis of
  `docs/SLS_PRINT_ORIENTATION.md`; final orientation is set with 3D Systems.
- **p. 13, mounting on long sections:** elongate one hole by at least 5 mm
  per 100 mm. **No current part needs it.** The two candidates found, the
  belly panel (120 mm screw span) and the battery cradle (130 mm hanger
  span), are both retired (`tools/sls_retired_parts.py`). The belly-panel
  slot made earlier on 2026-11-01 was reverted. Hull, collars and the twin
  pack tray are bonded.
- **p. 15, features above 1 mm:** **Open.** Audit R2: the feather-edge list
  in §4.
- **p. 15, tanks:** walls over 1 mm at density above 0.98 g/cc hold fluid. Not
  applicable; there are no printed tanks.
- **p. 16, threads:** SLS surface roughness interferes with printed threads.
  **Complies.** There are no printed threads. The gear-leg LG-13 pad is
  tapped after printing, and the spider screws thread into the motor.
- **p. 16, engineered tear:** not used.
- **p. 17, machines:** SLS 380 / ProX 6100 class at 15 × 13 × 18 in, sPro 140
  at 22 × 22 × 18 in, sPro 230 at 22 × 22 × 30 in. All three are available
  (owner, 2026-11-01). **Complies:** every part fits at least one.
