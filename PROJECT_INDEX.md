# PROJECT_INDEX.md — Serenity UAV
<!-- Auto-maintained: updated whenever active files are added or removed. -->
<!-- Archive contents described in ARCHIVE_INDEX.md. -->
<!-- Last updated: 2026-07-07 — Wing Rev R1a (spar de-skewed/camber-centred + EDF cableway); nozzle-drive trade study (NOZZLE_DRIVE_TRADE.md) -->

## Repository Root

```text
.editorconfig                     — Editor whitespace/indent rules (4-space, per coding standard)
.flake8                           — Python lint configuration
.gitignore                        — Repository-wide VCS ignore rules
.liveui.json                      — Live UI preview configuration
.github/workflows/ci.yml          — CI pipeline (lint, STL validation, build checks)
.github/workflows/ossar.yml       — OSSAR static-analysis security workflow
.github/workflows/stale-branches.yml — Stale branch cleanup workflow
.vscode/extensions.json           — Recommended VS Code extensions
AGENTS.md                         — Instructions for AI agents (authoritative source: CLAUDE.md;
                                    federated guidance in subordinate folders)
CLAUDE.md                         — Project instructions and standards (includes Standards Vetting Policy)
LICENSE                           — Repository license (CC BY 4.0)
PROJECT_INDEX.md                  — This file
ARCHIVE_INDEX.md                  — Archive file tree (see below)
README.md                         — Project overview
REFERENCES.md                     — Standards and regulatory reference catalog (REF-IDs, verified URLs,
                                    chapter/section/paragraph per citation, repo usage index)
REPO_ENFORCEMENT.md               — Repository rules
SECURITY.md                       — Security policy and vulnerability reporting
TODO.md                           — Work-breakdown structure and open items
freecad-stl2part.py                — Standalone FreeCAD STL→Part conversion utility
package.json                       — Node.js dependency manifest (tooling/preview support)
package-lock.json                  — Node.js dependency lockfile
previewConfig.json                 — Live preview configuration
requirements-dev.txt               — Python development dependencies
```

---

## tools/

Repository-level engineering tools and build automation.

```text
TODO.md                           — Build-tools & automation WBS (reference index into master TODO.md §1.1/Phase 0)
CLAUDE.md                         — Build tools and automation standards (hull-frame bake tool,
                                    Blender pipeline, SCAD generation, mesh validation)
validate_stls.py                  — CI STL watertight validator (trimesh)
verify_bow_pod.py                 — Bow sensor pod geometry verifier: ray-casts the camera/ToF/laser bores
                                    against the baked head shell on the 40° flat (replaces manual slicer checks)
bake_hull_frame.py                — R1: bakes validated FreeCAD placements into primary
                                    STLs (hull frame: X=+port, Y=+aft, Z=+dorsal);
                                    idempotent via 'SerenityUAV HULL-FRAME R1' STL
                                    header marker; single source of the historical
                                    placement constants (COMPONENTS)
```

---

## airframe/

Structural design, fabrication, 3D modeling, and CAD assembly.

```text
TODO.md                           — Airframe WBS view — master §1.1 geometry (STL exports); §2.x procurement refs
CLAUDE.md                         — Airframe design standards (coordinate system, CAD/3D
                                    modeling, hull-frame bake, fabrication specs, STL
                                    validation, structural joints, landing gear)
```

### airframe/FreeCAD-scripts/

Assembly pipeline for FreeCAD 0.20+ with Assembly4.

```text
Makefile                          — Build: SCAD→STL (openscad) + headless assembly (freecad)
serenity_assembly.py              — Full-airframe FreeCAD assembly (Rev R1, 2026-06-11:
                                    baked hull-frame STLs, identity placements; run with
                                    freecadcmd)
faraday-enclosure.py              — Faraday-cage avionics enclosure FreeCAD generator
make_flat_pattern.py              — Sheet-metal/flat-pattern unfold utility for FreeCAD parts
serenity_placeholders_assembly.py — Placeholder-block assembly (massing/CG study)
```

(5 deprecated prototype scripts — assembly1.py, Serenity-Assemble.py,
Serenity-Subsystem-Assembly.py, serenity_subsystem_assembler.py,
serenity_fuselage_asm4.py — archived 2026-06-29 to
airframe/archive/FreeCAD-scripts/; see ARCHIVE_INDEX.md.)

### airframe/blender-scripts/

Headless Blender Python scripts for shell hollowing and STL generation.

```text
add_structural_features.py        — Structural joint-feature booleans on head + middle baked shells (Rev R1; MESH-01 root-cause fix 2026-06-30 = single batched manifold3d difference; joint boss-pins removed 2026-07-06 — splice collars supersede; cargo DELEGATED to merge_cargo_interior.py, rear DELEGATED to regen_rear_interior.py): lofted bore-open joint faces, keel channel, ring-frame pockets, skid-rod bores; exports inner-profile CSVs
merge_cargo_interior.py           — DEFINITIVE cargo-shell processor (Rev R1 2026-06-30): clean-source bake + one robust manifold3d pass merging interior-wall (duct) removal, clamshell door aperture + hinge retention blocks, head/cargo + cargo/middle joint features (lofted bore-open cutter, JOINT-01 fix 2026-07-06), wing spar/mortises/bosses (re-derived chord), nacelle-servo pads, Inara avionics bosses; watertight single body
regen_rear_interior.py            — DEFINITIVE rear-shell processor (2026-07-06, MESH-01 fix): clean-source IN-MEMORY bake (float64, avoids the float32-STL-round-trip that split the delicate 3-body rear source and inflated manifold3d to ~357k) + single manifold3d boolean of the rear features (lofted bore-open fwd joint, keel channel, Y=+290 ring pocket, 2× skid-rod bores); watertight single body, 246,769 mm³; stamps HULL-FRAME R1 (do not re-bake)
merge_head_interior.py            — Bow sensor pod merge (Rev R1d 2026-07-03, TODO.md §1.1.1.1a): merges bow_sensor_pod.scad's camera/ToF/laser/faceplate-seat cuts into the published, already boss-featured head_shell24_2mm_repaired.stl via one manifold3d boolean; watertight single body, 183,192 mm³; Vera nose bosses and Shepherd's Book-bay bosses deliberately excluded (unverified/buggy placements, not yet certified)
blender_edf_bore_and_petals.py    — EDF bore + nozzle petal geometry
blender_hollow_shells.py          — Centroid-inset 2mm shell hollowing (all 4 sections)
blender_intake_cut.py             — Fuselage EDF intake cut
blender_middle_intake_cut.py      — Middle section intake cut
blender_nacelle_revo.py           — Nacelle pod shell from hull STL
blender_nozzle_gen.py             — Iris nozzle petal geometry
blender_shells_2mm_solidify.py    — 2mm solidify-modifier hollowing pass (Blender pipeline)
blender_shells_v3.py              — Rev N 24" hull shell generation
blender_stator_gen.py             — 11-fin inter-stage stator
check_nacelle_alignment.py        — Nacelle bore alignment verification
engrave_plaques.py                — Engraves identification plaques into hull shells
engrave_shuttles.py               — Engraves avionics bay shuttle/crew-quarter labels
fill_thin_details.py              — Fills thin-wall mesh details prior to hollowing
finalize_cargo_middle.py          — Final cargo + middle section mesh finishing pass
finalize_head_rear.py             — Final head + rear section mesh finishing pass
generate_overview_svgs.py         — SVG renders from 6 cardinal + 8 isometric views
hollow_manifold.py                — Manifold-safe shell hollowing utility
inspect_shell_center.py           — STL centroid measurement utility
make_bay_text.py                  — Generates avionics bay name text meshes (Shepherd/Inara/River/Simon)
make_shuttle_text.py              — Generates shuttle/section label text meshes
morph_open_voxel.py                — Voxel-remesh based mesh morph/open-surface repair
repair_shells_for_scad.py         — Mesh repair pipeline (voxel-remesh → manifold)
verify_shells.py                  — Post-hollow shell mesh verification (watertight/manifold check)
files-hollowed-24in/              — Canonical Rev R1 24" hollowed shell source STLs (pre-bake; see
                                    CLAUDE.md Hull-Frame Coordinate Standard) + operands/ boolean
                                    operand meshes (inner/outer split surfaces, engraved text meshes)
```

### airframe/gcode/davinci-jr-proto/

Prototype print batches (DaVinci Jr., PLA, visual-only parts).

```text
.gitignore                        — VCS ignore rules for generated g-code batch output
davinci_jr_pla.ini                — Slicer profile
slice_all_batches.sh              — Batch slicer script (Phase 11 deferred aft-EDF parts; see
                                    docs/PROTO_PRINT_DAVINCI_JR.md)
xyz_wrap.py                       — XYZ encryption wrapper
batch_A/ … batch_Q/               — Print batches A–Q (see TODO.md §1.1)
batch_VISUAL/                     — Visual-only prototype parts
```

### airframe/freecad/assembly/

Working FreeCAD assembly directory (in-progress / backup state; not yet the published
canonical `SerenityAssembly.FCStd` referenced by CLAUDE.md's Hull-Frame Coordinate Standard).

```text
SerenityAssembly.FCStd            — FreeCAD assembly document (canonical per CLAUDE.md
                                    Hull-Frame Coordinate Standard)
SerenityAssembly.FCStd.bak2       — FreeCAD assembly backup
```

(serenity_fuselage_asm4.py archived 2026-06-29 to airframe/archive/FreeCAD-scripts/;
see ARCHIVE_INDEX.md.)

### airframe/openscad/

All parametric source files.  Compiled to STLs via `airframe/FreeCAD-scripts/Makefile`.

#### airframe/openscad/fuselage/

```text
head_shell24.scad               — Nose/cockpit shell, 2mm CF-PETG skin (Rev R1a); integrates bow_sensor_pod.scad
bow_sensor_pod.scad             — Bow sensor pod CSG cuts on the 40° nose flat (Rev R1c): camera (PORT bump)
                                    10mm lens, ToF (STBD bump) 8mm, crosshair laser (CL) 6mm exit; bumps shaved +
                                    4× M2 inserts; use'd by head_shell24.scad
bow_sensor_faceplate.scad       — Combined bow sensor faceplate (Rev R1c): single 28×16×2.5mm CF-PETG plate
                                    carrying all three bow apertures; replaces the two camera bumps / separate bezels
middle_canonical_shell24.scad   — Horseshoe neck section shell (Rev R)
rear_shell24.scad               — Aft engine-room shell, 2mm CF-PETG (Rev R)
battery_tray.scad               — 6S 4000mAh LiPo tray, keel-rail slide (Rev R)
belly_panel.scad                — Battery bay belly access panel (Rev R)
access_panels_24in.scad         — All hull access panels: 4× Faraday-bay covers (Shepherd/Inara/River/Simon),
                                    2× ventral hatch covers (battery/Kaylee), 2× ventral hatch frames (Rev R)
rcrs49_wire_post.scad           — 49 MHz (Part 15 §15.235) top-wire antenna post, 12×12 mm PETG mast (Rev R)
landing_leg_assy.scad           — Rev R1 4× field-replaceable landing legs (CF-PETG flat spring,
                                    22×10mm, 185mm) + hull boss + 3×M3 nylon shear-bolt fuse;
                                    see docs/LANDING_GEAR_ANALYSIS.md for structural analysis
cargo/
cargo_sect_shell24.scad       — Rev R cargo section shell with clamshell doors, avionics bays, GPS mounts
```

#### airframe/openscad/nacelles/

```text
nacelle_pod_50mm_tandem_simple.scad — Rev R tandem pod, push-on nozzle (no iris; carried fwd from Rev T2)
nacelle_pod_50mm_tandem.scad        — Rev R tandem pod, full iris gear train (carried fwd from Rev T)
edf_stator_sleeve.scad              — Rev R 11-fin inter-stage stator sleeve (carried fwd from Rev A)
edf_aft_spider_sleeve.scad          — Rev R aft spider/motor-mount sleeve (carried fwd from Rev A)
edf_bore_sleeve.scad                — DEPRECATED (superseded by stator+spider)
nacelle_nozzle_straight.scad        — Rev R push-on straight nozzle (carried fwd from Rev T2)
nacelle_nozzle_iris.scad            — Rev R1 8-petal iris nozzle, full-circle M=1.0 72T ring gear (carried fwd from Rev O; idler-gear rework 2026-06-22)
nacelle_nozzle_idler.scad           — Rev R1 compound idler gear (44T/15T), Crown-Pinion-to-ring-gear stage (NEW 2026-06-22)
nacelle_bevel_housing.scad          — Rev R bevel-gear housing (carried fwd from Rev O)
nacelle_bevel_pair.scad             — Rev R M=1.0 14T 45° bevel pair (carried fwd from Rev O)
nacelle_pinion.scad                 — Rev R M=1.0 12T pinion (carried fwd from Rev O)
nacelle_sector_gear.scad            — Rev R1 M=1.0 58T sector gear, -5°/140° range (carried fwd from Rev O; grown from 38T 2026-06-22)
nacelle_servo_bracket.scad          — Rev R DS3218MG tilt servo bracket with M3 bosses
```

#### airframe/openscad/wings/

```text
wings_s1223_revo.scad             — Rev R S1223 high-lift wing pair (carried fwd from Rev O)
                                        RENDER_SIDE=+1 port, -1 stbd, 0 both
wing_nacelle_pylon_revo.scad      — Rev R nacelle tilt pylon (carried fwd from Rev O)
```

### airframe/diagrams/

Reference diagrams and machine-readable profiles generated from hull analysis.

```text
ring_frames/
ring_cargo_Y30_inner.csv    — Inner cross-section boundary at hull Y=+30 mm (9 paths, 4314 vertices); input for CF ring DXF
ring_rear_Y290_inner.csv    — Inner cross-section boundary at hull Y=+290 mm (14 paths, 2813 vertices); input for CF ring DXF
```

### airframe/stls/

Compiled and repaired STLs ready for slicing.

#### airframe/stls/fuselage/

```text
head_shell24.stl                — Head section (solid, for SCAD import ref)
head_shell24_2mm_repaired.stl   — Head section 2mm hollow, manifold
middle_canonical_shell24.stl    — Middle section
middle_shell24_2mm_repaired.stl — Middle section 2mm hollow, manifold
rear_shell24_2mm_repaired.stl   — Rear section 2mm hollow, manifold
battery_tray.stl                — 6S LiPo battery tray (part-local, VERIFY placement)
belly_panel.stl                 — Battery-bay belly access panel (part-local, VERIFY)
inara_access_cover.stl          — Inara Faraday-bay dorsal cover (cargo, GPS_PORT Ø38 clearance; access_panels_24in.scad Rev R2)
river_access_cover.stl          — River Faraday-bay dorsal cover (cargo, GPS_STBD Ø38 clearance; access_panels_24in.scad Rev R2)
head_cargo_splice_collar.stl    — Internal head/cargo joint splice collar (hull-frame, Rev R1, ~13g)
generate_head_cargo_splice_collar.py — Splice-collar generator (hull frame, from head inner contour)
cargo_middle_splice_collar.stl  — Internal cargo/middle joint splice collar (hull-frame, Rev R1, ~17g)
generate_cargo_middle_splice_collar.py — Splice-collar generator (hull frame, from middle inner contour)
middle_rear_splice_collar.stl   — Internal middle/rear joint splice collar (hull-frame, Rev R1, ~16g)
generate_middle_rear_splice_collar.py — Splice-collar generator (hull frame, from middle inner contour)
landing-gear/
legs_scaled24.stl             — Original Thingiverse landing legs × 4 (24" scale, cosmetic reference)
leg_1_scaled24.stl            — Individual leg 1 (Thingiverse reference)
leg_2_scaled24.stl            — Individual leg 2 (Thingiverse reference)
leg_3_scaled24.stl            — Individual leg 3 (Thingiverse reference)
leg_4_scaled24.stl            — Individual leg 4 (Thingiverse reference)
feet_x_4_scaled24.stl         — Landing feet × 4 (Thingiverse reference, TPU 95A)
foot_1_scaled24.stl           — Individual foot 1 (Thingiverse reference)
foot_2_scaled24.stl           — Individual foot 2 (Thingiverse reference)
foot_3_scaled24.stl           — Individual foot 3 (Thingiverse reference)
foot_4_scaled24.stl           — Individual foot 4 (Thingiverse reference)
landing_legs_hull_r1.stl      — ORPHANED: rendered from a pre-R1.4 single-leg design (PART="hull_legs") that
                                    no longer exists in landing_leg_assy.scad; superseded by the Rev R1.4 corner
                                    V-brace frame below.  Re-render or delete (TODO.md LG-04/LG-09).
[arm_upper_r1.stl]            — PENDING: Rev R1.4 upper corner V-arm CF-PETG (PART="arm_upper"; 4 per aircraft; struts ≈77.6 mm)
[arm_lower_r1.stl]            — PENDING: Rev R1.4 lower corner V-arm CF-PETG (PART="arm_lower"; 4 per aircraft; struts ≈53.9 mm)
[main_strut_r1.stl]           — PENDING: Rev R1.4 main vertical strut CF-PETG OD18 mm × 143 mm (PART="main_strut"; 4 per aircraft)
[junct_node_r1.stl]           — PENDING: Rev R1.4 arm-to-strut junction node PETG crush zone R9 mm (PART="node"; 8 per aircraft)
[hull_boss_r1.stl]            — PENDING: Rev R1.4 generic hull boss cylinder CF-PETG OD22 mm (PART="boss"; 16 per aircraft; 4 per corner)
[foot_pad_r1.stl]             — PENDING: Rev R1.4 TPU 95A foot pad 55×55×12 mm (PART="foot"; 4 per aircraft)
dorsal_antenna_fin.stl            — Dorsal antenna fin fairing
middle_canonical_edf_intake.stl — Middle section EDF intake opening
cargo/
cargo_sect_shell24_2mm_repaired.stl    — Cargo section 2mm hollow, manifold
cargo_sect_shell24_repaired.stl        — Cargo solid shell, manifold-repaired (used for intersection in access_panels_24in.scad)
cargo_door_port.stl                   — Port clamshell cargo door, hinges outboard at X≈-117.6mm (hull-frame, Rev R1b 2026-06-22)
cargo_door_stbd.stl                   — Stbd clamshell cargo door, hinges outboard at X≈-222.5mm (hull-frame, Rev R1b 2026-06-22)
generate_cargo_doors.py               — Door STL generator (Rev R1b, hull frame; see CLAUDE.md)
cargo_hinge_retention.stl             — Shell-side hinge-pin retention blocks (4: 2/door; hull-frame, Rev R1c 2026-06-29)
generate_cargo_hinge_retention.py     — Retention-block generator (Rev R1c, hull frame; merged into cargo shell)
cargo_cradle_autolatch.stl            — Auto-latch payload cradle
cargo_fpv_bezel.stl                   — FPV camera bezel
cargo_gps_retention_ring.stl          — GPS antenna retention ring
cargo_winch_motor_mount.stl           — N20 winch motor mount
cargo_winch_spool.stl                 — Winch spool
cargo_drv8833_tray.stl                — DRV8833 H-bridge PCB tray
cargo_door_servo_bracket.stl          — Door servo bracket
cargo_release_servo_bracket.stl       — Payload release servo bracket
generate_cargo_mounts.py              — Mount STL generation script
```

#### airframe/stls/nacelles/

```text
edf_aft_spider_sleeve.stl         — Aft spider/motor-mount sleeve (compiled from
                                    nacelles/edf_aft_spider_sleeve.scad)
edf_stator_sleeve.stl             — 11-fin inter-stage stator sleeve (compiled from
                                    nacelles/edf_stator_sleeve.scad)
eng_left_shell24_50mm_repaired.stl  — Port nacelle EDF engine shell, 50 mm, manifold-repaired;
                                    required by tools/bake_hull_frame.py,
                                    airframe/FreeCAD-scripts/serenity_assembly.py, and the
                                    FreeCAD-scripts Makefile (do not archive)
eng_right_shell24_50mm_repaired.stl — Stbd nacelle EDF engine shell, 50 mm, manifold-repaired;
                                    same active-pipeline dependency as eng_left_* (do not archive)
nacelle_bevel_housing.stl         — Bevel gear housing (also duplicated under nozzles/, see below)
nacelle_bevel_pair.stl            — 14T 45° bevel pair (also duplicated under nozzles/, see below)
nacelle_pinion.stl                — M=1.0 12T pinion
nacelle_port_revs.stl             — Port nacelle pod shell, Rev S (renamed from _revq 2026-07-04;
                                    Rev S1 nozzle/nav/intake mods baked in); required by
                                    tools/bake_hull_frame.py, serenity_assembly.py, and the
                                    FreeCAD-scripts Makefile (active, do not archive)
nacelle_sector_gear.stl           — M=1.0 58T sector gear, -5°/140° range; re-rendered
                                    2026-06-22, see §1.1.3.2
nacelle_stbd_revs.stl             — Stbd nacelle pod shell, Rev S (renamed from _revq 2026-07-04);
                                    same active-pipeline dependency as nacelle_port_revs.stl (do not archive)
nozzles/
nacelle_bevel_housing.stl       — Bevel gear housing
nacelle_bevel_pair.stl          — 14T 45° bevel pair
nacelle_nozzle_iris.stl         — Combined assembly-preview render (housing + ring + 8
                                    petals, closed position) of the Rev R1 full-circle
                                    ring gear + idler-gear stage; re-rendered 2026-06-22,
                                    see TODO.md §1.1.3.1
nacelle_nozzle_idler.stl        — Compound idler gear (44T/15T), Crown-Pinion-to-ring
                                    stage; rendered 2026-06-22, see TODO.md §1.1.3.1
nacelle_nozzle_idler_bracket.stl — Two-boss bracket for the idler gear above; rendered
                                    2026-06-22, see TODO.md §1.1.3.1
nacelle_nozzle_throat.stl       — Rev R2 fixed throat liner + housing (RENDER_PART="throat"
                                    of nacelle_nozzle_iris.scad); print part, 2026-07-04
nacelle_nozzle_ring.stl         — Rev R2 unison ring gear (72T + spiral cams,
                                    RENDER_PART="ring"); print part, re-rendered 2026-07-04
nacelle_nozzle_flap.stl         — Rev R2 overlapping tangential-hinge conical flap
                                    (RENDER_PART="flap", print × 8); NEW 2026-07-04,
                                    supersedes nacelle_nozzle_petal.stl (archived), see
                                    TODO.md §1.1.3.1 [REF-CAD-001]
nacelle_nozzle_closed_asm.stl   — Iris assembly (closed position, visual; legacy blender)
```

#### airframe/stls/wings/

```text
wing_port_s1223_revo.stl        — Port wing (RENDER_SIDE=+1)
wing_stbd_s1223_revo.stl        — Stbd wing (RENDER_SIDE=-1)
wing_nacelle_pylon_revo.stl     — Nacelle tilt pylon (one per side)
```

### airframe/placeholders/

Dimensionally-accurate bounding-geometry STL placeholder files for all non-printable
Rev R BOM components.  Used for FreeCAD assembly exploded views and build guides.
Generated by `generate_placeholders.py` (pure Python, stdlib only).
STL header marker: `SerenityUAV PLACEHOLDER R1`.
FreeCAD catalog: `airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`.

```text
generate_placeholders.py          — Standalone generator (python3, no dependencies)
propulsion/
EDF_50mm_6S.stl                 — 50 mm 6S EDF (BOM: EDF-50-6S, ×4)
EDF_120mm_6S_deferred.stl       — [STALE NAME] 120 mm 6S rear EDF placeholder; on-disk filename
                                    still reflects the pre-Rev-R1 120 mm rear EDF (superseded
                                    spec is 55 mm, see CLAUDE.md); pending regeneration to
                                    EDF_55mm_6S_deferred.stl for Phase 11
ESC_40A_6S_BLHeli32.stl         — 40 A BLHeli32 ESC (BOM: ESC-40A-6S, ×4)
ESC_80A_6S_BLHeli32_deferred.stl — [STALE NAME] 80 A ESC placeholder; on-disk filename still
                                    reflects the pre-Rev-R1 120 mm EDF's ESC sizing; pending
                                    regeneration to ESC_50A_6S_BLHeli32_deferred.stl for Phase 11
servos/
DS3218MG_25kgcm.stl             — DS3218MG servo (BOM: SERVO-TILT, MAL-GIMBAL-SERVO)
SG90_micro.stl                  — SG90 micro servo (BOM: SERVO-CARGO, SERVO-RCS-VALVE)
bearings/
MF104ZZ_4x10x4mm.stl            — MF104ZZ flanged bearing (BOM: BRG-MF104ZZ, ×4)
MR63ZZ_3x6x2p5mm.stl            — MR63ZZ miniature bearing (BOM: BRG-MR63ZZ, ×8)
B6804_20x32x7mm_GCS.stl         — 6804-2RS thin bearing (BOM: MAL-BRG-6804, ×1 GCS)
structural/
CF_rod_4mm_300mm_stock.stl      — 4 mm solid CF rod (BOM: CF-ROD-4MM)
CF_rod_3mm_300mm_stock.stl      — 3 mm CF gear shaft rod (BOM: SHAFT-CF-3MM)
CF_tube_12mm_OD_1p5w_350mm_spar.stl — 12 mm OD CF wing spar (BOM: CF-TUBE-12MM)
CF_bar_6x3mm_620mm_keel.stl     — 6×3 mm CF keel bar (BOM: CF-BAR-6X3)
CF_plate_2mm_200x300mm.stl      — 2 mm CF sheet (BOM: CF-PLATE-2MM)
PTFE_sleeve_4mm_OD_3mm_ID_52mm.stl — PTFE gear shaft sleeve (BOM: PTFE-SLEEVE-4MM)
avionics/
PocketBeagle2_Industrial_56x35mm.stl — PB2-I SBC (BOM: PB2-I-FC/CN/MAL-PB2-I)
Cape_A2_PCB_55x35mm.stl         — Wash FC cape 55×35mm (BOM: CAPE-A-2)
Cape_B2_PCB_55x35mm.stl         — Zoë Comms cape 55×35mm (BOM: CAPE-B-2, MAL-CAPE-B-2)
XCVR_49MHZ2_PCB_55x35mm.stl     — 49 MHz sub-module (BOM: Emma, MAL-Emma)
Kaylee_PDB_90x65mm.stl          — Power distribution board (BOM: Kaylee)
microSD_64GB.stl                — 64 GB microSD log card (BOM: MICROSD-LOG)
power/
LiPo_6S_4000mAh_138x44x36mm.stl — Primary flight battery (BOM: BATT-6S-4000)
LiPo_6S_2800mAh_115x35x35mm.stl — Cargo battery (BOM: BATT-6S-2800)
LiPo_4S_10000mAh_175x64x38mm_GCS.stl — GCS field battery (BOM: MAL-FIELD-BATTERY)
Fuse_MAXI_150A.stl              — 150 A MAXI blade fuse (BOM: FUSE-MAIN-150A)
Fuse_mini_40A.stl               — 40 A mini blade fuse (BOM: FUSE-ESC-40A)
Shunt_CSS2H_2512K_1mohm.stl     — 1 mΩ Kelvin shunt 2512 SMD (BOM: SHUNT-1MOHM)
cargo/
N20_motor_300RPM_6V.stl         — N20 winch motor (BOM: N20-WINCH)
HX711_loadcell_ADC_breakout.stl — HX711 load-cell ADC (BOM: HX711-LC)
DRV8833_Hbridge_breakout.stl    — DRV8833 H-bridge driver (BOM: DRV8833-CARGO)
Dyneema_SK75_0p5mm_coil.stl     — Dyneema SK75 line coil (BOM: DYNEEMA-SK75)
gears/
Sector_gear_M1_R22mm.stl        — M=1.0 sector gear R=22 mm (BOM: SECTOR-M1-R22)
Pinion_M1_12T_R6mm.stl          — M=1.0 12T pinion/crown (BOM: PINION-A-M1-12T, CROWN-M1-12T)
Bevel_M1_14T_pair.stl           — M=1.0 bevel pair N=14T (BOM: BEVEL-M1-14T)
Bevel_housing_CF_PETG.stl       — Bevel gear housing 24×14×20 mm (BOM: BEVEL-HOUSING)
hardware/
Pin_SS_3x5mm_hinge.stl          — SS roll pin 3×5 mm (BOM: PIN-3X5)
Insert_M25_brass_L5.stl         — M2.5 brass heat-set insert (BOM: INSERT-M25-BRASS)
Insert_M3_brass_L5.stl          — M3 brass heat-set insert (BOM: INSERT-M3-WING)
Screw_M3x8mm_button_ISO7380.stl — M3×8 button-head screw (BOM: SCREW-M3-8-BTN)
Batt_strap_silicone_16mm_CAM.stl — 16 mm silicone cam-buckle strap (BOM: BATT-STRAP-CAM)
lighting/
WS2812C_2020_SMD.stl            — WS2812C-2020 SMD nav light (BOM: LED-WS2812C-NAC)
wiring/
PTFE_conduit_4mm_OD_3mm_ID_700mm.stl — PTFE data bus conduit 700 mm (BOM: CONDUIT-PTFE)
Wire_4AWG_silicone_200mm_pair.stl — 4 AWG main battery wires (BOM: WIRE-4AWG)
Wire_10AWG_silicone_400mm.stl   — 10 AWG ESC branch wires (BOM: WIRE-10AWG)
Wire_28AWG_STP_bundle_500mm.stl — 28 AWG shielded signal leads (BOM: WIRE-28AWG-STP)
Wire_49MHz_antenna_0p3mm_470mm.stl — 49 MHz dorsal antenna wire (BOM: WIRE-49MHZ)
Post_49MHz_base_load_coil.stl   — 49 MHz wire post + coil (BOM: POST-FWD-49, POST-AFT-49)
gcs/
Malcolm_enclosure_IP65_145x90x65mm.stl — Hammond IP65 Al enclosure (BOM: MAL-ENCLOSURE)
Pololu_D24V50F5_5V5A_BEC.stl    — 5 V/5 A BEC (BOM: MAL-PWR-5V-BEC)
Pololu_D24V22F6_6V2A_BEC.stl    — 6 V/2.2 A BEC (BOM: MAL-PWR-6V-BEC)
Antenna_915MHz_omni_5dBi.stl    — 915 MHz rubber duck (BOM: MAL-ANT-915-OMNI)
Antenna_915MHz_Yagi_9dBi.stl    — 915 MHz Yagi (BOM: MAL-ANT-915-YAGI)
Antenna_5GHz_panel_14dBi.stl    — 5 GHz flat panel (BOM: MAL-ANT-WIFI-PNL)
Antenna_49MHz_whip_940mm.stl    — 49 MHz whip + radials (BOM: MAL-ANT-49MHZ)
Antenna_2p4GHz_zigbee_rubber_duck.stl — 2.4 GHz Zigbee antenna (BOM: MAL-ANT-ZIGBEE)
Antenna_GNSS_patch_ANN_MB00.stl — GNSS patch u-blox ANN-MB-00 (BOM: MAL-ANT-GPS)
GPS_module_M10Q_SparkFun.stl    — u-blox M10Q GNSS breakout (BOM: MAL-GPS-MODULE)
RF_splitter_915MHz_2way_ZFSC.stl — Mini-Circuits 915 MHz splitter (BOM: MAL-RF-SPLITTER)
AS5600_encoder_breakout_15x15mm.stl — AS5600 encoder PCB (BOM: MAL-GIMBAL-ENC)
N42_disc_magnet_6x2mm.stl       — N42 encoder rotor magnet (BOM: MAL-GIMBAL-MAG)
TCA9548A_I2C_mux_breakout.stl   — TCA9548A I²C mux (BOM: MAL-TCA9548A)
B6804_20x32x7mm_gimbal_pan.stl  — 6804-2RS bearing (BOM: MAL-BRG-6804, duplicate for GCS)
Malcolm_tripod_antenna_mast.stl — Tripod/mast ≥1.5 m (BOM: MAL-TRIPOD)
foam/
Foam_fill_head_125x231x136mm.stl      — Head section foam fill block (BOM: FOAM-FILL-HEAD)
Foam_fill_cargo_190x200x159mm.stl     — Cargo section foam fill block (BOM: FOAM-FILL-CARGO)
Foam_fill_middle_horseshoe_173x69x161mm.stl — Middle horseshoe U-frame fill (BOM: FOAM-FILL-MIDDLE)
Foam_fill_rear_136x177x154mm.stl      — Rear section foam fill block (BOM: FOAM-FILL-REAR)
Void_avionics_bay_62x42x75mm.stl      — Avionics bay void (×4: Shepherd/Inara/River/Simon)
Void_cargo_bay_120x150x80mm.stl       — Cargo bay belly void (BOM: VOID-CARGO-BAY)
Void_wiring_trunk_30x700x20mm.stl     — Dorsal wiring trunk void (BOM: VOID-WIRE-TRUNK)
Void_power_bus_25x500x25mm.stl        — Belly power bus void (BOM: VOID-POWER-BUS)
Void_vent_intake_20x250x20mm.stl      — Ventilation intake duct void (BOM: VOID-VENT-INTAKE)
Void_vent_exhaust_20x300x20mm.stl     — Ventilation exhaust duct void (BOM: VOID-VENT-EXHAUST)
Void_nacelle_pylon_20x80x20mm.stl     — Nacelle pylon foam pocket (×2, BOM: VOID-NACELLE-PYLON)
Void_far_cage_76x56x88mm.stl          — Faraday cage foam pocket 76×56×88 mm (BOM: VOID-FAR-CAGE)
Void_far_fan_spur_44x44x50mm.stl      — Cage vent duct spur 44×44×50 mm (BOM: VOID-FAR-FAN-SPUR)
faraday/
Far_cage_AV_70x50x82mm.stl            — Avionics bay Faraday cage 70×50×82 mm (BOM: FAR-CAGE-AV)
Far_gasket_AV_250x6x1mm.stl           — EMI spring-contact lid gasket strip (BOM: FAR-GASKET-AV)
Far_fan_40mm_5V.stl                   — 40 mm 5 V axial fan (BOM: FAR-FAN-40)
Far_EMI_vent_40x40x6mm.stl            — Al honeycomb EMI vent panel 40×40×6 mm (BOM: FAR-EMI-VENT-40)
Far_bond_strap_100mm.stl              — Tinned-Cu bonding strap 100 mm (BOM: FAR-BOND-STRAP)
Far_FT_panel_55x35mm.stl              — EMI-filtered feed-through panel 55×35 mm (BOM: FAR-FT-PANEL)
Far_ferrite_4mm_ID.stl                — Split ferrite clamp 4 mm bore (BOM: FAR-FERRITE-4MM)
Mal_far_fan_40mm_5V.stl               — Malcolm enclosure fan (BOM: MAL-FAR-FAN)
Mal_far_gasket_470x8x1p5mm.stl        — Malcolm Hammond lid EMI gasket (BOM: MAL-FAR-GASKET)
```

### airframe/FreeCAD-scripts/ (updated Rev R1 + placeholders)

```text
serenity_assembly.py              — Full hull-frame airframe assembly (Rev R1)
serenity_placeholders_assembly.py — 87-component placeholder catalog (8-col grid,
                                    run with freecadcmd; output Serenity-Placeholders.FCStd)
faraday-enclosure.py              — Faraday-cage avionics enclosure generator
make_flat_pattern.py              — Sheet-metal/flat-pattern unfold utility
Makefile                          — Build rules
```

(Deprecated prototypes assembly1.py, Serenity-Assemble.py,
Serenity-Subsystem-Assembly.py, serenity_subsystem_assembler.py, and
serenity_fuselage_asm4.py archived 2026-06-29 — see ARCHIVE_INDEX.md.)

### airframe/ (root-level files)

```text
[Serenity-Assembled.FCStd]        — [PENDING] FreeCAD full-airframe assembly; not yet generated
                                    on disk. See airframe/freecad/assembly/ for in-progress
                                    working files and serenity_assembly.py for the headless
                                    generation script.
```

---

## avionics/

KiCad PCB schematics and layouts, electronics design, firmware, and communications stack.

```text
TODO.md                           — Avionics WBS view — PCBs §1.2*/§1.4/§0.6, node firmware §4.1–4.4/§4.6
CLAUDE.md                         — Avionics design standards (cape naming, KiCad DRC
                                    workflow, security/cryptography, communications
                                    protocols, external radio regulations, avionics
                                    architecture)
```

### avionics/firmware/

CMake-based firmware for PocketBeagle 2 Industrial (AM6254) nodes.

```text
CMakeLists.txt                    — Top-level build
README.md                         — Firmware build guide
common/
CMakeLists.txt
include/
    ax25_types.h                  — AX.25 frame types
    kiss_types.h                  — KISS framing types
    sbus_input.h                  — SBUS input driver API
src/
    sbus_input.c                  — SBUS input driver
dts/
Makefile                        — DTS compile rules
README.md
cape-a/
    k3-am6254-pocketbeagle2-serenity-cape-a2.dts   — Wash cape-a2 device tree
cape-b/
    k3-am6254-pocketbeagle2-serenity-cape-b2.dts   — Zoë cape-b2 device tree
fc/
CMakeLists.txt
src/
    main.c                        — Flight control node main
    bmon_ina2xx.c/h               — INA2xx battery monitor driver
    cell_mon_bq769x0.c/h          — BQ769x0 cell monitor driver
    governor_config.h             — EDF governor config
    mag_mmc5983ma.c/h             — MMC5983MA magnetometer driver
    mag_qmc5883l.c/h              — QMC5883L magnetometer driver
    pwr_fault.c/h                 — Power fault detection
tools/
    governor_cal.py               — EDF governor calibration tool
    requirements.txt
    .gitignore                    — VCS ignore rules for calibration tool output
cn/
CMakeLists.txt
src/
    main.c                        — Comms node main
    si5351.c/h                    — Si5351 clock gen driver
    xcvr_kiss.c/h                 — 49MHz XCVR KISS framing
```

### avionics/kicad/

KiCad 7/9 PCB design files.  All active designs are Rev R (EMI-hardened -2 variants).

```text
README.md                         — KiCad directory overview, generation workflow, DRC notes
.gitignore                        — VCS ignore rules for KiCad backups/autosave/fp-info-cache

Wash — Flight Control & Sensor Cape (Cape-A-2):
Wash.kicad_pro                  — KiCad project file
Wash.kicad_sch                  — Schematic
Wash.kicad_pcb                  — PCB layout
Wash.kicad_prl                  — Layout rules
Wash.md                         — Design specification
[generated by gen_cape_a2.py + gen_cape_a2_pcb.py]

Zoë — Comms/Logging/Payload Cape (Cape-B-2):
Zoë.kicad_pro                   — KiCad project file
Zoë.kicad_sch                   — Schematic
Zoë.kicad_pcb                   — PCB layout
Zoë.kicad_prl                   — Layout rules
Zoë.md                          — Design specification
[generated by gen_cape_b2.py + gen_cape_b2_pcb.py]

Kaylee — Power Distribution Board (PDB):
Kaylee.kicad_pro                — KiCad project file (Rev A, 2026-06-10)
Kaylee.kicad_sch                — Schematic (Rev A, 90×65 mm 4-layer)
Kaylee.kicad_pcb                — PCB outline + stackup (Rev A)
Kaylee.kicad_prl                — Layout rules
Kaylee.md                       — Design specification
gen_kaylee.py                   — Python generator script (all 3 KiCad files)

Vera — Nose/Cargo-Bay Vision, ToF & Laser Board (STANDALONE, not a PB2-I cape):
Vera.kicad_pro                  — KiCad project file (design exploration, 2026-07-03)
Vera.kicad_sch                  — Schematic (net-correct, EMI-hardened; U1/U2/U3/U5/U_PMIC
                                   use placeholder pin numbers/footprints, see gen_vera.py)
Vera.kicad_pcb                  — PCB layout (1.0 × 2.75 in (25.4 × 69.85 mm), double-sided F.Cu+B.Cu, 4-layer,
                                   rounded corners, EMI-hardened; manually compacted in KiCad
                                   GUI past gen_vera_pcb.py's 78x80mm script output — footprint
                                   placement only, traces not routed)
Vera.md                         — Design specification, BOM, EMI-hardening status (matches
                                   Wash/Zoe Rev R baseline)
gen_vera.py                     — Python generator script (kicad_pro + kicad_sch)
gen_vera_pcb.py                 — Python generator script (kicad_pcb, 78x80mm layout; NOT in
                                   sync with the hand-compacted 1.0 × 2.75 in (25.4 × 69.85 mm) Vera.kicad_pcb —
                                   re-running it overwrites the compaction, see Vera.md)
[see TODO.md §1.2c and avionics/CLAUDE.md "Vera" for full status/open items]

Emma (49 MHz transceiver sub-module):
Emma.kicad_pro
Emma.kicad_sch
Emma.kicad_pcb
Emma.kicad_prl
Emma.md
[generated by complete_xcvr_49mhz2.py]

ENC-NACELLE-1 (nacelle encoder breakout):
ENC-NACELLE-1.kicad_sch
ENC-NACELLE-1.md

Python generation scripts:
gen_kaylee.py                   — Kaylee PDB generator (pro + sch + pcb)
gen_kaylee_pcb.py               — Kaylee PDB PCB layout generator (standalone)
gen_cape_a2.py                  — Schematic generator (Cape-A-2)
gen_cape_a2_pcb.py              — PCB layout generator (Cape-A-2)
gen_cape_b2.py                  — Schematic generator (Cape-B-2)
gen_cape_b2_pcb.py              — PCB layout generator (Cape-B-2)
complete_xcvr_49mhz2.py         — Emma completion script
gen_emma_sch.py                 — Emma schematic-first generator (authors Emma.kicad_sch from the as-placed PCB; 2026-07-04 reconciliation)
mod_emma_pcb.py                 — Emma PCB transform (pcbnew: drop J1, UART→PB2 rails, PTT_N/RSSI_DCD reassign, add RSSI comparator; 2026-07-04)
route_emma_rssi.py               — Emma RSSI sub-circuit router (pcbnew: GND/REF/+3V3/RSSI_ANA traces + vias; 2026-07-05)
cleanup_emma_drc.py             — Emma DRC debt cleanup (pcbnew: mask expansion 0.1→0.05mm, delete redundant close GND tracks; 2026-07-04)
add_eth_phy.py                  — Ethernet PHY addition script
add_sensors_sbus.py             — SBUS sensor addition script
apply_netlist.py                — Netlist application script
fix_xcvr_labels.py              — XCVR net label fix script
replace_footprints.py           — Footprint replacement utility for KiCad PCBs
check_impedance.py              — Impedance checker
generate_gerbers.py             — Gerber export script
Serenity-Custom.pretty/         — Custom KiCad component footprint library
drc_report.txt                  — Latest KiCad DRC report (Wash/Zoë/XCVR)
xcrv-DRC.rpt                    — Emma DRC report

gerbers/
CAPE-A-1/                       — Cape-A-1 gerbers (ARCHIVED design)
CAPE-B-1/                       — Cape-B-1 gerbers (ARCHIVED design)
Wash/                           — Wash (Cape-A-2) gerbers
Zoë/                            — Zoë (Cape-B-2) gerbers
XCVR-49MHZ-2/                   — Emma gerbers
Kaylee/                         — Kaylee PDB gerbers (Rev A, 2026-06-10)
```

### avionics/gerbers/

```text
archive/                          — Pre-Rev Q gerber snapshots
```

---

## docs/

Project documentation, design specifications, analysis reports, and standards references.

```text
TODO.md                           — Docs/standards/regulatory WBS view — §0.x, §1.5–1.7, §5.x, §6.x
FIRST_FLIGHT_READINESS.md         — Open-item rollup on the Phase-5 first-flight critical path
CLAUDE.md                         — Documentation standards (standards vetting policy,
                                    references management, measurements and units,
                                    version control, traceability matrix)
PROJECT_INDEX.md                  — This file: active project directory tree
structural_analysis.md            — First-principles structural analysis (Rev R1, 2026-06-14): keel, ring frames, joint bosses, skid rods, AUW, FOS calculations
AVIONICS_PB2_REDESIGN.md          — 8× PocketBeagle 2 Industrial avionics redesign spec (Rev R)
BATTERY_MOUNT.md                  — Battery CG analysis, retention load case, belly panel spec (Rev R)
LANDING_GEAR_ANALYSIS.md          — Landing gear structural analysis: 6 ft drop, fuse sizing, lateral loads (Rev R1)
NOZZLE_DRIVE_TRADE.md             — Nozzle-drive redesign trade study: internal ring gear (A) vs pushrod linkage (B) to kill the protruding idler (Rev R1a)
img/nozzle_drive_trade.png        — Nozzle-drive trade schematics + tilt→ring-angle curves (A vs B)
img/wing_rev_r1a_sections.png     — Wing Rev R1a root/tip sections: camber-centred spar + EDF cableway
POWER_DISTRIBUTION.md             — Power architecture: Kaylee PDB rails, fuse map, cable spec (Rev R; §3.2.1 Vera 5V rail added 2026-07-05)
VERA_LASER_ANALYSIS.md            — Vera laser: single 520nm green source feasibility, power/class vs spread-angle split, lens/DOE options (Rev A)
REVN_BUILD_GUIDE_24IN.md          — Revision N+ 24-inch hull build guide (active, Rev R baseline)
PHASED_BUILD_GUIDE.md             — Rev M 18-inch phased build guide (SUPERSEDED for 24-inch builds)
PROTO_PRINT_DAVINCI_JR.md         — DaVinci Jr. PLA prototype print guide (Rev P, historical)
README.md                         — Rev M 18-inch project overview (SUPERSEDED; active README.md at root)
bom_revR.json                     — Bill of materials (Rev R, JSON — active baseline)
bom_revQ.json                     — Bill of materials (Rev Q, JSON — historical reference)
bom_revP.json                     — Bill of materials (Rev P, JSON — historical reference)
MANIFEST.json                     — Rev F manifest (stale — historical reference only)
references/
Thing-4677565-Serenity.stl      — Low-detail Thingiverse reference hull (geometry guide)
```

---

## current-specification/

Active design specifications, requirements, and version-controlled design baselines.

```text
TODO.md                           — Specification-sync WBS (reference index into master §1.6/§1.7/§6.3)
CLAUDE.md                         — Specification standards (revision policy, document
                                    structure, standards citations, traceability matrix,
                                    specification approval workflow)
serenity-rev-r.jsx                — Rev R interactive specification (SUPERSEDED by Rev S per
                                    TODO.md §6.3; a serenity-rev-s.jsx complete non-delta
                                    replacement has not yet been authored — flagged open item)
bom_revS.csv                      — Bill of materials (Rev S, CSV flat table — active baseline;
                                    supersedes bom_revR.csv, archived 2026-07-04)
LICENSE_AND_ATTRIBUTION.md        — Attribution chain for all upstream sources
```

> Note: `serenity-rev-q.jsx` and `bom_revQ.csv` are NOT present in this directory; the Rev Q
> historical references live in `archives/` (`archives/serenity-rev-q.jsx`,
> `archives/bom_revQ.csv`, `archives/docs-superseded/bom_revQ.csv`,
> `archives/docs-superseded/serenity-rev-q.jsx`). See ARCHIVE_INDEX.md.

---

## gcs/

Ground control station and mission planning software. Malcolm ("CAPT Reynolds") is the
ArduPilot-compatible GCS for Serenity UAV.  Architecture: 1× PocketBeagle 2 Industrial +
Cape-B-2 (Zoë) + Emma, USB CDC-ECM tethered to a host Debian Linux PC running QGroundControl.
Five radio links: SiK 915 MHz, LoRa 915 MHz, Wi-Fi 5 GHz, 49 MHz Part 15 §15.235 (AX.25),
Zigbee 2.4 GHz.  Servo-driven two-axis antenna gimbal with AS5600 magnetic encoders.
No external PAs (FCC-compliant with directional antennas).  IP65 field enclosure.

```text
TODO.md                           — Malcolm GCS WBS view — master §4.5 (ground control, gimbal, comms)
CLAUDE.md                         — GCS design standards (operator interface, command
                                    authentication, telemetry display, communications
                                    protocols, security/compliance, hardware requirements)
gcs/malcolm/
README.md                                — Malcolm GCS overview, architecture table, radio link
                                            table, directory layout, build/setup steps, security notes
hardware/
    docs/
        malcolm_antenna_spec.md              — FCC EIRP compliance analysis for all 5 radio links;
                                            gain tables; no-PA conclusion; WiFi Tx power reduction
        malcolm_power_budget.md              — 5V and 6V rail budgets; field battery endurance calcs
        malcolm_wiring.md                    — Connector/cable spec: USB CDC-ECM, servo harness,
                                            encoder I²C, RF SMA, power rails, enclosure glands
    enclosure/
        openscad/
        malcolm_field_enclosure.scad       — IP65 two-part body+lid enclosure for PB2-I+Cape-B-2;
                                            110×80×55mm interior; EPDM gasket groove; 40mm fan
                                            cutout; cable gland locations; RENDER_MODE 0/1/2
    gimbal/
        openscad/
        malcolm_gimbal_pan.scad            — Pan stage: 6804 bearing (20×32×7mm), DS3218MG servo,
                                            sector gear, 120×100×12mm base plate with M6 tripod
                                            holes, 80mm OD turret; RENDER_MODE 0/1/2
        malcolm_gimbal_tilt.scad           — Tilt stage: MF104ZZ bearings, DS3218MG servo, yoke
                                            100mm wide, tilt range -10° to +90°
        malcolm_gimbal_mount.scad          — Antenna plate 80×200×6mm CF-PETG; flanged pivot hubs
                                            with MF104ZZ bore; encoder magnet pocket 6.1mm dia;
                                            U-bolt clamps for 15mm Yagi boom; WiFi panel M4 holes
firmware/
    pb2i/
        CMakeLists.txt                       — cmake C11 build; mal_gimbal executable; mal_telemetry
                                            static lib; strict security flags; MAVLINK_INCLUDE_DIR
        dts/
        k3-am6254-pocketbeagle2-malcolm-cape-b2.dts
                                            — Device tree overlay: EHRPWM0 pan/tilt gimbal servos,
                                            I²C2 TCA9548A+AS5600 encoders, UART2 SiK, UART5 49 MHz
        src/
        mal_config.h                       — All compile-time constants: MAVLink sysids, UDP ports,
                                            UART paths, LoRa SPI, WiFi tx_power_mbm, gimbal limits,
                                            AS5600 register map, TPM key handle, heartbeat timeout
        mal_gimbal.h                       — Gimbal API: init, set_target, update, get_position,
                                            is_on_target; types mal_gimbal_pos_t, mal_gimbal_err_t
        mal_gimbal.c                       — Gimbal implementation: sysfs PWM, TCA9548A mux select,
                                            AS5600 angle read (STATUS MD bit check), zero-calibration,
                                            rate-limited control, counts_to_deg, angle_to_duty_ns
        mal_telemetry.h                    — Telemetry API: init, feed, get_position, get_status,
                                            is_link_lost; types mal_aircraft_pos_t, mal_telemetry_status_t
        mal_telemetry.c                    — MAVLink2 parser (mavlink_parse_char); handles HEARTBEAT
                                            + GLOBAL_POSITION_INT; publishes JSON to UDP 127.0.0.1:14560
software/
    config/
        malcolm_config.yaml                  — YAML config: MAVLink source, tracker ports, gimbal_ctrl
                                            ports, PB2-I host, GNSS device, WiFi tx_power_mbm,
                                            49 MHz default channel
        mavlink_router.conf                  — mavlink-router config: pb2i_comms UDP 14551,
                                            qgc UDP 14550, tracking UDP 14552; serial fallback stubs
    install/
        install_deps.sh                      — apt-get system packages; pip3 tracking requirements;
                                            udev rule for u-blox GNSS (/dev/gnss_gcs)
        install_qgc.sh                       — Download QGC AppImage; USB serial udev rules; desktop entry
        install_mavlink_router.sh            — Clone+build mavlink-router; install config; systemd service
    tracking/
        requirements.txt                     — pymavlink≥2.4.41, PyYAML≥6.0.1, pyserial≥3.5, mypy
        src/
        telemetry_feed.py                  — pymavlink consumer: sysid=1 GLOBAL_POSITION_INT →
                                            publishes position JSON to UDP :14560
        tracker.py                         — Vincenty bearing + haversine range + Bennet 1982 refraction
                                            elevation; GNSS reader; publishes gimbal targets to UDP :14570
        gimbal_ctrl.py                     — Receives targets from tracker.py; software travel limits;
                                            rate limiting 90°/s; dead-band 0.2°; sends GIMBAL_TARGET
                                            JSON to PB2-I UDP :14571
        tests/
        test_tracker.py                    — 9 bearing/elevation unit tests: cardinal directions,
                                            NE quadrant, horizontal/above/overhead/airborne elevations,
                                            azimuth and elevation range assertions
```

---

## deferred/

Design work deferred beyond the current build phase (Phases 5–10). Includes planned upgrades
(Emma R1, Zoë R1, Kaylee A1) and Phase 11+ systems (rear EDF, RCS). Not archived — intended
for future build phases.

```text
TODO.md                           — Deferred-work WBS view — master Phase 11 (aft EDF + RCS)
CLAUDE.md                         — Deferred work standards (status categories, planned
                                    upgrades, Phase 11+ scope, design decision history,
                                    phase numbering convention)
```

### deferred/aft-edf/

```text
README.md                         — Aft fuselage EDF design scope, rationale, and defer decision
openscad/
aft_edf_plenum.scad           — Intake plenum manifold — [PRE-R1] still 120 mm geometry, pending
                                    regen to 55 mm EDF inlet + 4 RCS bleed taps
edf_120_motor_mount.scad      — [PRE-R1] 120 mm EDF motor mount ring; pending regen to
                                    edf_55_motor_mount.scad (still required by
                                    blender_edf_bore_and_petals.py / slice_all_batches.sh — do
                                    not archive until Rev R1 replacement exists)
edf_120_thrust_tube.scad      — [PRE-R1] 120 mm thrust tube; pending regen to
                                    edf_55_thrust_tube.scad (still required by active build
                                    pipeline files — do not archive until replaced)
neck_intake_frame.scad        — [PRE-R1] Reduced-area radial intake scoop frame; pending regen
                                    for 55 mm EDF
rear_neck_intake_shell24.scad — Rear neck intake shell integration shell
stls/
aft_edf_plenum.stl              — [PRE-R1] Compiled plenum STL, still 120 mm geometry
edf_120_motor_mount.stl         — [PRE-R1] Compiled motor mount STL
edf_120_thrust_tube.stl         — [PRE-R1] Compiled thrust tube STL
neck_intake_frame.stl           — Compiled intake frame STL
rear_shell24_2mm_edf_bored.stl  — Rear shell with EDF bore cut
rear_nozzle_closed_asm.stl      — [PRE-R1] Iris nozzle closed-position assembly (visual)
rear_nozzle_frame.stl           — [PRE-R1] Iris nozzle frame ring
rear_nozzle_petal.stl           — [PRE-R1] Single iris nozzle petal
rear_nozzle_petal_hull_0.stl … rear_nozzle_petal_hull_7.stl — [PRE-R1] Iris petal convex-hull
                                    boolean operands (× 8)
```

> **Rev R1 (2026-06-13) — REGEN PENDING:** the rear EDF spec changed from 120 mm (iris nozzle) to
> 55 mm with a fixed canonical elliptical tail nozzle + 4 RCS bleed-air thrusters (per CLAUDE.md).
> The on-disk SCAD/STL files in this directory **still reflect the pre-Rev-R1 120 mm / iris-nozzle
> geometry** — `edf_120_motor_mount.scad`, `edf_120_thrust_tube.scad`, `rear_nozzle_frame/petal*`
> have not yet been regenerated as `edf_55_motor_mount.scad`, `edf_55_thrust_tube.scad`,
> `rear_nozzle_canonical.scad`, `rcs_thruster.scad`, etc. `edf_120_motor_mount.scad` and
> `edf_120_thrust_tube.scad` remain **active** (referenced by
> `airframe/blender-scripts/blender_edf_bore_and_petals.py`,
> `airframe/gcode/davinci-jr-proto/slice_all_batches.sh`, and
> `docs/PROTO_PRINT_DAVINCI_JR.md`) and must not be archived until the Rev R1 55 mm/RCS
> replacements are generated. This is a deferred-but-active Phase 11 scope, not stale work.

---

## graphical-build-guide/

Visual build guides, assembly sequences, fabrication checklists, and troubleshooting documentation.
SVG visual build guide cards and hull outline diagrams generated by `gen_hull_outlines.py`
from blender-rendered views.

```text
TODO.md                           — Phased physical-build WBS view — master §3.0 Phases 0–10
CLAUDE.md                         — Build guide standards (phased approach, guide structure,
                                    illustrations/graphics, troubleshooting, phase
                                    completion sign-off)
gen_hull_outlines.py              — SVG generation script (runs headless Blender)
probe_stl.py                      — STL geometry probe utility (extents/centroid reporting for
                                    diagram camera framing)
update_overview_paths.py          — Rewrites overview SVG file path references after regeneration
build_guide_00_cover.svg          — Cover card
build_guide_01_print_prep.svg     — Print preparation
build_guide_02_print_hull.svg     — Printing the hull sections
build_guide_03_print_nacelle.svg  — Printing nacelle parts
build_guide_04_cut_cf.svg         — Carbon fibre cut list
build_guide_05_cf_skeleton.svg    — CF skeleton assembly
build_guide_06_nacelle_pivot.svg  — Nacelle tilt pivot installation
build_guide_07_edf_install.svg    — EDF installation
build_guide_08_nozzle_gear.svg    — Iris nozzle gear train
build_guide_09_avionics.svg       — Avionics bay layout
build_guide_10_power_wiring.svg   — Power wiring
build_guide_11_inter_board.svg    — Inter-board connections
build_guide_12_security_hw.svg    — Security hardware (TPM, tamper seals)
build_guide_13_nav_lights.svg     — Nav lights
build_guide_14_antennas.svg       — Antenna placement
build_guide_15_software.svg       — Software installation
build_guide_16_calibration.svg    — Sensor calibration
build_guide_17_ground_test.svg    — Ground test checklist
build_guide_18_first_flight.svg   — First flight procedure
build_guide_19_decal_placement.svg — Decal placement
build_guide_20_node_placement.svg — Avionics node placement
build_guide_21_node_install.svg   — Node installation
build_guide_22_void_formers.svg   — Void formers for foam fill
build_guide_23_foam_fill.svg      — Foam fill procedure
build_guide_24_access_panels.svg  — Access panel locations
build_guide_25_obstacle_sensors.svg — Obstacle sensor placement
build_guide_26_cargo_bay_winch.svg — Cargo bay winch assembly
build_plan.svg                    — Master build plan overview
components_overview.svg           — Component overview diagram
decal_sheet.svg                   — Decal sheet (CC BY 4.0 markings)
hull_bottom.svg                   — Hull bottom orthographic view
hull_front.svg                    — Hull front orthographic view
hull_side.svg                     — Hull side orthographic view
hull_top.svg                      — Hull top orthographic view
overview_bottom.svg               — Overview bottom view (assembly)
overview_front.svg                — Overview front view (assembly)
overview_side.svg                 — Overview side view (assembly)
overview_top.svg                  — Overview top view (assembly)
overview_svgs/
serenity_bottom.svg             — Rendered bottom view
serenity_bow.svg                — Rendered bow view
serenity_port.svg               — Rendered port view
serenity_starboard.svg          — Rendered starboard view
serenity_stern.svg              — Rendered stern view
serenity_top.svg                — Rendered top view
serenity_iso_port_bow.svg       — Isometric port-bow view
serenity_iso_port_quarter.svg   — Isometric port-quarter view
serenity_iso_starboard_bow.svg  — Isometric starboard-bow view
serenity_iso_stbd_quarter.svg   — Isometric starboard-quarter view
shellview/                        — Blender shell-inspection render dump: ~70 PNG renders
                                    (head/cargo/middle/rear sections, inner/outer hollow-wall
                                    comparisons, axis-labeled views, cross-sections, engrave
                                    previews) generated while iterating the hollowing pipeline,
                                    plus port_wall.stl (single-wall reference geometry probe)
```

---

## archives/

Superseded designs retained for reference (not included in active build).
See ARCHIVE_INDEX.md for full contents.

```text
18in-scale-scad/                  — 18" (SCALE=2.1974) OpenSCAD sources
```

---

## airframe/archive/

Per-component archive STLs and blender scripts superseded by active files.
See ARCHIVE_INDEX.md.

```text
stls/fuselage/                    — Pre-Rev Q fuselage STLs
stls/nacelles/                    — Pre-Rev Q nacelle STLs
blender-scripts/                  — Superseded Blender scripts
```
