# PROJECT_INDEX.md — Serenity UAV
<!-- Auto-maintained: updated whenever active files are added or removed. -->
<!-- Archive contents described in ARCHIVE_INDEX.md. -->
<!-- Last updated: Rev R (2026-06-11) -->

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
serenity_assembly.py              — Full-airframe FreeCAD assembly (Rev R, 2026-06-11)
Serenity-Assemble.py              — Legacy subsystem stub (Assembly4Lib placeholders)
Serenity-Subsystem-Assembly.py    — Legacy subsystem stub (Assembly4Lib placeholders)
serenity_subsystem_assembler.py   — Legacy subsystem assembler class (stub)
assembly1.py                      — Legacy single-part assembly stub (placeholder)
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
s_head_shell24.scad               — Nose/cockpit shell, 2mm CF-PETG skin (Rev R)
s_middle_canonical_shell24.scad   — Horseshoe neck section shell (Rev R)
s_rear_shell24.scad               — Aft engine-room shell, 2mm CF-PETG (Rev R)
battery_tray.scad                 — 6S 4000mAh LiPo tray, keel-rail slide (Rev R)
belly_panel.scad                  — Battery bay belly access panel (Rev R)
cargo/
  s_cargo_sect_shell24.scad       — Rev R cargo section shell with clamshell doors, avionics bays, GPS mounts
```

#### airframe/openscad/nacelles/

```
nacelle_pod_50mm_tandem_simple.scad — Rev R tandem pod, push-on nozzle (no iris; carried fwd from Rev T2)
nacelle_pod_50mm_tandem.scad        — Rev R tandem pod, full iris gear train (carried fwd from Rev T)
edf_stator_sleeve.scad              — Rev R 11-fin inter-stage stator sleeve (carried fwd from Rev A)
edf_aft_spider_sleeve.scad          — Rev R aft spider/motor-mount sleeve (carried fwd from Rev A)
edf_bore_sleeve.scad                — DEPRECATED (superseded by stator+spider)
nacelle_nozzle_straight.scad        — Rev R push-on straight nozzle (carried fwd from Rev T2)
nacelle_nozzle_iris.scad            — Rev R 8-petal iris nozzle (carried fwd from Rev O)
nacelle_bevel_housing.scad          — Rev R bevel-gear housing (carried fwd from Rev O)
nacelle_bevel_pair.scad             — Rev R M=1.0 14T 45° bevel pair (carried fwd from Rev O)
nacelle_pinion.scad                 — Rev R M=1.0 12T pinion (carried fwd from Rev O)
nacelle_sector_gear.scad            — Rev R M=1.0 38T sector gear (carried fwd from Rev O)
nacelle_servo_bracket.scad          — Rev R DS3218MG tilt servo bracket with M3 bosses
```

#### airframe/openscad/wings/

```
s_wings_s1223_revo.scad             — Rev R S1223 high-lift wing pair (carried fwd from Rev O)
                                      RENDER_SIDE=+1 port, -1 stbd, 0 both
s_wing_nacelle_pylon_revo.scad      — Rev R nacelle tilt pylon (carried fwd from Rev O)
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

KiCad 7/9 PCB design files.  All active designs are Rev R (EMI-hardened -2 variants).

```
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
  Kaylee.md                       — Design specification
  gen_kaylee.py                   — Python generator script (all 3 KiCad files)

XCVR-49MHZ-2 (49 MHz transceiver sub-module):
  XCVR-49MHZ-2.kicad_pro
  XCVR-49MHZ-2.kicad_sch
  XCVR-49MHZ-2.kicad_pcb
  XCVR-49MHZ-2.kicad_prl
  XCVR-49MHZ-2.md
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
  complete_xcvr_49mhz2.py         — XCVR-49MHZ-2 completion script
  add_eth_phy.py                  — Ethernet PHY addition script
  add_sensors_sbus.py             — SBUS sensor addition script
  apply_netlist.py                — Netlist application script
  fix_xcvr_labels.py              — XCVR net label fix script
  replace_footprints.py           — Footprint replacement utility for KiCad PCBs
  check_impedance.py              — Impedance checker
  generate_gerbers.py             — Gerber export script
  Serenity-Custom.pretty/         — Custom KiCad component footprint library
  drc_report.txt                  — Latest KiCad DRC report (Wash/Zoë/XCVR)
  xcrv-DRC.rpt                    — XCVR-49MHZ-2 DRC report

gerbers/
  CAPE-A-1/                       — Cape-A-1 gerbers (ARCHIVED design)
  CAPE-B-1/                       — Cape-B-1 gerbers (ARCHIVED design)
  Wash/                           — Wash (Cape-A-2) gerbers
  Zoë/                            — Zoë (Cape-B-2) gerbers
  XCVR-49MHZ-2/                   — XCVR-49MHZ-2 gerbers
  Kaylee/                         — Kaylee PDB gerbers (Rev A, 2026-06-10)
```

### avionics/gerbers/

```
archive/                          — Pre-Rev Q gerber snapshots
```

---

## docs/

```
PROJECT_INDEX.md                  — This file: active project directory tree
AVIONICS_PB2_REDESIGN.md          — 8× PocketBeagle 2 Industrial avionics redesign spec (Rev R)
BATTERY_MOUNT.md                  — Battery CG analysis, retention load case, belly panel spec (Rev R)
POWER_DISTRIBUTION.md             — Power architecture: Kaylee PDB rails, fuse map, cable spec (Rev R)
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

```
serenity-rev-r.jsx                — Rev R interactive specification (CURRENT)
serenity-rev-q.jsx                — Rev Q interactive specification (historical reference)
bom_revR.csv                      — Bill of materials (Rev R, CSV flat table — active baseline)
bom_revQ.csv                      — Bill of materials (Rev Q, CSV flat table — historical reference)
LICENSE_AND_ATTRIBUTION.md        — Attribution chain for all upstream sources
```

---

## gcs/

Ground control station.  Malcolm ("CAPT Reynolds") is the ArduPilot-compatible GCS
for Serenity UAV.  Architecture: 1× PocketBeagle 2 Industrial + Cape-B-2 (Zoë) +
XCVR-49MHZ-2, USB CDC-ECM tethered to a host Debian Linux PC running QGroundControl.
Five radio links: SiK 915 MHz, LoRa 915 MHz, WiFi 5 GHz, 49 MHz RCRS (AX.25),
Zigbee 2.4 GHz.  Servo-driven two-axis antenna gimbal with AS5600 magnetic encoders.
No external PAs (FCC-compliant with directional antennas).  IP65 field enclosure.

```
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
                                             I²C2 TCA9548A+AS5600 encoders, UART2 SiK, UART5 RCRS
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
                                             RCRS default channel
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

Design files for systems deferred until core propulsion and avionics are proven.
Not archived — intended for a future build phase.

### deferred/aft-edf/

```
README.md                         — Aft fuselage EDF design scope, rationale, and defer decision
openscad/
  s_aft_edf_plenum.scad           — Cross-shaped CF-PETG intake plenum manifold (120 mm EDF)
  s_edf_120_motor_mount.scad      — 120 mm EDF motor mount ring
  s_edf_120_thrust_tube.scad      — Thrust tube from plenum to iris nozzle
  s_neck_intake_frame.scad        — Four-port radial intake scoop frame at neck station ~310 mm
  s_rear_neck_intake_shell24.scad — Rear neck intake shell integration shell
stls/
  s_aft_edf_plenum.stl            — Compiled plenum STL
  s_edf_120_motor_mount.stl       — Compiled motor mount STL
  s_edf_120_thrust_tube.stl       — Compiled thrust tube STL
  s_neck_intake_frame.stl         — Compiled intake frame STL
  s_rear_shell24_2mm_edf_bored.stl — Rear shell with EDF bore cut
  rear_nozzle_frame.stl           — 8-petal iris nozzle ring frame
  rear_nozzle_petal.stl           — Single iris petal (print × 8)
  rear_nozzle_closed_asm.stl      — Iris assembly visual (closed position)
  rear_nozzle_petal_hull_0.stl … rear_nozzle_petal_hull_7.stl  — Individual petal hulls
```

---

## graphical-build-guide/

SVG visual build guide cards and hull outline diagrams.
Generated by `gen_hull_outlines.py` from blender-rendered views.

```
gen_hull_outlines.py              — SVG generation script (runs headless Blender)
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
```

---

## tools/

Standalone utility scripts (run from repo root).

```
validate_stls.py                  — Mesh validation: watertight check on all STLs in airframe/stls/
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
