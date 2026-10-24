# Pilot Interface Control Document: External Connectors

**Document:** Pilot-ICD-EXT, Revision A (draft for engineer review)  
**Applies to:** Pilot cape (CAPE-A-2) schematic `Pilot.kicad_sch`, 136 parts, ERC 0  
**Date:** 2026-10-19  
**Owner:** sgriffing (Griffing Technology LLC)  
**Prepared by:** Claude Sonnet 5.5 (Anthropic), via `scripts/gen_pilot_icd.py`  
**License:** CC BY-SA 4.0

> **Status:** the pin and net tables are generated from the netlist and are exact for
> the committed schematic. Items marked **OPEN** need an engineering decision or a
> document that is not on file. The PCB is not fully routed (130 connections open);
> this ICD describes the schematic, which is the controlling design.

## 1. Scope

This document defines every connector that crosses the Pilot cape's boundary except the
two PocketBeagle 2 Industrial rails, which are in `Pilot-ICD-PB2I.md`. Pin 1 is the pin
named `1` on the part's schematic symbol; physical pin-1 orientation is on the land
pattern (`Serenity-Custom.pretty`, `Connector_JST.pretty`).

Conventions: signal direction is from the Pilot cape's point of view. Voltage levels are
quoted only where a datasheet in `avionics/datasheets/` states them. Units are SI
for electrical quantities and imperial-primary for dimensions.

## 2. Interface summary

| Ref | Interface | Mating part | Pins |
| --- | --- | --- | ---: |
| PWR-IN | Power input | Molex Nano-Fit 105313-1204, 2.5 mm, 4 circuits (header) | 4 |
| CAN-FD | CAN FD field port (isolated) | JST SM04B-GHS-TB, 1.25 mm, 4 circuits | 4 |
| RS-485 | RS-485 field port (isolated) | JST SM04B-GHS-TB, 1.25 mm, 4 circuits | 4 |
| MIL-1553 | MIL-STD-1553B bus port (bus A) | JST SM04B-GHS-TB, 1.25 mm, 4 circuits | 4 |
| J-ETH-RMII2 | Ethernet port, RMII2 leg | JST SM04B-GHS-TB, 1.25 mm, 4 circuits | 4 |
| J-ETH-USB1 | Ethernet port, USB1 leg | JST SM04B-GHS-TB, 1.25 mm, 4 circuits | 4 |
| J-SPI | Expansion port (SPI2 / UART1 / UART6) | JST SM06B-GHS-TB, 1.25 mm, 6 circuits | 6 |
| J-PWM | Servo / ESC signal block | Samtec TSM-108-01-L-DV, 2 x 8, 2.54 mm (SMT male strip) | 16 |

## 3. Connector definitions

### 3.1 PWR-IN: Power input

* **Mating part:** Molex Nano-Fit 105313-1204, 2.5 mm, 4 circuits (header)
* **Contact rating:** OPEN: Molex 105313 drawing not on file (WBS 1.2a open gap); land not verified
* **Electrical class:** 5 V DC supply, both +5V_IN pins paralleled, both GND pins paralleled

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | +5V_IN | `+5V_IN` | In (power) | 5 V |
| 2 | +5V_IN | `+5V_IN` | In (power) | 5 V |
| 3 | GND | `GND` | Return |  |
| 4 | GND | `GND` | Return |  |

### 3.2 CAN-FD: CAN FD field port (isolated)

* **Mating part:** JST SM04B-GHS-TB, 1.25 mm, 4 circuits
* **Contact rating:** JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)
* **Electrical class:** Galvanically isolated, 5 000 Vrms (ISOW1044, REF-SENSOR-009), bus fault +/-58 V

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | GND | `GND2_CAN` | Isolated return |  |
| 2 | CAN_H | `CAN_H_F` | Bidirectional |  |
| 3 | CAN_L | `CAN_L_F` | Bidirectional |  |
| 4 | VCC | `VCC2_CAN` | Passive (isolated rail) | isolated 5 V (VISOIN) |
| shield / mounting tab | SHIELD | `PGND` | Chassis |  |

Termination: 120 R footprint (`R-CANT` / `R-485T`) is **DNP by default**; populate only at a bus end node.

### 3.3 RS-485: RS-485 field port (isolated)

* **Mating part:** JST SM04B-GHS-TB, 1.25 mm, 4 circuits
* **Contact rating:** JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)
* **Electrical class:** Galvanically isolated, 5 000 Vrms (ISOW1412, REF-SENSOR-010), 500 kbps

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | GND | `GND2_RS485` | Isolated return |  |
| 2 | A | `RS485_A_F` | Bidirectional |  |
| 3 | B | `RS485_B_F` | Bidirectional |  |
| 4 | VCC | `VCC2_RS485` | Passive (isolated rail) | isolated 5 V (VISOIN) |
| shield / mounting tab | SHIELD | `PGND` | Chassis |  |

Termination: 120 R footprint (`R-CANT` / `R-485T`) is **DNP by default**; populate only at a bus end node.

### 3.4 MIL-1553: MIL-STD-1553B bus port (bus A)

* **Mating part:** JST SM04B-GHS-TB, 1.25 mm, 4 circuits
* **Contact rating:** JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)
* **Electrical class:** Direct-coupled stub: PM-DB2791S 1:2.5 transformer, 2 x 55 R, 2 x SMAJ33CA (REF-MIL-001 sec 4.5.1.5.2, REF-SENSOR-025)

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | BUS_P | `BUS_1553_P` | Bidirectional |  |
| 2 | BUS_N | `BUS_1553_N` | Bidirectional |  |
| 3 | GND | `GND` | Return |  |
| 4 | SHIELD | `PGND` | Chassis |  |
| shield / mounting tab | SHIELD | `PGND` | Chassis |  |

Bus A only is populated; bus B is parked (REF-SENSOR-025).

### 3.5 J-ETH-RMII2: Ethernet port, RMII2 leg

* **Mating part:** JST SM04B-GHS-TB, 1.25 mm, 4 circuits
* **Contact rating:** JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)
* **Electrical class:** 10/100BASE-TX line side of the TC1G00 magnetics (1500 Vac, REF-SENSOR-061); Bob-Smith termination to PGND

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | TXP | `ETH_RMII2_LINE_TXP` | Out (TX pair) |  |
| 2 | TXN | `ETH_RMII2_LINE_TXN` | Out (TX pair) |  |
| 3 | RXP | `ETH_RMII2_LINE_RXP` | In (RX pair) |  |
| 4 | RXN | `ETH_RMII2_LINE_RXN` | In (RX pair) |  |
| shield / mounting tab | SHIELD | `PGND` | OPEN |  |

Each Ethernet pair is one `TC1G00` chip transformer (`T-<leg>-TX`, `-RX`); the pair is 100 ohm differential, 100BASE-TX.

### 3.6 J-ETH-USB1: Ethernet port, USB1 leg

* **Mating part:** JST SM04B-GHS-TB, 1.25 mm, 4 circuits
* **Contact rating:** JST GH: 1.0 A, 50 V AC/DC per contact, AWG 26-30 (eGH.pdf)
* **Electrical class:** 10/100BASE-TX line side of the TC1G00 magnetics (1500 Vac, REF-SENSOR-061); Bob-Smith termination to PGND

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | TXP | `ETH_USB1_LINE_TXP` | Out (TX pair) |  |
| 2 | TXN | `ETH_USB1_LINE_TXN` | Out (TX pair) |  |
| 3 | RXP | `ETH_USB1_LINE_RXP` | In (RX pair) |  |
| 4 | RXN | `ETH_USB1_LINE_RXN` | In (RX pair) |  |
| shield / mounting tab | SHIELD | `PGND` | OPEN |  |

Each Ethernet pair is one `TC1G00` chip transformer (`T-<leg>-TX`, `-RX`); the pair is 100 ohm differential, 100BASE-TX.

### 3.7 J-SPI: Expansion port (SPI2 / UART1 / UART6)

* **Mating part:** JST SM06B-GHS-TB, 1.25 mm, 6 circuits
* **Contact rating:** JST GH: 1.0 A, 50 V AC/DC per contact; cape fuse limits VCC to 0.35 A hold (Bourns MF-PSMF035X, REF-PWR-013)
* **Electrical class:** 3.3 V logic, ESD on all four signals (TPD4E05U06, REF-SENSOR-044)

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | VCC | `EXT_SPI_5V` | Out (fused 5 V) | 5 V (0.35 A fuse) |
| 2 | SCK | `EXT_SPI_SCK` | Out (SPI mode) |  |
| 3 | MISO | `EXT_SPI_MISO` | In (SPI mode) |  |
| 4 | MOSI | `EXT_SPI_MOSI` | Out (SPI mode) |  |
| 5 | SS1 | `EXT_SPI_SS1` | Out (SPI mode) |  |
| 6 | GND | `GND` | Return |  |
| shield / mounting tab | SHIELD | `PGND` | Chassis |  |

### 3.8 J-PWM: Servo / ESC signal block

* **Mating part:** Samtec TSM-108-01-L-DV, 2 x 8, 2.54 mm (SMT male strip)
* **Contact rating:** Samtec TSM series; no rating cited (REF-CONN-001 covers the land only)
* **Electrical class:** 3.3 V logic from PRU balls; 4 channels x (SIG, +5V, GND, PGND shield)

| Pin | Symbol function | Net | Direction | Level |
| --- | --- | --- | --- | --- |
| 1 | SIG0 | `DSHOT0` | Out |  |
| 2 | SIG2 | `DSHOT2` | Out |  |
| 3 | +5V_0 | `+5V` | Out (5 V rail) | 5 V |
| 4 | +5V_2 | `+5V` | Out (5 V rail) | 5 V |
| 5 | GND0 | `GND` | Return |  |
| 6 | GND2 | `GND` | Return |  |
| 7 | SHLD0 | `PGND` | Chassis |  |
| 8 | SHLD2 | `PGND` | Chassis |  |
| 9 | SIG1 | `DSHOT1` | Out |  |
| 10 | SIG3 | `DSHOT3` | Out |  |
| 11 | +5V_1 | `+5V` | Out (5 V rail) | 5 V |
| 12 | +5V_3 | `+5V` | Out (5 V rail) | 5 V |
| 13 | GND1 | `GND` | Return |  |
| 14 | GND3 | `GND` | Return |  |
| 15 | SHLD1 | `PGND` | Chassis |  |
| 16 | SHLD3 | `PGND` | Chassis |  |

## 4. Open items

1. **OPEN:** Molex 105313-1204 (PWR-IN) is not datasheet-verified (WBS 1.2a).
2. **OPEN:** JST GH and Samtec TSM ratings are quoted from `eGH.pdf`; neither is yet catalogued in `REFERENCES.md` with a verified URL (TODO).
3. **OPEN:** CAN-FD and RS-485 connector pin 4 (isolated VCC) current limit is not analysed; the ISOW DC-DC output budget has not been written down.
4. **OPEN:** mating-harness drawing and pin-1 marking convention for the cable ends.
5. **OPEN (owner):** J-PWM signal levels are 3.3 V from the AM625 PRU; confirm ESC inputs accept 3.3 V logic.
