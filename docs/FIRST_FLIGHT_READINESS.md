# Serenity UAV — First-Flight Readiness: Open-Item Summary

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0  
**Compiled by:** Claude (Opus 4.8), 2026-07-05, from master `WBS.md` (md5 `829246af291844cd6b557230e8430a12`).

> **First flight = master WBS Phase 5, "Minimum Viable Flyer."**
> Goal: CN1+FC1 (Shepherd's room / Bay A) and CN2+FC2 (Inara's shuttle / Bay B)
> installed and flying — a 4-node VTOL hover (nacelle T/W ~1.61). The aft EDF
> (Phase 11), the remaining 4 nodes (Phase 6), cargo (Phase 7), and Observer vision
> (Phase 6+) are **not** first-flight gates. This report rolls up every open item
> on the critical path to that milestone.

*"Define 'interesting.'" / "Oh God, oh God, we're all gonna die?" — Pilot & Skipper*


---


## Critical-path branches

| Master § | Branch | Open | Owning WBS file | Notes |
|----------|--------|-----:|-----------------|-------|
| §1.1 | 3D Models: SCAD -> STL Exports (Rev S baseline) | 88 | [airframe](../airframe/WBS.md) + fuselage-joints/-covers/-mid, wings-nacelles, landing-gear | Only the Phase-0/5 parts gate flight; §1.1 also carries Phase 6-11 geometry. |
| §1.2a | PCB Design: Pilot, XO, Commo (EMI-hardened) | 37 | [avionics](../avionics/WBS.md) | Pilot + XO EMI-hardened capes for the 4 MVP nodes (2 bays x 2). |
| §1.2b | PCB Redesigns: Commo / XO / Flight Engineer Rev S1 | 26 | [avionics/rev-s1](../avionics/rev-s1/WBS.md) | **Flight Engineer PDB** completion gates flight; Commo/XO-Rev-S1 items do not. |
| §0.6 | IEC 62368-1 PCB Layout Isolation Verification | 0 | [avionics/emi-hardening](../avionics/emi-hardening/WBS.md) | IEC 62368-1 isolation sign-off before any board is fabbed. |
| §1.4 | EMI Hardening Beyond the PCBs (500 W/m^2) | 43 | [avionics/emi-hardening](../avionics/emi-hardening/WBS.md) | 500 W/m^2 hardening is a design objective; a benign-environment maiden hover can precede full §1.4 close-out (annotate risk). |
| §4.2 | FC Node (Pilot) Firmware | 38 | [avionics/firmware](../avionics/firmware/WBS.md) | FC (Pilot) node firmware — PID governor, tilt, failover. |
| §4.3 | CN Node (XO) Firmware | 36 | [avionics/firmware](../avionics/firmware/WBS.md) | CN (XO) node firmware — comms, logging. |
| §4.4 | Both Nodes (shared firmware) | 22 | [avionics/firmware](../avionics/firmware/WBS.md) | Shared node firmware (TPM, signing, CAN/1553). |
| §4.5 | Ground Control (Skipper / CAPT Reynolds) | 34 | [gcs](../gcs/WBS.md) | Skipper GCS — needed to command/monitor the maiden flight. |
| §5.2 | FAA (airworthiness and operations) | 6 | [docs](../docs/WBS.md) | FAA registration + Part 107 remote-pilot currency — legal gate to fly. |
| §6.1 | Branch Reconciliation / Pre-Flight Compliance | 1 | [docs](../docs/WBS.md) | Pre-flight compliance: nav lights, data plate, structural validation. |
| §3.0 | **Physical build Phases 0-5** | **160** | [graphical-build-guide](../graphical-build-guide/WBS.md) (Phases 0-4) + [flight-phases](../graphical-build-guide/flight-phases/WBS.md) (Phase 5 = FIRST FLIGHT) | The literal build-to-flight sequence (enumerated below). |

**Prerequisite branches (design / PCB / firmware / GCS / regulatory): 331 open.**  
**Physical build Phases 0-5: 160 open.**  
Not every prerequisite item is strictly Phase-5 scoped (e.g. §1.1 and §4.5 carry post-MVP work); see each owning WBS file for the full branch. The physical-build enumeration below is exhaustive for Phases 0-5.


---

## Physical build to first flight — full open checklist (Phases 0-5)


### Phase 0 — Print All Parts + CF Cuts  (30 open)

- [x] **Flight Envelope Document** *(resolved 2026-07-12 — see master WBS.md §3.0 Phase 0)* — created `docs/flight_envelope.md`.
- [x] **Failsafe Threshold Document** *(resolved 2026-07-12 — see master WBS.md §3.0 Phase 0)* — created `docs/failsafe_thresholds.md` and `avionics/firmware/common/include/failsafe_config.h`. 2 new follow-ups opened (Wi-Fi/Zigbee RTL timer gap; ESC thermal reconciliation with `governor_config.h`) — see master.
- [x] **Electrical Fault Margin Validation** *(resolved 2026-07-12 — see master WBS.md §3.0 Phase 0)* — created `docs/electrical_fault_margins.md`; 3 of 4 checks were already done in `docs/POWER_DISTRIBUTION.md` §9/§11, only cross-referenced here.
- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)
- [ ] Calibrate E-steps and Pressure Advance for each filament
- [ ] Dry all filament 6 h at 65°C before printing
- [ ] Nacelle bore caliper: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm
- [ ] Stator fins visible in Z=53–95 mm gap (between the two EDF seats)
- [ ] Hub bore clear at stator: 16 mm ID minimum (motor leads)
- [ ] Sector gear ↔ pinion dry-mesh: 0.1–0.2 mm backlash
- [ ] Unison ring gear seats flush in the throat housing; the 8 flaps hinge freely on their 3mm×18mm tangential pins and each follower pin rides its spiral cam slot smoothly (no binding across the full 0°→90° sweep)
- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bearings seated
- [ ] All access panel lids flush ±0.2 mm in frames
- [ ] Keel dry-fits through all hull sections without force
- [ ] Rear neck shell scoop windows covered with removable 3mm PETG blanks (4 blanks, silicone-sealed)

### Phase 1 — Hull Structure + All Future Provisions  (23 open)

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
- [ ] Hull rigid — no flex when held at nose and tail
- [ ] All 8 pull strings accessible at both ends
- [ ] All standoffs in place; screws start freely
- [ ] Foam not in nacelle mounting bay, pivot housing, or panel bays
- [ ] All 6 access panel lids flush ±0.2 mm; latches/magnets engage

### Phase 2 — Nacelle Assembly  (23 open)

- [ ] Test EDF rotation direction on bench before installation: port = CW from intake; stbd = CCW from intake. Swap any two motor phase wires to reverse.
- [ ] Install EDF2 (aft/downstream) from nozzle end; seat at Z=5mm shoulder; epoxy 3 dabs at Z=50mm stator shoulder; route leads through hub bore.
- [ ] Install EDF1 (fore/upstream) from intake end; seat at Z=76mm; verify stator fins clear in Z=53–73mm gap; epoxy 3 dabs at Z=76mm shoulder.
- [ ] ESC pair: route to fuselage bay via spar conduit (ESC heat must NOT be trapped in nacelle bore).
- [ ] Cure 2h before proceeding.
- [ ] Repeat for stbd nacelle (opposite rotation direction).
- [ ] Press nacelle_nozzle_ring.stl onto nozzle exit face; confirm flush.
- [ ] Install nozzle inner ring (rack, R=28mm) inside base ring.
- [ ] Press a 2mm×4mm follower pin (PIN-2X4) into each of the 8 flaps' cam-follower lugs.
- [ ] Hinge the 8 flaps to the throat housing on 3mm×18mm tangential pins (PIN-3X18); seat each follower pin in its spiral cam slot on the unison ring.
- [ ] Dry-test: manually rotate the unison ring — flaps sweep smoothly 0°→90° (75%→105% bore), no binding, follower pins stay captured in the cam slots.
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
- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake
- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle
- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep
- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°

### Phase 3 — Tilt Mechanism  (12 open)

- [ ] Press MF104ZZ bearings into pivot housing bores (both ends); flush ±0.2mm.
- [ ] Insert 4mm CF pivot rod through wing spar pocket + pivot housing bearings (rod is FIXED to fuselage; nacelle rotates on it).
- [ ] Slide nacelle pivot housing onto pivot rod; verify <0.5mm axial play.
- [ ] Install tilt servos in fuselage servo mount bracket at wing root bay.
- [ ] Connect pushrods (servo arm → pivot arm): servo 0° = nacelle 0° (cruise), servo ~125° = nacelle 90° (hover), servo ~170° = nacelle 120° (backing).
- [ ] Install CF-PETG hard stop blocks; bond at −5° stop and 140° stop positions.
- [ ] Servo calibration: set FC software travel limits at −5° and 140°; verify both nacelles reach 90° simultaneously.
- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble
- [ ] Hard stops engage at −5° and 140° (servo stalls, does not strip)
- [ ] Nozzle opens/closes correctly via gear linkage through sweep (from Phase 2)
- [ ] Sector gear does NOT rotate with nacelle
- [ ] Both nacelles synchronise to within 2° at 0° and 90°

### Phase 4 — Hull Foam Pour + Close-up  (11 open)

- [ ] All PTFE conduits routed — pull strings accessible at both ends
- [ ] All bay standoffs installed
- [ ] Cargo hard points installed
- [ ] SMA bulkheads installed and dusted
- [ ] EPS void formers waxed (2 coats) and seated
- [ ] Nacelle bays and pivot housings masked OFF
- [ ] Servo mount brackets clear of foam path
- [ ] Mix X-30 per manufacturer (2:1 ratio by volume, 2-min pot life, 4× expansion). Pour in 3 shots: aft bay → mid bays (D+C) → forward bays (B+A). Allow 24h full cure before next shot.
- [ ] After full cure: remove EPS void formers; IPA wipe bay walls; verify foam did not intrude into panel bays, cargo bay, or conduit runs.
- [ ] Pull all 8 pull strings — verify still move freely.
- [ ] Install all 6 access panel lids; verify flush fit.

### Phase 5 — Minimum Viable Flyer  * FIRST FLIGHT  (61 open)

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ESCs.
- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore EDF = FC1; aft EDF = FC2).
- [ ] **Phase 11 only:** Install 50A ESC in Panel F for 55mm rear EDF (FC2 PRU Ch.2) — skip for Phase 5.
- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.
- [ ] Pull motor phase leads through conduit to ESCs; solder (verify rotation marking first).
- [ ] CAN FD termination: 120Ω SOLDERED to CN1 Cape-B at Shepherd's room (Bay A, bus start); temporary 120Ω at FC2 Cape-A in Inara's shuttle (Bay B, Phase 3 far-end; remove in Phase 7).
- [ ] Mount CN1 XO on Shepherd's room (Bay A) floor standoffs (M2.5 nylon 6mm). Insert PB2-I. Secure.
- [ ] Mount FC1 Pilot on inter-cape standoffs (M2.5 nylon 20mm) above CN1. Insert second PB2-I.
- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.
- [ ] Install log μSD (64GB) in CN1 Cape-B log slot. Label: **CN1-LOG**.
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN1 Cape-B header; connect its coax to forward 49 MHz wire post.
- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa → belly stbd SMA; Wi-Fi → dorsal fwd SMA.
- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~59mm); mount GPS patch on hull dorsal, face UP.
- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd's room (Bay A) toward Inara's shuttle (Bay B).
- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Bay B).
- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT 0x01.
- [ ] Cap Simon's medbay (Bay E) end of ETH-EA conduit (will connect to FC4 in Phase 7); connect Shepherd's room (Bay A) end to CN1 Cape-B ETH-2.
- [ ] Mount CN2 XO on Inara's shuttle (Bay B) floor standoffs; insert PB2-I; mount FC2 Pilot above.
- [ ] Flash OS to eMMC on CN2 and FC2 before installation.
- [ ] Install log μSD (64GB) in CN2 Cape-B log slot. Label: **CN2-LOG**.
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN2 XO J_XCVR header.
- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mount GPS patch on dorsal hull, face UP.
- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle: CN2 → FC2 + temporary 120Ω at FC2 (remove Phase 7).
- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's shuttle (Bay B).
- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle): FC1 Pilot ETH-1 → CN2 XO ETH-B (FC1↔CN2 Ethernet ring link).
- [ ] Cap River's room (Bay D) end of ETH-BD (will connect to CN3 in Phase 7).
- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR conduit; verify 5V ±0.05V at each header.
- [ ] Provision TPM 2.0 (SLB9670) on CN1, FC1, CN2, FC2 — unique key material per node.
- [ ] Verify CPLD write-blocker on CN1 and CN2: `echo test > /mnt/flightlog/test.txt` must return read-only error.
- [ ] Configure forensic log mount in `/etc/fstab` (noexec, nodev, nosuid, ro) on CN1 and CN2.
- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.
- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.
- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.
- [ ] Verify 4-node CAN FD heartbeat ring: `candump can0` shows frames 0x001–0x004 within 100ms.
- [ ] Configure MAVLink routing (mavlink-router) on elected FC master → SiK 915MHz on CN master.
- [ ] Install the 49 MHz (Part 15 §15.235) daemon on CN1 and CN2 (select channel per 47 CFR §15.235; not §95.623, which does not apply to this band).
- [ ] ESC calibration (full throttle power-on → drop to zero).
- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct directions.
- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° = horizontal ±0.5°.
- [ ] Rear nozzle servo endpoints verified.
- [ ] Static CG: **190mm from nose** (adjust battery position on rail).
- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.
- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup); 49 MHz (Part 15 §15.235) RC channels correct; Wi-Fi GCS telemetry.
- [ ] Node failover: kill FC master power → standby assumes authority within 100ms on tether.
- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW; ESC temps ≤60°C.
- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE tail, WHITE belly strobe).
- [ ] **Apply FAA registration number** (14 CFR Part 48 — replaces N00000 placeholder on airframe).
- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)
- [ ] Tethered hover 1m AGL × 3 successful passes before free flight (nacelles at 90°, ~60% throttle)
- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.3m)
- [ ] Free hover 3m AGL (yaw 360° both directions)
- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0° — altitude hold ±1.5m during transition
- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to hover, land
- [ ] Verify flight log written to CN1-LOG and CN2-LOG
- [ ] Stable hover 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All 4 nacelle ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all segments
- [ ] All 4-node CAN FD heartbeats confirmed
- [ ] Node failover: standby assumes within 100ms of master power-kill
- [ ] Flight log on both CN μSDs; CPLD write-block verified

---


## How to use this report

1. Clear the **prerequisite branches** (design, PCB fab, firmware, GCS, regulatory) in their owning WBS files — these unblock the build.
2. Work the **Phase 0-5 checklist** top-to-bottom; each phase gates the next.
3. Phase 5 completion = first flight. Re-baseline into Rev T and pick up Phase 6+ from the master `WBS.md`.


*Regenerate after master edits; this is a point-in-time rollup, not a live mirror. The master `WBS.md` is always authoritative.*
