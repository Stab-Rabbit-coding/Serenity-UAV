# Serenity UAV — Phased Physical Build — Flight Phases (Phases 5-10) TODO (Open Work Only)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> **This file lists only currently-open (unchecked) top-level tasks for
> this subsystem — one line each, <=70 chars, no prose.** Full detail
> (notes, rationale, nested sub-steps, done items) lives in
> [`WBS.md`](WBS.md), the full historical record for project-progression
> tracking. Close an item in `WBS.md` first, then delete its line here.

*"Love keeps her in the air when she oughta fall down. — Capt. Skipper Reynolds"*

---

## §Phase5 — Minimum Viable Flyer ★ FIRST FLIGHT
→ full detail: `WBS.md` §Phase5

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ESCs.
- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore EDF…
- [ ] Phase 11 only: Install 50A ESC in Panel F for 55mm rear EDF (FC2 PRU…
- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.
- [ ] Pull motor phase leads through conduit to ESCs
- [ ] CAN FD termination: 120Ω SOLDERED to CN1 TACCO at Shepherd's room…
- [ ] Mount CN1 XO on Shepherd's room (Bay A) floor standoffs (M2.5 nylon…
- [ ] Mount FC1 Pilot on inter-cape standoffs (M2.5 nylon 20mm) above CN1
- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.
- [ ] Install log μSD (64GB) in CN1 TACCO log slot. Label: CN1-LOG.
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN1 TACCO header
- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA
- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~59mm)
- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd's…
- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Bay B).
- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT 0x01.
- [ ] Cap Simon's medbay (Bay D) end of ETH-EA conduit (will connect to…
- [ ] Mount CN2 XO on Inara's shuttle (Bay B) floor standoffs; insert PB2-I
- [ ] Flash OS to eMMC on CN2 and FC2 before installation.
- [ ] Install log μSD (64GB) in CN2 TACCO log slot. Label: CN2-LOG.
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN2 XO J_XCVR header.
- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm)
- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle
- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's…
- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle)
- [ ] Cap River's room (Bay C) end of ETH-BD (will connect to CN3 in Phase…
- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR conduit
- [ ] Provision TPM 2.0 (SLB9672) on CN1, FC1, CN2, FC2
- [ ] Verify CPLD write-blocker on CN1 and CN2: `echo test >…
- [ ] Configure forensic log mount in `/etc/fstab` (noexec, nodev, nosuid…
- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.
- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.
- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.
- [ ] Verify 4-node CAN FD heartbeat ring: `candump can0` shows frames…
- [ ] Configure MAVLink routing (mavlink-router) on elected FC master →…
- [ ] Install the 49 MHz (Part 15 §15.235) daemon on CN1 and CN2 (select…
- [ ] ESC calibration (full throttle power-on → drop to zero).
- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct…
- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° =…
- [ ] Rear nozzle servo endpoints verified.
- [ ] Static CG: 190mm from nose (adjust battery position on rail).
- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.
- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup)
- [ ] Node failover: kill FC master power → standby assumes authority…
- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW
- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE tail…
- [ ] Apply FAA registration number (14 CFR Part 48
- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)
- [ ] Tethered hover 1m AGL × 3 successful passes before free flight…
- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.3m)
- [ ] Free hover 3m AGL (yaw 360° both directions)
- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0°
- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to hover…
- [ ] Verify flight log written to CN1-LOG and CN2-LOG
- [ ] Stable hover 1m AGL in ≤15° headwind
- [ ] Nacelle transition without altitude excursion >1.5m
- [ ] All 4 nacelle ESCs ≤70°C at full hover power
- [ ] MAVLink telemetry live to QGC during all segments
- [ ] All 4-node CAN FD heartbeats confirmed
- [ ] Node failover: standby assumes within 100ms of master power-kill
- [ ] Flight log on both CN μSDs; CPLD write-block verified

### Phase 6 — Full 8-Node Architecture + ToF Obstacle Avoidance
→ full detail: `WBS.md` Phase6

- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Pilot in Inara's…
- [ ] Mount CN3 XO on River's room (Bay C) floor standoffs; insert PB2-I
- [ ] Flash OS to eMMC; install log μSD. Label: CN3-LOG.
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN3 XO J_XCVR header.
- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm)
- [ ] Continue CAN FD chain: Inara's shuttle (Bay B) FC2 → River's room…
- [ ] Continue RS-485 chain Inara's shuttle (Bay B) → River's room (Bay C)…
- [ ] Connect ETH-BD (Inara's shuttle → River's room)
- [ ] Power tap River's room (Bay C); verify 5V ±0.05V.
- [ ] Mount CN4 XO on Simon's medbay (Bay D) standoffs; insert PB2-I
- [ ] Flash OS to eMMC; install log μSD. Label: CN4-LOG.
- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN4 header.
- [ ] Route FC4 GPS coax through dorsal PTFE sleeve (sta ~350mm)
- [ ] Terminate CAN FD bus end: CN4 → FC4 + 120Ω PERMANENT soldered to FC4…
- [ ] Connect ETH-DE (River's room → Simon's medbay)
- [ ] Connect ETH-EA ring-close (Simon's medbay → Shepherd's room)
- [ ] Power tap Simon's medbay (Bay D); verify 5V ±0.05V.
- [ ] TPM 2.0 on CN3, FC3, CN4, FC4 — unique key material per node.
- [ ] CPLD write-blocker verification on CN3 and CN4.
- [ ] Verify RSTP ring: `bridge vlan show`; disconnect one ETH cable →…
- [ ] Verify full 8-node CAN FD ring: `candump can0` shows frames…
- [ ] MIL-STD-1553 final config: FC1=BC, FC2=standby BC, FC3/FC4/CN1–CN4=RT
- [ ] Install 6× VL53L5CX in Array B flush-mount frames
- [ ] Install 6× VL53L5CX in Array A flush-mount frames
- [ ] Apply 0.5mm PMMA disc over each sensor aperture with UV adhesive.
- [ ] Configure OA fusion in firmware: halt at 1.0m obstacle clearance
- [ ] GPS clearance check for 49MHz wire post proximity
- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed
- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s
- [ ] MIL-STD-1553: all 8 RTs respond within 9μs
- [ ] CN3 and CN4 log μSD write-block verified
- [ ] All 12 ToF sensors return valid range at ≤4m
- [ ] OA halt test: approach wall at 0.5m/s → stops at 1.0m clearance
- [ ] Array failure mode: either FC1 or FC3 loss → remaining array…
- [ ] 3-waypoint autonomous mission with GPS, altitude hold, RTL on…

### Phase 7 — Cargo System
→ full detail: `WBS.md` Phase7

- [ ] Bond cargo gondola shell into belly void at 4× M3 hard points…
- [ ] Install 3mm CF door hinge pins; attach clamshell door halves…
- [ ] Install the STS3215 winch train: both winch pedestals, the Ø4 mm…
- [ ] Install SG90 door-actuator servo (spring-assist open, servo…
- [ ] Install SG90 payload-release servo; connect to DRV8833 IN1/IN2 via…
- [ ] Route control leads through PWR conduit belly tap to CN master (CN1…
- [ ] Seal gondola-hull perimeter with 3M foam gasket tape.
- [ ] Configure CN master GPIO: door open/close, winch deploy/retract…
- [ ] Door open/close × 10: no binding
- [ ] Winch deploy 1.5m: straight descent, line clear
- [ ] Winch retract: auto-latch clicks and holds at top
- [ ] 250g load test: winch deploy + retract × 5; latch holds
- [ ] Hover with 250g payload: altitude-hold degradation ≤10%
- [ ] Autonomous delivery: 3-waypoint mission, deploy at waypoint 2…

### Phase 8 — Finishing
→ full detail: `WBS.md` Phase8

- [ ] Replace FAA N00000 placeholder in `serenity/diagrams/decal_sheet.svg`…
- [ ] Print decal sheet on waterslide decal paper; seal with clear coat
- [ ] Apply decals per `build_guide_19_decal_placement.svg`
- [ ] Final airworthiness inspection: all fasteners, propulsion…
- [ ] Documentation archive: build log (photos + test results), TACCO…
- [ ] FAA compliance final check: registration visible without moving any…

### Phase 9 — Performance Tuning and Flight Envelope Expansion
→ full detail: `WBS.md` Phase9

- [ ] Thrust stand calibration — run `airframe/scripts/governor_cal.py` on…
- [ ] PID governor tuning — in-flight hover trim
- [ ] Nacelle transition tuning — refine tilt servo rate and cross-axis…
- [ ] Endurance test — full charge 6S 4000mAh, hover 1m AGL until…
- [ ] Cross-wind hover — verify stable hover in ≥10 kt headwind
- [ ] Extended autonomous mission — 5-waypoint GPS mission, altitude hold…
- [ ] T/W measured ≥1.10 (nacelles only) on thrust stand
- [ ] Hover altitude hold ±0.15 m for 60 s
- [ ] Nacelle transition altitude excursion ≤0.5 m
- [ ] Endurance ≥8 min at hover (6S 4000mAh baseline)
- [ ] Logs on all 4 CN nodes; write-block verified

### Phase 10 — Advanced Autonomy and Long-Range Operations
→ full detail: `WBS.md` Phase10

- [ ] BVLOS communication validation — verify handover between all 4 radio…
- [ ] Extended waypoint missions — ≥10-waypoint autonomous mission at ≤400…
- [ ] Payload delivery mission — fully autonomous
- [ ] Simulated node failure during flight — kill one FC node mid-hover
- [ ] Emergency RTL validation — disable all control links
- [ ] Regulatory readiness review — FAA Part 107 waiver pre-application…
- [ ] Mission continues on any single surviving radio link
- [ ] 10-waypoint autonomous mission completed without intervention
- [ ] Autonomous cargo delivery within 2 m of target
- [ ] Node failure: remaining FCs maintain flight ≥30 s
- [ ] RTL on link loss: lands within 3 m of takeoff point
- [ ] All regulatory documentation current and on file

---
