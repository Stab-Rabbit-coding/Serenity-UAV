# Serenity UAV — Power Distribution & Battery Management

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev Q
**Date:** 2026-06-07

---

## 1. Architecture Overview

```
                         ┌───────────────────────────────────────────┐
  6S 4000 mAh LiPo       │                 Kaylee                     │
  (22.2 V nominal)        │                                           │
  XT60 ──────────────────►│ J_BATT (XT60)                            │
                          │   │                                       │
  JST-XH-7P balance ─────►│ J_BAL  ──► BQ76930 cell monitor          │
                          │   │                                       │
                          │  F1 (150 A MAXI fuse)                     │
                          │   │                                       │
                          │  TVS + 2×220 µF bulk                      │
                          │   │                                       │
                          │  ├──── F_ESC1 (40 A) ── XT30 ── ESC1     │
                          │  ├──── F_ESC2 (40 A) ── XT30 ── ESC2     │
                          │  ├──── F_ESC3 (40 A) ── XT30 ── ESC3     │
                          │  ├──── F_ESC4 (40 A) ── XT30 ── ESC4     │
                          │  │        (ESC5 – Phase 11, DNP)         │
                          │  ├──── 5 V / 10 A BEC ── avionics bus    │
                          │  └──── 6 V /  5 A BEC ── servo bus       │
                          │                                           │
                          │  INA226 monitors (I2C → Cape-A / Shepherd's room / Bay A)  │
                          │   MAIN (0x44), ESC1 (0x40)–ESC4 (0x43)  │
                          └───────────────────────────────────────────┘
```

Each ESC feeds one 50 mm EDF (Phases 5–10). Phase 11 adds ESC5 for the 120 mm fuselage EDF.

---

## 2. Battery Selection

| Parameter | Hover / Endurance | Cargo Delivery |
|-----------|------------------|----------------|
| Pack | Tattu / Gens Ace 6S 4000 mAh 60C LiPo | Tattu 6S 2800 mAh LiPo |
| Nominal voltage | 22.2 V (3.70 V/cell × 6) | 22.2 V |
| Fully charged | 25.2 V (4.20 V/cell × 6) | 25.2 V |
| Storage voltage | 23.1 V (3.85 V/cell × 6) | 23.1 V |
| Cut-off voltage | 18.0 V (3.00 V/cell × 6) | 18.0 V |
| Max cont. discharge | 60 C × 4.0 Ah = **240 A** | 60 C × 2.8 Ah = 168 A |
| Est. pack IR | ~30 mΩ (5 mΩ/cell × 6) | ~40 mΩ |
| Mass | 750 g | 525 g |
| AUW contribution | Full hardware build: ~3 608 g | Cargo delivery: ~3 383 g |
| Connector | XT60 | XT60 |
| Balance | JST-XH-7P (7-pin, 2.54 mm) | JST-XH-7P |

### 2.1 Voltage Under Load

At sustained 115 A draw (four 50 mm EDFs at full thrust) with 30 mΩ pack IR:

```
V_sag = 115 A × 0.030 Ω = 3.45 V
V_pack_min_load = 22.2 V − 3.45 V ≈ 18.75 V  (nominal state-of-charge)
```

This is above the 18.0 V hardware cut-off. At storage voltage (23.1 V), minimum under-load
voltage is ~19.65 V — all ESCs and BECs maintain regulation throughout.

---

## 3. Load Analysis

### 3.1 Propulsion Loads (direct VBAT, 18–25.2 V)

| Load | Qty | Nom. draw (A ea.) | Peak draw (A ea.) | Total nom. (A) | Total peak (A) |
|------|-----|-------------------|-------------------|----------------|----------------|
| ESC1 – Port Fwd 50 mm EDF | 1 | 18 | 40 | 18 | 40 |
| ESC2 – Port Aft  50 mm EDF | 1 | 18 | 40 | 18 | 40 |
| ESC3 – Stbd Fwd 50 mm EDF | 1 | 18 | 40 | 18 | 40 |
| ESC4 – Stbd Aft  50 mm EDF | 1 | 18 | 40 | 18 | 40 |
| **ESC5 – Fuse 120 mm EDF (Ph. 11)** | 1 | 50 | 80 | DNP | DNP |
| **Propulsion subtotal (Ph. 5–10)** | — | — | — | **72** | **160** |

XFly Galaxy X5 50 mm 12-blade 6S 3200 KV at 1 240 g max thrust ≈ 400 W per EDF →
I = 400 W / 22.2 V ≈ 18 A nominal. 40 A is the ESC continuous rating (software
over-current threshold in governor_config.h: `EDF_ESC_OVERCURRENT_A = 80 A`).

### 3.2 Avionics Loads (5 V rail)

| Load | Qty | Nom. (mA ea.) | Peak (mA ea.) | Total nom. (mA) | Total peak (mA) |
|------|-----|--------------|---------------|-----------------|-----------------|
| PocketBeagle 2 Industrial (SoC active) | 8 | 500 | 1 200 | 4 000 | 9 600 |
| Wash (sensor suite + CAN/RS-485) | 4 | 700 | 1 400 | 2 800 | 5 600 |
| Zoë (radios TX simultaneous) | 4 | 1 500 | 2 500 | 6 000 | 10 000 |
| XCVR-49MHZ-2 sub-modules | 4 | 100 | 250 | 400 | 1 000 |
| WS2812B LED rings (3×) | 3 | 80 | 200 | 240 | 600 |
| HX711 + load cell | 1 | 10 | 10 | 10 | 10 |
| N20 winch motor (via DRV8833) | 1 | 200 | 500 | 200 | 500 |
| **5 V subtotal** | — | — | — | **13 650** | **27 310** |

At 5 V / 22.2 V conversion: 27.3 A × 5 V / 22.2 V ≈ **6.2 A from VBAT** at peak.

> **Note:** Simultaneous TX on all four Cape-B radios is an upper bound; in practice
> the four boards stagger TX by frequency and election priority. Sustained 5 V peak
> current ≈ 14–18 A in nominal flight.

### 3.3 Servo Loads (6 V rail)

| Load | Qty | Stall (mA) | Running (mA) | Total run (mA) |
|------|-----|-----------|--------------|----------------|
| Nacelle tilt servos (DS3218MG, ≥25 kg·cm @ 6 V) | 2 | 1 500 | 150 | 300 |
| Rear nozzle servo (SG90, Phase 11) | 1 | 700 | 70 | 70 |
| Cargo door servo (SG90) | 1 | 700 | 70 | 70 |
| Cargo release servo (SG90) | 1 | 700 | 70 | 70 |
| **6 V subtotal (running)** | — | — | — | **510** |
| **6 V subtotal (all stalled simultaneously)** | — | — | — | **5 300** |

All-servo stall is a transient; the BEC is sized for 5 A continuous (stall of 2×DS3218MG
+ 3×SG90 ≈ 5.1 A — marginal; the 6 V BEC is sized at 5 A with up to 7 A burst for
≤100 ms, which covers brief simultaneous stall events).

At 6 V / 22.2 V: 5.3 A × 6 V / 22.2 V ≈ **1.4 A from VBAT** at stall.

### 3.4 Total System Draw

| Scenario | VBAT current | Battery C-rate (4 Ah) |
|----------|-------------|----------------------|
| Hover, cruise (4× EDFs 50 % throttle) | ~45 A | 11.3 C |
| Max thrust hover (4× EDFs 100 %) | ~80 A | 20 C |
| Max thrust + all radios TX + all servos stall | ~90 A | 22.5 C |
| **Absolute peak (burst, <1 s)** | **~165 A** | **41 C** |

All figures are well within the 60 C (240 A) continuous rating of the 4 000 mAh pack
and the 150 A main fuse rating under sustained load.

---

## 4. Wire Gauge Sizing

Wire ampacity per UL 508A Table 40.3 / AWYC E-11, silicone insulation,
single conductor in free air, 60 °C ambient, 90 °C conductor temperature.

| Segment | Max current (A) | Required gauge | Specified gauge | Rated (A) | Margin |
|---------|----------------|---------------|-----------------|-----------|--------|
| Battery to PDB main bus | 165 (peak) / 90 (cont.) | ≥ 4 AWG | **4 AWG silicone** | 125 A cont. | +39 % at cont. |
| PDB to ESC1–ESC4 (each) | 55 (burst) / 28 (cont.) | ≥ 10 AWG | **10 AWG silicone** | 55 A | ≈ 0 % at burst |
| PDB 5 V BEC output | 18 A (cont.) | ≥ 14 AWG | **12 AWG silicone** | 30 A | +67 % |
| PDB 6 V BEC output | 5.3 A (stall) | ≥ 18 AWG | **16 AWG silicone** | 13 A | +145 % |
| Avionics bay intra-bay | 3 A/node | ≥ 22 AWG | **18 AWG shielded** | 7 A | +133 % |
| ESC signal (DSHOT) | <100 mA | 28 AWG | **28 AWG STP** | 500 mA | ≫ |

**ESC leg note:** 10 AWG silicone is rated 55 A free-air but ~40 A bundled. The
nacelle harness bundles port and starboard in the same conduit; derate to 40 A per
conductor. The 40 A fuse per ESC output provides coordinated protection.

---

## 5. Fuse Coordination

Fuse coordination ensures that a downstream fault clears the nearest upstream fuse
without propagating to the main bus or battery.

```
Battery ─────────────────────────────────────────────────────────
                │
          F1: 150 A MAXI blade (Littelfuse 0297150.ZXNV)
                │
         ┌──────┼──────────────────────┬─────────────┐
         │      │                      │             │
   F_ESC1: 40 A  F_ESC2: 40 A   F_ESC3: 40 A  F_ESC4: 40 A
   (Littelfuse   (Littelfuse      (Littelfuse   (Littelfuse
   0297040.WXNV) 0297040.WXNV)   0297040.WXNV) 0297040.WXNV)
         │      │                      │             │
        ESC1  ESC2                   ESC3          ESC4
```

### 5.1 Coordination Analysis

At an ESC-side short circuit (worst-case: ESC output directly to GND via zero impedance):

- Short current limited by wire impedance and battery IR. At 30 mΩ battery + 8 mΩ per
  1 m of 10 AWG = 38 mΩ total per branch: I_fault = 22.2 V / 0.038 Ω ≈ **584 A**.

- The 40 A branch fuse (standard automotive mini-blade) clears in < 1 ms at 584 A
  (10× rated current → clearing within 1–2 cycles per Littelfuse time–current curve).

- The 150 A MAXI fuse carries the same fault current. The MAXI fuse at 584 A (≈ 4×)
  clears in approximately 100–500 ms — much slower than the 40 A fuse.
  **Selective coordination is maintained**: the 40 A branch fuse blows first. ✓

- The surviving three ESC branches remain powered; the aircraft can continue on three
  nacelle motors (reduced T/W ≈ 1.20; controllable for RTH).

### 5.2 Phase 11 ESC5 Fusing (Deferred)

The 120 mm aft EDF ESC5 (80 A continuous, 110 A burst) shall use:
- F_ESC5: **100 A midi blade fuse** (Littelfuse 0299100.ZXNV, MIDI housing)
- Wire: **8 AWG silicone** from PDB to ESC5 (≥ 73 A rated free air)
- ESC5 output: XT60 (not XT30 — XT30 is rated 30 A continuous)

### 5.3 Fuse Temperature Derating

Automotive blade fuses derate to ~80 % of nominal in a 40 °C ambient (nacelle bay
temperature during sustained hover may reach 45–55 °C from EDF motor heat).
Effective ratings at 50 °C:
- 40 A mini blade → ~32 A effective continuous before nuisance trip risk
- 150 A MAXI blade → ~120 A effective continuous

**Consequence:** At sustained hover with each ESC drawing 28 A (nominal),
32 A effective rating provides 4 A / 14 % margin per branch. This is acceptable;
the branch fuse's role is fault protection, not thermal management. ESC thermal
derating should prevent sustained draws above 28 A in the nacelle environment.

---

## 6. EMI on Power Rails

### 6.0 500 W/m² Threat Environment

The Serenity UAV design envelope includes operation near commercial broadcast and
cellular antenna installations where ambient RF power density reaches **500 W/m²**.

```
E = √(P_density × Z₀) = √(500 W/m² × 377 Ω) ≈ 434 V/m
```

For comparison: MIL-STD-461G RS103 (the most demanding standard radiated
susceptibility test) requires operation at 200 V/m at 200 MHz–1 GHz. The Serenity
environment exceeds RS103 by a factor of 2.2× in field strength, or 7 dB.

**Required protection strategy:**

1. **Enclosure shielding (first line):** The Kaylee PCB is housed in a 1.5 mm 6061-T6
   aluminum enclosure with conductive EMI gasket providing ≥ 60 dB SE from 1 MHz
   to 6 GHz. At 434 V/m external, 60 dB reduces the internal field to ≤ 0.4 V/m —
   below the tested susceptibility of all ICs. See `Kaylee.md §Kaylee Shielded Enclosure`.

2. **Cable-conducted path (second line):** Cables act as antennas, injecting RF energy
   into the enclosure even when the enclosure shell itself is intact. Three layers of
   defense:
   - EMC cable glands (360° shield bond at enclosure wall)
   - Two-stage CM filter (CM1 + CM2 in series) on main bus input
   - Y-capacitors C_Y1/C_Y2 shunting residual CM energy to chassis

3. **PCB immunity (third line):** On-board TVS on I2C lines (D_I2C), low-ESR HF
   decoupling (C_DM1), and per-ESC CM chokes (CM_ESC1–4).

### 6.1 Main Bus EMI

The primary EMI coupling path is ESC switching noise (DSHOT600 / BLHeli32 synchronous
switching at 40–100 kHz) onto the VBAT bus, propagating to avionics via the BEC input.
The 500 W/m² external RF environment adds a second conducted coupling path via the
battery cable acting as a receiving antenna.

**Full mitigation stack (Kaylee):**

| Stage | Component | Purpose |
|---|---|---|
| 0. Enclosure | 1.5 mm Al box + CHO-SEAL 1217 gasket | ≥ 60 dB SE; reduces 434 V/m to ≤ 0.4 V/m at PCB |
| 0b. Cable gland | Pflitsch 750M EMC glands at all cable entries | 360° shield bond at enclosure wall; no pigtail break |
| 1. 1st stage CM choke | CM1: Würth 7440640500 (10 A, 2 × 100 µH) | CM attenuation: ~40 dB at 1 MHz; blocks cable antenna CM current |
| 2. 2nd stage CM choke | CM2: Würth 7440640500 (in series with CM1) | Additional ~40 dB at 1 MHz; two-stage cascade = ~80 dB CM at 1 MHz |
| 3. Y-capacitors | C_Y1, C_Y2: 4.7 nF / 250 V Y2 (VBAT+/− to chassis) | Residual CM RF energy shunted to chassis; bypasses PGND–chassis impedance |
| 4. Bulk capacitance | C1, C2: 2× 220 µF / 35 V electrolytic | Bus stiffening; DM low-frequency decoupling |
| 5. HF DM cap | C_DM1: 10 µF / 50 V X7R 1210 MLCC | Low-ESR DM decoupling above 100 kHz |
| 6. HF bypass | C3: 100 nF X7R 0805 MLCC | DM decoupling above 1 MHz |
| 7. TVS clamp | D1: SMBJ33CA bidirectional | Regen voltage spike + RF-induced transient clamping |
| 8. Per-ESC CM choke | CM_ESC1–4: Würth 7440640500 per ESC output | Prevents ESC PWM noise from coupling back into VDIS rail |
| 9. Per-ESC decoupling | C_DEC1–4: 470 µF / 35 V low-ESR electrolytic | Absorbs ESC stall transients before they reach VDIS |
| 10. BEC input | π-filter on each BEC input (10 µH + 100 µF + 100 nF) | Rejects ESC noise before SMPS conversion |
| 11. I2C TVS | D_I2C: NXP PRTR5V0U2X, dual TVS, 5 V clamp | Protects SCL/SDA from RF-induced transients at enclosure boundary |

### 6.2 5 V Avionics Bus EMI

The 5 V bus is a low-impedance rail shared by 8 nodes across four bays.
Avionics EMI coupling from motor noise is a serious concern.

**Mitigation:**

- Kaylee SMPS switching frequency is ≥ 300 kHz (TPS54620) — keeps switching noise
  above the EDF modulation frequencies but below the BLHeli32 DSHOT harmonics.
- Each avionics bay has a local 47 µF + 100 nF + 10 nF bypass cap stack at the
  5 V entry (J-PWR on Wash and Zoë).
- Wash power entry π-filter (FB1 Würth 742792512 + C11/C12) provides additional
  conducted immunity per CAPE-A-2.md §6.
- 5 V bus wire is twisted pair (18 AWG), shielded, drain wire grounded at Kaylee.

### 6.3 Grounding Architecture

**Star ground:** All power grounds return to a single point at the Kaylee PGND bar.

```
Kaylee PGND bar (star point)
├── Battery negative (XT60 GND)
├── ESC GND returns (each ESC GND to PGND via 10 AWG return wire)
├── 5 V BEC GND output (to avionics 5 V GND bus)
├── 6 V BEC GND output (to servo 6 V GND bus)
└── Chassis bond (10 AWG to CF keel bar datum)
```

The avionics GND bus is connected to PGND via a ferrite bead (Würth 742792512,
600 Ω @ 100 MHz, 2 A) to prevent ESC switching currents from injecting common-mode
noise into the avionics ground. Single-point; no ground loops.

---

## 7. Battery Monitoring Architecture

### 7.1 Pack-Level Voltage (INA226 on Wash)

Each Wash has one INA226AIDGSR wired to J_VBAT (direct VBAT tap), configured
in voltage-only mode (no shunt). Provides coarse pack voltage at 1.25 mV/LSB.

- I2C address: 0x40 (on Cape-A internal I2C bus)
- Driver: `bmon_ina2xx` (bmon_ina2xx.h / bmon_ina2xx.c)
- Poll rate: 10 Hz (via FC node pwr_fault task)

### 7.2 Main Bus + Per-ESC Current (INA226 on Kaylee)

Five INA226 devices on the Kaylee, connected to FC1 (Shepherd's room / Bay A, Wash) via a dedicated
I2C bus (I2C-PDB, JST-GH 4-pin to J_EXT_I2C on Wash).

| Device | Location | Shunt R | I2C Addr | Full-scale I |
|--------|----------|---------|----------|-------------|
| U_IS_MAIN | Main bus (post F1) | 500 µΩ | 0x44 | 150 A |
| U_IS1 | ESC1 output (post F_ESC1) | 1 mΩ | 0x40 | 60 A |
| U_IS2 | ESC2 output (post F_ESC2) | 1 mΩ | 0x41 | 60 A |
| U_IS3 | ESC3 output (post F_ESC3) | 1 mΩ | 0x42 | 60 A |
| U_IS4 | ESC4 output (post F_ESC4) | 1 mΩ | 0x43 | 60 A |

All five devices share one I2C segment. The FC node reads all five in a round-robin
at 10 Hz. Driver: `bmon_ina2xx` extended current-sensing mode.

**Shunt resistor selection:**

- U_IS_MAIN (500 µΩ): Isabellenhütte BVR-Z-R0005 or Bourns CSS2H-2512K-0L5F0F,
  4-terminal Kelvin, 3 W continuous (at 150 A: P = 150² × 0.0005 = 11.25 W — NOT
  continuous rated). Main bus INA226 is for average current monitoring; sustained
  150 A would damage a standard shunt. Use a current transformer (CST series,
  Murata 56-100A range) for high-current transient detection instead, with the
  shunt for calibration at moderate loads. Alternatively, use a 5 W / 1 mΩ shunt
  and accept 75 A full scale.

  **Revised main bus shunt:** 1 mΩ / 5 W → 75 A full scale (covers nominal 72 A
  propulsion load). Peak 165 A saturates the INA226 shunt register but the fault
  is detected via the ALERT pin (over-voltage on shunt). U_IS_MAIN I2C address
  remains 0x44.

- U_IS1–IS4 (1 mΩ each): Bourns CSS2H-2512K-1L00F, 4-terminal Kelvin, 3 W.
  At 40 A: P = 40² × 0.001 = 1.6 W — within 3 W rating. ✓
  At 55 A burst: P = 55² × 0.001 = 3.0 W — at rating limit; acceptable for ≤10 s.

### 7.3 Cell-Level Monitoring (BQ76930 on Kaylee)

The Texas Instruments BQ76930 is a 6–10 series cell front-end monitor IC mounted on
Kaylee and connected to the JST-XH-7P balance lead.

| Parameter | Value |
|-----------|-------|
| Part | BQ76930PWRQ1 (TI, automotive-qualified, HTSSOP-30) |
| Cells | 6S (VC0–VC6 inputs, BAL_GND reference) |
| Cell voltage range | 0.5–5.0 V per cell |
| OVP threshold | 4.20 V/cell (programmed) |
| UVP threshold | 3.00 V/cell (programmed) |
| OCD threshold | 50 A (programmed via PROTECT2 register) |
| SCD threshold | 150 A / 100 µs (programmed via PROTECT1 register) |
| Temperature input | 10 kΩ NTC on BAT exterior, TS1 input |
| Over-temp limit | 60 °C (PROTECT3 OT threshold) |
| I2C address | 0x08 (CHEM pin tied high; CRC mode enabled) |
| Alert output | Open-drain ALERT → Wash GPIO (J_EXT_I2C SCL-side, 2.2 kΩ pull-up) |
| Driver | `cell_mon_bq769x0` (cell_mon_bq769x0.h / cell_mon_bq769x0.c) |

The BQ76930 also drives CHG and DSG FET-enable outputs. On the Kaylee battery input,
the CHG/DSG outputs drive the gate of an integrated power path switch
(AON6556 N-MOSFET pair), enabling the BQ76930 to disconnect the battery in a
hardware-level fault event independent of firmware.

---

## 8. Fault Levels and Load Shedding

Implemented by the `pwr_fault` firmware module (pwr_fault.h / pwr_fault.c).

### 8.1 Voltage Thresholds

| State | Condition | Action |
|-------|-----------|--------|
| NORMAL | All cells ≥ 3.50 V; pack ≥ 21.0 V | No action |
| WARN | Any cell < 3.50 V OR pack < 21.0 V | CAN FD broadcast POWER_WARN; GCS alert; log entry |
| CRITICAL | Any cell < 3.30 V OR pack < 19.8 V | Shed non-essential loads (see §8.3); increase log rate; initiate RTH |
| EMERGENCY | Any cell < 3.00 V OR pack < 18.0 V OR BQ76930 UV latch | All non-propulsion loads off; 70 % throttle cap; FC fault latch |

Hysteresis: 100 mV per cell before stepping down a severity level.

### 8.2 Current Thresholds

| Fault | Threshold | Latency | Action |
|-------|-----------|---------|--------|
| ESC over-current warn | Any ESC > 35 A | Instant | CAN FD POWER_WARN; log |
| ESC over-current critical | Any ESC > 40 A for > 5 s | 5 s | DSHOT idle command to that EDF; latch requires GCS ack |
| ESC burst | Any ESC > 55 A | < 100 ms | Immediate DSHOT disarm that EDF; latch |
| Main bus warn | > 65 A (sustained) | 1 s | CAN FD broadcast; log |
| Main bus critical | > 75 A (sustained) | 5 s | Shed non-propulsion loads |
| BQ76930 SCD | Hardware short-circuit | < 200 µs | BQ76930 hardware disconnects DSG FET |

### 8.3 Load Shedding Priority

Shedding is additive: each higher level includes all lower-level sheds.

| Priority | Shed target | VBAT saving (A) | 5 V saving (A) |
|----------|------------|-----------------|----------------|
| 1 (CRITICAL) | Cargo winch N20 motor | 0.1 | 0.5 |
| 2 (CRITICAL) | WS2812B LED rings (all 3) | 0.1 | 0.6 |
| 3 (CRITICAL) | LoRa RFM95W TX reduced power | ~0.0 | 0.1 |
| 4 (CRITICAL) | WiFi WL1837MOD TX off | ~0.0 | 0.5 |
| 5 (EMERGENCY) | All non-propulsion 5 V loads off | ~0.3 | — |
| 6 (EMERGENCY) | EDF throttle cap at 70 % | ~22 A | 0 |

At 70 % throttle cap: thrust ≈ 49 % (thrust ∝ RPM² ∝ throttle²) — T/W drops from
1.61 to ~0.79. This is insufficient for hover, but firmware switches to a fixed-wing
glide descent profile and activates RTH / controlled descent algorithm.

### 8.4 Battery Hardware Protection (BQ76930)

The BQ76930 enforces hardware-level protection independent of firmware:

| Protection | Threshold | Response |
|-----------|-----------|---------|
| OVP (per cell) | 4.20 V | Opens CHG FET within 1 µs (charge path only) |
| UVP (per cell) | 3.00 V | Opens DSG FET within OD delay | 
| OCD (pack) | 50 A / 8 ms | Opens DSG FET |
| SCD (pack) | 150 A / 100 µs | Opens DSG FET |
| OTP (pack temp.) | 60 °C | Opens both FETs |

After a BQ76930 hardware trip, the battery is fully disconnected from the load.
Recovery requires a power cycle (reconnect battery) after the fault condition clears.
The flight controller logs the BQ76930 SYS_STAT register contents via Cape-A I2C
on every poll cycle, providing pre-fault data for post-flight analysis.

---

## 9. Electrical Fault Margin Validation

### 9.1 ESC Fuse Sizing Validation

**Constraint:** Fuse must carry max sustained ESC current without nuisance blowing,
but must clear before the 10 AWG wire reaches 90 °C.

- 10 AWG silicone rated 55 A (free air, 60 °C ambient)
- Nacelle ambient: ~45 °C during flight → derate to ~48 A effective
- 40 A fuse at 45 °C: derate to ~32 A continuous without trip
- Maximum ESC sustained current: 28 A nominal; 40 A brief peak
- Fuse tolerance: ±10 % on trip point (Littelfuse ATM/min-blade specs)
- At 40 A / 32 A effective rating: fuse operates at 125 % of its derated rating
  → blows in < 60 s per time-current curve ✓ (acceptable for transient peak)

**Conclusion:** 40 A mini-blade fuses are correctly coordinated with 10 AWG wire.
Sustained overcurrent trips within 60 s before wire insulation damage.

### 9.2 BEC Brown-Out Threshold

The TPS54620 BEC regulators maintain 5 V output over 4.5–28 V input.
Minimum operational input: 4.5 V + V_5V = 9.5 V → well below the 18.0 V
emergency cut-off. The BEC will not brown out before the battery emergency threshold.

Minimum PocketBeagle 2 Industrial VIN: 4.75 V (AM6254 VIN absolute minimum 4.5 V).
5 V BEC output tolerance: ±2 % = 4.90 V minimum → 0.40 V margin above PB2-I minimum.

### 9.3 Servo BEC Brown-Out

6 V BEC (TPS54540 configured for 6.0 V ±1 %): minimum output 5.94 V.
DS3218MG servo minimum operating voltage: 4.8 V.
SG90 minimum operating voltage: 4.8 V.
Margin: 5.94 V − 4.8 V = **1.14 V** — safe; brown-out requires catastrophic BEC failure.

### 9.4 Main Bus Fuse Sizing Validation

150 A MAXI fuse at sustained 90 A (continuous hover):
- 90 / 150 = 60 % of rated current → no trip; fuse operates indefinitely. ✓
- At peak 165 A: 165 / 150 = 110 % → blows in ~ 60–120 s per Littelfuse time-current curve
- This is undesirable (nuisance blow) but unlikely: 165 A requires all four EDFs at
  absolute burst simultaneously while all radios TX simultaneously, which is transient
  (< 1 s). The MAXI fuse at 110 % takes > 60 s to blow — well beyond the burst duration.

**Conclusion:** 150 A MAXI fuse is correctly sized for the 90 A sustained hover load
and provides 150+ s of protection margin at 110 % overload peak.

---

## 10. Power Sequencing

On battery connect, the system powers up in this order:

1. **T+0 ms:** VBAT available. BQ76930 wakes from SHIP mode; performs initial cell measurement (takes ≈ 200 ms).
2. **T+10 ms:** 5 V BEC output reaches regulation. PocketBeagle 2 boards begin boot (AM6254 boot ROM from eMMC, ≈ 30 s to Linux prompt).
3. **T+20 ms:** 6 V BEC output reaches regulation. Servos receive power; park at last-known position.
4. **T+250 ms:** BQ76930 cell voltages valid. FC1 reads initial cell voltages via cell_mon driver.
5. **T+30 s:** All 8 FC/CN nodes booted; CAN FD heartbeat election complete; FC1 assumes primary role.
6. **T+31 s:** ESC arming sequence initiated (zero-throttle signal for ≥ 2 s per BLHeli32 protocol).
7. **T+33 s:** All ESCs armed; system ready for pilot command.

**ESC soft-start:** BLHeli32 ESCs enforce their own motor start-up ramp (100 ms motor
start delay, 2 s idle before commanding). The DSHOT governor in firmware additionally
ramps from idle RPM at `EDF_GOV_RPM_RAMP_RATE` = 50 RPM/ms to prevent inrush current.

---

## 11. Redundant Power Rail Strategy

All 8 avionics nodes share one 5 V bus from Kaylee. This is a single rail, not
redundant in the hardware-failure sense. Redundancy provisions:

- **SMPS redundancy (Kaylee):** Two independent 5 V SMPS (TPS54620 × 2) with outputs
  Schottky diode-OR'd (MBRD1045CT × 2, each sharing 50 % load). If one SMPS fails,
  the other carries the full 5 V load up to 6 A (limiting; some nodes may brown out
  if peak load exceeds 6 A — load shedding handles this).

- **Node-level isolation:** Each Wash bay power connector (J-PWR, Molex Nano-Fit)
  can be individually disconnected. Any node pair (FC + CN) in one bay can be removed
  from service without affecting other bays.

- **Avionics bay Faraday isolation:** Each bay's 3M 1181 copper foil lining provides
  independent EMI shielding. A failure in one bay (e.g., short-circuit from a damaged
  Cape causing BEC current limit) does not propagate to adjacent bays.

- **No dual-battery architecture in Phases 5–10.** A second battery for avionics-only
  power would add 525 g (2800 mAh) and reduce T/W from 1.61 to 1.42. Decision:
  rely on BQ76930 hardware cell-protection and the SMPS redundancy above. Dual-battery
  architecture is a Phase 12 enhancement candidate if AUW budget permits.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
