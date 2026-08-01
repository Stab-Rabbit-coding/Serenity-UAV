# Serenity UAV — Phased Physical Build — Fabrication (Phases 0-4) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"Here's how it is: the Earth got used up. — opening narration"*

---

## §Phase0-4 — Print All Parts, Hull Structure, Nacelle/Tilt Assembly, Foam Pour
*(root `TODO.md` §Phase0-§Phase4)*


**Goal:** Every printed part complete and dry-fitted before first epoxy joint.

**Pre-print documentation (complete before any fabrication begins):**

- [x] **Flight Envelope Document** *(resolved 2026-07-12)* — created
    `docs/flight_envelope.md`:

    - [x] V_min vs. nacelle tilt angle — computed from wing area (19,025 mm², both wings), S1223 CL_max≈2.0, and nacelle thrust fraction; table at −5°/0°/10°/20°/30°/θ_hover≈38.3°/60°/90°/120°/140°; V_min=66.3 kt at 0° down to 0 kt (thrust-borne) at and above θ_hover

    - [x] V_max — regulatory ceiling 87 kt [REF-FAA-002 §107.51(a)]; EDF RPM ceiling carried from the existing `governor_config.h` EDF_RPM_MAX_50MM=35,000 RPM software redline (not converted to an airspeed — no validated drag polar exists); wing-spar structural order-of-magnitude check (≈811 kt) shown not to be the binding constraint.
      Actual achievable top speed explicitly left to Phase 9 flight test, not asserted here.

    - [x] Altitude operating limits — AGL 400 ft [REF-FAA-002 §107.51(b)]; MSL/density-altitude T/W margin computed (≈15,000 ft density altitude before T/W<1.0), a first-order estimate

    - [x] Maximum demonstrated crosswind — honestly marked pending Phase 9 flight test (no fabricated kt figures); computed engineering bound instead (hover max bank angle φ≈51.7° from T/W margin) plus the existing Phase 9 WBS ≥10 kt acceptance target

    - [x] Transition corridor — documented pre-flight-test operational floor of 20 ft (6.1 m) AGL (>12× margin over the Phase 9 ≤0.5 m excursion tuning target) to initiate a 90°→0° sweep, pending flight validation

- [x] **Failsafe Threshold Document** *(resolved 2026-07-12)* — created
    `docs/failsafe_thresholds.md` and `avionics/firmware/common/include/failsafe_config.h`:

    - [x] Battery low-voltage alert / RTL cutoff — **correction: the "3.7V/cell alert, 3.5V/cell RTL cutoff" defaults above are superseded.** `avionics/firmware/fc/src/pwr_fault.h` and `docs/POWER_DISTRIBUTION.md` §8.1 already implement and document a real WARN(3.50V)/CRITICAL(3.30V, RTL trigger)/EMERGENCY(3.00V) state machine, predating this WBS item's placeholder defaults.
      The new doc uses and cites the real, already-implemented values rather than the stale defaults (no firmware/doc change needed — this item was already done elsewhere, just not cross-referenced)

    - [x] Node heartbeat timeout for master re-election — 100ms, `FAILSAFE_CANFD_HEARTBEAT_TIMEOUT_MS` in the new `failsafe_config.h`

    - [x] Radio loss timer before automatic RTL — 5s SiK/LoRa, 10s 49 MHz (Part 15 §15.235), both newly defined in `failsafe_config.h`. **Open gap found and flagged (not fabricated):** Wi-Fi and Zigbee have no assigned RTL timer anywhere in the repository — new follow-up item below.

    - [x] ESC thermal cutback (85°C) / shutdown (95°C) — newly defined in `failsafe_config.h` as the Phase 0 documentation-gate design target.
      **Open reconciliation flagged (not silently applied):** `governor_config.h` already implements a single-stage `EDF_ESC_OVERTEMP_C=100` hard cutoff with no cutback stage; reconciling the two is a live-firmware safety-logic change and is deliberately left as a new follow-up item below rather than made in this documentation pass.

    - [x] ToF obstacle avoidance halt (1.0m) / resume (1.5m) clearance — newly defined in `failsafe_config.h`; both well within the VL53L5CX's 4 m rated range (`REFERENCES.md` REF-SENSOR-002 note)

    - [x] All thresholds defined as compile-time constants in `avionics/firmware/common/include/failsafe_config.h` (actual path; the WBS item's shorthand `firmware/common/failsafe_config.h` omitted the `avionics/` prefix used throughout the rest of the tree)

    - [ ] **New follow-up:** assign Wi-Fi (5 GHz) and Zigbee (2.4 GHz) link-loss RTL timers (currently no timer exists for either link, unlike SiK/LoRa and 49 MHz above) and add them to `failsafe_config.h` + `docs/failsafe_thresholds.md` §2.2.

    - [ ] **New follow-up:** reconcile `governor_config.h`'s existing single-stage `EDF_ESC_OVERTEMP_C=100` hard cutoff with the new two-stage 85°C cutback / 95°C shutdown scheme in `failsafe_config.h` — decide whether to add the cutback stage to `governor_config.h`'s live control loop and whether the existing 100°C hard fault should move to 95°C, then implement.

    - [ ] **New follow-up:** add a `REFERENCES.md` REF-ID for the VL53L5CX obstacle-avoidance sensor (currently only mentioned informally inside the REF-SENSOR-002 entry's comparison note).

- [x] **Electrical Fault Margin Validation** *(resolved 2026-07-12 — mostly
    already done, just not previously cross-referenced)* — created
    `docs/electrical_fault_margins.md` as a pointer document; three of the
    four checks were already fully analyzed in `docs/POWER_DISTRIBUTION.md`
    §9/§11 before this WBS item was picked up:

    - [x] Maximum ESC short-circuit current / fuse break time — already covered, `docs/POWER_DISTRIBUTION.md` §9.1 (40A mini-blade + 10AWG, correctly coordinated).
      **Correction: this WBS item's "XT30 + 100A poly fuse" reference is stale** — no 100A poly/PTC fuse exists anywhere in the current design (`current-specification/bom_revS.csv` specifies `FUSE-ESC-40A`, a 40A mini-blade, per ESC); flagged in the new doc rather than silently rewritten here.

    - [x] BEC brown-out threshold ≥4.90V — already covered, `docs/POWER_DISTRIBUTION.md` §9.2 (exact match to this item's target)

    - [x] Main bus fuse sizing — already covered, `docs/POWER_DISTRIBUTION.md` §9.4 (150A MAXI, 165A peak = 110%, >60s to trip; slightly more conservative than this item's own 160A peak estimate since it also accounts for simultaneous radio TX load)

    - [x] Balance of plant / single PWR conduit tap loss — **newly analyzed** (had no prior write-up): `docs/electrical_fault_margins.md` §4 documents that SMPS-channel-level redundancy exists (diode-OR'd dual TPS54620, `POWER_DISTRIBUTION.md` §11) but wiring-level rail-segment redundancy does NOT.
      That gap is covered architecturally by PACE avionics-role failover (root `CLAUDE.md`), not by the power wiring itself. Stated plainly rather than glossed over.

    - [ ] Balance of plant: verify that loss of any single PWR conduit tap does not collapse the 5V avionics rail (BEC must tolerate single-segment loss)

**Printer setup:**

- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)

- [ ] Calibrate E-steps and Pressure Advance for each filament

- [ ] Dry all filament 6 h at 65°C before printing

**Print schedule (ordered to minimize reprints):**

| Part | Material | Layer | Infill | Qty | Notes |
|------|----------|-------|--------|-----| ------ |
| feet_x_4_scaled24.stl | TPU 95A | 0.25mm | 40% | 1 set | |
| legs_scaled24.stl | CF-PETG | 0.15mm | 30% | 1 | |
| head_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| middle_canonical_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| cargo_sect_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| rear_neck_intake_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | Print now; cover reduced-area scoop windows (sized for 55mm EDF) with removable 3mm PETG blanks until Phase 11 |
| wings_s1223_revo.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| eng_left_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 | |
| eng_right_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 | |
| s_eng_piv_outer_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | |
| s_eng_piv_pins_scaled24.stl | CF-PETG | 0.15mm | 40% solid, 4 walls | 2 | |
| s_pivot_arm_a_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | |
| s_eng_pistons_scaled24.stl | PETG | 0.20mm | 20% gyroid | 2 | |
| wing_nacelle_pylon_revo.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | |
| nacelle_nozzle_petal.stl | PETG + translucent-blue inner | 0.20mm | 20% gyroid | 16 | |
| nacelle_nozzle_ring.stl | CF-PETG | 0.15mm | 40% | 2 | |
| nacelle_nozzle_iris.stl | PETG | 0.12mm | 40% | 2 | |
| rear_nozzle_canonical.stl | CF-PETG | 0.15mm | 30%, 4 walls | 1 | **DEFERRED — Phase 11.** Fixed canonical elliptical tail nozzle (2.06×1.76 in / 52.3×44.7 mm exit); replaces the old iris rear_nozzle_frame/petal. Requires regeneration for 55mm + canonical geometry — see §Phase 11. |
| rcs_thruster_nozzle.stl | CF-PETG | 0.15mm | 40%, 4 walls | 4 | **DEFERRED — Phase 11.** RCS bleed-air jet nozzle; fed from aft EDF plenum. Requires generation — see §Phase 11. |
| rcs_distribution_manifold.stl | PETG | 0.20mm | 30% | 1 | **DEFERRED — Phase 11.** Splits ~15% EDF mass flow to the 4 RCS proportional valves. Requires generation — see §Phase 11. |
| rcs_valve_bracket.stl | CF-PETG | 0.15mm | 40% | 4 | **DEFERRED — Phase 11.** SG90-class proportional valve mount, one per RCS jet. Requires generation — see §Phase 11. |
| nacelle_sector_gear.stl | CF-PETG | 0.12mm | 40%, 4 walls | 2 | |
| nacelle_pinion.stl | PETG or resin | 0.12mm | 40% | 4 | |
| nacelle_bevel_pair.stl | PETG or resin | 0.12mm | 40% | 2 sets | |
| nacelle_bevel_housing.stl | CF-PETG | 0.15mm | 40% | 2 | |
| rcrs49_wire_post.stl | PETG | 0.15mm | 40% | 2 | |
| Access panel frames A–F + lids | PETG | 0.20mm | 100% | 1 set | |
| s_cargo_gondola_shell.stl | PETG | 0.20mm | 15% gyroid | 1 | |
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

- [ ] Unison ring gear seats flush in the throat housing; the 8 flaps hinge freely on their 3mm×18mm tangential pins and each follower pin rides its spiral cam slot smoothly (no binding across the full 0°→90° sweep)

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

- [ ] Install SMA bulkheads: belly port (SiK 915MHz, X≈260mm), belly stbd (LoRa, X≈260mm), dorsal (Wi-Fi, X≈140mm).

- [ ] Install 49 MHz (Part 15 §15.235) forward wire post (dorsal, X≈120mm, bonded with 5-min epoxy).

- [ ] Install 49 MHz (Part 15 §15.235) **temporary** aft wire post: PETG hook bonded to aft dorsal hull skin near station ~580mm (NOT on rear nozzle frame — that post is Phase 11). This temporary post reduces antenna length slightly; field-strength compliance with 47 CFR §15.235 is firmware power-limited (see §0.1), not antenna-length dependent.

- [ ] String 49MHz top wire (0.3mm SS wire or 22AWG enamelled Cu) from forward post to temporary aft post with ~20g tension; CF keel connected to the 49 MHz (Part 15 §15.235) GND as counterpoise.

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

- [ ] Press a 2mm×4mm follower pin (PIN-2X4) into each of the 8 flaps' cam-follower lugs.

- [ ] Hinge the 8 flaps to the throat housing on 3mm×18mm tangential pins (PIN-3X18); seat each follower pin in its spiral cam slot on the unison ring.

- [ ] Dry-test: manually rotate the unison ring — flaps sweep smoothly 0°→90° (75%→105% bore), no binding, follower pins stay captured in the cam slots.

**2C — Gear linkage (per nacelle):**

- [ ] Mount sector gear to tilt bracket (FIXED — does not rotate with nacelle).

- [ ] Mount drive pinion on nacelle outer shell at pivot axis; mesh with sector gear; set backlash 0.1–0.2mm.

- [ ] Install bevel gear pair in nacelle body (nacelle-axis → longitudinal axis redirect).

- [ ] Thread 2mm steel longitudinal shaft through nacelle wall channel toward nozzle end.

- [ ] Mount crown pinion on shaft at nozzle end; mesh with Idler-In on the
    compound idler gear (`nacelle_nozzle_idler.scad`); set backlash 0.1–0.2mm.

- [ ] Mount idler gear on its bracket to the nozzle outer housing; mesh
    Idler-Out with the full-circle nozzle ring gear; set backlash 0.1–0.2mm.

- [ ] **Full sweep test (Rev R1, 2026-06-22):** rotate nacelle -5°→140°;
    verify nozzle ring gear rotates from ≈-1.33° to ≈38.45° (≈23.86° at the
    90° hover reference point), and petals swing from ≈18.76 mm to
    ≈34.42 mm tip radius (75%→105% of the 50 mm bore at the 0°/90°
    reference points) without binding against `HOUSING_INNER_R`=37.5 mm.
    Verify nozzle ring hard stop prevents over-drive beyond -5°/140°.

- [ ] Confirm petal closed position matches nacelle hull profile at 0°.

**Phase 2 checks:**

- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake

- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle

- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep

- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°

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


## §1.5.6 — Graphical Build Guide Rebuild ★

*(root `TODO.md` §1.5, detailed here — see also `docs/TODO.md` §1.5 for the general
documentation item this expands)*

> *“Love keeps her in the air when she oughta fall down.” — Captain Malcolm Reynolds*

This section covers the comprehensive rebuild of the graphical build guide's SVG assets and pipeline, transitioning from pre-Rev-N hand-drawn line art to 24-inch Rev R1 Blender and FreeCAD assembly-derived silhouettes. This process resolves the two major stale-geometry issues: hand-drawn line art of archived hardware (Cape-A-1/Cape-B-1) on 7 critical cards, and a partial silhouette pipeline referencing 18-inch pre-Rev-N models.

### 1.5.6 Rebuild Graphical Build Guide

- [ ] **Pipeline: Update silhouette pipeline (`gen_hull_outlines.py`)** — Refactor to source outlines from canonical 24" Rev R1 baked hull-frame STLs in `airframe/stls/` instead of pre-Rev-N 18" geometry.
- [ ] **Pipeline: Update outline mapping (`update_overview_paths.py`)** — Automate 2D path extraction and injection into 10 overview/silhouette SVG files.
- [ ] **Pipeline: Coordinate alignment check** — Verify outline-derivation pipeline matches Hull-Frame Coordinate Standard (X=+port, Y=+aft, Z=+dorsal).
- [ ] **Phase A (01/10): Rebuild `overview_front.svg`** — Generate front silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (02/10): Rebuild `overview_back.svg`** — Generate back silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (03/10): Rebuild `overview_left.svg`** — Generate left silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (04/10): Rebuild `overview_right.svg`** — Generate right silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (05/10): Rebuild `overview_top.svg`** — Generate top silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (06/10): Rebuild `overview_bottom.svg`** — Generate bottom silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (07/10): Rebuild `overview_isometric.svg`** — Generate isometric silhouette from 24" Rev R1 canonical CAD geometry.
- [ ] **Phase A (08/10): Rebuild `overview_close_up_head.svg`** — Generate close-up silhouette of 24" nose flat and bow sensor pod.
- [ ] **Phase A (09/10): Rebuild `overview_close_up_cargo.svg`** — Generate close-up silhouette of clamshell doors and winch mounts.
- [ ] **Phase A (10/10): Rebuild `overview_close_up_rear.svg`** — Generate close-up silhouette of aft engine-room and tandem EDF bays.
- [ ] **Phase B (1/2): Rebuild `build_plan.svg`** — Update master construction sequence flow chart to map 26 steps and milestones.
- [ ] **Phase B (2/2): Rebuild `components_overview.svg`** — Update exploded physical component map with 45 CAD-derived BOM parts.
- [ ] **Phase C (01/10): Rebuild `build_guide_01_parts.svg`** — Physical inventory and STL check card with 24" hull-frame components.
- [ ] **Phase C (02/10): Rebuild `build_guide_02_keel.svg`** — Carbon fiber keel prep showing datum marks at 91, 165, 251, 320, and 388mm.
- [ ] **Phase C (03/10): Rebuild `build_guide_03_hull_prep.svg`** — Hull section alignment card (head, cargo, middle, rear).
- [ ] **Phase C (04/10): Rebuild `build_guide_04_keel_install.svg`** — Keel insertion and bonding card.
- [ ] **Phase C (05/10): Rebuild `build_guide_05_ring_frames.svg`** — Ring frame placement and 5 station notches.
- [ ] **Phase C (06/10): Rebuild `build_guide_06_access_panels.svg`** — Access panel frame installation card for all 6 panels.
- [ ] **Phase C (07/10): Rebuild `build_guide_07_standoffs.svg`** — Avionics bay standoff positioning with correct M2.5 standoff locations.
- [ ] **Phase C (08/10): Rebuild `build_guide_08_wing_spar.svg`** — Wing spar sleeve mounting.
- [ ] **Phase C (09/10): Rebuild `build_guide_09_avionics.svg`** — **STALE geometry Cape-A/B fix:** Replace archived Cape-A-1/Cape-B-1 line art with active Rev R1 Cape-A-2 (Wash) and Cape-B-2 (Zoë) baseline layout. Ensure standards citations (`[REF-ID]`) survive.
- [ ] **Phase C (10/10): Rebuild `build_guide_10_servos.svg`** — Nacelle tilt servo bracket and sector gear assembly.
- [ ] **Phase D (01/10): Rebuild `build_guide_11_inter_board.svg`** — **STALE Cape-A/B fix:** Replace archived Cape-A-1/Cape-B-1 wiring schematic with active Cape-A-2 (Wash), Cape-B-2 (Zoë), Emma (XCVR-49MHZ-2), Kaylee, and Jayne inter-board CAN FD, RS-485, and Ethernet wiring.
- [ ] **Phase D (02/10): Rebuild `build_guide_12_security_hw.svg`** — **STALE Cape-A/B fix:** Update with active Cape-A-2 (Wash) and Cape-B-2 (Zoë) crypto-elements (TPM 2.0 enrollment, key generation, and operator certificates).
- [ ] **Phase D (03/10): Rebuild `build_guide_13_antennas.svg`** — Antenna SMA bulkheads and coax wire routing.
- [ ] **Phase D (04/10): Rebuild `build_guide_14_49mhz_post.svg`** — 49 MHz forward and temporary aft posts (temporary post at station ~580mm).
- [ ] **Phase D (05/10): Rebuild `build_guide_15_49mhz_wire.svg`** — 49 MHz wire tensioning and grounding with keel counterpoise.
- [ ] **Phase D (06/10): Rebuild `build_guide_16_tof_frames.svg`** — 12× VL53L5CX time-of-flight sensor frame mounting.
- [ ] **Phase D (07/10): Rebuild `build_guide_17_conduits.svg`** — PTFE wiring conduit threading.
- [ ] **Phase D (08/10): Rebuild `build_guide_18_void_formers.svg`** — EPS void former dry-fitting and pull string verification.
- [ ] **Phase D (09/10): Rebuild `build_guide_19_foam_pour.svg`** — PU foam zone-controlled injection (3 shots aft->fwd, <=60 mL per batch).
- [ ] **Phase D (10/10): Rebuild `build_guide_20_node_placement.svg`** — **STALE Cape-A/B fix:** Update 8-node arch placement showing all 8 nodes carrying active Cape-A-2 (Wash) and Cape-B-2 (Zoë) with uniform 5 kV galvanic isolation. Depict Emma transceivers only in River's Room and Simon's Medbay nodes (per `REF-FCC-003`).
- [ ] **Phase E (1/6): Rebuild `build_guide_21_node_install.svg`** — **STALE Cape-A/B fix:** Rebuild flight control node mounting card showing Cape-A-2 (Wash) and Cape-B-2 (Zoë) physical mounting, CAN FD terminal access, and isolated port wiring.
- [ ] **Phase E (2/6): Rebuild `build_guide_22_clamshell_doors.svg`** — Clamshell cargo doors, hinges at X≈-117.6mm, -222.5mm, and hinge retention blocks.
- [ ] **Phase E (3/6): Rebuild `build_guide_23_winch_latch.svg`** — Winch spool (STS3215 servo,
    twin pedestals, ratchet ring + pawl) and autolatch cargo cradle assembly card. Must show
    the spool supported at BOTH ends, not on the motor shaft.
- [ ] **Phase E (4/6): Rebuild `build_guide_24_gondola.svg`** — Gondola payload containment build and connection points.
- [ ] **Phase E (5/6): Rebuild `build_guide_25_nacelle_mount.svg`** — 50mm tandem EDF nacelle mounting, iris nozzle gear train, and sector gear.
- [ ] **Phase E (6/6): Rebuild `build_guide_26_first_flight.svg`** — Pre-flight checklist and initial hover (verify 4-radio link handover).
- [ ] **QA: Standards compliance check** — Re-verify all standards citations (`[REF-ID]`) in REFERENCES.md survive and are mapped correctly.
- [ ] **QA: STL coordinate check** — Ensure alignment with Hull-Frame Coordinate Standard.
- [ ] **QA: Geometry validation** — Run `validate_stls.py` on source files to prevent mesh defect propagation.

