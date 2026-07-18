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

As of R1 (2026-06-11), validated component placements are **baked into the published STL vertex data** by `tools/bake_hull_frame.py` (binary header marker: `SerenityUAV HULL-FRAME R1`). Every primary STL in `airframe/stls/` is stored **directly in hull-frame coordinates** and imports into FreeCAD with **identity placement**. Do not apply per-part transforms when positioning these components.

**Bake workflow (if you regenerate primary STLs):**
```sh
python3 tools/bake_hull_frame.py            # all components (idempotent)
python3 tools/bake_hull_frame.py --check    # report baked state only
```

Never bake a mesh *derived from* an already-baked file (e.g. a Blender repair of a baked STL loses the header marker).

## Geometry Reference Points

The fuselage has four canonical sections, each with specific spatial properties:

- **Head** — forwardmost; tapers to a narrow nose (most negative Y extent, Y ≈ −305.6 mm)
- **Cargo** — immediately aft of head; largest cross-section; wing attachment flanges on upper outer edges; bay door opens toward −Z (ventral)
- **Middle** — narrow horseshoe-ring neck between cargo and rear; open at −Z (ventral); houses the inner-neck tube and Kaylee's room (power distribution); aft EDF intake scoops deferred to Phase 11
- **Rear** — aftmost; houses engine room, dorsal pod, and two landing skids extending aft

**Wings and nacelles:**
- Wings attach to the cargo section lateral walls
- Nacelles are at the pylon tips, outboard of the wings; stored in forward-flight attitude; in hover they tilt to vertical thrust

See "Validated baked extents" and "Geometry Integrity" below for full spatial bounds and qualitative relationships.

## Fabrication Standards

### Material and Print Parameters

**CF-PETG** is the standard material:
- Layer height: 0.15 mm
- Perimeters: 4 minimum
- Infill: ≥40% for load-bearing regions; 25% for non-structural fill

(The DaVinci Jr prototype is exempt from these standards; it is not expected to meet full-build specifications.)

### Shell Specifications

- **Exterior shell walls:** hollowed to 2.0 mm (0.079 in) CF-PETG while maintaining a **watertight mesh surface** with no voids or holes
- **Interior fill:** 2 lb/ft³ (32 kg/m³) low-density closed-cell foam to provide internal structure and support
- **Bosses and ribs:** added to the interior as needed for mounting hardware, components, or structural flight requirements
- **Mating faces:** left open between the four fuselage sections to allow construction access and inter-compartment cable routing
- **Mounting brackets:** integrated and printed as part of the shell where feasible

### Structural Joints

All load-bearing mating surfaces must comply with:
- **Minimum 2-wall contact annulus** to ensure adequate surface area
- **Positive-stop shoulder** to prevent sliding under load
- **Friction fits alone are not acceptable** for flight-critical joints

### Mesh Validation

Every 3D model modification **must** be verified to produce clean, watertight surfaces:

1. Run mesh verification tools after every modification
2. Report all findings in `TODO.md`
3. Resolve all violations before committing

Models shall be **ready to slice for printing** immediately after generation.

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

The canonical fuselage source is the Blender hollowing pipeline:

**Blender-canonical source directory:** `airframe/blender-scripts/files-hollowed-24in/`  
These are the **authoritative canonical sources** for all fuselage geometry. Any future geometry change must start from the corresponding Blender source file in this directory. SCAD files for fuselage shells are secondary references only.

**Bake pipeline for fuselage sections:**
1. Update source in `airframe/blender-scripts/files-hollowed-24in/`
2. Copy updated file to `airframe/stls/fuselage/` (or `fuselage/cargo/` for cargo)
3. Run bake tool: `python3 tools/bake_hull_frame.py`

**Blender script execution:**
```sh
blender --background --python <script>.py
```

After running scripts:
- Verify Z-range and bore-diameter in console output before committing
- Output STLs go to `airframe/stls/` (subdirectories: `fuselage/`, `nacelles/`, `wings/`)

## Engineering Requirements — Weight, Balance, Power, Space

Every structural modification must account for real loads and mass budgets:

- **Size fasteners, walls, and structural members** for actual loads
- **Quote actual masses** and center-of-gravity (CG) shifts when adding or removing geometry
- **Do not leave these values as "TBD"**
- Use **imperial-primary with metric in parentheses** for all measurements (e.g., 10 in (254 mm))

For mass and force units:
- **lbm** for mass (pounds-mass)
- **lbf** for force (pounds-force)
- **kg** for metric mass; **N** for metric force
- **kt** (knots) for airspeed and wind speed

## Assembly and Placement

The canonical assembly document is `airframe/freecad/assembly/SerenityAssembly.FCStd`.  
The headless assembly script is `airframe/FreeCAD-scripts/serenity_assembly.py` (run with `freecadcmd`).

**PCBs and avionics placement:**
- PCBs are tightly packed; final component footprint positions will be placed manually after PCBs are populated and nets are built by script
- If a KiCad DRC violation requires repositioning a component footprint, refer the action to the user; other modifications are allowed

**Validated baked extents (hull frame, mm — updated 2026-06-13):**

| Component | X min..max | Y min..max | Z min..max |
| --- | --- | --- | --- |
| Head_Shell | −232.9..−103.5 | −305.7..−70.7 | +61.1..+201.5 |
| Cargo_Shell | −267.0..−72.7 | −71.5..+132.0 | 0.0..+163.2 |
| Middle_Shell | −258.5..−81.6 | +130.4..+203.6 | +1.3..+166.1 |
| Rear_Shell | −246.1..−105.5 | +203.2..+384.3 | +3.3..+161.1 |
| Wing_Port | −93.0..+4.7 | −7.0..+122.0 | +48.0..+77.0 |
| Wing_Stbd | −347.7..−250.0 | −12.0..+117.0 | +48.0..+77.0 |
| Nacelle_Port | +4.0..+86.0 | −58.2..+108.3 | +21.4..+104.7 |
| Nacelle_Stbd | −428.1..−346.1 | −64.2..+102.3 | +23.3..+106.6 |

## Geometry Integrity — Keep Skin True to Canon

- **Retain the outer mold line** of Serenity's canonical hull to the greatest extent possible
- **Interior modifications** (bore carving, sleeve insertion, boss protrusions) must blend into the canonical exterior hull
- **Do not alter the outer mold line unless structurally required**
- Because Serenity's geometry is complex, **bounding boxes and centroid calculations are inadequate** for positioning and orienting parts
- **Use the validated orientation and positions listed above** for determining where parts fit in space
- If there is uncertainty about placement, request manual placement in FreeCAD by the user

## Work Tracking and Documentation

- When adding a new structure or modifying an existing one, record load calculations, mass budgets, and CG shifts in a design note or commit message
- Update `TODO.md` with any unresolved mesh validation issues, deferred design work, or fabrication notes
- When a script regenerates STLs, verify Z-range and bore-diameter in console output **before committing**
- Keep `PROJECT_INDEX.md` up to date: add new active files, move archived files to `ARCHIVE_INDEX.md`

## Landing Gear

The landing-leg design (post/wire geometry, materials, energy sizing) changes as testing
matures — do not restate its specifics here or in any other file; they will go stale. Read
the current revision directly:

- **Canonical design and structural analysis:** `docs/LANDING_GEAR_ANALYSIS.md`
- **SCAD source:** `airframe/openscad/fuselage/wire_brace_leg.scad`
- **Open work:** `TODO.md` §1.1.4

## Nacelle Nozzle Drive

Each nacelle nozzle is variable-diameter, driven by nacelle tilt, sized 75% of bore at 0°
(forward) to 105% of bore at ≥90° (vertical/backing) — a fixed functional requirement. The
mechanism that achieves it (gear train vs. linkage alternatives) is an **active trade study**;
do not assume a specific mechanism here. Read the current state directly:

- **Trade study and current recommendation:** `docs/NOZZLE_DRIVE_TRADE.md`
- **SCAD source:** `nacelle_nozzle_iris.scad`
- **Open work:** `TODO.md` §1.1.3.1

---

For project-wide standards, see the root `AGENTS.md`.
