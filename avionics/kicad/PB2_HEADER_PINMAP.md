# PocketBeagle 2 Industrial — P1/P2 expansion header pin map (verified) and TACCO allocation

**Author:** Claude Fable 5.1, 2026-09-29, from the owner-supplied BeagleBoard.org PocketBeagle 2
schematic (`avionics/datasheets/pocketbeagle2_sch.pdf`, sheet "016_BP P1 & P2", v1.0) and the
board SysConfig (`avionics/datasheets/pocketbeagle-2.syscfg`, AM62x ALW package). Source
repository: <https://github.com/beagleboard/pocketbeagle> (BeagleBoard.org design files; the
schematic sheet itself carries no licence line — confirm the repository licence before
redistribution). **Owner:** S. Griffing. **License (this file):** CC BY-SA 4.0.

> **CAUTION — this map supersedes every earlier TACCO/Pilot header assumption.** The Rev S2
> TACCO generator (`gen_tacco_sch.py`, `PB2_P1`/`PB2_P2` tables before 2026-09-29) put **GND on
> P1-1/P1-2 (P1-1 is the PB2's 5 V VIN)**, +3V3/+5V on P1-33..36 (those are PRU/UART balls),
> MCAN0 on P1-15/16 (GND pins), SPI0 on P1-23..25 (ADC/GPIO balls) and SDIO on P2-1/2/19..22
> (MDC/PRU/GPIO balls). Plugging that board onto a PB2 would have shorted VIN to ground. The
> Pilot cape uses the same table family and must be checked the same way (`avionics/WBS.md`
> §1.2a, 2026-09-29 entry).

## 1. Header map (PB2 P1 / P2 as built)

Each position lists the AM6254 ball(s) wired to it and the pinmux options printed on the PB2
schematic. "+" means two balls are tied to one header pin (only one may be muxed active). ADC
positions (AIN0..AIN7) are 3.3 V-tolerant analog inputs that share the pin with a GPIO ball.

### P1

| Pin | Net / ball | Mux options (as printed) | Pin | Net / ball | Mux options |
| --- | --- | --- | --- | --- | --- |
| 1 | **VIN** (5 V in) | power | 2 | AA19 (+AIN6) | RMII2_TX_EN, GPIO0_87 |
| 3 | F18 | USB1_DRVVBUS, GPIO1_51 | 4 | Y18 | RMII2_TXD0, GPIO0_89 |
| 5 | USB1 VBUS | power | 6 | E19 | SPI2_CS0, UART1_RXD, EHRPWM0_A, GPIO1_13 |
| 7 | VIN.USB (USB_5V) | power | 8 | A20 | SPI2_CLK, UART1_TXD, EHRPWM0_B, GPIO1_14 |
| 9 | USB1 D− | USB | 10 | B19 (+A18) | SPI2_D0, UART1_CTSn, UART6_RXD, GPIO1_7 (+EXT_REFCLK1, GPIO1_30) |
| 11 | USB1 D+ | USB | 12 | A19 (+AE18) | SPI2_D1, UART1_RTSn, UART6_TXD, GPIO1_8 (+GPIO0_77) |
| 13 | N20 | USB1_ID, GPIO0_36 | 14 | **VDD_3V3** (out) | power |
| 15 | **GND** | | 16 | **GND** | |
| 17 | AIN VREF− | analog | 18 | AIN VREF+ (0 Ω to 3V3) | analog |
| 19 | AIN0 + AD22 | RMII2_RX_ER, GPIO1_1 | 20 | Y24 | UART4_TXD, GPIO0_50 |
| 21 | AIN1 + AE22 | GPIO1_6 | 22 | **GND** | |
| 23 | AIN2 + AC21 | GPIO1_5 | 24 | **VOUT** (VSYS) | power |
| 25 | AIN3 + AB20 | RMII2_RXD1, GPIO1_4 | 26 | K24 (+D6) | I2C2_SDA, UART4_TXD, GPIO0_44 (+MCU_MCAN0_TX) |
| 27 | AIN4 + AE23 | RMII2_RXD0, GPIO1_3 | 28 | K22 (+B3) | I2C2_SCL, UART4_RXD, GPIO0_43 (+MCU_MCAN0_RX) |
| 29 | Y20 | PRU0.7, UART3_CTSn, GPIO0_62 | 30 | E14 | UART0_TXD, EHRPWM2_B, GPIO1_21 |
| 31 | Y22 | PRU0.4, UART4_RTSn, GPIO0_59 | 32 | D14 | UART0_RXD, EHRPWM2_A, GPIO1_20 |
| 33 | AA23 (+A17) | PRU0.1, UART6_CTSn, GPIO0_56 (+I2C1_SDA, UART1_TXD, GPIO1_29) | 34 | AD23 | RMII2_REF_CLK, GPIO1_2 |
| 35 | AE21 | PRU1.1, RMII2_CRS_DV, GPIO0_88 | 36 | V20 (+B17) | UART6_RTSn, GPIO0_55 (+I2C1_SCL, UART1_RXD, EHRPWM2_A, GPIO1_28) |

### P2

| Pin | Net / ball | Mux options | Pin | Net / ball | Mux options |
| --- | --- | --- | --- | --- | --- |
| 1 | B20 (+AD24) | ECAP2_IN_APWM_OUT, GPIO1_11 (+MDIO0_MDC) | 2 | U22 | PRU1.0, UART2_RXD, GPIO0_45 |
| 3 | B18 (+AB22) | EHRPWM1_A, GPIO1_9 (+MDIO0_MDIO) | 4 | V24 | PRU1.1, UART2_TXD, GPIO0_46 |
| 5 | C15 (+B5) | **MCAN0_TX**, UART5_RXD, GPIO1_24 (+MCU_UART0_RXD) | 6 | W25 | PRU1.2, UART3_RXD, GPIO0_47 |
| 7 | E15 (+A5) | **MCAN0_RX**, UART5_TXD, GPIO1_25 (+MCU_UART0_TXD) | 8 | W24 | PRU1.3, UART3_TXD, GPIO0_48 |
| 9 | A15 (+D4) | UART0_CTSn, SPI0_CS2, I2C3_SCL, UART2_RXD, GPIO1_22 (+MCU_MCAN1_RX) | 10 | AD21 | PRU1.4, GPIO0_91 |
| 11 | B15 (+E5) | UART0_RTSn, SPI0_CS3, I2C3_SDA, UART2_TXD, GPIO1_23 (+MCU_MCAN1_TX) | 12 | PWR_BTN | control |
| 13 | **VOUT** (VSYS) | power | 14 | BAT VIN | power |
| 15 | **GND** | | 16 | BAT TEMP | analog |
| 17 | AC24 | PRU1.19, UART2_CTSn, GPIO0_64 | 18 | V21 | UART6_RXD, GPIO0_53 |
| 19 | AC20 | PRU1.16, PR0_UART0_CTSn, GPIO1_0 | 20 | Y25 | UART4_RXD, GPIO0_49 |
| 21 | **GND** | | 22 | AC25 | UART2_RTSn, GPIO0_63 |
| 23 | **VDD_3V3** (out) | power | 24 | Y23 | UART5_RXD, GPIO0_51 |
| 25 | B14 | **SPI0_D1 (MOSI)**, GPIO1_19 | 26 | nRESET | control |
| 27 | B13 | **SPI0_D0 (MISO)**, GPIO1_18 | 28 | AB24 | PRU1.15, UART3_RTSn, GPIO0_61 |
| 29 | A14 (+M22) | **SPI0_CLK**, GPIO1_17 (+GPIO0_40) | 30 | AA24 | PRU1.12, UART5_CTSn, GPIO0_58 |
| 31 | A13 (+AA18) | SPI0_CS0, GPIO1_15 (+**RMII2_TXD1**, GPIO0_90) | 32 | AB25 | PRU1.11, UART5_RTSn, GPIO0_57 |
| 33 | AA25 | UART5_TXD, GPIO0_52 | 34 | AA21 | PRU1.14, UART4_CTSn, GPIO0_60 |
| 35 | AIN5 + W21 | UART6_TXD, GPIO0_54 | 36 | AIN7 + C13 | SPI0_CS1, GPIO1_16 |

**Not on the headers:** MMC2 (SDIO) CLK/CMD/DAT0..3 (balls D25, C24, B24, C25, E23, D24 stay on
the PB2), RMII0/RGMII1 (used by the PB2's own Ethernet), OSPI, MCASP data. **USB1** (D−/D+,
VBUS, DRVVBUS, ID) is on P1-3/5/9/11/13 and is the only high-bandwidth peripheral interface
available to a cape besides SPI0.

## 2. TACCO allocation (2026-09-29 proposal, replaces `PB2_P1`/`PB2_P2` in `gen_tacco_sch.py`)

Fixed-function assignments first (the peripheral decides the pin); GPIO-class nets fill the
remaining positions. 24 GPIO-class nets are needed and 25 GPIO-capable positions remain, so the
header is fully subscribed: **no contiguous unused run is available** (the 2026-09-29 P2-3..10
gap idea is withdrawn — P2-5/7 are the only MCAN0 pins).

| Function | TACCO net | Position(s) | Ball | Note |
| --- | --- | --- | --- | --- |
| 5 V in from cape | +5V | P1-1 (VIN), P1-7 (VIN.USB) | | cape supplies the PB2 |
| 3V3 from PB2 | +3V3_PB2 | P1-14, P2-23 | | |
| GND | GND | P1-15, P1-16, P1-22, P2-15, P2-21 | | |
| Reset | PB2_RESET_N | P2-26 | | test point only |
| CAN FD | MCAN0_B_TX / MCAN0_B_RX | P2-5 / P2-7 | C15 / E15 | |
| CAN standby | CAN_B_STB | P2-2 | U22 | GPIO0_45 |
| RS-485 UART | RS485_B_TX / RS485_B_RX | P2-11 / P2-9 | B15 / A15 | UART2 |
| RS-485 DE | RS485_B_DE | P2-22 | AC25 | UART2_RTSn (hardware DE) |
| mLRS UART | UART_WIOE5_TX / _RX | P1-30 / P1-32 | E14 / D14 | UART0 (net names kept for the DTS) |
| BT UART | BT_UART_TX / RX / RTS / CTS | P1-8 / P1-6 / P1-12 / P1-10 | A20 / E19 / A19 / B19 | UART1 with flow control |
| SPI0 | SPI0_B_MOSI / MISO / CLK | P2-25 / P2-27 / P2-29 | B14 / B13 / A14 | |
| TPM CS | SPI0_B_CS_TPM | P2-36 | C13 | SPI0_CS1 |
| 1553 CS | SPI0_B_CS_1553 | P2-24 | Y23 | GPIO0_51 |
| Flash CS | SPI0_B_CS_FLASH | P2-30 | AA24 | GPIO0_58 |
| 802.15.4 CS / IRQ | SPI0_B_CS_ZB / ZB_SPI_INT | P2-32 / P2-34 | AB25 / AA21 | |
| Ethernet RMII | RMII2_TX_EN / TXD0 / TXD1 | P1-2 / P1-4 / P2-31 | AA19 / Y18 / AA18 | was RMII0_* |
| | RMII2_RX_ER / RXD1 / RXD0 | P1-19 / P1-25 / P1-27 | AD22 / AB20 / AE23 | |
| | RMII2_REF_CLK / CRS_DV | P1-34 / P1-35 | AD23 / AE21 | |
| MDIO | MDC0 / MDIO0 | P2-1 / P2-3 | AD24 / AB22 | |
| PHY control | PHY1_RSTN / PHY1_INTRN | P2-4 / P2-6 | V24 / W25 | |
| 1553 control | M1553B_IRQN / MRN / TX_INH | P2-8 / P2-10 / P2-17 | W24 / AD21 / AC24 | |
| TPM control | TPM_B_RSTN / TPM_B_IRQN | P2-18 / P2-19 | V21 / AC20 | |
| microSD detect | SD_CD | P2-20 | Y25 | |
| Wi-Fi control | WIFI_EN / WIFI_IRQ | P2-28 / P2-33 | AB24 / AA25 | pending host-interface decision (§3) |
| Fan | FAN_PWM_B | P1-36 | B17 | EHRPWM2_A |
| PLD interlock | PLD_CLK, PLD_I1..I8 | P1-13, P1-20, P1-21, P1-23, P1-26, P1-28, P1-29, P1-31, P1-33 | N20, Y24, AE22, AC21, K24, K22, Y20, Y22, AA23 | GPIO |
| USB host | USB1_DM / USB1_DP / USB1_VBUS / USB1_ID | P1-9 / P1-11 / P1-5 / P1-13* | | *P1-13 reassigned to PLD_CLK if USB ID is unused; see §3 |
| spare | — | P2-35 | W21 | |

## 3. Open decision — Wi-Fi/BT/802.15.4 host interface

The Murata Type 2EL (NXP IW612) WLAN core is **SDIO-only**; BT is UART and 802.15.4 is SPI.
The PB2 does not bring MMC2/SDIO to the headers, so WLAN cannot be hosted as designed. Options
for the owner: (a) a USB-attached Wi-Fi/BT module on USB1 (P1-9/11) plus the 802.15.4 radio on
SPI0 (module change; keeps all three radios on TACCO); (b) keep Type 2EL with BT + 802.15.4
only and provide Wi-Fi from a USB module elsewhere; (c) move Wi-Fi to another node. Recorded in
`avionics/WBS.md` §1.2a (2026-09-29 entry).

## 4. Firmware notes

`avionics/datasheets/pocketbeagle-2.syscfg` is BeagleBoard's TI SysConfig for the base board
(UART0 = console on P1-30/32, SPI0 = "SPI0", MCAN0, PRU0/PRU1, RGMII2 unused). The TACCO DTS
overlay must mux: MCAN0 (C15/E15), UART2 (A15/B15/AC25), UART1 (E19/A20/B19/A19), SPI0
(B14/B13/A14/C13), RMII2 + MDIO0, EHRPWM2_A (B17), and the GPIOs above (mux mode 7). The PB2's
UART0 console moves to the mLRS link, so the console must be re-pointed (USB or UART5).
