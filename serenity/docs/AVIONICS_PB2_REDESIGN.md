# Serenity Avionics Redesign — 8× PocketBeagle 2 Industrial

**Status:** Implemented — Rev M hardware baseline (supersedes AM6232 PB2 design from Rev K)  
**Date:** 2026-05-17 (updated for Rev M PB2-I upgrade from 2026-05-11 original)  
**Scope:** Avionics compute, cape specifications, bus topology, radio link architecture

> **Rev M board change:** All 8 PocketBeagle 2 (AM6232) replaced with PocketBeagle 2 Industrial (AM6254). Cape-A and Cape-B PCB designs unchanged. DigiKey P/N: 2820-100003007-ND · $51.03 ea.

---

## 1. Architecture overview

Eight PocketBeagle 2 Industrial boards split into two cooperative groups of four. Each board runs the same base Linux image (from 64GB eMMC — no OS microSD required). Real-time tasks are offloaded to the AM6254's PRU-ICSS cores, exactly as RP2350 PIO handled them in RevJ.

| Group | Count | Cape | Primary responsibility |
|---|---|---|---|
| FC1–FC4 | 4 | Cape-A (Sensor/Flight) | Flight control, navigation, obstacle avoidance, actuator drive |
| CN1–CN4 | 4 | Cape-B (Comms/Payload) | Radio links, system logging, payload & cargo management |

All 8 nodes participate equally on all 4 wired data buses. Every node is a potential failover candidate for any role. Role assignment is negotiated via heartbeat priority voting over CAN FD; no node has a hardwired role at power-on.

```
┌─────────────────────────────────────────────────────────┐
│                  WIRED BUS BACKBONE                     │
│  ─── MIL-STD-1553 (shielded 78Ω twisted pair) ─────── │
│  ─── CAN FD (ISO 11898-1, 5 Mbps data rate) ────────  │
│  ─── RS-485 (half-duplex, 4 Mbps max) ──────────────  │
│  ─── Ethernet (ring, CPSW3G, 100BASE-TX per link) ──  │
└────┬──────┬──────┬──────┬──────┬──────┬──────┬─────┘
    CN1   FC1   CN2   FC2   CN3   FC3   CN4   FC4
   [B]   [A]   [B]   [A]  [B]   [A]   [B]   [A]
```

Bus order: **CN1 → FC1 → CN2 → FC2 → CN3 → FC3 → CN4 → FC4** — one CN + one FC per bay (A/B/D/E). Any single segment cut or bay power failure leaves ≥2 FC + ≥2 CN accessible on both sides of the break.

---

## 2. PocketBeagle 2 Industrial base platform

| Item | Spec |
|---|---|
| Board | PocketBeagle 2 Industrial · MFR P/N 100003007 · DigiKey 2820-100003007-ND · $51.03 ea |
| SoC | TI AM6254 (Sitara) |
| App cores | 4× Cortex-A53 @ up to 1.4 GHz |
| RT co-processor | 1× Cortex-M4F (bare-metal or FreeRTOS) — runs PID governor at 500 Hz |
| PRU-ICSS | 2× PRU @ 250 MHz + 1× RTU (deterministic, direct GPIO) — runs DSHOT1200 |
| RAM | 1 GB DDR4 |
| Storage | 64 GB eMMC (OS + storage, pre-populated) — no OS microSD required |
| Log storage | Cape-B microSD slot (write-blocked by ATF16V8BQL CPLD — flight log only) |
| Onboard MCU | MSPM0L1105 + 12-bit ADC (future expansion) |
| LiPo charger | Onboard (future use) |
| CAN | 2× MCAN (ISO 11898-1:2015, CAN FD capable) |
| Ethernet | CPSW3G — 1 internal port + 2 external RGMII/RMII MAC ports |
| USB | USB-C power + 3.3V JST-SH UART debug |
| Expansion | 72-pin expansion headers exposing SPI, I²C, UART, PWM, PRU I/O, MCAN, GPIO |
| Power in | 5V via USB-C or expansion header VIN |
| Temperature | −40°C to 85°C industrial |
| Mass | 12.7 g |

### PRU as RP2350 replacement

The RP2350 PIO state machines in RevJ handled servo PWM generation, Manchester II encoding for 1553, ESC telemetry capture, and bit-banged protocols. The AM6254 PRU provides equivalent determinism:

| Task | RevJ | PB2-I redesign |
|---|---|---|
| Servo/ESC PWM | RP2350 PIO | AM6254 EHRPWM (6 ch) + PRU (additional channels) |
| 1553 Manchester II | HI-6130 SPI chip | PRU firmware (250 MHz → 250 cycles/µs bit cell) |
| ESC telemetry capture | RP2350 PIO | AM6254 eCAP + UART |
| CAN FD | MCP2518FD SPI | AM6254 MCAN (native, no external controller) |
| Ethernet | W5500 SPI (100 Mbps nominal) | AM6254 CPSW3G (Gigabit, hardware switch) |

---

## 3. Cape-A — Sensor & Flight Control

**Footprint:** ~85 × 55 mm, 4-layer PCB, mounts on P1/P2 via female 0.1″ headers  
**Population:** All 4 Cape-A boards identical; sensor population optional per FC role

### 3.1 Cape-A IC inventory

| Ref | Part | Interface | Function |
|---|---|---|---|
| U1 | ICM-42688-P | SPI (CS via GPIO) | 6-DOF IMU — ±16 g / ±2000 °/s |
| U2 | BMP388 | I²C | Barometric altimeter |
| U3 | u-blox M10Q | UART | GNSS — GPS/GLONASS/Galileo/BeiDou L1 |
| U4 | MS4525DO header | I²C JST-ZH 4-pin | Differential airspeed (populate FC1 only; header present on all) |
| U5 | ATA6561 | MCAN → JST-GH | CAN FD transceiver — 3.3 V compatible, 5 Mbps |
| U6 | MAX3485E | UART → JST-GH | RS-485 half-duplex transceiver + direction GPIO |
| U7 | DS26LV31 + DS26LV32 | PRU GPIO | MIL-STD-1553 differential driver + receiver |
| T1 | PE-68515 (or equiv) | — | 1553 coupling transformer, 1:1.41, 78 Ω |
| U8 | DP83825I × 2 | CPSW3G RMII | 10/100 Ethernet PHY, ring port A and port B |
| U9 | SLB9670 | SPI | TPM 2.0 — attestation, key storage |
| U10 | AP2112K-3.3 | — | 3.3 V LDO, 600 mA, ultra-low noise |
| U11 | TPS62933 (or equiv) | — | 3.3 V → 1.8 V SMPS for PHY AVDD if required |

> **Note:** If CPSW3G RGMII/RMII is not routed to P1/P2 on production PocketBeagle 2 boards, replace U8 (×2 DP83825I) with 2× W5500 SPI Ethernet controllers. The bus topology is unchanged; only the bandwidth drops from 100 Mbps to ~8 Mbps effective.

### 3.2 Cape-A flight control I/O

| Function | Count | Interface | Connector |
|---|---|---|---|
| Servo/ESC PWM outputs | 8 channels | EHRPWM (6 ch) + PRU (2 ch) | 2× 3-pin servo rail headers |
| ESC UART telemetry input | 1 | UART (BLHeli32 / Hobbywing) | JST-GH 4-pin |
| External I²C (ToF, peripherals) | 1 | I²C + 3.3 V | JST-GH 4-pin |
| Debug UART console | 1 | UART | JST-GH 4-pin |

### 3.3 Cape-A bus connectors (all JST-GH)

| Label | Pins | Bus |
|---|---|---|
| CAN-A | 4 | CAN FD CANH/CANL + 5 V + GND |
| RS485-A | 4 | RS-485 A/B + 5 V + GND |
| 1553-A | 4 | 1553 HILEG/LOLEG + shield + GND |
| ETH-P | 6 | Ethernet ring port A (to previous node) |
| ETH-N | 6 | Ethernet ring port B (to next node) |

### 3.4 Cape-A antenna / RF connectors

| Label | Connector | Signal |
|---|---|---|
| GPS-ANT | U.FL → SMA bulkhead | GPS L1 1575 MHz patch antenna |
| EXT-1 | U.FL | Spare (airspeed pitot has no antenna; reserved) |

### 3.5 Cape-A power budget

| Rail | Consumers | Max current |
|---|---|---|
| 5 V in | PB2 VIN, CAN/RS-485 transceivers | 2.0 A |
| 3.3 V (LDO) | ICM-42688-P, BMP388, M10Q, DP83825I × 2, SLB9670, MAX3485E | 600 mA |

---

## 4. Cape-B — Comms, Logging & Payload

**Footprint:** ~90 × 60 mm, 4-layer PCB, mounts on P1/P2  
**Population:** All 4 Cape-B boards identical — all 4 radio interfaces populated on every board

### 4.1 Radio link assignment

Each Cape-B board carries all 4 radio types. Software assigns one CN node as primary master per link; the other three boards' radios are hot standbys. If the primary comms node fails mid-flight, the surviving nodes elect a new primary via CAN FD heartbeat voting within one heartbeat period.

| Radio link | Module | Interface | Frequency | Role |
|---|---|---|---|---|
| MAVLink telemetry | SiK v3 module (RFD900x footprint) | UART + GPIO | 902–928 MHz | Bidirectional telemetry / command uplink |
| Long-range backup | RFM95W LoRa | SPI + DIO IRQ | 902–928 MHz (separate channel plan) | Backup command / low-rate telemetry |
| RC control | RCRS-49 sub-module | UART + timing GPIO | 49 MHz TDDS | Pilot RC input, dynamic channel assignment |
| Local mesh / GCS | TI WL1837MOD | SDIO | 2.4 + 5 GHz WiFi (802.11 a/b/g/n) + BT 5.0 | Ground station AP, short-range streaming; BT for tablet GCS |

> **SiK + LoRa coexistence:** Both operate in the 902–928 MHz US ISM band. Coordinate channel plans at firmware level — SiK on 915 MHz center, LoRa on 903 MHz or 927 MHz. Physical separation of SMA ports ≥50 mm, separate ground pours under each RF section.

> **RCRS-49 sub-module:** The RCRS-49 is a custom 49 MHz TDDS PCB (separate from this cape). Cape-B provides a 6-pin JST-GH header (5 V, GND, UART TX, UART RX, TDDS-SYNC GPIO, n/c) and an SMA bulkhead for the 49 MHz loaded whip. The sub-module plugs in; the RF section remains on the RCRS-49 board.

### 4.2 Cape-B IC inventory

| Ref | Part | Interface | Function |
|---|---|---|---|
| U1 | ATA6561 | MCAN → JST-GH | CAN FD transceiver (same as Cape-A) |
| U2 | MAX3485E | UART → JST-GH | RS-485 transceiver (same as Cape-A) |
| U3 | DS26LV31 + DS26LV32 | PRU GPIO | MIL-STD-1553 (same as Cape-A) |
| T1 | PE-68515 | — | 1553 coupling transformer (same as Cape-A) |
| U4 | DP83825I × 2 | CPSW3G RMII | Ethernet PHY ring ports (same as Cape-A) |
| U5 | RFD900x (or SiK v3 mod.) | UART, CTS/RTS | SiK 915 MHz MAVLink radio |
| U6 | RFM95W | SPI, DIO0–DIO3 | LoRa 915 MHz long-range backup |
| U7 | TI WL1837MOD | SDIO (4-bit) | WiFi 802.11 a/b/g/n (2.4 + 5 GHz) + BT 5.0 — uses TI wl18xx mainline kernel driver |
| — | RCRS-49 sub-module | JST-GH 6-pin header | 49 MHz TDDS RC control |
| U8 | W25Q128JV | SPI | 128 Mbit NOR flash — circular flight log buffer (non-executable) |
| U9 | microSD socket | SPI | Removable log card — hardware write-block enforced by U10 |
| U10 | ATF16V8BQL CPLD | GPIO latch → SD-WP pin | Write-block latch: SET at power-on by boot sequence, CLEAR only on hard power cycle; implements non-executable append-only log semantics identical to RevJ CPLD write-blocker |
| U11 | SLB9670 | SPI | TPM 2.0 — per-node attestation, radio key storage, boot measurement |
| U12 | DRV8833 | GPIO (H-bridge) | Cargo winch N20 300:1 motor driver, 1.5 A |
| U13 | HX711 | GPIO bit-bang (DOUT/SCK) | 24-bit load cell ADC — payload weight |
| U14 | TPS63031 (or equiv) | — | 3.3 V/1.5 A SMPS (radio TX peaks up to 800 mA combined) |
| U15 | AP2112K-3.3 | — | Auxiliary 3.3 V LDO for logic (separated from RF supply) |
| U16 | Ferrite + bulk cap array | — | Per-radio RF supply decoupling (100 µF + 100 nF per radio VCC) |

### 4.3 Cape-B payload / cargo I/O

| Function | Count | Interface | Connector |
|---|---|---|---|
| Cargo door servos | 2 ch | EHRPWM (PRU) | 2× 3-pin servo header |
| Winch motor (DRV8833) | 1 | H-bridge GPIO | JST-GH 4-pin (motor + power) |
| Load cell (HX711) | 1 | GPIO bit-bang | JST-GH 4-pin |
| Auto-latch GPIO | 2 | GPIO | JST-GH 4-pin |
| Debug UART | 1 | UART | JST-GH 4-pin |

### 4.4 Cape-B bus connectors (all JST-GH — identical to Cape-A)

| Label | Pins | Bus |
|---|---|---|
| CAN-A | 4 | CAN FD |
| RS485-A | 4 | RS-485 |
| 1553-A | 4 | MIL-STD-1553 |
| ETH-P | 6 | Ethernet ring port A |
| ETH-N | 6 | Ethernet ring port B |

### 4.5 Cape-B antenna connectors (SMA, all panel-mount)

| Label | Frequency | Antenna |
|---|---|---|
| SMA-915-SIK | 902–928 MHz | SiK λ/4 monopole whip (82 mm) |
| SMA-915-LORA | 902–928 MHz | LoRa λ/4 monopole or SMA whip |
| SMA-49 | 49 MHz | RCRS-49 loaded whip (via sub-module) |
| SMA-WIFI | 2.4 / 5 GHz | WL1837MOD PCB antenna or U.FL → SMA pigtail |

### 4.6 Cape-B power budget

| Rail | Consumers | Max current |
|---|---|---|
| 5 V in | PB2 VIN, DRV8833 motor, radio modules | 3.0 A |
| 3.3 V RF (SMPS) | RFD900x (1.2 A TX peak), RFM95W (120 mA TX), WL1837MOD (550 mA TX peak) | 1.5 A continuous, 2.0 A peak |
| 3.3 V logic (LDO) | MAX3485E, ATA6561, DS26LV31/32, DP83825I × 2, HX711, SLB9670, ATF16V8BQL | 350 mA |

---

## 5. Wired bus topologies

### 5.1 Ethernet — 8-node ring

Each PocketBeagle 2 CPSW3G provides two external MAC ports. Cape-A and Cape-B each add two DP83825I PHYs, giving each node two 100BASE-TX links. Nodes are wired in a ring:

```
CN1 ─ETH─ FC1 ─ETH─ CN2 ─ETH─ FC2
 │    Bay A    ETH-AB    Bay B   │
ETH                             ETH
(ETH-EA)                     (ETH-BD)
 │                               │
FC4 ─ETH─ CN4 ─ETH─ FC3 ─ETH─ CN3
     Bay E    ETH-DE    Bay D
```

CPSW3G operates in hardware-bridge (switch) mode per node, forwarding frames between its two external ports transparently. RSTP (Rapid Spanning Tree) prevents loops and provides sub-second ring healing on single-link failure. Any node can reach any other node via two independent paths.

**If RMII not available on P1/P2:** Replace DP83825I with W5500 (SPI) on both capes. Ring topology unchanged; effective bandwidth per link drops to ~8 Mbps but is adequate for MAVLink + sensor state distribution.

### 5.2 MIL-STD-1553 — single bus, 8 RT + 2 BC-capable nodes

All 8 nodes connect to one 1553 bus via their PRU-based Manchester II encoder/decoder:

```
CN1 ─T─ FC1 ─T─ CN2 ─T─ FC2 ─T─ CN3 ─T─ FC3 ─T─ CN4 ─T─ FC4
[RT]  [BC/RT] [RT]  [stbyBC] [RT]  [RT]  [RT]  [RT]
╰─ 78Ω term                                          ╰─ 78Ω term
   (CN1, Bay A)                                         (FC4, Bay E)
```

- **T** = stub coupling transformer (PE-68515 or equivalent, 0.9 m max stub)  
- **Primary BC:** FC1 (elected at boot via CAN FD priority arbitration)  
- **Standby BC:** FC2 (assumes BC role if FC1 heartbeat absent for 3 frames)  
- **Termination:** 78Ω at CN1 (bus start, Bay A) and FC4 (bus end, Bay E)  
- **Shielded cable:** MIL-C-17/131 or equivalent, 78 Ω, twisted pair, drain wire grounded at one end per segment  
- **PRU firmware requirement:** Manchester II encoder at 1 Mbps ± 0.5%; decoder with sync-word detection and RT address filtering; TX/RX half-duplex arbitration

### 5.3 CAN FD — linear bus, 8 nodes

```
CN1 ─┬─ FC1 ─ CN2 ─ FC2 ─ CN3 ─ FC3 ─ CN4 ─┬─ FC4
   120Ω                                     120Ω
  (start,                                  (end,
  Bay A)                                  Bay E)
```

- **Transceiver:** ATA6561 on every cape, 3.3 V, 5 Mbps data rate  
- **Termination:** 120 Ω resistor soldered on CN1 cape (bus start, Bay A) and FC4 cape (bus end, Bay E); all others: open  
- **Controllers:** AM6254 MCAN0 (primary bus) + MCAN1 (reserved for second CAN bus or redundant arbitration)  
- **Protocol:** DroneCAN v1 / UAVCANv1 for sensor data; custom priority-voting messages for role election

### 5.4 RS-485 — half-duplex bus, 8 nodes

```
CN1 ─┬─ FC1 ─ CN2 ─ FC2 ─ CN3 ─ FC3 ─ CN4 ─┬─ FC4
   120Ω                                     120Ω
  (CN1,                                    (FC4,
  Bay A)                                  Bay E)
```

- **Transceiver:** MAX3485E, direction control via GPIO (DE/RE)  
- **Rate:** 4 Mbps maximum; typically operated at 115200 baud for configuration, 1 Mbps for sensor streaming  
- **Use:** Secondary sensor bus, ESC configuration, low-priority inter-node messaging, bootloader access

---

## 6. Radio link distribution and failover

All 4 radio links are physically present on every Cape-B board. At any given time, one CN node is elected primary master for each link:

| Radio link | Default primary | Failover order |
|---|---|---|
| SiK 915 MHz MAVLink | CN1 | CN2 → CN3 → CN4 |
| LoRa 915 MHz backup | CN2 | CN3 → CN4 → CN1 |
| RCRS 49 MHz RC | CN3 | CN4 → CN1 → CN2 |
| WiFi 2.4 GHz / BLE | CN4 | CN1 → CN2 → CN3 |

Failover trigger: CAN FD heartbeat loss from primary CN node for ≥200 ms. The next-priority node activates its radio master TX and announces takeover via CAN FD. No pilot input is interrupted; the RC link failover handoff is transparent because all CN nodes are receiving RCRS-49 TDDS frames simultaneously (receive-all mode), and only the TX/processing primary changes.

GPS receivers (u-blox M10Q) are on all 4 Cape-A nodes. GNSS data is broadcast over CAN FD (DroneCAN GPS message). FC1 uses its local M10Q as primary; if FC1 fails, FC2's M10Q becomes the active GPS source via CAN FD arbitration.

---

## 7. Node role architecture

### Flight Control (Cape-A) nodes

| Node | Default role | Failover capability |
|---|---|---|
| FC1 | Primary flight controller; 1553 Bus Controller; CAN FD Bus Controller; primary GNSS | Any FC role |
| FC2 | Navigation / waypoint execution / OA primary; 1553 standby BC | Primary FC if FC1 down |
| FC3 | Obstacle avoidance backup; payload bay sensors; ESC telemetry aggregation | Nav primary if FC2 down |
| FC4 | Actuator redundancy (nacelle tilt, variable nozzle, nav lights) | Any FC role |

### Comms/Payload (Cape-B) nodes

| Node | Default radio master | Default payload role | Failover |
|---|---|---|---|
| CN1 | SiK 915 MHz | Primary system log writer | Any CN role |
| CN2 | LoRa 915 MHz | Secondary log (redundant writes) | SiK master if CN1 down |
| CN3 | RCRS 49 MHz | Cargo management primary (winch, doors, latch) | LoRa master if CN2 down |
| CN4 | WiFi / BLE | Cargo management backup | RC master if CN3 down |

---

## 8. Mass and power comparison

### Mass

| Architecture | Compute boards | Capes / hats | Total avionics mass (est.) |
|---|---|---|---|
| RevJ (CM4 + CM3+ mixed) | CM4-LITE ×2 (15g) + CM4-CARRIER-2 ×2 (35g) + CM3+ ×2 (16g) + CM3-CARRIER-1 ×2 (18g) + COMMS-HAT-SWITCH (29g) + MICROHAT (10g) + SENSORHAT-1 ×2 (25g) | — | **148 g** |
| PB2 redesign | PocketBeagle 2 ×8 (~80 g) | Cape-A ×4 (~50 g est.) + Cape-B ×4 (~65 g est.) | **~195 g** (+47 g) |

The mass increase is real. Mitigation: Cape-A and Cape-B share 90% of the bus-interface components; a combined 4-layer board with a PB2 SODIMM-style socket (instead of P1/P2 stacking) could reduce individual board mass significantly. JLCPCB assembly for a shared-BOM 90×60mm 4-layer PCB is ~$8/board at quantity 10.

### Power

| Architecture | Idle draw (all nodes) | Peak draw |
|---|---|---|
| RevJ RP2350 co-processors | ~1.3 W | ~2 W |
| RevJ CM4/CM3+ main compute | ~8 W | ~14 W |
| RevJ total avionics | ~9.3 W | ~16 W |
| PB2 redesign (×8 boards) | ~10 W (1.25 W/board) | ~26 W (radio TX peaks ×4 CN nodes) |

The Cape-B radio TX peak (SiK 1.2 A + LoRa 120 mA + ESP32 350 mA ≈ 8.3 W per CN node, worst-case all TX simultaneously) dominates. In practice, radios are not all transmitting simultaneously; typical flight average is ~3 W per CN node = 12 W across 4 CN nodes. Total system avionics average: FC group (~5 W) + CN group (~12 W) = **~17 W average**, vs. RevJ ~9.3 W. At 6S 4000 mAh = 88.8 Wh, the extra 7.7 W costs ~5 minutes of flight endurance. Manageable but not free.

---

## 9. PRU firmware requirements

Both cape variants require the same two PRU firmware images:

### PRU-0: MIL-STD-1553 Manchester II transceiver

- TX path: accept frame data via shared memory → encode Manchester II → strobe DS26LV31 driver
- RX path: sample DS26LV32 receiver → decode Manchester II → write frame to shared memory → raise RPMsg interrupt to A53
- BC mode (FC1/FC2 only, elected dynamically): issue command words, manage response timeouts, retransmit on error
- RT mode (all others): respond to addressed command words, return status words
- Timing budget: 1 µs bit cell; PRU at 250 MHz = 250 cycles/bit. Sync detection requires ±2% tolerance = ±5 cycles. Achievable with deterministic PRU loop.

### PRU-1: Servo/ESC PWM generation (Cape-A only)

- 8-channel 50 Hz PWM (servo) or 400 Hz (ESC digital)
- Resolution: 1 µs pulse width step = 250 PRU cycles (1000 steps across 1–2 ms range)
- Synchronised multi-channel update from shared memory command buffer
- EHRPWM handles 6 channels natively; PRU-1 handles 2 overflow channels

Cape-B PRU-1 is used for cargo servo PWM (2 channels only) + TDDS sync timing for RCRS-49.

---

## 10. Security model (unchanged from RevJ)

The CPLD write-blocker and STM32 OTP fuse architecture from RevJ applies unchanged. Each node boots from its 64GB eMMC (Rev M — no OS microSD). Log storage (Cape-B microSD + NOR flash) uses hardware write-protect via the CPLD latch — the latch is set at power-on and cannot be cleared until the node is powered off, enforcing non-executable, append-only log semantics.

TPM 2.0 (SLB9670) is present on **both Cape-A and Cape-B** — all 8 nodes carry a TPM. FC nodes use it for flight-critical attestation and key storage. CN nodes use it for radio link key storage, boot measurement, and flight-log authenticity attestation (the CPLD write-blocker enforces append-only access; the TPM binds log signing keys).

---

## 11. Open items and verification required

| Item | Risk | Action |
|---|---|---|
| CPSW3G RMII/RGMII availability on PocketBeagle 2 P1/P2 | Medium | Verify against BeagleBoard PB2 hardware reference manual before Cape-A layout. Fallback: W5500 SPI. |
| PRU I/O pin availability on P1/P2 | Medium | Confirm PRU_PRU0_GPIO pins are routed to P1/P2 expansion headers on PB2. |
| RCRS-49 sub-module connector footprint | Low | Define JST-GH 6-pin header pinout with RCRS-49 firmware team before Cape-B layout. |
| SiK + LoRa 915 MHz coexistence channel plan | Medium | Validate with spectrum analyzer — both in 902–928 MHz ISM band, minimum 2 MHz separation required between channels. |
| PB2 boot time in failover scenario | High | Benchmark: measure time from 5 V applied to CAN FD heartbeat present. Target <15 s. If >15 s, implement kexec warm-restart and/or pre-arm node-ready gating. |
| Cape power connector to vehicle bus | Low | Specify: Molex Nano-Fit 4-pin (5 V, 5 V, GND, GND) per node, rated 6 A. 4 FC + 4 CN = 8 connectors to PDB. |
| DRV8833 current sense for winch stall detection | Low | Add 0.1 Ω sense resistor on DRV8833 AOUT1 path; read via AM6254 ADC for stall current detection. |
| VL53L5CX obstacle avoidance array interface | Medium | The 12× ToF sensor arrays (TCA9548A + MCP23008 per array) connect to FC1 (Bay A, Array B host) and FC3 (Bay D, Array A host) via the external I²C header on Cape-A. Verify I²C pull-up voltage compatibility (VL53L5CX uses 1.8 V I²C — level shifter required between Cape-A 3.3 V and sensor 1.8 V). |

---

## 12. Cape PCB shared BOM section

The bus-interface section is identical on both capes (~60% of components). Consider a common daughterboard approach:

```
PocketBeagle 2
    ↕ P1/P2
[Bus Backbone Module]  ← shared PCB: ATA6561, MAX3485E, DS26LV31/32, T1, DP83825I×2, power
    ↕ board-to-board connector
[Cape-A function layer]   OR   [Cape-B function layer]
```

This reduces cape NRE: one shared 4-layer bus board, two smaller function boards. Total stack height increases ~3 mm but total PCB cost decreases.

---

*End of document. Supersedes RevJ CM4/CM3+ node architecture for avionics compute.*
