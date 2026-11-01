# Serenity UAV — SLS Print Orientation, Every Part (SLS 380)

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-11-01
**Author:** Steve Griffing, PE(CSE) (Stab-Rabbit-coding). Analysis by Claude
Opus 5.5 (Anthropic) under the author's direction.
**Source of truth:** `tools/sls_print_orientation.py` →
`docs/sls-study/sls_print_orientation.json`. The part list below is generated
from that JSON. Edit the tool, not this list.
**WBS:** §0.13

> [!WARNING]
> **ENGINEERING REVIEW REQUIRED.** Parts marked confidence **V** have a frame
> or load path that the repo sources don't confirm. Those parts shall be
> checked before the build is released to 3D Systems.

## 1. Why orientation matters for PA CF

DuraForm PA CF publishes only XY (in-plane) properties [REF-MAT-015]. A
fiber-filled SLS part is weakest across its layers, so the sizing tools carry
an ASSUMED 0.5 knockdown on build-Z strength (`tools/sls_materials.py`). Every
part below is oriented so its most critical tensile or bending stress lies in
the machine X–Y plane. Where that holds, the knockdown doesn't govern that
load. PA11 [REF-MAT-016] is near-isotropic, so the gear foot is oriented for
surface finish.

## 2. Rules

- **R-PLATE:** plates and panels in bending. The plate normal goes to build Z,
  so the bending stress runs in-plane through every layer.
- **R-RING:** rings, sleeves, gears and revolved ducts. The axis of revolution
  goes to build Z. Hoop stress and tooth-root bending stay in-plane, and round
  bores and bearing seats aren't stair-stepped.
- **R-BEAM:** beams, shafts, cantilevers, and hull shells in longitudinal
  bending. The span axis stays in-plane, and the least-loaded cross axis goes
  to build Z.

Rotation about build Z doesn't change strength. The tool lays the two
in-plane axes on machine X/Y in whichever way fits the 15 × 13 in
(381.0 × 330.2 mm) platform, with an 18 in (457.2 mm) build height (SLS 380,
owner 2026-11-01; [REF-MFG-001 p. 17]). Hull-frame axes follow datum R2:
X = lateral, Y = longitudinal, Z = vertical. "STL X→Y" means the part's X
axis lies along the machine's Y axis.

Confidence levels:

- **H:** the load path and geometry are documented in the repo.
- **M:** the load path is inferred from the part's function.
- **V:** verify before release.

## 3. Result

90 printed parts, port and starboard, from bow to stern: 89 fit the SLS 380
in their strength orientation, and 1 conflicts.

**Conflict: `head_cargo_shell24_2mm_merged.stl`.** This part is 17.1 in
(434.7 mm) long. It fits only standing on end (build Z = STL Y). That puts
fuselage bending stress straight across the layers, on the full 0.5
knockdown. **Recommendation:** for SLS, build the two-section hull as the
separate `head_shell24_2mm_repaired` and `cargo_sect_shell24_2mm_repaired`
shells, joined by `head_cargo_splice_collar`. Each fits lying down, with Y in
the build plane. If the merged shell is kept, its longitudinal design
allowable shall be the knocked-down value.

Hull-frame copies of the gear bays (`lg_r6_3_0in_bay_*.stl` without
`_print`) aren't print files and are excluded. Build the `_print` files.

## 4. Per-part orientation

### Bow and head

- **`bow_sensor_faceplate.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 28 × 16 × 2 mm on the machine. Critical: panel bending (handling).
  R-PLATE.
- **`bow_sensor_bay_insert.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 30 × 20 × 18 mm on the machine. Critical: sensor mount bending.
  R-PLATE: base flange flat.
- **`head_shell24.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 130 × 235 × 140 mm on the machine. Critical: fuselage vertical bending
  -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane, hull vertical -> Z;
  ring frames and webs stand vertical so their in-plane bending is in X-Y too.
- **`head_shell24_2mm_repaired.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 129 × 233 × 140 mm on the machine. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`head_cell_rail.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 52 × 91 × 64 mm on the machine. Critical: fwd/aft crash load into
  longitudinal webs (Y). R-BEAM: webs run along Y, stand vertical; ceiling
  bending in X-Y (tools/gen_head_cell_rail.py).
- **`head_cell_sled.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 39 × 133 × 36 mm on the machine. Critical: floor bending under cell,
  fwd/aft crash (Y). R-PLATE.
- **`head_cell_catch.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 30 × 20 × 7 mm on the machine. Critical: leaf-spring bending along X
  (LEAF_T is Z). R-PLATE: leaf strain in plane, 0.5 % << 3.8 %.
- **`twin_pack_tray.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 74 × 124 × 46 mm on the machine. Critical: ceiling + side-wall bending
  under packs. R-BEAM.
- **`twin_pack_sled.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 34 × 123 × 8 mm on the machine. Critical: sled floor bending. R-PLATE.
- **`twin_pack_gate.stl`** (PA CF, confidence M): build Z = STL Y (X->X Z->Y
  Y->Z); 70 × 12 × 4 mm on the machine. Critical: gate plate bending under pack
  fwd load. R-PLATE: normal is Y (4 mm).
- **`head_cargo_splice_collar.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 114 × 18 × 78 mm on the machine. Critical: splice moment ->
  Y tension at crown/keel. R-BEAM: same frame as hull so crown/keel Y stress is
  in plane.
- **`head_cargo_shell24_2mm_merged.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 194 × 435 × 202 mm on the machine. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too. **CONFLICT:** does not fit the SLS 380 in the strength
  orientation; fits only with build Z = STL Y.

### Cargo section

- **`cargo_sect_shell24_2mm_repaired.stl`** (PA CF, confidence H): build Z = STL
  Z (X->X Y->Y Z->Z); 194 × 198 × 163 mm on the machine. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`cargo_sect_shell24_repaired.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 194 × 204 × 163 mm on the machine. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`battery_tray.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 154 × 52 × 62 mm on the machine. Critical: battery inertia fwd/aft (Y)
  and vertical g. R-BEAM.
- **`battery_cradle.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 55 × 147 × 43 mm on the machine. Critical: inverted-U cradle bending
  under battery g. R-BEAM: U legs vertical, span X in plane.
- **`cargo_cradle_autolatch.stl`** (PA CF, confidence V): build Z = STL Z (X->X
  Y->Y Z->Z); 110 × 80 × 72 mm on the machine. Critical: payload hook load,
  vertical. R-BEAM.
- **`cargo_door_port.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 56 × 106 × 12 mm on the machine. Critical: door panel bending (air
  load). R-PLATE.
- **`cargo_door_stbd.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 50 × 106 × 11 mm on the machine. Critical: door panel bending (air
  load). R-PLATE.
- **`cargo_hinge_retention.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 97 × 132 × 9 mm on the machine. Critical: hinge-pin retention
  plate bending. R-PLATE.
- **`door_latch_crank_port.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 16 × 21 × 8 mm on the machine. Critical: crank arm bending about
  pivot. R-PLATE: arm in plane.
- **`door_latch_crank_stbd.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 10 × 10 × 8 mm on the machine. Critical: crank arm bending about
  pivot. R-PLATE: arm in plane.
- **`door_latch_bracket_port.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 20 × 24 × 13 mm on the machine. Critical: pivot-boss bearing +
  base bending. R-PLATE.
- **`door_latch_bracket_stbd.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 15 × 12 × 7 mm on the machine. Critical: pivot-boss bearing + base
  bending. R-PLATE.
- **`door_horn.stl`** (PA CF, confidence M): build Z = STL Y (X->X Z->Y Y->Z);
  11 × 14 × 6 mm on the machine. Critical: horn arm bending (servo torque).
  R-PLATE: thinnest axis Y.
- **`cargo_door_servo_bracket.stl`** (PA CF, confidence M): build Z = STL Z
  (X->X Y->Y Z->Z); 44 × 28 × 5 mm on the machine. Critical: servo-ear bending.
  R-PLATE.
- **`cargo_release_servo_bracket.stl`** (PA CF, confidence M): build Z = STL Z
  (X->X Y->Y Z->Z); 44 × 28 × 5 mm on the machine. Critical: servo-ear bending.
  R-PLATE.
- **`cargo_drv8833_tray.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 36 × 33 × 6 mm on the machine. Critical: board tray, light. R-PLATE.
- **`gateway_door_tray.stl`** (PA CF, confidence V): build Z = STL Y (X->X Z->Y
  Y->Z); 52 × 34 × 15 mm on the machine. Critical: board tray, light. R-PLATE:
  normal is Y (15 mm).
- **`chin_node_shelf.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 84 × 54 × 6 mm on the machine. Critical: shelf bending under node.
  R-PLATE.
- **`cargo_fpv_bezel.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 29 × 29 × 2 mm on the machine. Critical: cosmetic / light. R-PLATE.
- **`cargo_gps_retention_ring.stl`** (PA CF, confidence M): build Z = STL Z
  (X->X Y->Y Z->Z); 50 × 50 × 2 mm on the machine. Critical: ring hoop. R-RING.
- **`cargo_vera_faraday.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 77 × 71 × 33 mm on the machine. Critical: enclosure, light. R-PLATE:
  base flat.
- **`cargo_winch_motor_mount.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 36 × 28 × 15 mm on the machine. Critical: motor torque reaction in
  base. R-PLATE.
- **`cargo_winch_spool.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 26 × 26 × 22 mm on the machine. Critical: line tension -> drum hoop +
  flange bending. R-RING: drum axis Z.
- **`tilt_actuator_bracket_port.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 95 × 63 × 28 mm on the machine. Critical: worm thrust +
  wheel reaction in bracket plate (Y-Z). R-PLATE: plate normal X (28 mm).
- **`tilt_actuator_bracket_stbd.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 95 × 63 × 28 mm on the machine. Critical: worm thrust +
  wheel reaction in bracket plate (Y-Z). R-PLATE: plate normal X (28 mm).
- **`tilt_actuator_wheel.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 42 × 42 × 13 mm on the machine. Critical: worm-wheel tooth-root
  bending. R-RING: wheel axis X (13 mm face).
- **`tilt_actuator_worm.stl`** (PA CF, confidence M): build Z = STL X (Y->X Z->Y
  X->Z); 17 × 28 × 28 mm on the machine. Critical: thread-root shear along the
  worm axis (Y) + shaft torsion. R-BEAM: worm axis Y stays in plane.
- **`tilt_brake_guide.stl`** (PA CF, confidence V): build Z = STL Z (X->X Y->Y
  Z->Z); 15 × 17 × 26 mm on the machine. Critical: brake-pin bore hoop + side
  load. R-RING: bore axis Z.
- **`tilt_brake_guide_stbd.stl`** (PA CF, confidence V): build Z = STL Z (X->X
  Y->Y Z->Z); 15 × 17 × 26 mm on the machine. Critical: brake-pin bore hoop +
  side load. R-RING: bore axis Z.
- **`inara_access_cover.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 46 × 66 × 5 mm on the machine. Critical: cover panel bending. R-PLATE.
- **`river_access_cover.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 46 × 64 × 5 mm on the machine. Critical: cover panel bending. R-PLATE.
- **`belly_panel.stl`** (PA CF, confidence V): build Z = STL Y (X->X Z->Y Y->Z);
  160 × 65 × 4 mm on the machine. Critical: panel bending. R-PLATE: normal is Y
  (3.5 mm).
- **`cargo_middle_splice_collar.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 126 × 18 × 128 mm on the machine. Critical: splice moment ->
  Y tension at crown/keel. R-BEAM: same frame as hull.
- **`wing_root_flange_port.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 60 × 80 × 26 mm on the machine. Critical: wing root moment ->
  flange plate bending (Y-Z plane). R-PLATE: flange normal X (26 mm).
- **`wing_root_flange_stbd.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 60 × 80 × 26 mm on the machine. Critical: wing root moment ->
  flange plate bending (Y-Z plane). R-PLATE: flange normal X (26 mm).

### Middle and rear

- **`middle_shell24_2mm_repaired.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 177 × 71 × 165 mm on the machine. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`middle_canonical_shell24.stl`** (PA CF, confidence V): build Z = STL Z
  (X->X Y->Y Z->Z); 226 × 165 × 73 mm on the machine. Critical: fuselage bending
  (frame not confirmed). R-BEAM.
- **`middle_canonical_edf_intake.stl`** (PA CF, confidence V): build Z = STL Z
  (X->X Y->Y Z->Z); 226 × 165 × 73 mm on the machine. Critical: intake duct,
  light. R-BEAM.
- **`middle_rear_splice_collar.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 114 × 18 × 119 mm on the machine. Critical: splice moment ->
  Y tension at crown/keel. R-BEAM: same frame as hull.
- **`rear_shell24_2mm_repaired.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 141 × 180 × 158 mm on the machine. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`dorsal_antenna_fin.stl`** (PA CF, confidence M): build Z = STL Y (X->X Z->Y
  Y->Z); 20 × 35 × 4 mm on the machine. Critical: fin root bending (side gust).
  R-PLATE: normal is Y (4 mm).

### Landing gear

- **`lg_r6_3_0in_leg_frame.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 98 × 128 × 16 mm on the machine. Critical: leg frame in-plane
  bending (strike). R-PLATE: frame plane X-Y, 16 mm thick.
- **`lg_r6_3_0in_leg_frame_fore.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 103 × 124 × 16 mm on the machine. Critical: leg frame
  in-plane bending (strike). R-PLATE.
- **`lg_r6_1_5in_leg_frame.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 96 × 79 × 16 mm on the machine. Critical: bench/handling article.
  R-PLATE.
- **`lg_r6_common_foot.stl`** (PA11, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 68 × 56 × 10 mm on the machine. Critical: ground strike; PA11
  isotropic. sole flat for finish.
- **`lg_r6_3_0in_bay_aft-port_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 76 × 51 mm on the machine. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_3_0in_bay_aft-stbd_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 76 × 51 mm on the machine. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_3_0in_bay_fore-port_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 75 × 49 mm on the machine. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_3_0in_bay_fore-stbd_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 75 × 49 mm on the machine. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_common_bay.stl`** (PA CF, confidence V): build Z = STL X (Y->X Z->Y
  X->Z); 54 × 78 × 33 mm on the machine. Critical: leg side-load bending along
  the socket axis (Z). R-BEAM: socket axis in plane.
- **`lg_a1b_housing_fore-port.stl`** (PA CF, confidence V): build Z = STL Y
  (X->X Z->Y Y->Z); 56 × 70 × 37 mm on the machine. Critical: balanced-couple
  housing; metal carries the couple. R-BEAM: long axis Z in plane.
- **`lg_a1b_housing_fore-stbd.stl`** (PA CF, confidence V): build Z = STL Y
  (X->X Z->Y Y->Z); 56 × 70 × 37 mm on the machine. Critical: balanced-couple
  housing; metal carries the couple. R-BEAM: long axis Z in plane.

### Wings

- **`wing_port_s1223_revo.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 96 × 129 × 33 mm on the machine. Critical: spanwise bending (CF
  spar is primary). R-PLATE: airfoil thickness Z; span + chord in plane.
- **`wing_stbd_s1223_revo.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 96 × 129 × 33 mm on the machine. Critical: spanwise bending (CF
  spar is primary). R-PLATE: airfoil thickness Z; span + chord in plane.
- **`wing_tilt_pinion_port.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 13 × 13 × 10 mm on the machine. Critical: 14T pinion tooth-root
  bending. R-RING: gear axis X.
- **`wing_tilt_pinion_stbd.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 13 × 13 × 10 mm on the machine. Critical: 14T pinion tooth-root
  bending. R-RING: gear axis X.

### Nacelles, port and starboard

- **`nacelle_port_64mm.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 95 × 194 × 99 mm on the machine. Critical: pod bending about trunnion
  -> axial (Y) duct stress. R-BEAM: duct axis Y in plane.
- **`nacelle_stbd_64mm.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 95 × 194 × 99 mm on the machine. Critical: pod bending about trunnion
  -> axial (Y) duct stress. R-BEAM: duct axis Y in plane.
- **`nacelle_port_revs.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 76 × 167 × 79 mm on the machine. Critical: legacy 50 mm pod. R-BEAM:
  duct axis Y in plane.
- **`nacelle_stbd_revs.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 76 × 167 × 78 mm on the machine. Critical: legacy 50 mm pod. R-BEAM:
  duct axis Y in plane.
- **`eng_left_shell24_50mm_repaired.stl`** (PA CF, confidence M): build Z = STL
  X (Y->X Z->Y X->Z); 83 × 185 × 75 mm on the machine. Critical: legacy 50 mm
  pod, duct axis Z in this file. R-BEAM: duct axis in plane.
- **`eng_right_shell24_50mm_repaired.stl`** (PA CF, confidence M): build Z = STL
  X (Y->X Z->Y X->Z); 83 × 185 × 75 mm on the machine. Critical: legacy 50 mm
  pod, duct axis Z in this file. R-BEAM: duct axis in plane.
- **`nacelle_trunnion_64mm_port.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 54 × 50 × 18 mm on the machine. Critical: 2 x 6804 bearing
  seat (Ø32 H7) hoop + barrel-to-flange bending. R-RING: bearing axis X -> Z
  keeps the H7 bore round; flange plate in plane.
- **`nacelle_trunnion_64mm_stbd.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 54 × 50 × 18 mm on the machine. Critical: 2 x 6804 bearing
  seat (Ø32 H7) hoop + barrel-to-flange bending. R-RING: bearing axis X -> Z
  keeps the H7 bore round; flange plate in plane.
- **`nacelle_trunnion.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 50 × 50 × 12 mm on the machine. Critical: legacy 50 mm disc trunnion.
  R-RING.
- **`nacelle_servo_bracket.stl`** (PA CF, confidence V): build Z = STL Z (X->X
  Y->Y Z->Z); 44 × 22 × 18 mm on the machine. Critical: servo-ear bending.
  R-PLATE.
- **`edf_motor_mount_64mm_stage2_stbd.stl`** (PA CF, confidence M): build Z =
  STL Z (X->X Y->Y Z->Z); 69 × 72 × 84 mm on the machine. Critical: motor torque
  and thrust through stator vanes. R-RING: duct axis Z; vanes radial in plane.
- **`edf_stator_sleeve.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 55 × 58 × 32 mm on the machine. Critical: stator vane bending (swirl
  torque), sleeve hoop. R-RING.
- **`edf_aft_spider_sleeve.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 55 × 58 × 44 mm on the machine. Critical: spider arm bending,
  sleeve hoop. R-RING.
- **`nacelle_esc_cover_port_a.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 24 mm on the machine. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_esc_cover_port_b.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 24 mm on the machine. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_esc_cover_stbd_a.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 25 mm on the machine. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_esc_cover_stbd_b.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 25 mm on the machine. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_nozzle_fixed.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 71 × 71 × 48 mm on the machine. Critical: duct hoop + bond-lip
  shear. R-RING.
- **`nacelle_nozzle_throat.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 71 × 71 × 21 mm on the machine. Critical: duct hoop. R-RING.
- **`nacelle_nozzle_ring.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 66 × 66 × 8 mm on the machine. Critical: unison-ring hoop + tooth
  bending. R-RING.
- **`nacelle_nozzle_flap.stl`** (PA CF, confidence M): build Z = STL X (Y->X
  Z->Y X->Z); 23 × 50 × 10 mm on the machine. Critical: flap cantilever bending
  along its 50 mm length (Z). R-BEAM: flap length in plane.
- **`nacelle_nozzle_flap_seal.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 26 × 50 × 9 mm on the machine. Critical: flap cantilever
  bending along its 50 mm length (Z). R-BEAM: flap length in plane.

## 5. Notes for the build order to 3D Systems

- Send each STL with its "build Z = STL …" line. 3D Systems nests parts
  freely about build Z; say so explicitly, and say that build-Z rotation of
  any part shall not be changed.
- PA CF fibers align with the recoater direction, which may favor one
  in-plane axis. No source in hand quantifies this, so it isn't used here.
  Ask 3D Systems for X-vs-Y data on DuraForm PA CF (**requires
  verification**).
- The tallest part in its strength orientation is the middle shell, at
  6.49 in (164.8 mm), well under the 18 in build height. Several shells can
  share one build height-wise.
