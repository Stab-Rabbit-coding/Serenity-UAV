---
title: "Migrate the whole airframe to one aircraft datum (centreline, nose, ground)"
date: 2026-10-19
status: active
execution: code
owner: Stab-Rabbit-coding
author: "Claude (Claude Opus 5.5, Anthropic), under owner direction"
---

# Migrate the whole airframe to one aircraft datum

## 1. Owner direction (2026-10-19)

> "There needs to be a single datum for the entire aircraft. Specific
> translations need to be made for each nacelle, but otherwise, there's no
> reason for ever having more than one 0,0,0 point, which should be
> centerline, nose, groundplane."

Decisions taken with the owner the same day:

- **Origin:** X = 0 on the port/starboard symmetry plane; Y = 0 at the nose
  tip (the foremost point of the head shell); Z = 0 on the static ground
  plane, the aircraft at rest and level on the 3.0 in flight gear.
- **Axes keep their sense:** +X port, +Y aft, +Z up. The migration is a pure
  translation, no sign change.
- **Sequence:** migrate first, then rebuild the fuselage (symmetry, gear,
  doors) once, in the new frame.

## 2. The frame change

The old "hull frame R1" origin is the world origin of the hand-built
`SerenityAssembly.FCStd`, an arbitrary point. In R1 coordinates the new
origin sits at:

| Datum | R1 value | Source |
| --- | --- | --- |
| Centreline X | −169.850 | `tools/hull_datums.py` X_CL (the value the merge and layout tools were built on) |
| Nose tip Y | −305.704 | foremost vertex of `head_shell24_2mm_repaired.stl` after the 2026-10-19 re-centre |
| Ground Z | −80.000 | foot-sole plane, 3.0 in gear at rest (`landing_gear_r6_sizing.py` GROUND_Z_3IN) |

So **R2 = R1 + (169.850, 305.704, 80.000) mm**, defined once as
`hull_datums.R1_TO_R2`. Each nacelle keeps its own local frame and its own
bake translation into the aircraft frame (owner: "specific translations need
to be made for each nacelle").

## 3. Rules

- **R1. One origin.** After the migration, nothing outside a nacelle-local or
  part-local print frame uses any origin but the aircraft datum.
- **R2. Datums are imported, never typed.** Python reads `hull_datums`; SCAD
  includes the generated `airframe/openscad/hull_datums.scad`.
  `tools/check_datum_drift.py` fails any re-typed datum.
- **R3. Proven, not asserted.** Each migrated generator or gate is run before
  and after. Positions must move by exactly R1_TO_R2; every derived number
  (volume, clearance, margin, mass) must be unchanged.
- **R4. STL header marker.** Migrated hull-frame STLs are stamped
  `SerenityUAV AIRCRAFT-FRAME R2`. A file still carrying the R1 marker is a
  migration gap, and the drift gate fails on it.

## 4. Units

| Unit | Work | Gate |
| --- | --- | --- |
| **U1 Datum module** | `hull_datums.py`: R2 values, `R1_TO_R2`, helpers; SCAD include regenerated | `--check` |
| **U2 Inventory** | Every hull-frame STL (marker or by geometry), every Python/SCAD/FreeCAD file with frame coordinates, JSON outputs | inventory file committed |
| **U3 Drift gate** | `tools/check_datum_drift.py` in `.githooks/pre-commit` and CI: re-typed datums, R1 markers, bake table vs published meshes | runs green on the migrated tree |
| **U4 STLs** | Translate every published hull-frame STL by R1_TO_R2, restamp R2 | before/after volume and shape identical |
| **U5 Bake table + assembly** | `bake_hull_frame.py` COMPONENTS in R2; `serenity_assembly.py` reads it (no restated copies) | assembly export = U4 meshes |
| **U6 Single-source layout tools** | `cargo_layout_fit.py`, `middle_layout_fit.py`, regenerated SCAD params | regression harness |
| **U7 Merge pipelines** | `merge_cargo_interior.py`, `merge_head_interior.py`, `regen_rear_interior.py`, `add_structural_features.py`, collar/door/flange/bay/former generators | regenerate → matches U4 |
| **U8 Gates and studies** | the ~30 tools under `tools/` with frame coordinates | regression harness |
| **U9 SCAD parts** | gear CORNERS, bow pod, cargo/fuselage SCADs that place parts in the hull frame | render → matches U4 |
| **U10 Docs** | frame note in AGENTS.md "Hull-Frame Coordinate Standard"; dated docs keep R1 numbers with a pointer to this plan | doc wording |

## 5. Then rebuild, once, in R2

Symmetry (head/rear re-centre, cargo mirrored about X = 0, starboard twins
mirrored), grown thigh + 13.0 lbm wires + larger bosses, two-row layout at
both stations, F2 payload edge relief, door rework (port over starboard, one
latch), brake-guide mount, starboard bracket, battery cradle.

*Plan drafted by Claude (Claude Opus 5.5, Anthropic) under the direction of
Stab-Rabbit-coding, 2026-10-19, per `AGENTS.md` §3 AI attribution.*
