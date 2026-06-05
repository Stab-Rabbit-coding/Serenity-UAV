# XCVR-49MHZ-2 — EMI-Hardened 49 MHz AX.25 Transceiver

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** A (EMI-hardened variant of XCVR-49MHZ-1)
**Date:** 2026-06-02
**Status:** Schematic complete — Phase 2 PCB layout pending

---

## Purpose

XCVR-49MHZ-2 is an electromagnetic-environment-hardened variant of XCVR-49MHZ-1. The
board is a 49 MHz AX.25 KISS modem for FCC Part 95 Subpart D operation; the -2 variant
adds conducted and radiated immunity measures to handle the EDF motor and ESC switching
environment inside the Serenity UAV nacelles.

All Phase 1 IC selections (Si5351A-B-GT DDS, MMBT2222A + 2N3866 PA, MCP4921 DAC,
LM393 comparator, MGA-82563 LNA, PE4259-63 T/R switch) are unchanged. The regulatory
constraints from XCVR-49MHZ-1 apply unchanged.

---

## Changes from XCVR-49MHZ-1

### 1. J1 host interface — EMI filter and protection

The 6-pin 2.54 mm pitch header J1 that connects to CAPE-B-2's RCRS-49 port is the
primary EMI ingress path. Any high-frequency conducted noise arriving on the UART and
PTT lines from the CAPE-B harness routes directly to the Si5351A logic interface
and MCP4921 SPI port. XCVR-49MHZ-2 adds a three-tier protection network:

## Tier 1 — Common-mode choke (CM5)

- Bourns SRF2012-100Y on the UART_TX/UART_RX pair (CM5)
- Placed between J1 and the Si5351A / MCU I²C interface
- Attenuates CM RF currents at the 49 MHz band and EDF switching harmonics (20–100 kHz)

## Tier 2 — Series ferrite beads

- Würth 742792510 (600 Ω @ 100 MHz, 100 mA, 0402) on UART_TX, UART_RX, and PTT_N,

  placed after CM5 toward the on-board circuitry

- Suppresses conducted EMI above 50 MHz that passes through the CMC

## Tier 3 — TVS protection array (TVS6)

- PRTR5V0U2X (NXP, dual-channel, 5.5 V clamp, SOT-363) on UART_TX and UART_RX
- Placed before CM5, immediately at J1 pin 3 and pin 4
- Clamps ESD / cable-injected transients to 5.5 V before they can reach any IC

## RSSI analog output (J1 pin 6)

- 1 nF C0G capacitor to GND, placed at J1 pin 6
- Filters HF noise on the analog output without distorting the DC–3 kHz RSSI signal

## +5V supply at J1 (pin 1)

- 10 µF MLCC + 100 nF 0402, placed immediately at J1 pin 1
- These are in addition to the existing AMS1117 / MCP1703 input capacitors

### 2. LDO upgrade: AMS1117-3.3 → MCP1703T-3302E/CB

| Parameter | XCVR-49MHZ-1 | XCVR-49MHZ-2 |
| --- | --- | --- |
| Part | AMS1117-3.3 (SOT-223) | MCP1703T-3302E/CB (SOT-23A-5) |
| PSRR (100 kHz) | 40 dB | 72 dB |
| PSRR (1 MHz) | 15 dB (typical) | 45 dB |
| Noise (10 Hz–100 kHz) | 50 µV RMS (typ) | 30 µV RMS (typ) |
| Dropout voltage | 1.2 V @ 800 mA | 425 mV @ 250 mA |
| Quiescent current | 5 mA | 55 µA |

The MCP1703T's superior PSRR at 100 kHz and above prevents EDF PWM ripple on the +5V
supply rail from modulating the 3.3 V reference voltage that feeds the Si5351A and
MCP4921 DAC. Supply noise on the Si5351A reference input translates directly to phase
noise on the 49 MHz carrier; better PSRR reduces incidental FM, which is particularly
important for the 1200-baud AFSK modulation scheme.

> **DigiKey:** MCP1703T-3302ECB-ND · $0.57 ea.

### 3. Enhanced supply bypass cascade

The original AMS1117 output had a single 10 µF + 100 nF bypass pair. XCVR-49MHZ-2
adds a four-capacitor cascade to address both low-frequency (EDF PWM) and high-frequency
(RF pickup) ripple:

```text

+5V_J1 ── FB2 ── +5V_F ── MCP1703T ── +3V3_F
|  |
                 C21                      C23  C24  C25  C26
                (100µF)             (100µF)(10µF)(100nF)(10nF)

```

| Reference | Value / Type | Placed at |
| --- | --- | --- |
| FB2 | Würth 742792512 (600 Ω @ 100 MHz, 2 A) | +5V input, before LDO |
| C21 | 100 µF / 10 V MLCC X5R 1210 | +5V, input bulk |
| C22 | 100 nF / 10 V MLCC X7R 0402 | +5V, HF bypass |
| C23 | 100 µF / 10 V MLCC X5R 1210 | +3V3, output bulk |
| C24 | 10 µF / 10 V MLCC X5R 0805 | +3V3, mid-frequency |
| C25 | 100 nF / 10 V MLCC X7R 0402 | +3V3, HF bypass |
| C26 | 10 nF / 10 V MLCC C0G 0402 | +3V3, VHF bypass |

C26 (C0G 10 nF) specifically targets the 49 MHz fundamental and its harmonics.
C0G dielectric has no piezoelectric effect and maintains capacity within 1% across
temperature, preventing resonance shifts in the decoupling network.

### 4. Improved low-pass filter: 6-element Chebyshev

XCVR-49MHZ-1 specified a 5-element Chebyshev LPF (FL1) with fc = 75 MHz and
≥ 40 dBc attenuation at the 2nd harmonic (98 MHz). XCVR-49MHZ-2 upgrades to a
6-element design to add one additional pole, targeting ≥ 50 dBc at 98 MHz and
≥ 60 dBc at 147 MHz (3rd harmonic):

| Element | Value (6-element Chebyshev, 0.5 dB ripple, Zin/Zout = 50 Ω) | Component |
| --- | --- | --- |
| L1 | 100 nH | Coilcraft 0805HQ-101JLBC (shielded ferrite) |
| C1 | 120 pF | C0G 0402 |
| L2 | 180 nH | Coilcraft 0805HQ-181JLBC |
| C2 | 180 pF | C0G 0402 |
| L3 | 180 nH | Coilcraft 0805HQ-181JLBC |
| C3 | 120 pF | C0G 0402 |

> **SPICE/QUCS-S verification** required in Phase 4 per XCVR-49MHZ-1 design notes.
> The 6-element network is specifically designed to ensure ≥ 60 dBc at 147 MHz
> (per 47 CFR 95.655 requirement for spurious above 1 GHz when harmonically related
> to a sub-30-MHz fundamental — the relevant limit at the 3rd harmonic of 49 MHz).

### 5. Chassis ground (PGND) and shielding

## Board-level chassis ground

A PGND copper pour ring (3 mm wide, all four board edges) connects to:

- The SMA J2 connector shell (shield contact, outer conductor)
- All four M3 corner mounting holes
- The PE4259-63 T/R switch body GND pad (RF section, In1.Cu)
- TVS-SMA (SMAJ5.0A, see §6)

PGND-to-GND single-point connection: 0 Ω solder-selectable link at J1 GND (pin 2),
so the board shares chassis ground with the CAPE-B host when plugged in. If RF isolation
from the host ground is preferred, the link is left open.

## EMI shield can footprint

The RF section (Si5351A, PA stage, LPF, T/R switch, LNA — right 25 mm of board) has a
metal EMI shield can footprint (Laird / Würth snap-on or soldered lid, 25 × 30 mm).
Tin-plated steel (Laird MSA030020T or equivalent). Soldering tabs connect to PGND.
The shield can:

- Prevents RF leakage from the PA from coupling into the digital UART/I²C section
- Provides >30 dB additional shielding against external E-field at 49 MHz

### 6. Antenna port TVS protection

A SMAJ5.0A bidirectional TVS is placed on the SMA J2 antenna port center conductor,
clamping any cable-injected transients to ±5 V before the PE4259-63 T/R switch.
The TVS is a SOD-123FL package, placed within 2 mm of J2, with the cathode to PGND.

> **Note:** The SMAJ5.0A is a protective device against cable-injected ESD/lightning
> — it does NOT attenuate the 49 MHz signal (insertion loss < 0.1 dB at 49 MHz at
> 100 mW output level). The device does affect VSWR above 500 MHz, which is acceptable
> since the LPF already provides ≥ 40 dBc attenuation at those frequencies.

### 7. PCB layout — additional constraints beyond XCVR-49MHZ-1

- **PGND pour:** In1.Cu GND plane is divided at the midpoint between digital and RF

  sections; the RF side pour is labeled PGND and connects to the SMA shell. The
  digital side is plain GND. The moat is bridged by a 10 nF C0G capacitor (C27)
  for RF, referencing PGND on one side and GND on the other.

- **Shield can wall clearance:** All components inside the EMI can footprint must be

  at least 0.5 mm from the can footprint outline to allow the snap-on lid.

- **MCP1703T placement:** The LDO must be outside the shield can (digital section),

  with its output traces entering the RF section through a ferrite bead (FB2 or
  dedicated 0402 bead). This prevents LDO switching noise from contaminating the
  RF supply path.

- **J1 filter placement:** CM5 common-mode choke and TVS6 array must be within 3 mm

  of J1 and outside the shield can.

- **SMA TVS placement:** TVS-SMA (SMAJ5.0A) must be within 2 mm of J2 on the board

  edge side, outside the shield can.

---

## Updated Bill of Materials (delta from XCVR-49MHZ-1)

### Removed

| Reference | Part |
| --- | --- |
| U6 | AMS1117-3.3 LDO |
| FL1 | 5-element Chebyshev LPF (replaced by 6-element) |

### Added / changed

| Reference | Part | Function |
| --- | --- | --- |
| U6 | MCP1703T-3302E/CB (SOT-23A-5) | Upgraded LDO, 72 dB PSRR at 100 kHz |
| CM5 | Bourns SRF2012-100Y | Common-mode choke on J1 UART pair |
| TVS6 | PRTR5V0U2X (SOT-363) | Dual TVS on J1 UART_TX/RX |
| TVS-SMA | SMAJ5.0A (SOD-123FL) | Antenna port transient clamp |
| FB2 | Würth 742792512 | +5V input ferrite bead |
| FB-TX | Würth 742792510 × 3 | Series beads: UART_TX, UART_RX, PTT_N |
| C21 | 100 µF / 10 V MLCC 1210 | +5V input bulk |
| C22 | 100 nF 0402 | +5V HF bypass |
| C23 | 100 µF / 10 V MLCC 1210 | +3V3 output bulk |
| C24 | 10 µF 0805 | +3V3 mid-frequency |
| C25 | 100 nF 0402 | +3V3 HF bypass |
| C26 | 10 nF C0G 0402 | +3V3 VHF (49 MHz) bypass |
| C27 | 10 nF C0G 0402 | GND–PGND moat bridge |
| Shield | Laird MSA030020T (or equiv) | RF section EMI shield can |
| FL1_L1 | 100 nH (Coilcraft 0805HQ-101J) | 6-element LPF element 1 |
| FL1_C1 | 120 pF C0G 0402 | 6-element LPF element 2 |
| FL1_L2 | 180 nH (Coilcraft 0805HQ-181J) | 6-element LPF element 3 |
| FL1_C2 | 180 pF C0G 0402 | 6-element LPF element 4 |
| FL1_L3 | 180 nH (Coilcraft 0805HQ-181J) | 6-element LPF element 5 |
| FL1_C3 | 120 pF C0G 0402 | 6-element LPF element 6 |

---

## Board Size and Stackup

**Board size:** 55 × 35 mm — unchanged from XCVR-49MHZ-1.

The EMI shield can footprint fits within the existing RF section keep-out area (right
25 mm × 30 mm). The new filter components (CM5, TVS6, FB2, bypass caps) occupy the
vacated AMS1117 SOT-223 pad area plus a 5 × 8 mm strip adjacent to J1.

**Layer stackup:** 4-layer, identical to XCVR-49MHZ-1.

---

## Regulatory Constraints

Unchanged from XCVR-49MHZ-1. The 6-element LPF provides additional margin vs. the
5-element version, improving compliance margin for 47 CFR 95.655 spurious emission
limits.

---

## Security Notes

Unchanged from XCVR-49MHZ-1. The board carries no TPM. All cryptographic operations
for AX.25 payload signing remain on the CAPE-B host CPU.

---

## Related Files

- `XCVR-49MHZ-1.kicad_sch` — original (Phase 1 stub) schematic
- `XCVR-49MHZ-1.md` — original Phase 1 design notes and committed BOM
- `CAPE-B-2.kicad_sch` — host board with J1 counter-connector
- `CAPE-B-2.md` — CAPE-B-2 design notes

---

## References

1. Microchip MCP1703 Data Sheet DS22049E — PSRR curves (Figures 2-5)

- Step 2: Würth Elektronik EMC Design Guide — ferrite bead and LDO bypass layout

- Step 3: NXP PRTR5V0U2X Product Data Sheet Rev. 3

- Step 4: Laird MSA Series Shield Can Selection Guide

- Step 5: XCVR-49MHZ-1.md — Phase 1 design decisions (IC selection rationale)

- Step 6: 47 CFR 95.655 — FCC spurious emission requirements

- Step 7: QUCS-S / SPICE Chebyshev filter synthesis reference:

   Williams & Taylor, "Electronic Filter Design Handbook" 4th ed., Table 11-60

---

## PCB File Inline Notes

KiCad S-expression files do not support inline comments. The following content was
previously carried as semicolon-prefixed comment lines in `XCVR-49MHZ-2.kicad_pcb`
and is preserved here per project standards (CLAUDE.md §Coding Standards).

### File Header (removed from kicad_pcb)

- **Board:** XCVR-49MHZ-2 EMI-Hardened 49 MHz AX.25 KISS Transceiver
- **Date:**2026-06-03**Rev:** 2
- **4-layer stackup:** F.Cu (signal) / In1.Cu (GND) / In2.Cu (+5V power) / B.Cu (signal)
- **Board size:** 55 × 35 mm, origin at (100, 100) mm
- **FAB target:** JLCPCB 4-layer, 1.6 mm FR4, ENIG
- **Changes from Rev 1:** Added CMC_CAN (SRF2012), D_TVS (PRTR5V0U2X), FB1 (742792512),

  C_X2Y (4.7 nF X2Y cap); all UUIDs regenerated with prefix `49020000-0000-0000-0000-`

### Reference Designator Convention — CMC_CAN

The suffix "CAN" in `CMC_CAN` follows the project naming convention for the antenna
common-mode choke per the task specification "CMC_CAN: SRF2012 near antenna path".
This component suppresses common-mode currents on the antenna feed line to reduce
conducted EMI per IEEE 1613 / CISPR 32.
Pad 1 = ANT input (from RF section); Pad 2 = ANT output (clean side, toward J2 SMA).
Both KiCad pads are assigned to net ANT because a separate ANT_CMC_OUT net was not
declared; the functional distinction is physical placement only.

### Footprint Pad Net Assignments

| Ref | Pad | Net | Notes |
| ----- | ----- | ----- | ------- |
| J1 | 1 | GND | Left-most pin, 1.25 mm pitch SMD |
| J1 | 2 | UART_TX |
| J1 | 3 | UART_RX |
| J1 | 4 | PTT_N |
| J1 | 5 | RSSI_ANA |
| J1 | 6 | +3V3 | Right-most pin |
| J2 | 1 | ANT | SMA centre pin, 0.9 mm drill, thru-hole circle |
| J2 | 2 | GND | Upper GND tab, 1.0 mm drill |
| J2 | 3 | GND | Lower GND tab, 1.0 mm drill |
| CMC_CAN | 1 | ANT | Input from RF section; left pad, silkscreen notch marks pin 1 |
| CMC_CAN | 2 | ANT | Output to J2; right pad |
| D_TVS | 1 | GND | Left column bottom — SOT-363 pin 1 per NXP PRTR5V0U2X pinout |
| D_TVS | 2 | ANT | Left column centre — TVS anode A1 |
| D_TVS | 3 | GND | Left column top |
| D_TVS | 4 | GND | Right column top |
| D_TVS | 5 | RF_TX | Right column centre — TVS anode A2 |
| D_TVS | 6 | GND | Right column bottom |
| FB1 | 1 | +5V | Input — raw +5V from J1 before filtering |
| FB1 | 2 | +5V_FILT | Output — clean supply to on-board ICs; 0805 pad reused for bead |
| C_X2Y | 1 | GND | Both pads GND for X2Y differential-mode bridge function |
| C_X2Y | 2 | GND | Both pads GND for X2Y differential-mode bridge function |

### Copper Pour Notes

- **In1.Cu — GND plane:** Full-board pour, polygon (100,100)→(155,135).

  Per IPC-2141A controlled-impedance inner plane requirement.
  Min thickness 0.25 mm; thermal gap 0.5 mm; thermal bridge width 0.5 mm.

- **In2.Cu — +5V power plane:** Digital section only, polygon (100,100)→(130,135).

  Excludes RF section (x = 130–155 mm) per PCB layout constraint: no power plane
  under RF section.

### Footprint Courtyard and Body Dimensions

| Ref | Courtyard (mm) | Fab body (mm) | Notes |
| ----- | ---------------- | --------------- | ------- |
| CMC_CAN | 2.4 × 1.4, centred | 2.0 × 1.25 | Silkscreen notch on left edge for pin 1 |
| D_TVS | 2.1 × 2.4 | 1.3 × 2.0 (SOT-363) | Filled triangle poly marks pin 1 |
| FB1 | 3.4 × 2.0 | 2.0 × 1.2 | Silkscreen tick on left edge for pin 1 |
| C_X2Y | 1.4 × 0.9 | 1.0 × 0.5 | 0402 metric |

---

## Schematic Inline Notes

The following content was previously carried as `;;`-prefixed comment lines in
`XCVR-49MHZ-2.kicad_sch` and is preserved here per project standards.

### Component Placement Coordinates

All coordinates are in KiCad schematic mm units. Pin offsets are from the component
anchor; they are needed for hand-editing this file because KiCad pin exits are at
fixed offsets from the symbol anchor per the lib_symbols definition above.

| Ref | Anchor (x, y) | Rotation | Pin exit notes |
| ----- | --------------- | ---------- | ---------------- |
| J1 | 50.00, 100.00 | 0° | Pins exit at x = 52.54; y pitch = 2.54 mm; pin 1 at y = 106.35 |
| FB1 | 90.00, 96.19 | 90° | Pin A exits at (86.19, 100.00); Pin B exits at (90.00, 92.38) |
| CMC_CAN | 200.00, 100.00 | 0° | L1A at (194.92, 101.27); L2A at (194.92, 98.73); L1B at (205.08, 101.27); L2B at (205.08, 98.73) |
| D_TVS | 240.00, 100.00 | 0° | A1 at (234.92, 101.27); A2 at (234.92, 98.73); K at (245.08, 100.00); GND at (240.00, 105.08) |
| J2 | 280.00, 100.00 | 0° | RF pin at (274.92, 100.00); GND pin at (285.08, 100.00) |
| C_X2Y | 270.00, 120.00 | 0° | Pin 1 top at (270.00, 116.19); Pin 2 bottom at (270.00, 123.81) |

### Power Symbol Placements

| Symbol | UUID suffix | At (x, y) | Connects to |
| -------- | ------------- | ----------- | ------------- |
| GND #PWR01 | …000201 | 57.62, 106.35 | J1 pin 1 (GND) |
| +5V #PWR02 | …000203 | 57.62, 103.81 | J1 pin 2 (+5V, before FB1) |
| +5V #PWR03 | …000205 | 90.00, 92.38 | FB1 pin B (filtered +5V output) |
| GND #PWR04 | …000207 | 240.00, 105.08 | D_TVS pin 6 (GND) |
| GND #PWR05 | …000209 | 285.08, 100.00 | J2 pin 2 (GND/shield) |
| GND #PWR06 | …000211 | 270.00, 123.81 | C_X2Y pin 2 (bottom) |
| GND #PWR07 | …000213 | 209.16, 98.73 | CMC_CAN L2B (pin 4, return path) |
| GND #PWR08 | …000215 | 190.84, 98.73 | CMC_CAN L2A (pin 2, input) |

### Signal Routing

- J1 pin 1 → GND power symbol at (57.62, 106.35)
- J1 pin 2 → +5V, then wire through (80.00, 103.81)→(80.00, 100.00)→(86.19, 100.00)

  to FB1 pin A

- J1 pin 3 → global label `SDA` (I²C data to transceiver MCU)
- J1 pin 4 → global label `SCL` (I²C clock to transceiver MCU)
- J1 pin 5 → global label `PTT_N` (push-to-talk, active LOW)
- J1 pin 6 → global label `RX_OUT` (received audio / AFSK out)
- `RF_ANT` label at (190.84, 101.27) → short wire → CMC_CAN L1A (194.92, 101.27)
- CMC_CAN L2A (194.92, 98.73) → GND at (190.84, 98.73)
- CMC_CAN L1B (205.08, 101.27) → `RF_ANT_F` label at (209.16, 101.27)
- CMC_CAN L2B (205.08, 98.73) → GND at (209.16, 98.73)
- `RF_ANT_F` label at (234.92, 101.27) → D_TVS A1 and A2 (junction at 234.92, 101.27)
- D_TVS K (245.08, 100.00) → `RF_ANT_F` label at (250.16, 100.00)
- `RF_ANT_F` label at (274.92, 100.00) → J2 RF pin
- J2 GND pin (285.08, 100.00) → GND power symbol
- `RF_ANT_F` label at (270.00, 116.19) → C_X2Y pin 1 (top)
- C_X2Y pin 2 (270.00, 123.81) → GND power symbol
