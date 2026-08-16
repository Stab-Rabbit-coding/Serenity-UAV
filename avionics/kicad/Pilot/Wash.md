# Wash — EMI-Hardened Flight Control & Sensor Cape

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Callsign:** Wash
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** R (Rev R baseline; carried forward from Rev A — EMI-hardened variant of CAPE-A-1 Rev M; no design changes)
**Date:** 2026-06-11
**Status:** Schematic complete — PCB layout pending

---

## Purpose

Wash is an electromagnetic-environment-hardened variant of CAPE-A-1 (Rev M) intended
for operation in the nacelle bays and fuselage sections of the Serenity UAV where EDF motor
switching noise, high-current ESC PWM harmonics, and external RF threats require a higher
level of conducted and radiated immunity than the standard Rev M design provides.

This variant maintains full functional equivalence with CAPE-A-1: same PocketBeagle 2
Industrial (AM6254) host, same sensor suite, same bus topology. The changes are purely
protective hardening — no firmware or DTS changes are required.

---

## Changes from CAPE-A-1 (Rev M)

### 1. EMI-Hardened Dual Ethernet PHY (Rev R baseline; introduced Rev A)

Two Texas Instruments DP83825I 10/100BASE-TX PHYs are included with full EMI
hardening. Each PHY connects via RMII to one of the PocketBeagle 2 AM6254's
two RGMII/RMII Ethernet ports (RMII0 and RMII1).

EMI hardening measures per PHY:

- **LAN magnetics:** Pulse Electronics HX1188NL dual 10/100BASE-TX transformer
  with integrated common-mode choke (1500 V isolation, SOIC-16).
- **Additional CMC:** Bourns SRF2012-100Y on PHY-side MDI lines (belt-and-suspenders).
- **TVS protection:** 2× PRTR5V0U2X (dual-channel SOT-363) on connector-side MDI lines.
- **Bypass capacitors:** 100nF + 10nF + 1nF triplet on all VDD pins (100BASE-TX edge
  rates suppressed; 100 MHz emissions are primarily the VDD ripple, not MDI lines).
- **1.8V supply:** TPS62933 SMPS (3.3V→1.8V, 300mA) for PHY AVDD and DVDD.
  Switching frequency 2.2 MHz — far from 100BASE-TX 125 MHz spectral content.
- **RBIAS:** 49.9Ω 1% 0402 resistor on RBIAS pin.
- **Connector:** JST SM06B-GHS-TB-1MP (6-pin shielded GH) — GND/TX+/TX-/RX+/RX-/GND,
  SHIELD pin to PGND. One connector per PHY, both populated on the PCB.

PHY1 connects to PocketBeagle 2 RMII0; PHY2 connects to RMII1.
MDC and MDIO are shared between both PHYs (different PHY addresses: PHY1=0x01, PHY2=0x02).

Ethernet connector assignments:

| Connector | PHY | Port | Signals |
|---|---|---|---|
| J_ETH1 | DP83825I PHY1 | RMII0 / ETH0 | ETH1_TX+/TX-/RX+/RX-, GND, SHIELD |
| J_ETH2 | DP83825I PHY2 | RMII1 / ETH1 | ETH2_TX+/TX-/RX+/RX-, GND, SHIELD |

### 2. CAN FD transceiver: ATA6561 → ISOW1044BDFMR

| Parameter | CAPE-A-1 | Wash |
|---|---|---|
| Part | ATA6561 (SOIC-8) | ISOW1044BDFMR (SOIC-16) |
| Isolation | None (non-isolated) | 5000 V RMS reinforced (IEC 62368-1) |
| Surge | ±25 V bus fault protection | ±42 V bus fault protection |
| Data rate | 5 Mbps CAN FD | 5 Mbps CAN FD (ISO 11898-1:2015 compliant) |
| Supply | 5 V (VCC) | 3.3 V VCC1 (logic); internal DC/DC generates VCC2 |
| Current | 40 mA typical | 55 mA typical (includes DC/DC overhead) |
| DigiKey | — | 296-ISOW1044BDFMRCT-ND |

The integrated DC/DC converter in the ISOW1044BDFMR generates the isolated bus-side VCC2
from VCC1 — no external isolated power supply is required. The CAN transceiver pins (TXD,
RXD, STB_N) are logically compatible with the ATA6561 pinout, with the following note:

> **Polarity note:** ISOW1044BDFMR STB_N is active LOW for standby (same polarity as
> ATA6561 STB). No firmware change required.

A 100 nF + 10 nF bypass capacitor pair is placed on VCC2-to-GND2 at the isolation
boundary. A 4.7 nF X2Y capacitor bridges GND1-to-GND2 externally per TI application note
SLLA337A, providing a low-impedance CM noise return path at RF frequencies (>1 MHz)
without compromising DC isolation.

### 3. RS-485 transceiver: MAX3485E → ADM2795EBRWZ → ISOW1412 (REF-SENSOR-010)

| Parameter | CAPE-A-1 | Wash (current) |
|---|---|---|
| Part | MAX3485E (SOIC-8) | **ISOW1412** (20-pin DFM, `Package_SO:SOIC-20W_7.5x12.8mm_P1.27mm`) |
| Isolation | None (non-isolated) | 5000 V RMS reinforced |
| Data rate | 32 Mbps | 500 kbps (ISOW1412 variant; pin-compatible ISOW1432 is the 12 Mbps part, not used) |
| Supply / DC-DC | 3.3 V | 3.3 V VIO; **own integrated isolated DC/DC** generates the bus-side supply (no external isolated supply needed) |
| Current | 3.5 mA | ≤60 mA (VIO 4.5–5.5 V, incl. integrated DC/DC per datasheet §8.9/8.10); 20 mA of the DC/DC's output is available for other bus-side circuits |
| DigiKey | — | see REFERENCES.md REF-SENSOR-010 |

**Fleet-wide swap, 2026-07-26** (REFERENCES.md "Removed / Superseded Citations"): ADM2795EBRWZ
was briefly used here but is signal-isolation-only and needs a *separate* external isolated
DC-DC for its bus-side VDD2. ISOW1412 integrates its own isolated DC-DC, removing that extra
supply fleet-wide (same swap applied to TACCO, Observer, FlightEngineer, CAN-PERIPH-GW-1). While performing
this swap, Wash's pre-existing ADM2795EBRWZ symbol was found to have incorrectly numbered pins
(pre-existing defect, corrected in the same pass — see `avionics/kicad/fix_wash_zoe_isolators.py`).
Wash's own **PCB footprint has not yet been swapped to ISOW1412** — it currently still carries
the old ADM2795EBRWZ footprint; this is open work (see root `TODO.md` §1.2a).

ISOW1412 is a full-duplex part (separate Y/Z driver-out, A/B receiver-in); it is run in
half-duplex mode on this project's 2-wire RS485_A/RS485_B bus by shorting Y-to-A and Z-to-B,
the standard technique for using a full-duplex transceiver as half-duplex. The half-duplex
direction-control scheme (RS485_DE driving DE/RE_N) is preserved unchanged.

A 4.7 nF X2Y capacitor bridges GND1-to-GND2 externally for the same RF CM noise return
path reason described above for the CAN transceiver.

### 4. Common-mode chokes on CAN and RS-485 bus lines

Each bus exits the isolated transceiver through a common-mode choke before reaching the
JST-GH field connector:

| Reference | Bus | Part | Spec | Package |
| --- | --- | --- | --- | --- |
| CM1 | CAN FD | Bourns SRF2012-100Y | 100 Ω @ 100 MHz, 800 mA, 0805 | 2012 SMD |
| CM2 | RS-485 | Bourns SRF2012-100Y | 100 Ω @ 100 MHz, 800 mA, 0805 | 2012 SMD |

The chokes suppress common-mode currents injected by the EDF switching environment onto
the bus cable shields.

### 5. TVS diode arrays on all external field connectors

| Reference | Connector | Part | Clamp | DigiKey |
| --- | --- | --- | --- | --- |
| TVS-CAN | CAN-A JST-GH | PRTR5V0U2X | 5.5 V, bidirectional, 25 A 8/20 µs | 1727-4776-1-ND |
| TVS-485 | RS485-A JST-GH | PRTR5V0U2X | 5.5 V, bidirectional, 25 A 8/20 µs | 1727-4776-1-ND |
| TVS-1553 | 1553-A JST-GH | SMAJ33CA (×2) | 33 V, bidirectional, 400 W 1 ms | SMAJ33CACT-ND |

The PRTR5V0U2X is a dual-channel SOT-363 array; one device protects both differential
lines of a bus simultaneously. The 1553 bus is protected with two individual SMAJ33CA
bidirectional TVS diodes (one per bus line, clamped to chassis ground PGND), since the
1553 coupling transformer secondary already provides 1:1.41 isolation — the TVS protects
the transformer primary from destructive cable-injected transients.

### 6. Power entry filter

A π-filter is placed on the +5V power entry from the cape power bus connector (J-PWR,
Molex Nano-Fit 4-pin). The filter attenuates conducted EMI entering the board on the
supply rails:

```text

+5V_IN ── FB1 ── +5V (cape rail)
|  |
          C11          C12
|  |
          GND          GND

```

| Reference | Value | Part | Spec |
| --- | --- | --- | --- |
| C11 | 47 µF / 10 V | MLCC X5R 1210 | Input bulk cap; low ESL |
| FB1 | 600 Ω @ 100 MHz | Würth 742792512 | 2 A, 2012 SMD ferrite bead |
| C12 | 10 µF / 10 V | MLCC X5R 0805 | Output bulk; plus 100 nF 0402 in parallel |

### 7. Chassis ground (PGND) implementation

A dedicated chassis ground net (PGND) is introduced, connected to:

- All four M3 mounting holes (via 0 Ω solder-selectable resistors to PGND)
- Isolated bus sides of ISOW1044BDFMR (GND2)
- Isolated bus sides of ADM2795EBRWZ (GND2)
- Shield pins of all JST-GH field connectors (CAN-A, RS485-A, 1553-A)
- TVS return pins (TVS-CAN, TVS-485, TVS-1553)
- C11 (power entry bulk cap return)

PGND is connected to GND (signal ground) at exactly one point via a 0 Ω / 10 Ω
solder-selectable link at J-PWR. This single-point connection prevents ground loops
while ensuring a defined potential relationship. In the installed aircraft, each cape
bay provides a secondary chassis bond through the mounting hardware.

### 8. Additional bypass capacitors

All logic-side IC VCC pins receive a 100 nF + 10 nF + 1 nF bypass capacitor triplet
(in 0402 packages, placed within 0.5 mm of the power pin) in addition to the original
100 nF single-cap practice. This suppresses higher-order resonances that a single cap
value cannot address.

---

## PCB Layout Constraints (additions to CAPE-A-1 rules)

- **PGND copper pour:** All inner-layer copper (In1.Cu GND) is renamed to PGND on the

  board perimeter ring (3 mm width around all four edges). Signal GND and PGND connect
  at the single-point J-PWR star under the mounting hole.

- **Isolation creepage:** Maintain ≥ 8 mm creepage and ≥ 1.5 mm clearance between

  GND1 and GND2 copper pours on the ISOW1044BDFMR and ADM2795EBRWZ
  [REF-IEC-001 §5.5.2] [REF-VDE-001 Cl.4.3]. Per IEC 62368-1 Annex G, 5 kV
  reinforced isolation at 250 V working voltage requires ≥ 8 mm creepage in
  pollution degree 2 environment.

  > **Verification status (2026-06-22, `kicad-cli pcb drc` against `Wash.kicad_pcb`,
  > KiCad 9.0.2): NOT MET — BLOCKS PCB fab.** The board does not currently meet this
  > requirement. After excluding same-package pin-to-pin spacing (adjacent pins on the
  > secondary side of the same isolator IC, which the `ISOLATION` netclass rule also
  > flags but which are not a primary/secondary creepage issue), DRC found **13 genuine
  > cross-domain clearance violations**, all between the `TMESH_P`/`TMESH_N`
  > tamper-detect mesh and `GND2_CAN`/`GND2_ETH` isolated-domain pads/tracks, with
  > actual measured spacing as low as **0.125 mm** — far short of both the 0.5 mm
  > `ISOLATION` netclass DRC minimum and the ≥ 8 mm physical creepage target above.
  > Root cause and full violation count are already tracked in `TODO.md` §1.2a (tamper
  > mesh routed through the isolated `GND2_*` domains; ≈335 of Wash's then-465 DRC
  > errors). This verification did not change layout — per `AGENTS.md`, footprint/route
  > rework to close this gap is referred to the user, not performed automatically.

- **CMC placement:** CM1 and CM2 must be placed on the board side of the field

  connector (between the IC and the JST-GH pin row), not on the cable side.

- **TVS placement:** TVS-CAN and TVS-485 must be placed within 5 mm of the JST-GH

  connector body, on the outer copper layer, with GND return via ≥ 2× 0.3 mm vias to
  the inner PGND plane.

- **X2Y isolation caps (C13, C14):** Place on the PCB with the isolation-boundary

  axis perpendicular to the creepage gap axis. Reference TI SLLA337A layout guidance.

- **Stitching vias:** Double the original stitching via density around the isolated

  transceiver areas to prevent fringe fields from bridging the isolation gap.

---

## Eliminated vs. CAPE-A-1 Bill of Materials (delta)

### Removed

| Reference | Part | Notes |
|---|---|---|
| CAN-TR (ATA6561) | Non-isolated CAN FD transceiver | Replaced by ISOW1044BDFMR |
| RS485 (MAX3485E) | Non-isolated RS-485 | Replaced by ADM2795EBRWZ |

### Added

| Reference | Part | Function |
|---|---|---|
| ETH1-PHY | DP83825I | RMII PHY for ETH0, EMI-hardened |
| ETH2-PHY | DP83825I | RMII PHY for ETH1, EMI-hardened |
| U_ETH1_1V8 | TPS62933 | 1.8V supply for ETH1 PHY (AVDD, DVDD) |
| U_ETH2_1V8 | TPS62933 | 1.8V supply for ETH2 PHY (AVDD, DVDD) |
| HX1188_1 | HX1188NL | ETH1 LAN transformer + integrated CMC |
| HX1188_2 | HX1188NL | ETH2 LAN transformer + integrated CMC |
| TVS_ETH1_TX | PRTR5V0U2X | ETH1 TX+/TX- TVS protection |
| TVS_ETH1_RX | PRTR5V0U2X | ETH1 RX+/RX- TVS protection |
| TVS_ETH2_TX | PRTR5V0U2X | ETH2 TX+/TX- TVS protection |
| TVS_ETH2_RX | PRTR5V0U2X | ETH2 RX+/RX- TVS protection |
| CM_ETH1 | SRF2012-100Y | ETH1 PHY-side MDI common-mode choke |
| CM_ETH2 | SRF2012-100Y | ETH2 PHY-side MDI common-mode choke |
| J_ETH1 | JST SM06B-GHS-TB-1MP | ETH1 shielded 6-pin GH connector |
| J_ETH2 | JST SM06B-GHS-TB-1MP | ETH2 shielded 6-pin GH connector |
| CAN-ISO | ISOW1044BDFMR | Isolated CAN FD transceiver (5 kV reinforced) |
| RS485-ISO | ADM2795EBRWZ | Isolated RS-485 transceiver (5 kV reinforced, ±42 V) |
| CM1 | Bourns SRF2012-100Y | CAN bus common-mode choke |
| CM2 | Bourns SRF2012-100Y | RS-485 bus common-mode choke |
| TVS-CAN | PRTR5V0U2X | Dual TVS on CAN-A connector |
| TVS-485 | PRTR5V0U2X | Dual TVS on RS485-A connector |
| TVS-1553 | SMAJ33CA × 2 | Bidirectional TVS on 1553 bus lines |
| FB1 | Würth 742792512 | 5V power entry ferrite bead |
| C11 | 47 µF MLCC 1210 | 5V input bulk capacitor |
| C12 | 10 µF + 100 nF | 5V filtered rail bypass |
| C13 | 4.7 nF X2Y | CAN isolation boundary CM bypass |
| C14 | 4.7 nF X2Y | RS-485 isolation boundary CM bypass |
| J-PWR | Molex Nano-Fit 4-pin | Power entry connector (per AVIONICS_PB2_REDESIGN §11) |

---

## Power Budget (updated)

| Rail | Consumers | Max current |
| --- | --- | --- |
| +5V (filtered) | PB2 VIN | 2.0 A |
| +3V3 (LDO) | ICM-42688-P, BMP388, M10Q, SLB9670, ISOW1044BDFMR VCC1, ADM2795EBRWZ VDD1, 2× DP83825I IOVDD (55 mA each = 110 mA), 2× TPS62933 VIN quiescent | 720 mA |
| +3V3 isolated bus-side (VCC2/VDD2 — internal) | CAN bus stub loads, RS-485 line drivers | ≤ 150 mA combined (limited by ISOW1044B) |
| +1V8_ETH1 (TPS62933 output) | DP83825I PHY1 AVDD + DVDD | 80 mA |
| +1V8_ETH2 (TPS62933 output) | DP83825I PHY2 AVDD + DVDD | 80 mA |

Both DP83825I PHYs are populated and active. The two TPS62933 converters (3.3V→1.8V,
300 mA rated) supply AVDD and DVDD for each PHY respectively. The +3V3 rail increases
by approximately 110 mA IOVDD (2× 55 mA) plus two TPS62933 conversion losses (~10 mA
each). Total +3V3 budget remains within the LDO regulator's rated capacity.

---

## EMC Compliance Targets

This variant is designed to achieve immunity per the following standards, applicable
to the Serenity UAV airframe operating environment:

| Standard | Level | Test | Notes |
| --- | --- | --- | --- |
| IEC 61000-4-2 [REF-IEC-003] | Level 4 (±8 kV contact, ±15 kV air) | ESD | TVS arrays at all field connectors |
| IEC 61000-4-4 [REF-IEC-004] | Level 4 (4 kV peak) | EFT/Burst on signal lines | CMCs + isolated transceivers |
| IEC 61000-4-5 [REF-IEC-005] | Level 3 (2 kV CM, 1 kV DM) | Surge | ±42 V bus fault on CAN/RS-485 |
| MIL-STD-461G RE102 [REF-MIL-002] | Limit C | Radiated emissions | 100BASE-TX EMI suppressed via HX1188NL magnetics, CMCs, and TVS arrays |
| MIL-STD-461G RS103 [REF-MIL-002] | 200 V/m, 10 kHz–18 GHz | Radiated susceptibility | Isolated buses + chassis ground |

Pre-compliance testing against IEC 61000-4-2 through 4-5 is required before first
flight. Formal MIL-STD-461G testing is deferred pending airframe integration.

---

## §14 — Field Connectors Summary

All field connectors use JST GH series (1.25 mm pitch) with shrouded shielded housings.
SHIELD/MP pins on all connectors connect to chassis ground (PGND). Power pins are
routed through the π-filter (FB1/C11/C12) before distribution to the cape rail.

| Designator | Type | Pin Assignments | Function |
|---|---|---|---|
| J_PWR | SM04B-GHS-TB-1MP | 1=+5V_IN, 2=GND, 3=GND, 4=+5V_IN, MP=PGND | Power input (4-pin dual-rail entry) |
| J_CAN | SM03B-GHS-TB-1MP | 1=CAN_A_H, 2=CAN_A_L, 3=GND, MP=PGND | CAN FD bus (ISOW1044BDFMR isolated) |
| J_485 | SM03B-GHS-TB-1MP | 1=RS485_A_P, 2=RS485_A_N, 3=GND, MP=PGND | RS-485 half-duplex (ADM2795EBRWZ isolated) |
| J_1553 | SM04B-GHS-TB-1MP | 1=BUS_1553_A_P, 2=BUS_1553_A_N, 3=GND, 4=PGND, MP=PGND | MIL-STD-1553B differential bus |
| J_GPS | SM05B-GHS-TB-1MP | 1=GND, 2=+3V3, 3=GPS_TX(UART2_RX), 4=GPS_RX(UART2_TX), 5=GPS_PPS, MP=PGND | u-blox M10Q GPS module |
| J_SERVO | SM06B-GHS-TB-1MP | 1=GND, 2=+5V, 3=SERVO_CH0, 4=SERVO_CH1, 5=SERVO_CH2, 6=SERVO_CH3, MP=PGND | Nacelle tilt servos (PWM) |
| J_ESC | SM04B-GHS-TB-1MP | 1=ESC_PWM_0, 2=ESC_PWM_1, 3=ESC_PWM_2, 4=GND, MP=PGND | EDF ESC PWM / BDSHOT outputs |
| J_ENC | SM04B-GHS-TB | 1=GND, 2=+3V3, 3=ENC_SDA, 4=ENC_SCL, MP=PGND | AS5600 nacelle tilt angle encoder (I2C) |
| J_ETH1 | SM06B-GHS-TB-1MP | 1=GND, 2=ETH1_TX+, 3=ETH1_TX-, 4=ETH1_RX+, 5=ETH1_RX-, 6=GND, MP=PGND | Ethernet PHY1 (DP83825I, RMII0) |
| J_ETH2 | SM06B-GHS-TB-1MP | 1=GND, 2=ETH2_TX+, 3=ETH2_TX-, 4=ETH2_RX+, 5=ETH2_RX-, 6=GND, MP=PGND | Ethernet PHY2 (DP83825I, RMII1) |
| J_SBUS | SM03B-GHS-TB-1MP | 1=GND, 2=+5V, 3=SBUS_RAW, MP=PGND | RC receiver SBUS input (inverted via 74LVC1G14) |
| J_VBAT | SM02B-GHS-TB-1MP | 1=VBAT_MON_P, 2=GND, MP=PGND | Battery voltage monitor (INA226 sense input) |
| J_FAN | SM03B-GHS-TB-1MP | 1=GND, 2=+5V, 3=FAN_PWM_A, MP=PGND | Bay ventilation fan PWM control |

**Notes:**

- GPS pin 3 (GPS_TX) connects to PocketBeagle 2 UART2_RX: the GPS module transmits, the SBC receives.
- GPS pin 4 (GPS_RX) connects to PocketBeagle 2 UART2_TX: the SBC transmits, the GPS module receives.
- SERVO_CH3 on J_SERVO pin 6 is a spare servo channel; populate as needed.
- J_1553 pin 4 is chassis shield drain; both pins 4 and MP connect to PGND to provide a
  dual-point shield termination compliant with MIL-STD-1553B stub cabling practice.
- All PGND connections float relative to signal GND except at the single-point star under J_PWR
  (0 Ω / 10 Ω solder-selectable link per §7 above).

---

## Known Issues

### `PB2-P2` header appears fully unwired (found 2026-07-26, unresolved)

`kicad-cli sch erc` reports every one of `PB2-P2`'s 36 pins as `pin_not_connected`, and
`kicad-cli sch export netlist` confirms zero nets reference `PB2-P2` at all — not even a
single-pin net. This is surprising: `WBS.md` §1.2a.1 records the ETH2/`PB2-P2` wiring
(RMII1, MDIO1/MDC1 on repurposed servo pins, etc.) as completed work back in 2026-06-12.

Investigation so far: `PB2-P2` uses the same `Conn_36` lib symbol as `PB2-P1`, whose pins
mostly **do** connect correctly (only 6 of 36 fail, all edge pins) — so the general
label-to-pin coincidence mechanism works in this file. Reconstructing the coordinate
transform from a known-good `PB2-P1` pin (`sheet_x = anchor_x + local_x`, `sheet_y =
anchor_y − local_y`, matching this project's documented KiCad hand-authoring convention)
and applying it to `PB2-P2` pin 1 predicts sheet position (67.54, 474.45) — and the
`MDIO1` global label sits at exactly that position. Despite the apparent exact coincidence,
KiCad does not merge the nets.

**Not resolved before this finding was recorded.** Next step is almost certainly to open
`Wash.kicad_sch` in the KiCad GUI and look at the `PB2-P2` block directly — something is
visually different there vs. `PB2-P1` that isn't obvious from the raw S-expression text
(a duplicate/orphaned object exactly on top of the label, a stray hierarchical sheet pin,
or a symbol instance issue are all plausible). **If this is a genuine defect, Wash's
ETH2/MDIO1 wiring has been silently non-functional** — treat as higher priority than the
rest of the pre-existing ERC/DRC backlog.

---

## Related Files

- `CAPE-A-1.kicad_sch` — standard (non-EMI-hardened) variant, Rev M baseline
- `AVIONICS_PB2_REDESIGN.md` — system architecture and power budgets
- `COMMO.md` — EMI-hardened 49 MHz transceiver, XCVR-49MHZ-2 (companion board)
- `TACCO.md` — EMI-hardened comms/logging cape (companion board)
- `Wash.kicad_sch` — schematic for this board (canonical filename: Wash.kicad_sch)

---

## References

1. TI Application Note SLLA337A — "Isolation Boundary Layout Guidelines for ISOW Devices"
2. Analog Devices ADM2795E Data Sheet Rev. B — isolation boundary capacitor guidance
3. Bourns SRF2012 Series Data Sheet — common-mode choke attenuation curves
4. IEC 62368-1:2018 Annex G — creepage/clearance for reinforced insulation [REF-IEC-001 §5.5.2]
5. IEC 61000-4-5:2014+AMD1:2017 — surge immunity test levels [REF-IEC-005]
6. MIL-STD-461G:2015 — EM emissions and susceptibility requirements for aircraft [REF-MIL-002]
7. Texas Instruments DP83825I Data Sheet (SNLS505C) — 10/100BASE-TX RMII PHY, RBIAS and bypass cap recommendations
8. Pulse Electronics HX1188NL Data Sheet — dual 10/100BASE-TX LAN transformer application circuit, center-tap termination
9. Texas Instruments TPS62933 Data Sheet (SLVSGM7) — 3.3V→1.8V SMPS, FB divider, output filter design
