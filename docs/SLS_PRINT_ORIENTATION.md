# Serenity UAV — SLS Print Orientation, Every Part (Design Intent)

**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-11-01
**Author:** Steve Griffing, PE(CSE) (Stab-Rabbit-coding). Analysis by Claude
Opus 5.5 (Anthropic) under the author's direction.
**Source of truth:** `tools/sls_print_orientation.py` →
`docs/sls-study/sls_print_orientation.json`. The part list below is generated
from that JSON by the tool. Edit the tool, not this list.
**WBS:** §0.13

> [!WARNING]
> **ENGINEERING REVIEW REQUIRED.** Parts marked confidence **V** have a frame
> or load path that the repo sources don't confirm. Those parts shall be
> checked before the build is released to 3D Systems.

## 0. Decision: final orientation is set with 3D Systems

**Owner decision, 2026-11-01 (Stab-Rabbit-coding):** the owner sets the final
build orientation and machine for every part with 3D Systems before ordering.
The orientations in this document are the **design-intent request** taken to
that conversation. They aren't a release instruction.

- **Machines available at 3D Systems** (owner, 2026-11-01; the same figures
  are on [REF-MFG-001 p. 17]):
  - SLS 380 at 15 × 13 × 18 in (381.0 × 330.2 × 457.2 mm)
  - sPro 140 at 22 × 22 × 18 in (558.8 × 558.8 × 457.2 mm)
  - sPro 230 at 22 × 22 × 30 in (558.8 × 558.8 × 762.0 mm)
- **To ask 3D Systems:**
  - their orientation restrictions on each machine;
  - whether 3D Sprint auto-orients parts ([REF-MFG-001 p. 17]), and how to
    lock an orientation;
  - DuraForm PA CF properties in X, Y and Z (recoater-direction fiber
    alignment);
  - whether bead blast reaches blind heat-set-insert bosses
    ([REF-MFG-001 p. 6]).
- **After the conversation:** record the agreed orientation and machine per
  part in `tools/sls_print_orientation.py` (`ORIENT`, `MACHINES`). Where the
  agreed orientation puts a critical stress across the layers, re-run that
  part's sizing tool with the 0.5 Z knockdown (`tools/sls_materials.py`).

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

These rules apply the guide's one explicit orientation rule, "avoid stair
steps coinciding with the tensile surface" [REF-MFG-001 p. 13], to every
part. Rotation about build Z doesn't change strength. The tool lays the two
in-plane axes on machine X/Y in whichever way fits, and places each part on
the smallest of the three machines that holds it. Hull-frame axes follow
datum R2: X = lateral, Y = longitudinal, Z = vertical. "STL X→Y" means the
part's X axis lies along the machine's Y axis.

Confidence levels:

- **H:** the load path and geometry are documented in the repo.
- **M:** the load path is inferred from the part's function.
- **V:** verify before release.

## 3. Result

79 current printed parts, port and starboard, from bow to stern: 78 fit the
SLS 380 in their strength orientation. One, the hull, needs the sPro 140, and
none conflicts.

**The hull is two sections joined at the cargo/middle collar**
(`docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md` §4):

- **Forward section:** head+cargo, merged in one piece,
  `head_cargo_shell24_2mm_merged.stl` (commit `d92c4f14`, 2026-10-31). It's
  17.1 in (434.7 mm) long. On the SLS 380 it fits only standing on end, which
  would put fuselage bending straight across the layers. On the sPro 140 it
  lies down with Y in the build plane, so **request the sPro 140 for the
  forward section** (§0). Separate head and cargo shells aren't an option,
  because the twin battery tray needs the merged section.
- **Joint:** `cargo_middle_splice_collar.stl`, which stays a separate part.
- **Aft section:** middle+rear in one piece is the planned baseline (plan
  2026-10-31-003, `docs/MASS_AUDIT_MIDDLE_REAR_SECTIONS.md` §4), but **the
  merged STL hasn't been generated yet**. Until it is, the middle shell, the
  rear shell and `middle_rear_splice_collar` are oriented here as they
  stand. Joined, the aft section is about 250 × 177 × 165 mm, so it fits the
  SLS 380 lying down with Y in-plane (a footprint estimate, not yet
  measured).

Parts still on disk but retired are excluded and listed in
`tools/sls_retired_parts.py`, with the decision that retired each one: the
separate head and cargo shells (now inputs to the merge), the head-cargo
collar, the battery cradle, the head-cell rail, sled and catch, the belly
panel and the keel battery tray. Hull-frame copies of the gear bays
(`lg_r6_3_0in_bay_*.stl` without `_print`) aren't print files either. Build
the `_print` files.

## 4. Per-part orientation

### Bow and head

- **`bow_sensor_faceplate.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 28 × 16 × 2 mm on the SLS 380. Critical: panel bending (handling).
  R-PLATE.
- **`bow_sensor_bay_insert.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 30 × 20 × 18 mm on the SLS 380. Critical: sensor mount bending.
  R-PLATE: base flange flat.
- **`twin_pack_tray.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 74 × 124 × 46 mm on the SLS 380. Critical: ceiling + side-wall bending
  under packs. R-BEAM.
- **`twin_pack_sled.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 34 × 123 × 8 mm on the SLS 380. Critical: sled floor bending. R-PLATE.
- **`twin_pack_gate.stl`** (PA CF, confidence M): build Z = STL Y (X->X Z->Y
  Y->Z); 70 × 12 × 4 mm on the SLS 380. Critical: gate plate bending under pack
  fwd load. R-PLATE: normal is Y (4 mm).
- **`head_cargo_shell24_2mm_merged.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 194 × 435 × 202 mm on the sPro 140. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too. **Note:** needs the sPro 140 in its strength
  orientation; on the SLS 380 it fits only with build Z = STL Y.

### Cargo section

- **`cargo_cradle_autolatch.stl`** (PA CF, confidence V): build Z = STL Z (X->X
  Y->Y Z->Z); 110 × 80 × 72 mm on the SLS 380. Critical: payload hook load,
  vertical. R-BEAM.
- **`cargo_door_port.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 56 × 106 × 12 mm on the SLS 380. Critical: door panel bending (air
  load). R-PLATE.
- **`cargo_door_stbd.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 50 × 106 × 11 mm on the SLS 380. Critical: door panel bending (air
  load). R-PLATE.
- **`cargo_hinge_retention.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 97 × 132 × 9 mm on the SLS 380. Critical: hinge-pin retention
  plate bending. R-PLATE.
- **`door_latch_crank_port.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 16 × 21 × 8 mm on the SLS 380. Critical: crank arm bending about
  pivot. R-PLATE: arm in plane.
- **`door_latch_crank_stbd.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 10 × 10 × 8 mm on the SLS 380. Critical: crank arm bending about
  pivot. R-PLATE: arm in plane.
- **`door_latch_bracket_port.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 20 × 24 × 13 mm on the SLS 380. Critical: pivot-boss bearing +
  base bending. R-PLATE.
- **`door_latch_bracket_stbd.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 15 × 12 × 7 mm on the SLS 380. Critical: pivot-boss bearing + base
  bending. R-PLATE.
- **`door_horn.stl`** (PA CF, confidence M): build Z = STL Y (X->X Z->Y Y->Z);
  11 × 14 × 6 mm on the SLS 380. Critical: horn arm bending (servo torque).
  R-PLATE: thinnest axis Y.
- **`cargo_door_servo_bracket.stl`** (PA CF, confidence M): build Z = STL Z
  (X->X Y->Y Z->Z); 44 × 28 × 5 mm on the SLS 380. Critical: servo-ear bending.
  R-PLATE.
- **`cargo_release_servo_bracket.stl`** (PA CF, confidence M): build Z = STL Z
  (X->X Y->Y Z->Z); 44 × 28 × 5 mm on the SLS 380. Critical: servo-ear bending.
  R-PLATE.
- **`cargo_drv8833_tray.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 36 × 33 × 6 mm on the SLS 380. Critical: board tray, light. R-PLATE.
- **`gateway_door_tray.stl`** (PA CF, confidence V): build Z = STL Y (X->X Z->Y
  Y->Z); 52 × 34 × 15 mm on the SLS 380. Critical: board tray, light. R-PLATE:
  normal is Y (15 mm).
- **`chin_node_shelf.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 84 × 54 × 6 mm on the SLS 380. Critical: shelf bending under node.
  R-PLATE.
- **`cargo_fpv_bezel.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 29 × 29 × 2 mm on the SLS 380. Critical: cosmetic / light. R-PLATE.
- **`cargo_gps_retention_ring.stl`** (PA CF, confidence M): build Z = STL Z
  (X->X Y->Y Z->Z); 50 × 50 × 2 mm on the SLS 380. Critical: ring hoop. R-RING.
- **`cargo_vera_faraday.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 77 × 71 × 33 mm on the SLS 380. Critical: enclosure, light. R-PLATE:
  base flat.
- **`cargo_winch_motor_mount.stl`** (PA CF, confidence M): build Z = STL Z (X->X
  Y->Y Z->Z); 36 × 28 × 15 mm on the SLS 380. Critical: motor torque reaction in
  base. R-PLATE.
- **`cargo_winch_spool.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 26 × 26 × 22 mm on the SLS 380. Critical: line tension -> drum hoop +
  flange bending. R-RING: drum axis Z.
- **`tilt_actuator_bracket_port.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 95 × 63 × 28 mm on the SLS 380. Critical: worm thrust +
  wheel reaction in bracket plate (Y-Z). R-PLATE: plate normal X (28 mm).
- **`tilt_actuator_bracket_stbd.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 95 × 63 × 28 mm on the SLS 380. Critical: worm thrust +
  wheel reaction in bracket plate (Y-Z). R-PLATE: plate normal X (28 mm).
- **`tilt_actuator_wheel.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 42 × 42 × 13 mm on the SLS 380. Critical: worm-wheel tooth-root
  bending. R-RING: wheel axis X (13 mm face).
- **`tilt_actuator_worm.stl`** (PA CF, confidence M): build Z = STL X (Y->X Z->Y
  X->Z); 17 × 28 × 28 mm on the SLS 380. Critical: thread-root shear along the
  worm axis (Y) + shaft torsion. R-BEAM: worm axis Y stays in plane.
- **`tilt_brake_guide.stl`** (PA CF, confidence V): build Z = STL Z (X->X Y->Y
  Z->Z); 15 × 17 × 26 mm on the SLS 380. Critical: brake-pin bore hoop + side
  load. R-RING: bore axis Z.
- **`tilt_brake_guide_stbd.stl`** (PA CF, confidence V): build Z = STL Z (X->X
  Y->Y Z->Z); 15 × 17 × 26 mm on the SLS 380. Critical: brake-pin bore hoop +
  side load. R-RING: bore axis Z.
- **`inara_access_cover.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 46 × 66 × 5 mm on the SLS 380. Critical: cover panel bending. R-PLATE.
- **`river_access_cover.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 46 × 64 × 5 mm on the SLS 380. Critical: cover panel bending. R-PLATE.
- **`cargo_middle_splice_collar.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 126 × 18 × 128 mm on the SLS 380. Critical: splice moment ->
  Y tension at crown/keel. R-BEAM: same frame as hull.
- **`wing_root_flange_port.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 60 × 80 × 26 mm on the SLS 380. Critical: wing root moment ->
  flange plate bending (Y-Z plane). R-PLATE: flange normal X (26 mm).
- **`wing_root_flange_stbd.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 60 × 80 × 26 mm on the SLS 380. Critical: wing root moment ->
  flange plate bending (Y-Z plane). R-PLATE: flange normal X (26 mm).

### Middle and rear

- **`middle_shell24_2mm_repaired.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 177 × 71 × 165 mm on the SLS 380. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`middle_canonical_shell24.stl`** (PA CF, confidence V): build Z = STL Z
  (X->X Y->Y Z->Z); 226 × 165 × 73 mm on the SLS 380. Critical: fuselage bending
  (frame not confirmed). R-BEAM.
- **`middle_canonical_edf_intake.stl`** (PA CF, confidence V): build Z = STL Z
  (X->X Y->Y Z->Z); 226 × 165 × 73 mm on the SLS 380. Critical: intake duct,
  light. R-BEAM.
- **`middle_rear_splice_collar.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 114 × 18 × 119 mm on the SLS 380. Critical: splice moment ->
  Y tension at crown/keel. R-BEAM: same frame as hull.
- **`rear_shell24_2mm_repaired.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 141 × 180 × 158 mm on the SLS 380. Critical: fuselage
  vertical bending -> longitudinal (Y) skin stress. R-BEAM: Y and X in plane,
  hull vertical -> Z; ring frames and webs stand vertical so their in-plane
  bending is in X-Y too.
- **`dorsal_antenna_fin.stl`** (PA CF, confidence M): build Z = STL Y (X->X Z->Y
  Y->Z); 20 × 35 × 4 mm on the SLS 380. Critical: fin root bending (side gust).
  R-PLATE: normal is Y (4 mm).

### Landing gear

- **`lg_r6_3_0in_leg_frame.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 98 × 128 × 16 mm on the SLS 380. Critical: leg frame in-plane
  bending (strike). R-PLATE: frame plane X-Y, 16 mm thick.
- **`lg_r6_3_0in_leg_frame_fore.stl`** (PA CF, confidence H): build Z = STL Z
  (X->X Y->Y Z->Z); 103 × 124 × 16 mm on the SLS 380. Critical: leg frame
  in-plane bending (strike). R-PLATE.
- **`lg_r6_1_5in_leg_frame.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 96 × 79 × 16 mm on the SLS 380. Critical: bench/handling article.
  R-PLATE.
- **`lg_r6_common_foot.stl`** (PA11, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 68 × 56 × 10 mm on the SLS 380. Critical: ground strike; PA11
  isotropic. sole flat for finish.
- **`lg_r6_3_0in_bay_aft-port_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 76 × 51 mm on the SLS 380. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_3_0in_bay_aft-stbd_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 76 × 51 mm on the SLS 380. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_3_0in_bay_fore-port_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 75 × 49 mm on the SLS 380. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_3_0in_bay_fore-stbd_print.stl`** (PA CF, confidence V): build Z = STL
  X (Y->X Z->Y X->Z); 54 × 75 × 49 mm on the SLS 380. Critical: leg side-load
  bending along the socket axis (print Z). R-BEAM: socket axis in plane.
- **`lg_r6_common_bay.stl`** (PA CF, confidence V): build Z = STL X (Y->X Z->Y
  X->Z); 54 × 78 × 33 mm on the SLS 380. Critical: leg side-load bending along
  the socket axis (Z). R-BEAM: socket axis in plane.
- **`lg_a1b_housing_fore-port.stl`** (PA CF, confidence V): build Z = STL Y
  (X->X Z->Y Y->Z); 56 × 70 × 37 mm on the SLS 380. Critical: balanced-couple
  housing; metal carries the couple. R-BEAM: long axis Z in plane.
- **`lg_a1b_housing_fore-stbd.stl`** (PA CF, confidence V): build Z = STL Y
  (X->X Z->Y Y->Z); 56 × 70 × 37 mm on the SLS 380. Critical: balanced-couple
  housing; metal carries the couple. R-BEAM: long axis Z in plane.

### Wings

- **`wing_port_s1223_revo.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 96 × 129 × 33 mm on the SLS 380. Critical: spanwise bending (CF
  spar is primary). R-PLATE: airfoil thickness Z; span + chord in plane.
- **`wing_stbd_s1223_revo.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 96 × 129 × 33 mm on the SLS 380. Critical: spanwise bending (CF
  spar is primary). R-PLATE: airfoil thickness Z; span + chord in plane.
- **`wing_tilt_pinion_port.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 13 × 13 × 10 mm on the SLS 380. Critical: 14T pinion tooth-root
  bending. R-RING: gear axis X.
- **`wing_tilt_pinion_stbd.stl`** (PA CF, confidence H): build Z = STL X (Y->X
  Z->Y X->Z); 13 × 13 × 10 mm on the SLS 380. Critical: 14T pinion tooth-root
  bending. R-RING: gear axis X.

### Nacelles, port and starboard

- **`nacelle_port_64mm.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 95 × 194 × 99 mm on the SLS 380. Critical: pod bending about trunnion
  -> axial (Y) duct stress. R-BEAM: duct axis Y in plane.
- **`nacelle_stbd_64mm.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 95 × 194 × 99 mm on the SLS 380. Critical: pod bending about trunnion
  -> axial (Y) duct stress. R-BEAM: duct axis Y in plane.
- **`nacelle_port_revs.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 76 × 167 × 79 mm on the SLS 380. Critical: legacy 50 mm pod. R-BEAM:
  duct axis Y in plane.
- **`nacelle_stbd_revs.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 76 × 167 × 78 mm on the SLS 380. Critical: legacy 50 mm pod. R-BEAM:
  duct axis Y in plane.
- **`eng_left_shell24_50mm_repaired.stl`** (PA CF, confidence M): build Z = STL
  X (Y->X Z->Y X->Z); 83 × 185 × 75 mm on the SLS 380. Critical: legacy 50 mm
  pod, duct axis Z in this file. R-BEAM: duct axis in plane.
- **`eng_right_shell24_50mm_repaired.stl`** (PA CF, confidence M): build Z = STL
  X (Y->X Z->Y X->Z); 83 × 185 × 75 mm on the SLS 380. Critical: legacy 50 mm
  pod, duct axis Z in this file. R-BEAM: duct axis in plane.
- **`nacelle_trunnion_64mm_port.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 54 × 50 × 18 mm on the SLS 380. Critical: 2 x 6804 bearing
  seat (Ø32 H7) hoop + barrel-to-flange bending. R-RING: bearing axis X -> Z
  keeps the H7 bore round; flange plate in plane.
- **`nacelle_trunnion_64mm_stbd.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 54 × 50 × 18 mm on the SLS 380. Critical: 2 x 6804 bearing
  seat (Ø32 H7) hoop + barrel-to-flange bending. R-RING: bearing axis X -> Z
  keeps the H7 bore round; flange plate in plane.
- **`nacelle_trunnion.stl`** (PA CF, confidence M): build Z = STL Z (X->X Y->Y
  Z->Z); 50 × 50 × 12 mm on the SLS 380. Critical: legacy 50 mm disc trunnion.
  R-RING.
- **`nacelle_servo_bracket.stl`** (PA CF, confidence V): build Z = STL Z (X->X
  Y->Y Z->Z); 44 × 22 × 18 mm on the SLS 380. Critical: servo-ear bending.
  R-PLATE.
- **`edf_motor_mount_64mm_stage2_stbd.stl`** (PA CF, confidence M): build Z =
  STL Z (X->X Y->Y Z->Z); 69 × 72 × 84 mm on the SLS 380. Critical: motor torque
  and thrust through stator vanes. R-RING: duct axis Z; vanes radial in plane.
- **`edf_stator_sleeve.stl`** (PA CF, confidence H): build Z = STL Z (X->X Y->Y
  Z->Z); 55 × 58 × 32 mm on the SLS 380. Critical: stator vane bending (swirl
  torque), sleeve hoop. R-RING.
- **`edf_aft_spider_sleeve.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 55 × 58 × 44 mm on the SLS 380. Critical: spider arm bending,
  sleeve hoop. R-RING.
- **`nacelle_esc_cover_port_a.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 24 mm on the SLS 380. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_esc_cover_port_b.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 24 mm on the SLS 380. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_esc_cover_stbd_a.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 25 mm on the SLS 380. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_esc_cover_stbd_b.stl`** (PA CF, confidence M): build Z = STL Y
  (X->X Z->Y Y->Z); 50 × 58 × 25 mm on the SLS 380. Critical: flush cover panel
  bending. R-PLATE: normal Y.
- **`nacelle_nozzle_fixed.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 71 × 71 × 48 mm on the SLS 380. Critical: duct hoop + bond-lip
  shear. R-RING.
- **`nacelle_nozzle_throat.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 71 × 71 × 21 mm on the SLS 380. Critical: duct hoop. R-RING.
- **`nacelle_nozzle_ring.stl`** (PA CF, confidence H): build Z = STL Z (X->X
  Y->Y Z->Z); 66 × 66 × 8 mm on the SLS 380. Critical: unison-ring hoop + tooth
  bending. R-RING.
- **`nacelle_nozzle_flap.stl`** (PA CF, confidence M): build Z = STL X (Y->X
  Z->Y X->Z); 23 × 50 × 10 mm on the SLS 380. Critical: flap cantilever bending
  along its 50 mm length (Z). R-BEAM: flap length in plane.
- **`nacelle_nozzle_flap_seal.stl`** (PA CF, confidence M): build Z = STL X
  (Y->X Z->Y X->Z); 26 × 50 × 9 mm on the SLS 380. Critical: flap cantilever
  bending along its 50 mm length (Z). R-BEAM: flap length in plane.

## 5. Notes for the build order to 3D Systems

- Send each STL with its "build Z = STL …" line as the requested
  orientation (§0). Rotation about build Z is free.
- PA CF fibers align with the recoater direction, which may favor one
  in-plane axis. No source in hand quantifies this, so it isn't used here.
  Ask 3D Systems for X-vs-Y data on DuraForm PA CF (**requires
  verification**).
- The tallest part in its strength orientation is the middle shell, at
  6.49 in (164.8 mm), well under the 18 in build height. Several shells can
  share one build height-wise.
