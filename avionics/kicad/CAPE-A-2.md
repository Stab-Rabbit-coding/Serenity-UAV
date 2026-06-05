# CAPE-A-2 — EMI-Hardened Flight Control & Sensor Cape

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** A (EMI-hardened variant of CAPE-A-1 Rev M)
**Date:** 2026-06-02
**Status:** Schematic complete — PCB layout pending

---

## Purpose

CAPE-A-2 is an electromagnetic-environment-hardened variant of CAPE-A-1 (Rev M) intended
for operation in the nacelle bays and fuselage sections of the Serenity UAV where EDF motor
switching noise, high-current ESC PWM harmonics, and external RF threats require a higher
level of conducted and radiated immunity than the standard Rev M design provides.

This variant maintains full functional equivalence with CAPE-A-1: same PocketBeagle 2
Industrial (AM6254) host, same sensor suite, same bus topology. The changes are purely
protective hardening — no firmware or DTS changes are required.

---

## Changes from CAPE-A-1 (Rev M)

### 1. Ethernet PHY removal (space recovery)

The two DP83825I 100BASE-TX PHYs and their associated magnetics and RJ45-style connectors
are removed. The 18 PocketBeagle 2 P2 expansion-header pins formerly used for RMII0/1,
MDC, and MDIO are left as DNP (do-not-populate) / no-connect. The board-to-board
Ethernet ring remains available in the standard CAPE-A-1 variant; in CAPE-A-2 nodes,
inter-node communication relies on CAN FD (primary) and RS-485 (secondary) and
MIL-STD-1553. All three remaining buses carry adequate bandwidth for flight-critical
messaging in degraded connectivity scenarios.

**Rationale:** 100BASE-TX 100 MHz edge rates are a primary source of both conducted and
radiated EMI on the cape. Removing the PHYs eliminates this emission source and frees
approximately 12 × 10 mm of board area for EMI filter components.

### 2. CAN FD transceiver: ATA6561 → ISOW1044BDFMR

| Parameter | CAPE-A-1 | CAPE-A-2 |
| --- | --- | --- |
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

### 3. RS-485 transceiver: MAX3485E → ADM2795EBRWZ

| Parameter | CAPE-A-1 | CAPE-A-2 |
| --- | --- | --- |
| Part | MAX3485E (SOIC-8) | ADM2795EBRWZ (SOIC-20W) |
| Isolation | None (non-isolated) | 5000 V RMS reinforced (IEC 62368-1) |
| Surge / bus fault | ±12 V (standard RS-485) | ±42 V (exceeds IEC 61000-4-5 ±2 kV on bus) |
| Data rate | 32 Mbps | 20 Mbps |
| Supply | 3.3 V | 3.3 V VDD1; internal DC/DC generates VDD2 |
| Current | 3.5 mA | 25 mA (includes DC/DC) |
| DigiKey | — | ADM2795EBRWZ-ND |

The ADM2795EBRWZ is pin-logically compatible: DI, DE, RE_N, RO on the logic side have
the same polarity convention as the MAX3485E. The half-duplex direction-control scheme
(RS485_DE driving both DE and RE_N) is preserved unchanged.

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

  GND1 and GND2 copper pours on the ISOW1044BDFMR and ADM2795EBRWZ. Per IEC 62368-1
  Annex G, 5 kV reinforced isolation at 250 V working voltage requires ≥ 8 mm creepage
  in pollution degree 2 environment.

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
| --- | --- | --- |
| ETH1-PHY | DP83825I | Ethernet PHY — removed |
| ETH2-PHY | DP83825I | Ethernet PHY — removed |
| U10 (TPS62933) | 3.3→1.8 V SMPS for PHY AVDD | No longer required |
| ETH-P connector | JST-GH 6-pin | Ethernet port A — removed |
| ETH-N connector | JST-GH 6-pin | Ethernet port B — removed |
| CAN-TR (ATA6561) | Non-isolated CAN FD transceiver | Replaced by ISOW1044BDFMR |
| RS485 (MAX3485E) | Non-isolated RS-485 | Replaced by ADM2795EBRWZ |

### Added

| Reference | Part | Function |
| --- | --- | --- |
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
| +3V3 (LDO) | ICM-42688-P, BMP388, M10Q, SLB9670, ISOW1044BDFMR VCC1, ADM2795EBRWZ VDD1 | 600 mA |
| +3V3 isolated bus-side (VCC2/VDD2 — internal) | CAN bus stub loads, RS-485 line drivers | ≤ 150 mA combined (limited by ISOW1044B) |

DP83825I removal saves approximately 100 mA from the 3.3V rail (50 mA per PHY). Net 3.3V
budget is essentially unchanged due to new isolated transceiver overhead.

---

## EMC Compliance Targets

This variant is designed to achieve immunity per the following standards, applicable
to the Serenity UAV airframe operating environment:

| Standard | Level | Test | Notes |
| --- | --- | --- | --- |
| IEC 61000-4-2 | Level 4 (±8 kV contact, ±15 kV air) | ESD | TVS arrays at all field connectors |
| IEC 61000-4-4 | Level 4 (4 kV peak) | EFT/Burst on signal lines | CMCs + isolated transceivers |
| IEC 61000-4-5 | Level 3 (2 kV CM, 1 kV DM) | Surge | ±42 V bus fault on CAN/RS-485 |
| MIL-STD-461G RE102 | Limit C | Radiated emissions | No 100BASE-TX emission source |
| MIL-STD-461G RS103 | 200 V/m, 10 kHz–18 GHz | Radiated susceptibility | Isolated buses + chassis ground |

Pre-compliance testing against IEC 61000-4-2 through 4-5 is required before first
flight. Formal MIL-STD-461G testing is deferred pending airframe integration.

---

## Related Files

- `CAPE-A-1.kicad_sch` — standard (non-EMI-hardened) variant, Rev M baseline
- `AVIONICS_PB2_REDESIGN.md` — system architecture and power budgets
- `XCVR-49MHZ-2.md` — EMI-hardened 49 MHz transceiver (companion board)
- `CAPE-B-2.md` — EMI-hardened comms/logging cape (companion board)

---

## References

1. TI Application Note SLLA337A — "Isolation Boundary Layout Guidelines for ISOW Devices"

- Step 2: Analog Devices ADM2795E Data Sheet Rev. B — isolation boundary capacitor guidance

- Step 3: Bourns SRF2012 Series Data Sheet — common-mode choke attenuation curves

- Step 4: IEC 62368-1:2018 Annex G — creepage/clearance for reinforced insulation

- Step 5: IEC 61000-4-5:2017 — surge immunity test levels

- Step 6: MIL-STD-461G:2015 — EM emissions and susceptibility requirements for aircraft
