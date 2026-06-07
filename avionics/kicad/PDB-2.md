# PDB-2 — Power Distribution Board Rev A

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** A
**Date:** 2026-06-07
**Status:** Schematic complete — PCB layout pending DRC sign-off

---

## Purpose

PDB-2 replaces the generic off-the-shelf dual-BEC PDB-BEC module with a custom
four-layer PCB sized for the Serenity UAV power architecture. It provides:

- Coordinated multi-level fusing (main bus + per-ESC branch fuses)
- **Per-EDF independent power isolation**: each EDF output is electrically decoupled
  so that a stall or blown fuse on one EDF cannot collapse the supply to any other
  EDF, including the partner EDF in the same nacelle
- **Separated FC signal paths**: the forward EDF and aft EDF in each nacelle are
  commanded by different FC nodes — a single FC node failure cannot silence both
  EDFs in any nacelle
- Per-output current sensing via INA226 (reported over I2C to FC1 / Bay A)
- Per-cell battery monitoring via BQ76930 (6S balance lead input)
- Hardware-level battery protection FETs driven by BQ76930
- Dual redundant 5 V / 10 A SMPS (diode-OR'd) for avionics bus
- 6 V / 5 A SMPS for servo bus
- EMI suppression on main bus and all BEC outputs
- **Shield ground connection on every connector** (chassis ground pad or shielded
  JST-GH MP pin at each output)
- **All power cables twisted pair with per-output CM choke** and snap-on ferrites
  at both cable ends

Full electrical design rationale is documented in `docs/POWER_DISTRIBUTION.md`.

---

## Board Specification

| Parameter | Value |
|-----------|-------|
| Board size | 90 × 65 mm |
| Layers | 4 (F.Cu signal, In1.Cu GND plane, In2.Cu VBAT power plane, B.Cu signal) |
| Copper weight | 4 oz (140 µm) on F.Cu / In2.Cu (main power); 1 oz (35 µm) on In1.Cu / B.Cu (signal / GND) |
| Min trace width | 0.20 mm (signal); ≥ 6 mm pour (ESC outputs) |
| Min clearance | 0.15 mm (signal); 3 mm between VBAT and GND pours |
| Surface finish | ENIG (gold) |
| Solder mask | Green |
| Max operating temp | 85 °C |
| PCB material | FR-4 TG170 |
| Fab notes | Order through JLCPCB or PCBWay; request 4-oz copper inner planes; no V-score |

---

## Connectors

All connectors carry a shield ground connection.  Power connectors use an M3
threaded brass insert adjacent to the connector body for cable braid/drain-wire
termination.  Signal connectors use a PGND via-pad within 3 mm of the connector
for shield drain wire attachment.  See Harness Specification for cable construction
requirements.

### Input

| Reference | Part | Function |
|-----------|------|---------|
| J_BATT | Amass XT60PW-F (PCB-mount XT60 female) | 6S LiPo main positive + negative |
| J_BAL | JST XH-7P 2.54 mm male right-angle | 6S balance lead (7 wires: BAL_GND + B1–B6) |
| J_PGND_BATT | M3 × 6 mm PCB-mount threaded brass insert (adjacent to J_BATT) | Battery cable braid/foil shield drain → chassis PGND |

### ESC Outputs

| Reference | Part | Current rating | EDF served |
|-----------|------|---------------|-----------|
| J_ESC1 | Amass XT30PW-F (PCB-mount XT30 female) | 30 A continuous / 60 A burst | Port Fwd (EDF0) |
| J_ESC2 | Amass XT30PW-F | 30 A continuous / 60 A burst | Port Aft  (EDF1) |
| J_ESC3 | Amass XT30PW-F | 30 A continuous / 60 A burst | Stbd Fwd  (EDF2) |
| J_ESC4 | Amass XT30PW-F | 30 A continuous / 60 A burst | Stbd Aft  (EDF3) |
| J_ESC5 | DNP (Amass XT60PW-F footprint, unpopulated Phase 5–10) | 80 A / 110 A | Fuse 120 mm (EDF4, Phase 11) |
| J_SHLD_ESC1–4 | M3 × 6 mm PCB-mount threaded brass insert (×4, one adjacent to each J_ESCn) | ESC cable braid/foil shield drain → chassis PGND |
| J_SHLD_ESC5 | M3 × 6 mm PCB-mount threaded brass insert (DNP, adjacent to J_ESC5 footprint) | Phase 11 ESC5 cable shield drain (unpopulated) |

### BEC Outputs

| Reference | Part | Rail | Consumers |
|-----------|------|------|-----------|
| J_5V | Molex Nano-Fit 4-pin (pitch 2.50 mm) | 5 V / 10 A (dual SMPS) | Avionics bus to all 4 bays |
| J_6V | Molex Nano-Fit 4-pin (pitch 2.50 mm) | 6 V / 5 A | Servo bus (tilt servos + nozzle servos) |
| J_SHLD_5V | PGND via-pad 1.2 mm hole (adjacent to J_5V) | 5 V avionics cable shield drain → PGND plane |
| J_SHLD_6V | PGND via-pad 1.2 mm hole (adjacent to J_6V) | 6 V servo cable shield drain → PGND plane |

### Monitoring / Comms

All monitoring cables use shielded twisted-pair construction (see Harness Specification).
The cable shield terminates at the adjacent PGND drain pad at the PDB-2 end; at the
Cape-A-2 end the drain wire connects to the cape chassis GND point.

| Reference | Part | Function |
|-----------|------|---------|
| J_I2C | JST-GH SM04B-GHS-TB(LF)(SN), 4-pin 1.25 mm (GND, +5 V, SCL, SDA) | PDB I2C bus to Cape-A-2 J_EXT_I2C (Bay A FC1); shielded cable required |
| J_ALERT | JST-GH SM02B-GHS-TB(LF)(SN), 2-pin 1.25 mm (GND, ALERT_N) | BQ76930 open-drain alert to Cape-A-2 GPIO; shielded cable required |
| J_NTC | JST-GH SM02B-GHS-TB(LF)(SN), 2-pin 1.25 mm (NTC+, NTC−) | External battery NTC thermistor (10 kΩ, on battery strap); shielded cable required |
| J_SHLD_I2C | PGND via-pad 1.2 mm hole (adjacent to J_I2C) | I2C cable shield drain → PGND plane |
| J_SHLD_ALERT | PGND via-pad 1.2 mm hole (adjacent to J_ALERT) | ALERT cable shield drain → PGND plane |
| J_SHLD_NTC | PGND via-pad 1.2 mm hole (adjacent to J_NTC) | NTC cable shield drain → PGND plane |

---

## Schematic Description

### Main Bus Path

```
J_BATT(+) ──── CM1 (common-mode choke) ──── F1 (150 A MAXI fuse) ──── VBAT rail
J_BATT(−) ──── CM1 ──────────────────────────────────────────────────── PGND rail

VBAT rail:
  │
  ├── C1, C2: 220 µF / 35 V (bulk stiffening)
  ├── C3: 100 nF X7R (HF bypass)
  ├── D1: SMBJ33CA (bidirectional TVS, 33 V / 53.3 V clamp)
  │
  ├── Q_BATT_DSG (AON6556 N-MOSFET, 60 V, 30 A): drain=VBAT, source=VDIS
  │     gate driven by BQ76930 DSG pin (hardware disconnect on SCD/OCD)
  │
  └── VDIS rail:
        ├── U_IS_MAIN (INA226, addr 0x44): shunt RS_MAIN (1 mΩ, 5 W) → VBAT_SENSE
        ├── F_ESC1 → J_ESC1 (ESC1 branch, see below)
        ├── F_ESC2 → J_ESC2
        ├── F_ESC3 → J_ESC3
        ├── F_ESC4 → J_ESC4
        ├── F_ESC5 → J_ESC5 (DNP, Phase 11)
        ├── 5 V BEC section (see below)
        └── 6 V BEC section (see below)
```

### ESC Branch (× 4, identical)

Three isolation layers prevent a stalled or blown-fuse EDF from collapsing the supply
to any other EDF, including the partner EDF sharing the same nacelle:

- **Layer 1 — F_ESCn (branch fuse):** Disconnects a faulted output at > 40 A; clears
  before the 150 A main bus fuse responds (selective coordination maintained).
- **Layer 2 — C_DECn (local bulk capacitor):** 470 µF low-ESR electrolytic placed between
  the fuse output and the CM choke input. Absorbs stall-induced voltage transients locally;
  prevents VDIS rail sag from propagating to adjacent ESC branches.
- **Layer 3 — CM_ESCn (per-output CM choke):** Common-mode choke on each ESC output blocks
  ESC PWM switching noise and ringing from coupling back into the VDIS rail or into adjacent
  ESC current monitors (INA226 measurement integrity preserved at full throttle).

```
VDIS ──── F_ESCn (40 A mini blade fuse, automotive housing) ──────────────────────
                │
         C_DECn (Panasonic EEUFC1V471, 470 µF / 35 V, low-ESR electrolytic)
                │             ← stall transient absorbed here; VDIS rail sag isolated
         CM_ESCn (Würth 7440640500, 10 A, 2 × 100 µH CMC)
                │             ← ESC PWM switching noise blocked from VDIS / adjacent branches
         RS_n (Bourns CSS2H-2512K-1L00F, 1 mΩ, 3 W, 4-terminal Kelvin)
                │                          │
         J_ESCn(+) [Amass XT30PW-F]   U_IS_n (INA226AIDGSR, addr 0x40–0x43)
         (twisted-pair shielded cable)     Vin+ → RS_n Kelvin+
                                           Vin- → RS_n Kelvin-
                                           Vbus → RS_n output side (bus voltage ref)
                                           SDA/SCL → J_I2C PDB bus
J_SHLD_ESCn (M3 chassis ground lug pad, adjacent to J_ESCn) ← cable shield drain wire
J_ESCn(−) ──── PGND (power return — GND shared, no shunt)
```

### 5 V BEC (Dual Redundant)

```
VDIS ──── FB_5V1 (Würth 742792612, 10 µH, 2 A) ──── BEC5V_1 section
                  │
           C_BEC1_IN (100 µF / 50 V)
                  │
           U_BEC_5V_1 (Texas Instruments TPS54620RGYT, adjustable, 6 A)
             R_FB1 divider: Vout = 5.0 V
             C_BEC1_OUT (220 µF + 100 nF)
                  │
                  ├── D_OR1 (MBRD1045CT cathode, Schottky 10 A / 45 V)
                  │
VDIS ──── FB_5V2 ──── U_BEC_5V_2 (TPS54620RGYT, identical) ──── D_OR2
                                                                      │
                                                                5V_AVIONICS rail
                                                                   │
                                                               J_5V (+/−)
```

If U_BEC_5V_1 fails (output collapses), D_OR1 reverse-biases; U_BEC_5V_2 continues
carrying full load via D_OR2. The Schottky forward drop (~0.3 V at 10 A) is absorbed
by the 5.3 V set-point (TPS54620 output adjusted to 5.3 V so rail arrives at 5.0 V
after diode drop).

### 6 V BEC

```
VDIS ──── FB_6V (Würth 742792612, 10 µH, 2 A) ────
               │
          C_BEC_SV_IN (100 µF / 50 V)
               │
          U_BEC_6V (Texas Instruments TPS54540DDAR, 40 V / 5 A adjustable)
            R_FB: Vout = 6.0 V ± 1 %
            C_BEC_SV_OUT (100 µF + 100 nF)
               │
           J_6V (+/−)
```

### BQ76930 Cell Monitor

```
J_BAL pins (BAL_GND, B1–B6) ──► BQ76930 (VC0–VC6, BAL_GND)
J_NTC ──────────────────────────► BQ76930 TS1 input (10 kΩ NTC)

BQ76930:
  SDA/SCL ──────────────────────► J_I2C (shared with INA226 devices)
  ALERT_N ──────────────────────► J_ALERT (open-drain, 2.2 kΩ pull-up to 5 V)
  DSG ──────────────────────────► Q_BATT_DSG gate (via 10 kΩ gate resistor)
  CHG ──────────────────────────► Q_BATT_CHG gate (future / DNP)
  BAT+ ─────────────────────────► VBAT (voltage reference for pack measurement)
  REGSRC ───────────────────────► VBAT (device supply input, internal 3.3 V LDO)
  CAP ──────────────────────────► 4.7 µF to REGSRC (boot capacitor)
```

---

## ESC Control and Telemetry Signal Routing

Each nacelle contains two EDFs in tandem.  Power for both EDFs in a nacelle comes from
the PDB-2, but the ESC control (DSHOT600) and telemetry (BDSHOT) signal paths are routed
to **separate** FC nodes.  A single FC node failure therefore cannot silence both EDFs in
any nacelle — thrust and directional control are degraded but not lost.

### FC Assignment Table

| EDF position | ESC ref | PDB-2 power conn | Controlling FC node | Cape-A-2 bay | Signal pin |
|---|---|---|---|---|---|
| Port Fwd (EDF0) | ESC1 | J_ESC1 | FC1 (Node 1) | Bay A | UART2-TX (DSHOT600) |
| Port Aft (EDF1) | ESC2 | J_ESC2 | FC2 (Node 2) | Bay B | UART2-TX (DSHOT600) |
| Stbd Fwd (EDF2) | ESC3 | J_ESC3 | FC2 (Node 2) | Bay B | UART3-TX (DSHOT600) |
| Stbd Aft (EDF3) | ESC4 | J_ESC4 | FC3 (Node 3) | Bay C | UART2-TX (DSHOT600) |

### Single-FC-Node Failure Matrix

| Failed node | EDFs lost | EDFs retained | Flight implication |
|---|---|---|---|
| FC1 only | Port Fwd (EDF0) | Port Aft, both Stbd (3/4) | Degraded port nacelle thrust; controllable; continue or RTH |
| FC2 only | Port Aft (EDF1) + Stbd Fwd (EDF2) | Port Fwd, Stbd Aft (2/4) | Symmetric diagonal pair retained; yaw authority maintained; RTH recommended |
| FC3 only | Stbd Aft (EDF3) | Port Fwd, Port Aft, Stbd Fwd (3/4) | Degraded stbd nacelle thrust; controllable; continue or RTH |

No single FC node failure eliminates both EDFs in any nacelle.

### Signal Cable Independence

DSHOT600 / BDSHOT signal cables are routed completely independently of the PDB-2 power
cables.  Each ESC signal connector (JST-SH 3-pin: DSHOT+, GND, TELEM) connects directly
to the controlling FC node's Cape-A-2 via a dedicated shielded twisted-pair cable that
passes through a separate cable gland from the corresponding power cable.  This separation
prevents conducted EMI on the high-current power cable from corrupting the DSHOT frame.

---

## Bill of Materials (Delta vs Generic PDB-BEC)

### Removed from BOM

| Was | Notes |
|-----|-------|
| PDB-BEC (generic dual-BEC PDB from AliExpress) | Replaced by PDB-2 |

### Added to BOM

| Reference | Part | Function | DigiKey / Supplier |
|-----------|------|----------|--------------------|
| U_BEC_5V_1, U_BEC_5V_2 | TPS54620RGYT | 6 A / 28 V sync buck (5 V output) | 296-25672-1-ND |
| U_BEC_6V | TPS54540DDAR | 5 A / 40 V buck (6 V output) | 296-TPS54540DDARCT-ND |
| U_IS_MAIN | INA226AIDGSR | Main bus current/voltage monitor (0x44) | 296-29942-1-ND |
| U_IS1–U_IS4 | INA226AIDGSR (×4) | Per-ESC current monitor (0x40–0x43) | 296-29942-1-ND |
| U_CELL | BQ76930PWRQ1 | 6S cell-level monitor + hardware protection | 296-BQ76930PWRQ1CT-ND |
| Q_BATT_DSG | AON6556 (N-MOSFET 60 V / 30 A) | Battery disconnect FET (DSG path) | 785-AON6556CT-ND |
| D_OR1, D_OR2 | MBRD1045CT (Dual Schottky 10 A / 45 V) | BEC OR-diode pair | 863-MBRD1045CTCT-ND |
| F1 | Littelfuse 0297150.ZXNV (150 A MAXI blade) | Main bus fuse | 576-0297150.ZXNV-ND |
| F_ESC1–F_ESC4 | Littelfuse 0297040.WXNV (40 A mini blade, ×4) | Per-ESC branch fuse | 576-0297040.WXNV-ND |
| F_ESC5 | DNP (footprint: Littelfuse MIDI 100 A) | Phase 11 aft EDF fuse (unpopulated) | — |
| RS_MAIN | Bourns CSS2H-2512K-1L00F (1 mΩ, 3 W, Kelvin 2512) | Main bus shunt | SRR2H-5-ND |
| RS1–RS4 | Bourns CSS2H-2512K-1L00F (1 mΩ, 3 W, ×4) | Per-ESC shunt | SRR2H-5-ND |
| CM1 | Würth 7440640500 (10 A, 2×100 µH CMC) | Input CM choke (battery lead) | 732-7440640500-ND |
| D1 | SMBJ33CA (33 V / 400 W bidirectional TVS, SMB package) | Main bus TVS clamp | 576-SMBJ33CACT-ND |
| C1, C2 | Panasonic EEF-CX1V221R (220 µF / 35 V, D10×12.5 radial) | Bulk stiffening capacitors | P12380-ND |
| C3 | 100 nF X7R 0805 MLCC / 50 V | HF bypass (main bus) | |
| C_NTC | 100 nF X7R 0805 MLCC | BQ76930 TS1 filter capacitor | |
| J_BATT | Amass XT60PW-F (PCB-mount XT60 female) | Battery input | AliExpress / GetFPV |
| J_BAL | JST XH-7P, 2.54 mm, right-angle through-hole | 6S balance lead | B07X6JCRZS (Amazon) |
| J_ESC1–J_ESC4 | Amass XT30PW-F (PCB-mount XT30 female, ×4) | ESC power outputs | AliExpress |
| J_ESC5 | DNP (XT60PW-F footprint) | Phase 11 aft EDF output | — |
| J_5V | Molex Nano-Fit 4-pin (2.50 mm, RA) | 5 V avionics bus output | WM1720-ND |
| J_6V | Molex Nano-Fit 4-pin (2.50 mm, RA) | 6 V servo bus output | WM1720-ND |
| J_I2C | JST-GH SM04B-GHS-TB(LF)(SN) 4-pin, 1.25 mm | PDB I2C to Cape-A-2; shielded cable, drain to J_SHLD_I2C | Mouser 440-SM04B-GHS-TB |
| J_ALERT | JST-GH SM02B-GHS-TB(LF)(SN) 2-pin, 1.25 mm | BQ76930 ALERT output; shielded cable, drain to J_SHLD_ALERT | Mouser 440-SM02B-GHS-TB |
| J_NTC | JST-GH SM02B-GHS-TB(LF)(SN) 2-pin, 1.25 mm | Battery NTC thermistor input; shielded cable, drain to J_SHLD_NTC | Mouser 440-SM02B-GHS-TB |
| R_ALERT | 2.2 kΩ 0402 | ALERT pull-up to 5 V | |
| R_DSG_G | 10 kΩ 0402 | DSG gate resistor (AON6556) | |
| R_FB1_1, R_FB1_2 | Resistors for 5.3 V set-point on TPS54620 #1 | See TPS54620 datasheet Table 2 | |
| R_FB2_1, R_FB2_2 | Resistors for 5.3 V set-point on TPS54620 #2 | See TPS54620 datasheet Table 2 | |
| R_FB6_1, R_FB6_2 | Resistors for 6.0 V set-point on TPS54540 | See TPS54540 datasheet Table 2 | |
| L1, L2 | 10 µH power inductor (Würth 744314100 or equiv, ≥ 6 A Isat) | TPS54620 switching inductors | |
| L3 | 10 µH power inductor (Würth 744314100 or equiv, ≥ 6 A Isat) | TPS54540 switching inductor | |
| FB_5V1, FB_5V2 | Würth 742792612 (600 Ω @ 100 MHz, 2 A) | 5 V BEC input ferrite beads | 732-742792612-ND |
| FB_6V | Würth 742792612 | 6 V BEC input ferrite bead | 732-742792612-ND |
| C_DEC1–C_DEC4 | Panasonic EEUFC1V471 (470 µF / 35 V, D10 × 20 mm, low-ESR radial, ×4) | Per-ESC output bulk decoupling (Layer 2 stall isolation) | P10349TB-ND |
| CM_ESC1–CM_ESC4 | Würth 7440640500 (10 A, 2 × 100 µH CMC, through-hole, ×4) | Per-ESC output CM choke (Layer 3 noise isolation) | 732-7440640500-ND |
| J_PGND_BATT | M3 × 6 mm PCB-mount threaded brass insert + M3 ring terminal lug (×1) | Battery cable shield/braid drain → chassis PGND | McMaster-Carr 94459A120 |
| J_SHLD_ESC1–4 | M3 × 6 mm PCB-mount threaded brass insert + M3 ring terminal lug (×4) | Per-ESC cable shield/braid drain → chassis PGND | McMaster-Carr 94459A120 |
| J_SHLD_ESC5 | M3 × 6 mm PCB-mount threaded brass insert (DNP; Phase 11) | Phase 11 ESC5 cable shield drain (unpopulated) | McMaster-Carr 94459A120 |
| FERRITE-PWR | Würth 7427122 (25 mm ID, 31 Ω @ 25 MHz, ×14) | Snap-on ferrite chokes for power cables: 2 per cable end (J_BATT + J_ESC1–4 + J_5V + J_6V) | 732-7427122-ND |
| FERRITE-SIG | Würth 7427120 (7 mm ID, 80 Ω @ 25 MHz, ×6) | Snap-on ferrite chokes for signal cables: 2 per cable end (J_I2C + J_ALERT + J_NTC) | 732-7427120-ND |

---

## INA226 Address Assignment

| Device | Location | A0 | A1 | I2C Address | Full-Scale Current |
|--------|----------|----|----|-------------|-------------------|
| U_IS1 | ESC1 output | GND | GND | 0x40 | 60 A |
| U_IS2 | ESC2 output | VCC | GND | 0x41 | 60 A |
| U_IS3 | ESC3 output | SDA | GND | 0x42 | 60 A |
| U_IS4 | ESC4 output | SCL | GND | 0x43 | 60 A |
| U_IS_MAIN | Main bus | GND | VCC | 0x44 | 75 A |

The PDB-2 I2C bus (J_I2C) connects to Cape-A-2 Bay A (FC1) on J_EXT_I2C.
These addresses reside on a separate physical I2C bus segment from the Cape-A-2
internal INA226 (0x40 on the Cape's own I2C-0 bus). No address conflict.

The BQ76930 at 0x08 shares this same J_I2C bus segment. Total devices: 6.
All operate at 400 kHz (Fast Mode). Pull-ups: 4.7 kΩ to 5 V at J_I2C host end.

---

## INA226 Calibration Register Values

The INA226 calibration register (0x05) sets the current-measurement scale.

```
CAL = floor(0.00512 / (CURRENT_LSB × R_shunt_Ω))
where CURRENT_LSB = I_max / 32768
```

| Device | R_shunt (Ω) | I_max (A) | CURRENT_LSB (mA) | CAL value |
|--------|-------------|----------|-----------------|-----------|
| U_IS1–IS4 | 0.001 | 60 | 1.831 | 2796 (0x0AEC) |
| U_IS_MAIN | 0.001 | 75 | 2.289 | 2237 (0x08BB) |

Write CAL to register 0x05 during INA226 initialisation. The firmware function
`bmon_ina226_configure_shunt()` performs this write. After configuration, the
current register (0x04) returns signed current in units of CURRENT_LSB.

---

## BQ76930 Configuration

On start-up, the `cell_mon_bq769x0` driver writes the following registers:

| Register | Address | Value | Purpose |
|----------|---------|-------|---------|
| CC_CFG | 0x0B | 0x19 | Required by TI (always write 0x19) |
| SYS_CTRL1 | 0x04 | 0x18 | ADC_EN=1, TEMP_SEL=1 (thermistor mode) |
| SYS_CTRL2 | 0x05 | 0x40 | CC_EN=1 (coulomb counter on) |
| PROTECT1 | 0x06 | 0xA9 | RSNS=1 (18 mΩ sense); SCD: 200 µs delay, 150 A threshold |
| PROTECT2 | 0x07 | 0x05 | OCD: 640 ms delay, ~50 A threshold |
| PROTECT3 | 0x08 | 0x40 | OV delay = 2 s, UV delay = 4 s |
| OV_TRIP | 0x09 | 0xAB | OVP threshold ≈ 4.20 V per cell |
| UV_TRIP | 0x0A | 0x96 | UVP threshold ≈ 3.00 V per cell |

### OV_TRIP / UV_TRIP Calculation

```
OV_TRIP register = floor((V_OV / GAIN − OFFSET) / 16)
UV_TRIP register = floor((V_UV / GAIN − OFFSET) / 16)
```

Using datasheet defaults (before calibration):
- GAIN ≈ 380 µV/LSB, OFFSET = 0 mV
- V_OV = 4.20 V: OV_TRIP = floor(4200000 / (380 × 4 × 16)) = floor(4200000 / 24320) = 172 = 0xAC ≈ 0xAB
- V_UV = 3.00 V: UV_TRIP = floor(3000000 / 24320) = floor(123.4) = 123 = 0x7B

The driver reads GAIN (register 0x50) and OFFSET (register 0x51) from the device
and recomputes OV_TRIP and UV_TRIP using the actual trimmed calibration values.

---

## Power Budget

| Rail | Consumers | Max output current |
|------|-----------|-------------------|
| VBAT main bus | 4× ESC outputs | Up to 4 × 40 A = 160 A burst |
| 5 V avionics (dual BEC) | 8× PocketBeagle 2 + 4× Cape-A-2 + 4× Cape-B-2 + accessories | 10 A cont. (dual SMPS) |
| 6 V servo | 2× DS3218MG tilt + 3× SG90 (nozzle/cargo) | 5 A cont. |
| BQ76930 self | Internal LDO from REGSRC | < 100 µA quiescent |

Total VBAT draw (avionics + servos at peak, from VBAT side):
- 5 V @ 10 A → 10 × 5 / (22.2 × 0.92 BEC efficiency) ≈ **2.4 A at VBAT**
- 6 V @ 5 A → 5 × 6 / (22.2 × 0.92) ≈ **1.5 A at VBAT**
- ESC outputs (hover): ~72 A
- **Total continuous hover: ~76 A at VBAT** ← well within 150 A fuse rating and battery capacity.

---

## EMC Compliance Targets

| Standard | Level | Test | Mitigation |
|----------|-------|------|-----------|
| IEC 61000-4-5 | Level 3 (±2 kV CM, ±1 kV DM) | Surge on VBAT | D1 SMBJ33CA TVS + bulk caps |
| IEC 61000-4-2 | Level 4 (±8 kV contact) | ESD on connectors | D1 TVS at J_BATT; XT30/XT60 are shrouded |
| MIL-STD-461G CE102 | Limit B (conducted emission, power leads) | Conducted emission | CM1 input choke + π-filter on each BEC |
| MIL-STD-461G CS101 | 50 V 30 Hz–150 kHz | Power bus susceptibility | 2× 220 µF bulk + BEC regulation |

Pre-compliance testing against CE102 and CS101 at system level is required
before first flight. Full MIL-STD-461G testing is deferred pending airframe integration.

---

## Harness Specification

All cables leaving the PDB-2 must comply with the construction rules below.  The
500 W/m² EMI design environment mandates shielded twisted-pair construction with
continuous braid coverage and snap-on ferrite treatment at both cable ends.  All
wire insulation must be silicone-rated (200 °C continuous) for propulsion cables
and PVC/PTFE acceptable for signal cables.

### Power Cables (J_BATT, J_ESC1–4)

| Parameter | Specification |
|---|---|
| Conductor gauge | 4 AWG silicone (J_BATT main bus, 200 mm max); 10 AWG silicone (J_ESCn branches, 300 mm max) |
| Construction | Twisted pair (+/−), ≥ 4 twists per 10 cm, 95 % optical-coverage spiral braid shield |
| Shield termination | Both ends: braid drain wire (18 AWG) to M3 ring terminal at J_PGND_BATT or J_SHLD_ESCn chassis lug |
| On-board CM choke | CM1 (Würth 7440640500) at main bus input; CM_ESCn (7440640500) per ESC output — these replace the cable-end choke for the board-side termination |
| Snap-on ferrites | Würth 7427122 (25 mm ID, 31 Ω @ 25 MHz): one snap-on at each cable end (2 per cable) |
| Connector (cable side) | Amass XT30PW-M male (J_ESCn); XT60 pig-tail (J_BATT) — solder cup termination only, no crimps on > 12 AWG |

### 5 V Avionics Bus Cable (J_5V)

| Parameter | Specification |
|---|---|
| Conductor gauge | 16 AWG silicone (2 conductors per polarity, paralleled for 10 A total) |
| Construction | Twisted pair (+/−), 85 % coverage spiral braid shield |
| Shield termination | Drain wire to J_SHLD_5V PGND via-pad at PDB-2 end; chassis GND lug at avionics bay entry point |
| Snap-on ferrites | Würth 7427122 at both cable ends |
| Connector (cable side) | Molex Nano-Fit 4-pin cable-side plug (mates with J_5V on PDB-2) |

### 6 V Servo Bus Cable (J_6V)

| Parameter | Specification |
|---|---|
| Conductor gauge | 18 AWG silicone |
| Construction | Twisted pair (+/−), 85 % coverage spiral braid shield |
| Shield termination | Drain wire to J_SHLD_6V PGND via-pad at PDB-2 end; chassis GND lug at servo harness entry |
| Snap-on ferrites | Würth 7427122 at both cable ends |
| Connector (cable side) | Molex Nano-Fit 4-pin cable-side plug (mates with J_6V on PDB-2) |

### I2C and Signal Cables (J_I2C, J_ALERT, J_NTC)

| Parameter | Specification |
|---|---|
| Conductor gauge | 28 AWG stranded silver-plated copper (2 twisted pairs for J_I2C: SCL/SDA + GND/5 V; single pair for J_ALERT, J_NTC) |
| Construction | Individually shielded twisted pairs (Belden 9501 or equivalent); overall foil + braid shield |
| Shield termination | Drain wire to J_SHLD_I2C / J_SHLD_ALERT / J_SHLD_NTC PGND via-pad at PDB-2 end; chassis GND at cape end; shield grounded at PDB-2 end only (single-end grounding prevents ground loop at 400 kHz) |
| Snap-on ferrites | Würth 7427120 (7 mm ID, 80 Ω @ 25 MHz): one at each cable end |
| Cable length | J_I2C: ≤ 150 mm (I2C bus capacitance budget ≤ 400 pF total at 400 kHz); J_ALERT / J_NTC: ≤ 300 mm |
| Connector (cable side) | JST GHR-04V-S (4-pin, mates with J_I2C); JST GHR-02V-S (2-pin, mates with J_ALERT / J_NTC) |

### ESC Signal Cables (ESC1–4 DSHOT/BDSHOT, not on PDB-2)

ESC signal cables route directly between each ESC and its controlling FC node and do
not connect to the PDB-2.  They are documented here for completeness.

| Parameter | Specification |
|---|---|
| Conductor gauge | 28 AWG stranded |
| Construction | Shielded twisted pair (DSHOT+ and GND as pair; TELEM as third conductor) |
| Shield termination | Chassis GND at ESC end; chassis GND at Cape-A-2 end |
| Snap-on ferrites | Würth 7427120 at both cable ends |
| Cable routing | Separate cable gland / pass-through from the corresponding power cable for that ESC |

---

## PCB Layout Constraints

- **Power pours:** In2.Cu carries VBAT. Pour width ≥ 12 mm under all high-current
  paths (J_BATT to F1, F1 to ESC fuse holders, ESC fuse holders to J_ESCn).
- **GND return:** In1.Cu is full-plane PGND. All GND vias stitch through at ≤ 5 mm
  spacing in high-current areas.
- **Kelvin shunt connections:** Each 4-terminal shunt resistor must be wired with
  Kelvin force and sense pairs on separate traces/vias — do not share via with current
  path. Sense traces (INA226 IN+ / IN−) must be ≥ 0.3 mm trace on signal layer,
  routed away from power planes.
- **BQ76930 isolation:** Maintain ≥ 8 mm creepage between individual VC_n cell
  terminals (each at different potentials). Balance resistors (100 Ω in series with
  each balance wire) on J_BAL between the PCB balance-sense pads and VC_n pins
  to limit imbalance currents.
- **INA226 bypass:** 100 nF + 10 nF at each INA226 VCC pin (0402, within 0.5 mm).
- **TVS D1 placement:** Within 10 mm of J_BATT positive pin. GND return via ≥ 3 ×
  0.4 mm vias to In1.Cu PGND plane.
- **BEC switching noise:** TPS54620 and TPS54540 switching nodes (SW pin) must be
  enclosed in a copper keepout from the GND pour (prevent CM noise injection). Place
  bootstrap capacitor (C_BOOT) within 1 mm of BST pin.
- **Thermal vias:** Place ≥ 6 × 0.3 mm vias under the TPS54620 PowerPAD exposed
  pad (thermal relief) to In2.Cu; add thermal copper pour on B.Cu under each SMPS.
- **Chassis ground lugs (J_PGND_BATT, J_SHLD_ESC1–4):** Place M3 threaded insert
  footprints within 8 mm of their associated power connector. Each lug pad must
  have ≥ 4 × 0.4 mm vias to In1.Cu PGND plane. Include a 3 mm copper flood
  connecting the via cluster to the nearest GND pour edge.
- **Shield drain via-pads (J_SHLD_5V, J_SHLD_6V, J_SHLD_I2C, J_SHLD_ALERT,
  J_SHLD_NTC):** Single 1.2 mm drilled / 2.0 mm annular via-pad within 5 mm of the
  associated connector, stitched to In1.Cu PGND plane. Label each pad in the
  F.Silkscreen layer.

---

## Phase 11 ESC5 Population

When Phase 11 is ready, populate the following DNP components on the PDB-2:

1. J_ESC5 (XT60PW-F PCB-mount female)
2. F_ESC5 (100 A MIDI blade fuse, Littelfuse 0299100.ZXNV, MIDI holder)
3. RS5 (1 mΩ / 5 W shunt — use TLRH10100R001FE for higher power rating)
4. U_IS5 (INA226AIDGSR, solder to DNP footprint, I2C address 0x45)
5. Wire J_ESC5(−) via 8 AWG return to PGND bar

Update firmware: add ESC5 (EDF_ID_FUSE) to the pwr_fault poll list
and set INA226 address 0x45 in the ESC5 monitor context.

---

## Estimated Mass

| Component | Mass (g) |
|-----------|---------|
| PCB bare (90 × 65 mm, 4-layer FR-4) | ~32 |
| Connectors (all, including M3 chassis lugs × 5) | ~24 |
| Fuse holders + fuses | ~15 |
| INA226 × 5 | ~1 |
| BQ76930 | ~1 |
| TPS54620 × 2 + TPS54540 | ~3 |
| Passives (caps, inductors, resistors) | ~8 |
| Shunt resistors × 5 | ~5 |
| Mosfet Q_BATT_DSG | ~1 |
| C_DEC1–C_DEC4 (470 µF electrolytic × 4, D10 × 20 mm) | ~16 |
| CM_ESC1–CM_ESC4 (Würth 7440640500 CMC × 4) | ~40 |
| **Total (Phases 5–10)** | **~146 g** |

Compare to generic PDB-BEC at 40 g — additional 106 g for full monitoring, hardware
protection, redundant BEC, per-EDF decoupling, and per-output CM filtering. The mass
increase is dominated by the four per-ESC CM chokes (~10 g each); this is a deliberate
trade for 500 W/m² EMI immunity. Well within mass budget.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
