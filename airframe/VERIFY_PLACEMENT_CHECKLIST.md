# VERIFY Parts Placement Checklist — Rev R1 (Hull Frame)

**Status:** Phase 1 — Initial Placement by AI + User Verification  
**Last Updated:** 2026-07-18  
**Assembly Output:** `airframe/Serenity-Assembled.FCStd`

This checklist guides the placement of VERIFY-tier (un-validated, part-local or estimated) components in hull-frame coordinates. The assembly loads cleanly with all parts present but unplaced; this task places them systematically section-by-section for user visual inspection and final precision alignment.

---

## Workflow

1. **AI Initial Placement** — for each section below, I position parts at estimated hull-frame coordinates based on SCAD/design intent.
2. **User Verification in FreeCAD** — you review in `Serenity-Assembled.FCStd`; fix gross errors (wrong side, inverted, etc.) and save.
3. **AI Precision Alignment** — I read your corrected placement and refine to 1/100 in (0.254 mm) tolerance via matrix transforms.
4. **Commit** — update `serenity_assembly.py` with validated placements, regenerate FCStd, verify, and commit.

---

## Hull-Frame Coordinate System (Canonical)

- **X**: positive port (left wing side) — lateral axis
- **Y**: positive aft (backward) — longitudinal axis  
- **Z**: positive dorsal (up) — vertical axis
- **Origin**: SerenityAssembly.FCStd world origin (the baked primary hulls center here)

**Primary component extents (mm, hull frame):**

| Component | X min..max | Y min..max | Z min..max |
|-----------|----------|----------|----------|
| Head_Shell | −232.9..−103.5 | −305.7..−70.7 | +61.1..+201.5 |
| Cargo_Shell | −267.0..−72.7 | −71.5..+132.0 | 0.0..+163.2 |
| Middle_Shell | −258.5..−81.6 | +130.4..+203.6 | +1.3..+166.1 |
| Rear_Shell | −246.1..−105.5 | +203.2..+384.3 | +3.3..+161.1 |
| Wing_Port | −93.0..+4.7 | −7.0..+122.0 | +48.0..+77.0 |
| Wing_Stbd | −347.7..−250.0 | −12.0..+117.0 | +48.0..+77.0 |
| Nacelle_Port | +4.0..+86.0 | −58.2..+108.3 | +21.4..+104.7 |
| Nacelle_Stbd | −428.1..−346.1 | −64.2..+102.3 | +23.3..+106.6 |

---

## Sections (in processing order)

---

## §1 — CARGO BAY (Cargo_Shell interior)

**11 components**, all currently imported but **unplaced (origin + identity).**

Cargo bay interior mounts:
- Doors (2) × hinge retention blocks (4)
- Cradle (autolatch frame)
- FPV camera bezel (dorsal nadir facing)
- GPS antenna retention ring
- Winch motor mount + spool
- Motor driver (DRV8833) tray
- Two servo mounting brackets (door actuator + payload-release)

**VERIFY sub-tasks:**

### 1.1 Cargo Door Port
- **Part:** `cargo_door_port.stl`
- **Design intent:** Piano-hinge port-side door, belly (−Z face), swings down and outboard.
- **Current state:** Unplaced (at origin).
- **Placement:** Hull-frame position already baked into the door STL during `generate_cargo_doors.py` (Rev R1b/R1c). Door should align with cargo belly cutout.
- **Verification:** Does port door hinge knuckle align at hull X ≈ −117.6 mm? Free edge (starboard side) at hull X ≈ −169.85 mm (cargo centreline)? Z ≈ 5.1 mm (hinge height)?
- **User action in FreeCAD:** Confirm visual alignment; if door interpenetrates cargo shell, flag for investigation.
- **Status:** [ ] Visually verified
- **Notes:** Door panels span Y ≈ 2..108 mm; aft-outboard corner (Y → 108) previously required manual despike inspection — confirm it doesn't flatten against the hull.

### 1.2 Cargo Door Stbd
- **Part:** `cargo_door_stbd.stl`
- **Design intent:** Mirror of port door (opposite X, same kinematics).
- **Placement:** Hull-frame, same as port (already baked).
- **Hinge X:** ≈ −222.5 mm (stbd outboard). Free edge at X ≈ −169.85 mm.
- **Verification:** Same as 1.1, but stbd side.
- **User action:** Confirm alignment; check aft-outboard corner despike.
- **Status:** [ ] Visually verified

### 1.3 Cargo Hinge Retention Blocks (4 total)
- **Part:** `cargo_hinge_retention.stl` (4 blocks, 2 per door)
- **Design intent:** Shell-side piano-hinge pin-bore blocks. Bonded to belly interior; support door rotation.
- **Current state:** Unplaced.
- **Placement:** Hull-frame (already baked into the STL). Two blocks mount on port side (hinge X ≈ −117.6), two on stbd (hinge X ≈ −222.5). Bores Ø3.3 mm, coaxial with door rod axes.
- **Verification:** Do all 4 blocks align with their respective door hinge lines (port/stbd X, door-panel span Y ≈ 2..108, Z ≈ 5.1)?
- **User action:** Confirm blocks don't float; should bond tightly to interior cargo shell.
- **Status:** [ ] Visually verified

### 1.4 Cargo Cradle (Autolatch)
- **Part:** `cargo_cradle_autolatch.stl`
- **Design intent:** Spring-loaded cargo frame locator; sits on cargo-bay floor to center payload and provide friction/positive stop.
- **Current state:** Unplaced (at origin).
- **Placement estimate:** Cargo bay floor (belly −Z face), centred on cargo area. Nominal belly centroid ≈ X ≈ −170 mm, Y ≈ 30..60 mm (middle of bay), Z ≈ 0..2 mm (resting on shell floor).
- **User action:** Rough placement near cargo floor; will refine after initial inspection.
- **Status:** [ ] Positioned for inspection
- **Notes:** No active SCAD source — VERIFY placement is by visual fit in FreeCAD.

### 1.5 Cargo FPV Bezel
- **Part:** `cargo_fpv_bezel.stl`
- **Design intent:** Nadir-facing FPV camera mount pod + Jayne cape co-location. Hangs from cargo-bay roof (dorsal face), pointing down for ground/target imagery.
- **Current state:** Unplaced.
- **Placement estimate:** Cargo-section dorsal interior ceiling, aft of the GPS antenna. Nominal: X ≈ −170 mm (centred), Y ≈ 40..80 mm, Z ≈ 160..163 mm (touching roof interior).
- **User action:** Confirm orientation (camera lens points −Z / downward); adjust Y if needed to clear other mounts.
- **Status:** [ ] Positioned for inspection
- **Notes:** Jayne board (TI AM62A vision SoC + stepper/laser driver) mounts here; full harness routing is Phase 11 (deferred).

### 1.6 Cargo GPS Retention Ring
- **Part:** `cargo_gps_retention_ring.stl`
- **Design intent:** u-blox M10Q GNSS antenna clip; mounts to dorsal cargo roof; antenna thru-hull or up into the head for roof clearance.
- **Current state:** Unplaced.
- **Placement estimate:** Cargo-section dorsal interior roof, forward of FPV bezel. Nominal: X ≈ −170 mm (centred), Y ≈ 10..30 mm, Z ≈ 160..163 mm.
- **User action:** Confirm it doesn't interfere with FPV bezel or internal structure.
- **Status:** [ ] Positioned for inspection
- **Notes:** Antenna lead routes via PTFE conduit to FC node GPS input. Final antenna feedthru location TBD per CLAUDE.md Phase 5 task.

### 1.7 Cargo Winch Motor Mount
- **Part:** `cargo_winch_motor_mount.stl`
- **Design intent:** N20 6V 300:1 gearmotor base. Bolted to belly interior, provides mechanical advantage for cargo deploy/retract.
- **Current state:** Unplaced.
- **Placement estimate:** Cargo bay floor (belly −Z), port side for balance. Nominal: X ≈ −140 mm (outboard of CL), Y ≈ 40..70 mm, Z ≈ 0..5 mm (floor-mounted).
- **User action:** Confirm motor orientation (shaft pointing Y or Z); check clearance to cradle and door servo.
- **Status:** [ ] Positioned for inspection
- **Notes:** Drum/spool spins to wind/unwind Dyneema line. Phase 7 (cargo ops).

### 1.8 Cargo Winch Spool
- **Part:** `cargo_winch_spool.stl`
- **Design intent:** Drum that attaches to motor shaft; winds Dyneema payload line.
- **Current state:** Unplaced.
- **Placement estimate:** On winch motor shaft (coaxial); Y/Z position follows motor mount (1.7).
- **User action:** Will need to confirm as sub-assembly to motor mount; should be coaxial.
- **Status:** [ ] Positioned for inspection

### 1.9 Cargo DRV8833 Tray
- **Part:** `cargo_drv8833_tray.stl`
- **Design intent:** Motor H-bridge driver PCB support tray. Foam-taped to a non-structural interior wall or spar.
- **Current state:** Unplaced.
- **Placement estimate:** Belly interior, stbd side (opposite winch motor for balance). Nominal: X ≈ −200 mm, Y ≈ 40..70 mm, Z ≈ 10..20 mm (standoff above floor).
- **User action:** Confirm it clears door servo, doesn't block airflow conduits.
- **Status:** [ ] Positioned for inspection

### 1.10 Cargo Door Servo Bracket
- **Part:** `cargo_door_servo_bracket.stl`
- **Design intent:** SG90 servo mount for door-open/close actuator. Spring-assist open; servo pulls closed.
- **Current state:** Unplaced.
- **Placement estimate:** Cargo bay wall (likely port wall interior, high up to clear payload). Nominal: X ≈ −140..−110 mm, Y ≈ 70..100 mm, Z ≈ 100..120 mm.
- **User action:** Confirm servo axis aligns with door-actuator kinematics (needs detail SCAD review).
- **Status:** [ ] Positioned for inspection
- **Notes:** Servo control lead routes via PTFE to CN master GPIO (Phase 7).

### 1.11 Cargo Release Servo Bracket
- **Part:** `cargo_release_servo_bracket.stl`
- **Design intent:** SG90 servo mount for payload-release mechanism. Unlocks cargo latch on command.
- **Current state:** Unplaced.
- **Placement estimate:** Opposite wall from door servo (stbd wall interior). Nominal: X ≈ −200..−220 mm, Y ≈ 70..100 mm, Z ≈ 100..120 mm.
- **User action:** Confirm it clears the autolatch cradle and door swing arc.
- **Status:** [ ] Positioned for inspection
- **Notes:** Servo control lead routes via PTFE to CN master GPIO (Phase 7).

---

## §2 — BATTERY TRAY & BELLY PANEL (Fuselage Interior Accessories)

Located in the middle section's ventral interior (inner-neck/Kaylee's room).

### 2.1 Battery Tray
- **Part:** `battery_tray.stl`
- **Design intent:** 6S LiPo battery support platform; sits on the keel underside. CG must align with forward CG (FCOG ≈ sta 130 mm) for trim.
- **Current state:** VERIFY placement estimated in assembly (lines 405–414).
- **Current estimate:**
  ```
  X: 172.0 (fore edge at station 112 mm)
  Y: −263.0 (keel underside ≈ CY_head − TRAY_H)
  Z: 41.0 (centred: CZ_hull − TRAY_W/2)
  ```
- **CLAUDE.md reference:** Kaylee's room (battery bay) is in the inner neck of the middle section, accessible through the open ventral face (−Z). Central location minimises power run lengths to all 4 nacelles and avionics stacks.
- **Verification needed:** 
  - Does tray fore edge sit at ship station ≈ 112 mm (roughly mid-cargo)?
  - Is tray CG centred on the FCOG (forward CG)?
  - Does battery mass (≈ 600 g / 1.32 lbm) sit safely on the keel?
- **User action:** 
  - Slide tray along the keel (Y axis) until the battery CG aligns with the calculated FCOG. 
  - Measure cross-sections in slicer to confirm before committing.
- **Status:** [ ] CG aligned and verified
- **Notes:** Phase 5 (first flight) — battery is critical for trim and flight envelope.

### 2.2 Belly Panel
- **Part:** `belly_panel.stl`
- **Design intent:** Protective cover over battery tray; prevents accidental contact and retains battery during impact.
- **Current state:** VERIFY placement estimated (lines 416–425).
- **Current estimate:**
  ```
  X: 172.0 (aligns with tray opening)
  Y: −267.0 (flush with belly skin)
  Z: 41.0 (centred under tray)
  ```
- **Verification needed:**
  - Does panel align with tray fore/aft edges?
  - Is panel Z height flush (no gaps) with belly exterior?
  - Does panel clear avionics bay conduit runs?
- **User action:**
  - Confirm panel sits flush over tray opening.
  - Adjust Y if needed to seat against middle-section belly interior.
- **Status:** [ ] Flush alignment verified

---

## §3 — WINGS & PYLONS (Wing Root Attachments)

### 3.1 Nacelle Tilt Pylon — Port
- **Part:** `wing_nacelle_pylon_revo.stl` (one instance, left/port wing)
- **Design intent:** Carbon-fiber reinforced tilt bracket; mounts the nacelle's pivot axis and houses the servo-control sector gear. Bolts to wing root.
- **Current state:** Unplaced (just imported, see assembly lines 447–448).
- **Placement:** Hull-frame (wing root is already at identity placement). Pylon should orient vertically (like a "horn" from the wing root, pointing outboard +X for port). Nominal pylon pivot base should sit approximately at the cargo/middle junction (Y ≈ 0..30 mm), inboard of the wing-root trailing edge.
- **Verification needed:**
  - Does pylon extend outboard from the cargo section, clear of the fuselage?
  - Is the pivot axis (bore centerline) aligned with the nacelle's own pivot housing bore?
  - Does the sector gear mounting face sit at the correct nacelle-pylon interface height (Z)?
- **User action:** 
  - Position pylon relative to Wing_Port root. 
  - Verify it doesn't interpenetrate the wing or fuselage.
  - Confirm sector-gear bore clearance (will align with nacelle internal gear train once placed).
- **Status:** [ ] Positioned for inspection

### 3.2 Nacelle Tilt Pylon — Stbd
- **Part:** `wing_nacelle_pylon_revo.stl` (one instance, right/stbd wing)
- **Design intent:** Mirror of port pylon.
- **Placement:** Stbd wing root (X ≈ −250..−347.7 per Wing_Stbd extents). Pylon should mirror port (pivot base at Y ≈ 0..30 mm).
- **User action:** Same as 3.1, port-side reflection.
- **Status:** [ ] Positioned for inspection

---

## §4 — NACELLE SERVO BRACKETS (Fuselage-Mounted Tilt Actuators)

### 4.1 Nacelle Servo Bracket — Port Mount
- **Part:** `nacelle_servo_bracket.stl` (instance 1 for port nacelle)
- **Design intent:** SG90-class digital servo mount bracket. Bolts to the fuselage (likely on the cargo-section interior wall); pushrod connects servo arm to the port-nacelle tilt pivot.
- **Current state:** Unplaced (see assembly lines 684–689; noted as pending manual FreeCAD placement per TODO.md §1.1.3).
- **Known issue:** The servo-mount pad in `cargo_sect_shell24.scad` has ambiguous Z-axis labelling ("port wall" vs "stbd wall") predating the hull-frame standard. The mount location is in cargo interior walls (around Y ≈ −288 mm per SCAD comments), but Z placement is not validated.
- **Placement estimate:** 
  - Cargo-section interior wall (likely port-facing, Y ≈ −288 mm near the wing root).
  - Servo arm should reach the port pylon's tilt pivot arm (estimated Y ≈ 0..50 mm, Z ≈ 100..140 mm).
  - Servo bracket X ≈ −100..−140 mm (inboard of nacelle tilt path).
- **Verification needed:**
  - Is the servo within pushrod reach of the port pylon?
  - Does servo arm swing freely without hitting the fuselage?
  - Is the servo clear of conduits and other mounts?
- **User action:**
  - Manually position in FreeCAD on the cargo interior wall (likely on the port wall where the wing spar passes).
  - Confirm pushrod routing from servo arm to pylon tilt pivot.
  - Save placement so I can extract it for matrix transform.
- **Status:** [ ] Positioned for inspection
- **Notes:** Servo will be mounted at −5° to 140° tilt range; verify hard stops are clear.

### 4.2 Nacelle Servo Bracket — Stbd Mount
- **Part:** `nacelle_servo_bracket.stl` (instance 2 for stbd nacelle)
- **Design intent:** Mirror of port servo bracket (stbd wall, same Y station concept, opposite X).
- **Placement estimate:** Cargo interior stbd wall, mirror of port.
- **User action:** Same as 4.1, stbd-side mirror.
- **Status:** [ ] Positioned for inspection

---

## §5 — DORSAL ANTENNA FIN (Fuselage-Mounted RF Support)

### 5.1 Dorsal Antenna Fin
- **Part:** `dorsal_antenna_fin.stl`
- **Design intent:** Streamlined fairing/antenna mount post; bolts to the dorsal roof of the cargo section. Supports the SMA bulkhead for the Wi-Fi 5 GHz (upper fuselage) and provides a structural reference for forward wire posts (49 MHz Part 15 §15.235).
- **Current state:** Unplaced (see assembly line 695).
- **Placement estimate:**
  - Cargo-section dorsal roof (Z ≈ 160..163 mm).
  - Forward of the FPV bezel, roughly Y ≈ 30..60 mm (forward-mid cargo).
  - Centred laterally, X ≈ −170 mm.
- **Verification needed:**
  - Does fin point dorsally without fouling the hull roof?
  - Is it positioned to clear the forward 49 MHz wire post (Rev R1, deferred; post will attach to the forward upper fuselage).
  - Does the SMA bulkhead routing route cleanly to the Wi-Fi comms node (Inara's shuttle, Bay B)?
- **User action:**
  - Position fin on cargo roof; confirm it doesn't occlude roof geometry.
  - Note antenna feedthru X/Y for later wire-post alignment (Phase 5).
- **Status:** [ ] Positioned for inspection
- **Notes:** Part-local print frame (not yet baked to hull frame). Final antenna routing and RF safety review are Phase 5.

---

## §6 — LANDING GEAR (Fuselage-Mounted Shock Absorption)

### 6.1 Landing Leg Vertical Posts (Deferred to §1.1.4)
- **Parts:** `feet_x_4_scaled24.stl`, `legs_scaled24.stl`
- **Design intent:** Rev R5 wire-brace landing gear (vertical CF-PETG posts + spring/ductile wire braces). Mounts to the four cargo-section corner boss sockets.
- **Current state:** Imported but **unplaced** — placement is explicitly deferred to TODO.md §1.1.4 (§1.1.5 in the full airframe/WBS.md).
- **Notes:** Hull-frame placement of Rev R5 gear assembly is a separate work item (deferred). The wire brace design and boss locations are documented in `docs/LANDING_GEAR_ANALYSIS.md` Rev R5. Placement verification pending user work on boss socket integration.
- **Status:** [ ] Deferred to §1.1.4

---

## §7 — PRECISION ALIGNMENT NOTES (AI Phase 2)

Once you've reviewed all sections in FreeCAD and made corrections for gross errors, I will:

1. **Extract final placement matrices** from `Serenity-Assembled.FCStd` (via FreeCAD Python API or manual measurement).
2. **Compute 4×4 transform matrices** (position + rotation) for each VERIFY part.
3. **Apply sub-0.01 in (0.254 mm) fine-tuning** to align surfaces, mesh edges, and bearing races.
4. **Update `serenity_assembly.py`** with the validated `transform_mesh()` calls or bake instructions.
5. **Regenerate and verify** the assembly; commit all changes.

**Precision tolerances:**
- **Coaxial bores** (servo brackets to pivot arms, hinge-block bores): ≤ ±0.1 mm
- **Flush surfaces** (belly panel to battery tray, door to hull): ≤ ±0.2 mm
- **Standoff clearance** (servo arms to fuselage, motor to cradle): ≥ 2 mm minimum (no interference)

---

## §8 — Checklist Summary for User Sign-Off

Print or reference this section after all sections are reviewed:

- [ ] §1.1 Cargo Door Port — visually verified, hinge alignment ✓
- [ ] §1.2 Cargo Door Stbd — visually verified, hinge alignment ✓
- [ ] §1.3 Cargo Hinge Retention (4 blocks) — coaxial with doors ✓
- [ ] §1.4 Cargo Cradle (Autolatch) — floor-mounted, friction-fitted ✓
- [ ] §1.5 Cargo FPV Bezel — dorsal roof, points −Z ✓
- [ ] §1.6 Cargo GPS Ring — dorsal roof, aft of FPV ✓
- [ ] §1.7 Cargo Winch Motor Mount — floor-mounted, motor clears surrounding structure ✓
- [ ] §1.8 Cargo Winch Spool — coaxial on motor shaft ✓
- [ ] §1.9 Cargo DRV8833 Tray — stbd interior wall, standoff ✓
- [ ] §1.10 Cargo Door Servo Bracket — wall-mounted, servo arm free swing ✓
- [ ] §1.11 Cargo Release Servo Bracket — opposite wall, clear of cradle ✓
- [ ] §2.1 Battery Tray — CG aligned on FCOG ✓
- [ ] §2.2 Belly Panel — flush over tray, no gaps ✓
- [ ] §3.1 Nacelle Tilt Pylon Port — pylon clear of fuselage, pivot aligned ✓
- [ ] §3.2 Nacelle Tilt Pylon Stbd — mirror of port ✓
- [ ] §4.1 Servo Bracket Port — pushrod reach to pylon, clear swing ✓
- [ ] §4.2 Servo Bracket Stbd — mirror of port ✓
- [ ] §5.1 Dorsal Antenna Fin — roof-mounted, clear of roof geometry ✓
- [ ] §6.1 Landing Gear — deferred to §1.1.4 (separate work) —

---

## Next Steps

1. **I update `serenity_assembly.py`** with initial placements based on SCAD geometry and design intent.
2. **Regenerate assembly:** `freecadcmd airframe/FreeCAD-scripts/serenity_assembly.py`
3. **You review in FreeCAD:** `airframe/Serenity-Assembled.FCStd` — check each section per the checklist.
4. **You fix gross errors** (wrong side, inverted, major misalignment) and **save**.
5. **You report** which items need adjustment (e.g., "Cargo Door Port hinge is at X=−120 instead of −117.6").
6. **I refine** based on your feedback and regenerate for fine-tuning.
7. **Final precision pass** — I extract matrices and do the 0.01 in alignment.
8. **Commit** updated `serenity_assembly.py` + validated `Serenity-Assembled.FCStd`.

---

*"You can't take the sky from me." — Capt. Malcolm Reynolds*
