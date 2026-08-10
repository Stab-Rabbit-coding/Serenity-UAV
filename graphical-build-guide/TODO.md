# Serenity UAV — Phased Physical Build — Fabrication (Phases 0-4) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"Here's how it is: the Earth got used up. — opening narration"*

---

## §Phase0-4 — Print All Parts, Hull Structure, Nacelle/Tilt Assembly, Foam Pour

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

### Phase 1 — Hull Structure + All Future Provisions

- [ ] Epoxy keel through all hull sections; cure 2h. Datum marks at 9…
- [ ] Bond ring frames at all 5 station notches; cure 1h.
- [ ] Bond access panel frames A–F into hull sections (5-min epoxy, 3…
- [ ] Install M2.5 nylon standoffs in bays A, B, D, E (floor 6mm + in…
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

### Phase 2 — Nacelle Assembly

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

### Phase 3 — Tilt Mechanism

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

### Phase 4 — Hull Foam Pour + Close-up

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

### 1.5.6 Rebuild Graphical Build Guide

- [ ] Pipeline: Update silhouette pipeline (`gen_hull_outlines.py`)
- [ ] Pipeline: Update outline mapping (`update_overview_paths.py`)
- [ ] Pipeline: Coordinate alignment check
- [ ] Phase A (01/10): Rebuild `overview_front.svg`
- [ ] Phase A (02/10): Rebuild `overview_back.svg`
- [ ] Phase A (03/10): Rebuild `overview_left.svg`
- [ ] Phase A (04/10): Rebuild `overview_right.svg`
- [ ] Phase A (05/10): Rebuild `overview_top.svg`
- [ ] Phase A (06/10): Rebuild `overview_bottom.svg`
- [ ] Phase A (07/10): Rebuild `overview_isometric.svg`
- [ ] Phase A (08/10): Rebuild `overview_close_up_head.svg`
- [ ] Phase A (09/10): Rebuild `overview_close_up_cargo.svg`
- [ ] Phase A (10/10): Rebuild `overview_close_up_rear.svg`
- [ ] Phase B (1/2): Rebuild `build_plan.svg`
- [ ] Phase B (2/2): Rebuild `components_overview.svg`
- [ ] Phase C (01/10): Rebuild `build_guide_01_parts.svg`
- [ ] Phase C (02/10): Rebuild `build_guide_02_keel.svg`
- [ ] Phase C (03/10): Rebuild `build_guide_03_hull_prep.svg`
- [ ] Phase C (04/10): Rebuild `build_guide_04_keel_install.svg`
- [ ] Phase C (05/10): Rebuild `build_guide_05_ring_frames.svg`
- [ ] Phase C (06/10): Rebuild `build_guide_06_access_panels.svg`
- [ ] Phase C (07/10): Rebuild `build_guide_07_standoffs.svg`
- [ ] Phase C (08/10): Rebuild `build_guide_08_wing_spar.svg`
- [ ] Phase C (09/10): Rebuild `build_guide_09_avionics.svg`
- [ ] Phase C (10/10): Rebuild `build_guide_10_servos.svg`
- [ ] Phase D (01/10): Rebuild `build_guide_11_inter_board.svg`
- [ ] Phase D (02/10): Rebuild `build_guide_12_security_hw.svg`
- [ ] Phase D (03/10): Rebuild `build_guide_13_antennas.svg`
- [ ] Phase D (04/10): Rebuild `build_guide_14_49mhz_post.svg`
- [ ] Phase D (05/10): Rebuild `build_guide_15_49mhz_wire.svg`
- [ ] Phase D (06/10): Rebuild `build_guide_16_tof_frames.svg`
- [ ] Phase D (07/10): Rebuild `build_guide_17_conduits.svg`
- [ ] Phase D (08/10): Rebuild `build_guide_18_void_formers.svg`
- [ ] Phase D (09/10): Rebuild `build_guide_19_foam_pour.svg`
- [ ] Phase D (10/10): Rebuild `build_guide_20_node_placement.svg`
- [ ] Phase E (1/6): Rebuild `build_guide_21_node_install.svg`
- [ ] Phase E (2/6): Rebuild `build_guide_22_clamshell_doors.svg`
- [ ] Phase E (3/6): Rebuild `build_guide_23_winch_latch.svg`
- [ ] Phase E (4/6): Rebuild `build_guide_24_gondola.svg`
- [ ] Phase E (5/6): Rebuild `build_guide_25_nacelle_mount.svg`
- [ ] Phase E (6/6): Rebuild `build_guide_26_first_flight.svg`
- [ ] QA: Standards compliance check
- [ ] QA: STL coordinate check
- [ ] QA: Geometry validation

---