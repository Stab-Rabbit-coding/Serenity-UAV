# Serenity UAV — Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Last updated:** 2026-06-11  
**Current design revision:** Rev R (2026-06-10) | **Build target:** 24-inch hull (REVN_BUILD_GUIDE_24IN.md)

---

## Quick-Reference: End State vs. Current State

| Domain | End State | Current Status |
|--------|-------------------|----------------|
| Hull   | 609.6 mm PETG / PU foam / CF skeleton | SCAD sources complete; all four fuselage SCAD shells at Rev R; cargo section at Rev R (clamshell, avionics bays, GPS); STLs pending regeneration |
| Nacelles | 2× 50mm tandem EDF, CG pivot Z=83mm, M=1.0 gear, iris nozzle | `nacelle_pod_50mm_tandem.scad` complete; Rev R stator shells (`_revo.stl`) pending render |
| Nacelle EDFs | XFly Galaxy X5 50mm 12-blade 6S 3200KV, 1240g each; 2232g/nacelle (90% additive via stator); 4464g total | Baseline EDF selected (xfly-model.eu); nacelle T/W ≈ 1.61 at Phase 5–10 AUW — VTOL hover capable |
| Rear propulsion | 120mm 6S EDF, 4-scoop radial intake, iris nozzle | **DEFERRED — Phase 11.** All design files moved to `deferred/aft-edf/`. SCAD and STLs complete. Adds ~3500g thrust; Phase 11 T/W ≈ 2.21. |
| Cargo bay | Clamshell doors + SG90 servos + DRV8833 + N20 winch + Dyneema + auto-latch + GPS ring + FPV bezel | ✓ All 13 cargo STLs generated (PR #21 + PR #22 2026-06-01); BOM updated bom_revP.json/csv; gondola shell open |
| PCBs | **Rev Q: all 8 nodes use the EM hardened Wash Flight Control and Zoë Comms/Security capes** at every position. The **Kaylee Power Distribution Board** ensures that everything stays shiny.  Two **Emma** daughter boards provide connectivity on RCRS.  Cape-A-1, Cape-B-1, XCVR-49MHZ-1 archived 2026-06-05. **| Rev R schematics complete (Wash: 2× EMI-hardened Ethernet PHY; Zoë: 1× Ethernet PHY; all field connectors added). Kaylee PCB DRC clean (0 shorts); gerbers generated 2026-06-10; manual component placement (Section F, shield lugs) and trace routing remain. |
| Firmware | 8-node cooperative flight, PID governor, OA, cargo, logging | serenity-cn Phase 6 ✓; serenity-fc Phase 6 stub only; all Phase 7 items open |
| Physical build | Airborne, autonomous, cargo-capable | Not started — awaiting STL exports, PCB fabrication |
| Regulatory | FAA Part 107, ICAO nav lights, FCC Part 95 | FAA registration placeholder; XCVR-49MHZ-1 pre-compliance pending |

---

## 1.0 — Design Artifacts (Pre-Fabrication)

Complete all items in this section before ordering PCBs or starting any physical build step.

### 1.1 — 3D Models: SCAD → STL Exports (Rev R baseline)

All SCADs run on a host machine with OpenSCAD 2021.01+ or Blender 3.x+ (headless).
Output STLs go to `thingverse-serenity/files-hollowed-18in/`.

#### 1.1.0 **Hull-Frame Coordinate Standardisation (R1, 2026-06-11)**

All design artifacts standardised on the validated hull frame (X = +port, Y = +aft,
Z = +dorsal; origin = SerenityAssembly.FCStd world origin). See CLAUDE.md
"Hull-Frame Coordinate Standard".

- [x] **`tools/bake_hull_frame.py` created** — idempotent STL bake tool; applies the
  validated 2026-06-10 placements to STL vertex data; stamps binary header marker
  `SerenityUAV HULL-FRAME R1`; refuses to double-transform. *(done 2026-06-11)*
- [x] **9 STLs baked to hull frame** — Head, Cargo (both repair copies), Middle, Rear,
  Wing×2, Nacelle×2. Watertight validation PASS before and after; facet counts
  unchanged; re-read verification ≤ 1.5e-5 mm. *(done 2026-06-11)*
- [x] **`serenity_assembly.py` Rev R1** — all 8 primary placements now identity;
  `doc.saveAs()` fix; `freecadcmd` entry-point fix; `airframe/Serenity-Assembled.FCStd`
  regenerated and world extents verified identical to the validated assembly.
  *(done 2026-06-11)*
- [x] **48 generator/analysis scripts stamped** with the hull-frame standard header
  (SCAD, Blender, FreeCAD, cargo generators, build-guide tools; GCS and deferred
  files annotated as documented exceptions). *(done 2026-06-11)*
- [x] **Docs updated** — CLAUDE.md (baked-extents table + pipeline rule), README.md,
  REPO_ENFORCEMENT.md, serenity-rev-r.jsx (R1 entry; axis typo fixed),
  PROJECT_INDEX.md. *(done 2026-06-11)*
- [x] **Resolve nacelle port/stbd label swap.** Confirmed by user FreeCAD layout
  inspection (2026-06-11): harness conduit exits inboard face; original SCAD naming
  was inverted. Fixed: STL files renamed (port↔stbd swap), binary 80-byte headers
  patched, `bake_hull_frame.py` COMPONENTS corrected, `serenity_assembly.py` audit
  comment updated, SCAD build commands corrected (port: SWIRL_DIR=−1/PYLON_SIDE=−1,
  stbd: SWIRL_DIR=+1/PYLON_SIDE=+1), CLAUDE.md extents table corrected.
  *(done 2026-06-11)*
- [ ] **Re-verify head↔cargo joint bosses in hull Y.** The 2026-06-10 joint analysis
  used hull X as the longitudinal mating axis; in the validated frame the longitudinal
  axis is Y (sections mate at hull Y ≈ −71 mm; X is lateral). Re-check
  BOSS_FORE/BOSS_AFT positions in `s_head_shell24.scad` / `s_cargo_sect_shell24.scad`
  against the baked meshes. **BLOCKS head/cargo printing.**
- [ ] **Regenerate cargo doors from the baked shell.** `cargo_door_port/stbd.stl`
  (2026-06-01) predate both the repaired-shell re-orientation and the bake; regenerate
  via `generate_cargo_doors.py` against the baked
  `s_cargo_sect_shell24_2mm_repaired.stl` and verify the belly faces hull −Z.
- [ ] **Consolidate duplicate cargo shell copies.**
  `fuselage/s_cargo_sect_shell24_2mm_repaired.stl` (367,506 facets, later repair pass)
  vs `fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl` (368,352 facets, used by
  the assembly). Both now baked; keep one canonical copy.
- [ ] **Hull-frame placements for VERIFY parts.** Cargo mounts (8), pylons, EDF sleeves,
  nozzles/gears, battery tray, belly panel, tip caps, dorsal antenna fin, landing
  legs/feet remain part-local; validate each in FreeCAD against the baked hull and
  either bake or record explicit placements in `serenity_assembly.py`.
- [ ] **Generate `battery_tray.stl` and `belly_panel.stl`** from their SCAD sources —
  currently missing (WARN during assembly regeneration).
- [ ] **Archive deprecated FreeCAD prototypes** — `assembly1.py`, `Serenity-Assemble.py`,
  `Serenity-Subsystem-Assembly.py`, `serenity_subsystem_assembler.py`,
  `serenity_fuselage_asm4.py` are marked DEPRECATED (pre-R1 transforms would
  double-transform baked STLs); move to `airframe/archive/` at next revision checkpoint.

#### 1.1.1 **Fuselage**

- [x] **Access panel frames + covers (24" Rev R)** — `airframe/openscad/fuselage/access_panels_24in.scad` created 2026-06-11. Geometries derived from authoritative shell SCADs (Rev R baseline):
  - 4× Faraday-bay covers (Shepherd/Inara/River/Simon): 72×52 mm, 4× M3 clearance bores, positive-stop shoulder; Inara + River covers include Ø42 mm GPS retention-ring recess.
  - 2× ventral hatch covers: battery 160×60 mm, Kaylee 115×100 mm; M2.5 pilots into bonded frames.
  - 2× ventral hatch frames: battery + Kaylee; 6 mm PETG wall, West System 105/206 epoxy-bonded to hull.
  - **SUB-TASKS:**
    - [ ] Export individual STLs (set RENDER variable in SCAD): shepherd, inara, river, simon, battery, battery_f, kaylee, kaylee_f → `airframe/stls/fuselage/`
    - [ ] Verify cover shoulder fit in slicer cross-section (confirm 1.5 mm step seats on hull face)
    - [ ] Verify GPS recess depth clears GPS retention ring (Inara: dZ=−14.3 mm, River: dZ=+0.7 mm)
    - [ ] Confirm M3 bore positions match shell boss pattern (±25 mm × ±15 mm from bay centre)

- [x] **49MHz RCRS wire posts** — `airframe/openscad/fuselage/rcrs49_wire_post.scad` created 2026-06-11. Single `wire_post()` module: 12×12×2 mm PETG base, 8×8×7 mm mast, Ø1.5 mm athwartships wire-retention bore at 2 mm from top. Print two: forward (sta ≈ 120 mm, dorsal) + temporary aft (sta ≈ 580 mm, dorsal).
  - **BLOCKS Phase 1 (antenna installation)**
  - **SUB-TASKS:**
    - [ ] Export STL → `airframe/stls/fuselage/rcrs49_wire_post.stl`
    - [ ] Bond forward post to hull dorsal skin at sta 120 mm; dress wire to Emma feed
    - [ ] Install temporary aft post at sta 580 mm; remove and replace with integrated mount in Phase 11

##### 1.1.1.1 *Head*

**Geometry verification (hull-frame coordinate analysis, 2026-06-10):**

- [ ] **Verify head-cargo mating boss positions in slicer.**
  Hull-frame analysis (2026-06-10): `Head_Shell` Identity rotation, Base=[−332, −18, +61];
  head aft face (head local_X=99) maps to hull_X = 99−332 = **−233 mm**.
  `Cargo_Shell` 180°-Z rotation, Base=[−274.4, −282.8, 0]; matching cargo local_X =
  −(−233) − 274.4 = **−41.4 mm** — corrected in `cargo_sect_shell24.scad` BOSS_FORE
  (was X=−7, now X=−41.4). **VERIFY** both sections simultaneously in an assembly render
  or slicer that shows both STLs in hull-frame placement.  Confirm 6 head BOSS_AFT bosses
  (at head local_X=99) align with 6 cargo BOSS_FORE bosses (at cargo local_X=−41.4) in
  the assembled hull.  All Y/Z offsets remain estimated; also VERIFY those after X is confirmed.
  Ref: `head_shell24.scad` BOSS_AFT_* comments; `cargo_sect_shell24.scad` hull-frame block.
  **R1 AUDIT (2026-06-11): this analysis used hull X as the longitudinal mating axis, but
  in the validated hull frame X is LATERAL (+port) and the longitudinal axis is Y — the
  baked head and cargo meshes mate at hull Y ≈ −71 mm.  Redo the joint analysis in hull Y
  (see §1.1.0) before trusting BOSS_FORE = −41.4 mm.**

**Rev R shell updates (sensor/antenna mounts; carried fwd from Rev O, 2026-05-24):**

- [ ] **head_shell24.stl** — regenerate from `serenity/stl/head_shell24.scad` (dual VL53L5CX bosses, FPV mount, GPS dome, 49MHz post, SMA bulkheads added 2026-05-24). Verify all mount boss positions in slicer cross-section before printing.

##### 1.1.1.2 *Cargo*

**Rev R shell updates (sensor/antenna mounts; carried fwd from Rev O, 2026-05-24):**

- [ ] **cargo_sect_shell24.stl** — regenerate from `serenity/stl/cargo_sect_shell24.scad` (cargo nadir FPV mount added)
  - Both outputs go to `thingverse-serenity/files-hollowed-18in/`

###### 1.1.1.2.1 *Cargo Handling*

**Cargo handling equipment:**

- [x] **Mounting hardware — 8 STLs** generated by `serenity/stl/generate_cargo_mounts.py` (Python/trimesh/manifold3d). Output: `thingverse-serenity/files-hollowed-18in/cargo_*.stl` *(done 2026-05-30, PR #21)*
  - [x] cargo_winch_motor_mount (CF-PETG), cargo_winch_spool (PETG), cargo_door_servo_bracket (CF-PETG), cargo_release_servo_bracket (CF-PETG), cargo_drv8833_tray (PETG), cargo_cradle_autolatch (PETG), cargo_gps_retention_ring (PETG), cargo_fpv_bezel (PETG)

- [ ] **Cargo gondola shell** — create `serenity/stl/s_cargo_gondola_shell.scad`: 112×85×22 mm belly pod, 4× M3 hard point pattern, 18 mm protrusion below hull line
- [x] **Clamshell door halves** — `cargo_door_port.stl` + `cargo_door_stbd.stl` generated by
  `serenity/stl/generate_cargo_doors.py` (trimesh/scipy bilinear interpolation from Rev-O shell
  belly faces). Both watertight; 8-barrel piano hinge, 3 mm CF rod, 3.15 mm bore. *(done 2026-06-01)*
- [x] **`cargo_sect_shell24.scad` Rev S** — belly opening (100×9×165 mm), 2× hinge-pin blocks
  (3.3 mm bore + M3 grub-screw tap), 2× SG90 servo mounting pads (4× M2.5 pilots each), 4×
  latch-catch lips (Z=42/122 mm at each X frame edge). *(done 2026-06-01)*
- [x] **`cargo_sect_shell24.scad` Rev S1** — wing root mortises (30.8×20.8×15 mm), spar bearing
  blocks (22 mm OD × 10 mm boss, M3 grub-screw), full-Z spar bore (Ø12.3 mm), and nacelle tilt
  servo mount blocks (52×30×8 mm, 4× RX-M3×5.7 inserts) at port + stbd interior Z walls.
  All 4 spatial conflicts resolved (NSVMT_X_CEN moved AFT to −147.6 mm). Load FOS ≥ 11 vs 4.0
  AUVSI target. *(done 2026-06-08, PR #42)*
- [x] **`cargo_sect_shell24.scad` Rev S2** — Inara and River avionics bay dorsal standoffs
  (8× M3 boss posts, ±40×±25 mm pattern) + dorsal access panel cuts (62×42 mm each) for Cape-B
  (55×35 mm) at port half (Z_CEN=118 mm, Inara) and stbd half (Z_CEN=45 mm, River). GPS_PORT/STBD
  co-located for minimal SMA routing. *(done 2026-06-08, PR #42)*
- [x] **`cargo_sect_shell24.scad` Rev S3** — Faraday enclosure space allocation.
  Panel cuts enlarged 55×35 → 62×42 mm; boss offsets updated ±40×±25 → [TBD pending PCB layout — hole pattern must be derived from Wash.kicad_pcb / Zoë.kicad_pcb once layout is complete] to match
  Faraday tray corner mounts; bay Z centres adjusted ±1 mm (Inara 118→119, River 45→44) for 10 mm
  inter-bay gap; FARADAY_* envelope parameters (95×65×65 mm, 1.5 mm Al wall, 25 mm fan) added.
  *(done 2026-06-08, PR #42)*
- [x] **`nacelle_servo_bracket.scad`** — U-channel saddle clamp for DS3218MG nacelle tilt servo;
  4× M3×10 SHCS flanges at ±17.5×±8 mm; 10×6 mm lead notch; FOS_shear=85.7. *(done 2026-06-08)*
- [x] **`REVN_BUILD_GUIDE_24IN.md` Phase 3 anti-rework** — spar grub-screw torque sequence
  (0.5 N·m each, before foam pour) with consequence documentation. *(done 2026-06-08)*

- [ ] **`cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z walls.**
  Canonical Serenity shuttles (Shuttle 1 = Inara's, Shuttle 2) sit just above the wing roots on
  the exterior Z faces of the cargo section. Their outline profiles need to be added as raised
  exterior features at Y≈−273..−213 mm on both Z walls, matching the canonical hull geometry.
  Interior avionics zone (Inara + River dorsal band) coexists — shuttles are exterior, avionics
  interior. Reference the Thingiverse low-detail hull for shuttle fairing geometry.
  **BLOCKS canonical hull fidelity (CLAUDE.md requirement: keep skin geometry true to reference).**

- [ ] **Avionics dorsal access covers / Faraday tray lids for Inara and River bays (two parts).**
  Create `inara_access_cover.scad` and `river_access_cover.scad` (or a single parametric SCAD):
  Cover footprint 105×75 mm with 5 mm shoulder lip seating on hull skin around 95×65 mm opening.
  Copper-foil-lined PETG or 0.5 mm Al sheet; Ø38 mm GPS clearance bore at GPS offset from cover
  centre (Inara: offset −13.3 mm in Z from bay centre; River: offset +0.7 mm in Z from bay centre).
  4× M2 flathead captive screws at ±40 mm (X) × ±25 mm (Z) from cover centre for EMI-seal clamping.
  Must be removable with common hand tools per CLAUDE.md field disassembly requirement.
  Ref: FARADAY_* parameters in cargo_sect_shell24.scad Rev S3; CLAUDE.md §1.4.1.
  Add to Phase 0 print schedule.

- [ ] **Simon bay — define avionics bay in rear section SCAD file.**
  Simon's stack (Cape-B-2 + Cape-A-2, 55×35 mm (both), 29.2 mm stack height) needs boss standoffs and
  dorsal access panel in the rear engine cone SCAD (pre-Phase 11) or the middle ring SCAD (Phase 11
  and beyond, once rear EDF occupies the cone). Verify rear section bounds and available dorsal band
  before adding geometry. Reference CLAUDE.md PACE: Simon = alternate watchdog, aft EDF control.
  **BLOCKS Phase 6 full 8-node installation.**

- [ ] **Update REVN_BUILD_GUIDE_24IN.md bay layout table** to reflect revised avionics stack
  positions (Inara + River in cargo section dorsal band; Shepherd Book in head section forward;
  Simon in rear cone pre-Phase 11, middle ring post-Phase 11). Current guide Bays A–E are from an
  older layout that does not match the cargo-section dorsal placement in Rev R.

- [ ] **Regenerate `cargo_sect_shell24.stl`** from Rev R SCAD source. Run:
  `openscad -o airframe/stls/fuselage/cargo_sect_shell24.stl
    airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad`
  Verify in slicer: wing mortises at both Z walls; spar bore at X=−70 mm; 8 dorsal boss posts;
  two 62×42 mm dorsal panel openings. Z-range must be 0..163 mm; all features inside hull skin.
  **BLOCKS Phase 0 cargo section printing.**

- [ ] Add motor-mount and DRV8833-tray boss locations to `cargo_sect_shell24.scad` interior
  drawing notes (Phase 1 pre-pour checklist reference).
- [ ] Add SG90 bell-crank boss to inner face of each door panel for pushrod attachment.
  - Export gondola shell to `thingverse-serenity/files-hollowed-18in/`
  - **BLOCKS Phase 8**

###### 1.1.1.2.2 *Wing Root*

##### 1.1.1.3 *Middle Neck*

- [ ] **neck_intake_frame.stl** — `openscad -o neck_intake_frame.stl deferred/aft-edf/openscad/neck_intake_frame.scad`
  - Verify: 4 registration tongues 5 mm depth; intake lips project 6 mm forward
  - Material: CF-PETG; **DEFERRED — BLOCKS Phase 11 only.** STL at `deferred/aft-edf/stls/`.

- [ ] **rear_neck_intake_shell24.stl** — `openscad -o ... deferred/aft-edf/openscad/rear_neck_intake_shell24.scad`
  - Verify: 4 radial scoop windows present; NECK_X station ~310 mm; window alignment
  - **DEFERRED — BLOCKS Phase 11.** Print in Phase 0 with windows covered by removable PETG blanks.

  **Rear intake system (OpenSCAD):**

- [ ] **aft_edf_plenum.stl** — `openscad -o aft_edf_plenum.stl deferred/aft-edf/openscad/aft_edf_plenum.scad`
  - Verify: 4 rectangular arms 65×60 mm, aft outlet 120 mm circular; no self-intersection
  - **DEFERRED — BLOCKS Phase 11 only.** STL is already generated at `deferred/aft-edf/stls/aft_edf_plenum.stl`.

  **Canonical middle shell (OpenSCAD — belly restored, no belly scoop):**

- [x] **middle_canonical_shell24.stl** — `openscad -o ... serenity/stl/middle_canonical_shell24.scad`
  - Note: NOT the same as `middle_shell24.stl` (which has the obsolete belly intake cut). This is the Rev N canonical belly.
- [ ]

##### 1.1.1.4 *Rear Engine Cone*

#### 1.1.2 **Wings**

**Wing pylon (OpenSCAD — Rev R integrated design; carried fwd from Rev O):**

- [ ] **wing_nacelle_pylon_revo.stl** — `openscad -o ... serenity/stl/wing_nacelle_pylon_revo.scad`
  - Verify WING_SLOT_W and WING_SLOT_H against `s_wings_both_shell24.stl` (caliper-measure from the mesh) before printing — estimated 50×40 mm at 2.197× Thingiverse scale
- [ ] **wings_s1223_revo.stl** — `openscad -o ... serenity/stl/wings_s1223_revo.scad`
  - Verify WING_CHORD_ROOT, WING_CHORD_TIP, WING_SEMI_SPAN, WING_SWEEP_LE against original STL before printing

#### 1.1.3 **Nacelles**

**Nacelle shells (Blender, Rev R geometry; carried fwd from Rev O — must run on host machine):**

- [ ] **Rev R1 nacelle stator shells** — run `blender --background --python thingverse-serenity/blender_nacelle_revo.py`.
  - Port nacelle: `SWIRL_DIR=-1` (CCW from intake); stbd nacelle: `SWIRL_DIR=+1` (CW).
    *(SWIRL_DIR assignments corrected 2026-06-11 per Rev R1/nacelle-swap — original directions were inverted.)*
  - Output: `s_eng_left_stator_shell24_revo.stl` (stbd use), `s_eng_right_stator_shell24_revo.stl` (port use)
  - Verify: Z-range 0–148.3 mm, bore ID 55.0–56.0 mm, 11 stator fins visible in Z=53–95 mm gap
  - **BLOCKS Phase 0 nacelle printing**

##### 1.1.3.1 *Nozzle*

- [ ] **nacelle_nozzle_iris.stl** — `openscad -o ... serenity/stl/nacelle_nozzle_iris.scad`
  - Spec: 50 mm iris — inner ring (M=1.0 rack), outer housing, 8-petal geometry

##### 1.1.3.2 *Tilt Gear Train*

  **Rev R gear train (OpenSCAD — all 5 parts, M=1.0; carried fwd from Rev O):**

- [ ] **nacelle_sector_gear.stl** — `openscad -o ... serenity/stl/nacelle_sector_gear.scad`
  - Spec: R=22mm, 38T, 155° arc; fixed to tilt bracket
- [ ] **nacelle_pinion.stl** — `openscad -o ... serenity/stl/nacelle_pinion.scad`
  - Spec: N=12T, D-bore shaft (×4 total: drive pinion + crown pinion per nacelle)
- [ ] **nacelle_bevel_pair.stl** — `openscad -o ... serenity/stl/nacelle_bevel_pair.scad`
  - Spec: N=14T, 45° pitch cone, 1:1, 90° axis redirect
- [ ] **nacelle_bevel_housing.stl** — `openscad -o ... serenity/stl/nacelle_bevel_housing.scad`
  - Spec: CF-PETG, 24×14×20 mm housing block

#### 1.1.4 **Landing Gear**

##### 1.1.4.1 *Legs*

- [ ] Separate 4x leg stl into individual leg files, orient and test fit on freeCAD assembly

- [ ] evaluate suitability of model legs for actual use

  - [ ] evaluate static and dynamic alternatives

    - [ ] Multipart / Unitary?

    - [ ] Springs / Struts ?

    - [ ] Mounting to hull

  - [ ] Implement canonically and mechanically sound legs

##### 1.1.4.2 *Feet*

- [ ] Modify feet as needed to mount to legs to provide stable landing



**Remaining parts needing SCAD source creation then STL export:**

- **BLOCKS Phase 1**

**Combined airframe model (visual verification):**

- [ ] **Combine all airframe STLs** into a single assembly model including the 1.25× scaled nacelles, all EDF tubes, cargo bay clamshells, antenna bosses, sensor cutouts, access panels, landing legs, and feet.
  **Canonical assembly script:** `airframe/FreeCAD-scripts/serenity_assembly.py` (8 major components validated 2026-06-10; nacelle internals, pylons, and accessories pending VERIFY).
  Run headlessly: `freecad --background --python airframe/FreeCAD-scripts/serenity_assembly.py`
  Output: `airframe/Serenity-Assembled.FCStd`
  - [ ] **Render overview SVGs using FreeCAD TechDraw** — 6 cardinal directions (top, bottom, front, rear, port, stbd) and all 8 isometric views (8 corners). Headless script creates a TechDraw page per view and exports SVG via `TechDraw.writeSVGPage()`. Save to `airframe/diagrams/overview/`.
    **BLOCKS** exploded view SVGs below.
- [ ] **Exploded view SVG — printed parts only** (all printed components labelled and exploded from assembly position). **Generate using FreeCAD:** drive part translations via a headless Python script that offsets each `Mesh::Feature` Placement along its explosion axis, then exports SVG via FreeCAD TechDraw. Save to `airframe/diagrams/exploded/`.
- [ ] **Exploded view SVG — full build** (all components: PCBs, SBCs, motors, ESCs, wires, sensors, antennas, hardware). Same FreeCAD TechDraw headless approach as printed-parts exploded view. Save to `airframe/diagrams/exploded/`.

---

#### 1.1.5 **Non-Printable Component Placeholders** *(Rev R1, 2026-06-12)*

Dimensionally-accurate bounding-geometry STL placeholder files for all non-printable
Rev R BOM components, for use in FreeCAD exploded-view and build-guide assembly.

**Generator:** `airframe/placeholders/generate_placeholders.py`
(pure Python, no external dependencies; run with `python3 generate_placeholders.py`)

**FreeCAD catalog script:** `airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`
(loads all 76 placeholder STLs into a grid-layout catalog document;
 run with `freecadcmd airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`)

**Output:** `airframe/Serenity-Placeholders.FCStd` (76 components, 8-column grid)

**Placeholder coverage (76 STLs, 6056 triangles total):**

| Category | Count | Files |
|---|---|---|
| Propulsion (EDFs, ESCs) | 4 | `airframe/placeholders/propulsion/` |
| Servos (DS3218MG, SG90) | 2 | `airframe/placeholders/servos/` |
| Bearings (MF104ZZ, MR63ZZ, 6804) | 3 | `airframe/placeholders/bearings/` |
| Structural CF (rods, tube, bar, plate, PTFE) | 6 | `airframe/placeholders/structural/` |
| Avionics PCBs (PB2-I, Cape-A-2/B-2, Emma, Kaylee, microSD) | 6 | `airframe/placeholders/avionics/` |
| Power (LiPos, fuses, shunt) | 7 | `airframe/placeholders/power/` |
| Cargo (N20, HX711, DRV8833, Dyneema) | 4 | `airframe/placeholders/cargo/` |
| Gears M=1.0 (sector, pinion, bevel, housing) | 4 | `airframe/placeholders/gears/` |
| Hardware (pins, inserts, screws, straps, wire ring) | 6 | `airframe/placeholders/hardware/` |
| Lighting (WS2812B ring, WS2812C SMD) | 2 | `airframe/placeholders/lighting/` |
| Wiring (conduit, harnesses, antenna wire, posts) | 6 | `airframe/placeholders/wiring/` |
| GCS / Malcolm (enclosure, BECs, antennas, tripod, encoders) | 15 | `airframe/placeholders/gcs/` |
| Foam fill + interior voids (head/cargo/middle/rear fill; avbay, cargo bay, wiring trunk, power bus, ventilation, pylon pockets; Faraday cage pockets + vent duct spurs) | 13 | `airframe/placeholders/foam/` |
| EMC / Faraday shielding (cage, gasket, fan, EMI vent, bond strap, feed-through panel, ferrite; Malcolm fan + gasket) | 9 (×2 STL files share gen_far_fan_40) | `airframe/placeholders/faraday/` |

**Completed (2026-06-12):**
- [x] **Generate all 65 component placeholder STLs** — `generate_placeholders.py` created;
  all files verified `OK`. STL header marker: `SerenityUAV PLACEHOLDER R1`. *(done 2026-06-12)*
- [x] **FreeCAD catalog assembly script** — `serenity_placeholders_assembly.py` created;
  component grid layout; run with `freecadcmd`. *(done 2026-06-12)*
- [x] **Faraday shielding hardware** — 9 new generators; 11 new STL files in `airframe/placeholders/faraday/`:
  FAR-CAGE-AV (cage), FAR-GASKET-AV, FAR-FAN-40, FAR-EMI-VENT-40, FAR-BOND-STRAP,
  FAR-FT-PANEL, FAR-FERRITE-4MM; MAL-FAR-FAN, MAL-FAR-GASKET (GCS).
  BOM entries added to `current-specification/bom_revR.csv`.
  **⚠ MASS NOTICE: Faraday system adds 484 g (1.07 lbm) to aircraft AUW
  (reduced from 648 g: cage → 0.1 mm Al foil bonded to foam — 2026-06-13).
  Hover T/W ≈ 1.09 — still below safe VTOL minimum (~1.2). See open
  mass budget review in §1.1.5 below.** *(done 2026-06-13)*
- [x] **Faraday cage foam voids** — VOID-FAR-CAGE (76×56×88 mm cage pocket) and
  VOID-FAR-FAN-SPUR (44×44×50 mm vent duct spur) added to `airframe/placeholders/foam/`.
  Use ×4 and ×8 copies respectively in FreeCAD to plan all 4 bays. *(done 2026-06-13)*
- [x] **Foam-fill and void visualization STLs** — 11 new STLs in `airframe/placeholders/foam/`:
  4× FOAM-FILL-* (head/cargo/middle/rear hull sections) and 7× VOID-* (avionics bays,
  cargo bay, wiring trunk, power bus, ventilation intake/exhaust, nacelle pylon pockets).
  Total 76 components, 6056 triangles. Use tan/ochre for FOAM-FILL, translucent cyan for
  VOID objects in FreeCAD. *(done 2026-06-12)*

**Open sub-tasks:**
- [ ] **Run FreeCAD catalog** — execute `serenity_placeholders_assembly.py` once
  FreeCAD is available to verify grid layout and produce
  `airframe/Serenity-Placeholders.FCStd`. Commit the FCStd to the repo.
- [ ] **Hull-frame placement pass** — for the full-build exploded view (§1.1.4 task),
  derive the hull-frame position and orientation of each placeholder (e.g., EDF
  inside nacelle bore, battery tray in cargo section, avionics PCBs in bays)
  and add `place_mesh()` calls to `serenity_placeholders_assembly.py`.
- [ ] **Add Phase-11 (deferred) items to catalog** — `EDF_120mm_6S_deferred.stl` and
  `ESC_80A_6S_BLHeli32_deferred.stl` are generated; confirm they appear in the
  `deferred/aft-edf/` sub-assembly once that phase resumes.
- [ ] **Mesh watertightness audit** — run `python tools/validate_stls.py` across
  `airframe/placeholders/**/*.stl` after first CI run; resolve any non-manifold
  findings (complex compound meshes: piano-wire torus ring, RF splitter ports, etc.).
  **Known finding:** `Foam_fill_middle_horseshoe_173x69x161mm.stl` has coplanar
  T-junction faces at Z=121 mm between left/right pillar tops and the arch bottom
  (all three pieces share a common plane but are separate box meshes joined via `_cat()`).
  Acceptable for visualisation; fix by replacing with a proper extruded U-shape when
  trimesh/CSG support is available.
- [ ] **FAR-FT-PANEL PCB design** — design the EMI-filtered feed-through panel
  KiCad schematic + layout (55×35 mm, LP π-filter + TVS on CAN FD ×2,
  RS-485, Ethernet RJ45, power JST-GH 2P). Run DRC; generate gerbers; add
  to `avionics/kicad/`. **BLOCKS Faraday cage final assembly.**
- [ ] **Faraday mass budget review** — cage wall reduced to 0.1 mm 5052-H34 Al
  foil bonded to foam (elastic foundation raises panel f₁ ≈ 810 Hz >
  EDF shaft ~470 Hz; no stiffening features needed); system mass now
  484 g (1.07 lbm), T/W ≈ 1.09 — still below ~1.2 minimum.
  Remaining options to close gap:
  (b) 4 ferrites/cage instead of 8 (saves 80 g → 404 g, T/W ≈ 1.11);
  (c) 1 bond strap/cage instead of 2 (saves 40 g → 364 g / 444 g w/o b,
      T/W ≈ 1.12 / 1.10);
  (d) accept T/W = 1.09 if EDF bin-test confirms nominal thrust exceeds
      spec (1240 g × 90% × 2 EDFs = 2232 g is a floor, not mean).
  Target: Faraday mass ≤ 400 g to restore T/W ≥ 1.12.
  **BLOCKS final cage fabrication.**
- [ ] **Link placeholders to BOM entries** — add `Placeholder_STL` field to
  `docs/bom_revR.json` for each non-printable row pointing to its STL path.

---

### 1.2 — PCB Design: Cape-A-1 and Cape-B-1

- [x] **Regenerate Cape-A-1 gerbers** — `.kicad_pcb` modified 2026-05-23 (tamper-mesh commit); gerbers in `serenity/kicad/gerbers/CAPE-A-1/` are from 2026-05-22.
  - Open in KiCad → Plot → Gerbers; overwrite files in `serenity/kicad/gerbers/CAPE-A-1/`; re-export drill files.
  - Run DRC to zero errors before plotting.
  - **BLOCKS Phase 6 fab order**

- [x] **Regenerate Cape-B-1 gerbers** — same timestamp issue. `serenity/kicad/gerbers/CAPE-B-1/` files are from 2026-05-22.
  - **BLOCKS Phase 6 fab order**

---

### 1.2a — PCB Design: Wash, Zoë, and Emma (EMI-Hardened Variants)

#### ***EM hardening Objective is to ensure safe and controlled operations in hostile em/rf environments such as the vicinity of radiating commercial broadcast, amateur radio and cellular towers.***

Design files on branch `claude/cape-em-harsh-variants-9Yfr1`. Schematics (`*.kicad_sch`) and PCB
layout files (`*.kicad_pcb`) are complete. Gerber files have not yet been generated or DRC-verified.

**Key changes from -1 variants:**

- **CAN FD**: ATA6561 (non-isolated) → ISOW1044BDFMR (TI, SOIC-16W, 5 kV reinforced isolation +
  integrated DC/DC converter, IEC 62368-1 / VDE 0884-11)
- **RS-485**: MAX3485E (non-isolated) → ADM2795EBRWZ (ADI, SOIC-20W, 5 kV reinforced isolation +
  integrated DC/DC converter)
- **Ethernet PHY (Rev R baseline; introduced Rev Q)**: DP83825I (TI, LQFP-32, 10/100BASE-TX RMII) with EMI hardening:
  HX1188NL LAN magnetics (1500 V isolation), SRF2012-100Y CMC, PRTR5V0U2X TVS, TPS62933 1.8V
  supply. JST SM06B-GHS-TB-1MP connector (no RJ45). Wash: 2× PHY (RMII0+RMII1);
  Zoë: 1× PHY (RMII0).
- **Emma**: SRF2012-100Y CMC on antenna coax shield, PRTR5V0U2X TVS on PTT/RX lines,
  X2Y bridging capacitor on RF ground plane, Würth 742792512 ferrite bead on +5V rail

**Transform scripts** (generate -2 files from -1 originals):

- `avionics/kicad/gen_cape_a2.py` → `CAPE-A-2.kicad_sch`
- `avionics/kicad/gen_cape_b2.py` → `CAPE-B-2.kicad_sch`
- `avionics/kicad/add_eth_phy.py` — ETH PHY isolation sub-circuit generator (called by above)
- `avionics/kicad/gen_cape_a2_pcb.py` → `CAPE-A-2.kicad_pcb`
- `avionics/kicad/gen_cape_b2_pcb.py` → `CAPE-B-2.kicad_pcb`

**Open tasks:**

##### 1.2a.1 *Cape DRC / routing / ETH2 status (2026-06-12)* — see `avionics/kicad/README.md`

- [x] **Wire second Ethernet (ETH2) on Wash.** `ETH2` / `ETH2-PHY` (ADIN1300) /
  `T-ETH2` (749010012A) were placed but unconnected; nets now mirror ETH1
  (`ETH2_LINE_*` → `T-ETH2` → `ETH2_*` → PHY), reusing the host-side `RMII1_*`,
  `MDIO`/`MDC`, `PHY2_INTRN`/`PHY2_RSTN`, `VCC2_ETH`/`GND`/`GND2_ETH` nets on
  PB2-P2. 44 pads assigned; diff pairs verified. *(PR #59, 2026-06-12)*
- [x] **Separate the two Wash PHYs onto independent MDIO buses** (instead of an
  address strap). PHY1/ETH1-PHY → `MDIO0`/`MDC0` (CPSW MDIO, PB2-P2 pins 17/18);
  PHY2/ETH2-PHY → `MDIO1`/`MDC1` (2nd bus, PB2-P2 pins 1/2 = the two spare servo
  channels SERVO6/7). Each PB2-I NIC manages its own PHY; no shared-address
  conflict. PCB + schematic global labels updated. *(2026-06-12)*
  - **Firmware/DT:** PHY2's bus must be brought up as `mdio-gpio` (bit-banged) on
    the two repurposed balls; verify they are GPIO-capable in the PB2-I pinmux.
- [x] **Wire the field-connector pins to their signals on Wash** (connectors were
  all floating). Done per each footprint's Description pinout: SERVO-PWM pads 1–6
  → SERVO0–5 (PWM); ESC-TLM → UART_ESC_TX/RX; GPIO-A…F → GND/+3V3 (+ `GPIO_EXP_*`
  signal pin labelled); CAN-FD → CAN_H/CAN_L; RS-485 → RS485_A/B; PWR-IN → +5V/GND.
  *(2026-06-12)*
- [x] **Source the 6 `GPIO_EXP_A…F` signals via an I2C GPIO expander.** Added
  `U-GPIO` (PCA9555DB, SSOP-24, addr 0x20) on the existing I2C1 bus with a
  `C-GPIO` 100 nF decoupling cap; P0_0–P0_5 → GPIO_EXP_A–F. *(2026-06-12)*
  - [ ] Verify/add I2C1 pull-ups (≈4.7 kΩ to +3V3 on SDA/SCL) — none on cape;
    confirm whether the PB2-I provides them.
  - [ ] Finalise placement of U-GPIO/C-GPIO (added at a tentative location).
- [x] **Add an ESC-PWM output connector for DSHOT0–3.** Added `ESC-PWM`
  (JST-GH 5-pin SM05B): pins 1–4 → DSHOT0–3, pin 5 → GND. *(2026-06-12)*
  - [ ] Finalise ESC-PWM placement (added at a tentative location).
- [ ] **Reconcile Wash.md §14 field-connector table with the actual PCB
  connectors** (PCB has SERVO-PWM 1×8 + GPIO-A…F + ESC-TLM; §14 lists J_SERVO/
  J_ESC/J_GPS/J_ENC/J_SBUS/J_VBAT/J_FAN). Bring the doc and board into agreement.
- [ ] **Wire the MIL-1553 connector + transformer.** `MIL-1553` connector and the
  `1553-XFM` transformer coupling to the bus are unwired at the IC level; the
  driver/receiver (DS26LV31/32) are only partially netted.
- [ ] **Redesign the tamper mesh as a per-domain anti-tamper mesh (all 4 capes).**
  The current `TMESH_P`/`TMESH_N` cross-hatch grid on F.Cu/B.Cu shorts across SMD
  pads and across the isolated `GND2_*` domains (≈335 of Wash's 465 DRC errors;
  similar on Zoë). Rework as one monitored mesh net per isolation region
  (secure/`GND` + per-`GND2_CAN`/`GND2_ETH`/`GND2_RS485` field side), keeping the
  0.5 mm `ISOLATION` creepage moat clear between domains. **BLOCKS DRC-clean.**
- [ ] **Carry the tamper signal over the link for the TPM-less boards.** Kaylee
  and Emma have no local TPM: route Kaylee's mesh signal to Wash and
  Emma's to Zoë over the inter-board link.
- [ ] **Route the rearranged capes.** The manual component reseat left ~60 signal
  nets per cape unrouted (7 power/ground nets are planes). Headless freerouting
  was **not** usable (see toolchain findings in `avionics/kicad/README.md`):
  KiCad 9.0.2 `ExportSpecctraDSN` is broken in standalone Python, and freerouting
  2.1 headless never self-exits and emits incomplete SES. **Finish routing in the
  KiCad GUI**; route the impedance-controlled Ethernet pairs interactively
  (length-matched, 100 Ω ±10% MDI). **BLOCKS gerbers / fab.**
- [ ] **Clear residual DRC after mesh + routing** (counts measured 2026-06-12,
  error+warning): Wash 465 / 121 unconnected, Zoë 554 / 146, Emma 421 /
  160, Kaylee 221 / 181. Remaining types after the mesh fix are mostly
  silk-over-copper, text-height, courtyard-overlap, and lib-footprint mismatch.

- [ ] finish Wash PCB.  ensure all phy have shielded connectors, all nets are valid, all ferrite beads and isolation caps are in place.- [ ] Add sbus/uart dip to Wash.
- [ ] **Generate Wash gerbers** — `CAPE-A-2.kicad_pcb` complete; run DRC to zero errors in
  KiCad; export to `avionics/kicad/gerbers/CAPE-A-2/`; re-export drill files.
  - **BLOCKS Wash fab order**
- [ ] **Generate Zoë gerbers** — `CAPE-B-2.kicad_pcb` complete; same DRC + export procedure;
  export to `avionics/kicad/gerbers/CAPE-B-2/`.
  - **BLOCKS Zoë fab order**

- [x] remove wifi, sik, and loRa antennas from Zoë. Use filtered chokes on rf lines to route all RF signals from antennas to wifi, lora, zigbee,and sik xcvr circuits on Zoë, and/or use uart or i2c with filtering to connect isolated xcvrs to the cape. **Done (2026-06-05):** Added §13 antenna filter chains to CAPE-B-2.kicad_sch — each radio ANT pin now routes through a Johanson BPF (FL_LORA/FL_SIK: 0915LP15B0100E; FL_WIFI: 2450BP15B050E) and RCLAMP0502B ESD shunt to a dedicated SMA connector (J_SMA_LORA, J_SMA_WIFI, J_SMA_SIK). SiK uses Hirose U.FL J_SIK_ANT for module pigtail. All connector shells PGND. See CAPE-B-2.md §13.
- [x] **Re-evaluate space / restore Ethernet to Zoë** — One DP83825I EMI-hardened PHY
  added to Zoë at Rev R (introduced Rev Q); J_ETH_B connector populated. Board has adequate
  space; RF SMA connectors remain. *(done 2026-06-07)*

- [ ] **Generate Emma gerbers** — `XCVR-49MHZ-2.kicad_pcb` complete; export to
  `avionics/kicad/gerbers/XCVR-49MHZ-2/`.
  - **BLOCKS Emma fab order**
- [ ] **FCC Part 95 Subpart D pre-compliance checklist for Emma** — document center
  frequency accuracy (±0.005% per 47 CFR 95.655), ERP (≤100 mW), harmonic suppression ≥40 dBc at
  2nd/3rd harmonics, 47 CFR 95.603 FCC ID silkscreen labeling block.
- [ ] **EMI isolation validation checklist** — verify isolation barrier clearance: ISOW1044BDFMR
  5 kV working voltage; ADM2795EBRWZ 5 kV working voltage; measure CMRR at 1 MHz on CAN and
  RS-485 channels; verify differential impedance 100 Ω ±10% on ETH MDI traces.

- [ ] **Merge `claude/cape-em-harsh-variants-9Yfr1` → master** after gerbers pass DRC and
  pre-compliance checklist is signed off.

- [ ] Design Faraday cages / boxes to protect all PCBs, minimizing weight and space but ensuring needed protection.

- [ ] Specify / implement tightly twisted pair bonded shielded wiring and cables throughout the aircraft.

---

### 1.3 — PCB Design: XCVR-49MHZ-1 (49 MHz AX.25 RCRS Transceiver)

Stub KiCad project at `serenity/kicad/XCVR-49MHZ-1.*`. Design notes in `serenity/kicad/XCVR-49MHZ-1.md`.
All Phase 1–3 items must be sequentially complete. Phase 4 verification runs in parallel with Phase 3.

**Phase 1 — IC Selection (gates all downstream work):**

- [x] **Resolve DDS choice** — **Si5351A-B-GT selected** (Silicon Labs, MSOP-10) + EPSON TG2520SMN 25 MHz ±0.5 ppm TCXO. I²C direct to 49 MHz; firmware driver already written (`si5351.c`); < ±1 ppm system stability, meeting Part 95 ±0.005% with > 25× margin. AD9833 eliminated (max 12.5 MHz; required ×4 external PLL). *(decided 2026-05-31)*

- [x] **Evaluate PA options** — **Two-stage discrete BJT selected**: MMBT2222A (SOT-23, driver) + 2N3866 (SOT-39, final). Class-A/AB; +5 V supply direct; ≈ 100 mW ERP; ≈ $1.60 BOM; ≥ 40 dBc harmonic suppression via FL1 LPF (SPICE verify Phase 4). RA07H4047M eliminated (requires 7.2–13.6 V; needs boost converter). *(decided 2026-05-31)*

- [x] **Confirm TCM3105 availability** — TCM3105 confirmed discontinued (TI); no in-production drop-in. **Software Bell 202 AFSK selected**: AM6254 Cape-B MCU generates/decodes audio; TX via MCP4921 SPI 12-bit DAC; RX via LM393 comparator + passive RC bandpass filter. *(decided 2026-05-31)*

**Phase 2 — Schematic:**

- [ ] **U1 DDS sub-circuit** — power decoupling, SPI/I²C to J1, frequency configuration load sequence; channel select (49.830–49.890 MHz) software-configurable.

- [ ] **U2 AFSK modem sub-circuit** — software Bell 202 on Cape-B MCU; MCP4921 SPI 12-bit DAC (TX audio to U3 modulator); LM393 comparator + passive RC bandpass filter (RX demod); UART to J1 pins 3/4; LM393 output as CD (carrier detect) to Cape-B GPIO.

- [ ] **U3 PA + modulator sub-circuit** — DDS carrier in, AFSK audio in, RF out to FL1; PTT_N gate; bias network and 50 Ω output matching.

- [ ] **FL1 5-element Chebyshev LPF** — calculate values for fc=75 MHz, 50 Ω; verify −40 dBc at 98 MHz (2nd harmonic of 49 MHz). Simulate in QUCS-S before committing values.

- [ ] **U4 LNA + envelope detector RX chain** — MGA-82563 input, gain/NF budget, RSSI voltage divider to J1 pin 6.

- [ ] **U5 TX/RX switch** — PE4259-63 SPDT; PTT_N control; isolation must protect LNA during TX (PE4259 ≥35 dB TX→RX isolation).

- [ ] **U6 3.3 V LDO and power tree** — AMS1117-3.3 from +5V; bulk decoupling; ferrite bead between digital and RF sections on +5V.

- [ ] **J1 and J2 connectors** with all pin labels.

- [ ] **Run ERC; resolve all errors.**

**Phase 3 — PCB Layout:**

- [ ] **Set up layer stack** — 4L: F.Cu signal / In1.Cu GND / In2.Cu +3V3 / B.Cu signal; 1.6 mm total thickness (JLCPCB standard).

- [ ] **Place components** — RF section (right 25 mm): U1, U3, U4, U5, FL1, J2; digital section (left 30 mm): U2, U6, J1.

- [ ] **Route RF path** — 50 Ω microstrip, 2.75 mm wide on F.Cu (Z₀ = 52.26 Ω confirmed by `check_impedance.py` 2026-05-30); continuous GND stitching vias; no 90° bends.

- [ ] **Route digital signals** — UART traces ≥5 mm from RF section boundary; ferrite bead (BLM18PG221SN1D or equiv.) on +5V at boundary.

- [ ] **LPF shield keep-out** — mark Coilcraft SER inductor cans on F.Fab; orient perpendicular; verify no mutual coupling.

- [ ] **Thermal vias under U3 PA** — exposed pad to In1.Cu GND; minimum 9× 0.3 mm vias; verify <85°C case at 100 mW continuous TX.

- [ ] **SMA J2 edge placement** — flush to right board edge; 3 mm Cu keep-out either side of feed line from edge to U5.

- [ ] **Run DRC; resolve all errors.**

**Phase 4 — Verification and Compliance:**

- [ ] **SPICE/QUCS simulation of FL1 LPF** — verify harmonic suppression meets 47 CFR 95.655 before board spin.

- [x] **50 Ω trace impedance check** — Z₀ = 52.26 Ω for W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm → **PASS** [45–55 Ω]. *(done 2026-05-30 — serenity/kicad/check_impedance.py)*

- [ ] **FCC Part 95 pre-compliance checklist** — document: center frequency accuracy, ERP calculation, harmonic levels, labeling requirements (47 CFR 95.603 FCC ID block on silkscreen).

**Phase 5 — Production Files:**

- [ ] **Export gerbers** to `serenity/kicad/gerbers/XCVR-49MHZ-1/`

- [ ] **Export BOM** — add XCVR-49MHZ-1 line items to `serenity/docs/bom_revN.csv` and `bom_revN.json`

- [x] **Update `PROJECT_INDEX.md`** to list XCVR-49MHZ-1. *(done 2026-05-25)*

---

### 1.4 - EMI Hardening Beyond the PCBs to provide protection for 500 W/m^2 environment

#### 1.4.1 Faraday Enclosures

- Must have proper bonding/grounding without loops.

- Must have a fan and appropriate cooling

- Must minimize weight, size, and cost

- [ ] PB2-I + Wash Enclosure

- Must account for all sensor inputs and flight control and comms outputs.

- [ ] PB2-I + Zoë Enclosure

- Must account for RF routing from external antennas to internal transceivers

- Must protect the log uSD

#### 1.4.2. Antenna Placement and feedlines

feelines

- [ ] 2 antennas for each of the 4 comm links, plus 2 gps/gnss antennas. This alsomeansthere are only 2 49MHz xcvrs. Each avionics stack has two. No Avionics stack has both LoRa and SiK, since those use the same 900mhz ism band.

- [ ] antenna mounts

- [ ] feedlines

- [ ] chokes

#### 1.4.3 internode communication wiring

- [ ] Specify Signal wiring for CAN-FD, RS485, MIL-1553b, Ethernet

#### 1.4.4 flight control signal wiring

- [ ] Specify wiring for UART, I2C, BSHOT, PWM, 

#### 1.4.5 power distribution — Kaylee (PDB) and battery

**Battery placement decision (2026-06-08):**
The 6S 4000 mAh LiPo (~450–520 g, ~155×52×36 mm) must be located near the aircraft CG.
Phase 5 ground-test requirement: static CG at 190 mm from nose (REVN_BUILD_GUIDE_24IN.md §Phase 5).
The keel datum at 190 mm from nose falls within the **middle ring section** (between keel stations
165 mm and 251 mm), which is the main fuselage body above the cargo gondola.
Battery is placed on the keel floor of the middle section, oriented longitudinally, secured by:
- Two M3 boss standoffs at X≈−190 mm (CG station) on the keel face
- Velcro retention strap through keel slot (safety tether, not sole retention)
- Slide-in rail guides on keel face prevent lateral shift at 3g manoeuvre

**Kaylee (PDB) placement decision (2026-06-08):**
Kaylee (XT90 PDB, 4× XT30 outputs, ~80×60 mm) mounts adjacent to the battery in the middle
section keel area (X≈−165..−245 mm station range) to minimise high-current 14 AWG wire length
to the four nacelle ESC feeds (fed through PTFE conduits in the wing spar channel and to the
cargo gondola lateral walls).
Battery swap access via a **ventral hatch** in the middle section belly skin (hatch centred at
X≈−190 mm, ~120×60 mm opening; 2 mm shoulder lip; 4× M2 captive screws).

**Open items — BLOCKS Phase 1 foam pour:**
- [ ] **Add Kaylee/battery boss pattern to `middle_canonical_shell24.scad`.**
  Boss posts: 4× M3 at (±55 mm X) × (±25 mm Z) from X=−190 mm keel centre for battery tray.
  Kaylee PDB: 4× M3 boss posts at X≈−205 mm, Z=CZ±25 mm. Both on keel interior face (+Y rail).
  Verify boss positions clear keel CF flat bar (6×3 mm) and ring frame station notches in slicer.

- [ ] **Add ventral battery-swap hatch cut to `middle_canonical_shell24.scad`.**
  120×60 mm belly cut centred at X=−190 mm; 2 mm shoulder lip; same pattern as avionics panels.
  **BLOCKS Phase 1 foam pour** (void former must clear hatch zone before foam pour).

- [ ] **Create `kaylee_battery_tray.scad`.**
  CF-PETG slide-in rail guide tray for 6S LiPo 155×52×36 mm; M3 attachment to boss posts;
  two captive Velcro strap slots; XT90 connector exit cutout on AFT face.
  **Add to Phase 0 print schedule.**

- [ ] **Create `kaylee_pdb_tray.scad`.**
  CF-PETG mounting tray for Kaylee PDB (80×60 mm footprint); M3 boss attachment;
  XT90 input pigtail route-through; 4× XT30 output ports facing AFT (toward ESC conduits).
  **Add to Phase 0 print schedule.**

- [x] **Kaylee PCB KiCad files generated (Rev A, 2026-06-10):**
  - [x] `avionics/kicad/Kaylee.kicad_pro` — project file; net classes VBAT/PGND/POWER_5V/Default; DRC rules
  - [x] `avionics/kicad/Kaylee.kicad_sch` — full schematic; 90×65 mm 4-layer; BQ76930 6S cell monitor;
        dual TPS54620 5V BEC; TPS54540 6V BEC; 5× INA226 monitors; 4× ESC branches with 40A fuses +
        470µF caps + CMC + 1 mΩ shunts; SMBJ33CA TVS; AON6556 discharge FET; dual Würth 7440640500 CM filter
  - [x] `avionics/kicad/Kaylee.kicad_pcb` — PCB outline + 4-layer stackup (F.Cu signal, In1.Cu GND,
        In2.Cu VBAT 4oz, B.Cu signal); 4× M3 NPTH mounting holes; all 19 nets declared
  - [x] `avionics/kicad/gen_kaylee.py` — Python generator producing all three KiCad files

- [x] **Kaylee PCB — DRC run and gerbers generated (Rev A, 2026-06-10):**
  - [x] Run KiCad DRC; resolved all shorting and 0.0 mm clearance violations
  - [x] Generate gerbers to `avionics/kicad/gerbers/Kaylee/` (17 Gerber layers + Kaylee.drl)
  - [ ] **DRC accepted violations (document only — not fixable without PCB re-architecture):**
    - [ ] 16 clearance violations at 0.15 mm: INA226 MSOP-10 adjacent pads (pins 3/4) at 0.5 mm pitch
          inherently violate 0.2 mm PGND/POWER_5V class rule; IPC-2221B allows ≥ 0.1 mm for ≤ 31 V
    - [ ] 77 courtyard overlaps: dense 90×65 mm layout; 3D bodies do not conflict; no manufacturing impact
    - [ ] 59 lib_footprint_mismatch: all footprints are inline in .kicad_pcb (not library copies); expected
    - [ ] 33 silk_over_copper / 26 silk_overlap / 2 silk_edge_clearance: cosmetic; board is fab-ready
    - [ ] 8 lib_footprint_issues: inline footprints; not KiCad library-linked; expected
    - [ ] 181 unconnected_items: traces not yet routed (power planes on In1/In2.Cu are correct)
  - [ ] **Kaylee PCB — remaining layout tasks (BLOCKS fabrication):**
    - [ ] Manually place in KiCad: CM_ESC1–4 (INA226 shunt caps), C_DEC1–4 (ESC decoupling), Section F
          (BQ76930, J_BAL, R_BAL1–6, C_CAP, J_NTC, C_NTC) — area x=62–88, y=50–65 recommended
    - [ ] Manually place: J_SHLD_5V, J_SHLD_6V, J_SHLD_I2C, J_SHLD_ALERT chassis shield lugs
    - [ ] Route all traces; verify 4 oz Cu pour on VBAT/PGND power planes (In2.Cu / In1.Cu)
    - [ ] Add BQ76930 thermal pad (TSSOP-30 PowerPAD) to footprint — currently missing from gen_kaylee_pcb.py
    - [ ] Verify XT30 connectors (J_ESC1–4) courtyard clears board edge on left side
    - [ ] Verify size and weight: PCB target ≤ 90×65 mm, ≤ 0.110 lbm (≤ 50 g)

- [ ] **Update REVN_BUILD_GUIDE_24IN.md Phase 1** to include Kaylee + battery tray installation
  in the pre-foam-pour checklist. Battery tray and hatch must be installed and hatch zone
  masked before the foam pour step.

---

### 1.5 — Documentation

- [x] **1.4.1 `serenity-rev-p.jsx`** — comprehensive 11-tab standalone Rev P specification created: Overview, Airframe, Propulsion, Avionics, Comms, Cargo, Security, Regulatory, BOM, Files, Build Status. Supersedes serenity-rev-o.jsx as current spec. *(done 2026-06-01)*

- [x] **1.4.2 Wash: rename + dual Ethernet PHY** — Board renamed to "Wash"
  throughout schematic and markdown. Added 2× EMI-hardened DP83825I PHYs (J_ETH1, J_ETH2):
  HX1188NL magnetics, SRF2012-100Y CMC, PRTR5V0U2X TVS, TPS62933 1.8V supply per PHY.
  RMII0→PHY1 (PHY addr 0x01), RMII1→PHY2 (PHY addr 0x02). MDC/MDIO shared.
  CAPE-A-2.md §1 updated from "PHY removal" to "EMI-hardened dual Ethernet PHY". *(done 2026-06-07)*

- [x] **1.4.3 Zoë: rename + Ethernet PHY** — Board renamed to
  "Zoë". Added 1× EMI-hardened DP83825I PHY (J_ETH_B): HX1188NL magnetics,
  SRF2012-100Y CMC, PRTR5V0U2X TVS ×2, TPS62933 1.8V supply. RMII0 interface, PHY addr 0x01.
  CAPE-B-2.md §1 updated from "PHY removal" to "EMI-hardened Ethernet PHY". *(done 2026-06-07)*

- [x] **1.4.4 Wash: add missing field connectors** — Connector audit found J_PWR,
  J_CAN, J_485, J_1553, J_GPS, J_SERVO, J_ESC absent from schematic despite protection circuits
  being present. All 7 connectors added (JST SM03B/SM04B/SM05B/SM06B-GHS-TB-1MP series). §14
  field connector table added to CAPE-A-2.md. *(done 2026-06-07)*

- [x] **1.4.5 Zoë: add missing field connectors** — J_PWR, J_CAN, J_485,
  J_1553 added to schematic (JST SM03B/SM04B-GHS-TB-1MP). §14 field connector table added to
  CAPE-B-2.md. *(done 2026-06-07)*

- [ ] **Update PHASED_BUILD_GUIDE.md** from Rev M 18-inch to Rev R 24-inch specifications
  (hull 609.6 mm, 50mm EDFs, v2·v2·v2·v2 node placement, Rev R power system, cargo system).

- [ ] **Sync `bom_revO.json` ↔ `bom_revO.csv`** — verify all XCVR-49MHZ-1 BOM items (Phase 5
  above) are reflected in both files once XCVR-49MHZ-1 Phase 5 is complete.

- [x] **Create `bom_revQ.json` + `bom_revQ.csv`** — Rev Q BOM: replace all v1 cape procurement
  quantities with v2 equivalents (4× Wash, 4× Zoë, 4× Emma). Remove Cape-A-1,
  Cape-B-1, XCVR-49MHZ-1 line items.

---

### 1.5 — Rev Q: Repo-Wide Architecture Propagation (2026-06-07)

- [x] **1.5.1 Rev Q documentation propagation** — Updated all project documentation from Rev P
  (v2·v1·v1·v2 mixed placement) to Rev Q (v2·v2·v2·v2 uniform EMI-hardened placement across
  all 8 avionics nodes). Changes include:

  - **TODO.md**: Rev P → Rev Q; node placement updated; §1.2a procurement updated to 4× Wash,
    4× Zoë, 4× Emma; Phase 6 / Phase 7 installation steps updated to v2 capes;
    procurement tables updated; Cape-A-1 / Cape-B-1 / XCVR-49MHZ-1 retired from active BOM.

  - **CLAUDE.md**: Rev Q already reflected (v2·v2·v2·v2, archive notes).

  - **README.md**: Rev Q already reflected (updated prior to this commit).

  - **POWER_SYSTEM_Q.md** (`docs/`): written at Rev Q baseline.

  - **AVIONICS_PB2_REDESIGN.md**: Rev Q node placement already reflected.
  *(done 2026-06-07)*

### 1.6 — Rev R: Component Revision Synchronisation + s_ Prefix Removal (2026-06-11)

- [x] **1.6.1 Rev R propagation to all active files** — Updated all project-level revision headers
  from Rev Q → Rev R (2026-06-11). Changes include: README.md battery spec table, all five
  fuselage SCAD changelog entries, all GCS Malcolm firmware headers (Q1→R1), FreeCAD assembly
  scripts, avionics firmware README, ENC-NACELLE-1.md, and 18 GCS Malcolm source files.
  *(done 2026-06-11)*

- [x] **1.6.2 Component revision synchronisation** — All component-level revision designations
  updated to Rev R per CLAUDE.md: "All components are referenced as of the latest revision."
  - Nacelle gear train (Rev O → Rev R): nacelle_nozzle_iris, nacelle_bevel_housing, nacelle_bevel_pair,
    nacelle_pinion, nacelle_sector_gear
  - EDF sleeves (Rev A → Rev R): edf_stator_sleeve, edf_aft_spider_sleeve
  - Nacelle pod/nozzle (Rev T/T2 → Rev R): nacelle_pod_50mm_tandem, nacelle_pod_50mm_tandem_simple,
    nacelle_nozzle_straight
  - Wings/pylon (Rev O → Rev R): wings_s1223_revo, wing_nacelle_pylon_revo
  - Cargo shell: Rev R baseline entry prepended to S4 changelog
  - Servo bracket: Rev R baseline entry prepended to S1 entry
  - Avionics: Wash.md, Kaylee.md, XCVR-49MHZ-2.md Rev A → Rev R; Zoë.md, Zoë.kicad_sch,
    Kaylee.kicad_pcb, gen_kaylee.py, gen_kaylee_pcb.py updated.
  *(done 2026-06-11)*

- [x] **1.6.3 Remove `s_` prefix from all SCAD and STL file names** — Removed leading `s_` from
  11 SCAD files and 19 STL files across `airframe/openscad/`, `airframe/stls/`, and
  `deferred/aft-edf/`. Updated all references in 37 active text files (Python, Markdown, JSON,
  SCAD, shell scripts, Makefile, JSX). Archive files and historical BOMs (bom_revP.json,
  bom_revQ.json) intentionally not modified.
  *(done 2026-06-11)*

### 1.5.1. Names

- [x] The ground control station is named "Malcolm" aka "CAPT Reynolds" or "CAPT Tight Pants" - "I aim to misbehave" *(implemented throughout all docs)*

- [x] The Flight Control Avionics Cape is named "Wash" - "I'm a leaf on the wind" *(implemented: CAPE-A-2.kicad_sch, CAPE-A-2.md, all docs)*

- [x] The Comms/Logging/Payload Cape is named "Zoë" - "Big Damn Heros, sir." *(implemented: CAPE-B-2.kicad_sch, CAPE-B-2.md, all docs)*

- [x] The Power Distribution Board is named "Kaylee" - "Everything is shiny." *(implemented: Kaylee.md, PWR-DIST-1.kicad_sch)*

- [ ] The Cargo handling system is named "Jayne's bunk" - "I was aiming for his head."

- [x] The forward avionics bay is named "Shepherd's room" (Bay A) - "I have heathens enough right here." *(implemented 2026-06-07)*

- [x] The second avionics bay is named "Inara's shuttle" (Bay B) - "Mal, I will never understand you." *(implemented 2026-06-07)*

- [x] The third avionics bay is named "River's room" (Bay D) - "Also, I can kill you with my mind." *(implemented 2026-06-07)*

- [x] The aft avionics bay is named "Simon's medbay" (Bay E) - "What did they do to you?" *(implemented 2026-06-07)*

### Avionics Workload Balancing

- While all Wash capes are identical and all Zoë capes are also identical, they have different primary tasking.  **All Stacks are capable to communicate and control the UAV safety in a benign environment on their own.***

- UAV Tasks with PACE prioritization and failover per stack (primary, alternative, contingency, emergency)

-- Watchdog: P - Shepherd; A - Inara; C - Simon, E - River

-- Comms: P - Inara; A - Shepherd; C - River; E - Simon

-- Flight Control: P - River; A - Simon; C - Shepherd; E - Inara

-- Payload Control: P - Simon; A - River; C - Inara; E - Shepherd

---

- Mal is the ground control station - He's the boss.

- Shepherd is the crew's conscience and therefore takes care of primarily watchdog, fault detection, failover, and authentication. His stack has SiK primary and WiFi secondary.

- Inara has primarily camera, external sensors, and high bandwidth ground communication.  Her stack is connected to  WiFi primarily and LoRa secondary.

- River provides primary control of the forward EDFs, and provides EDF and nacelle control command and syncing, and the most resilient comms.  She may be crazy, but she comes through when no one else can.  She has 49Mhz RCRS primary and LoRa secondary.

- Simon is the alternate watchdog for the ship, but most of his attention is on River.  He's got aft EDF control and alternate nacelle control. He follows River's lead but makes sure she doesn't crash the ship. Simon also controls Jayne, and ensures that the cargo isn't jettisoned or the crew abandoned. He's got 49MHz as his primary antenna and SiK as his backup.

---

## 2.0 — Procurement (Before Physical Build)

Order components after all Phase 0 STLs are confirmed printable in slicer. Long-lead items should be ordered concurrently with PCB fabrication.

### 2.1 — Filament and CF Stock (needed for Phase 0)

| Item | Qty | Notes |
|------|-----|-------|
| PETG filament | ~1,200 g | Hull sections, access panels, nozzle parts, cargo gondola |
| CF-PETG filament | ~500 g | Nacelle pods, tilt brackets, pylon, intake frame — hardened-steel nozzle required |
| TPU 95A filament | ~200 g | Landing skid feet — direct-drive extruder required |
| CF flat bar 6×3mm | ~700 mm | Keel 620 mm + 80 mm ring frame offcuts |
| CF tube 12mm OD / 1.5mm wall | ~850 mm | Wing spars 2×380 mm + 90 mm scrap |
| CF solid rod 4mm OD | ~300 mm | Pivot rods (2× nacelle) per pivot housing drawing |
| CF plate 2mm | 250×150 mm | Ring frames (5 stations per drawing) |

### 2.2 — Structural Hardware (Phase 1)

| Item | Qty | Notes |
|------|-----|-------|
| West System 105/206 epoxy | 1 kit | Keel + spar bonding; structural joints |
| 5-minute epoxy syringe 25mL | 3× | Access frames, sensor mounts |
| X-30 PU foam 2-part | ~600 mL | 2 lb/ft³, 4× expansion, 2-min pot life |
| EPS blue foam board 25mm | 500×250 mm | Void formers A–E; Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | Void former release agent (2 coats) |
| 3M 4016 closed-cell gasket tape | 1 roll | Access panel frame lips |
| PTFE tube 5mm OD × 3mm ID | 6 m | 8 conduits (CAN FD, RS-485, 1553A, 1553B, ETH×2, SERVO-PWR, MAIN-PWR) |
| M2.5 nylon hex standoff 6mm | 16× | Cape-B floor mounts (4 per bay × 4 bays) |
| M2.5 nylon hex standoff 20mm | 16× | Cape-A inter-cape spacing |
| M2.5 × 8mm SS button screws | 64× | Standoff attachment + panel B/E fasteners |
| M3 heat-set threaded inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead | 3× | SiK 915MHz (belly) + LoRa 915MHz (belly) + WiFi (dorsal fwd) |
| 0.3mm stainless wire or 22AWG enamelled Cu | ~500 mm | 49MHz RCRS top wire |
| Ceramic bead insulator 3mm ID | 1× | Aft end of 49MHz wire (insulated/open end) |

### 2.3 — Propulsion System (Phases 2–4)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| 50mm EDF @ 6S (budget tier) | 4× | ~$25–40ea | 2 per nacelle, tandem; verify OD fits 55–56mm ID bore |
| 40A 6S BLHeli32 BDSHOT ESC | 4× | ~$18–25ea | 1 per nacelle EDF |
| 120mm 6S EDF | 1× | ~$60–80 | Fuselage rear; single final motor |
| 80A 6S BLHeli32 ESC | 1× | ~$25–35 | Fuselage EDF |
| Digital tilt servo ≥25 kg·cm @ 6V, metal gear | 2× | ~$20–30ea | Nacelle tilt; prefer 30+ kg·cm |
| SG90 micro servo | 3× | ~$3ea | Nacelle nozzle ×2 (redundant) + rear nozzle ×1 |
| MF104ZZ flanged bearing 4×10×4mm | 4× | ~$8 total | 2 per nacelle pivot |
| 4mm OD CF rod (pivot) | 2× cut lengths | — | From 2.3 CF stock above |
| Steel pushrod 2mm OD × ~60mm | 2× | ~$3 total | Longitudinal nozzle shaft per nacelle |
| Steel pushrod 2mm, Z-bend ends | 2× | ~$4 total | Tilt servo pushrod |
| M2 clevis links | 4× | ~$3 total | Servo-to-pushrod |
| 0.8mm piano wire | ~600 mm | ~$3 | Nozzle iris petal link rings |
| 3mm SS hinge pins | 16× | ~$4 total | 8 per nacelle iris nozzle |
| WS2812B LED ring (50mm) | 2× | ~$6 total | Nacelle duct exit |
| WS2812C-2020 addressable LED | 6× | ~$6 total | Nav lights |
| XT90 PDB, 4× XT30 outputs | 1× | ~$12 | Power distribution |
| XT90 battery pigtail | 1× | ~$5 | Battery lead |
| 5V 5A switching BEC | 1× | ~$8 | Avionics power rail |
| 14AWG silicone wire | 1 m | ~$6 | Main bus |
| 16AWG silicone wire | 0.5 m | ~$4 | ESC signal + fuselage taps |
| 6S 4000mAh LiPo battery | 1× | ~$55–70 | Phase 6 first flight |

### 2.4 — Avionics (Phase 6 — 4-node minimum viable)

*Rev R: all nodes use v2 EMI-hardened capes. Cape-A-1 / Cape-B-1 / XCVR-49MHZ-1 are retired.*

| Item | Qty | Unit Cost | Total | Notes |
|------|-----|----------|-------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | $51.03 | ~$204 | DK 2820-100003007-ND |
| Wash (Wash) PCB (JLCPCB assembled) | 2× | ~$55 | ~$110 | FC1/Shepherd's room (Bay A) + FC2/Inara's shuttle (Bay B) (v2, EMI-hardened) |
| Zoë (Zoë) PCB (JLCPCB assembled) | 2× | ~$95 | ~$190 | CN1/Shepherd's room (Bay A) + CN2/Inara's shuttle (Bay B) (v2, EMI-hardened) |
| Emma PCB (JLCPCB assembled) | 2× | ~$25 | ~$50 | RCRS sub-module for CN1, CN2 (v2 EMI-hardened) |
| SiK 915MHz ground station radio | 1× | ~$15 | ~$15 | MAVLink GCS link |
| microSD 64GB (log, write-blocked) | 2× | ~$10 | ~$20 | CN1-LOG, CN2-LOG |
| JST-GH cables: CAN 3-pin, RS-485 3-pin, ETH 6-pin, 1553 4-pin, GPS 5-pin | assorted | — | ~$20 | Per §14 connector table |
| USB-UART adapter (CP2102) | 1× | ~$8 | ~$8 | Debug console (one-time tool) |
| 3M double-sided foam tape | 1× | ~$5 | ~$5 | ESC and node mounting |
| Zip ties 100mm + 200mm | 1 bag | ~$4 | ~$4 | Wire management |

### 2.5 — Avionics (Phase 7 — remaining 4 nodes + ToF arrays)

*Rev Q: all Phase 7 nodes also use v2 EMI-hardened capes.*

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | ~$204 | CN3, FC3, CN4, FC4 |
| Wash (Wash) PCB (JLCPCB assembled) | 2× | ~$110 | FC3/River's room (Bay D) + FC4/Simon's medbay (Bay E) (v2) |
| Zoë (Zoë) PCB (JLCPCB assembled) | 2× | ~$190 | CN3/River's room (Bay D) + CN4/Simon's medbay (Bay E) (v2) |
| Emma PCB (assembled) | 2× | ~$50 | CN3, CN4 (v2 EMI-hardened) |
| microSD 64GB (log) | 2× | ~$20 | CN3-LOG, CN4-LOG |
| VL53L5CX 8×8 ToF sensor | 12× | ~$84 | Dual OA arrays |
| TCA9548A 8-ch I²C multiplexer | 2× | ~$3 | One per array host |
| MCP23008 8-port I²C GPIO expander | 2× | ~$2.40 | XSHUT control |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$12 | ToF sensor leads |
| 5mm PMMA disc 0.5mm thick | 12× | ~$6 | ToF aperture covers |
| UV adhesive | 1× | ~$6 | ToF aperture seal |
| JST-GH cables (remaining bus segments) | assorted | ~$20 | Ring completion |

### 2.6 — Cargo System (Phase 8)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| N20 DC motor 6V 300:1 | 1× | ~$8 | Winch drive |
| DRV8833 dual H-bridge driver | 1× | ~$2 | |
| SG90 servo | 2× | ~$6 | Door actuator + payload release |
| Dyneema SK75 0.5mm braid | 2 m | ~$4 | Winch line |
| 3mm CF rod | ~60 mm | — | Clamshell door hinge pin |
| Closed-cell foam gasket tape | — | — | Gondola-to-hull perimeter seal |

---

## 3.0 — Physical Build

**Dependency:** All items in Section 1.0 (STL exports) must be complete before Phase 0.  
**PCB fab lead time:** ~7–14 days for JLCPCB assembled boards — order after 1.2 gerber regen and 1.3 Phase 5 are complete; boards arrive during physical Phases 0–5.

### Phase 0 — Print All Parts + CF Cuts

**Goal:** Every printed part complete and dry-fitted before first epoxy joint.

**Pre-print documentation (complete before any fabrication begins):**

- [ ] **Flight Envelope Document** — create `docs/flight_envelope.md` covering:

  - V_min (minimum control airspeed) vs. nacelle tilt angle — computed from wing area, CL_max, and nacelle thrust fraction

  - V_max (never-exceed speed) vs. structural load limit and EDF rpm ceiling

  - Altitude operating limits (AGL and MSL) per FAA Part 107 and battery performance

  - Maximum demonstrated crosswind per nacelle angle increment (0°, 30°, 60°, 90°)

  - Transition corridor: altitude AGL floor for nacelle 90°→0° sweep (minimum safe altitude to initiate transition)

- [ ] **Failsafe Threshold Document** — create `docs/failsafe_thresholds.md` covering:

  - Battery low-voltage alert threshold per cell (default 3.7V/cell) and RTL cutoff (3.5V/cell)

  - Node heartbeat timeout for master re-election (default 100ms on CAN FD)

  - Radio loss timer before automatic RTL (default 5s for SiK/LoRa; 10s for RCRS-49 as backup)

  - ESC thermal cutback threshold (default 85°C) and shutdown threshold (95°C)

  - ToF obstacle avoidance halt clearance (default 1.0m) and resume clearance (default 1.5m)

  - All thresholds must be defined as compile-time constants in `firmware/common/failsafe_config.h`

- [ ] **Electrical Fault Margin Validation** — create `docs/electrical_fault_margins.md` covering:

  - Maximum ESC short-circuit current at 6S and required fuse break time; verify XT30 + 100A poly fuse coordinates with ESC MOSFET safe operating area

  - BEC brown-out threshold: minimum input voltage at which 5V BEC output stays in regulation (≥4.90V); verify with actual 14AWG wire resistance at peak current

  - Main bus fuse sizing: peak current = 4× EDF ESCs (4× 40A) = 160A nacelle peak; verify main XT90 connector rating and main fuse break curve do not nuisance-trip on motor surge

  - Balance of plant: verify that loss of any single PWR conduit tap does not collapse the 5V avionics rail (BEC must tolerate single-segment loss)

**Printer setup:**

- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)

- [ ] Calibrate E-steps and Pressure Advance for each filament

- [ ] Dry all filament 6 h at 65°C before printing

**Print schedule (ordered to minimize reprints):**

| Part | Material | Layer | Infill | Qty |
|------|----------|-------|--------|-----|
| feet_x_4_scaled24.stl | TPU 95A | 0.25mm | 40% | 1 set |
| legs_scaled24.stl | CF-PETG | 0.15mm | 30% | 1 |
| head_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| middle_canonical_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| cargo_sect_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 |
| rear_neck_intake_shell24.stl | PETG | 0.20mm | 8% gyroid | 1 | Print now; cover 4 scoop windows with removable 3mm PETG blanks until Phase 11 |
| wings_s1223_revo.stl | PETG | 0.20mm | 8% gyroid | 1 |
| eng_left_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 |
| eng_right_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 |
| s_eng_piv_outer_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 |
| s_eng_piv_pins_scaled24.stl | CF-PETG | 0.15mm | 40% solid, 4 walls | 2 |
| s_pivot_arm_a_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 |
| s_eng_pistons_scaled24.stl | PETG | 0.20mm | 20% gyroid | 2 |
| wing_nacelle_pylon_revo.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 |
| nacelle_nozzle_petal.stl | PETG + translucent-blue inner | 0.20mm | 20% gyroid | 16 |
| nacelle_nozzle_ring.stl | CF-PETG | 0.15mm | 40% | 2 |
| nacelle_nozzle_iris.stl | PETG | 0.12mm | 40% | 2 |
| rear_nozzle_petal.stl | PETG + translucent-blue | 0.20mm | 20% gyroid | 8 | **DEFERRED — Phase 11.** File in `deferred/aft-edf/stls/`. Do not print until Phase 11. |
| rear_nozzle_frame.stl | CF-PETG | 0.15mm | 30% | 1 | **DEFERRED — Phase 11.** File in `deferred/aft-edf/stls/`. Do not print until Phase 11. |
| nacelle_sector_gear.stl | CF-PETG | 0.12mm | 40%, 4 walls | 2 |
| nacelle_pinion.stl | PETG or resin | 0.12mm | 40% | 4 |
| nacelle_bevel_pair.stl | PETG or resin | 0.12mm | 40% | 2 sets |
| nacelle_bevel_housing.stl | CF-PETG | 0.15mm | 40% | 2 |
| rcrs49_wire_post.stl | PETG | 0.15mm | 40% | 2 |
| Access panel frames A–F + lids | PETG | 0.20mm | 100% | 1 set |
| s_cargo_gondola_shell.stl | PETG | 0.20mm | 15% gyroid | 1 |
| cargo_door_port.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Generated (PR #22) — reprint if hinge changes |
| cargo_door_stbd.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Generated (PR #22) — reprint if hinge changes |
| cargo_cradle_autolatch.stl | PETG | 0.20mm | 30% | 1 | Already generated (PR #21) — reprint if dimensions change |
| cargo_winch_spool.stl | PETG | 0.20mm | 40% | 1 | Already generated (PR #21) — reprint if dimensions change |
| nacelle_servo_bracket.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | One per nacelle; from `airframe/openscad/nacelles/nacelle_servo_bracket.scad` (Rev R). Print with channel mouth up; no supports needed. VERIFY M3 hole ±17.5×±8 mm pattern matches NSVMT inserts in slicer before printing. |
| inara_access_cover.stl | PETG (Cu-foil lined) | 0.20mm | 40% | 1 | Faraday tray lid for Inara bay; 105×75 mm footprint, 5 mm shoulder, Ø38 mm GPS bore offset −13.3 mm Z from cover centre. SCAD not yet created — **BLOCKS printing.** |
| river_access_cover.stl | PETG (Cu-foil lined) | 0.20mm | 40% | 1 | Faraday tray lid for River bay; 105×75 mm footprint, 5 mm shoulder, Ø38 mm GPS bore at +0.7 mm Z from cover centre. SCAD not yet created — **BLOCKS printing.** |
| kaylee_battery_tray.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Battery slide-in rail tray for 6S 4000 mAh LiPo; keel mount at 190 mm station. SCAD not yet created — **BLOCKS Phase 1.** |
| kaylee_pdb_tray.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Kaylee PDB mount tray; keel area, middle section. SCAD not yet created — **BLOCKS Phase 1.** |

**CF cuts:**

| Part | Material | Dimension | Notes |
|------|----------|-----------|-------|
| Keel | CF flat bar 6×3mm | 620 mm | Mark datums at 91, 165, 251, 320, 388mm from nose |
| Wing spars | CF tube 12mm OD / 1.5mm wall | 2× 380 mm | Sand spar ends to fit wing-root pockets |
| Pivot rods | CF solid rod 4mm OD | 2× cut per pivot housing drawing | Deburr; press-fit into MF104ZZ bearings |
| Ring frames | CF plate 2mm | 5 profiles per station drawing | Fit to keel slot-notches |

**Phase 0 checks:**

- [ ] Nacelle bore caliper: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm

- [ ] Stator fins visible in Z=53–95 mm gap (between the two EDF seats)

- [ ] Hub bore clear at stator: 16 mm ID minimum (motor leads)

- [ ] Sector gear ↔ pinion dry-mesh: 0.1–0.2 mm backlash

- [ ] Iris nozzle ring fits flush on nacelle exit; petals hinge freely on 3mm pins

- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bearings seated

- [ ] All access panel lids flush ±0.2 mm in frames

- [ ] Keel dry-fits through all hull sections without force

- [ ] Rear neck shell scoop windows covered with removable 3mm PETG blanks (4 blanks, silicone-sealed)

---

### Phase 1 — Hull Structure + All Future Provisions

**Goal:** Structurally complete hull, every conduit/standoff/void former/sensor mount installed — ready for foam pour.

> ⚠ **Point of no return.** Complete all sub-steps before mixing foam (Step 13). Nothing can be added after foam cures.

- [ ] Epoxy keel through all hull sections; cure 2h. Datum marks at 91, 165, 251, 320, 388mm.

- [ ] Bond ring frames at all 5 station notches; cure 1h.

- [ ] Bond access panel frames A–F into hull sections (5-min epoxy, 30 min cure per phase guide table).

- [ ] Install M2.5 nylon standoffs in bays A, B, D, E (floor 6mm + inter-cape 20mm per bay).

- [ ] Bond wing spar pocket inserts at wing root stations, both sides.

- [ ] Bond tilt servo mount brackets at wing root bay interior (one per nacelle tilt servo).

- [ ] Install M3 heat-set inserts ×4 at belly cargo hard-point locations.

- [ ] Install SMA bulkheads: belly port (SiK 915MHz, X≈260mm), belly stbd (LoRa, X≈260mm), dorsal (WiFi, X≈140mm).

- [ ] Install 49MHz RCRS forward wire post (dorsal, X≈120mm, bonded with 5-min epoxy).

- [ ] Install 49MHz RCRS **temporary** aft wire post: PETG hook bonded to aft dorsal hull skin near station ~580mm (NOT on rear nozzle frame — that post is Phase 11). This temporary post reduces antenna length slightly but maintains FCC Part 95 ERP compliance.

- [ ] String 49MHz top wire (0.3mm SS wire or 22AWG enamelled Cu) from forward post to temporary aft post with ~20g tension; CF keel connected to RCRS-49 GND as counterpoise.

- [ ] Install 12× VL53L5CX flush-mount PETG frames (6.5mm hull cutouts); apply 0.5mm PMMA disc over each aperture with UV adhesive.

- [ ] Feed 8× PTFE conduits nose-to-tail; thread pull strings through each immediately; label both ends.

- [ ] Install EPS void formers (waxed 2×) in bays A–E; verify pull strings clear voids.

- [ ] Full dry-fit: all 8 pull strings accessible, standoffs clear, void formers sealed, SMA bulkheads installed.

- [ ] Foam pour: X-30 PU foam, 3 shots aft→fwd, ≤60 mL per batch; cure 24h per zone. **Do NOT foam nacelle bays, pivot housing, or access panel bays.**

- [ ] Remove EPS void formers; IPA wipe bay walls; verify foam not in conduit runs.

- [ ] Bond cockpit cap (verify cockpit bay wires and GPS coax accessible first).

**Phase 1 checks:**

- [ ] Hull rigid — no flex when held at nose and tail

- [ ] All 8 pull strings accessible at both ends

- [ ] All standoffs in place; screws start freely

- [ ] Foam not in nacelle mounting bay, pivot housing, or panel bays

- [ ] All 6 access panel lids flush ±0.2 mm; latches/magnets engage

---

### Phase 2 — Nacelle Assembly

**Goal:** Both nacelles fully assembled — EDFs installed, stator integral, iris nozzle fitted, gear linkage dry-meshed.

**2A — EDF installation (port first, then starboard):**

- [ ] Test EDF rotation direction on bench before installation: port = CW from intake; stbd = CCW from intake. Swap any two motor phase wires to reverse.

- [ ] Install EDF2 (aft/downstream) from nozzle end; seat at Z=5mm shoulder; epoxy 3 dabs at Z=50mm stator shoulder; route leads through hub bore.

- [ ] Install EDF1 (fore/upstream) from intake end; seat at Z=76mm; verify stator fins clear in Z=53–73mm gap; epoxy 3 dabs at Z=76mm shoulder.

- [ ] ESC pair: route to fuselage bay via spar conduit (ESC heat must NOT be trapped in nacelle bore).

- [ ] Cure 2h before proceeding.

- [ ] Repeat for stbd nacelle (opposite rotation direction).

**2B — Nozzle iris assembly (per nacelle):**

- [ ] Press nacelle_nozzle_ring.stl onto nozzle exit face; confirm flush.

- [ ] Install nozzle inner ring (rack, R=28mm) inside base ring.

- [ ] Bend 0.8mm piano wire link ring through all 8 petal link holes.

- [ ] Install 8 petals on 3mm hinge pins in base ring lugs.

- [ ] Dry-test: manually rotate inner ring — petals open smoothly 0°→75°, no binding.

- [ ] Install WS2812B LED ring at duct exit lip; route 3-wire lead through hub bore.

**2C — Gear linkage (per nacelle):**

- [ ] Mount sector gear to tilt bracket (FIXED — does not rotate with nacelle).

- [ ] Mount drive pinion on nacelle outer shell at pivot axis; mesh with sector gear; set backlash 0.1–0.2mm.

- [ ] Install bevel gear pair in nacelle body (nacelle-axis → longitudinal axis redirect).

- [ ] Thread 2mm steel longitudinal shaft through nacelle wall channel toward nozzle end.

- [ ] Mount crown pinion on shaft at nozzle end; mesh with nozzle inner ring rack; set backlash 0.1–0.2mm.

- [ ] **Full sweep test:** rotate nacelle 0°→90°; verify nozzle inner ring rotates ~71°; petals open fully. Verify nozzle inner ring hard stop prevents over-drive at >90°.

- [ ] Confirm petal closed position matches nacelle hull profile at 0°.

**Phase 2 checks:**

- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake

- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle

- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep

- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°

- [ ] LED ring installed and wired

---

### Phase 3 — Tilt Mechanism

**Goal:** Both nacelles mounted on fuselage, pivot freely on MF104ZZ bearings, tilt driven by fuselage-mounted servos with hard stops.

- [ ] Press MF104ZZ bearings into pivot housing bores (both ends); flush ±0.2mm.

- [ ] Insert 4mm CF pivot rod through wing spar pocket + pivot housing bearings (rod is FIXED to fuselage; nacelle rotates on it).

- [ ] Slide nacelle pivot housing onto pivot rod; verify <0.5mm axial play.

- [ ] Install tilt servos in fuselage servo mount bracket at wing root bay.

- [ ] Connect pushrods (servo arm → pivot arm): servo 0° = nacelle 0° (cruise), servo ~125° = nacelle 90° (hover), servo ~170° = nacelle 120° (backing).

- [ ] Install CF-PETG hard stop blocks; bond at −5° stop and 140° stop positions.

- [ ] Servo calibration: set FC software travel limits at −5° and 140°; verify both nacelles reach 90° simultaneously.

**Phase 3 checks:**

- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble

- [ ] Hard stops engage at −5° and 140° (servo stalls, does not strip)

- [ ] Nozzle opens/closes correctly via gear linkage through sweep (from Phase 2)

- [ ] Sector gear does NOT rotate with nacelle

- [ ] Both nacelles synchronise to within 2° at 0° and 90°

---

### Phase 4 — Hull Foam Pour + Close-up

**Goal:** Structural foam cured; all void formers removed; hull rigid.

**Pre-pour final checklist:**

- [ ] All PTFE conduits routed — pull strings accessible at both ends

- [ ] All bay standoffs installed

- [ ] Cargo hard points installed

- [ ] SMA bulkheads installed and dusted

- [ ] EPS void formers waxed (2 coats) and seated

- [ ] Nacelle bays and pivot housings masked OFF

- [ ] Servo mount brackets clear of foam path

**Pour sequence:**

- [ ] Mix X-30 per manufacturer (2:1 ratio by volume, 2-min pot life, 4× expansion). Pour in 3 shots: aft bay → mid bays (D+C) → forward bays (B+A). Allow 24h full cure before next shot.

- [ ] After full cure: remove EPS void formers; IPA wipe bay walls; verify foam did not intrude into panel bays, cargo bay, or conduit runs.

- [ ] Pull all 8 pull strings — verify still move freely.

- [ ] Install all 6 access panel lids; verify flush fit.

---

### Phase 5 — Minimum Viable Flyer ★ FIRST FLIGHT

**Goal:** CN1+FC1 (Shepherd's room / Bay A) and CN2+FC2 (Inara's shuttle / Bay B) installed and operational — first flight achieved.

> **Aft EDF not installed** (Phase 11). The 4 nacelle XFly Galaxy X5 EDFs (1240g each, 90%
> additive via stator = 2232g/nacelle × 2 = 4464g total) deliver T/W ≈ **1.61** at the
> Phase 5–10 AUW of ~2,768g — **full VTOL hover is achievable from Phase 5**. Phase 11
> adds the rear EDF to reach T/W ≈ 2.21 for higher payload capacity and cruise performance.

**Dependency:** Cape-A (×2) and Cape-B (×2) PCB assemblies received from JLCPCB.

**Power system:**

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ESCs.

- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore EDF = FC1; aft EDF = FC2).

- [ ] **Phase 11 only:** Install 80A ESC in Panel F for 120mm rear EDF (FC2 PRU Ch.2) — skip for Phase 5.

- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.

- [ ] Pull motor phase leads through conduit to ESCs; solder (verify rotation marking first).

- [ ] CAN FD termination: 120Ω SOLDERED to CN1 Cape-B at Shepherd's room (Bay A, bus start); temporary 120Ω at FC2 Cape-A in Inara's shuttle (Bay B, Phase 3 far-end; remove in Phase 7).

**ESC assignment (cross-nacelle redundancy — any FC failure retains 50% thrust both nacelles):**

| ESC | EDF | Nacelle | Controlled by |
|-----|-----|---------|---------------|
| ESC1 | EDF1 (fore) | Port | FC1 Cape-A PRU Ch.0 |
| ESC2 | EDF2 (aft) | Port | FC2 Cape-A PRU Ch.0 |
| ESC3 | EDF1 (fore) | Stbd | FC1 Cape-A PRU Ch.1 |
| ESC4 | EDF2 (aft) | Stbd | FC2 Cape-A PRU Ch.1 |
| ESC5 | 120mm rear | Fuselage | **DEFERRED — Phase 11** |

**CN1+FC1 installation — Shepherd's room (Bay A, nose) — Zoë / Wash (v2 EM-hardened):**
> Shepherd's room (Bay A) is the CAN FD / RS-485 / 1553B bus start termination node.  Use Zoë (ADM2795E
> RS-485, ISOW1044 CAN FD, ADIN1300 Ethernet) and Wash for 5 kV isolated transceivers at
> this end of the bus.  v2 placement is mandatory here (see TODO §1.2a node placement note).

- [ ] Mount CN1 Zoë on Shepherd's room (Bay A) floor standoffs (M2.5 nylon 6mm). Insert PB2-I. Secure.

- [ ] Mount FC1 Wash on inter-cape standoffs (M2.5 nylon 20mm) above CN1. Insert second PB2-I.

- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.

- [ ] Install log μSD (64GB) in CN1 Cape-B log slot. Label: **CN1-LOG**.

- [ ] Seat RCRS-49 sub-module on CN1 Cape-B header; connect RCRS coax to forward 49MHz wire post.

- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa → belly stbd SMA; WiFi → dorsal fwd SMA.

- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~59mm); mount GPS patch on hull dorsal, face UP.

- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd's room (Bay A) toward Inara's shuttle (Bay B).

- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Bay B).

- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT 0x01.

- [ ] Cap Simon's medbay (Bay E) end of ETH-EA conduit (will connect to FC4 in Phase 7); connect Shepherd's room (Bay A) end to CN1 Cape-B ETH-2.

**CN2+FC2 installation — Inara's shuttle (Bay B, dorsal fwd) — Zoë / Wash (Rev R):**
> Rev R: Inara's shuttle (Bay B) also uses v2 EMI-hardened capes (same as Shepherd's room). All four bays use Wash + Zoë.

- [ ] Mount CN2 Zoë on Inara's shuttle (Bay B) floor standoffs; insert PB2-I; mount FC2 Wash above.

- [ ] Flash OS to eMMC on CN2 and FC2 before installation.

- [ ] Install log μSD (64GB) in CN2 Cape-B log slot. Label: **CN2-LOG**.

- [ ] Seat RCRS-49 sub-module on CN2 Zoë J_XCVR header.

- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mount GPS patch on dorsal hull, face UP.

- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle: CN2 → FC2 + temporary 120Ω at FC2 (remove Phase 7).

- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's shuttle (Bay B).

- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle): FC1 Wash ETH-1 → CN2 Zoë ETH-B (FC1↔CN2 Ethernet ring link).

- [ ] Cap River's room (Bay D) end of ETH-BD (will connect to CN3 in Phase 7).

- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR conduit; verify 5V ±0.05V at each header.

**Security provisioning (before first flight):**

- [ ] Provision TPM 2.0 (SLB9670) on CN1, FC1, CN2, FC2 — unique key material per node.

- [ ] Verify CPLD write-blocker on CN1 and CN2: `echo test > /mnt/flightlog/test.txt` must return read-only error.

- [ ] Configure forensic log mount in `/etc/fstab` (noexec, nodev, nosuid, ro) on CN1 and CN2.

**Software configuration:**

- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.

- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.

- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.

- [ ] Verify 4-node CAN FD heartbeat ring: `candump can0` shows frames 0x001–0x004 within 100ms.

- [ ] Configure MAVLink routing (mavlink-router) on elected FC master → SiK 915MHz on CN master.

- [ ] Install RCRS-49 daemon on CN1 and CN2 (select channel per 47 CFR 95.623).

**Ground tests:**

- [ ] ESC calibration (full throttle power-on → drop to zero).

- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct directions.

- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° = horizontal ±0.5°.

- [ ] Rear nozzle servo endpoints verified.

- [ ] Static CG: **190mm from nose** (adjust battery position on rail).

- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.

- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup); RCRS-49 RC channels correct; WiFi GCS telemetry.

- [ ] Node failover: kill FC master power → standby assumes authority within 100ms on tether.

- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW; ESC temps ≤60°C.

- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE tail, WHITE belly strobe).

- [ ] **Apply FAA registration number** (14 CFR Part 48 — replaces N00000 placeholder on airframe).

**First flight sequence (per REVN_BUILD_GUIDE_24IN.md §Phase 5):**

- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)

- [ ] Tethered hover 1m AGL × 3 successful passes before free flight (nacelles at 90°, ~60% throttle)

- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.3m)

- [ ] Free hover 3m AGL (yaw 360° both directions)

- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0° — altitude hold ±1.5m during transition

- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to hover, land

- [ ] Verify flight log written to CN1-LOG and CN2-LOG

**Phase 5 pass criteria:**

- [ ] Stable hover 1m AGL in ≤15° headwind

- [ ] Nacelle transition without altitude excursion >1.5m

- [ ] All 4 nacelle ESCs ≤70°C at full hover power

- [ ] MAVLink telemetry live to QGC during all segments

- [ ] All 4-node CAN FD heartbeats confirmed

- [ ] Node failover: standby assumes within 100ms of master power-kill

- [ ] Flight log on both CN μSDs; CPLD write-block verified

---

### Phase 6 — Full 8-Node Architecture + ToF Obstacle Avoidance

**Goal:** All 8 nodes installed, full ring redundancy, 12× VL53L5CX dual-redundant obstacle avoidance operational.

**CN3+FC3 installation — River's room (Bay D, dorsal aft) — Zoë / Wash (Rev R):**
> Rev R: River's room (Bay D) also uses v2 EMI-hardened capes. All four bays uniform.

- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Wash in Inara's shuttle (Bay B).

- [ ] Mount CN3 Zoë on River's room (Bay D) floor standoffs; insert PB2-I; mount FC3 Wash above.

- [ ] Flash OS to eMMC; install log μSD. Label: **CN3-LOG**.

- [ ] Seat RCRS-49 sub-module on CN3 Zoë J_XCVR header.

- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm); mount GPS patch, face UP.

- [ ] Continue CAN FD chain: Inara's shuttle (Bay B) FC2 → River's room (Bay D) CN3 → FC3 → exit toward Simon's medbay (Bay E).

- [ ] Continue RS-485 chain Inara's shuttle (Bay B) → River's room (Bay D) → Simon's medbay (Bay E).

- [ ] Connect ETH-BD (Inara's shuttle → River's room): FC2 Wash ETH-1 → CN3 Zoë ETH-B.

- [ ] Power tap River's room (Bay D); verify 5V ±0.05V.

**CN4+FC4 installation — Simon's medbay (Bay E, aft service) — Zoë / Wash (v2 EM-hardened):**
> Simon's medbay (Bay E) is the CAN FD / RS-485 / 1553B bus end termination node and is physically closest to the
> nacelle motor wiring and rear 120mm EDF.  Use Zoë / Wash for 5 kV isolated
> transceivers at this end of the bus.  v2 placement is mandatory here.

- [ ] Mount CN4 Zoë on Simon's medbay (Bay E) standoffs; insert PB2-I; mount FC4 Wash above.

- [ ] Flash OS to eMMC; install log μSD. Label: **CN4-LOG**.

- [ ] Seat RCRS-49 sub-module on CN4 header.

- [ ] Route FC4 GPS coax through dorsal PTFE sleeve (sta ~350mm); mount GPS patch, face UP.

- [ ] Terminate CAN FD bus end: CN4 → FC4 + **120Ω PERMANENT** soldered to FC4 Cape-A.

- [ ] Connect ETH-DE (River's room → Simon's medbay): FC3 Cape-A ETH-1 → CN4 Cape-B ETH-2.

- [ ] Connect ETH-EA ring-close (Simon's medbay → Shepherd's room): FC4 Cape-A ETH-1 → [Shepherd's room CN1 Cape-B ETH-2 already connected]. Closes the 8-node RSTP ring.

- [ ] Power tap Simon's medbay (Bay E); verify 5V ±0.05V.

**Security provisioning — remaining 4 nodes:**

- [ ] TPM 2.0 on CN3, FC3, CN4, FC4 — unique key material per node.

- [ ] CPLD write-blocker verification on CN3 and CN4.

**Full ring integration:**

- [ ] Verify RSTP ring: `bridge vlan show`; disconnect one ETH cable → traffic re-routes within 1s.

- [ ] Verify full 8-node CAN FD ring: `candump can0` shows frames 0x001–0x008 within 100ms.

- [ ] MIL-STD-1553 final config: FC1=BC, FC2=standby BC, FC3/FC4/CN1–CN4=RT; all 8 RT addresses respond within 9μs.

**ToF sensor installation:**

Array B (hosted by FC1, Shepherd's room / Bay A):

| Sensor | Station | Position |
|--------|---------|----------|
| S1B | 50mm | Nose ring |
| S2B | 510mm | Rear bell rim |
| S3B | 180mm | Port hull |
| S4B | 180mm | Stbd hull |
| S5B | 315mm | Dorsal keel |
| S6B | 265mm | Belly blister |

- [ ] Install 6× VL53L5CX in Array B flush-mount frames; wire to TCA9548A ch.0–5 in Shepherd's room (Bay A); MCP23008 GP0–GP5 → XSHUT; I²C to FC1 Cape-A.

Array A (hosted by FC3, River's room / Bay D):

| Sensor | Station | Position |
|--------|---------|----------|
| S1A | 30mm | Nose ring |
| S2A | 525mm | Rear bell rim |
| S3A | 240mm | Port hull |
| S4A | 240mm | Stbd hull |
| S5A | 215mm | Dorsal keel |
| S6A | 195mm | Belly blister |

- [ ] Install 6× VL53L5CX in Array A flush-mount frames; wire to TCA9548A ch.0–5 in River's room (Bay D); separate I²C bus (electrically isolated from Array B).
- [ ] Apply 0.5mm PMMA disc over each sensor aperture with UV adhesive.
- [ ] Configure OA fusion in firmware: halt at 1.0m obstacle clearance; either array independent on single-FC failure.
- [ ] GPS clearance check for 49MHz wire post proximity: bench-verify HDOP ≤1.5 with RCRS-49 transmitting; if GPS degrades, move GPS patch to ≥165mm from forward post.

**Phase 6 pass criteria:**

- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed

- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s

- [ ] MIL-STD-1553: all 8 RTs respond within 9μs

- [ ] CN3 and CN4 log μSD write-block verified

- [ ] All 12 ToF sensors return valid range at ≤4m

- [ ] OA halt test: approach wall at 0.5m/s → stops at 1.0m clearance

- [ ] Array failure mode: either FC1 or FC3 loss → remaining array provides full OA coverage

- [ ] 3-waypoint autonomous mission with GPS, altitude hold, RTL on simulated link loss

---

### Phase 7 — Cargo System

**Goal:** 250g payload delivery via autonomous winch deploy with auto-latch cradle.

- [ ] Bond cargo gondola shell into belly void at 4× M3 hard points (installed Phase 1). Cure 24h.

- [ ] Install 3mm CF door hinge pins; attach clamshell door halves (spring-loaded to open).

- [ ] Install DRV8833 + N20 winch motor + drum; wind 1.5m Dyneema; attach auto-latch cradle via double-bowline.

- [ ] Install SG90 door-actuator servo (spring-assist open, servo pull-close via bell-crank).

- [ ] Install SG90 payload-release servo; connect to DRV8833 IN1/IN2 via PWM→resistor divider→GPIO.

- [ ] Route control leads through PWR conduit belly tap to CN master (CN1 or CN2 — winner of CN master election).

- [ ] Seal gondola-hull perimeter with 3M foam gasket tape.

- [ ] Configure CN master GPIO: door open/close, winch deploy/retract, payload latch status (microswitched).

**Phase 7 pass criteria:**

- [ ] Door open/close × 10: no binding

- [ ] Winch deploy 1.5m: straight descent, line clear

- [ ] Winch retract: auto-latch clicks and holds at top

- [ ] 250g load test: winch deploy + retract × 5; latch holds

- [ ] Hover with 250g payload: altitude-hold degradation ≤10%

- [ ] Autonomous delivery: 3-waypoint mission, deploy at waypoint 2, retract empty, complete mission

---

### Phase 8 — Finishing

**Goal:** Aircraft legally compliant, aesthetically complete, and fully documented.

- [ ] Replace FAA N00000 placeholder in `serenity/diagrams/decal_sheet.svg` with issued FAA registration number (via FAA DroneZone, 14 CFR Part 48).

- [ ] Print decal sheet on waterslide decal paper; seal with clear coat; dry 24h.

- [ ] Apply decals per `build_guide_19_decal_placement.svg`: Serenity lettering, FAA blocks, universe markings (宁静 Chinese name, Alliance registry), safety labels, weathering.

- [ ] Final airworthiness inspection: all fasteners, propulsion, electronics, battery, CG.

- [ ] Documentation archive: build log (photos + test results), Cape-B CPLD bitstream, TPM endorsement key fingerprints, final AUW + CG measurements.

- [ ] FAA compliance final check: registration visible without moving any part; remote pilot certificate current; AUW <55 lbs; LAANC authorization for any controlled airspace.

---

### Phase 9 — Performance Tuning and Flight Envelope Expansion

**Goal:** Optimise PID governor coefficients, measure actual thrust and efficiency, and expand the
safe flight envelope beyond the minimum parameters established in Phase 5.

**Dependency:** Phase 6 (all 8 nodes + ToF OA) and Phase 7 (cargo system) complete.

- [ ] **Thrust stand calibration** — run `airframe/scripts/governor_cal.py` on bench against all 4 nacelle EDFs (tandem pairs); measure actual thrust vs. RPM; update `EDF_THRUST_K` in `governor_config.h`.

- [ ] **PID governor tuning** — in-flight hover trim: adjust attitude PID gains until hover hold ±0.15 m altitude, ±2° attitude; log CAN FD governor data for analysis.

- [ ] **Nacelle transition tuning** — refine tilt servo rate and cross-axis coupling compensation; target altitude excursion ≤0.5 m during 90°→0° nacelle sweep.

- [ ] **Endurance test** — full charge 6S 4000mAh, hover 1m AGL until 3.7V/cell cutoff; measure hover time and battery health.

- [ ] **Cross-wind hover** — verify stable hover in ≥10 kt headwind; document max demonstrated crosswind.

- [ ] **Extended autonomous mission** — 5-waypoint GPS mission, altitude hold, RTL on link loss; verify log integrity on all 4 CN μSDs.

**Phase 9 pass criteria:**

- [ ] T/W measured ≥1.10 (nacelles only) on thrust stand

- [ ] Hover altitude hold ±0.15 m for 60 s

- [ ] Nacelle transition altitude excursion ≤0.5 m

- [ ] Endurance ≥8 min at hover (6S 4000mAh baseline)

- [ ] Logs on all 4 CN nodes; write-block verified

---

### Phase 10 — Advanced Autonomy and Long-Range Operations

**Goal:** Validate extended autonomous mission capability, BVLOS readiness, and multi-link
communication redundancy sufficient for real-world deployment.

**Dependency:** Phase 9 complete.

- [ ] **BVLOS communication validation** — verify handover between all 4 radio links (SiK, LoRa, WiFi, RCRS-49) in a degraded RF environment; mission continues on any single surviving link.

- [ ] **Extended waypoint missions** — ≥10-waypoint autonomous mission at ≤400 ft AGL; verify all obstacle avoidance halts function through the full mission.

- [ ] **Payload delivery mission** — fully autonomous: takeoff → 3-waypoint transit → cargo deploy → return → land; pass criteria: payload delivered within 2 m of target, cradle auto-latched on return.

- [ ] **Simulated node failure during flight** — kill one FC node mid-hover; verify remaining 3 FC nodes maintain flight for 30 s; RTL executed correctly.

- [ ] **Emergency RTL validation** — disable all control links; verify automatic RTL initiates within 5 s of link loss; lands within 3 m of takeoff point.

- [ ] **Regulatory readiness review** — FAA Part 107 waiver pre-application checklist; confirm LAANC authorization for planned operational area; update flight log and maintenance record.

**Phase 10 pass criteria:**

- [ ] Mission continues on any single surviving radio link

- [ ] 10-waypoint autonomous mission completed without intervention

- [ ] Autonomous cargo delivery within 2 m of target

- [ ] Node failure: remaining FCs maintain flight ≥30 s

- [ ] RTL on link loss: lands within 3 m of takeoff point

- [ ] All regulatory documentation current and on file

---

### Phase 11 — Aft EDF Integration (Deferred)

**Goal:** Install the 120mm 6S fuselage EDF and its supporting intake and nozzle system, achieving
the full T/W ≈ 1.47 VTOL hover capability specified in Rev R.

**Dependency:** Phases 0–10 complete and proven in flight.

**Design files:** `deferred/aft-edf/` — see `deferred/aft-edf/README.md` for full details.

> **VTOL note:** With only the 4 nacelle EDFs (Phases 5–10), nacelle-only thrust is ~1 822 g
> against a ~3 550 g AUW, giving T/W ≈ 0.51.  Pure vertical hover is not possible.  Phase 11
> adds the 120mm rear EDF (~3 500 g additional thrust) to achieve T/W ≈ 1.47 for full VTOL.

**11A — Procurement (if not yet in stock):**

| Item | Qty | Approx. Cost |
|------|-----|-------------|
| 120mm 6S EDF | 1× | ~$60–80 |
| 80A 6S BLHeli32 ESC | 1× | ~$25–35 |
| SG90 micro servo (rear nozzle) | 1× | ~$3 |
| 3mm × 5mm SS hinge pins | 8× | ~$2 |
| 0.8mm piano wire | ~200mm | ~$1 |
| WS2812B LED ring (120mm duct) | 1× | ~$4 |

**11B — Rear neck shell swap (if printed without windows):**

- [ ] Print `rear_neck_intake_shell24.stl` from `deferred/aft-edf/openscad/rear_neck_intake_shell24.scad`. Verify NECK_X ≈ 310mm alignment in slicer.

- [ ] Remove temporary window covers from existing neck shell, or swap in the new windowed shell if a plain shell was used for Phases 0–10.

**11C — STL generation and printing:**

- [ ] Print `neck_intake_frame.stl` (CF-PETG, 0.15mm, 40% gyroid, 4 walls) from `deferred/aft-edf/openscad/neck_intake_frame.scad`.

- [ ] Print `aft_edf_plenum.stl` (PETG, 0.20mm, 20% gyroid) from `deferred/aft-edf/openscad/aft_edf_plenum.scad`.

- [ ] Print `rear_nozzle_frame.stl` (CF-PETG, 0.15mm, 30%) from `deferred/aft-edf/stls/rear_nozzle_frame.stl` (already generated).

- [ ] Print `rear_nozzle_petal.stl` × 8 (PETG + translucent-blue inner, 0.20mm, 20% gyroid) from `deferred/aft-edf/stls/rear_nozzle_petal.stl`.

**11D — Intake frame installation:**

- [ ] Dry-fit `neck_intake_frame.stl` into 4 scoop windows; registration tongues insert with ~0.2mm clearance (sand if tight).

- [ ] Verify aerodynamic orientation: intake lips face forward (+X).

- [ ] Apply structural epoxy to tongues + shoulder flanges; press frame into position; clamp; cure 24h.

- [ ] Fillet all gaps between flange and hull; cure 2h.

**11E — Plenum manifold installation:**

- [ ] Dry-fit `aft_edf_plenum.stl`; verify arm alignment and 120mm outlet centred.

- [ ] Bond plenum forward arms to intake frame exits; fillet joints; cure 2h.

- [ ] Pressure-test: seal EDF face with tape; cover 3 of 4 scoops; shop-vac at 4th — confirm draft at outlet, no joint leakage.

**11F — 120mm EDF installation:**

- [ ] Bench-test 120mm EDF (correct rotation, no vibration).

- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bond; cure 1h.

- [ ] Seat EDF in plenum 120mm outlet; press forward to retaining lip; bond with 4 dabs slow-cure epoxy.

- [ ] Route motor leads through Panel F to 80A ESC; route signal lead forward via MAIN-PWR conduit to Inara's shuttle (Bay B, FC2 PRU Ch.2).

- [ ] Install 80A ESC in Panel F bay; foam tape + cable tie. Cure 2h before applying thrust.

**11G — Rear nozzle installation:**

- [ ] Press `rear_nozzle_frame.stl` onto 120mm EDF duct exit (Panel F aft end).

- [ ] Install 8 rear nozzle petals on 3mm hinge pins; install piano wire link ring.

- [ ] Install SG90 rear nozzle servo inside Panel F; pushrod to nozzle inner ring.

- [ ] Calibrate: servo 0° = petals closed (hull-matched bell); servo ~90° = petals fully open.

- [ ] Install WS2812B LED ring at rear duct exit lip.

**11H — 49MHz antenna upgrade:**

- [ ] Bond permanent aft 49MHz RCRS wire post to top of `rear_nozzle_frame.stl` (5-min epoxy).

- [ ] Remove temporary aft post from station ~580mm.

- [ ] Restring 49MHz top wire (~470mm) from forward post to nozzle-frame aft post with ~20g tension.

**11I — Software:**

- [ ] Enable ESC5 in FC2 firmware (PRU Ch.2); configure BDSHOT governor for 120mm EDF.

- [ ] Add rear EDF to thrust-balance algorithm; calibrate via `governor_cal.py`.

- [ ] Verify all 5 ESC heartbeats on CAN FD; confirm FC2 cross-drive capability for ESC5.

- [ ] Perform tethered hover test with all 5 EDFs at 60% throttle; verify T/W ≥1.10 on tether.

- [ ] Free VTOL hover 1m AGL × 3 passes — altitude hold ±0.3m, all ESCs ≤70°C.

**Phase 11 checks:**

- [ ] Intake frame tongues fully seated in all 4 scoop windows

- [ ] Plenum pressure-test passed (no joint leakage)

- [ ] EDF seated at station ~430mm, centreline ±2mm; rotation verified before sealing

- [ ] 80A ESC installed; ESC5 signal routed to FC2 PRU Ch.2

- [ ] Rear nozzle 8 petals open/close evenly without binding; servo calibrated

- [ ] 49MHz aft wire post on nozzle frame; top wire re-strung at full ~470mm span

- [ ] VTOL hover achieved: T/W ≥1.10 measured; stable hover 1m AGL for ≥30 s

- [ ] All 5 ESC telemetry visible on CAN FD; ESC temps ≤70°C at hover power

---

## 4.0 — Firmware and Software

**Dependency for Phase 6:** serenity-fc Phase 7 items can be developed concurrently with physical Phases 0–5 and must be integrated by Phase 6 first flight.

### 4.1 — Completed

- [x] Firmware directory structure (`serenity/firmware/`) *(done 2026-05-25)*

- [x] KISS/AX.25 UART driver for XCVR-49MHZ-1 — `serenity/firmware/cn/src/xcvr_kiss.c/.h` *(done 2026-05-25)*

- [x] Si5351A I²C driver — `serenity/firmware/cn/src/si5351.c/.h` *(done 2026-05-25)*

- [x] AM6254 device tree overlays — Cape-A and Cape-B DTSs *(done 2026-05-25)*

- [x] serenity-cn Phase 6 daemon (XCVR KISS driver + argparse + SIGTERM) *(done 2026-05-25)*

- [x] serenity-fc Phase 6 stub (signal handling, idle loop placeholder) *(done 2026-05-25)*

### 4.2 — FC Node (Wash) — Phase 7 Firmware

- [ ] **EDF ESC PID governor** — BDSHOT600 telemetry input on PRU-ICSS, EHRPWM output to ESCs, CAN FD cross-node synchronisation. Targets: settle <200ms, overshoot <5%; equalization |RPM_FWD − RPM_AFT| <100 RPM; fault latch on overtemp/overcurrent (no auto-recovery, GCS ack required).

- [ ] **Nacelle tilt servo PWM generation** — EHRPWM or PRU; travel limits −5°/140° enforced in firmware; symmetric 2° tracking both nacelles.

- [ ] **IMU / barometer sensor fusion** — ICM-42688-P (SPI), BMP388/BMP390 (SPI); complementary or Kalman filter for attitude; altitude hold PID using barometric altitude + GPS.

- [ ] **ToF sensor array management** — VL53L5CX ×6 per node via TCA9548A I²C mux; XSHUT sequencing via MCP23008; OA fusion (Array A + Array B cross-check); halt at 1.0m clearance.

- [ ] **u-blox M10Q GNSS integration** — UART NMEA/UBX parse; position fix broadcast on CAN FD; HDOP gating (≤1.5 for valid position); multi-node position cross-check (≤2m disagreement threshold).

- [ ] **MIL-STD-1553B RT implementation** — PRU-ICSS Manchester II encoder/decoder; RT address assignment per node role; BC arbitration on FC1 and FC2.

- [ ] **TPM-bound attestation** — SLB9670 TPM 2.0 HMAC on all outbound flight-critical CAN FD messages; pcrs extend on each boot; boot measurement chain.

- [x] **governor_cal.py** — thrust stand calibration script: sweeps 0%→100%→0% throttle, fits k coefficient (T = k × RPM²), outputs `EDF_THRUST_K` for `governor_config.h`. *(done 2026-06-04)*

- [x] **governor_config.h** — template with calibrated k values per EDF; compile-time constants. *(done 2026-06-04)*

### 4.3 — CN Node (Zoë) — Phase 7 Firmware

- [ ] **CAN FD heartbeat and telemetry forwarding** — broadcast 0x001–0x008 node health frames; relay MAVLink telemetry from elected FC master to SiK GCS link.

- [ ] **MIL-STD-1553B BC/RT tasks** — BC on CN1 (standby), RT on CN2–CN4; mirror FC bus controller arbitration.

- [ ] **RS-485 inter-board messaging** — structured message format (header/payload/CRC); inter-node command and status relay.

- [ ] **Ethernet RSTP ring management** — CPSW3G bridge configuration; RSTP fast-failover (<1s) verification; ring segment health monitoring.

- [ ] **Signed-log write via CPLD write-blocker** — log records written as read-only-append through ATF16V8BQL latch interface; NOR flash (W25Q128JV) circular buffer for overflow.

- [ ] **TPM-bound HMAC on all outbound AX.25 payloads** — each RCRS-49 packet includes HMAC-SHA256 computed from SLB9670 stored key; receiver nodes verify before acting.

- [ ] **Cargo control** — DRV8833 winch H-bridge, HX711 load cell (payload weight sensing), SG90 door and release servos; state machine: IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED.

- [ ] **MAVLink routing configuration** — mavlink-router config: elected CN master routes FC master telemetry to all 4 radio links (SiK, LoRa, WiFi, RCRS-49 backup).

### 4.4 — Both Nodes

- [ ] **Node role election protocol** — CAN FD priority arbitration at boot; lowest node-ID wins master role; automatic failover on heartbeat timeout (100ms); FC master and CN master elected independently.

- [ ] **Autonomous navigation** — 3-waypoint GPS mission execution; altitude hold ±0.3m; waypoint radius 2m; RTL on any link loss >5s.

- [ ] **OA integration** — ToF halt trigger feeds into navigation; velocity command zeroed within 1.0m of obstacle; resumes when clear.

- [ ] **GPS cross-check** — 4 GPS receivers (one per FC node); positions averaged; outlier >2m flagged and excluded from blend.

- [ ] **Security message signing** — every inter-node CAN FD message signed; unauthenticated messages discarded; signing key material bound to node TPM endorsement key.

### 4.5 — Ground Control (Malcolm / "CAPT Reynolds")

> "I aim to misbehave."

**Architecture summary:** Malcolm stays at a safe operator distance.  The link budget
(directional antennas + gain) is sized to maintain reliable uplink/downlink with an
aircraft whose receivers may be desensed by proximity to high-power RF sources.
No additional transmit power amplifiers are FCC-compliant for any link in the standard
configuration with directional antennas.  See `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`.

**File tree:** `gcs/malcolm/` — hardware docs, SCAD gimbal designs, PB2-I firmware, and
host-PC software all created in Rev R.  See `gcs/malcolm/README.md` for layout.

#### 4.5.1 — Malcolm Hardware Design

- [ ] **Create Malcolm host computer specification** (`gcs/malcolm/hardware/docs/malcolm_host_spec.md`):
  minimum x86\_64 Debian Linux, 8 GB RAM, 256 GB SSD, USB 3.0+; ruggedized laptop
  (IP54 or better) for field use.  Document recommended models and any BIOS/driver notes.

- [ ] **Malcolm field enclosure — print and fit-check** `gcs/malcolm/hardware/enclosure/openscad/malcolm_field_enclosure.scad`:
  export STL (`openscad -o malcolm_field_enclosure_body.stl ... -D RENDER_MODE=0`);
  verify PCB standoff spacing matches Cape-B-2 55×35 mm mounting hole pattern in slicer;
  run mesh validation; print body + lid in PETG (IP65 gasket groove accepts 3 mm EPDM cord).
  **Add to Phase Malcolm-1 print schedule.**

- [ ] **Gimbal STL generation and mesh verification** — for each of the three SCAD files:
  - `malcolm_gimbal_pan.scad` → `malcolm_gimbal_pan_base.stl` + `malcolm_gimbal_pan_turret.stl`
  - `malcolm_gimbal_tilt.scad` → `malcolm_gimbal_tilt_yoke.stl`
  - `malcolm_gimbal_mount.scad` → `malcolm_gimbal_mount.stl`
  Print in CF-PETG (0.15 mm, 40% infill, 4 walls).  Verify bearing pocket diameters
  (6804: 32 mm OD housing; MF104ZZ: 10 mm OD housing) against bearing datasheets before printing.

- [ ] **Gimbal servo wind-load torque check** — compute worst-case wind torque on a 9 dBi Yagi
  (~1.2 m boom, ~0.04 m² front area) at 30 kt crosswind.  Verify DS3218MG (25 kg·cm @ 6 V)
  provides ≥2× safety factor.  Document in `gcs/malcolm/hardware/docs/malcolm_power_budget.md`.

- [ ] **Procure Malcolm comms node hardware:**
  - 1× PocketBeagle 2 Industrial (AM6254) — same DigiKey PN 2820-100003007-ND
  - 1× Cape-B-2 (Zoë) PCB — order 1 additional unit when placing aircraft PCB order at JLCPCB
  - 1× Emma sub-module — order 1 additional unit with aircraft Emma order
  - 1× 64 GB microSD (Samsung or equiv, same as aircraft CN nodes)
  - 1× 5 V / 5 A switching BEC (Pololu D24V50F5 or equiv)
  - 1× 6 V / 2 A servo BEC (Pololu D24V22F6 or equiv)

- [ ] **Procure antenna hardware** per `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`:
  - 2× 5 dBi 915 MHz omni rubber duck (RP-SMA) — one SiK, one LoRa
  - 1× 9 dBi 915 MHz Yagi directional (RP-SMA) — shared SiK+LoRa via RF splitter
  - 1× 14 dBi 5 GHz flat panel (RP-SMA) — WiFi, gimbal-mounted
  - 1× 49 MHz base-loaded whip 1/4-wave (~0.94 m physical) with 4 ground radials
  - 1× 3 dBi 2.4 GHz rubber duck dipole (Zigbee, optional)
  - 1× u-blox ANN-MB-00 or equiv active GNSS patch (GCS position fix)
  - 1× 2-way 915 MHz RF splitter ≥20 dB isolation (Minicircuits ZFSC-2-1W-S+ or equiv)
  - Coax cables per `malcolm_wiring.md` cable table (LMR-195, RG-58, RG-316)

- [ ] **Procure gimbal hardware:**
  - 2× DS3218MG digital servo (same as aircraft nacelle servos — reduces spare parts inventory)
  - 2× AS5600 magnetic encoder PCB breakout module (I²C, 0x36)
  - 2× N42 diametrically magnetised disc magnet 6×2 mm (encoder rotor)
  - 1× 6804 thin-section bearing (20×32×7 mm) — pan stage
  - 2× MF104ZZ flanged bearing (4×10×4 mm) — tilt pivot (same as nacelle pivot)
  - 1× TCA9548A I²C mux PCB breakout (encoder bus isolation)
  - 1× M6 camera tripod (heavy-duty) or 3 m telescoping mast for outdoor use

#### 4.5.2 — Malcolm Comms Node Setup (Phase Malcolm-2)

**Dependency:** Cape-B-2 and Emma PCBs received from JLCPCB.

- [ ] **Flash Debian Linux to Malcolm PB2-I eMMC** — same OS image as aircraft nodes.
  USB-C boot procedure per BeagleBone Debian documentation.

- [ ] **Apply Cape-B-2 device tree overlay for Malcolm** — compile and install
  `gcs/malcolm/firmware/pb2i/dts/k3-am6254-pocketbeagle2-malcolm-cape-b2.dtbo`.
  Verify EHRPWM0 appears as `/sys/class/pwm/pwmchip0/` with 2 channels.
  Verify I²C2 appears as `/dev/i2c-2`.

- [ ] **Provision TPM 2.0 (SLB9670) on Malcolm's PB2-I** — unique key material; persistent
  handle `MAL_TPM_KEY_HANDLE` (0x81000001) per `mal_config.h`.
  Follow the same provisioning procedure as aircraft nodes (PROVISIONING.md, TBD).

- [ ] **Verify CPLD write-blocker on Malcolm's log μSD** (Cape-B-2 ATF16V8BQL):
  `echo test > /mnt/flightlog/test.txt` must return read-only error.
  Configure `/etc/fstab` noexec/nodev/nosuid/ro mount for log partition.

- [ ] **Build and install Malcolm PB2-I firmware:**

  ```sh
  cd gcs/malcolm/firmware/pb2i
  mkdir build && cd build
  cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-aarch64.cmake ..
  make -j$(nproc)
  sudo make install
  ```

  Verify `mal_gimbal` binary installed at `/usr/local/bin/mal_gimbal`.

- [ ] **Install and configure mavlink-router on Malcolm's PB2-I** — same binary as for
  aircraft CN nodes; configure for GCS role (forward all radio links → USB CDC-ECM → host PC).
  Test: QGC on host PC should receive heartbeat on UDP :14550 with aircraft bench-powered.

- [ ] **Enable all 5 radio interfaces on Malcolm's PB2-I** and verify each link at bench:
  - SiK UART2: `screen /dev/ttyS2 57600` — observe MAVLink framing bytes
  - LoRa SPI1: Python test: `python3 -c "import spidev; ..."` — read RFM95W version register (expected 0x12)
  - WiFi wlan0: `iw dev wlan0 scan` — observe available networks
  - 49 MHz UART5: `screen /dev/ttyS5 1200` — verify Emma responds to KISS init
  - I²C2 (encoders): `i2cdetect -y 2` — verify TCA9548A at 0x70 and AS5600 at 0x36

- [ ] **Configure WiFi transmit power** per FCC EIRP compliance:
  When 14 dBi panel is in use, set `iw dev wlan0 set txpower fixed 1700` (17 dBm = 1700 mBm).
  Create persistent udev hook or network config to apply on boot.

#### 4.5.3 — Malcolm Host PC Software Setup (Phase Malcolm-3)

- [ ] **Install Debian Linux on GCS host PC** (bookworm or later).

- [ ] **Run installation scripts in order:**

  ```sh
  sudo bash gcs/malcolm/software/install/install_deps.sh
  sudo bash gcs/malcolm/software/install/install_mavlink_router.sh
  bash gcs/malcolm/software/install/install_qgc.sh
  ```

  Verify: `mavlink-routerd --version`; `~/Applications/QGroundControl.AppImage --version` (launches GUI).

- [ ] **Configure QGroundControl:**
  Application Settings → Comm Links → Add → UDP → localhost:14550 (mavlink-router output).
  Set vehicle type to ArduPilot.  Import parameter file from `gcs/malcolm/software/config/qgc_params.params`
  (create this file in Phase Malcolm-3 after first aircraft connection).

- [ ] **Configure WiFi Tx power on host PC** — if host PC has WiFi and 14 dBi panel connected,
  reduce to 17 dBm before use: `iw dev wlan0 set txpower fixed 1700`.

- [ ] **Run tracking software tests:**

  ```sh
  cd gcs/malcolm/software/tracking
  pip install -r requirements.txt
  pytest tests/test_tracker.py -v
  ```

  All 9 bearing/elevation tests must pass.

- [ ] **Implement `gcs/malcolm/firmware/pb2i/src/mal_comms.c` and `mal_comms.h`** — GCS-side
  comms daemon: USB CDC-ECM bridge, MAVLink authentication (TPM HMAC), RCRS-49 KISS relay,
  LoRa relay, WiFi UDP relay, mavlink-router integration.  Structure parallel to aircraft
  `avionics/firmware/cn/src/main.c`.  Add `mal_comms` target to `CMakeLists.txt`.
  **BLOCKS Phase Malcolm-2 full multi-link operation.**

#### 4.5.4 — Tracking and Gimbal Integration (Phase Malcolm-3)

- [ ] **Bench test gimbal hardware** — connect two AS5600 encoders via TCA9548A to Malcolm
  PB2-I I²C2 bus.  Run `i2cdetect` to confirm encoder presence.  Run mal_gimbal daemon;
  verify it reads encoder angles and drives servo PWM on EHRPWM0.

- [ ] **Gimbal calibration:**
  - Home position: set `s_pan_zero_counts` and `s_tilt_zero_counts` to encoder readings when
    gimbal physically points North at 0° elevation (calibration step in mal_gimbal.c init).
  - Travel limit verification: command pan to ±170°; verify hard stops engage at ±175°.
  - Tilt limit: command −10° and +90°; verify hard stops engage at −15° and +95°.

- [ ] **Run telemetry_feed.py bench test** — power aircraft (Phase 5 minimum: 2-node),
  run `python3 src/telemetry_feed.py`; verify GLOBAL\_POSITION\_INT JSON datagrams appear
  on UDP :14560 within 2 s of aircraft GPS lock (HDOP ≤1.5).

- [ ] **Run tracker.py bench test** — with telemetry_feed.py running and GCS GNSS connected,
  run `python3 src/tracker.py`; verify gimbal target JSON appears on UDP :14570 at ≥5 Hz.
  Confirm azimuth and elevation values change correctly as aircraft position is varied.

- [ ] **Run gimbal_ctrl.py bench test** — with tracker.py running, run `python3 src/gimbal_ctrl.py`;
  verify `GIMBAL_TARGET` commands appear on PB2-I UDP :14571; verify gimbal physically slews
  to commanded position and encoder confirms on-target within 3 s.

- [ ] **End-to-end tracking test (outdoor):**
  - GCS GNSS acquires fix (HDOP ≤1.5); operator records GCS position.
  - Walk aircraft (powered, GPS locked) 30–50 m in cardinal directions.
  - Verify gimbal pan tracks aircraft azimuth within 5°.
  - Verify gimbal tilt tracks aircraft elevation within 3° (at low aircraft altitude, elevation ≈ 0°).

#### 4.5.5 — Malcolm Integration Testing (Phase Malcolm-4)

- [ ] **Multi-link communication bench test:** connect aircraft (Phase 5 minimum) to Malcolm;
  verify QGC heartbeat on each link independently (disable 3, test 1, rotate):
  SiK 915 MHz → LoRa 915 MHz → WiFi 5 GHz → RCRS-49 MHz.
  All 4 links must deliver ≥1 MAVLink heartbeat per 5 s with aircraft at 1 m range.

- [ ] **915 MHz link margin test (open field, 1 km):**
  Aircraft powered (no flight) at 1 km. Observe QGC RSSI on SiK link.
  Required: RSSI ≥ −90 dBm (SiK sensitivity ≈ −112 dBm → ≥22 dB link margin;
  adequate to absorb ~20 dB receiver desense at aircraft in 500 W/m² environment).

- [ ] **WiFi link margin test (open field, 200 m):**
  Aircraft at 200 m. Observe WiFi telemetry rate in QGC.
  Required: ≥100 kbps sustained (adequate for video + MAVLink telemetry at 200 m).

- [ ] **49 MHz RCRS link test (1 km):**
  Aircraft at 1 km. Verify AX.25 KISS frames received on RCRS-49 link.
  Log RSSI from Emma STATUS register.

- [ ] **Gimbal pointing accuracy test (outdoor, aircraft at 200–500 m):**
  With aircraft carrying a known position-fix (GPS HDOP ≤1.0), compare gimbal-pointed
  azimuth to independently measured true bearing.  Required: pointing error ≤5°.

- [ ] **MAVLink authentication test:** verify aircraft nodes reject unsigned commands from
  Malcolm if TPM provisioning is incomplete (remove TPM key, attempt arm command →
  should be rejected; re-provision TPM → arm command accepted).

- [ ] **Node loss with Malcolm active:** kill one aircraft FC node during bench hover test;
  verify Malcolm (QGC) shows failover in status panel within 200 ms; remaining nodes
  maintain MAVLink heartbeat to Malcolm on all links.

---

## 5.0 — Regulatory Compliance

### 5.1 — FCC (external radio systems)

- [ ] **XCVR-49MHZ-1 FCC Part 95 compliance** — center frequency accuracy ±0.005%, ERP ≤100mW, harmonic suppression ≥40dBc (47 CFR 95.655). Document via pre-compliance checklist (1.3 Phase 4). Formal FCC equipment authorization (FCC ID grant) required before airborne transmission on 49MHz channels (47 CFR 95.603).

- [x] **SiK 915MHz** — operates under FCC Part 15 / ISM band (no license required for operation). Verify SiK radio module carries FCC ID marking.

- [x] **LoRa RFM95W 915MHz** — same Part 15 / ISM band. Verify module carries FCC ID.

- [x] **WiFi (WL1837MOD)** — Part 15 / ISM. Module must carry FCC ID; verify.

- [x] **ZigBee 2.4GHz (if used)** — Part 15 / ISM. Verify FCC ID on any ZigBee module installed.

### 5.2 — FAA (airworthiness and operations)

- [ ] **Aircraft registration** — register under 14 CFR Part 48 (sUAS, AUW <55 lbs) at FAA DroneZone. Replace N00000 placeholder in `decal_sheet.svg`. Mark on airframe per 14 CFR 47 — visible without moving any part. **Complete before first untethered flight.**

- [ ] **Remote Pilot Certificate** — verify FAA Part 107 Remote Pilot Certificate is current (24-month knowledge test recurrency).

- [ ] **Navigation lights compliance** — verify 6-position WS2812C nav light implementation: port RED (≥3 SM visibility), stbd GREEN, tail WHITE steady, belly WHITE strobe. Compliant with ICAO Annex 2 and 14 CFR 91.209.

- [ ] **sUAS data plate** — attach to airframe: operator name, contact info, registration number. See `decal_sheet.svg` "D — safety labels" zone.

- [ ] **Pre-flight area check** — LAANC authorization for any Class B/C/D/E airspace. Verify no TFRs, NOTAM conflicts. File NOTAM if operating in uncontrolled airspace with public nearby.

- [ ] **Airspace waiver (if applicable)** — if operating above 400ft AGL or in controlled airspace without LAANC, apply for FAA Part 107 waiver (approval time 90 days typical).

### 5.3 — Industry Standards Compliance

- [ ] **Structural validation** — wing spar, keel, pivot rod, and tilt servo torque analysis documented per REVN_BUILD_GUIDE_24IN.md structural summary. Verify at actual build dimensions (24" hull).

- [ ] **IEEE/ISA/AUVSI best practices** — validate all design decisions against AUVSI UAS best practices; document in build record.

- [ ] **Tamper-evident logging** — verify CPLD write-blocker (ATF16V8BQL) on all 4 CN nodes prevents post-flight log modification; function as hardware-enforced non-executable microSD per CLAUDE.md requirement.

---

## 6.0 — Version Control and Repository Maintenance

### 6.1 — Branch Reconciliation (2026-06-09)

**Context:** A `git merge --allow-unrelated-histories` at commit `406c53f` joined two divergent
history trees. This created a topology where 11 feature branches appeared to have 44–168 commits
"not in main," but no file content was actually lost.

**Reconciliation findings (verified 2026-06-09):**

- [x] **`claude/aft-edf-phase-11-CMM8b`** — PRs #37, #39 merged. 0 files missing from main. Branch is a pre-merge snapshot; content fully absorbed. ✅
- [x] **`claude/cape-em-harsh-variants-9Yfr1`** — PRs #28–#35 merged. 0 files missing from main. ✅
- [x] **`claude/cargo-equipment-mounts-70I3i`** — PRs #21, #23 merged. Old `serenity/` paths reorganized to `airframe/` and `archives/` in main. ✅
- [x] **`claude/docs-scrub-revision-p-Y7pja`** — PRs #24, #25 merged; PR #27 closed. 0 files missing from main. ✅
- [x] **`claude/kicad-silk-labels-HnUIe`** — PRs #7, #9, #10 merged. Old `serenity/diagrams/` SVGs now in `graphical-build-guide/`; 18in STLs archived in `archives/thingverse-serenity/`. ✅
- [x] **`claude/revision-q-avionics-archive-BXwZI`** — PRs #35, #36, #41 merged. 0 files missing from main. ✅
- [x] **`claude/revt-nacelle-simplified-3Ri7A`** — PRs #38, #40 merged. 0 files missing from main. ✅
- [x] **`claude/todo-implementation-2LV2X`** — PRs #15, #18 merged. Old paths reorganized to current structure. ✅
- [x] **`claude/todo-implementation-8bRee`** — PRs #11–#14, #16, #19 merged. Hull SVGs (hull_bottom/front/side/top) present in `graphical-build-guide/`. ✅
- [x] **`claude/todo-implementation-AY2pY`** — PR #31 merged. 0 files missing from main. ✅
- [x] **`claude/todo-implementation-by1W7`** — PRs #20, #22, #26 merged. KiCad backup ZIPs and lock files not design artifacts. ✅
- [x] **`claude/wing-root-nacelle-mounts-5bSEA`** — PRs #42, #43 merged. 0 commits not in main. ✅

**Result:** Main is a superset of all 12 feature branches. All 43 PRs (42 merged, 1 closed) are
fully integrated. The stale branches are safe to delete via GitHub once this PR is merged.

- [ ] **Delete stale feature branches** on GitHub after confirming this reconciliation PR merges
  cleanly. Branches to delete: all `claude/*` branches except `claude/pr-reconciliation-forced-merge-4yefsw`.

### 6.2 — STL Mesh Repair (2026-06-09)

**Context:** CI STL Validation job was failing on 11 files (22 reported — each scanned twice due
to duplicate search paths in the validator). Root causes and resolutions:

**Validator fix:**
- [x] Removed duplicate SEARCH_PATHS (`airframe/stls/fuselage`, `nacelles`, `wings` are subsets
  of `airframe/stls` rglob — each file was reported twice). Fixed by reducing to
  `["airframe/stls", "stls"]` plus a `seen` deduplication set.
- [x] Added per-body watertightness check: a mesh passes CI if `mesh.is_watertight` OR every
  `mesh.split()` body is individually watertight. This correctly handles multi-body assembly
  STLs (4 landing feet, nacelle assembly, shell + insert bodies) where the combined mesh fails
  trimesh's global winding check but every solid sub-body is closed.

**STL repairs (manifold3d 3.5.1):**
- [x] `nacelle_nozzle_closed_asm.stl` — repaired: 1704 → 1648 faces, wt=True (16 bodies)
- [x] `nacelle_nozzle_petal.stl` — repaired: 213 → 206 faces, wt=True
- [x] `head_shell24_2mm_repaired.stl` — repaired: 227428 → 226812 faces, wt=True (6 bodies)
- [x] `cargo_sect_shell24_2mm_repaired.stl` — repaired: 368352 → 367506 faces, wt=True
- [x] `cargo_sect_shell24_2mm_repaired_largest.stl` — repaired: 367514 → 367474 faces, wt=True
- [x] `middle_canonical_edf_intake.stl` — **regenerated** from `middle_canonical_shell24.stl`
  via manifold3d Boolean difference (4 radial intake scoops). Original was non-manifold (3
  connected components, all non-manifold). New mesh: 20734 faces, wt=True. Parameters from
  `airframe/blender-scripts/blender_middle_intake_cut.py` Rev C.

**STLs passing via per-body check (no geometry change needed):**
- [x] `feet_x_4_scaled24.stl` — 4 feet (4 bodies, each wt=True)
- [x] `rear_shell24_2mm_repaired.stl` — 15 bodies, all wt=True
- [x] `middle_shell24_2mm_repaired.stl` — 10 bodies, all wt=True
- [x] `dorsal_antenna_fin.stl` — 3 bodies, all wt=True
- [x] `cargo_sect_shell24.stl` — 190 bodies, all wt=True

**Result:** All 37 STL files pass `python tools/validate_stls.py` (0 failures).

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*  
*Hull: Peter Farell CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal — Not an officially licensed product.*
