# Serenity UAV — Avionics Node Firmware (Wash / Zoe, Both Nodes) Work Breakdown Structure (Detail)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Current design revision:** Rev S (2026-07-04)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `CLAUDE.md`. This file carries the full task detail for the WBS
> branches the root indexes below. Close an item here first, then check it off in
> the root index as a commit prerequisite (root `CLAUDE.md` "Revisions and Version
> Control").

*"That's a real shame, doctor, seeing how well engineered it is. — Wash"*

---

## §4.1 — §4.4 — Firmware: FC Node (Wash), CN Node (Zoe), Shared
*(root `TODO.md` §4.1-§4.4)*


- [x] Firmware directory structure (`serenity/firmware/`) *(done 2026-05-25)*

- [x] KISS/AX.25 UART driver for XCVR-49MHZ-1 — `serenity/firmware/cn/src/xcvr_kiss.c/.h` *(done 2026-05-25)*

- [x] Si5351A I²C driver — `serenity/firmware/cn/src/si5351.c/.h` *(done 2026-05-25)*

- [x] AM6254 device tree overlays — Cape-A and Cape-B DTSs *(done 2026-05-25)*

- [x] serenity-cn Phase 6 daemon (XCVR KISS driver + argparse + SIGTERM) *(done 2026-05-25)*

- [x] serenity-fc Phase 6 stub (signal handling, idle loop placeholder) *(done 2026-05-25)*

### 4.2 — FC Node (Wash) — Phase 7 Firmware

- [ ] **EDF ESC PID governor** — BDSHOT600 telemetry input on PRU-ICSS, EHRPWM output to ESCs, CAN FD cross-node synchronisation. Targets: settle <200ms, overshoot <5%; equalization |RPM_FWD − RPM_AFT| <100 RPM; fault latch on overtemp/overcurrent (no auto-recovery, GCS ack required).
    - [ ] PRU-ICSS BDSHOT600 telemetry decoder (RPM, voltage, current, temp frames).
    - [ ] EHRPWM throttle output driver with `governor_config.h` k-coefficient (§4.1, already calibrated).
    - [ ] CAN FD cross-node RPM sync message (fwd/aft pairing across River/Simon).
    - [ ] PID tuning bench test against `governor_cal.py` thrust-stand data; verify settle/overshoot/equalization targets above.
    - [ ] Overtemp/overcurrent fault-latch unit test (no auto-recovery path).

- [ ] **Nacelle tilt servo PWM generation** — EHRPWM or PRU; travel limits −5°/140° enforced in firmware; symmetric 2° tracking both nacelles.
    - [ ] EHRPWM/PRU servo output driver with firmware-enforced travel limits (−5°/140°).
    - [ ] Symmetric tracking control loop (port/stbd nacelle ≤2° divergence).
    - [ ] Bench test: command full sweep, verify limit clamping and tracking error budget.

- [ ] **IMU / barometer sensor fusion** — ICM-42688-P (SPI), BMP388/BMP390 (SPI); complementary or Kalman filter for attitude; altitude hold PID using barometric altitude + GPS.
    - [ ] ICM-42688-P SPI driver (accel/gyro read, calibration/bias removal).
    - [ ] BMP388/BMP390 SPI driver (pressure/altitude read).
    - [ ] Attitude filter (complementary or Kalman) fusing IMU + barometer.
    - [ ] Altitude-hold PID using fused barometric + GPS altitude.
    - [ ] Bench test: static and bench-rotation attitude accuracy check.

- [ ] **ToF sensor array management** — VL53L5CX ×6 per node via TCA9548A I²C mux; XSHUT sequencing via MCP23008; OA fusion (Array A + Array B cross-check); halt at 1.0m clearance.
    - [ ] TCA9548A I²C mux driver (channel select for 6× VL53L5CX per node).
    - [ ] MCP23008 XSHUT sequencing driver (sensor power-up ordering, address conflict avoidance).
    - [ ] VL53L5CX 8×8 ranging driver and per-sensor data aggregation.
    - [ ] Array A / Array B cross-check fusion logic; halt-at-1.0m / resume-at-1.5m hysteresis (matches §4.4 "OA integration").
    - [ ] Bench test: known-distance target sweep, verify halt/resume thresholds.

- [ ] **u-blox M10Q GNSS integration** — UART NMEA/UBX parse; position fix broadcast on CAN FD; HDOP gating (≤1.5 for valid position); multi-node position cross-check (≤2m disagreement threshold).
    - [ ] UART NMEA/UBX parser (position, velocity, HDOP, fix-type fields).
    - [ ] HDOP gating logic (reject fix if HDOP >1.5).
    - [ ] CAN FD position-fix broadcast frame.
    - [ ] Multi-node cross-check consumer (flag/exclude outliers >2m, feeds §4.4 "GPS cross-check").
    - [ ] Bench/field test: static fix HDOP and 4-node position agreement.

- [ ] **MIL-STD-1553B RT implementation** — PRU-ICSS Manchester II encoder/decoder; RT address assignment per node role; BC arbitration on FC1 and FC2.
    - [ ] PRU-ICSS Manchester II encode/decode driver.
    - [ ] RT address assignment table per node role (FC1–FC4).
    - [ ] BC arbitration logic for FC1 (primary) / FC2 (standby).
    - [ ] Bench test against the 1553-XFM transformer coupling hardware (§1.2 "Wire the MIL-1553 connector + transformer").

- [ ] **TPM-bound attestation** — SLB9670 TPM 2.0 HMAC on all outbound flight-critical CAN FD messages; pcrs extend on each boot; boot measurement chain.
    - [ ] SLB9670 TPM 2.0 driver (HMAC key derivation, PCR extend calls).
    - [ ] Boot measurement chain (PCR extend at each boot stage).
    - [ ] Outbound CAN FD HMAC signing hook for flight-critical message classes.
    - [ ] Bench test: tamper/replay rejection unit test against signed vs. unsigned frames.

- [x] **governor_cal.py** — thrust stand calibration script: sweeps 0%→100%→0% throttle, fits k coefficient (T = k × RPM²), outputs `EDF_THRUST_K` for `governor_config.h`. *(done 2026-06-04)*

- [x] **governor_config.h** — template with calibrated k values per EDF; compile-time constants. *(done 2026-06-04)*

### 4.3 — CN Node (Zoë) — Phase 7 Firmware

- [ ] **CAN FD heartbeat and telemetry forwarding** — broadcast 0x001–0x008 node health frames; relay MAVLink telemetry from elected FC master to SiK GCS link.
    - [ ] 0x001–0x008 node health frame broadcaster (per-node heartbeat content/period).
    - [ ] MAVLink telemetry relay path: FC master CAN FD → CN master → SiK GCS link.
    - [ ] Bench test: heartbeat timeout detection feeding §4.4 "Node role election protocol."

- [ ] **MIL-STD-1553B BC/RT tasks** — BC on CN1 (standby), RT on CN2–CN4; mirror FC bus controller arbitration.
    - [ ] BC standby logic on CN1 (mirrors FC1/FC2 arbitration, §4.2).
    - [ ] RT implementation on CN2–CN4 (shares PRU-ICSS Manchester II driver with §4.2).
    - [ ] Bench test against 1553-XFM transformer coupling hardware (§1.2).

- [ ] **RS-485 inter-board messaging** — structured message format (header/payload/CRC); inter-node command and status relay.
    - [ ] Define structured frame format (header/payload/CRC) shared across all 8 nodes.
    - [ ] Driver for the RS485_A/B footprint pinout already fixed on Wash/Zoë (§1.2).
    - [ ] Bench test: CRC-reject malformed frame, command/status round-trip between two nodes.

- [ ] **Ethernet RSTP ring management** — CPSW3G bridge configuration; RSTP fast-failover (<1s) verification; ring segment health monitoring.
    - [ ] CPSW3G bridge configuration for the 8-node ring topology (§1.4.3).
    - [ ] RSTP fast-failover implementation and timer tuning.
    - [ ] Ring segment health monitoring/reporting hook (feeds CAN FD heartbeat above).
    - [ ] Bench test: physically break one ring segment, verify <1s failover.

- [ ] **Signed-log write via CPLD write-blocker** — log records written as read-only-append through ATF16V8BQL latch interface; NOR flash (W25Q128JV) circular buffer for overflow.
    - [ ] ATF16V8BQL CPLD write-blocker interface driver (enforces append-only).
    - [ ] microSD log writer (primary store) per node's write-blocked card.
    - [ ] W25Q128JV NOR flash circular buffer driver for overflow when microSD is full/unavailable.
    - [ ] Bench test: attempt out-of-order/overwrite write, verify CPLD blocks it.

- [ ] **TPM-bound HMAC on all outbound AX.25 payloads** — each 49 MHz (Part 15 §15.235) packet includes HMAC-SHA256 computed from SLB9670 stored key; receiver nodes verify before acting.
    - [ ] SLB9670 stored-key HMAC-SHA256 signer for outbound AX.25/49 MHz frames (Emma boards, River/Simon).
    - [ ] Receiver-side verification gate (discard unsigned/invalid before acting, mirrors §4.4 "Security message signing").
    - [ ] Bench test: signed/unsigned/corrupted-signature frame acceptance matrix.

- [ ] **Cargo control** — DRV8833 winch H-bridge, HX711 load cell (payload weight sensing), SG90 door and release servos; state machine: IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED.
    - [ ] DRV8833 H-bridge winch driver.
    - [ ] HX711 load-cell driver (payload weight sensing, overload cutoff).
    - [ ] SG90 door + release servo driver.
    - [ ] State machine implementation: IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED, with fault states.
    - [ ] Bench test: full cycle with simulated payload load, verify HX711 cutoff and state transitions.

- [ ] **MAVLink routing configuration** — mavlink-router config: elected CN master routes FC master telemetry to all 4 radio links (SiK, LoRa, Wi-Fi, 49 MHz (Part 15 §15.235) backup).
    - [ ] mavlink-router config file per CN role (master vs. standby).
    - [ ] Per-link output adapter: SiK, LoRa (Emma), Wi-Fi, 49 MHz (Part 15 §15.235) (Emma, backup).
    - [ ] Bench test: verify telemetry reaches Malcolm GCS over each of the 4 links independently.

### 4.4 — Both Nodes

- [ ] **Node role election protocol** — CAN FD priority arbitration at boot; lowest node-ID wins master role; automatic failover on heartbeat timeout (100ms); FC master and CN master elected independently.
    - [ ] Boot-time CAN FD priority arbitration (lowest node-ID wins, per PACE table in CLAUDE.md).
    - [ ] Independent FC-master / CN-master election state machines.
    - [ ] Failover trigger on 100ms heartbeat timeout (consumes §4.3 heartbeat broadcast).
    - [ ] Bench test: kill the current master, verify failover to next PACE tier within timeout.

- [ ] **Autonomous navigation** — 3-waypoint GPS mission execution; altitude hold ±0.3m; waypoint radius 2m; RTL on any link loss >5s.
    - [ ] Waypoint mission sequencer (3-waypoint minimum viable mission).
    - [ ] Altitude-hold integration with §4.2 barometric/GPS altitude PID.
    - [ ] Waypoint-radius capture logic (2m) and RTL trigger on link loss >5s.
    - [ ] Field test: full 3-waypoint mission with deliberate link-loss RTL trigger.

- [ ] **OA integration** — ToF halt trigger feeds into navigation; velocity command zeroed within 1.0m of obstacle; resumes when clear.
    - [ ] Navigation-layer consumer for §4.2 ToF array halt/resume signal.
    - [ ] Velocity command zeroing at 1.0m clearance; resume logic at 1.5m clearance.
    - [ ] Bench/field test: approach a target obstacle, verify halt/resume hysteresis in flight.

- [ ] **GPS cross-check** — 4 GPS receivers (one per FC node); positions averaged; outlier >2m flagged and excluded from blend.
    - [ ] Multi-node position collection (4× u-blox M10Q via §4.2 CAN FD broadcast).
    - [ ] Averaging/blend algorithm with outlier exclusion (>2m disagreement).
    - [ ] Bench test: inject a synthetic outlier fix, verify exclusion from blend.

- [ ] **Security message signing** — every inter-node CAN FD message signed; unauthenticated messages discarded; signing key material bound to node TPM endorsement key.
    - [ ] CAN FD message signing hook bound to each node's TPM endorsement key (SLB9670, §4.2).
    - [ ] Receiver-side verification gate; discard unauthenticated frames before acting.
    - [ ] Bench test: inject unsigned/forged frame on the bus, verify it is discarded and logged.

