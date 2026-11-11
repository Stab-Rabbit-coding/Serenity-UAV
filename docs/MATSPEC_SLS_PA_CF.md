# Material specification MS-SLS-PACF — SLS DuraForm PA CF flight parts

**Revision:** Rev U, 2026-11-11, issue A (interim: no build-axis data). **Status:** proposed; owner
approval required. **Applies to:** every Serenity UAV part printed in DuraForm PA CF (`AGENTS.md` §7:
hull sections, nacelle pods, collars, brackets, trays, gears, wing skins, fairings).
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner) — drafted by Claude (Anthropic, Claude
Opus 5.5) under the author's direction, with the `3d-print-design` and `mechanical-engineering` skills.
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a qualified engineer.**
> Every result, calculation, and recommendation produced with this skill **must be independently
> reviewed and accepted by a properly qualified individual** — a licensed Professional Engineer or an
> equivalently qualified authority for the jurisdiction and discipline — **before it is applied to
> any system carrying risk to life or safety.** This skill informs engineering judgment; it does not
> replace it. It is reference material provided AS-IS (see LICENSE §5), is not an engineering
> service, and does not constitute a sealed, certified, or reviewed work product for any specific
> project.

Requirement wording follows `AGENTS.md` §6: **shall** is mandatory, **should** is recommended, **may**
is optional.

## 1. Material

DuraForm PA CF, 3D Systems: **33 % carbon-fibre-filled nylon 12**, selective laser sintering.
Datasheet 3DS-30108A (10-23), REF-MAT-015, re-read from the 3D Systems product page 2026-11-11; that
page still links only this revision.

| Property (ASTM method) | Value | Status |
|---|---|---|
| Solid density (D792) | 0.040 lbm/in³ (1.11 g/cm³) | typical |
| 24 h water absorption (D570) | 0.47 % | typical |
| Tensile ultimate (D638 Type I) | 12,200 psi (84 MPa); **did not yield** | typical, XY implied |
| Tensile modulus (D638) | 1,230 ksi (8,500 MPa) | typical, XY implied |
| Elongation at break (D638) | **3.8 %** | typical |
| Flexural strength / modulus (D790) | 19,700 psi (140 MPa) / 1,010 ksi (7,000 MPa) | typical |
| Izod notched / unnotched (D256 / D4812) | 1 ft-lbf/in (52 J/m) / 9 ft-lbf/in (490 J/m) | typical |
| HDT at 66 / 264 psi (D648) | 357 °F (181 °C) / 351 °F (177 °C) | typical |
| **Build-axis (Z) properties** | **not published** | the sheet gives one value per property and no orientation |
| Electrical properties | not published ("complete data set ... Q1 2024", not issued) | — |

**What the data mean for design.** The values are *typical* (means), not design allowables. The
material does not yield and breaks at 3.8 %: it is **brittle** for design purposes. A comparable
material from another maker, ALM PA 602-CF (23 % carbon-filled PA12, sheet in
`airframe/datasheets/PA-602-CF-Data-Sheet-2021.pdf`), also publishes XY values only (85 MPa,
7,900 MPa, 4 %). Neither supplier states Z properties.

## 2. Design values (interim, until §8 coupons are tested)

1. **Failure theory.** Treat PA CF as brittle: maximum normal stress (or modified Mohr for combined
   compression), stress concentration factors applied in full, no plastic redistribution, and no
   credit for yield.
2. **Orientation.** Where the drawing fixes the build orientation so that the principal stress lies in
   the build plane, design to the XY typical value. **Where it does not, or where the load path
   crosses layers, design to 0.5 x the typical value** (`sls_materials.Z_KNOCKDOWN_PA_CF`, ASSUMED).
   The general SLS figure of about 10-15 % Z loss for unfilled PA12 (`3d-print-design` reference,
   uncited) does **not** transfer to a 33 % fibre-filled powder, whose fibres lie in the recoated
   layers. Only coupons settle it.
3. **Factors of safety.** Load-bearing parts: 1.5 basic x 1.5 special = **2.25** on limit load
   (declared judgment after the 14 CFR §23.2265 special-factor model, REF-FAA-002). The special factor
   covers both process variability and the gap between typical and statistically based values.
   Non-load-bearing parts: 1.5. Bonded and bearing joints: no allowable exists, so the joint shall
   be qualified by test.
4. **Compression.** No compressive value is published. Use the tensile ultimate (ASSUMED,
   `sls_materials.py`).
5. **Fatigue.** No endurance limit and no S-N data. A part under cyclic load (gear teeth, tilt-joint
   parts, motor mounts, nozzle drive) shall be qualified by cycle test to its service life; static
   margins do not cover it.
6. **Temperature and moisture.** The HDT is high, but no elevated-temperature strength is published.
   Parts that run above 140 °F (60 °C) (nacelle pods near the motors, ESC bays) shall be checked by
   coupon at the service temperature. Moisture: test coupons conditioned per ASTM D618.
7. **Stiffness.** Use flexural modulus for skins and bending, tensile modulus for struts and members,
   each x 0.5 when orientation is not fixed.

## 3. Build orientation (mandatory)

- Every PA CF drawing and STL release shall state the build orientation: which part axis is the
  machine Z (build) axis, and the recoat (X) direction if the part is loaded in-plane. Without it the
  part shall be designed to the Z-knocked values in §2.
- Orient so the principal tensile and bending stresses lie in the build plane, and so that no
  load-bearing joint (bolt boss, insert, lug, snap) is loaded across layers.
- Large shells (hull sections, pods) cannot be in-plane everywhere. Their analysis shall either use
  Z-knocked values or show the stress direction against layers region by region.
- Avoid stair-stepping on tensile surfaces (REF-MFG-001 p. 13).

## 4. Process control

- The service bureau shall print under a written process specification recorded with each build:
  machine model and serial, powder lot, virgin-to-refresh ratio, layer thickness, laser parameters,
  build-chamber temperature, part position in the build, and cool-down. This is the 14 CFR §23.2260(b)
  model: a process that needs close control is part of the design record (REF-FAA-002).
- Flight-article builds shall carry witness coupons (§8) from the same build.
- A change of machine, powder supplier or parameter set re-opens qualification of the parts it makes.
- Hollow parts shall have at least two escape holes of more than 0.08 in (2 mm) diameter
  (REF-MFG-001 p. 6). Foam-filled parts shall have a fill hole and a vent.

## 5. Geometry rules

| Feature | Rule | Source |
|---|---|---|
| Minimum wall | per `docs/SLS_MIN_WALL_THICKNESS.md`; **interim floor 0.059 in (1.5 mm)** for this filled powder | corrected 2026-11-11, see §6 |
| Load-bearing free-standing wall | 0.098 in (2.5 mm) any orientation; 0.077 in (2.0 mm) XY fixed | stiffness parity with the old CF-PETG basis |
| Running clearance | at least 0.012 in (0.3 mm); 0.008 in (0.2 mm) minimum | REF-MFG-001 pp. 7, 12 |
| Hole diameter | at least 0.059 in (1.5 mm) recommended | `3d-print-design` reference (uncited) |
| Long sections, mounting | elongate one hole at least 0.2 in per 4 in (5 mm per 100 mm) | REF-MFG-001 p. 13 |
| Fillets | at every re-entrant corner of a loaded part, radius at least the wall thickness (declared) | brittle: Kt applies in full |
| Tolerance | design to ±0.012 in (±0.3 mm) or ±0.3 %, whichever is larger, until the bureau states its own | `3d-print-design` reference (uncited) |
| Lattice struts | the guide shows struts to about 0.020 in (0.5 mm) for unfilled powder (REF-MFG-001); for PA CF use at least the 1.5 mm wall floor until shown otherwise | interim |
| Joints | `AGENTS.md` §7: two-wall contact annulus and a positive-stop shoulder; insert wall at least 0.079 in (2.0 mm) to a bore | project rule |

## 6. Correction to the minimum-wall basis

`docs/SLS_MIN_WALL_THICKNESS.md` first used 0.039 in (1.0 mm) as an SLS process floor citing
REF-MFG-001 p. 15. That page gives ">1mm" as the wall of a pressure-tight SLS **tank**, not a minimum
wall, and the guide (2019) predates PA CF. `tools/sls_dfm_audit.py` (`MIN_WALL_MM = 1.0`) carries the
same citation. **The interim floor is 0.059 in (1.5 mm)** until the service bureau states its
minimum for this powder. Logged as WBS SLS-WALL-FLOOR.

## 7. Inspection and acceptance

1. **Visual**: no delamination, open porosity, curl or unfused regions; escape holes clear.
2. **Mass**: each flight part shall weigh within ±3 % (declared) of its mesh mass at 1.11 g/cm³, the
   BOM value enforced by `tools/check_bom_mesh_sync.py`. A light part suggests porosity; a heavy one
   suggests trapped powder.
3. **Dimensions**: interfaces (bores, register faces, insert holes, mating seams) shall be measured
   against the drawing.
4. **Witness coupons**: each flight build's Z tensile coupons shall meet or exceed the Z design value
   the part analyses used.
5. **Flight-critical joints** (tilt joint, wing root, gear) should get CT or sectioned first articles.
6. **First article**: the first build of each flight part shall be proof-loaded to limit load where
   a test fixture exists.

## 8. Coupon test plan (replaces the 0.5 assumption)

| Test | Standard | Orientations | Count |
|---|---|---|---|
| Tensile strength, modulus, elongation | ASTM D638 Type I | X (recoat), Y, Z (built upright) | at least 5 per orientation per build |
| Flexural strength and modulus | ASTM D790 | flat, on edge, upright | at least 5 per orientation per build |
| Pin bearing (insert and bolt holes) | ASTM D953 | hole axis in Z and in XY | at least 5 each |
| Conditioning | ASTM D618 | all | before test |
| Elevated temperature | D638 at 140 °F (60 °C) and the worst nacelle temperature | Z | at least 5 |

Coupons shall come from at least three builds, ideally on the production machine, before a
statistically based design value is set. The orientation knockdown becomes the ratio of the Z mean to
the XY mean; set the interim design value to the Z mean minus three standard deviations until enough
builds exist for a basis value. The ASTM standards above are not yet catalogued in `REFERENCES.md`;
catalogue them, with editions, before the plan is issued.

## 9. Open items

- PA CF build-axis data: none published by 3D Systems (checked 2026-11-11). Get it from the service
  bureau, from a literature search (open-access hosts are not yet allowed in this environment), or
  from §8.
- Minimum wall for this powder: ask the bureau (SLS-WALL-FLOOR).
- Foam-core properties for foam-filled parts: no datasheet for FOAM-PU-2LB.
- Elevated-temperature and fatigue data: none.
- Textbook methods used by the minimum-wall study (Roark, Timoshenko, Allen) and the ASTM methods
  above: catalogue in `REFERENCES.md`.
