# Airframe Design Archive — Rev Q (2026-06-05)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/
**Archived:** 2026-06-05 (Revision Q)

---

## Purpose

Rev Q establishes a single canonical design for each airframe component by archiving
superseded design variants, exploratory scripts, and mesh-repair copies that accumulated
during development. Only production-ready, slice-ready STLs and their generating scripts
remain in the active `airframe/` tree.

---

## Archived Blender Scripts (`blender-scripts/`)

| File | Archived Reason |
|------|-----------------|
| `blender_nacelle_integrated_v1.py` | Superseded by `blender_nacelle_revo.py` (Rev O) |
| `blender_nacelle_integrated_v2.py` | Superseded by `blender_nacelle_revo.py` (Rev O) |
| `blender_shells_v3_2mm.py` | Exploratory 2 mm thin-shell variant — not used in build |
| `blender_shells_v3_50mm.py` | Exploratory 50 mm thick-shell variant — not used in build |
| `generate_hollow_shells.py` | Intermediate script superseded by `blender_shells_v3.py` |
| `generate_shells_v2.py` | Intermediate script superseded by `blender_shells_v3.py` |

**Canonical nacelle scripts (active):**
- `airframe/blender-scripts/blender_nacelle_revo.py` — Rev O CG-pivot nacelle with 11-fin stator
- `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad` — parametric nacelle pod, SWIRL_DIR=±1

**Canonical shell scripts (active):**
- `airframe/blender-scripts/blender_shells_v3.py` — 2.5 mm hull shell generator

---

## Archived Nacelle STLs (`stls/nacelles/`)

| File | Archived Reason |
|------|-----------------|
| `s_eng_left_shell24_50mm_repaired.stl` | Mesh-repair copy; canonical file is `s_eng_left_stator_shell24_revo.stl` |
| `s_eng_right_shell24_50mm_repaired.stl` | Mesh-repair copy; canonical file is `s_eng_right_stator_shell24_revo.stl` |
| `s_nacelle_port_revt.stl` | Intermediate Rev T nacelle; superseded by revo design |
| `s_nacelle_stbd_revt.stl` | Intermediate Rev T nacelle; superseded by revo design |
| `sector_gear_22mm_fixed.obj` | Mesh-fixed OBJ; superseded by `nacelle_sector_gear.stl` (from SCAD) |
| `sector_gear_22mm_fixed.stl` | Mesh-fixed STL; superseded by `nacelle_sector_gear.stl` (from SCAD) |
| `stator_50mm.stl` | Standalone stator; superseded by stator integral to nacelle shell |

### Archived Nozzle STLs (`stls/nacelles/nozzles/`)

| File | Archived Reason |
|------|-----------------|
| `nacelle_nozzle_closed_asm_repaired.stl` | Mesh-repair copy; canonical is `nacelle_nozzle_closed_asm.stl` |
| `nacelle_nozzle_petal_repaired.stl` | Mesh-repair copy; canonical is `nacelle_nozzle_petal.stl` |
| `rear_nozzle_petal_repaired.stl` | Mesh-repair copy; canonical is `rear_nozzle_petal.stl` |

---

## Archived Fuselage STLs (`stls/fuselage/`)

### Main Fuselage Variants

| File | Archived Reason |
|------|-----------------|
| `hull_engine_bell.stl` | Pre-Rev N engine bell; superseded by `s_edf_120_motor_mount.stl` + `s_edf_120_thrust_tube.stl` |
| `s_rear_shell24.stl` | Pre-Rev N rear shell without radial scoop windows; superseded by `s_rear_neck_intake_shell24.stl` |
| `s_rear_shell24_2mm.stl` | 2 mm exploratory variant; not used in build |
| `s_rear_shell24_2mm_repaired.stl` | Mesh-repair copy of 2 mm variant |
| `s_rear_shell24_repaired.stl` | Mesh-repair copy; superseded by current SCAD export |
| `s_head_shell24_2mm.stl` | 2 mm exploratory variant; not used in build |
| `s_head_shell24_2mm_repaired.stl` | Mesh-repair copy of 2 mm variant |
| `s_head_shell24_repaired.stl` | Mesh-repair copy; superseded by current SCAD export |
| `s_middle_shell24.stl` | Pre-canonical belly-scoop middle section; superseded by `s_middle_canonical_shell24.stl` |
| `s_middle_intake_shell24.stl` | Exploratory belly-intake variant; superseded by neck-radial-intake design |
| `s_middle_shell24_2mm.stl` | 2 mm exploratory variant |
| `s_middle_shell24_2mm_repaired.stl` | Mesh-repair copy |
| `s_feet_x_4_scaled24_repaired.stl` | Mesh-repair copy; canonical is `s_feet_x_4_scaled24.stl` |

### Cargo Section Variants

| File | Archived Reason |
|------|-----------------|
| `s_cargo_sect_shell24_2mm.stl` | 2 mm exploratory variant; not used in build |
| `s_cargo_sect_shell24_2mm_repaired.stl` | Mesh-repair copy |
| `s_cargo_sect_shell24_repaired.stl` | Mesh-repair copy; canonical is `s_cargo_sect_shell24.stl` (Rev S) |
| `s_cargo_door_scaled24.stl` | Pre-Rev P placeholder cargo door |
| `s_cargo_door_strutts_scaled24.stl` | Pre-Rev P placeholder cargo door with struts |

---

## Active Canonical Designs (Rev Q)

All production-ready STLs are in `airframe/stls/` with their generating scripts.
See `current-specification/serenity-rev-q.jsx` (Airframe tab) for the complete print schedule.
