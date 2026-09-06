# Serenity UAV — Work Breakdown Structure (Master Index)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0  
**Last updated:** 2026-09-06  
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog) | **Build target:** 24-inch hull (REVN_BUILD_GUIDE_24IN.md)

> **This is the full historical record — every task ever defined, done or open,**
> for clear project-progression tracking. It is a compact *index* (one line per
> task, <=70 chars, headings/subheadings/checkboxes only, no prose) — full notes,
> rationale, and code references live in the subordinate `WBS.md` referenced under
> each heading ("→ detail: ..."). Close an item in its detail file first, then
> check the matching one-line item here as a commit prerequisite.
>
> **For a short list of what's actually left to do, see [`TODO.md`](TODO.md)** —
> it carries only the still-open items from this file, one line each, with a
> pointer back here for full context. Every subsystem folder follows the same
> `WBS.md` (full record) / `TODO.md` (open work only) pairing.
>
> **★ = critical path to first flight (Phase 5).**

---

## Quick-Reference: End State vs. Current State

| Domain | End State | Current Status |
|--------|-------------------|----------------|
| Hull   | 609.6 mm CF-PETG / PU foam / CF skeleton | SCAD sources complete; all four fuselage SCAD shells at Rev S baseline, carried forward unchanged into Rev T; STLs pending regeneration where noted |
| Wings | Fixed CF spar (20x16.3mm tube, 35% root chord), S1223-derived section, gear-linked nacelle tilt drive | Rev T1c: spar bonded wing member (not rotating shaft), root joint splits shear(socket)/moment(80x60 flange); 14T/50T reduction drive; SPAR-20-2 station 45.15→28.0mm |
| Nacelles | 2x 50mm tandem EDF, CG pivot ~Z=107.5mm, M=1.0 gear, iris nozzle, hinged ESC bays | Rev T4c: trunnion skewer deleted, pods hollowed (285→196g fwd-biased), 4 flush ESC covers, 4x90° motor pattern, cooling ports (Rev T4d); nacelle T/W ~1.61 at Phase 5-10 AUW — VTOL hover capable |
| Nacelle EDFs | XFly Galaxy X5 50mm 12-blade 6S 3200KV, 1240g each; 2232g/nacelle (90% additive via stator); 4464g total | Baseline EDF selected; unchanged at Rev T |
| Landing gear | Sponson-mounted bays, canonical 1.5in leg (extended 3.0in variant retained) | Rev R6 (independent component-level track, not part of the S/T letter chain): sponson wells CLOSED, leg length derived from nozzle clearance not belly height |
| Rear propulsion | 55mm 6S EDF, reduced-area neck intake, fixed canonical elliptical tail nozzle (2.06x1.76 in / 52.3x44.7 mm) + 4 RCS bleed-air thrusters | DEFERRED — Phase 11. Adds ~1275g forward thrust; not counted in hover T/W; Phase 11 hover T/W ~1.43 |
| Cargo bay | Clamshell doors + SG90 servos (OpenServoCore) + DRV8833 + SPT5425LV/LibreServo v2 winch + Dyneema + auto-latch + GPS ring + FPV bezel | N20 winch train retired Rev S; STS3215 winch servo superseded 2026-08-02 by SPT5425LV+LibreServo v2 (envelope gate resolved, 6 winch STLs still unimplemented — see WBS §1.1.1.2.1); other cargo STLs generated; gondola shell open |
| PCBs | Rev Q: all 8 nodes use EM-hardened Pilot/XO capes. Flight Engineer is the PDB. Two Commo boards give 49 MHz connectivity. Rev S adds Observer (standalone vision/ToF/laser board). | Rev S schematics complete; Flight Engineer PCB DRC clean, gerbers generated; manual placement/routing remain (see avionics detail files) |
| Firmware | 8-node cooperative flight, PID governor, OA, cargo, logging | serenity-cn Phase 6 done; serenity-fc Phase 6 stub only; all Phase 7 items open |
| Physical build | Airborne, autonomous, cargo-capable | Not started — awaiting STL exports, PCB fabrication |
| Regulatory | FAA Part 107 [REF-FAA-002], Part 48 §48.205 [REF-FAA-001], §91.209 [REF-FAA-003], FCC Part 15 [REF-FCC-001, REF-FCC-002, REF-FCC-003 §15.235] | FAA registration placeholder; XCVR-49MHZ-2 pre-compliance pending |

---

## 0.0 — Standards Vetting and Regulatory Compliance

### 0.1 — FCC Part 95 Section Number Verification
→ detail: `docs/WBS.md` §0.1

- [x] Correct REF-FCC-003 in REFERENCES.md
- [x] Rework skipper_antenna_spec.md Link 4 compliance math
- [x] Update CLAUDE.md, TODO.md status lines, and other docs
- [x] Re-architect the 49 MHz link's power/range budget — RCRS rese…
- [x] §15.203 antenna/connector non-compliance, confirmed violation…
- [x] Remaining TODO.md references to "RCRS"/old Part 95 section numb…
- [x] Remaining non-TODO.md references to "RCRS"
- [x] Code-identifier "RCRS" naming renamed to "49MHZ_XCVR"/"XCVR-49MHZ…

### 0.2 — Incorrect Reference Correction
→ detail: `REFERENCES.md` "Removed / Superseded Citations"

- [x] Remove NIST SP 800-72 write-blocker citation

### 0.3 — 14 CFR Part 47 vs Part 48 Clarification
→ detail: `REFERENCES.md` "Open Standards Verification Items"

- [x] Replace 14 CFR Part 47 references with Part 48 §48.205 where ap…

### 0.4 — AUVSI/ASTM Standards Identification
→ detail: `REFERENCES.md` "Open Standards Verification Items"

- [x] Identify specific ASTM F38 Committee standards applicable to ai…

### 0.5 — Citation Completeness Audit (All Source Files)
→ detail: `docs/WBS.md` §0.5

- [x] Audit SVG build guide files for standards citations — priority…
- [x] Audit remaining firmware source files for standards citations —…
- [x] Audit KiCad companion Markdown files — done 2026-06-22.

### 0.6 — IEC 62368-1 PCB Layout Isolation Verification
→ detail: `avionics/emi-hardening/WBS.md` §0.6

- [x] Verify creepage and clearance distances in Pilot PCB layout
- [x] Verify creepage and clearance distances in XO PCB layout
- [x] Document verified creepage/clearance values

### 0.7 — CI Lint Scope and Repo-Wide Lint Debt
→ detail: `docs/WBS.md` §0.7

- [x] Resolved (confirmed 2026-06-29). run-lint (github/super-linter@…
- [x] Repo-wide lint debt — remediation pass complete 2026-07-18

### 0.8 — Tilt-Spar Material Allowables + Hall Encoder Verification
→ detail: `docs/WBS.md` §0.8

- [ ] Verify 4130 / 17-4 PH / 7075 allowables vs MMPDS/AMS (REF-MAT-*)
- [ ] Add 4130 corrosion-finish spec (zinc/cad plate) to BOM/build guide
- [ ] Verify AK7455 off-axis geometry + pinout vs datasheet (REF-SENSOR-*)

### 0.9 — Licensing Updates
→ detail: `docs/WBS.md` §0.9

- [x] Correct misubisu Thingiverse model [REF-CAD-004] license to CC-BY-SA 4.0
- [x] Integrate REF-CAD-002/003/004 as Available Components under CERN-OHL-W 2.0
- [x] License wings, nacelles, landing gear, cargo, other airframe under CERN-OHL-W
- [x] License all avionics under CERN-OHL-W
- [x] License all documentation, code, scripts, drawings under CC-BY-SA
- [x] Create per-subsystem LICENSE files federated from root + attribution doc
- [x] Create OSHW certification supporting documents (readiness checklist)
- [x] Rename avionics boards to non-trademarked names — former Firefly-character names
    → Pilot/XO/Flight Engineer/Commo/Observer/Skipper (user-supplied names, 2026-08-01;
    files+content, KiCad ERC/DRC not verified — no kicad-cli in this environment; full
    former-name mapping in `AGENTS.md` §9 "Naming history")

### 0.10 Update and correct documentation touching every non-archived file.
→ detail: docs/WBS.md §0.10

*(Renumbered 2026-08-01 from a stale "0.9" — this file's own §0.6 was already taken by the
distinct, completed "IEC 62368-1 PCB Layout Isolation Verification" item above, so `TODO.md`'s
matching "§0.6" label for this item was also a collision, not a valid cross-reference; both
files are renumbered here to §0.10, which frees "0.9" cleanly for the new §0.9 "Licensing
Updates" item above. See docs/WBS.md §0.9 for the note.)*

#### 0.10.1 Systems
→ detail: docs/WBS.md §0.10.1

*(Audited 2026-08-22 — substantial fixes applied to all four; none fully closed, each has a
short honestly-scoped residual list. See docs/WBS.md §0.10.1 for exactly what was verified,
what was fixed, and what remains open per item.)*

- [ ] Verify and update airframe specifications vs as built for each component.
- [ ] Verify avionics specifications vs as- built.
- [ ] Verify and update all assessment and engineering documents.
- [ ] Verify and update all software, firmware, and scripts, along with their documentation.
- [ ] Decide: fold landing gear's standalone "Rev R6" label into the Rev T letter chain,
    or amend AGENTS.md §8 for a documented per-component exception

#### 0.10.2 Documentation

→ detail: docs/WBS.md §0.10.2

*(Audited 2026-08-22 — items 1, 2, and 5 closed below; items 3 and 4 have real residual work,
see docs/WBS.md §0.10.2.)*

- [x] Verify and update all compliance and licensing documents. *(closed 2026-08-22 — found
    and fixed a stale duplicate policy doc with materially wrong license terms; see
    docs/WBS.md §0.10.2 item 1.)*
- [x] Verify and update all README files and the starting with subsystem ones and correcting
    the root README to match. *(closed 2026-08-22 — see docs/WBS.md §0.10.2 item 2.)*
- [ ] Verify and update the system specification files and BOM.
- [ ] Verify and update the WBS and TODO files.
- [x] Verify and update the REFERENCES.md file. *(closed 2026-08-22 — fixed a duplicate
    REF-ID bug, added 3 missing catalog entries, updated the timestamp; see docs/WBS.md
    §0.10.2 item 5.)*
- [ ] Verify and update the REFERENCES.md file.

---

## 1.0 — Design Artifacts (Pre-Fabrication)

### 1.1 — 3D Models: SCAD → STL Exports (Rev T baseline; hull carries forward from Rev S,
wings/nacelles at Rev T1c/T4c — see `docs/WBS.md` §6.4)

#### 1.1.0 — Hull-Frame Coordinate Standardisation (R1)
→ detail: `airframe/WBS.md` §1.1.0

- [x] tools/bake_hull_frame.py created
- [x] 9 STLs baked to hull frame
- [x] serenity_assembly.py Rev R1
- [x] 48 generator/analysis scripts stamped
- [x] Docs updated
- [x] Resolve nacelle port/stbd label swap.
- [x] Re-verify head↔cargo joint bosses in hull Y.
- [x] Regenerate cargo doors from the baked shell.
- [x] Correct hinge location: outboard flank, not centerline.
- [x] Consolidate duplicate cargo shell copies.
- [ ] Hull-frame placements for VERIFY parts
- [x] Generate battery_tray.stl and belly_panel.stl
- [x] Archive deprecated FreeCAD prototypes

#### 1.1.1 — Fuselage
→ detail: `airframe/fuselage-joints/WBS.md` §1.1.1 (1/3)

- [x] Built tools/verify_bow_pod.py
- [x] Located the canonical bow mounting flat
- [x] Placed + skin-verified all three apertures on the flat (3/3 PAS…
- [x] Confirmed fit:
- [ ] User FreeCAD fine-tune (fractional mm):
- [x] Merge bow_pod_cuts() into the canonical Blender head shell — DO…
- [x] Re-run mesh validation after head shell regen — DONE 2026-07-03
- [x] Designed bow_sensor_faceplate.scad
- [x] Superseded bow_camera_bezel.scad + bow_tof_laser_bezel.scad
- [ ] PMMA window spec finalised
- [ ] Procure PMMA discs
- [x] Laser down-angle review
- [x] Superseded 2026-07-03 — see §1.2c "Observer" below.
- [x] Wire TFmini-S UART to bow sensor MCU.
- [x] Wire bow camera video output to bow sensor MCU
- [x] Wire laser GPIO enable bow sensor MCU
- [x] Add laser enable command to MAVLink C2 interface
- [ ] Add standards REF-IDs to bow_sensor_pod.scad firmware integrati…
- [x] BOM updated
- [x] head_shell24_2mm_repaired.stl — 790 036 tri; X −232.9..−103.5 /…
- [x] cargo_sect_shell24_2mm_repaired.stl — 1 414 068 tri; X −267.0..…
- [x] middle_shell24_2mm_repaired.stl — 855 328 tri; X −258.5..−81.6…
- [x] rear_shell24_2mm_repaired.stl — 1 095 972 tri; X −246.1..−105.5…
- [x] Cargo section interior boss features
- [ ] Middle section inner neck — Phase 5-10 print guidance
- [ ] Deprecate SCAD fuselage shell files
- [x] Update REVN_BUILD_GUIDE_24IN.md fuselage shell source references
- [x] Head/Cargo joint boss design (hull Y ≈ −71 mm)
- [x] Cargo/Middle joint boss design (hull Y ≈ +131 mm)
- [x] Middle/Rear joint boss design (hull Y ≈ +203 mm)
- [x] JOINT-01 — cargo mating-face rims ragged + dorsal bite — RESOLV…

#### 1.1.1 — Fuselage (continued)
→ detail: `airframe/fuselage-covers/WBS.md` §1.1.1 (2/3)

- [x] MESH-01 add_structural_features.py boolean cuts left non-wate…
- [x] CF ring plate (CF-PLATE-2MM) — complete first-principles re-eva…
- [x] Hull keel (CF-BAR-6X3) — complete first-principles re-evaluatio…

#### 1.1.1 — Fuselage (continued)
→ detail: `airframe/fuselage-mid/WBS.md` §1.1.1 (3/3)

- [x] Access panel frames + covers (24" Rev R)
- [x] 49 MHz (Part 15 §15.235) wire posts
- [x] Verify head-cargo mating boss positions in slicer — SUPERSEDED,…
- [x] ★ CARGO-01 payload won't fit past the wing spar (BLOCKER)
- [x] CARGO-02 shell bores Ø12.3 for a spar the wing retired (8.3)
- [x] ★ CARGO-03 wing root mortise now penetrates — CLOSED
- [x] ★ CARGO-03b tenon/mortise on one datum — CLOSED
- [ ] ★ CARGO-03c coupon gates tenon vs second spar (15 MPa)
- [x] CARGO-04 conduits clear through the re-cut shell — CLOSED
- [ ] head_shell24.stl
- [ ] cargo_sect_shell24.stl
- [x] Mounting hardware — 8 STLs
- [ ] Cargo gondola shell
- [ ] Clamshell door halves
- [x] cargo_sect_shell24.scad Rev S
- [x] cargo_sect_shell24.scad Rev S1
- [x] cargo_sect_shell24.scad Rev S2
- [x] cargo_sect_shell24.scad Rev S3
- [x] nacelle_servo_bracket.scad
- [x] REVN_BUILD_GUIDE_24IN.md Phase 3 anti-rework
- [ ] cargo_sect_shell24.scad — shuttle exterior fairing profiles on…
- [ ] Avionics dorsal access covers / Faraday tray lids for Inara and…
- [ ] Update REVN_BUILD_GUIDE_24IN.md bay layout table
- [ ] Regenerate cargo_sect_shell24.stl
- [ ] Add DRV8833-tray boss locations to cargo_sect_shell24.scad
- [ ] Add SG90 bell-crank boss to inner face of each door panel for p…
- [x] Cargo winch Rev B spec — STS3215, both-ends spool, ratchet
- [x] N20 winch train scrubbed from active files (Rev A withdrawn)
- [x] New winch hardware specified — 6 STLs + 7 BOM ref
- [x] ★ STS3215 datasheet gate — envelope/torque/mass/stall [SUPERCEDED]
- [x] Cargo winch Rev C spec — SPT5425LV+LibreServo v2 replaces STS3215, pin removed
- [x] Nacelle tilt servo bracket updated for SPT5425LV envelope (DS3218MG→SPT5425LV)
- [x] SG90 cargo servos specified to use OpenServoCore control board
- [ ] ★ Bench-verify SPT5425LV stall current + pin-removal procedure (unblocks §5.4/§6)
- [ ] RS-485 gateway integration for LibreServo v2 bus (J_FLEX has no local transceiver)
- [x] Winch coupler trade closed: slip clutch in the spool hub
- [ ] ★ Winch containment: 5 positive fixes (spool = projectile)
- [ ] Verify Part 107 dropped-object section number
- [ ] Containment checks on assembly + pre-flight cards
- [ ] ★ Shed threshold vs maneuver envelope (2.0g = 0.98x)
- [ ] Calibrate T_slip 0.060 N·m at the spool hub collar
- [ ] Set servo torque ceiling below T_slip (wear protection)
- [ ] Servo mode: continuous rotation by construction (pin removed); confirm LibreServo v2 protocol commands
- [ ] Mark winch spool a consumable (wear item + spare)
- [ ] AK7455 spool encoder on gateway J_ENC (spec §3.7.3)
- [ ] Implement the six Rev S winch STLs
- [ ] Winch pedestal M3 boss stations in cargo_sect_shell24.scad
- [ ] RS-485 differential bus wiring for LibreServo v2 (was: half-duplex TTL on FLEX_TTL_GPIO)
- [ ] Catch solenoid drive (AO3400 + pull-down + SS34)
- [ ] Bench-calibrate ratchet slip to 8.0 N ± 1.0 N
- [ ] Line-shed test (inboard end must NOT be anchored)
- [ ] Winch state machine firmware (Simon + gateway)
- [ ] Re-run winch mass/CG once SPT5425LV+LibreServo v2 mass is bench-weighed
- [x] Blender canonical source baked
- [ ] Slicer verification
- [ ] Flight Engineer's room — PDB mounting in inner neck
- [ ] CF skid rod channels
- [ ] Simon bay — define avionics bay in the MIDDLE section (moved he…
- [ ] Flight Engineer room — PDB + battery bay, middle VENTRAL (2026-06-13).
- [ ] Avionics-bay interior name marks (DEFERRED, 2026-06-13).
- [ ] Phase 11 — aft EDF intake scoop cuts
- [ ] neck_intake_frame.stl (Phase 11)
- [ ] aft_edf_plenum.stl
- [x] middle_canonical_shell24.stl
- [ ] Mount ant-collision strobe on belly of middle section in accord…
- [ ] Mount ant-collision steady white tail light on upper pod of rea…

#### 1.1.2 — Wings
→ detail: `airframe/wings-nacelles/WBS.md` §1.1.2

- [x] wing_nacelle_pylon_revo.stl
- [x] wings_s1223_revo.stl
- [x] Spar bore de-skewed
- [x] Tip thickened for spar fit
- [x] EDF cableway added
- [x] Fuselage spar-interface mismatched — station RESOLVED (Rev S1b)
  (spar DIAMETER Ø12.3 vs 8.3 still open — see §1.1.1 CARGO-02)
- [x] ★ WING-01 S1223 section self-intersects at x/c 0.742 (BLOCKER)
- [x] SPAR-01 spars stop at the wall; CF thwarts fore/aft of bay
- [x] SPAR-02 DS3225 torque re-derived (aero+inertia only, gravity nulled by CG pivot) -- DS3225 clears at ~7.3% margin, no part change; 6 V tilt-servo rail resized to 2.3A/servo (RAIL-2 is unrelated -- winch/Observer rail, corrected citation)
- [x] SPAR-04 Hall tip jog crosses the spar bore — CLOSED

#### 1.1.3 — Nacelles
→ detail: `airframe/wings-nacelles/WBS.md` §1.1.3

- [x] Rev R1 nacelle stator shells
- [x] nacelle_nozzle_iris.stl
- [x] nacelle_nozzle_idler.stl
- [x] Rebuild petals using the BamJr variable nozzle [REF-CAD-001]…
- [x] nacelle_sector_gear.stl
- [x] nacelle_pinion.stl
- [x] nacelle_bevel_pair.stl
- [x] nacelle_bevel_housing.stl
- [x] Map all nacelle-internal mechanism components to hull frame f…
- [x] Fix crown_pinion_boss() in nacelle_pod_50mm_tandem.scad
- [x] Resolve the unresolved Crown-Pinion-to-rack mesh radius in
- [x] Render updated/new gear-train STLs
- [x] Mesh-verify the regenerated nacelle gear-train STLs
- [x] Idler angular position about the nozzle axis
- [x] idler axial mesh-band mismatch — RESOLVED 2026-07-04
- [x] Confirm Sector Gear standoff distance from the nacelle face
- [x] nacelle_tip_cap_port/stbd.stl — ARCHIVED 2026-06-22
- [x] cargo_sect_shell24.scad's port/stbd mirroring used the wrong…
- [ ] [OPEN — DESIGN] Nozzle drive protrudes ~10 mm past the nacelle…
- [x] Trim the intake bell to the canonical leading nacelle dome
- [x] Move the port (red) / stbd (green) nav lights INWARD→OUTWARD fa…
- [x] Route nav-light wires through an internal cableway (not protrud…
- [x] Remove the exhaust WS2812B LED rings + harnesses from the desig…
- [ ] Reconcile crazy-ivan/PR#141 as SUPERSEDED by fix/nozzle branch
- [ ] Merge cargo_spar_drive into cargo shell (bearing/servo/mortise…
- [ ] Verify stbd cargo-chunk placement of spar-drive features
- [ ] Tune servo→spar horn/pushrod linkage throw (−5°..140°)
- [ ] Repair pre-existing stator sleeve non-manifold (edf_stator_sleeve)
- [ ] VERIFY INBOARD_FACE_X sign in _export_pivot_slab.scad
- [ ] Migrate nacelle_hall_ring_hub → nacelle_pod_50mm_tandem.scad + re-bake
- [ ] Bench-cal AK7455 with steel spar/MF128 bearing (ferrous-field check)
- [ ] VERIFY Rev T CG (first-pass, band ≈109–112 mm)
- [ ] Re-solve single-straight-spar alignment for +7 mm pivot move
- [ ] Nozzle drive: replace invalid spar-crank w/ wing-referenced sync…
- [x] Fix iris asm flap sign (nacelle_nozzle_iris.scad) — 8-flap loop…
- [ ] Stator spar crossing (Rev T2): 11 vanes, coprime w/ 12-blade rotor
- [ ] Ø72 nozzle-pocket eats the aft cowl tail…
- [x] Re-derive rotating-assembly CG for Rev T pushrod/cam drive…

#### 1.1.4 — Landing Gear
→ detail: `airframe/landing-gear/WBS.md` §1.1.4

- [x] Build and render the Rev R5 post + wire SCAD/STL *(done —
- [x] Build assembled / exploded / deformed demonstration compound ST…
- [x] LG-12 Model the post per the §4.6 dimensions *(superseded and
      delivered as Rev R6, 2026-07-21)*
- [x] LG-10 Finalize the 4 bay placements *(closed 2026-08-17; all eight
      sub-items LG-10.1…10.8 done)*
- [x] Ground clearance check carried forward from Rev R1 *(closed
      2026-07-21; requirement corrected 2026-07-23)*
- [ ] LG-15 Procure both wire grades/tempers; coupon test
- [ ] LG-16 Confirm ductile wire temper survives jig-forming
- [ ] LG-13 Define wire-end retention detail at bay bosses
- [ ] LG-02 Bay mounting integration: backing plates, flank conform…
- [x] Feet separated into individual STLs (foot_1 through foot_4 in l…
- [ ] Add top-face socket to canonical foot
- [ ] Assess foot grip on concrete/asphalt
- [x] Rev R1.4 corner V-brace (landing_leg_assy.scad) is retired
- [x] Rev R4 closed-ring wire fuse (wire_loop_fuse.scad) is retired
- [x] LG-03 CF rod channel in rear skid arms (superseded by LG-26)
- [x] landing_legs_hull_r1.stl is orphaned
- [ ] LG-06 Elastic bench check: quarter-AUW fixture, 1.5 ft drop
- [ ] LG-07 Confirm avionics enclosure shock rating
- [ ] LG-11 Coupon-test CF-PETG
- [ ] LG-14 Instrumented drop test (load cell + high-speed video) at…
- [ ] Reconcile the remaining-parts list
- [ ] Combine all airframe STLs
- [ ] Exploded view SVG — printed parts only
- [ ] Exploded view SVG — full build
- [x] LG-17 Drop-height decision: 6 ft vs 4 ft ductile wire schedule
      *(closed 2026-08-09 — 4 ft adopted)*
- [ ] LG-18 Mass-reduction pass (leg frame / bay / thigh)
- [ ] LG-19 Styling refinement pass vs REF-CAD-002 (cosmetic)
- [x] LG-25 Fore bay frame vs U5 tie-rod boss: 12mm proud (relieved boss)
- [x] LG-26 Rear skid CF-rod bore misses the skid tube (fixed)
- [ ] Render overview SVGs using FreeCAD TechDraw

#### 1.1.5 — Non-Printable Component Placeholders
→ detail: `airframe/WBS.md` §1.1.5

- [x] Generate all 65 component placeholder STLs
- [x] FreeCAD catalog assembly script
- [x] Faraday shielding hardware
- [x] Faraday cage foam voids
- [x] Foam-fill and void visualization STLs
- [ ] Rear skid reinforcement — SCAD update (TWO files)
- [ ] Run FreeCAD catalog
- [ ] Hull-frame placement pass
- [ ] Add Phase-11 (deferred) items to catalog
- [ ] Mesh watertightness audit
- [ ] FAR-FT-PANEL PCB design
- [x] Faraday mass budget review
- [ ] Link placeholders to BOM entries

### 1.2 — PCB Design: Cape-A-1 and Cape-B-1 (archived)
→ detail: `avionics/WBS.md` §1.2

- [x] Regenerate Cape-A-1 gerbers
- [x] Regenerate Cape-B-1 gerbers

### 1.2b — PCB Redesigns: Commo Rev S1 / XO Rev S1 / Flight Engineer Rev S1
→ detail: `avionics/rev-s1/WBS.md` §1.2b

- [ ] Commo Rev S1 — add LoRa, replace JST with P1+P2 socket rails
- [ ] XO (Cape-B-2) Rev S1 — remove LoRa, add P1+P2 passthrough rails
- [ ] Flight Engineer Rev S1 — remove 6 V BEC, add 5 V servo output

### 1.2c — PCB Design: Observer (Nose/Cargo-Bay Vision, ToF & Laser)
→ detail: `avionics/observer/WBS.md` §1.2c

- [x] Create avionics/kicad/Observer/kicads/Observer.kicad_sch
- [x] SoM re-scope — Observer = PHYTEC phyCORE PCM-071 SoM on a trapez…
- [ ] FLEET-WIDE ISOW1044BDFMR footprint audit (flight-hardware error…
- [x] Confirm PCB fab/assembly house can handle the AM62Ax 484-ball F…
- [x] Source and cite a real Class 3B nose crosshair laser module
- [x] Design Class 3B interlock circuit for the nose laser
- [x] Reuse the existing 5 mW 650 nm Class 3R crosshair module and dr…
- [x] Shielded JST-GH connector selection
- [x] PGND/GND isolation barrier
- [x] EMI hardening gap — RESOLVED 2026-07-03.
- [x] Create avionics/kicad/Observer/kicads/Observer.kicad_pcb
- [x] Run ERC on the schematic — DONE, 0 shorts/net-conflicts, 116 ac…
- [x] Run DRC on the PCB layout (kicad-cli pcb drc --schematic-parity…
- [x] SoM-end-state rebuild re-verification — DONE 2026-07-13.
- [ ] Final component placement (user-reserved) + impedance-controlle…
- [ ] Generate production-ready Gerber files to avionics/kicad/Observer/…
- [x] Update PROJECT_INDEX.md — done in the same session (see PROJECT…
- [x] Observer mounting bosses added to head_shell24.scad
- [x] Flag: same legacy Y-as-dorsal axis bug found in head_shell24.sc…
- [ ] Flag stale laser bore dimensions:
- [x] Observer mounting bosses added to cargo_sect_shell24.scad
- [ ] Add cargo_tof_cut() and cargo_laser_cut() cutter modules
- [ ] Local sensor harness (both sites):
- [ ] External ring harness — nose:
- [ ] External ring harness — cargo:
- [ ] Flight Engineer second 5 V rail — cross-tied, mutually fault-tolerant…
- [ ] Observer 5 V harness:
- [ ] Laser — unify to a single 520 nm green source, Class 2 both sit…
- [ ] Both Class 2 caps must be hardware-enforced
- [ ] Nose camera strobe + frame-difference detection
- [x] *(No longer required — the Rev-A "nose Class 3B mechanical beam…
- [ ] Do not source

### 1.2a — PCB Design: Pilot, XO, and Commo (EMI-Hardened Variants)
→ detail: `avionics/WBS.md` §1.2a

- [x] USB-to-Ethernet bridge (LAN9500A class) evaluated as an alter…
- [x] Wire second Ethernet (ETH2) on Pilot.
- [x] Separate the two Pilot PHYs onto independent MDIO buses
- [x] Wire the field-connector pins to their signals on Pilot
- [x] Source the 6 GPIO_EXP_A…F signals via an I2C GPIO expander.
- [x] Add an ESC-PWM output connector for DSHOT0–3.
- [ ] Reconcile Pilot.md §14 field-connector table with the actual P…
- [ ] Wire the MIL-1553 connector + transformer.
- [ ] Redesign the tamper mesh as a per-domain anti-tamper mesh (all…
- [ ] Carry the tamper signal over the link for the TPM-less boards.
- [ ] Route the rearranged capes.
- [ ] Clear residual DRC after mesh + routing
- [ ] Finish Pilot PCB (CAPE-A-2) close-out pass:
- [ ] Add SBUS/UART DIP switch to Pilot
- [ ] Generate Pilot gerbers
- [ ] Generate XO gerbers
- [x] remove Wi-Fi, sik, and loRa antennas from XO. Use filtered cho…
- [x] Re-evaluate space / restore Ethernet to XO
- [ ] Zigbee RF chain was never actually added to XO — PCB scope g…
- [ ] Generate Commo gerbers
- [ ] FCC Part 15 §15.235 pre-compliance checklist for Commo
- [ ] EMI isolation validation checklist
- [ ] Merge claude/cape-em-harsh-variants-9Yfr1 → master
- [ ] Design Faraday cages / boxes to protect all PCBs
- [ ] Specify / implement tightly twisted pair bonded shielded wiring…

### 1.3 — PCB Design: XCVR-49MHZ-1 (SUPERSEDED)
→ detail: `avionics/rev-s1/WBS.md` §1.3

- [x] Resolve DDS choice
- [x] Evaluate PA options
- [x] Confirm TCM3105 availability
- [x] 50 Ω trace impedance check
- [x] Update PROJECT_INDEX.md

### 1.4 — EMI Hardening Beyond the PCBs (500 W/m^2 environment)
→ detail: `avionics/emi-hardening/WBS.md` §1.4

- [ ] PB2-I + Pilot Enclosure
- [ ] PB2-I + XO Enclosure
- [x] Resolve total antenna count per stack against the PACE radio ta…
- [x] Antenna mounts
- [x] Feedlines
- [x] Chokes
- [x] Second 49 MHz antenna for Simon's Medbay
- [x] Ensure all transceivers have antenna placement and wiring fro…
- [ ] CAN FD
- [ ] RS-485
- [ ] MIL-STD-1553B
- [ ] Ethernet
- [ ] UART
- [ ] I2C
- [ ] BDSHOT/DSHOT (ESC telemetry)
- [ ] PWM
- [ ] Add FlightEngineer/battery boss pattern to middle_canonical_shell24.sca…
- [ ] Add ventral battery-swap hatch cut to middle_canonical_shell24.…
- [ ] Create flight_engineer_battery_tray.scad.
- [ ] Create flight_engineer_pdb_tray.scad.
- [x] Flight Engineer PCB KiCad files generated (Rev A, 2026-06-10):
- [x] Flight Engineer PCB — DRC run and gerbers generated (Rev A, 2026-06-10):
- [ ] Update REVN_BUILD_GUIDE_24IN.md Phase 1

### 1.5 — Documentation
→ detail: `docs/WBS.md` §1.5

- [x] 1.5.1 serenity-rev-p.jsx
- [x] 1.5.2 Pilot: rename + dual Ethernet PHY
- [x] 1.5.3 XO: rename + Ethernet PHY
- [x] 1.5.4 Pilot: add missing field connectors
- [x] 1.5.5 XO: add missing field connectors
- [ ] Update PHASED_BUILD_GUIDE.md
- [ ] 1.5.6 Rebuild Graphical Buiild Guide
- [ ] Sync bom_revO.json ↔ bom_revO.csv
- [x] Create bom_revQ.json + bom_revQ.csv
- [x] 1.5.7 Consolidate CLAUDE.md/AGENTS.md into one AGENTS.md

### 1.6 — Rev Q: Repo-Wide Architecture Propagation
→ detail: `docs/WBS.md` §1.6

- [x] 1.6.1 Rev Q documentation propagation

### 1.7 — Rev R: Component Revision Synchronisation + s_ Prefix Removal
→ detail: `docs/WBS.md` §1.7

- [x] 1.7.1 Rev R propagation to all active files
- [x] 1.7.2 Component revision synchronisation
- [x] 1.7.3 Remove s_ prefix from all SCAD and STL filenames

### 1.8 — Names
→ detail: `avionics/WBS.md` §1.8

- [x] The ground control station is named "Skipper" aka "CAPT Reynold…
- [x] The Flight Control Avionics Cape is named "Pilot" - "I'm a leaf…
- [x] The Comms/Logging/Payload Cape is named "XO" - "Big Damn Heros…
- [x] The Power Distribution Board is named "Flight Engineer" - "Everything is…
- [x] The Cargo handling system is named "Observer" - "I was aiming for…
- [x] The forward avionics bay is named "Shepherd's room" (Bay A) - "…
- [x] The second avionics bay is named "Inara's shuttle" (Bay B) - "M…
- [x] The third avionics bay is named "River's room" (Bay D) - "Also,…
- [x] The aft avionics bay is named "Simon's medbay" (Bay D) - "What…

### 1.9 — Avionics Workload Balancing
→ detail: `avionics/WBS.md` §1.9

---

## 2.0 — Procurement (Before Physical Build)

BOM tables (not checkbox tasks) — referenced, not duplicated here:
- §2.1 Filament and CF Stock → `airframe/TODO.md`
- §2.2 Structural Hardware → `airframe/TODO.md`
- §2.3 Propulsion System → `airframe/TODO.md`
- §2.4 Avionics (Phase 6, 4-node minimum viable) → `avionics/TODO.md`
- §2.5 Avionics (Phase 7, remaining 4 nodes + ToF arrays) → `avionics/TODO.md`
- §2.6 Cargo System → `airframe/TODO.md`

---

## 3.0 — Physical Build

### Phase0 — Print All Parts + CF Cuts
→ detail: `graphical-build-guide/WBS.md` §Phase0

- [x] Flight Envelope Document
- [x] Failsafe Threshold Document
- [x] Electrical Fault Margin Validation
- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)
- [ ] Calibrate E-steps and Pressure Advance for each filament
- [ ] Dry all filament 6 h at 65°C before printing
- [ ] Nacelle bore caliper: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm
- [ ] Stator fins visible in Z=53–95 mm gap (between the two EDF seat…
- [ ] Hub bore clear at stator: 16 mm ID minimum (motor leads)
- [ ] Sector gear ↔ pinion dry-mesh: 0.1–0.2 mm backlash
- [ ] Unison ring gear seats flush in the throat housing; the 8 flaps…
- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bear…
- [ ] All access panel lids flush ±0.2 mm in frames
- [ ] Keel dry-fits through all hull sections without force
- [ ] Rear neck shell scoop windows covered with removable 3mm PETG b…

### Phase1 — Hull Structure + All Future Provisions
→ detail: `graphical-build-guide/WBS.md` §Phase1

- [ ] Epoxy keel through all hull sections; cure 2h. Datum marks at 9…
- [ ] Bond ring frames at all 5 station notches; cure 1h.
- [ ] Bond access panel frames A–F into hull sections (5-min epoxy, 3…
- [ ] Install M2.5 nylon standoffs in bays A, B, C, D (floor 6mm + in…
- [ ] Bond wing spar pocket inserts at wing root stations, both sides.
- [ ] Bond tilt servo mount brackets at wing root bay interior (one p…
- [ ] Install M3 heat-set inserts ×4 at belly cargo hard-point locati…
- [ ] Install SMA bulkheads: belly port (SiK 915MHz, X≈260mm), belly…
- [ ] Install 49 MHz (Part 15 §15.235) forward wire post (dorsal, X≈1…
- [ ] temporary
- [ ] String 49MHz top wire (0.3mm SS wire or 22AWG enamelled Cu) fro…
- [ ] Install 12× VL53L5CX flush-mount PETG frames (6.5mm hull cutout…
- [ ] Feed 8× PTFE conduits nose-to-tail; thread pull strings through…
- [ ] Install EPS void formers (waxed 2×) in bays A–E; verify pull st…
- [ ] Full dry-fit: all 8 pull strings accessible, standoffs clear, v…
- [ ] Do NOT foam nacelle bays, pivot housing, or access panel bays.
- [ ] Remove EPS void formers; IPA wipe bay walls; verify foam not in…
- [ ] Bond cockpit cap (verify cockpit bay wires and GPS coax accessi…
- [ ] Hull rigid — no flex when held at nose and tail
- [ ] All 8 pull strings accessible at both ends
- [ ] All standoffs in place; screws start freely
- [ ] Foam not in nacelle mounting bay, pivot housing, or panel bays
- [ ] All 6 access panel lids flush ±0.2 mm; latches/magnets engage

### Phase2 — Nacelle Assembly
→ detail: `graphical-build-guide/WBS.md` §Phase2

- [ ] Test EDF rotation direction on bench before installation: port…
- [ ] Install EDF2 (aft/downstream) from nozzle end; seat at Z=5mm sh…
- [ ] Install EDF1 (fore/upstream) from intake end; seat at Z=76mm; v…
- [ ] ESC pair: route to fuselage bay via spar conduit (ESC heat must…
- [ ] Cure 2h before proceeding.
- [ ] Repeat for stbd nacelle (opposite rotation direction).
- [ ] Press nacelle_nozzle_ring.stl onto nozzle exit face; confirm fl…
- [ ] Install nozzle inner ring (rack, R=28mm) inside base ring.
- [ ] Press a 2mm×4mm follower pin (PIN-2X4) into each of the 8 flaps…
- [ ] Hinge the 8 flaps to the throat housing on 3mm×18mm tangential…
- [ ] Dry-test: manually rotate the unison ring — flaps sweep smoothl…
- [ ] Mount sector gear to tilt bracket (FIXED — does not rotate with…
- [ ] Mount drive pinion on nacelle outer shell at pivot axis; mesh w…
- [ ] Install bevel gear pair in nacelle body (nacelle-axis → longitu…
- [ ] Thread 2mm steel longitudinal shaft through nacelle wall channe…
- [ ] Mount crown pinion on shaft at nozzle end; mesh with Idler-In o…
- [ ] Mount idler gear on its bracket to the nozzle outer housing; me…
- [ ] Full sweep test (Rev R1, 2026-06-22):
- [ ] Confirm petal closed position matches nacelle hull profile at 0…
- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake
- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle
- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep
- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°

### Phase3 — Tilt Mechanism
→ detail: `graphical-build-guide/WBS.md` §Phase3

- [ ] Press MF104ZZ bearings into pivot housing bores (both ends); fl…
- [ ] Insert 4mm CF pivot rod through wing spar pocket + pivot housin…
- [ ] Slide nacelle pivot housing onto pivot rod; verify <0.5mm axial…
- [ ] Install tilt servos in fuselage servo mount bracket at wing roo…
- [ ] Connect pushrods (servo arm → pivot arm): servo 0° = nacelle 0°…
- [ ] Install CF-PETG hard stop blocks; bond at −5° stop and 140° sto…
- [ ] Servo calibration: set FC software travel limits at −5° and 140…
- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble
- [ ] Hard stops engage at −5° and 140° (servo stalls, does not strip)
- [ ] Nozzle opens/closes correctly via gear linkage through sweep (f…
- [ ] Sector gear does NOT rotate with nacelle
- [ ] Both nacelles synchronise to within 2° at 0° and 90°

### Phase4 — Hull Foam Pour + Close-up
→ detail: `graphical-build-guide/WBS.md` §Phase4

- [ ] All PTFE conduits routed — pull strings accessible at both ends
- [ ] All bay standoffs installed
- [ ] Cargo hard points installed
- [ ] SMA bulkheads installed and dusted
- [ ] EPS void formers waxed (2 coats) and seated
- [ ] Nacelle bays and pivot housings masked OFF
- [ ] Servo mount brackets clear of foam path
- [ ] Mix X-30 per manufacturer (2:1 ratio by volume, 2-min pot life,…
- [ ] After full cure: remove EPS void formers; IPA wipe bay walls; v…
- [ ] Pull all 8 pull strings — verify still move freely.
- [ ] Install all 6 access panel lids; verify flush fit.

### Phase5 — Minimum Viable Flyer ★ FIRST FLIGHT
→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase5

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ES…
- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore…
- [ ] Phase 11 only:
- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.
- [ ] Pull motor phase leads through conduit to ESCs; solder (verify…
- [ ] CAN FD termination: 120Ω SOLDERED to CN1 Cape-B at Shepherd's r…
- [ ] Mount CN1 XO on Shepherd's room (Bay A) floor standoffs (M2.5…
- [ ] Mount FC1 Pilot on inter-cape standoffs (M2.5 nylon 20mm) above…
- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.
- [ ] CN1-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN1 Cape-B head…
- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa →…
- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~…
- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd…
- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Ba…
- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT…
- [ ] Cap Simon's medbay (Bay D) end of ETH-EA conduit (will connect…
- [ ] Mount CN2 XO on Inara's shuttle (Bay B) floor standoffs; inser…
- [ ] Flash OS to eMMC on CN2 and FC2 before installation.
- [ ] CN2-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN2 XO J_XCVR…
- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mou…
- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle: CN…
- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's s…
- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle): FC1 Pilot ET…
- [ ] Cap River's room (Bay C) end of ETH-BD (will connect to CN3 in…
- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR con…
- [ ] Provision TPM 2.0 (SLB9672) on CN1, FC1, CN2, FC2 — unique key…
- [ ] Verify CPLD write-blocker on CN1 and CN2: echo test > /mnt/flig…
- [ ] Configure forensic log mount in /etc/fstab (noexec, nodev, nosu…
- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.
- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.
- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.
- [ ] Verify 4-node CAN FD heartbeat ring: candump can0 shows frames…
- [ ] Configure MAVLink routing (mavlink-router) on elected FC master…
- [ ] Install the 49 MHz (Part 15 §15.235) daemon on CN1 and CN2 (sel…
- [ ] ESC calibration (full throttle power-on → drop to zero).
- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct…
- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° = hori…
- [ ] Rear nozzle servo endpoints verified.
- [ ] 190mm from nose
- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.
- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup); 49…
- [ ] Node failover: kill FC master power → standby assumes authority…
- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW; ESC…
- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE…
- [ ] Apply FAA registration number
- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)
- [ ] Tethered hover 1m AGL × 3 successful passes before free flight…
- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.…
- [ ] Free hover 3m AGL (yaw 360° both directions)
- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0° — altitude ho…
- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to ho…
- [ ] Verify flight log written to CN1-LOG and CN2-LOG
- [ ] Stable hover 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All 4 nacelle ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all segments
- [ ] All 4-node CAN FD heartbeats confirmed
- [ ] Node failover: standby assumes within 100ms of master power-kill
- [ ] Flight log on both CN μSDs; CPLD write-block verified

### Phase6 — Full 8-Node Architecture + ToF Obstacle Avoidance
→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase6

- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Pilot in Inara's s…
- [ ] Mount CN3 XO on River's room (Bay C) floor standoffs; insert P…
- [ ] CN3-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN3 XO J_XCVR…
- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm); mou…
- [ ] Continue CAN FD chain: Inara's shuttle (Bay B) FC2 → River's ro…
- [ ] Continue RS-485 chain Inara's shuttle (Bay B) → River's room (B…
- [ ] Connect ETH-BD (Inara's shuttle → River's room): FC2 Pilot ETH-1…
- [ ] Power tap River's room (Bay C); verify 5V ±0.05V.
- [ ] Mount CN4 XO on Simon's medbay (Bay D) standoffs; insert PB2-I…
- [ ] CN4-LOG
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN4 header.
- [ ] Route FC4 GPS coax through dorsal PTFE sleeve (sta ~350mm); mou…
- [ ] 120Ω PERMANENT
- [ ] Connect ETH-DE (River's room → Simon's medbay): FC3 Cape-A ETH-…
- [ ] Connect ETH-EA ring-close (Simon's medbay → Shepherd's room): F…
- [ ] Power tap Simon's medbay (Bay D); verify 5V ±0.05V.
- [ ] TPM 2.0 on CN3, FC3, CN4, FC4 — unique key material per node.
- [ ] CPLD write-blocker verification on CN3 and CN4.
- [ ] Verify RSTP ring: bridge vlan show; disconnect one ETH cable →…
- [ ] Verify full 8-node CAN FD ring: candump can0 shows frames 0x001…
- [ ] MIL-STD-1553 final config: FC1=BC, FC2=standby BC, FC3/FC4/CN1–…
- [ ] Install 6× VL53L5CX in Array B flush-mount frames; wire to TCA9…
- [ ] Install 6× VL53L5CX in Array A flush-mount frames; wire to TCA9…
- [ ] Apply 0.5mm PMMA disc over each sensor aperture with UV adhesiv…
- [ ] Configure OA fusion in firmware: halt at 1.0m obstacle clearanc…
- [ ] GPS clearance check for 49MHz wire post proximity: bench-verify…
- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed
- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s
- [ ] MIL-STD-1553: all 8 RTs respond within 9μs
- [ ] CN3 and CN4 log μSD write-block verified
- [ ] All 12 ToF sensors return valid range at ≤4m
- [ ] OA halt test: approach wall at 0.5m/s → stops at 1.0m clearance
- [ ] Array failure mode: either FC1 or FC3 loss → remaining array pr…
- [ ] 3-waypoint autonomous mission with GPS, altitude hold, RTL on s…

### Phase7 — Cargo System
→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase7

- [ ] Bond cargo gondola shell into belly void at 4× M3 hard points (…
- [ ] Install 3mm CF door hinge pins; attach clamshell door halves (s…
- [ ] Install SPT5425LV/LibreServo v2 winch + twin-pedestal spool + ratchet; wind Dy…
- [ ] Install SG90 door-actuator servo (spring-assist open, servo pul…
- [ ] Install SG90 payload-release servo; connect to DRV8833 IN1/IN2…
- [ ] Route control leads through PWR conduit belly tap to CN master…
- [ ] Seal gondola-hull perimeter with 3M foam gasket tape.
- [ ] Configure CN master GPIO: door open/close, winch deploy/retract…
- [ ] Door open/close × 10: no binding
- [ ] Winch deploy 1.5m: straight descent, line clear
- [ ] Winch retract: auto-latch clicks and holds at top
- [ ] 250g load test: winch deploy + retract × 5; latch holds
- [ ] Hover with 250g payload: altitude-hold degradation ≤10%
- [ ] Autonomous delivery: 3-waypoint mission, deploy at waypoint 2,…

### Phase8 — Finishing
→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase8

- [ ] Replace FAA N00000 placeholder in serenity/diagrams/decal_sheet…
- [ ] Print decal sheet on waterslide decal paper; seal with clear co…
- [ ] Apply decals per build_guide_19_decal_placement.svg: Serenity l…
- [ ] Final airworthiness inspection: all fasteners, propulsion, elec…
- [ ] Documentation archive: build log (photos + test results), Cape-…
- [ ] FAA compliance final check: registration visible without moving…

### Phase9 — Performance Tuning and Flight Envelope Expansion
→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase9

- [ ] Thrust stand calibration
- [ ] PID governor tuning
- [ ] Nacelle transition tuning
- [ ] Endurance test
- [ ] Cross-wind hover
- [ ] Extended autonomous mission
- [ ] T/W measured ≥1.10 (nacelles only) on thrust stand
- [ ] Hover altitude hold ±0.15 m for 60 s
- [ ] Nacelle transition altitude excursion ≤0.5 m
- [ ] Endurance ≥8 min at hover (6S 4000mAh baseline)
- [ ] Logs on all 4 CN nodes; write-block verified

### Phase10 — Advanced Autonomy and Long-Range Operations
→ detail: `graphical-build-guide/flight-phases/WBS.md` §Phase10

- [ ] BVLOS communication validation
- [ ] Extended waypoint missions
- [ ] Payload delivery mission
- [ ] Simulated node failure during flight
- [ ] Emergency RTL validation
- [ ] Regulatory readiness review
- [ ] Mission continues on any single surviving radio link
- [ ] 10-waypoint autonomous mission completed without intervention
- [ ] Autonomous cargo delivery within 2 m of target
- [ ] Node failure: remaining FCs maintain flight ≥30 s
- [ ] RTL on link loss: lands within 3 m of takeoff point
- [ ] All regulatory documentation current and on file

### Phase11 — Aft EDF Integration (Deferred)
→ detail: `deferred/WBS.md` §Phase11

- [ ] Scoop windows must be re-sized for the 55 mm EDF (reduced area).
- [ ] Remove temporary window covers from existing neck shell, or swa…
- [ ] Regenerate
- [ ] Regenerate
- [ ] Generate
- [ ] Generate
- [ ] Run mesh watertightness verification on all regenerated STLs; r…
- [ ] Dry-fit neck_intake_frame.stl into the resized scoop windows; r…
- [ ] Verify aerodynamic orientation: intake lips face forward (−Y /…
- [ ] Apply structural epoxy to tongues + shoulder flanges; press fra…
- [ ] Fillet all gaps between flange and hull; cure 2h.
- [ ] Dry-fit aft_edf_plenum.stl; verify intake arm alignment and 55m…
- [ ] Bond plenum forward arms to intake frame exits; fillet joints;…
- [ ] Bond rcs_distribution_manifold.stl to the 4 plenum bleed taps;…
- [ ] Pressure-test: seal EDF face with tape; cover all but one scoop…
- [ ] Bench-test 55mm EDF (correct rotation, no vibration).
- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bo…
- [ ] Seat EDF in plenum 55mm inlet; press forward to retaining lip;…
- [ ] Route motor leads through Panel F to 50A ESC; route signal lead…
- [ ] Install 50A ESC in Panel F bay; foam tape + cable tie. Cure 2h…
- [ ] Fixed — no moving petals.
- [ ] Install 4× rcs_thruster_nozzle.stl at their RCS stations; conne…
- [ ] Install 4× SG90-class proportional valves on rcs_valve_bracket.…
- [ ] Calibrate RCS valves: 0% = closed (no bleed); 100% = full bleed…
- [ ] Bond permanent aft 49 MHz (Part 15 §15.235) wire post to top of…
- [ ] Remove temporary aft post from station ~580mm.
- [ ] Restring 49MHz top wire (~470mm) from forward post to nozzle af…
- [ ] Enable ESC5 in FC2 firmware (PRU Ch.2); configure BDSHOT govern…
- [ ] Add the 4 RCS proportional-valve channels to the attitude-contr…
- [ ] Add rear EDF to the forward-thrust (cruise) schedule — NOT the…
- [ ] Verify all 5 ESC heartbeats on CAN FD; confirm FC2 cross-drive…
- [ ] Bench-test RCS attitude authority; then forward-flight thrust t…
- [ ] All regenerated rear-EDF STLs pass mesh watertightness verifica…
- [ ] Intake frame tongues fully seated in the resized scoop windows
- [ ] Plenum + RCS manifold pressure-test passed (draft at EDF inlet…
- [ ] EDF seated at station ~430mm, centerline ±2mm; rotation verifie…
- [ ] 50A ESC installed; ESC5 signal routed to FC2 PRU Ch.2
- [ ] Canonical nozzle bonded flush to hull outer mold line; exit 2.0…
- [ ] All 4 RCS valves calibrated; pitch/yaw authority confirmed on b…
- [ ] 49MHz aft wire post on canonical nozzle; top wire re-strung at…
- [ ] Forward-thrust test passed; rear EDF NOT used for hover lift; E…
- [ ] All 5 ESC telemetry visible on CAN FD; ESC temps ≤70°C at cruis…

### Phase12 — Cargo-bay Range-Extender Battery Module (Deferred)
→ detail: `deferred/WBS.md` §Phase12

- [ ] RBM module:
- [ ] Flight Engineer input:
- [ ] Current sharing:
- [ ] Firmware (pwr_fault):
- [ ] W&B:
- [ ] CAD:

---

## 4.0 — Firmware and Software

### 4.1 — Completed
→ detail: `avionics/firmware/WBS.md` §4.1

- [x] Firmware directory structure (serenity/firmware/) *(done 2026-0…
- [x] KISS/AX.25 UART driver for XCVR-49MHZ-1 — serenity/firmware/cn/…
- [x] Si5351A I²C driver — serenity/firmware/cn/src/si5351.c/.h *(don…
- [x] AM6254 device tree overlays — Cape-A and Cape-B DTSs *(done 202…
- [x] serenity-cn Phase 6 daemon (XCVR KISS driver + argparse + SIGTE…
- [x] serenity-fc Phase 6 stub (signal handling, idle loop placeholde…

### 4.2 — FC Node (Pilot) - Phase 7 Firmware
→ detail: `avionics/firmware/WBS.md` §4.2

- [ ] EDF ESC PID governor
- [ ] Nacelle tilt servo command generation (RS-485/LibreServo v2, was PWM under DS3218MG — see REFERENCES.md "Servo Fleet Standardisation, 2026-08-02")
- [ ] IMU / barometer sensor fusion
- [ ] ToF sensor array management
- [ ] u-blox M10Q GNSS integration
- [ ] MIL-STD-1553B RT implementation
- [ ] TPM-bound attestation
- [x] governor_cal.py
- [x] governor_config.h

### 4.3 — CN Node (XO) - Phase 7 Firmware
→ detail: `avionics/firmware/WBS.md` §4.3

- [ ] CAN FD heartbeat and telemetry forwarding
- [ ] MIL-STD-1553B BC/RT tasks
- [ ] RS-485 inter-board messaging
- [ ] Ethernet RSTP ring management
- [ ] Signed-log write via CPLD write-blocker
- [ ] TPM-bound HMAC on all outbound AX.25 payloads
- [ ] Cargo control
- [ ] MAVLink routing configuration

### 4.4 — Both Nodes
→ detail: `avionics/firmware/WBS.md` §4.4

- [ ] Node role election protocol
- [ ] Autonomous navigation
- [ ] OA integration
- [ ] GPS cross-check
- [ ] Security message signing

### 4.5 — Ground Control (Skipper / "CAPT Reynolds")

#### 4.5.1 — Skipper Hardware Design
→ detail: `gcs/WBS.md` §4.5

- [ ] Create Skipper host computer specification
- [ ] Skipper field enclosure — print and fit-check
- [ ] Gimbal STL generation and mesh verification
- [ ] Gimbal servo wind-load torque check
- [ ] Procure Skipper comms node hardware:
- [ ] Procure antenna hardware
- [ ] Procure gimbal hardware:

#### 4.5.2 — Skipper Comms Node Setup (Phase Skipper-2)
→ detail: `gcs/WBS.md` §4.5

- [ ] Flash Debian Linux to Skipper PB2-I eMMC
- [ ] Apply Cape-B-2 device tree overlay for Skipper
- [ ] Provision TPM 2.0 (SLB9672) on Skipper's PB2-I
- [ ] Verify CPLD write-blocker on Skipper's log μSD
- [ ] Build and install Skipper PB2-I firmware:
- [ ] Install and configure mavlink-router on Skipper's PB2-I
- [ ] Enable all 5 radio interfaces on Skipper's PB2-I
- [ ] Configure Wi-Fi transmit power

#### 4.5.3 — Skipper Host PC Software Setup (Phase Skipper-3)
→ detail: `gcs/WBS.md` §4.5

- [ ] Install Debian Linux on GCS host PC
- [ ] Run installation scripts in order:
- [ ] Configure QGroundControl:
- [ ] Configure Wi-Fi Tx power on host PC
- [ ] Run tracking software tests:
- [ ] Implement gcs/skipper/firmware/pb2i/src/skipper_comms.c and skipper_com…

#### 4.5.4 — Tracking and Gimbal Integration (Phase Skipper-3)
→ detail: `gcs/WBS.md` §4.5

- [ ] Bench test gimbal hardware
- [ ] Gimbal calibration:
- [ ] Run telemetry_feed.py bench test
- [ ] Run tracker.py bench test
- [ ] Run gimbal_ctrl.py bench test
- [ ] End-to-end tracking test (outdoor):

#### 4.5.5 — Skipper Integration Testing (Phase Skipper-4)
→ detail: `gcs/WBS.md` §4.5

- [ ] Multi-link communication bench test:
- [ ] 915 MHz link margin test (open field, 1 km):
- [ ] Wi-Fi link margin test (open field, 200 m):
- [ ] 49 MHz (Part 15 §15.235) link test (1 km):
- [ ] Gimbal pointing accuracy test (outdoor, aircraft at 200–500 m):
- [ ] MAVLink authentication test:
- [ ] Node loss with Skipper active:

### 4.6 — Observer Node (Nose/Cargo Vision, ToF & Laser) — Firmware

#### 4.6.1 — TI AM62Ax Vision Pipeline Bring-Up
→ detail: `avionics/observer/WBS.md` §4.6.1

- [ ] MIPI CSI-2 camera sensor bring-up
- [ ] VPAC/ISP pipeline configuration
- [ ] H.264/H.265 hardware encoder pipeline
- [ ] Kernel/BSP integration
- [ ] Bench test:

#### 4.6.2 — TI MSPM0G3507 Control Firmware
→ detail: `avionics/observer/WBS.md` §4.6.2

- [ ] MCAN (CAN-FD) driver bring-up
- [ ] TFmini-S UART driver
- [ ] KSZ9477 Ethernet switch management driver
- [ ] Laser GPIO driver (both sites Class 2 — docs/OBSERVER_LASER_ANALYS…
- [ ] Laser strobe + crosshair-metrology routine (AM62A7 ISP):
- [ ] SPI driver to Infineon SLB9672 TPM
- [ ] Signed telemetry:

#### 4.6.3 — Integration Testing
→ detail: `avionics/observer/WBS.md` §4.6.3

- [ ] Bench test:
- [ ] Ring failure test:
- [ ] Laser safety interlock test (nose only):

---

## 5.0 — Regulatory Compliance

### 5.1 — FCC (external radio systems)
→ detail: `docs/WBS.md` §5.1

- [ ] XCVR-49MHZ-1/2 FCC Part 15 §15.235 compliance
- [x] SiK 915MHz
- [x] LoRa RFM95W 915MHz
- [x] Wi-Fi (WL1837MOD)
- [x] ZigBee 2.4GHz (if used)

### 5.2 — FAA (airworthiness and operations)
→ detail: `docs/WBS.md` §5.2

- [ ] Aircraft registration
- [ ] Remote Pilot Certificate
- [ ] Navigation lights compliance
- [ ] sUAS data plate
- [ ] Pre-flight area check
- [ ] Airspace waiver (if applicable)

### 5.3 — Industry Standards Compliance
→ detail: `docs/WBS.md` §5.3

- [ ] Structural validation
- [ ] IEEE/ISA/AUVSI best practices
- [ ] Tamper-evident logging

---

## 6.0 — Version Control and Repository Maintenance

### 6.1 — Branch Reconciliation (2026-06-09)
→ detail: `docs/WBS.md` §6.1

- [x] claude/aft-edf-phase-11-CMM8b
- [x] claude/cape-em-harsh-variants-9Yfr1
- [x] claude/cargo-equipment-mounts-70I3i
- [x] claude/docs-scrub-revision-p-Y7pja
- [x] claude/kicad-silk-labels-HnUIe
- [x] claude/revision-q-avionics-archive-BXwZI
- [x] claude/revt-nacelle-simplified-3Ri7A
- [x] claude/todo-implementation-2LV2X
- [x] claude/todo-implementation-8bRee
- [x] claude/todo-implementation-AY2pY
- [x] claude/todo-implementation-by1W7
- [x] claude/wing-root-nacelle-mounts-5bSEA
- [ ] Delete stale feature branches

### 6.2 — STL Mesh Repair (2026-06-09)
→ detail: `docs/WBS.md` §6.2

- [x] Removed duplicate SEARCH_PATHS (airframe/stls/fuselage, nacelle…
- [x] Added per-body watertightness check: a mesh passes CI if mesh.i…
- [x] nacelle_nozzle_closed_asm.stl — repaired: 1704 → 1648 faces, wt…
- [x] nacelle_nozzle_petal.stl — repaired: 213 → 206 faces, wt=True
- [x] head_shell24_2mm_repaired.stl — repaired: 227428 → 226812 faces…
- [x] cargo_sect_shell24_2mm_repaired.stl — repaired: 368352 → 367506…
- [x] cargo_sect_shell24_2mm_repaired_largest.stl — repaired: 367514…
- [x] regenerated
- [x] feet_x_4_scaled24.stl — 4 feet (4 bodies, each wt=True)
- [x] rear_shell24_2mm_repaired.stl — 15 bodies, all wt=True
- [x] middle_shell24_2mm_repaired.stl — 10 bodies, all wt=True
- [x] dorsal_antenna_fin.stl — 3 bodies, all wt=True
    - **MESH FIX 2026-08-25** (surfaced by `airframe/freecad/assembly/
        SerenityAssembly.FCStd` failing to open cleanly — "mesh data
        structure has some defects"): re-measured, the published file
        actually carried 7 bodies — the 3 real ones this line recorded, plus
        4 degenerate zero-area single-triangle fragments not caught by a
        per-body watertight check (each fragment IS trivially "watertight"
        alone; the whole-file `trimesh.is_watertight` was False). Two of the
        3 real bodies also had inverted (negative-volume) winding. Fixed:
        dropped the 4 degenerate fragments, corrected winding
        (`trimesh.fix_normals`), unioned the 3 real bodies via `manifold3d`
        (same primitive as the sleeve fix above) — result is 1 body, 22
        faces (was 56 total across all 7), fully watertight, volume 2800 mm³
        matching the largest single real body exactly (the smaller box and
        the mast were both fully contained within its footprint — genuine
        duplicate/leftover fragments, not distinct features; visually
        re-verify this reads as the intended flat blade fin, not a
        mistakenly-collapsed multi-part design, before next print).
- [x] cargo_sect_shell24.stl — 190 bodies, all wt=True

### 6.3 — Rev S Checkpoint (2026-07-04)
→ detail: `docs/WBS.md` §6.3

### 6.4 — Rev T Checkpoint (2026-09-06)
→ detail: `docs/WBS.md` §6.4

---

*"Love. You can learn all the math in the 
'verse, but you take a boat in the air that you don't love, she'll shake you
off just as sure as the turning of the worlds. Love keeps her in the air when
she oughta fall down, tells you she's hurtin' 'fore she keels. Makes her
a home." — Capt. Skipper Reynolds*
