# PROJECT_INDEX.md — Serenity UAV
<!-- Auto-maintained: updated whenever active files are added or removed. -->
<!-- Archive contents described in ARCHIVE_INDEX.md. -->
<!-- Last updated: Rev Q (2026-06-08) -->

## Repository Root

```
CLAUDE.md                         — Project instructions and standards
PROJECT_INDEX.md                  — This file
ARCHIVE_INDEX.md                  — Archive file tree (see below)
README.md                         — Project overview
REPO_ENFORCEMENT.md               — Repository rules
TODO.md                           — Work-breakdown structure and open items
```

---

## airframe/

### airframe/FreeCAD-scripts/

Assembly pipeline for FreeCAD 0.20+ with Assembly4.

```
Makefile                          — Build: SCAD→STL (openscad) + headless assembly (freecad)
serenity_assembly.py              — Full-airframe FreeCAD assembly (Rev Q, 2026-06-08)
Serenity-Assemble.py              — Legacy subsystem stub (Assembly4Lib placeholders)
Serenity-Subsystem-Assembly.py    — Legacy subsystem stub (Assembly4Lib placeholders)
serenity_subsystem_assembler.py   — Legacy subsystem assembler class (stub)
```

### airframe/blender-scripts/

Headless Blender Python scripts for shell hollowing and STL generation.

```
blender_edf_bore_and_petals.py    — EDF bore + nozzle petal geometry
blender_hollow_shells.py          — Centroid-inset 2mm shell hollowing (all 4 sections)
blender_intake_cut.py             — Fuselage EDF intake cut
blender_middle_intake_cut.py      — Middle section intake cut
blender_nacelle_revo.py           — Nacelle pod shell from hull STL
blender_nozzle_gen.py             — Iris nozzle petal geometry
blender_shells_v3.py              — Rev N 24" hull shell generation
blender_stator_gen.py             — 11-fin inter-stage stator
check_nacelle_alignment.py        — Nacelle bore alignment verification
generate_overview_svgs.py         — SVG renders from 6 cardinal + 8 isometric views
inspect_shell_center.py           — STL centroid measurement utility
repair_shells_for_scad.py         — Mesh repair pipeline (voxel-remesh → manifold)
files-hollowed-18in/              — 18" source STLs (Thingiverse base, SCALE_24=2.9294×)
```

### airframe/gcode/davinci-jr-proto/

Prototype print batches (DaVinci Jr., PLA, visual-only parts).

```
davinci_jr_pla.ini                — Slicer profile
slice_all_batches.sh              — Batch slicer script
xyz_wrap.py                       — XYZ encryption wrapper
batch_A/ … batch_Q/               — Print batches A–Q (see TODO.md §1.1)
batch_VISUAL/                     — Visual-only prototype parts
```

### airframe/openscad/

All parametric source files.  Compiled to STLs via `airframe/FreeCAD-scripts/Makefile`.

#### airframe/openscad/fuselage/

```
s_head_shell24.scad               — Nose/cockpit shell, 2mm CF-PETG skin (Rev Q)
s_middle_canonical_shell24.scad   — Horseshoe neck section shell (Rev Q)
s_rear_shell24.scad               — Aft engine-room shell, 2mm CF-PETG (Rev Q, 2026-06-08)
battery_tray.scad                 — 6S 4000mAh LiPo tray, keel-rail slide (Rev Q)
belly_panel.scad                  — Battery bay belly access panel (Rev Q)
cargo/
  s_cargo_sect_shell24.scad       — Cargo section shell with clamshell doors (Rev Q)
```

#### airframe/openscad/nacelles/

```
nacelle_pod_50mm_tandem_simple.scad — Rev T2 tandem pod, push-on nozzle (no iris)
nacelle_pod_50mm_tandem.scad        — Rev T tandem pod, full iris gear train
edf_stator_sleeve.scad              — 11-fin inter-stage stator sleeve (Rev A)
edf_aft_spider_sleeve.scad          — Aft spider/motor-mount sleeve (Rev A)
edf_bore_sleeve.scad                — DEPRECATED (superseded by stator+spider)
nacelle_nozzle_straight.scad        — Rev T2 push-on straight nozzle
nacelle_nozzle_iris.scad            — Rev O 8-petal iris nozzle (iris version)
nacelle_bevel_housing.scad          — Rev O bevel-gear housing
nacelle_bevel_pair.scad             — Rev O M=1.0 14T 45° bevel pair
nacelle_pinion.scad                 — Rev O M=1.0 12T pinion
nacelle_sector_gear.scad            — Rev O M=1.0 38T sector gear
```

#### airframe/openscad/wings/

```
s_wings_s1223_revo.scad             — S1223 high-lift wing pair (Rev O)
                                      RENDER_SIDE=+1 port, -1 stbd, 0 both
s_wing_nacelle_pylon_revo.scad      — Nacelle tilt pylon (Rev O)
```

### airframe/stls/

Compiled and repaired STLs ready for slicing.

#### airframe/stls/fuselage/

```
s_head_shell24.stl                — Head section (solid, for SCAD import ref)
s_head_shell24_2mm_repaired.stl   — Head section 2mm hollow, manifold
s_middle_canonical_shell24.stl    — Middle section
s_middle_shell24_2mm_repaired.stl — Middle section 2mm hollow, manifold
s_cargo_sect_shell24_2mm_repaired.stl — Cargo section 2mm hollow, manifold
s_rear_shell24_2mm_repaired.stl   — Rear section 2mm hollow, manifold
s_feet_x_4_scaled24.stl           — Landing feet × 4 (24" scale)
s_legs_scaled24.stl               — Landing legs (24" scale)
dorsal_antenna_fin.stl            — Dorsal antenna fin fairing
s_middle_canonical_edf_intake.stl — Middle section EDF intake opening
cargo/
  s_cargo_sect_shell24.stl              — Cargo shell (SCAD output)
  s_cargo_sect_shell24_2mm_repaired_largest.stl — Repaired largest shell body
  cargo_door_port.stl                   — Port clamshell cargo door
  cargo_door_stbd.stl                   — Stbd clamshell cargo door
  cargo_cradle_autolatch.stl            — Auto-latch payload cradle
  cargo_fpv_bezel.stl                   — FPV camera bezel
  cargo_gps_retention_ring.stl          — GPS antenna retention ring
  cargo_winch_motor_mount.stl           — N20 winch motor mount
  cargo_winch_spool.stl                 — Winch spool
  cargo_drv8833_tray.stl                — DRV8833 H-bridge PCB tray
  cargo_door_servo_bracket.stl          — Door servo bracket
  cargo_release_servo_bracket.stl       — Payload release servo bracket
  generate_cargo_doors.py               — Door STL generation script
  generate_cargo_mounts.py              — Mount STL generation script
```

#### airframe/stls/nacelles/

```
nacelle_pinion.stl                — M=1.0 12T pinion
nacelle_sector_gear.stl           — M=1.0 38T sector gear
nacelle_tip_cap_port.stl          — Port nacelle intake tip cap
nacelle_tip_cap_stbd.stl          — Stbd nacelle intake tip cap
nozzles/
  nacelle_bevel_housing.stl       — Bevel gear housing
  nacelle_bevel_pair.stl          — 14T 45° bevel pair
  nacelle_nozzle_iris.stl         — 8-petal iris nozzle ring
  nacelle_nozzle_petal.stl        — Single iris petal (print × 8)
  nacelle_nozzle_ring.stl         — Iris nozzle ring body
  nacelle_nozzle_closed_asm.stl   — Iris assembly (closed position, visual)
```

#### airframe/stls/wings/

```
s_wing_port_s1223_revo.stl        — Port wing (RENDER_SIDE=+1)
s_wing_stbd_s1223_revo.stl        — Stbd wing (RENDER_SIDE=-1)
s_wing_nacelle_pylon_revo.stl     — Nacelle tilt pylon (one per side)
```

### airframe/ (root-level files)

```
Serenity-Assembled.FCStd          — FreeCAD full-airframe assembly (235MB)
```

---

## avionics/

### avionics/firmware/

CMake-based firmware for PocketBeagle 2 Industrial (AM6254) nodes.

```
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
cn/
  CMakeLists.txt
  src/
    main.c                        — Comms node main
    si5351.c/h                    — Si5351 clock gen driver
    xcvr_kiss.c/h                 — 49MHz XCVR KISS framing
```

### avionics/kicad/

KiCad 7 PCB design files.  All active designs are Rev Q (EMI-hardened -2 variants).

```
Wash — Flight Control & Sensor Cape:
  [generated by gen_cape_a2.py + gen_cape_a2_pcb.py]

Zoë — Comms/Logging/Payload Cape:
  [generated by gen_cape_b2.py + gen_cape_b2_pcb.py]

XCVR-49MHZ-2 (49 MHz transceiver sub-module):
  [generated by complete_xcvr_49mhz2.py]

ENC-NACELLE-1 (nacelle encoder breakout):
  ENC-NACELLE-1.kicad_sch
  ENC-NACELLE-1.md

Python generation scripts:
  gen_cape_a2.py                  — Schematic generator (Cape-A-2)
  gen_cape_a2_pcb.py              — PCB layout generator (Cape-A-2)
  gen_cape_b2.py                  — Schematic generator (Cape-B-2)
  gen_cape_b2_pcb.py              — PCB layout generator (Cape-B-2)
  complete_xcvr_49mhz2.py         — XCVR-49MHZ-2 completion script
  add_eth_phy.py                  — Ethernet PHY addition script
  add_sensors_sbus.py             — SBUS sensor addition script
  apply_netlist.py                — Netlist application script
  fix_xcvr_labels.py              — XCVR net label fix script
  check_impedance.py              — Impedance checker
  generate_gerbers.py             — Gerber export script

gerbers/
  CAPE-A-1/                       — Cape-A-1 gerbers (ARCHIVED design)
  CAPE-B-1/                       — Cape-B-1 gerbers (ARCHIVED design)
  Wash/                           — Wash (Cape-A-2) gerbers
  Zoë/                            — Zoë (Cape-B-2) gerbers
  XCVR-49MHZ-2/                   — XCVR-49MHZ-2 gerbers
```

### avionics/gerbers/

```
archive/                          — Pre-Rev Q gerber snapshots
```

---

## docs/

```
bom_revP.json                     — Bill of materials (Rev P snapshot)
[additional docs as generated]
```

---

## archives/

Superseded designs retained for reference (not included in active build).
See ARCHIVE_INDEX.md for full contents.

```
18in-scale-scad/                  — 18" (SCALE=2.1974) OpenSCAD sources
```

---

## airframe/archive/

Per-component archive STLs and blender scripts superseded by active files.
See ARCHIVE_INDEX.md.

```
stls/fuselage/                    — Pre-Rev Q fuselage STLs
stls/nacelles/                    — Pre-Rev Q nacelle STLs
blender-scripts/                  — Superseded Blender scripts
```
