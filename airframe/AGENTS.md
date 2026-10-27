# Airframe Design — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for airframe design, fabrication, and 3D modeling.*

## Scope

This folder contains all hardware design for the airframe structure: printed shells, internal ribs and bosses, wings, nacelles, landing gear assemblies, and associated SCAD source code, FreeCAD assemblies, Blender scripts, and STL output files.

## Canonical Geometry and Coordinate System

**Aircraft datum (Rev R2 — owner directive 2026-10-19): ONE origin for the whole aircraft.**

> "There needs to be a single datum for the entire aircraft. Specific translations need to
> be made for each nacelle, but otherwise, there's no reason for ever having more than one
> 0,0,0 point, which should be centerline, nose, groundplane." — owner, 2026-10-19

- **Origin (0, 0, 0)** — on the aircraft centreline (the port/starboard symmetry plane), at
  the **nose tip** (the foremost point of the head shell), on the **static ground plane**
  (the aircraft at rest and level on the 3.0 in flight landing gear).
- **X** — positive port (left), the lateral axis; **X = 0 is the symmetry plane**, so a
  starboard twin is the port part mirrored X → −X.
- **Y** — positive aft, the longitudinal axis; Y = 0 at the nose tip.
- **Z** — positive up (dorsal); Z = 0 on the ground plane.

Rules:

- **Every** design artifact uses this datum: SCAD sources, STLs, STEP files,
  Blender/FreeCAD/Python generators and gates, and documentation. Each STL and STEP is
  published **at its installed position** in the aircraft datum, so it imports into FreeCAD
  with identity placement. Print orientation is a slicer operation; a `*_print.stl` copy
  in print orientation is a derived export for the slicer only and is never used for fit
  or clash checking.
- **One STL per installed instance** (owner 2026-10-19): a part used at several positions
  (four leg frames, eight nozzle flaps per nacelle, repeated fasteners and placeholders)
  is published as one STL per instance, each at its own installed position (e.g.
  `lg_r6_3_0in_leg_frame_fore-port.stl`), all generated from the same source — never a
  hand copy, and never a design STL plus a separate placement table.
- **The only exception is a PCB while it is being designed in KiCad**, which keeps
  KiCad's own board coordinates. Any PCB **STEP or STL used for fitting** (enclosures,
  bays, census, mass ledger) is exported or placed **in the aircraft datum** at its
  installed position.
- **Nacelles:** each nacelle's geometry is stored in the aircraft datum at the cruise
  (forward-flight) attitude. Tilt is applied as that nacelle's own rotation about its
  pivot axis; this is the one per-part transform allowed.
- **Datums are never re-typed.** Python imports `tools/hull_datums.py`; OpenSCAD includes
  the GENERATED `airframe/openscad/hull_datums.scad`. `tools/check_datum_drift.py` (in
  `.githooks/pre-commit` and CI) fails a re-typed datum or a stale frame marker.

**Migration in progress:** the former "hull frame R1" put the origin at the
`SerenityAssembly.FCStd` world origin, an arbitrary point. R2 = R1 + (169.850, 305.704,
80.000) mm (`hull_datums.R1_TO_R2`). Until every file is migrated (plan
`docs/plans/2026-10-19-001-aircraft-datum-migration-plan.md`, WBS DATUM-R2), a file is in
R2 only if its STL header carries `SerenityUAV AIRCRAFT-FRAME R2` or its code imports the R2
datums. Numbers quoted in dated documents written before 2026-10-19 are R1.
**`airframe/HULL_FRAME_REFERENCE.md`** holds the bake workflow, the canonical-accuracy
authority order (REF-CAD-002/003/004, `docs/references/`) and the baked-extents table; it
is re-issued in R2 by the migration.

## Geometry Reference Points

The fuselage has four canonical sections, each with specific spatial properties:

- **Head** — forwardmost; tapers to a narrow nose (most negative Y extent)
- **Cargo** — immediately aft of head; largest cross-section; wing attachment flanges on upper outer edges; bay door opens toward −Z (ventral)
- **Middle** — narrow horseshoe-ring neck between cargo and rear; open at −Z (ventral); houses the inner-neck tube and Flight Engineer's room (power distribution); aft EDF intake scoops belong to Phase 11 (`deferred/AGENTS.md`)
- **Rear** — aftmost; houses engine room, dorsal pod, and two landing skids extending aft

**Wings and nacelles:**

- Wings attach to the cargo section lateral walls
- Nacelles are at the pylon tips, outboard of the wings; stored in forward-flight attitude; in hover they tilt to vertical thrust

## Fabrication Standards

Root `AGENTS.md` §7 "Fabrication Standards" is authoritative for material, print parameters,
shell wall and foam fill, integrated bosses/ribs/brackets, and the open inter-section mating
faces — read it there and do not restate it here.

Airframe-specific application: root §7's structural-joint rule (minimum 2-wall contact annulus
**and** positive-stop shoulder — never a friction fit alone on a flight-critical joint) and its
mandatory post-edit mesh validation apply to every model in this folder. Additionally, models
shall be **ready to slice for printing** immediately after generation; report validation findings
in `TODO.md` and resolve all violations before committing.

## STL and SCAD Conventions

### File Naming

- **Legacy `s_` prefix dropped (Rev R1):** Historical shell/STL/SCAD files used the prefix `s_` (e.g., `s_cargo_sect_shell24_2mm_repaired.stl`). This prefix is no longer used in active files. When you encounter an `s_`-prefixed reference in active code or docs, drop the prefix and correct the string in place.
- Active files use unprefixed names: `cargo_sect_shell24_2mm_repaired.stl`

### SCAD Source Code

Generator scripts may model parts in a convenient part-local frame, but any **regenerated primary-component STL must be re-baked before publishing**.

**SCAD best practices:**

- 4-space indenting
- Verbose comments conforming to OpenSCAD style
- Validation: render and verify bore diameters and Z-range in console output before committing

## Blender Pipeline

**Blender-canonical source directory:** `airframe/blender-scripts/files-hollowed-24in/`
These are the **authoritative canonical sources** for all fuselage geometry. Any future geometry
change must start from the corresponding Blender source file in this directory. SCAD files for
fuselage shells are secondary references only.

The headless invocation, the fuselage bake pipeline (update source → copy into
`airframe/stls/fuselage/`, or `fuselage/cargo/` for cargo → run `tools/bake_hull_frame.py`), and
the pre-commit checklists are in `tools/TOOL_REFERENCE.md` "Blender Hollowing Pipeline" — do not
restate them here. After running any script, verify Z-range and bore-diameter in console output
before committing; output STLs go to `airframe/stls/` (subdirectories: `fuselage/`, `nacelles/`,
`wings/`).

## Engineering Requirements — Weight, Balance, Power, Space

Every structural modification must account for real loads and mass budgets: size fasteners,
walls, and structural members for actual loads; quote actual masses and center-of-gravity (CG)
shifts when adding or removing geometry; **do not leave these values as "TBD."** Units follow
root `AGENTS.md` §5 "Engineering Requirements".

## Assembly and Placement

The canonical assembly document is `airframe/freecad/assembly/SerenityAssembly.FCStd`.
The headless assembly script is `airframe/FreeCAD-scripts/serenity_assembly.py` (run with `freecadcmd`).

PCB and avionics footprint placement is governed by root `AGENTS.md` §5 and
`avionics/AGENTS.md` "Footprint and Component Placement" — not by this file.

## Geometry Integrity — Keep Skin True to Canon

- **Retain the outer mold line** of Serenity's canonical hull to the greatest extent possible
- **Interior modifications** (bore carving, sleeve insertion, boss protrusions) must blend into the canonical exterior hull
- **Do not alter the outer mold line unless structurally required**
- Because Serenity's geometry is complex, **bounding boxes and centroid calculations are inadequate** for positioning and orienting parts — use the validated extents in `airframe/HULL_FRAME_REFERENCE.md`
- If there is uncertainty about placement, request manual placement in FreeCAD by the user

## Work Tracking and Documentation

- When adding a new structure or modifying an existing one, record load calculations, mass budgets, and CG shifts in a design note or commit message
- Update `TODO.md` with any unresolved mesh validation issues, deferred design work, or fabrication notes
- When a script regenerates STLs, verify Z-range and bore-diameter in console output **before committing**
- Index and archive upkeep (`PROJECT_INDEX.md`, `ARCHIVE_INDEX.md`) follows root `AGENTS.md` §10

## Landing Gear

The landing-leg design (post/wire geometry, materials, energy sizing, selected variant) changes as
testing matures and is descriptive. Do not restate it here or in any other `AGENTS.md`. Read it
directly:

- **Canonical design and structural analysis:** `docs/LANDING_GEAR_ANALYSIS.md`
- **SCAD source and variants:** `airframe/openscad/fuselage/`. Decision (2026-09-06): the 3.0 in
  leg (`canonical_leg_r6_3_0in.scad`) is the flight article, driven by nozzle belly clearance
  (`docs/LANDING_GEAR_ANALYSIS.md` §4.8); the 1.5 in leg (`canonical_leg_r6_1_5in.scad`) is
  retired to bench and ground-handling use. The Rev R5 `wire_brace_leg.scad` is superseded.
- **Open work:** `airframe/landing-gear/TODO.md`

## Nacelle Nozzle Drive

Each nacelle nozzle is variable-diameter and **scheduled on measured nacelle tilt**, sized 75% of
bore at 0° (forward) to 105% of bore at every tilt from 90° to the 145° limit (vertical/backing),
and shall fail to 105% on loss of servo power, command, or tilt-angle validity — a fixed
functional requirement. Decision (owner, 2026-09-28, servo drive): one sub-micro servo per nacelle
inside the pod, commanded from the tilt angle by its bus gateway, pulling the unison ring through a
pull-only link against a spring that opens it to a hard 105% stop; the passive gear and linkage
drives were retired. The trade study holds the rationale. Read the current state directly:

- **Trade study and decision record:** `docs/NOZZLE_DRIVE_TRADE.md`
- **Implementation plan:** `docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md`
- **Open work:** `airframe/wings-nacelles/TODO.md`
