# Airframe Design — Agent Instructions

> *See the root `AGENTS.md` for project-wide policies. This file provides specific guidance for airframe design, fabrication, and 3D modeling.*

## Scope

This folder contains all hardware design for the airframe structure: printed shells, internal ribs and bosses, wings, nacelles, landing gear assemblies, and associated SCAD source code, FreeCAD assemblies, Blender scripts, and STL output files.

## Canonical Geometry and Coordinate System

**Hull-frame coordinate standard (Rev R1 — baked, canonical):**

All design artifacts in this folder — SCAD sources, STLs, Blender/FreeCAD scripts, and documentation — use the **single validated hull frame**:

- **X** — positive port (left) — the lateral axis
- **Y** — positive aft (back) — the longitudinal axis (nose tip at Y ≈ −305.6 mm)
- **Z** — positive dorsal (up)
- **Origin** — the `airframe/freecad/assembly/SerenityAssembly.FCStd` world origin

Primary STLs in `airframe/stls/` are stored directly in hull-frame coordinates and import into
FreeCAD with **identity placement** — do not apply per-part transforms. **`airframe/HULL_FRAME_REFERENCE.md`**
holds the bake workflow and `tools/bake_hull_frame.py` usage, the canonical-accuracy authority
order (REF-CAD-002/003/004, `docs/references/`), and the validated baked-extents table for all
eight primary components. Read it before regenerating or placing any primary STL.

## Geometry Reference Points

The fuselage has four canonical sections, each with specific spatial properties:

- **Head** — forwardmost; tapers to a narrow nose (most negative Y extent, Y ≈ −305.6 mm)
- **Cargo** — immediately aft of head; largest cross-section; wing attachment flanges on upper outer edges; bay door opens toward −Z (ventral)
- **Middle** — narrow horseshoe-ring neck between cargo and rear; open at −Z (ventral); houses the inner-neck tube and Flight Engineer's room (power distribution); aft EDF intake scoops deferred to Phase 11
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

The landing-leg design (post/wire geometry, materials, energy sizing) changes as testing
matures — do not restate its specifics here or in any other file; they will go stale. Read
the current revision directly:

- **Canonical design and structural analysis:** `docs/LANDING_GEAR_ANALYSIS.md`
- **SCAD source:** `airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad` (THE FLIGHT
  ARTICLE, adopted 2026-09-06 — nozzle belly-clearance driver, `docs/LANDING_GEAR_ANALYSIS.md`
  §4.8) and `canonical_leg_r6_1_5in.scad` (RETIRED to bench/ground-handling use — below the
  minimum safe nozzle clearance). The Rev R5 `wire_brace_leg.scad`
  this file used to name is superseded — corrected 2026-08-23.
- **Open work:** `airframe/landing-gear/TODO.md` §1.1.4

## Nacelle Nozzle Drive

**Phases 5–10 (Rev T6, owner decision D-TW-3, 2026-09-29): each nacelle carries a one-piece
FIXED OPEN nozzle** whose FLOW exit radius is 105% of the bore radius (26.25 mm) — the hover
setting of the variable requirement below, held at every tilt. It has no drive and no failure
mode to manage. Source `nacelle_nozzle_fixed.scad`; rationale and trade in
`docs/plans/2026-09-29-001-tw-recovery-stem-to-stern-plan.md` §6.1. The exit radius is a
parameter so the thrust stand can move it; change the requirement here if the stand does.
The tilt pivot was re-datumed to the resulting CG, `PIVOT_Z` 103.5 mm (D-TW-5).

**The variable-diameter requirement below is DEFERRED to Phase 11b** (`deferred/WBS.md`). It
stands as the Phase 11 target, unchanged, with one correction to carry: the percentages apply to
the nozzle's FLOW surface. The modelled iris placed them on the flap hinge line and reached only
95% at "open".

Each nacelle nozzle is variable-diameter, **scheduled on measured nacelle tilt**, sized 75% of
bore at 0° (forward) to 105% of bore at every tilt from 90° to the 145° limit (vertical/backing),
and shall fail to 105% on loss of servo power, command, or tilt-angle validity — a fixed
functional requirement. Mechanism (owner decision 2026-09-28, servo drive): one sub-micro servo per
nacelle inside the pod, commanded from the AK7455 tilt angle by its bus gateway, pulling the
unison ring through a pull-only link against a spring that opens it to a hard 105% stop. The
passive gear/linkage drives were retired (unbuildable in the Rev T4 joint; over-travel past 90°).
Read the current state directly:

- **Trade study and decision record:** `docs/NOZZLE_DRIVE_TRADE.md`
- **Implementation plan:** `docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md`
- **SCAD source:** `nacelle_nozzle_fixed.scad` (Phases 5–10); `nacelle_nozzle_iris.scad`
  (deferred, Phase 11b)
- **Open work:** `TODO.md` §1.1.3.1 (fixed nozzle); `deferred/TODO.md` §Phase11b (iris)
