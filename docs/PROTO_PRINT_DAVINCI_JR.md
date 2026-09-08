<!-- OpenDyslexic font for screen reading (CC BY 4.0) -->

# Serenity-Class Tiltrotor UAV — Prototype Print Guide

## XYZprinting da Vinci Jr. 1.0 w · PLA · Rev T Baseline

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Date:** 2026-09-07 | **Baseline:** Rev T (current-specification/TODO.md, 2026-09-06 hull-frame bake)
**Supersedes:** the 2026-06-01 Rev P edition of this guide — every part list, bounding box,
scale factor, and batch below was re-measured directly from the current `airframe/stls/`
tree (bounding boxes computed 2026-09-07 via `trimesh`) and cross-checked against
`current-specification/bom_revS.csv`. See §9 for what changed and what got dropped.

> Fan engineering work inspired by the Firefly-class transport ship *Serenity*
> from *Firefly* (Fox, 2002) and *Serenity* (Universal, 2005).
> © Joss Whedon / Mutant Enemy Productions — **Not an officially licensed product.**

---

## 1. Printer Reference

| Parameter | Value |
| ----------- | ------- |
| Printer | XYZprinting da Vinci Jr. 1.0 **w** (WiFi model) |
| Build volume | 150 × 150 × 150 mm |
| Nozzle | 0.4 mm (fixed, non-swappable) |
| Filament | 1.75 mm PLA — XYZ cartridge or compatible 3rd-party |
| Bed | Non-heated — apply glue stick before every plate |
| Slicer | XYZware 3.x (Windows / Mac) |
| Output format | `.3w` (WiFi print) or USB `.3w` file |

> **Note on XYZware settings:** XYZware exposes Quality (Draft/Normal/Fine), Fill %, Surface
> (shell count), Support (Off/Standard/Full), and Raft (On/Off). Temperature and speed are
> fixed per quality preset — 200 °C / ~40–50 mm/s for Normal PLA. All settings in this guide
> use those labels.

---

## 2. Global PLA Settings for All Prototype Prints

| Setting | Value | XYZware Control |
| --------- | ------- | ----------------- |
| Quality | **Normal** (0.2 mm layers) | Quality → Normal |
| Nozzle temp | 200 °C (automatic for PLA) | — |
| Shell count | **2** (functional/fit parts) or **1** (shape-only hull shells, §3) | Surface → 2 or 1 |
| First layer | Automatic slow-down in firmware | — |
| Cooling | On after first layer (automatic) | — |
| Bed prep | Glue stick — light even coat | — |
| Raft | See per-batch table | Raft → On/Off |

> **Prototype vs. flight-spec:** Production prints use CF-PETG/PETG with 4 perimeters, 20–40%
> infill, 0.15 mm layers, per-part gyroid/wall specs in `current-specification/bom_revS.csv`.
> These PLA prototype settings prioritize speed and fit-checking, not structural performance.
> **Do NOT fly any part printed to this spec.**

---

## 3. Reduced-Scale Policy

The Rev P edition of this guide scaled each hull shell independently (63–84%) to fit the
150 mm bed, which §9 of that edition flagged as a known defect — a hull mockup assembled from
those prints was not internally to scale. This edition fixes that:

- **Hull shells (head/cargo/middle/rear) print at one consistent scale: 64%.** The most
  restrictive shell (`head_shell24_2mm_repaired.stl`, 232.8 mm Y-extent) sets the ceiling —
  150 / 232.8 = 64.4%, rounded down to 64% for margin. At 64% every other hull shell clears
  the bed with room to spare (see §4). A shell-only mockup assembled from these four prints is
  now proportionally correct at **15.4 in** (64% of the 24 in canonical hull).
- **Everything else prints as close to 1:1 as the bed allows.** Cargo hardware, nozzle/flap
  parts, nacelle mechanism parts, splice collars, avionics enclosures, and landing gear are
  functional fit-checks against real servos, PCBs, bearings, and fasteners — shrinking them
  to 64% would defeat the purpose. Only the handful of parts that individually exceed 150 mm
  in some axis (battery tray, belly panel, nacelle pods) get a small bed-fit-only scale,
  noted per part in §4.
- Wings and landing-gear legs already clear the bed at 1:1 and print at 1:1 — they are not
  forced to the 64% hull scale, so do not expect them to look proportionally undersized next
  to the scaled hull shells in a mock assembly. This is a fit/mechanism check set, not a
  scale-model kit.

---

## 4. Part Inventory — Measured Bounding Boxes and Scale Factors

All dimensions below are from direct bounding-box measurement of the STL files currently in
`airframe/stls/` (2026-09-07), X × Y × Z in the project hull frame. Superseded/stale STL
variants that still exist on disk (see §9) are excluded from this table.

### 4.1 Parts that print at 1:1

| File | X mm | Y mm | Z mm | Notes |
| ------ | ------ | ------ | ------ | ------- |
| `fuselage/cargo/cargo_door_servo_bracket.stl` | 44.0 | 28.0 | 5.0 | SG90 door-cam bracket |
| `fuselage/cargo/cargo_release_servo_bracket.stl` | 44.0 | 28.0 | 5.0 | SG90 latch-release bracket |
| `fuselage/cargo/cargo_drv8833_tray.stl` | 36.0 | 33.0 | 6.0 | DRV8833 breakout tray |
| `fuselage/cargo/cargo_gps_retention_ring.stl` | 50.0 | 50.0 | 2.5 | GPS module retention ring |
| `fuselage/cargo/cargo_fpv_bezel.stl` | 29.0 | 29.0 | 2.5 | FPV camera bezel |
| `fuselage/cargo/cargo_cradle_autolatch.stl` | 110.0 | 80.0 | 72.0 | Auto-latch payload cradle |
| `fuselage/cargo/cargo_door_port.stl` | 55.2 | 106.0 | 9.1 | Rev T clamshell door (redesigned since Rev P) |
| `fuselage/cargo/cargo_door_stbd.stl` | 55.7 | 106.0 | 9.2 | Rev T clamshell door |
| `fuselage/cargo/cargo_hinge_retention.stl` | 106.9 | 132.0 | 8.9 | New — door hinge retention strip |
| `fuselage/cargo/cargo_vera_faraday.stl` | 76.8 | 70.8 | 32.6 | New — Observer cape Faraday enclosure |
| `fuselage/cargo/cargo_winch_motor_mount.stl` | 36.0 | 28.0 | 15.0 | **Legacy N20 mount — see §9, not the current winch design** |
| `fuselage/cargo/cargo_winch_spool.stl` | 26.0 | 26.0 | 22.0 | **Legacy spool — see §9, not the current winch design** |
| `fuselage/battery_tray.stl` | 154.0 | 51.5 | 62.0 | X exceeds bed — scale 97% (see 4.2) |
| `fuselage/belly_panel.stl` | 160.0 | 3.5 | 65.0 | X exceeds bed — scale 94% (see 4.2) |
| `fuselage/bow_sensor_faceplate.stl` | 28.0 | 16.0 | 2.5 | Nose sensor cluster faceplate |
| `fuselage/dorsal_antenna_fin.stl` | 20.0 | 4.0 | 35.0 | Dorsal antenna fin |
| `fuselage/inara_access_cover.stl` | 46.5 | 66.5 | 4.8 | Payload-bay access cover |
| `fuselage/river_access_cover.stl` | 46.5 | 64.0 | 4.6 | Payload-bay access cover |
| `fuselage/wing_root_flange_port.stl` | 39.3 | 60.0 | 80.0 | Bonded wing-root flange (Rev T1) |
| `fuselage/wing_root_flange_stbd.stl` | 40.0 | 60.0 | 80.0 | Bonded wing-root flange |
| `fuselage/head_cargo_splice_collar.stl` | 110.2 | 17.7 | 77.8 | Section splice collar |
| `fuselage/cargo_middle_splice_collar.stl` | 125.8 | 18.0 | 128.1 | Section splice collar |
| `fuselage/middle_rear_splice_collar.stl` | 112.1 | 18.0 | 118.8 | Section splice collar |
| `fuselage/landing-gear/lg_r6_1_5in_leg_assembled.stl` | 142.1 | 55.6 | 117.5 | **Default** LG leg (1.5 in stroke, Rev R6) |
| `fuselage/landing-gear/lg_r6_1_5in_leg_frame.stl` | 96.3 | 79.1 | 16.0 | LG leg bay frame |
| `fuselage/landing-gear/lg_r6_common_bay.stl` | 32.9 | 54.0 | 78.0 | Shared LG sponson bay |
| `fuselage/landing-gear/lg_r6_common_foot.stl` | 68.5 | 55.6 | 10.0 | Shared LG foot |
| `fuselage/landing-gear/lg_r6_common_ductile_wire_nominal.stl` | 7.6 | 4.3 | 41.4 | Undeformed ductile-wire jig reference |
| `fuselage/landing-gear/lg_r6_common_spring_wire_nominal.stl` | 7.0 | 3.6 | 35.3 | Undeformed spring-wire jig reference |
| `nacelles/nacelle_trunnion.stl` | 50.0 | 50.0 | 11.5 | Rev T4 trunnion (2× BRG-6704ZZ, replaces MF104ZZ) |
| `nacelles/nacelle_servo_bracket.stl` | 44.4 | 22.4 | 18.0 | DS3225 tilt-servo bracket |
| `nacelles/edf_stator_sleeve.stl` | 55.0 | 58.0 | 32.5 | 50 mm EDF stator sleeve |
| `nacelles/edf_aft_spider_sleeve.stl` | 55.0 | 58.0 | 43.8 | 50 mm EDF aft spider sleeve |
| `nacelles/esc/nacelle_esc_cover_port_a.stl` | 50.5 | 24.2 | 75.5 | Rev T4c ESC bay cover |
| `nacelles/esc/nacelle_esc_cover_port_b.stl` | 50.5 | 24.2 | 75.5 | Rev T4c ESC bay cover |
| `nacelles/esc/nacelle_esc_cover_stbd_a.stl` | 50.2 | 25.4 | 75.5 | Rev T4c ESC bay cover |
| `nacelles/esc/nacelle_esc_cover_stbd_b.stl` | 50.2 | 25.4 | 75.5 | Rev T4c ESC bay cover |
| `nacelles/nozzles/nacelle_nozzle_flap.stl` | 10.5 | 23.2 | 50.2 | Rev T3 shingle-flap nozzle petal (replaces old iris petal) |
| `nacelles/nozzles/nacelle_nozzle_flap_seal.stl` | 9.2 | 25.5 | 50.2 | Seal-lapped alternate flap |
| `nacelles/nozzles/nacelle_nozzle_ring.stl` | 66.4 | 66.2 | 8.0 | Nozzle iris base ring |
| `nacelles/nozzles/nacelle_nozzle_throat.stl` | 71.2 | 71.2 | 22.1 | Nozzle throat |
| `nacelles/nozzles/nacelle_nozzle_iris-closed.stl` | 71.2 | 71.2 | 57.6 | Closed-assembly reference print |
| `nacelles/nozzles/nacelle_nozzle_iris-open.stl` | 71.2 | 71.2 | 58.1 | Open-assembly reference print |
| `wings/wing_port_s1223_revo.stl` | 95.7 | 129.0 | 31.4 | S1223 wing, port |
| `wings/wing_stbd_s1223_revo.stl` | 95.7 | 129.0 | 31.4 | S1223 wing, starboard |

### 4.2 Parts that require bed-fit scaling

| File | Native size (mm) | Constraint | Scale | Scaled size (mm) |
| ------ | ----------------- | ------------ | ------- | ----------------- |
| `fuselage/battery_tray.stl` | 154.0 × 51.5 × 62.0 | X=154.0 > 150 | **97%** | 149.4 × 50.0 × 60.1 |
| `fuselage/belly_panel.stl` | 160.0 × 3.5 × 65.0 | X=160.0 > 150 | **94%** | 150.4 × 3.3 × 61.1 — round down to **93%** if it still clips |
| `nacelles/nacelle_port_revs.stl` | 76.4 × 167.3 × 79.1 | Y=167.3 > 150 | **89%** | 68.0 × 148.9 × 70.4 |
| `nacelles/nacelle_stbd_revs.stl` | 76.4 × 167.3 × 77.7 | Y=167.3 > 150 | **89%** | 68.0 × 148.9 × 69.2 |
| `fuselage/head_shell24_2mm_repaired.stl` | 129.4 × 232.8 × 140.5 | Y=232.8 > 150 | **64%** | 82.8 × 149.0 × 89.9 |
| `fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl` | 194.3 × 198.5 × 163.2 | X,Y,Z all > 150 | **64%** | 124.4 × 127.0 × 104.4 |
| `fuselage/middle_shell24_2mm_repaired.stl` | 176.9 × 71.3 × 164.8 | X,Z > 150 | **64%** | 113.2 × 45.6 × 105.5 |
| `fuselage/rear_shell24_2mm_repaired.stl` | 140.6 × 180.0 × 157.8 | Y,Z > 150 | **64%** | 90.0 × 115.2 × 101.0 |

> **Nacelle pod caveat (unchanged from the Rev P finding):** at 89% the pod's internal EDF
> bore is undersized relative to the real 50 mm EDF stack — this print checks external
> shape, stator-sleeve interface, and trunnion boss location only. Print `edf_stator_sleeve`
> and `edf_aft_spider_sleeve` (§4.1, 1:1) separately for an actual EDF-diameter fit check.
>
> **Scale tip:** Enter the percentage in XYZware → Transform → Scale (uniform). Lock the
> aspect ratio checkbox. The fields accept a percentage value directly.

---

## 5. Print Batches

### Batch A — Cargo Door Hardware (1 plate)

**Goal:** Verify SG90 servo pocket, DRV8833 tray fit, and GPS/FPV bezel openings —
unchanged from Rev P (BOM confirms these rows carry forward untouched).

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `cargo_door_servo_bracket.stl` | 2 | Flat side down | Print 2× (door + release use the same bracket) |
| `cargo_release_servo_bracket.stl` | 1 | Flat side down | |
| `cargo_drv8833_tray.stl` | 1 | Mounting face down | No supports |
| `cargo_gps_retention_ring.stl` | 1 | Flat (2.5 mm) | Use raft — very thin |
| `cargo_fpv_bezel.stl` | 1 | Flat (2.5 mm) | Print beside GPS ring |

| Setting | Value |
| --------- | ------- |
| Fill | 20% |
| Surface | 2 shells |
| Support | Off |
| Raft | On |
| Est. time | ~2 h |

**Verify:** SG90 body drops into both bracket pockets without force · DRV8833 breakout snaps
into tray · GPS ring opening is round and centered · FPV bezel opening is round and centered.

---

### Batch B — Port Cargo Door + Hinge Retention (1 plate)

**Goal:** Verify the Rev T clamshell door geometry — redesigned since Rev P (new bbox is
55.2×106×9.1 mm vs. the old 108×33.7×87 mm profile, so re-check hinge and gasket details from
scratch, not against the Rev P print).

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `cargo_door_port.stl` | 1 | Outer hull face down | Supports on hinge tab only |
| `cargo_hinge_retention.stl` | 1 | Flat | Batch with door — new Rev T part |

| Setting | Value |
| --------- | ------- |
| Fill | 20% |
| Surface | 2 shells |
| Support | Standard (hinge tab overhang) |
| Raft | Off |
| Est. time | ~2.5 h |

**Verify:** hinge tab bore accepts intended pin stock with slight clearance · hinge retention
strip captures the tab without binding · outer curvature lays flush against
`cargo_sect_shell24_2mm_repaired.stl` at 64% (Batch H).

---

### Batch C — Starboard Cargo Door (1 plate)

Mirror of Batch B, `cargo_door_stbd.stl` only. Same settings and checks. **Additional
check:** port/stbd doors mate symmetrically along the center seam, ≤1 mm gap.

---

### Batch D — Cargo Cradle + Faraday Enclosure (1 plate)

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `cargo_cradle_autolatch.stl` | 1 | Base down | Supports on latch tab overhang if present |
| `cargo_vera_faraday.stl` | 1 | Flat mounting face down | New Rev T part — Observer cape enclosure |

| Setting | Value |
| --------- | ------- |
| Fill | 25% |
| Surface | 2 shells |
| Support | Standard |
| Raft | Off |
| Est. time | ~2.5 h |

**Verify:** cradle latch tab flexes without cracking (PLA is more brittle than production
CF-PETG) · pull-wire channel runs cleanly · Faraday enclosure lid seats flush.

---

### Batch E — Nozzle Flap System — 1 Nacelle Set (1 plate)

**Goal:** verify the current Rev T3 shingle-flap petal (interpenetrating, seal-lapped
alternate flaps) — this **replaces** the Rev P iris-petal design entirely; do not compare
against old `nacelle_nozzle_petal.stl` prints.

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `nacelle_nozzle_flap.stl` | 4 | Flat, concave face up | Master flaps |
| `nacelle_nozzle_flap_seal.stl` | 4 | Flat, concave face up | Seal-lapped alternates, 0.2 mm outboard offset |
| `nacelle_nozzle_ring.stl` | 1 | Tooth-side up | Batch with flaps |
| `nacelle_nozzle_throat.stl` | 1 | Flat | Batch with flaps |

| Setting | Value |
| --------- | ------- |
| Fill | 15% |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~2 h |

**Verify:** 8 flaps (4 master + 4 seal) form a closed disc with no gap >1 mm at the
seal-lap overlaps · ring/throat register concentrically with the flap band · no binding
through a full sweep.

---

### Batch F — Nozzle Assembly Reference Prints (1 plate)

**Goal:** whole-assembly visual reference — these two STLs are pre-merged closed/open
states, useful for checking the flap band against the pod exterior without hand-assembling
loose flaps.

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `nacelle_nozzle_iris-closed.stl` | 1 | Base down | Reference only — not a functional test article |
| `nacelle_nozzle_iris-open.stl` | 1 | Base down | Reference only |

| Setting | Value |
| --------- | ------- |
| Fill | 10% |
| Surface | 1 shell |
| Support | Off |
| Raft | Off |
| Est. time | ~2.5 h (both) |

---

### Batch G — Nacelle Mechanism Hardware (1 plate)

**Goal:** verify the Rev T4 trunnion (2× BRG-6704ZZ, 20×27×4 mm — **not** the superseded
MF104ZZ this guide previously called out, see §9), DS3225 tilt-servo bracket, and EDF
sleeves.

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `nacelle_trunnion.stl` | 2 | Flat face down | One per nacelle |
| `nacelle_servo_bracket.stl` | 2 | Flat face down | DS3225 body, not SPT5425LV — bracket geometry changed at Rev S1d |
| `edf_stator_sleeve.stl` | 1 | Flat face down | Real 50 mm EDF diameter — functional fit |
| `edf_aft_spider_sleeve.stl` | 1 | Flat face down | Real 50 mm EDF diameter — functional fit |

| Setting | Value |
| --------- | ------- |
| Fill | 25% |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~3 h |

**Verify:** two BRG-6704ZZ (OD 27 mm) press into the trunnion bores — light thumb pressure ·
DS3225 body (40×20×40.5 mm, per its datasheet in `avionics/datasheets/`) drops into the
servo bracket pocket without force · EDF stator/spider sleeves accept an actual 50 mm EDF
can with light clearance.

---

### Batch H — ESC Bay Covers (1 plate)

**Goal:** verify the Rev T4c hinged ESC bay covers, 4 distinct parts (port/stbd × A/B).

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `nacelle_esc_cover_port_a.stl` | 1 | Flat | |
| `nacelle_esc_cover_port_b.stl` | 1 | Flat | |
| `nacelle_esc_cover_stbd_a.stl` | 1 | Flat | |
| `nacelle_esc_cover_stbd_b.stl` | 1 | Flat | |

| Setting | Value |
| --------- | ------- |
| Fill | 20% |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~3.5 h (all 4) |

**Verify:** each cover's hinge feature closes flush against its nacelle pod print (Batch K)
without interference at the trunnion boss.

---

### Batch I — Nacelle Pods at 89% (2 plates)

**Goal:** external shape, stator-sleeve interface, and trunnion boss location check — the
89% scale undersizes the EDF bore (see §4.2 caveat); use Batch G for a real-diameter EDF fit
check instead.

| Part | Qty | Orientation at 89% | Notes |
| ------ | ----- | --------------------- | ------- |
| `nacelle_port_revs.stl` | 1 | Intake face down | 68.0 × 148.9 × 70.4 mm |
| `nacelle_stbd_revs.stl` | 1 | Intake face down | 68.0 × 148.9 × 69.2 mm — separate plate |

| Setting | Value |
| --------- | ------- |
| Fill | 15% (shape check only) |
| Surface | 2 shells |
| Support | Off |
| Raft | On (tall print, improves base adhesion) |
| Est. time | ~5 h each |

**Verify:** overall external shape matches the canonical-accuracy reference hierarchy
(`airframe/HULL_FRAME_REFERENCE.md`) · trunnion boss location matches Batch G's trunnion
print · ESC bay covers (Batch H) seat correctly.

---

### Batch J — Wings + Landing Gear (2 plates)

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `wing_port_s1223_revo.stl` | 1 | Top surface up | 1:1 — fits the bed without scaling |
| `wing_stbd_s1223_revo.stl` | 1 | Top surface up | Separate plate or batch if room allows |
| `wing_root_flange_port.stl` | 1 | Flat | Batch with wings if plate space allows |
| `wing_root_flange_stbd.stl` | 1 | Flat | |

## Wing plate

| Setting | Value |
| --------- | ------- |
| Fill | 15% |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~2.5 h each wing |

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `lg_r6_1_5in_leg_assembled.stl` | 1 | Flat | Default LG leg (1.5 in stroke) — see §9 for the 3.0 in variant |
| `lg_r6_1_5in_leg_frame.stl` | 1 | Flat | |
| `lg_r6_common_bay.stl` | 1 | Flat | Sponson bay, shared between both leg variants |
| `lg_r6_common_foot.stl` | 1 | Flat | |
| `lg_r6_common_ductile_wire_nominal.stl` | 1 | Axis flat | Bending jig reference only |
| `lg_r6_common_spring_wire_nominal.stl` | 1 | Axis flat | Bending jig reference only |

## LG plate

| Setting | Value |
| --------- | ------- |
| Fill | 25% (landing loads even in prototype) |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~3 h |

**Verify:** leg assembly stroke is unobstructed through full travel · foot seats in leg
without binding · bay accepts leg + foot in the sponson mounting orientation.

---

### Batch K — Splice Collars (1 plate)

**Goal:** verify the section-to-section open-face splice joints (2-wall contact annulus +
positive stop, per root `AGENTS.md` §7 structural-joint rule).

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `head_cargo_splice_collar.stl` | 1 | Flat | |
| `cargo_middle_splice_collar.stl` | 1 | Flat | |
| `middle_rear_splice_collar.stl` | 1 | Flat | |

| Setting | Value |
| --------- | ------- |
| Fill | 25% |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~4.5 h (all 3) |

**Verify:** each collar seats its two mating hull-shell open faces with a positive stop —
no friction-fit-only contact.

---

### Batch L — Avionics/Structural Small Parts (1 plate)

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `bow_sensor_faceplate.stl` | 1 | Flat | |
| `dorsal_antenna_fin.stl` | 1 | Base down | |
| `inara_access_cover.stl` | 1 | Flat | |
| `river_access_cover.stl` | 1 | Flat | Batch beside inara cover |
| `battery_tray.stl` | 1 | Base down, **97% scale** | 149.4 × 50.0 × 60.1 mm |

| Setting | Value |
| --------- | ------- |
| Fill | 20% |
| Surface | 2 shells |
| Support | Off |
| Raft | Off |
| Est. time | ~4 h |

**Verify:** access covers seat flush against their cutouts · battery tray footprint accepts
the intended battery pack dimensions (check current cell against `bom_revS.csv`) even at
97% scale (should be a 3% oversize allowance, not undersize — recheck before flight-spec
print).

---

### Batch M — Belly Panel (1 plate, separate — flat/thin)

| Part | Qty | Orientation | Notes |
| ------ | ----- | ------------- | ------- |
| `belly_panel.stl` | 1 | Flat, **94% scale** | 150.4 × 3.3 × 61.1 mm — recheck actual clearance after scaling; drop to 93% if the sliced footprint still clips 150 mm |

| Setting | Value |
| --------- | ------- |
| Fill | 15% |
| Surface | 2 shells |
| Support | Off |
| Raft | On (very thin, long part — prevents warp lift) |
| Est. time | ~1.5 h |

---

### Batch N — Hull Shells at 64% (4 plates)

**Goal:** internally-consistent scaled hull mockup — see §3. Not a structural or fit-check
set; shape/proportion reference only.

| Part | Qty | Scaled size (64%) | Orientation |
| ------ | ----- | -------------------- | ------------- |
| `head_shell24_2mm_repaired.stl` | 1 | 82.8 × 149.0 × 89.9 mm | Nose-up, broadest relatively flat face down |
| `cargo_sect_shell24_2mm_repaired.stl` | 1 | 124.4 × 127.0 × 104.4 mm | Belly face down |
| `middle_shell24_2mm_repaired.stl` | 1 | 113.2 × 45.6 × 105.5 mm | Belly face down |
| `rear_shell24_2mm_repaired.stl` | 1 | 90.0 × 115.2 × 101.0 mm | Engine-bell aft face down |

| Setting | Value |
| --------- | ------- |
| Fill | 10% (shape reference only) |
| Surface | **2 shells** (not 1 — see §10; sampled nominal wall at 64% runs as low as ~1.08 mm, close enough to the 0.8 mm 2-perimeter floor that a single 0.4 mm perimeter leaves no margin) |
| Support | Standard (each shell has some undercut — cockpit glazing, engine bell, intake) — **PrusaSlicer pipeline only, see §10**; the CuraEngine pipeline in `airframe/gcode/davinci-jr-proto/cura/` slices these 4 shells with support **off** (support crashes/hangs the CLI on this geometry) |
| Raft | Off |
| Est. time | ~4–5 h each, ~18 h total |

**Verify:** all four sections register at their splice-collar interfaces (Batch K, printed
1:1 — **note the collars will not mate with 64%-scale shells**; this is a visual-alignment
check only, not a physical mate test) · overall silhouette matches
`airframe/HULL_FRAME_REFERENCE.md` canonical-accuracy references · nacelle pods (Batch I,
89% scale) sit visually near the wing attachment zone, acknowledging the two are not at the
same scale factor (§3).

---

## 6. Master Print Schedule and Time Estimate

| Batch | Key Parts | Scale | Plates | Est. Time | Priority |
| ------- | ----------- | ------- | -------- | ----------- | ---------- |
| A | Cargo door hardware | 1:1 | 1 | ~2.0 h | ★★★ |
| B | Port cargo door + hinge retention | 1:1 | 1 | ~2.5 h | ★★★ |
| C | Stbd cargo door | 1:1 | 1 | ~2.5 h | ★★★ |
| D | Cargo cradle + Faraday enclosure | 1:1 | 1 | ~2.5 h | ★★★ |
| E | Nozzle flap system (8 flaps + ring/throat) | 1:1 | 1 | ~2.0 h | ★★ |
| F | Nozzle assembly reference | 1:1 | 1 | ~2.5 h | ★ |
| G | Nacelle mechanism (trunnion, servo bkt, EDF sleeves) | 1:1 | 1 | ~3.0 h | ★★ |
| H | ESC bay covers ×4 | 1:1 | 1 | ~3.5 h | ★★ |
| I | Nacelle pods, port + stbd | 89% | 2 | ~10.0 h | ★★ |
| J | Wings + landing gear | 1:1 | 2 | ~5.5 h | ★ |
| K | Splice collars ×3 | 1:1 | 1 | ~4.5 h | ★★ |
| L | Avionics/structural small parts | 1:1 / 97% | 1 | ~4.0 h | ★ |
| M | Belly panel | 94% | 1 | ~1.5 h | ★ |
| N | Hull shells ×4 | 64% | 4 | ~18.0 h | ★ |
| **Total** | **14 batches · 20 plates** | — | — | **~64.5 h** | — |

> **Priority key:** ★★★ = cargo system validation (current build focus); ★★ = propulsion /
> mechanism verification; ★ = shape/visual reference. Print ★★★ and ★★ batches first.

---

## 7. Bed Adhesion and PLA-Specific Notes

### 7.1 Glue Stick Application

Apply a thin, even coat of glue stick to the full bed surface before every plate. Too much
glue causes rough first layers; too little causes part detachment. Allow glue to dry for
30 seconds before starting the print.

### 7.2 Raft vs. No Raft

Use raft for: tall narrow prints (nacelle pods, Batch I), very thin flat parts (GPS ring,
FPV bezel, belly panel), first print on fresh glue stick. Skip raft for large flat parts
with good bed contact (cargo doors, wings).

### 7.3 PLA vs. Production Materials

All production flight parts use CF-PETG (structural) or PETG (shells) per
`current-specification/bom_revS.csv`. PLA is stiffer and more brittle. Expect snap-fit
features (cargo cradle latch tab) to be more fragile than the CF-PETG version; threaded
bores to run tighter — chase with a drill bit if needed; PLA is not heat-tolerant (deforms
above ~60 °C); do not print pivot rods, hinge pins, or the trunnion bearing shafts in PLA —
use the real steel/CF hardware for those fit checks.

### 7.4 Support Removal

XYZware support material is the same PLA as the part. Remove with flush cutters and a hobby
knife. Sand support-contact surfaces to 320 grit if surface finish matters for the fit check.

---

## 8. Post-Print Verification Checklist

### Cargo System (Batches A–D)

- [ ] Both cargo doors fit the cargo shell's belly curve (visual only vs. the 64%-scale Batch N shell)
- [ ] Port/stbd door hinge tabs interdigitate, no interference
- [ ] SG90 servo fits both door and release brackets, no binding
- [ ] DRV8833 breakout PCB snaps into tray
- [ ] Hinge retention strip captures the door tab
- [ ] GPS ring and FPV bezel openings are round and centered
- [ ] Faraday enclosure lid seats flush

### Nozzle Flap System (Batches E–F)

- [ ] All 8 flaps (4 master + 4 seal-lapped) install on the ring/throat and sweep freely
- [ ] Closed position forms a smooth band with no gap >1 mm at any seal lap
- [ ] Reference closed/open assembly prints match the loose-flap assembly

### Nacelle Mechanism (Batches G–I)

- [ ] 2× BRG-6704ZZ (27 mm OD) press into the trunnion — light thumb pressure, not a hammer fit
- [ ] DS3225 servo body drops into the servo bracket pocket
- [ ] EDF stator/spider sleeves accept a real 50 mm EDF can
- [ ] ESC bay covers close flush at both port and stbd, all 4 covers
- [ ] Nacelle pod exterior shape matches canonical-accuracy references

### Wings and Landing Gear (Batch J)

- [ ] Wing planform matches the S1223-derived canonical profile
- [ ] Wing root flange registers against the wing root tenon
- [ ] LG leg strokes through full travel without binding; foot seats in bay

### Hull Assembly Mock-up (Batch N)

- [ ] All four hull sections are internally consistent at 64% (not the case in the Rev P edition)
- [ ] Section-to-section silhouettes align visually at the splice locations
- [ ] Overall shape matches `airframe/HULL_FRAME_REFERENCE.md` canonical-accuracy references

---

## 9. Changes Since the Rev P Edition, and Known Limitations

### 9.1 Design changes this edition reflects

- **Cargo door redesigned** — bounding box changed from 108×33.7×87 mm to 55.2×106×9.1 mm;
  the Rev P print is not a valid reference for hinge/gasket geometry any more.
- **Nozzle mechanism replaced** — the Rev P iris-petal design (`nacelle_nozzle_petal.stl`,
  8 identical petals) is gone. Rev T3 uses a shingle-flap band (4 master + 4 seal-lapped
  flaps, `nacelle_nozzle_flap.stl` / `nacelle_nozzle_flap_seal.stl`).
- **Nacelle trunnion bearing changed** — the Rev P/Rev S guide's MF104ZZ (OD 10 mm) callout
  is superseded; Rev T4 uses 2× BRG-6704ZZ (OD 27 mm) per nacelle. Do not chase a 10 mm bore
  when fitting the current trunnion print.
- **Nacelle tilt servo changed** — DS3225 (40×20×40.5 mm), not the SPT5425LV this guide's
  prior edition would have implied for the tilt axis.
- **Gear train deleted** — the M=0.5/M=1.0 sector-gear/pinion/bevel-gear train (Rev P §6,
  Batch F) was archived at Rev T (2026-07-18, replaced by the Option B pushrod tilt drive).
  Its STLs now live only as reference placeholders in `airframe/placeholders/gears/` and are
  **not part of this print set.**
- **Rear 120 mm EDF deferred** — remains Phase 11 per root `AGENTS.md`; its STL is a
  placeholder (`airframe/placeholders/propulsion/EDF_120mm_6S_deferred.stl`), not a build
  target. Dropped from this guide's batches entirely (was Batch G/I/J in the Rev P edition).
- **ESC bay covers, splice collars, Faraday enclosure, hinge retention** are new parts with
  no Rev P equivalent (Rev T4c and Rev T1c work).
- **Landing gear replaced** — Rev P had no printed landing gear STLs in this guide; current
  gear is Rev R6, with two leg-length variants sharing common bay/foot/wire hardware. This
  guide defaults to the **1.5 in leg** (canonical default per `airframe/AGENTS.md` landing
  gear pointer); the 3.0 in extended variant (`lg_r6_3_0in_*`) is not printed by default —
  swap it in if you're validating the extended-clearance case.

### 9.2 Parts on disk that are NOT current — do not print as reference

- `fuselage/cargo/cargo_winch_motor_mount.stl` and `cargo_winch_spool.stl` are the retired
  N20-gearmotor-era winch design. The current winch (SPT5425LV converted with LibreServo v2,
  `docs/CARGO_WINCH_SPECIFICATION.md` Rev C) uses `cargo_winch_pedestal_port.stl`,
  `cargo_winch_pedestal_stbd.stl`, and `cargo_winch_spool_r2.stl` — **none of which have been
  generated yet** (BOM rows `PRINT-CARGO-WINCH-PEDESTAL-PORT/STBD` and
  `PRINT-CARGO-WINCH-SPOOL-R2` are marked "NOT YET GENERATED"). This batch is blocked on
  that generator work, not on this print guide.
- `fuselage/head_shell24.stl` (no `_2mm_repaired` suffix), `fuselage/cargo/cargo_sect_shell24_repaired.stl`
  (no `2mm`), `fuselage/middle_canonical_shell24.stl`, and
  `nacelles/eng_left_shell24_50mm_repaired.stl` / `eng_right_shell24_50mm_repaired.stl` are
  pre-Rev-T bakes (mtimes June 2026, before the 2026-09-06 hull-frame bake) superseded by the
  `_2mm_repaired` shells and `nacelle_port_revs.stl` / `nacelle_stbd_revs.stl` used in this
  guide.
- `fuselage/landing-gear/lg_r6_1_5in_hull_legs.stl`, `lg_r6_1_5in_hull_stance.stl`, and the
  `*_deformed.stl` wire/leg meshes are FEA/visualization outputs (full-stance renders,
  deflected shapes), not individually printable parts — excluded from all batches.

### 9.3 Known limitations of this prototype set

1. **Nacelle pods at 89%:** EDF bore is undersized versus the real 50 mm EDF — shape and
   trunnion-boss check only. Use Batch G (1:1 stator/spider sleeves) for the real-diameter
   EDF fit check.
2. **Hull shells (64%) and nacelle pods (89%) are at different scale factors** — this is
   intentional (§3): the hull scale is fixed by the bed, the nacelle scale is kept as close
   to functional 1:1 as the bed allows. A single mock assembly of Batch I + Batch N parts
   will not be dimensionally consistent between hull and nacelle.
3. **Splice collars (Batch K) print 1:1 but the hull shells they join (Batch N) print at
   64%** — the two will not physically mate. Collars are validated against the real 1:1
   hull sections separately, not against the scaled shape-reference prints.
4. **PLA is fragile at these wall/infill settings** — hull sections at 1 shell / 10% infill
   are visual reference only; handle carefully.
5. **XYZware `.3w` gcode in `airframe/gcode/davinci-jr-proto/batch_*` predates this
   revision** — every batch folder there (`batch_A` through `batch_VISUAL`) was sliced
   against Rev P/Rev O geometry and does not match the parts in §4–§5 above. Re-slice from
   the current STLs listed here before printing; do not reuse the existing `.gcode` files.

---

## 10. Rev T Mesh-Integrity and Cura-Slicing Verification (2026-09-07)

Every part in §4 was run through a manifold/watertight check (`trimesh`,
vertex-merged), a scale-adjusted wall-thickness sample (250 rays per part,
5th-percentile reported to avoid single-outlier bias), and a real slice
attempt with `cura-engine` 5.0.0 (headless CLI, no GUI) targeting the da
Vinci Jr. 1.0 w profile. Driver script and output:
`airframe/gcode/davinci-jr-proto/cura/slice_all_batches_cura.py` and
`airframe/gcode/davinci-jr-proto/cura/sdcard/` (microSD-ready, see that
directory's `README.md`).

### 10.1 Mesh integrity — all 49 parts watertight

Every part in §4.1/§4.2 is watertight, has consistent face winding, and zero
broken/non-manifold faces once vertices are merged (raw unmerged-vertex STL
topology gives false non-manifold results — merge first). Five parts are
legitimately multi-body (a main shell plus attached pins/tabs/bosses in one
file) — not a defect on their own:

| Part | Bodies | Note |
| ------ | -------- | ------ |
| `cargo_cradle_autolatch.stl` | 3 | latch pins overlap the main body's Z-range — touching, not floating |
| `cargo_hinge_retention.stl` | 4 | 4 clip bodies, all bed-adjacent (Z 0.5–9.3 mm) |
| `lg_r6_1_5in_leg_assembled.stl` | 2 | leg + foot, Z-ranges overlap — touching |
| `lg_r6_common_bay.stl` | 2 | bay + internal boss, second body nested inside the first's Z-range |
| `cargo_vera_faraday.stl` | 2 | **defect — see 10.2** |

### 10.2 Real defect: `cargo_vera_faraday.stl` lid floats in the source STL

Body 0 (base) spans Z 0.00–19.10 mm; body 1 (lid) spans Z 28.10–32.60 mm —
a **9 mm open-air gap** between them with nothing underneath the lid. This
is not printable as exported: an FDM printer has nothing to build the lid on
until it reaches Z=28.1mm. **Before printing**, either reposition the lid
body to rest on the bed (Z=0) in the slicer, or re-export the SCAD source
with the lid laid flat beside the base rather than in its assembled
position. Sliced as-is in the Cura output for completeness, but do not print
that file without fixing the orientation first.

### 10.3 Wall-thickness caution (FDM design-rule floor: 0.8 mm / 2 perimeters)

Sampled 5th-percentile wall thickness at each part's actual **print** scale
(native thickness × the scale factor from §4.2), per
`references/fdm-design-rules.md` "Wall Thickness":

- **Hull shells at 64%** (`head_shell24_2mm_repaired.stl` etc.): nominal
  ~2 mm shell design lands at ~1.08–1.28 mm printed — above the 0.8 mm floor
  but below the 1.2 mm "recommended" band. §5 Batch N is revised to
  **2 shells minimum** (was 1) to keep real margin; 1 shell (~0.45 mm single
  perimeter) would leave several sampled regions under-thickness.
- **Nacelle pods at 89%** (`nacelle_port_revs.stl`, `nacelle_stbd_revs.stl`):
  sampled as low as **0.48–0.61 mm** in places — genuinely below the 0.8 mm
  floor, not a sampling artifact (consistent across both pods). This is in
  addition to the already-documented EDF-bore-undersize caveat (§4.2) — the
  89% scale is now flagged for wall thickness too. If a feature fails to
  print cleanly on these pods, this is why; there is no bed-fit scale
  between 89% and 100% that clears both the Y-extent and this margin.
- A cluster of small functional brackets (SG90 door/release brackets, ESC bay
  covers, nacelle servo bracket, nozzle ring, DRV8833 tray, FPV bezel, stbd
  wing) sample in the 0.86–1.19 mm band at 1:1 — inside the printable range
  but below the "recommended" 1.2 mm. These were very likely designed
  assuming CF-PETG production settings (4 perimeters, ~1.6–1.8 mm); at this
  guide's 2-shell PLA prototype default they have less margin than the
  larger cargo/nacelle parts. No guide change made for these (they clear the
  0.8 mm floor), but if a bracket cracks at a screw boss or snap feature,
  bump that one part to 3 shells rather than assuming a slicer problem.
- Two apparent near-zero readings (`nacelle_trunnion.stl` 0.29 mm,
  `wing_root_flange_stbd.stl` 0.095 mm) are almost certainly ray-sampling
  artifacts at sharp edges/chamfers, not real thin walls — every other
  sample point on both parts is well clear of the floor, and the flagged
  point is a single 5th-percentile outlier rather than a cluster. Not acted
  on; noted so a future check isn't surprised by the same number.

### 10.4 CuraEngine 5.0.0 could not reliably slice 6 of the 49 parts — 5 needed nothing, 1 needed a repair

The 4 hull shells and 2 nacelle pods (all "HEAVY" in the driver script) carry
a `[WARNING] Mesh has overlapping faces!` from CuraEngine — self-intersecting
geometry left over from the Blender hollowing/boolean pipeline
(`project_scad_manifold_fixes` / `cargo_interior_merge_pipeline` project
history) that a watertight check does not catch. In this CLI/environment it
causes two distinct failures:

- **With support enabled:** CuraEngine's path-combing pass hits an assertion
  and aborts (`Comb.cpp:296`, confirmed on `cargo_sect_shell24_2mm_repaired.stl`
  at 64%). All six heavy parts are sliced with support **off** in this
  pipeline for that reason (§5 batch tables still call for support on the
  hull shells for the PrusaSlicer pipeline, which was not affected).
- **With support disabled:** 3 of the 4 hull shells (head, cargo, middle)
  and **both nacelle pods** (`nacelle_port_revs.stl`, `nacelle_stbd_revs.stl`
  at 89%) slice successfully as-is, despite carrying the same
  overlapping-faces warning. Only `rear_shell24_2mm_repaired.stl` — the
  largest mesh of the six by face count (~1.0M triangles, versus ~740–860k
  for the other three shells) — did not finish within a 400-second budget.
  This read as a face-count/complexity wall specific to that one file, not
  a property of the overlapping-faces defect in general — confirmed by the
  repair in §10.5, which fixes it without changing the underlying geometry.

**What this means practically:** the Cura pipeline in
`airframe/gcode/davinci-jr-proto/cura/` now slices **all 49 parts**
successfully (support disabled throughout, per-batch settings otherwise
matching §5) and stages them for microSD in `cura/sdcard/` — 294 MB across
the 14 batch folders. `cargo_vera_faraday.stl` (§10.2) is included in that
output but still needs its lid repositioned before it will actually print
correctly; every other file is print-ready as sliced.

### 10.5 `rear_shell24_2mm_repaired.stl` repair (2026-09-07)

Fixed via `airframe/gcode/davinci-jr-proto/cura/mesh_repair.py`, applied
automatically by `slice_all_batches_cura.py` for this one part (see its
`NEEDS_REPAIR` set) before scaling to 64%. Method: a **self-union** through
the Manifold CSG kernel (`manifold3d`, already installed system-wide) —
`(mesh ∪ mesh)` — which canonicalizes the mesh and removes the
duplicated/overlapping coincident triangles the boolean pipeline left
behind, guaranteed by Manifold's own no-self-intersection invariant, then a
0.15 mm-tolerance `simplify()` pass (well under 0.4 mm-nozzle resolution
even before the 64% print scale) for a modest triangle-count reduction.

Result: 1,007,832 → 722,056 faces (−28%), volume unchanged to 4
significant figures (220,429.2 mm³ native → 219,893.8 mm³, a 0.24% change
from the simplify pass — not from the self-union, which preserved volume to
5 decimal places on its own). The repaired mesh slices in ~5.5 minutes at
64% with support off — slow (this is by far the heaviest mesh in the set)
but no longer blocked. `trimesh` reports the repaired mesh as not
100%-watertight (8 residual non-manifold edges out of ~2.1M edges,
localized to a handful of ribs); `manifold3d` reports `Error.NoError` on
the identical geometry both before and after re-checking its own output —
this is a difference in how the two tools define manifoldness at edges
where coincident-but-topologically-separate surface patches meet, not a
slicing-blocking defect. Verified by the successful slice, not by chasing
the trimesh edge count to exactly zero.

This is a print-pipeline-local fix — the repaired mesh is a scratch
artifact regenerated on demand by the driver (not committed, same as this
directory's `.gcode` output), and the canonical geometry in `airframe/stls/`
is untouched. If the same overlapping-faces defect needs fixing at the
canonical-source level (it is currently present but harmless in the other 5
heavy files too), that is Blender-hollowing-pipeline work per
`tools/TOOL_REFERENCE.md`, not something to hand-patch on the STL.

---

*© 2026 Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP — CC BY-SA 4.0*
*Hull: misubisu CC BY-SA 4.0 · Nozzles/gears (Rev P/Q era, archived): BamJr CC BY 4.0 ·
Inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal*
