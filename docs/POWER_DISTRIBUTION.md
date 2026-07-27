# Serenity UAV — Power Distribution & Battery Management

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Rev R
**Date:** 2026-06-11

---

## 1. Architecture Overview

```text
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

Each ESC feeds one 50 mm EDF (Phases 5–10). Phase 11 adds ESC5 for the 55 mm fuselage EDF.

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

```text
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
| **ESC5 – Fuse 55 mm EDF (Ph. 11)** | 1 | 40 | 65 | DNP | DNP |
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
| Emma sub-modules | 4 | 100 | 250 | 400 | 1 000 |
| HX711 + load cell | 1 | 10 | 10 | 10 | 10 |
| STS3215 winch servo (via CAN-PERIPH-GW, RAIL-2) | 1 | 200 | 1200 | 200 | 1200 |
| **5 V subtotal** | — | — | — | **13 410** | **26 710** |

At 5 V / 22.2 V conversion: 26.7 A × 5 V / 22.2 V ≈ **6.0 A from VBAT** at peak.
(The WS2812B exhaust LED rings — formerly 240 mA nom / 600 mA peak — were removed
from the design; see TODO §1.1.3.5.)

> **Note:** Simultaneous TX on all four Cape-B radios is an upper bound; in practice
> the four boards stagger TX by frequency and election priority. Sustained 5 V peak
> current ≈ 14–18 A in nominal flight.

The §3.2 table does **not** include the two **Jayne** vision boards (nose + cargo). Jayne is
a standalone board (not a PB2-I cape) with its own 5 V input (`J_PWR`); its load is budgeted
separately in §3.2.1 below and is fed from a **dedicated Kaylee 5 V payload rail**, not the
shared avionics bus.

### 3.2.1 Jayne Vision-Board Loads (dedicated 5 V payload rail)

Two Jayne boards are installed (bow sensor pod + cargo-bay nadir mount). Each carries a TI
AM62A7 vision SoC (via TPS65219 PMIC), a KSZ9477 Ethernet switch, an MSPM0G3507 MCU, an
SLB9670 TPM, an ISOW1044 isolated CAN-FD, plus the camera module, TFmini-S ToF, and a laser.
Figures are **datasheet-typical** at the 5 V board input (PMIC/buck-fed items divided by
0.88 efficiency); refine when the placeholder SoC/switch footprints are replaced with sourced
silicon (Jayne.md "Verified vs. Placeholder").

| Load (per board) | Typ (A @5 V) | Peak (A @5 V) | Notes |
|---|---|---|---|
| AM62A7 SoC (quad-A53 + VPAC/ISP + H.264/H.265 encode) | 0.57 | 1.02 | via TPS65219 PMIC |
| KSZ9477 7-port Ethernet switch (3 ports active) | 0.27 | 0.46 | |
| MSPM0G3507 MCU + SLB9670 TPM | 0.02 | 0.03 | |
| ISOW1044 isolated CAN-FD (integrated iso DC-DC) | 0.05 | 0.10 | |
| Camera module (MIPI CSI-2, via J_CAM) | 0.11 | 0.18 | |
| TFmini-S ToF (140 mA typ / 200 mA peak @5 V) | 0.14 | 0.20 | REF-SENSOR-002 |
| Ethernet magnetics + passives + LDO overhead | 0.04 | 0.07 | |
| **Core subtotal (no laser)** | **1.20** | **2.06** | |
| Laser — both sites (Class 2 green, ≤ 1 mW optical) | +0.02 | +0.02 | negligible; see `docs/JAYNE_LASER_ANALYSIS.md` (nose is Class 2, not 3B) |

**Per board:** ≈ **1.22 A** typ / **2.08 A** peak (both boards are now Class 2 laser — the nose
is a concentrated dot + camera strobe-difference detection, ~0.45 mW, not a 500 mW Class 3B
module, so its laser draw is negligible like the cargo unit).
**Both boards (2×):** ≈ **2.4 A** typ / **~4.2 A** peak at 5 V →
≈ **0.6 A** typ / **~1.0 A** peak at VBAT (5 V ÷ 22.2 V ÷ 0.92 BEC eff).

**Feed decision — dedicated Kaylee 5 V payload rail (recommended over sharing the avionics
bus).** The shared 5 V avionics rail is already tight: realistic sustained load ≈ 10 A (§3.2)
against a dual-TPS54620 BEC whose **single-fault** capacity is only 6 A (both healthy ≈ 12 A;
§11). Adding Jayne's ~2.4 A nom to that rail pushes nominal to ≈ 12.4 A — at/over the healthy
BEC ceiling and well past the 6 A single-fault floor, worsening the existing brown-out
exposure. Jayne is also a switching video-SoC load whose noise should not sit on the shared
avionics bus. Therefore Jayne is powered from its **own** Kaylee rail:

- **U_BEC_5V_3 (RAIL-2):** a third identical TPS54620RGYT (6 A) BEC channel, VDIS input →
  5.4 V set-point. 6 A rating vs 2.4 A nom / 4.2 A peak = comfortable margin. Rather than a
  standalone rail, RAIL-2 is **diode-OR cross-tied to the avionics RAIL-1** so the two rails
  back each other up while staying fault-isolated — full topology, drop budget, and fault-mode
  table in **§11.1**.
- **J_JAYNE:** new Molex Nano-Fit 4-pin (matches `J_5V`) 5 V payload output on Kaylee, harnessed
  to both Jayne `J_PWR` inputs.
- **Fuse/limit:** the TPS54620 internal current limit plus a 3 A resettable polyfuse per Jayne
  drop (each board ≤ 2.72 A peak).
- **Wire gauge:** 18 AWG shielded twisted pair (7 A rated) per drop — ≫ the ≤ 2.7 A per-board
  load; consistent with §4 "Avionics bay intra-bay".
- **Runs:** Kaylee (middle-section inner neck) → nose (bow pod) and → cargo nadir mount;
  comparable length to the existing avionics 5 V bay runs. Route with the Ethernet-ring / CAN
  harness Jayne already shares to each bay.

Implementing the RAIL-2 channel (`U_BEC_5V_3`) + cross-tie + `J_JAYNE` on Kaylee is a Kaylee
revision change (sibling to the planned Rev S1 servo-rail change); full design in **§11.1**,
tracked in TODO.md §1.2c.4. Until implemented, a Jayne board may be bench-fed from the shared
5 V bus **only** with active load-management (accept that it consumes the remaining avionics
margin and worsens single-fault brown-out) — not the flight configuration.

### 3.3 Servo Loads (6 V rail)

| Load | Qty | Stall (mA) | Running (mA) | Total run (mA) |
|------|-----|-----------|--------------|----------------|
| Nacelle tilt servos (DS3218MG, ≥25 kg·cm @ 6 V) | 2 | 1 500 | 150 | 300 |
| RCS proportional valve servos (SG90 class, Phase 11) | 4 | 700 | 70 | 280 |
| Cargo door servo (SG90) | 1 | 700 | 70 | 70 |
| Cargo release servo (SG90) | 1 | 700 | 70 | 70 |
| **6 V subtotal (running)** | — | — | — | **720** |
| **6 V subtotal (all stalled simultaneously)** | — | — | — | **7 400** |

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

The two **Jayne** vision boards add ≈ **0.6 A typ / ~1.2 A peak at VBAT** (2.4 A / 4.8 A at
5 V through the dedicated U_BEC_VERA rail, §3.2.1) — negligible against the propulsion-dominated
totals above, but material to the 5 V-side budget, which is why Jayne gets its own rail rather
than loading the already-tight shared avionics BEC.

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

```text
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

The 55 mm aft EDF ESC5 (50 A continuous, ~65 A burst) shall use:

- F_ESC5: **60 A midi blade fuse** (Littelfuse 0299060.ZXNV, MIDI housing)
- Wire: **10 AWG silicone** from PDB to ESC5 (≥ 55 A rated free air)
- ESC5 output: XT60 (not XT30 — XT30 is rated 30 A continuous; 55 mm EDF draws ~40 A)

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

```text
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
  conducted immunity per Wash.md §6.
- 5 V bus wire is twisted pair (18 AWG), shielded, drain wire grounded at Kaylee.

### 6.3 Grounding Architecture

**Star ground:** All power grounds return to a single point at the Kaylee PGND bar.

```text
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

The Texas Instruments BQ76930 is a 6–10 series cell frontend monitor IC mounted on
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
| 1 (CRITICAL) | Cargo winch STS3215 servo | 0.2 | 1.2 |
| 2 (CRITICAL) | LoRa RFM95W TX reduced power | ~0.0 | 0.1 |
| 3 (CRITICAL) | Wi-Fi WL1837MOD TX off | ~0.0 | 0.5 |
| 4 (EMERGENCY) | All non-propulsion 5 V loads off | ~0.3 | — |
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
  architecture is a Phase 12 enhancement — now specified as a **swappable cargo-bay
  Range-Extender Battery Module (§11.2)**, so its AUW/T-W cost is paid only on range missions.

### 11.1 Second 5 V Rail (Jayne / payload) — cross-tied, mutually fault-tolerant (PLAN)

**Objective.** Give Jayne its own 5 V rail (§3.2.1) using the **same BEC part chain** as the
avionics rail, so the two rails are **interchangeable** (identical channels) and **fault
tolerant of each other** (a fault on one rail cannot collapse the other, and either rail's
supply can back up the other). Minimal delta — no new part numbers.

**BEC channel (the reused "part chain," identical for every channel).** One channel =
TPS54620RGYT (6 A sync buck) + 10 µH inductor (Würth 744314100) + `R_FB` divider + 100 µF/50 V
input cap + 220 µF ∥ 100 nF output cap + 742792612 input ferrite + MBRD1045CT output OR-diode.
Each new channel is a copy-paste of `U_BEC_5V_1`.

**Topology (N+1, cross-tied).** The avionics rail keeps its existing **two** channels (it needs
~10 A, > one 6 A channel); the Jayne rail adds **one** identical channel; the two rails are
diode-OR cross-tied for mutual backup:

```text
BEC-1 ─D_OR1─┐
             ├── RAIL-1  (5V_AVIONICS) ── F_5V (6 A) ──── J_5V     [2 channels, 12 A]
BEC-2 ─D_OR2─┘        │
                 D_X1 ▼  ▲ D_X2   ── F_X (3 A, cross-tie)          [mutual backup path]
                      │  │
BEC-3 ─D_OR3──────────┴──┴──────── RAIL-2 (5V_JAYNE) ── F_VERA (3 A) ── J_JAYNE   [1 channel, 6 A]
```

- **`D_X1` (RAIL-1→RAIL-2)** and **`D_X2` (RAIL-2→RAIL-1)** are two more MBRD1045CT (reused
  part), in series with cross-tie fuse **`F_X`**. Normally both rails sit at the same voltage
  so neither `D_X` conducts; a `D_X` conducts only when the *other* rail droops.

**Set-point / drop budget (important).** Backup current crosses **two** Schottky drops
(source channel's `D_OR` + the cross-tie `D_X` ≈ 0.6 V total). To keep a backed-up rail above
the PocketBeagle-2-I 4.75 V minimum (§9.2), raise the TPS54620 set-point from the present
**5.3 V to 5.4 V**:

| Mode | Path | Rail voltage |
|---|---|---|
| Normal | BEC → `D_OR` → rail | 5.4 − 0.3 = **5.1 V** (within 5 V +2 %) |
| Cross-tie backup | BEC → `D_OR` → other rail → `D_X` → rail | 5.4 − 0.6 = **4.8 V** (> 4.75 V min, +0.05 V) |

(If more backup margin is wanted, a 5.5 V set-point gives 5.2 V normal / 4.9 V backup; or an
ideal-diode-OR controller cuts the drop to ~0.02 V — but that adds a new part, against the
minimal-parts goal, so plain Schottky + a modest set-point bump is the recommendation.)

**Fault modes — each rail is tolerant of the other:**

| Fault | Response |
|---|---|
| BEC-3 (Jayne) regulator fails | RAIL-2 droops → `D_X1` feeds Jayne from the RAIL-1 pair (2.4 A ≪ 12 A spare); avionics unaffected |
| One avionics BEC fails | survivor (6 A) + BEC-3 via `D_X2` back up RAIL-1; §8.3 load-shed trims to fit |
| Short on the RAIL-2 node (upstream of `F_VERA`) | `F_X` blows → RAIL-2 isolated from RAIL-1; BEC-3 OCP limits; **RAIL-1 keeps running** |
| Short at J_JAYNE (downstream) | `F_VERA` clears; RAIL-1 unaffected |
| Short at J_5V (downstream) | `F_5V` clears; RAIL-2 unaffected |
| A BEC output fails *short* | its `D_OR` reverse-blocks, keeping the shorted channel off its rail so the cross-tie can carry the rail |

**Delta vs. today (no new part numbers):** +1 TPS54620 channel (`U_BEC_5V_3` + `L_5V3` +
`R_FB3` + `C_BEC3_IN` + `C_BEC3_OUT` + `FB_5V3` + `D_OR3`); +2 MBRD1045CT (`D_X1`/`D_X2`);
+2 fuses (`F_X`, `F_VERA`) and re-use/add `F_5V`; +1 output connector (`J_JAYNE`, Molex
Nano-Fit 4-pin, matching `J_5V`); the two existing `R_FB` dividers re-valued for 5.4 V. Mass
≈ +5 g. Interchangeability is at the **channel** level: all three BEC channels are the identical
block, and any channel can be built or swapped identically.

**Symmetric alternative (fully interchangeable *rails*, +1 more channel).** If both rails should
be equal-capacity and each internally redundant, make RAIL-2 a **pair** too (4 channels total,
2 + 2, both 12 A, both diode-OR internally, cross-tied). This is the maximally-fault-tolerant
option but adds a 4th channel — recommended only if the payload rail later grows past ~5 A or
needs its own single-fault redundancy. The N+1 (2 + 1) plan above is the minimal choice that
still makes the two rails fault-tolerant of each other.

**Status: PLAN.** Not yet in KiCad — this is a **Kaylee board revision** (schematic-first, then
PCB placement/routing; place `U_BEC_5V_3` near the existing BEC pair, keep its SW node in a
GND-pour keepout per §PCB Layout Constraints). Sibling to the planned Rev S1 servo-rail change.
Tracked in `avionics/kicad/Kaylee.md` and `TODO.md §1.2c.4`.

### 11.2 Cargo-bay Range-Extender Battery Module (swappable payload) — PLAN

**Objective.** Make the cargo bay accept **either** the standard cargo payload **or** a drop-in
**Range-Extender Battery Module (RBM)** — a second 6S pack — for extended-range missions. This
realizes the "dual-battery architecture" previously deferred to Phase 12 (§11, last bullet),
now as an *interchangeable payload* rather than a permanent fixture, so the AUW/T-W penalty is
paid only on range missions. The two uses are **mutually exclusive** (cargo *or* RBM, not both).

**Electrical — self-contained module, OR-combined into VBAT (hot-swap-safe, fault-isolated).**
The intelligence lives on the RBM so the cargo payload path stays a dumb mechanical swap and
Kaylee gains only one input:

```text
RBM (in cargo bay):
   6S LiPo ─ JST-XH bal ─ BQ76930-class BMS (OVP/UVP/OCD/SCD, own FET) ─┐
                                                                        ├─ ideal-diode ORing
   (on-module protection + reverse-blocking)                           │   (LTC4359-class)
                                                                        ▼
                                            RBM XT60 out ───────────────┘
                                                    │
Kaylee:  J_BATT2 (new XT60 in) ── F_BATT2 ── ideal-diode / current-share combiner ── VBAT rail
                                              (with the main pack's J_BATT path)
```

- The **ideal-diode ORing combiner** (e.g., LTC4359 per pack, or an LTC4370 dual current-share
  controller across `J_BATT`/`J_BATT2`) lets the RBM parallel the main pack **without
  cross-charging surge** if the packs' state-of-charge differ, and **reverse-blocks** so a
  faulted or absent RBM cannot drain or back-feed the main pack — each pack is fault-tolerant
  of the other (same philosophy as the §11.1 5 V cross-tie, applied at VBAT).
- **Current sharing:** for the two packs to share hover current, use the *same pack model* and
  start both **matched-SoC at takeoff** (or an LTC4370 to force balanced sharing). Simple
  diode-ORing alone lets the higher-voltage pack hog — acceptable if matched, otherwise use the
  current-share controller.
- **Monitoring:** the RBM carries its own BMS; the `pwr_fault` firmware adds a second pack
  context (voltage/current/SoC) over the existing I²C/telemetry, and the combiner's fault/PGOOD
  status is logged. On RBM fault the combiner isolates it and the aircraft continues on the
  main pack (RTH).

**Battery options and the range/endurance trade** (baseline AUW 2 768 g / T-W 1.61, hover
≈ 76 A, usable hover ≈ 2.5 min; hover current scales ≈ AUW¹·⁵, cruise range ≈ energy⁄weight):

| RBM pack | Added mass | AUW | Hover T/W | Hover endurance | Cruise range |
|---|---|---|---|---|---|
| none (cargo) | — | 2 768 g (6.10 lbm) | 1.61 | 2.5 min (1.0×) | 1.0× |
| 6S 2 800 mAh | +525 g (1.16 lbm) | 3 293 g (7.26 lbm) | 1.36 | 3.3 min (1.31×) | ~1.43× |
| **6S 4 000 mAh** (matched) | +750 g (1.65 lbm) | 3 518 g (7.76 lbm) | **1.27** | 3.5 min (1.40×) | **~1.57×** |
| 6S 6 000 mAh (hi-cap) | +1 000 g (2.20 lbm) | 3 768 g (8.31 lbm) | 1.18 | 4.0 min (1.57×) | ~1.84× |

**Key finding — this is a *cruise-range* enhancement, not a hover one.** Every RBM option drops
hover T-W below the 1.5 comfort target (to 1.18–1.36), though all stay above the 1.0 hover
floor. So the RBM is for **extended-range forward flight** (wings carrying lift), where range
gains ~1.4–1.8×; hover is still possible but with reduced attitude-control margin, so hover
should be brief (takeoff/transition/landing) on a range mission. **Recommended pack: the matched
6S 4 000 mAh** (identical to the main pack → simplest current-sharing and interchangeability,
~1.57× range at T-W 1.27).

**Mechanical (Jayne cargo mounts).** The RBM is a tray sized to the cargo-bay payload envelope,
retained by the **same cargo hooks / release mechanism** the standard payload uses (so a fault
can still jettison it if required), with a captive **XT60 pigtail to `J_BATT2`** and a keyed
polarity guard. Mass budget above; verify the cargo-bay door and Jayne clearances against the
tray. **CG:** the RBM sits at/near the cargo-bay station, close to the main battery rail (CG
target 190 mm, §14) — a second ~750 g mass in the bay shifts CG and must be re-balanced on the
keel rail; check on the physical CG rig per §14.1 before flight (a full moment-table entry is a
follow-on to this plan).

**Delta parts (Kaylee):** +1 `J_BATT2` (XT60) input, +`F_BATT2` fuse, + the ideal-diode/
current-share combiner (LTC4359- or LTC4370-class — a *new* part family, unlike the §11.1 rail
which reused existing parts) + its FETs/passives. Plus the RBM assembly (pack + BMS + ORing +
tray). **Status: PLAN, Phase 12 enhancement** — supersedes the §11 "dual-battery Phase 12
candidate" note; tracked in `TODO.md`. Not yet in KiCad/CAD.

---

## 12. VTOL Thrust Analysis (Phases 5–10)

<!-- ============================================================
     VTOL THRUST ANALYSIS — Phases 5–10 (XFly Galaxy X5 50 mm)
     Authoritative EDF specification: XFly Galaxy X5 50 mm
       12-blade 6S 3200 KV, 1,240 g static thrust per unit.
     AUW figures from §2 of this document (Rev Q baseline).
     All imperial primary, metric parenthetical per AGENTS.md.
     Reference: AGENTS.md §"Powerplant" and §2 Battery Selection.
     ============================================================ -->

### 12.1 Nacelle-Only Vertical Lift (Nacelles at 90°)

In VTOL hover the nacelles are tilted to 90° (vertical). The rear fuselage EDF
exhausts longitudinally and contributes **zero vertical thrust** in its fixed
installation regardless of throttle setting.

<!-- Thrust summation per AGENTS.md: "Use 2232g per nacelle for static thrust."
     Each nacelle = 2 EDFs × 1,240 g × 90 % stator efficiency = 2,232 g.
     2 nacelles × 2,232 g = 4,464 g total nacelle VTOL lift.
     Phase 5–10 AUW = ~2,768 g (minimum viable 4-node build, per TODO.md). -->

| EDF group | Unit count | Thrust per unit | Group thrust | Contributes to VTOL lift? |
|---|---|---|---|---|
| Nacelle EDFs — XFly Galaxy X5 50 mm 6S 3200 KV (Phases 5–10) | 4 | 1,240 g (2.73 lbf) each; **2,232 g (4.92 lbf) per nacelle pair** at 90 % stator eff. | **4,464 g (9.84 lbf)** | **YES** |
| Rear fuselage EDF — 55 mm 6S (Phase 11, DNP) | 1 | ~1,500 g (3.31 lbf) fan; ~1,275 g (2.81 lbf) net forward after ~15 % RCS bleed | ~1,275 g forward | **NO — horizontal (cruise) thrust only; fixed canonical aft nozzle** |

### 12.2 Thrust-to-Weight Ratios

<!-- AUW figures from TODO.md (authoritative build guide):
       Phase 5–10 AUW = ~2,768 g (4-node minimum viable flyer; from TODO.md §Phase 5).
       Phase 11 AUW   = ~3,130 g (Phase 5–10 + ~360 g 55 mm rear-EDF + RCS system).
     AGENTS.md spec: "Use 2232g per nacelle for static thrust."
     The rear EDF fires aft through the fixed canonical nozzle → horizontal (cruise) thrust only;
       it is NOT counted in hover T/W. Hover T/W is set by the 4 nacelle EDFs alone.
     T/W at Phase 5–10: 4,464 / 2,768 = 1.61 — VTOL hover is achievable from Phase 5.
     T/W at Phase 11:   4,464 / 3,130 = 1.43 (nacelles only; rear EDF adds cruise thrust, not lift). -->

**Phase 5–10 VTOL thrust (nacelle-only):** 2 nacelles × 2,232 g = **4,464 g (9.84 lbf)**

| Mission profile | AUW | T/W (hover) | Assessment |
|---|---|---|---|
| Phase 5–10 (4-node min. viable, ~2,768 g) | **2,768 g (6.10 lbm)** | 4,464 / 2,768 = **1.61** | Above 1.5 target — **VTOL hover achievable from Phase 5** |
| Phase 11 (full + 55 mm rear EDF, ~3,130 g) | **3,130 g (6.90 lbm)** | 4,464 / 3,130 = **1.43** | Rear EDF is forward-thrust only (not summed into hover). Above 1.0 floor, below 1.5 comfort target — keep hover payload light; rear EDF improves cruise/range, not hover. |

Required T/W ≥ **1.5** for stable hover with adequate attitude control margin.
Phase 5–10 nacelle-only configuration meets this requirement at **T/W = 1.61**.

### 12.3 Phase 5–10 VTOL Margin Breakdown

<!-- Sensitivity analysis at Phase 5–10 AUW = 2,768 g, nacelle thrust = 4,464 g. -->

| Scenario | AUW | T/W | Notes |
|---|---|---|---|
| Phase 5 nominal (2,768 g) | 2,768 g | **1.61** | Baseline — VTOL capable |
| With full hover battery (+225 g cargo→hover swap) | 2,993 g | **1.49** | Slightly below 1.5; use cargo battery for initial hover proving |
| With Phase 6 (+4 nodes, ≈ +200 g avionics) | 2,968 g | **1.50** | At target with additional nodes |
| With 12-blade fan upgrade (+320 g thrust) | 2,768 g | (4,464+320)/2,768 = **1.73** | Recommended for confident margin |
| Phase 11 full build (55 mm rear EDF + RCS, ~3,130 g) | 3,130 g | 4,464/3,130 = **1.43** | Rear EDF fires aft (canonical nozzle) — cruise thrust only, no hover lift. RCS jets give pitch/yaw authority. Keep hover payload light to stay ≥1.5. |

### 12.4 Note on POWER_SYSTEM_Q.md §2.3 (Superseded)

<!-- POWER_SYSTEM_Q.md §2.3 used 228 g/EDF "budget" EDFs (Phase 2–6 interim
     hardware) and correctly concluded T/W = 0.48 for those units — they cannot
     achieve VTOL. That conclusion does NOT apply to the XFly Galaxy X5 3200 KV
     specification adopted for Phases 5–10 in this document. POWER_SYSTEM_Q.md
     is archived as a pre-Rev-Q analysis document. -->

POWER_SYSTEM_Q.md §2.3 used 228 g/EDF "budget" EDFs and concluded T/W = 0.48
(cannot achieve VTOL). **That conclusion does not apply** to the XFly Galaxy X5
3200 KV hardware specified for Phases 5–10. POWER_SYSTEM_Q.md is superseded
by this document as of Rev Q (2026-06-07).

---

## 13. ESC Selection

<!-- ============================================================
     ESC SELECTION — Phases 5–10 and Phase 11
     Kaylee board footprints: J_ESC1–J_ESC4 (XT30PW-F, populated);
       J_ESC5 (XT60PW-F, DNP Phases 5–10, populate Phase 11).
     Fuses: F_ESC1–F_ESC4 (40 A mini blade, populated);
       F_ESC5 (100 A MIDI blade, DNP Phases 5–10, see §5.2).
     Governor firmware: governor_config.h
     References: §3.1 Load Analysis, §5 Fuse Coordination.
     ============================================================ -->

### 13.1 ESC Selection by Phase

| Phase | Position | EDF model | ESC model | Rating | Connector | Fuse |
|---|---|---|---|---|---|---|
| Phases 5–10 | Each nacelle EDF (×4) | XFly Galaxy X5 50 mm 12-blade 6S 3200 KV | Generic BLHeli32 60 A 6S | 60 A / 6S | XT30 (30 A cont.) | 40 A mini blade |
| Phase 11 | Rear fuselage 55 mm | 55 mm 6S (~1,500 gf) | Generic BLHeli32 50 A 6S | 50 A / 6S | XT60 | 60 A MIDI blade |

### 13.2 Nacelle ESC Firmware Configuration (All Four Units)

<!-- All four nacelle ESCs (ESC1–ESC4) share identical BLHeli32 programming.
     Governor mode provides closed-loop RPM control with Wash UART2/3 as
     the DSHOT600 command source. INA226 cross-validation catches ESC
     current reporting faults. Settings stored in governor_config.h. -->

All nacelle ESCs (ESC1–ESC4) shall be programmed identically to:

- **Demag compensation:** high
  *(prevents demagnetization stall at high RPM commutation transitions)*
- **BDSHOT telemetry:** enabled
  *(Kaylee INA226 current monitors cross-validate RPM and current data from each ESC)*
- **Governor mode:** closed-loop RPM; setpoint sourced from Wash UART2/3 DSHOT600 frame
  *(each Wash FC cape issues DSHOT600 to its primary ESC; Kaylee INA226 validates
  reported current against actual measured current at the shunt)*
- **Software over-current threshold:** 80 A
  *(set via `governor_config.h` constant `EDF_ESC_OVERCURRENT_A`; mirrors the
  hardware fuse at a lower trip threshold to allow orderly ESC shutdown before
  the 40 A fuse clears)*

### 13.3 Phase 11 ESC5 — Rear Fuselage 55 mm EDF

<!-- ESC5 is DNP (Do Not Populate) for all Phases 5–10.
     When Phase 11 commences, populate J_ESC5 and F_ESC5 on the Kaylee board
     per the Kaylee.md §Phase 11 bring-up procedure.
     Signal routing: Simon's medbay (Bay E, FC4 node), UART1-TX.
     The 55 mm rear EDF is a forward-thrust (cruise) device and also feeds 4 RCS bleed jets
       via proportional valves on the 6 V servo rail (see §3.3). -->

When the 55 mm fuselage EDF is integrated (Phase 11):

1. Populate **J_ESC5** (XT60PW-F footprint on Kaylee, DNP in Phases 5–10)
   with the 50 A BLHeli32 ESC harness.
2. Install **F_ESC5** (60 A MIDI blade fuse, Littelfuse 0299060.ZXNV)
   in the corresponding MIDI fuse holder on Kaylee (see §5.2).
3. Route the ESC5 DSHOT600 signal cable to **Simon's medbay (Bay E, FC4 node),
   UART1-TX** — Simon is the primary EDF5 controller per the PACE task matrix
   in AGENTS.md.
4. Connect the 4 RCS proportional-valve servos to the 6 V servo bus; map to the
   FC attitude mixer (2 pitch + 2 yaw).
5. Re-run Kaylee DRC and verify no connector spacing violations after population.

---

## 14. Weight and Balance

<!-- ============================================================
     WEIGHT AND BALANCE — Power System Components
     CG target: 190 mm aft of nose tip (from build guides).
     Battery rail: ±25 mm adjustable on keel → ±5 mm CG travel.
     Kaylee mass: 278 g installed (PCB + enclosure + hardware).
     AUW reference: Phase 5–10 = ~2,768 g (TODO.md authoritative);
       Phase 11 full build = ~3,130 g (Phase 5–10 + ~360 g 55 mm rear-EDF + RCS system).
     All stations measured from nose tip (Serenity bow) along
       the longitudinal (X) axis, positive aft.
     Imperial primary, metric parenthetical per AGENTS.md.
     ============================================================ -->

### 14.1 CG Target and Battery Adjustability

<!-- The 190 mm station is the aerodynamic neutral-point offset derived from
     the thingiverse reference model geometry (thing:4677565). The keel rail
     provides continuous adjustment; 25 mm travel each side of nominal. -->

- **Longitudinal CG target:** 190 mm (7.48 in) aft of nose tip
- **Battery rail adjustability:** ±25 mm (±0.98 in) on keel rail
- **Resulting CG travel:** ±5 mm (±0.20 in) — sufficient for normal payload variation

### 14.2 Power-System Component CG Contributions

<!-- Moments calculated as: Moment (g·mm) = Mass (g) × Station (mm from nose).
     Subtotal CG = Sum of moments / Sum of mass (excluding Phase 11 DNP items).
     Kaylee 278 g = PCB assembly 198 g + 1.5 mm Al enclosure 60 g + standoffs/hardware 20 g.
     4× nacelle ESCs 220 g total = 55 g each (generic BLHeli32 60 A 6S with heatsink). -->

| Component | Mass (g) | Station (mm from nose) | Moment (g·mm) |
|---|---|---|---|
| 6S 4,000 mAh LiPo (hover battery) | 750 | 190 (adjustable) | 142,500 |
| Kaylee PDB — Phases 5–10 (PCB + enclosure) | 278 | 200 (fixed, keel mid) | 55,600 |
| 4× nacelle ESCs (BLHeli32 60 A 6S, ×4) | 220 | 90 (wing root) | 19,800 |
| 1× rear EDF ESC — Phase 11, DNP (BLHeli32 50 A 6S) | 40 | 490 (aft bay) | 19,600 |
| Keel bonding strap (MIL-B-5087B 19 mm Cu braid) | 35 | 250 | 8,750 |
| **Subtotal — Phases 5–10 (excl. DNP ESC5)** | **1,283** | **CG = (142,500 + 55,600 + 19,800 + 8,750) / 1,243 = 182 mm** | |

<!-- Denominator for CG subtotal is 1,243 g (1,283 g − 40 g DNP ESC5).
     226,650 g·mm / 1,243 g = 182.3 mm → rounds to 182 mm. -->

**Power-system CG at 182 mm (7.17 in) is 8 mm (0.31 in) forward of the 190 mm target.**

Correction: slide battery aft 8 mm on the rail.

```text
ΔCGL ≈ (battery_mass / AUW) × Δbatt_position
     = (750 / 2,768) × 8 mm   ← Phase 5–10 AUW from TODO.md
     ≈ 2.2 mm of forward CG shift per 8 mm slide
```

<!-- The full 8 mm battery slide does not fully resolve the 8 mm CG offset because
     the battery mass (750 g) is a fraction of Phase 5–10 AUW (2,768 g). The remaining
     ~6 mm offset shall be balanced by aft servo/wiring mass placement during final
     assembly. Use the CG sensitivity formula below to calculate additional trim
     adjustments. Phase 11 AUW (3,130 g) reduces sensitivity constant to 0.240. -->

Balance the remaining ~6 mm offset by placement of aft servo wiring and mounting
hardware. Verify on the physical CG rig before first flight.

### 14.3 Battery CG Sensitivity

<!-- Formula: ΔCG ≈ (battery_mass / AUW) × Δbatt_position
     Phase 5–10 AUW = 2,768 g (TODO.md authoritative). Phase 11 AUW = 3,130 g.
     Hover battery sensitivity constant = 750 / 2,768 = 0.271 (Phase 5–10).
     Cargo battery (525 g) sensitivity = 525 / 2,568 = 0.204 (Phase 5, no hover batt.).
     This is a first-order approximation; use full moment table for precise trim. -->

Phase 5–10 hover battery sensitivity (750 g, AUW 2,768 g):

```text
ΔCG ≈ (750 / 2,768) × Δbatt_position
    = 0.271 × Δ mm per mm of battery slide
```

Phase 5–10 cargo battery sensitivity (525 g, AUW ~2,543 g):

```text
ΔCG ≈ (525 / 2,543) × Δbatt_position
    = 0.206 × Δ mm per mm of battery slide
```

Phase 11 full build hover battery sensitivity (750 g, AUW 3,130 g):

```text
ΔCG ≈ (750 / 3,130) × Δbatt_position
    = 0.240 × Δ mm per mm of battery slide
```

The hover battery at Phase 5 is **13 % more CG-sensitive** than at Phase 11 full
build — use fine (5 mm) increments when trimming with the minimum-viable build.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
