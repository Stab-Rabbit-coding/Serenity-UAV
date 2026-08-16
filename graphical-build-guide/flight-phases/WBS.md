# Serenity UAV — Phased Physical Build — Flight Phases (Phases 5-10) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control").

*"Love keeps her in the air when she oughta fall down. — Capt. Malcolm Reynolds"*

---

## §Phase5 — Minimum Viable Flyer ★ FIRST FLIGHT
*(root `WBS.md` §Phase5)*


**Goal:** CN1+FC1 (Shepherd's room / Bay A) and CN2+FC2 (Inara's shuttle / Bay B) installed and operational — first flight achieved.

> **Aft EDF not installed** (Phase 11). The 4 nacelle XFly Galaxy X5 EDFs (1240g each, 90%
> additive via stator = 2232g/nacelle × 2 = 4464g total) deliver T/W ≈ **1.61** at the
> Phase 5–10 AUW of ~2,768g — **full VTOL hover is achievable from Phase 5**. Phase 11
> adds the 55mm rear EDF for **forward-flight (cruise) thrust and RCS attitude authority** — it
> exhausts aft through the canonical nozzle and is not counted in hover (Phase 11 hover T/W ≈ 1.43).

**Dependency:** Cape-A (×2) and Cape-B (×2) PCB assemblies received from JLCPCB.

**Power system:**

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ESCs.

- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore EDF = FC1; aft EDF = FC2).

- [ ] **Phase 11 only:** Install 50A ESC in Panel F for 55mm rear EDF (FC2 PRU Ch.2) — skip for Phase 5.

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
| ESC5 | 55mm rear | Fuselage | **DEFERRED — Phase 11** |

**CN1+FC1 installation — Shepherd's room (Bay A, nose) — TACCO / Wash (v2 EM-hardened):**
> Shepherd's room (Bay A) is the CAN FD / RS-485 / 1553B bus start termination node.  Use TACCO (ADM2795E
> RS-485, ISOW1044 CAN FD, ADIN1300 Ethernet) and Wash for 5 kV isolated transceivers at
> this end of the bus.  v2 placement is mandatory here (see TODO §1.2a node placement note).

- [ ] Mount CN1 TACCO on Shepherd's room (Bay A) floor standoffs (M2.5 nylon 6mm). Insert PB2-I. Secure.

- [ ] Mount FC1 Wash on inter-cape standoffs (M2.5 nylon 20mm) above CN1. Insert second PB2-I.

- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.

- [ ] Install log μSD (64GB) in CN1 Cape-B log slot. Label: **CN1-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN1 Cape-B header; connect its coax to forward 49 MHz wire post.

- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa → belly stbd SMA; Wi-Fi → dorsal fwd SMA.

- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~59mm); mount GPS patch on hull dorsal, face UP.

- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd's room (Bay A) toward Inara's shuttle (Bay B).

- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Bay B).

- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT 0x01.

- [ ] Cap Simon's medbay (Bay E) end of ETH-EA conduit (will connect to FC4 in Phase 7); connect Shepherd's room (Bay A) end to CN1 Cape-B ETH-2.

**CN2+FC2 installation — Inara's shuttle (Bay B, dorsal fwd) — TACCO / Wash (Rev R):**
> Rev R: Inara's shuttle (Bay B) also uses v2 EMI-hardened capes (same as Shepherd's room). All four bays use Wash + TACCO.

- [ ] Mount CN2 TACCO on Inara's shuttle (Bay B) floor standoffs; insert PB2-I; mount FC2 Wash above.

- [ ] Flash OS to eMMC on CN2 and FC2 before installation.

- [ ] Install log μSD (64GB) in CN2 Cape-B log slot. Label: **CN2-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN2 TACCO J_XCVR header.

- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mount GPS patch on dorsal hull, face UP.

- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle: CN2 → FC2 + temporary 120Ω at FC2 (remove Phase 7).

- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's shuttle (Bay B).

- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle): FC1 Wash ETH-1 → CN2 TACCO ETH-B (FC1↔CN2 Ethernet ring link).

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

- [ ] Install the 49 MHz (Part 15 §15.235) daemon on CN1 and CN2 (select channel per 47 CFR §15.235; not §95.623, which does not apply to this band).

**Ground tests:**

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

**CN3+FC3 installation — River's room (Bay D, dorsal aft) — TACCO / Wash (Rev R):**
> Rev R: River's room (Bay D) also uses v2 EMI-hardened capes. All four bays uniform.

- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Wash in Inara's shuttle (Bay B).

- [ ] Mount CN3 TACCO on River's room (Bay D) floor standoffs; insert PB2-I; mount FC3 Wash above.

- [ ] Flash OS to eMMC; install log μSD. Label: **CN3-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN3 TACCO J_XCVR header.

- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm); mount GPS patch, face UP.

- [ ] Continue CAN FD chain: Inara's shuttle (Bay B) FC2 → River's room (Bay D) CN3 → FC3 → exit toward Simon's medbay (Bay E).

- [ ] Continue RS-485 chain Inara's shuttle (Bay B) → River's room (Bay D) → Simon's medbay (Bay E).

- [ ] Connect ETH-BD (Inara's shuttle → River's room): FC2 Wash ETH-1 → CN3 TACCO ETH-B.

- [ ] Power tap River's room (Bay D); verify 5V ±0.05V.

**CN4+FC4 installation — Simon's medbay (Bay E, aft service) — TACCO / Wash (v2 EM-hardened):**
> Simon's medbay (Bay E) is the CAN FD / RS-485 / 1553B bus end termination node and is physically closest to the
> nacelle motor wiring and rear 55mm EDF.  Use TACCO / Wash for 5 kV isolated
> transceivers at this end of the bus.  v2 placement is mandatory here.

- [ ] Mount CN4 TACCO on Simon's medbay (Bay E) standoffs; insert PB2-I; mount FC4 Wash above.

- [ ] Flash OS to eMMC; install log μSD. Label: **CN4-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN4 header.

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
- [ ] GPS clearance check for 49MHz wire post proximity: bench-verify HDOP ≤1.5 with the 49 MHz (Part 15 §15.235) link transmitting; if GPS degrades, move GPS patch to ≥165mm from forward post.

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

- [ ] Install the STS3215 winch train: both winch pedestals, the Ø4 mm fixed axle,
    the spool (2× MR84ZZ) and its ratchet ring, the pawl + spring + catch solenoid.
    Wind 1.5 m Dyneema; attach auto-latch cradle via double-bowline. **Do NOT anchor
    the inboard end** — it is friction-retained so the line can shed at overload
    (`docs/CARGO_WINCH_SPECIFICATION.md` §3.6). Bench-calibrate the pawl spring to an
    8.0 N ± 1.0 N slip threshold before flight. (DRV8833 stays for the door/release servos.)

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

- [ ] **BVLOS communication validation** — verify handover between all 4 radio links (SiK, LoRa, Wi-Fi, 49 MHz (Part 15 §15.235)) in a degraded RF environment; mission continues on any single surviving link.

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

