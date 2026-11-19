# Airframe Design — Agent Instructions

Adds airframe-specific rules to root `AGENTS.md`, which wins wherever it speaks. Scope: printed
shells, ribs and bosses, wings, nacelles, landing gear, and their SCAD, FreeCAD, Blender, and
STL files. Section roles and layout: `airframe/README.md`.

## Aircraft Datum

One origin for the whole aircraft (owner directive 2026-10-19; root `AGENTS.md` §5):

- **Origin (0, 0, 0)** on the centreline (port/starboard symmetry plane), at the **nose tip**
  (foremost point of the head shell), on the **static ground plane** (aircraft at rest, level,
  on the 3.0 in flight landing gear).
- **X** positive port; X = 0 is the symmetry plane, so a starboard twin is the port part
  mirrored X → −X. **Y** positive aft; Y = 0 at the nose tip. **Z** positive up; Z = 0 on the
  ground plane.

Rules:

- **Every** design artifact uses this datum: SCAD, STL, STEP, Blender/FreeCAD/Python
  generators and gates, and documentation. Publish each STL and STEP **at its installed
  position**, so it imports into FreeCAD with identity placement. A `*_print.stl` in print
  orientation is a slicer-only export, never used for fit or clash checks.
- **One STL per installed instance**, each at its own position (e.g.,
  `lg_r6_3_0in_leg_frame_fore-port.stl`), all generated from one source — never a hand copy,
  never a design STL plus a placement table.
- **Exception:** a PCB keeps KiCad coordinates only while designed in KiCad (see
  `avionics/AGENTS.md` "PCB Design Rules").
- **Nacelles** are stored at the cruise (forward-flight) attitude; tilt is that nacelle's own
  rotation about its pivot axis, the one per-part transform allowed.
- **Datums are never re-typed.** Python imports `tools/hull_datums.py`; OpenSCAD includes the
  generated `airframe/openscad/hull_datums.scad`. `tools/check_datum_drift.py` (hook and CI)
  fails a re-typed datum or a stale frame marker.
- **Frame R1 → frame R2 migration** (plan `docs/plans/2026-10-19-001-aircraft-datum-migration-plan.md`,
  WBS DATUM-R2): frame R1 put the origin at the FreeCAD assembly world origin. Frame R2 =
  frame R1 + `hull_datums.R1_TO_R2` = (169.85, 305.70, 80.00) mm. A file is in frame R2 only if
  its STL header carries `SerenityUAV AIRCRAFT-FRAME R2` or its code imports the R2 datums.
  Numbers in documents dated before 2026-10-19 are frame R1.
- `airframe/HULL_FRAME_REFERENCE.md` holds the bake workflow, the canonical-accuracy authority
  order (REF-CAD-002/003/004, `docs/references/`), and the validated extents table.

## Geometry Integrity

Root `AGENTS.md` §5 "Airframe geometry" states the outer-mold-line and canon rules. Applied
here to fuselage, wings, and nacelles alike: where function forces a departure from canon
(e.g., the 64 mm intake), fair it into the measured canonical skin rather than adding a
foreign shape (worked example: `tools/nacelle_cowl_fair.py`).

## Fabrication and Validation

Root `AGENTS.md` §7 governs material, print parameters, walls, foam, joints, and the mesh gate.
In addition, models shall be **ready to slice** immediately after generation, and every
regenerated primary-component STL shall be re-baked before publishing.

## Sources and Pipelines

- **Blender-canonical fuselage sources:** `airframe/blender-scripts/files-hollowed-24in/`. Any
  fuselage geometry change starts there; fuselage SCAD files are secondary references.
- Bake pipeline, headless invocations, and pre-commit checklists: `tools/TOOL_REFERENCE.md`
  "Blender Hollowing Pipeline". Output STLs go to `airframe/stls/{fuselage,nacelles,wings}/`.
- **Assembly:** `airframe/FreeCAD-scripts/serenity_assembly.py` (`freecadcmd`) builds
  `airframe/freecad/assembly/SerenityAssembly.FCStd`, a local working file not tracked in git.
- PCB footprint placement is governed by root §5 and `avionics/AGENTS.md`, not this file.

## Nacelle Nozzle Drive

Functional requirement (the one home for it): each nacelle nozzle is variable-diameter and
**scheduled on measured nacelle tilt**, 75% of bore at 0° (forward) to 105% of bore at every
tilt from 90° to the 135° limit, and shall fail to 105% on loss of servo power, command, or
tilt-angle validity. Drive mechanism (servo, owner 2026-09-28) and rationale:
`docs/NOZZLE_DRIVE_TRADE.md`; plan `docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md`.

## Interior Air Path (tail EDF)

Standing rules for the tail EDF's air path through the fuselage interior (owner, 2026-11-19).
Basis and figures: `docs/plans/2026-11-15-002-feat-ramp-intake-edf-cooling-plan.md` (U6) and
`docs/plans/2026-11-19-001-feat-flight-engineer-split-relayout-plan.md` (R15, R16).

- **Stream floor: 12.4 in² (8,000 mm²) of free area at every bay station.** Every future
  change to the interior holds this line; lowering it is an owner decision, never an edit to
  make a layout fit. `tools/cargo_duct_layout_fit.py` (`A_STREAM_MIN`) gates it.
- **No PCB is an air dam.** Every board in the air path lies in line with the flow: its
  thinnest side is across the flow (X or Z), never along Y. The same tool gates it.

## Design Records

- Landing gear: `docs/LANDING_GEAR_ANALYSIS.md`, SCAD in `airframe/openscad/fuselage/`.
- Record load calculations, mass budgets, and CG shifts for any new or modified structure in
  its design note; record open work in the owning `WBS.md` (root §10 federation).
