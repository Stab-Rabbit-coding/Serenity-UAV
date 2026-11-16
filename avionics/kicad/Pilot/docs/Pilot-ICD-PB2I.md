# Pilot Interface Control Document: PocketBeagle 2 Industrial Headers

**Document:** Pilot-ICD-PB2I, Revision A (draft for engineer review)  
**Date:** 2026-10-19  
**Prepared by:** Claude Sonnet 5.5 (Anthropic), via `scripts/gen_pilot_icd.py`  
**License:** CC BY-SA 4.0

## 1. Scope

Pilot is a cape for the PocketBeagle 2 Industrial (AM625). Two 2 x 18, 2.54 mm Samtec
TSM-118-04-L-DV-LC SMT male strips (`PB2-P1`, `PB2-P2`) mate with the PB2-I's female
receptacles. Pin names follow the BeagleBoard SRM designators `P1.01` to `P2.36`
[REF-SENSOR-041 sec 4.2]. The cape drives none of: P1-14 / P2-23 (PB2 3.3 V out),
P1-24 / P2-13 (VSYS), P2-14 (VBAT), P2-16 (BAT_TS), P2-12 (PWR_BTN), P2-26 (RESET#),
P1-7 (VIN.USB), P1-17/18 (AIN references), P1-30/32 (UART0 console).

The source of every row below is `PB2_P1` / `PB2_P2` in `gen_pilot_sch.py`; the ball
text is that table's own comment. Full mux options per ball are in
`../PB2I_AM625_HEADER_CAPABILITIES.md` section 4 [REF-SENSOR-049].

> **Firmware rule:** where a header pin carries two AM625 balls, the second ball must be
> held as a GPIO input with no pull by the device tree. P1-19/21/23/25/27 and P2-35/36
> are also MSPM0L1105 AIN inputs; wiring never depends on firmware state alone.

## P1

| Pin | Net | Ball / function (from schematic generator) |
| --- | --- | --- |
| P1.01 | `+5V` | VIN 5 V in (cape powers the PB2-I) |
| P1.02 | `RMII2_TX_EN` | AA19 RMII2_TX_EN (E18 GPIO1_10 left input) |
| P1.03 | `SPI0_CS_IMU` | F18 GPIO1_51 (GPIO chip select, next to the IMU) |
| P1.04 | `RMII2_TXD0` | Y18 RMII2_TXD0 (D20 left input) |
| P1.05 | `+5V` | USB1_VBUS: cape-supplied VBUS (PB2-I divides 1k/20k to AB10) |
| P1.06 | `EXT_SPI_SS1` | E19 SPI2_CS0 (AD18 left input) |
| P1.07 | (not connected) | VIN.USB |
| P1.08 | `EXT_SPI_SCK` | A20 SPI2_CLK |
| P1.09 | `USB1_DM` | AD10 USB1_DM -> AX88772E USB_DM |
| P1.10 | `EXT_SPI_MISO` | B19 SPI2_D0 (A18 left input) |
| P1.11 | `USB1_DP` | AE9 USB1_DP -> AX88772E USB_DP |
| P1.12 | `EXT_SPI_MOSI` | A19 SPI2_D1 (AE18 left input) |
| P1.13 | `DSHOT1` | N20 PR0_PRU0_GPO13 |
| P1.14 | (not connected) | VDD_3V3 out of the PB2 (cape has its own +3V3) |
| P1.15 | `GND` |  |
| P1.16 | `GND` |  |
| P1.17 | (not connected) | AIN.VREF- |
| P1.18 | (not connected) | AIN.VREF+ |
| P1.19 | `RMII2_RX_ER` | AD22 RMII2_RX_ER (+AIN0) |
| P1.20 | `TPM_IRQN` | Y24 GPIO0_50 |
| P1.21 | `DSHOT3` | AE22 PR0_PRU0_GPO16 (+AIN1) |
| P1.22 | `GND` |  |
| P1.23 | `DSHOT0` | AC21 PR0_PRU0_GPO4 (+AIN2) |
| P1.24 | (not connected) | VOUT (VSYS) |
| P1.25 | `RMII2_RXD1` | AB20 RMII2_RXD1 (+AIN3) |
| P1.26 | `SPI0_CS_TPM` | K24 GPIO0_44 (D6 left input) — beside the TPM |
| P1.27 | `RMII2_RXD0` | AE23 RMII2_RXD0 (+AIN4) |
| P1.28 | `TPM_RSTN` | K22 GPIO0_43 (B3 left input) |
| P1.29 | `DSHOT2` | Y20 PR0_PRU0_GPO7 |
| P1.30 | (not connected) | E14 UART0_TXD — PB2 console, left free |
| P1.31 | `NIC-USB1_VBUS` | Y22 GPIO0_59 — AX88772E VBUS detach over 4.7 k pull-up (owner) |
| P1.32 | (not connected) | D14 UART0_RXD — PB2 console, left free |
| P1.33 | (not connected) | A17 I2C1_SDA (AA23 left input) — spare (was J-GPS, removed 2026-10-18) |
| P1.34 | `RMII2_REF_CLK` | AD23 RMII2_REF_CLK |
| P1.35 | `RMII2_CRS_DV` | AE21 RMII2_CRS_DV |
| P1.36 | (not connected) | B17 I2C1_SCL (V20 left input) — spare (was J-GPS, removed 2026-10-18) |

## P2

| Pin | Net | Ball / function (from schematic generator) |
| --- | --- | --- |
| P2.01 | `MDC0` | AD24 MDIO0_MDC (B20 left input) |
| P2.02 | (not connected) | U22 UART2_RXD — spare (was J-GPS, removed 2026-10-18) |
| P2.03 | `MDIO0` | AB22 MDIO0_MDIO (B18 left input) |
| P2.04 | (not connected) | V24 UART2_TXD — spare (was J-GPS, removed 2026-10-18) |
| P2.05 | `MCAN0_TX` | C15 MCAN0_TX (B5 left input) |
| P2.06 | `M1553_MRN` | W25 GPIO0_47 |
| P2.07 | `MCAN0_RX` | E15 MCAN0_RX (A5 left input) |
| P2.08 | `M1553_TX_INH` | W24 GPIO0_48 |
| P2.09 | `SPI0_CS_1553` | A15 SPI0_CS2 (D4 left input) |
| P2.10 | `CAN_STB` | AD21 GPIO0_91 |
| P2.11 | `SPI0_CS_BARO` | B15 SPI0_CS3 (E5 left input) |
| P2.12 | (not connected) | PWR_BTN |
| P2.13 | (not connected) | VOUT (VSYS) |
| P2.14 | (not connected) | BAT.VIN |
| P2.15 | `GND` |  |
| P2.16 | (not connected) | BAT.TEMP |
| P2.17 | `M1553_IRQN` | AC24 GPIO0_64 |
| P2.18 | `BARO_INT` | V21 GPIO0_53 |
| P2.19 | `IMU_INT1` | AC20 GPIO1_0 |
| P2.20 | `RMII2_PHY_RSTN` | Y25 GPIO0_49 (DP83825I reset) |
| P2.21 | `GND` |  |
| P2.22 | `IMU_INT2` | AC25 GPIO0_63 |
| P2.23 | (not connected) | VDD_3V3 out of the PB2 |
| P2.24 | `RS485_RX` | Y23 UART5_RXD |
| P2.25 | `SPI0_MOSI` | B14 SPI0_D1 |
| P2.26 | (not connected) | RESET# |
| P2.27 | `SPI0_MISO` | B13 SPI0_D0 |
| P2.28 | `RMII2_PHY_INTRN` | AB24 GPIO0_61 (DP83825I interrupt) |
| P2.29 | `SPI0_CLK` | A14 SPI0_CLK (M22 left input) |
| P2.30 | (not connected) | AA24 GPIO0_58 — spare |
| P2.31 | `RMII2_TXD1` | AA18 RMII2_TXD1 (A13 SPI0_CS0 left input) |
| P2.32 | `RS485_DE` | AB25 UART5_RTSn (hardware RS-485 direction) |
| P2.33 | `RS485_TX` | AA25 UART5_TXD |
| P2.34 | (not connected) | AA21 GPIO0_60 — spare |
| P2.35 | (not connected) | W21 GPIO0_54 (+AIN5) — spare |
| P2.36 | (not connected) | C13 SPI0_CS1 (+AIN7) — spare |

## Open items

1. **OPEN:** P1-31 (`NIC-USB1_VBUS`, GPIO0_59) must idle as a high-impedance input; the device-tree overlay does not exist yet (WBS 1.2a Pilot firmware items).
2. **OPEN:** RMII2 timing with the MSPM0 AIN load (5 pF per pin) is verified at bring-up, not by analysis (owner decision 2026-10-17).
