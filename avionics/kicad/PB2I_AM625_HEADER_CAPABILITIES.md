# PocketBeagle 2 Industrial — AM625 pin-mux capabilities on the P1/P2 headers

**Author:** Claude Opus 5.5 (AI), 2026-10-17, at the request of the owner (Stab-Rabbit-coding).
**License (this file):** CC BY-SA 4.0. **Status:** reference data, extracted from TI and
BeagleBoard.org documents; no design decision is made in this file.

**Sources:**

- [REF-SENSOR-049] TI SPRSP58C, *AM62x Sitara Processors* data sheet (rev. October 2025):
  §1 Features, Table 4-1 Device Comparison, §5.2 Table 5-1 Pin Attributes (ALW package),
  §5.3.1 Tables 5-2 to 5-5 (CPSW3G RGMII1/RGMII2/RMII1/RMII2 signal descriptions).
- [REF-SENSOR-050] TI SPRUIV7C, *AM62x Processors Technical Reference Manual* (rev. November
  2025): §1.4.12 CPSW3G features, §4.10.1.1 CPSW unsupported features.
- [REF-SENSOR-041] BeagleBoard.org *PocketBeagle 2 System Reference Manual*, §4.2
  "Cape Header Connectors" (header ball and mux tables).
- [REF-SENSOR-021] BeagleBoard.org PocketBeagle 2 schematic, sheet "016_BP P1 & P2" and
  sheet "015_SoC JTAG & MISC" (U11, MSPM0L1105TRGER).
- [REF-SENSOR-051] TI SLASEX5C, *MSPM0L1105, MSPM0L1106* data sheet (rev. January 2024):
  §1 Features, Table 6-1 Pin Attributes, §7.1 Absolute Maximum Ratings, digital I/O
  characteristics (RPU, RPD, CI), §8.12 ADC.
- [REF-SENSOR-052] TI SLAU847F, *MSPM0 L-Series 32-MHz Microcontrollers Technical Reference
  Manual* (rev. March 2026): §2.4.1.2 Initial Conditions After Power-Up, §8.2 IOMUX Operation
  (default IOMUX state).

The machine-readable form of §4 is
`avionics/datasheets/extracted/AM625_PB2I_header_mux.json` (header pin → ball → mux modes).

## 1. Why this file exists

The owner noted on 2026-10-17 that the AM625 data sheet (page 2) lists two Ethernet ports, and
that earlier work had read the SoC's capabilities from the PocketBeagle 2 System Reference
Manual (SRM) summary instead of the data sheet. This file records what the data sheet's own
pin-mux table (Table 5-1) allows on every ball that reaches the PB2-I P1/P2 headers, so that
pin allocation on the Pilot and TACCO capes can be checked against the SoC, not against a
board-level summary.

The PB2-I and the PB2 share one design repository; the PB2-I adds 1 GB DDR4, 64 GB eMMC and
a -40 to 85 °C rating [REF-SENSOR-047]. The header wiring is the same, so this file applies to
both.

## 2. Corrected assumptions

| Earlier assumption | What the sources say | Source |
| --- | --- | --- |
| "Only RMII2 reaches the header, so the SoC has one usable Ethernet port." | The CPSW3G switch has **two external ports** (RMII or RGMII each) plus one internal CPPI port. Port 1's balls (RGMII1/RMII1: AD17, AE17, AE19, AD19, AB17, AC17, AB16, AA15, AE20, AD20) have **no alternate ball** in Table 5-2/5-4 and none of them reaches P1/P2. Only RGMII1_TD2 (AE18, P1-12 second ball) and RGMII1_TD3 (AD18, P1-6 second ball) reach the header, which is not a usable interface. **Port 2's balls are all on the header**, as RMII2 or as **RGMII2** (all 12 RGMII2 balls). Gigabit operation through the header is unverified (see next row). | [REF-SENSOR-049 §1, Tables 5-2 to 5-5]; [REF-SENSOR-050 §1.4.12] |
| The cape cannot use a gigabit MAC interface. | RGMII2 (TXC, TX_CTL, TD0..3, RXC, RX_CTL, RD0..3) is on P1-2, P1-4, P1-19, P1-21, P1-23, P1-25, P1-27, P1-34, P1-35, P2-10, P2-19, P2-31. Using it costs four more header pins than RMII2 (P1-21, P1-23, P2-10, P2-19). Eight of the 12 signals carry an on-board stub on the PB2-I (a second SoC ball or an MSPM0 AIN pin, §6), and the PB2-I routing has not been checked against the data sheet's RGMII timing limits, so gigabit RGMII2 through the header **requires verification** before any adoption. | [REF-SENSOR-049 Table 5-3] |
| The two external CPSW ports could form the ring in hardware. | They could on a board that brings out both ports, but on the PB2-I only port 2 is reachable. A cape ring therefore needs a second MAC outside the CPSW (the owner's 2026-10-17 choice: PHY on RMII2 plus a USB NIC on USB1), and forwarding between the two is done by the Linux bridge, not by the CPSW's wire-rate switch fabric. | [REF-SENSOR-050 §1.4.12] |
| One CAN-FD bus on the header (MCAN0). | The SoC has **3 MCAN modules** with CAN FD. All three reach the header: MCAN0 (P2-5/P2-7), **MCU_MCAN0** (TX P1-26 ball D6, RX P1-28 ball B3) and **MCU_MCAN1** (TX P2-11 ball E5, RX P2-9 ball D4). Each MCU_MCAN pair shares its header pins with a MAIN-domain ball, so only one of the two balls on each pin shall be driven. | [REF-SENSOR-049 §1, Table 4-1, Table 5-1] |
| Few I2C/UART options. | Header-reachable: I2C1, I2C2, I2C3; UART0..UART6, MCU_UART0 and PR0_UART0 (see §4). UART1, UART2, UART3, UART4, UART5 and UART6 have both RTSn and CTSn on the header. | [REF-SENSOR-049 Table 5-1] |
| "MCASP data and MMC2 are not on the headers" (PB2_HEADER_PINMAP.md §1 footnote, before 2026-10-17). | MMC2 CLK/CMD/DAT are not on the header (correct), but MMC2_SDWP (P1-33 ball A17, and P2-11) and MMC2_SDCD (P1-36 second ball B17, and P2-9) are. McASP0 has a full serializer set on the header (ACLKX/R, AFSX/R, AXR0..3) and McASP2 has clocks, frame syncs and many AXR pins. | [REF-SENSOR-049 Table 5-1] |
| P1-2, P1-4, P1-6 each carry one SoC ball. | Each carries **two** SoC balls: P1-2 = E18 + AA19 (plus AIN6), P1-4 = D20 + Y18, P1-6 = E19 + AD18. The SRM tables and the PB2 schematic both show the second ball; `PB2_HEADER_PINMAP.md` §1 had omitted it (corrected 2026-10-17). | [REF-SENSOR-041 §4.2]; [REF-SENSOR-021] |
| SRM shows "SPI2_DI" on P1-12 (ball A19, mode 1). | The data sheet signal is **SPI2_D1**; "SPI2_DI" is a typo in the SRM. | [REF-SENSOR-049 Table 5-1]; [REF-SENSOR-041 §4.2] |

> **CAUTION** — Seventeen header pins are wired to two SoC balls, and eight header pins are
> also wired to an MSPM0L1105 pin (§6). Only
> one ball on each pin shall be configured as an output; the other shall be left in its
> reset (input, no pull) state or muxed to a GPIO input. Driving both balls at once shorts
> two SoC outputs together and can damage the AM625. Pins with two balls: P1-2, P1-4, P1-6,
> P1-10, P1-12, P1-26, P1-28, P1-33, P1-36, P2-1, P2-3, P2-5, P2-7, P2-9, P2-11, P2-29, P2-31.

<!-- separate callouts -->

> **NOTE** — The owner's rule (2026-10-17) is that hardware wiring is not decided from
> firmware remapping alone. The tables below say what the SoC *allows*; each use still needs
> the PB2-I schematic check (I/O voltage domain of the ball, any on-board pull, filter or
> second ball) before a cape wire is committed.

## 3. Pin-allocation opportunities for the Pilot cape

> **NOTE** — Owner decisions 2026-10-17: the extra CAN-FD buses below are **rejected** (the
> fleet's four buses already cover the need), and moving RMII2 or DSHOT off the MSPM0-shared
> pins is **rejected** (§6). The items stay here as capability records only.


- **Up to three CAN-FD buses.** MCU_MCAN0 is on P1-26/P1-28 (Pilot today: SPI0_CS_TPM and
  TPM_RSTN, both GPIO-driven, so they can move to spare GPIO pins). MCU_MCAN1 is on P2-9/P2-11
  (Pilot today: SPI0_CS_1553 and SPI0_CS_BARO, which are the **hardware** chip selects
  SPI0_CS2/SPI0_CS3 and exist on no other header ball). Freeing P2-9/P2-11 leaves SPI0_CS1
  (P2-36, shared with MSPM0 AIN7) as the only spare hardware chip select, so one of the two
  devices would move to a GPIO-driven chip select. Balls D6, B3, D4 and E5 are powered from
  VDDSHV_CANUART, 1.8 V / 3.3 V LVCMOS [REF-SENSOR-049 Table 5-1], which the PB2 schematic
  ties to VDD_3V3 (decoupling group "VDDSHV0,1,2,3,5,6,CANUART,MCU"; label "CANUART 3.3V")
  [REF-SENSOR-021], so they are 3.3 V I/O. Whether the Linux SDK exposes MCU-domain MCAN to
  the A53 cores is not covered by these sources (requires verification).
- **RMII2 vs. RGMII2.** The Pilot uses RMII2 (100 Mbit/s). RGMII2 would allow a gigabit PHY
  but uses four more header pins, needs a gigabit PHY and magnetics, and is unverified through
  the PB2-I's stubbed routing (§2); the 100 Mbit/s ring does not need it.
- **IEEE 1588 hardware timestamp pins.** CPTS0 HW1/HW2 timestamp-push inputs (P2-27, P2-25),
  TS_SYNC (P2-29), TS_COMP (P2-36) and the CPTS reference clock input (P1-10) are on the
  header. P2-25/27/29 are SPI0 on the Pilot, so using them would move SPI0.
- **Spare-pin protocol choice for the GH expansion port.** SPI2 (P1-6/8/10/12, alternates
  P1-30/32/33), I2C1/I2C2/I2C3, UART1..UART6 and eHRPWM/eCAP/eQEP are all reachable; see §4.

## 4. Header ball mux table (SPRSP58C Table 5-1, ALW package)

Pins marked "A" are the second SoC ball tied to the same header pin (SRM naming). P1-2,
P1-19, P1-21, P1-23, P1-25, P1-27, P2-35 and P2-36 also carry an MSPM0L1105 pin (AIN6, AIN0 to
AIN5, AIN7; §6). Power,
ground, analog-only (AIN, VREF), battery, reset and power-button pins have no SoC mux and are
listed in `PB2_HEADER_PINMAP.md` §1.

| Header pin | Ball | Mux modes (mode: signal) |
| --- | --- | --- |
| P1.02 | E18 | 0: MCASP0_AXR0; 1: PR0_ECAP0_IN_APWM_OUT; 2: AUDIO_EXT_REFCLK0; 5: PR0_UART0_TXD; 6: EHRPWM1_B; 7: GPIO1_10; 8: EQEP0_I |
| P1.02A | AA19 | 0: RGMII2_TX_CTL; 1: RMII2_TX_EN; 2: MCASP2_AXR4; 3: PR0_PRU1_GPO0; 4: PR0_PRU1_GPI0; 7: GPIO0_87 |
| P1.03 | F18 | 0: USB1_DRVVBUS; 7: GPIO1_51 |
| P1.04 | D20 | 0: MCASP0_AFSX; 1: SPI2_CS3; 2: AUDIO_EXT_REFCLK1; 7: GPIO1_12; 8: EQEP1_B |
| P1.04A | Y18 | 0: RGMII2_TD0; 1: RMII2_TXD0; 2: MCASP2_AXR6; 3: PR0_PRU1_GPO2; 4: PR0_PRU1_GPI2; 7: GPIO0_89 |
| P1.05 | AB10 | fixed function (USB1) |
| P1.06 | E19 | 0: MCASP0_AFSR; 1: SPI2_CS0; 2: UART1_RXD; 6: EHRPWM0_A; 7: GPIO1_13; 8: EQEP1_S |
| P1.06A | AD18 | 0: RGMII1_TD3; 2: PR0_UART0_TXD; 7: GPIO0_78 |
| P1.08 | A20 | 0: MCASP0_ACLKR; 1: SPI2_CLK; 2: UART1_TXD; 6: EHRPWM0_B; 7: GPIO1_14; 8: EQEP1_I |
| P1.09 | AD10 | fixed function (USB1) |
| P1.10 | A18 | 0: EXT_REFCLK1; 1: SYNC1_OUT; 2: SPI2_CS3; 3: SYSCLKOUT0; 4: TIMER_IO4; 5: CLKOUT0; 6: CP_GEMAC_CPTS0_RFT_CLK; 7: GPIO1_30; 8: ECAP0_IN_APWM_OUT |
| P1.10A | B19 | 0: MCASP0_AXR3; 1: SPI2_D0; 2: UART1_CTSn; 3: UART6_RXD; 4: PR0_IEP0_EDIO_DATA_IN_OUT28; 5: ECAP1_IN_APWM_OUT; 6: PR0_UART0_RXD; 7: GPIO1_7; 8: EQEP0_A |
| P1.11 | AE9 | fixed function (USB1) |
| P1.12 | A19 | 0: MCASP0_AXR2; 1: SPI2_D1; 2: UART1_RTSn; 3: UART6_TXD; 4: PR0_IEP0_EDIO_DATA_IN_OUT29; 5: ECAP2_IN_APWM_OUT; 6: PR0_UART0_TXD; 7: GPIO1_8; 8: EQEP0_B |
| P1.12A | AE18 | 0: RGMII1_TD2; 2: PR0_UART0_RXD; 7: GPIO0_77 |
| P1.13 | N20 | 0: GPMC0_BE1n; 3: MCASP2_AXR12; 4: PR0_PRU0_GPO13; 5: PR0_PRU0_GPI13; 6: TRC_DATA11; 7: GPIO0_36 |
| P1.19 | AD22 | 0: RGMII2_RX_CTL; 1: RMII2_RX_ER; 2: MCASP2_AXR3; 3: PR0_PRU0_GPO0; 4: PR0_PRU0_GPI0; 7: GPIO1_1 |
| P1.20 | Y24 | 0: VOUT0_DATA5; 1: GPMC0_A5; 2: PR0_PRU1_GPO5; 3: PR0_PRU1_GPI5; 4: UART4_TXD; 5: PR0_PRU0_GPO13; 6: PR0_PRU0_GPI13; 7: GPIO0_50 |
| P1.21 | AE22 | 0: RGMII2_RD3; 2: AUDIO_EXT_REFCLK0; 3: PR0_PRU0_GPO16; 4: PR0_PRU0_GPI16; 5: PR0_UART0_TXD; 7: GPIO1_6; 8: EQEP2_B |
| P1.23 | AC21 | 0: RGMII2_RD2; 2: MCASP2_AXR0; 3: PR0_PRU0_GPO4; 4: PR0_PRU0_GPI4; 5: PR0_UART0_RXD; 7: GPIO1_5; 8: EQEP2_A |
| P1.25 | AB20 | 0: RGMII2_RD1; 1: RMII2_RXD1; 2: MCASP2_AFSR; 3: PR0_PRU0_GPO3; 4: PR0_PRU0_GPI3; 5: MCASP2_AXR7; 7: GPIO1_4 |
| P1.26 | K24 | 0: GPMC0_CSn3; 1: I2C2_SDA; 2: GPMC0_A20; 3: UART4_TXD; 4: MCASP1_AXR5; 6: TRC_DATA18; 7: GPIO0_44; 8: MCASP1_ACLKR |
| P1.26A | D6 | 0: MCU_MCAN0_TX; 1: WKUP_TIMER_IO0; 2: MCU_SPI0_CS3; 7: MCU_GPIO0_13 |
| P1.27 | AE23 | 0: RGMII2_RD0; 1: RMII2_RXD0; 2: MCASP2_AXR2; 3: PR0_PRU0_GPO2; 4: PR0_PRU0_GPI2; 6: PR0_UART0_RTSn; 7: GPIO1_3 |
| P1.28 | K22 | 0: GPMC0_CSn2; 1: I2C2_SCL; 2: MCASP1_AXR4; 3: UART4_RXD; 4: PR0_PRU0_GPO19; 5: PR0_PRU0_GPI19; 6: TRC_DATA17; 7: GPIO0_43; 8: MCASP1_AFSR |
| P1.28A | B3 | 0: MCU_MCAN0_RX; 1: MCU_TIMER_IO0; 2: MCU_SPI1_CS3; 7: MCU_GPIO0_14 |
| P1.29 | Y20 | 0: VOUT0_DE; 1: GPMC0_A17; 2: PR0_PRU1_GPO17; 3: PR0_PRU1_GPI17; 4: UART3_CTSn; 5: PR0_PRU0_GPO7; 6: PR0_PRU0_GPI7; 7: GPIO0_62 |
| P1.30 | E14 | 0: UART0_TXD; 1: ECAP2_IN_APWM_OUT; 2: SPI2_D1; 3: EHRPWM2_B; 7: GPIO1_21 |
| P1.31 | Y22 | 0: VOUT0_DATA14; 1: GPMC0_A14; 2: PR0_PRU1_GPO13; 3: PR0_PRU1_GPI13; 4: UART4_RTSn; 5: PR0_PRU0_GPO4; 6: PR0_PRU0_GPI4; 7: GPIO0_59 |
| P1.32 | D14 | 0: UART0_RXD; 1: ECAP1_IN_APWM_OUT; 2: SPI2_D0; 3: EHRPWM2_A; 7: GPIO1_20 |
| P1.33 | A17 | 0: I2C1_SDA; 1: UART1_TXD; 2: TIMER_IO1; 3: SPI2_CLK; 4: EHRPWM0_SYNCO; 7: GPIO1_29; 8: EHRPWM2_B; 9: MMC2_SDWP |
| P1.33A | AA23 | 0: VOUT0_DATA11; 1: GPMC0_A11; 2: PR0_PRU1_GPO10; 3: PR0_PRU1_GPI10; 4: UART6_CTSn; 5: PR0_PRU0_GPO1; 6: PR0_PRU0_GPI1; 7: GPIO0_56 |
| P1.34 | AD23 | 0: RGMII2_RXC; 1: RMII2_REF_CLK; 2: MCASP2_AXR1; 3: PR0_PRU0_GPO1; 4: PR0_PRU0_GPI1; 5: PR0_ECAP0_SYNC_IN; 7: GPIO1_2 |
| P1.35 | AE21 | 0: RGMII2_TXC; 1: RMII2_CRS_DV; 2: MCASP2_AXR5; 3: PR0_PRU1_GPO1; 4: PR0_PRU1_GPI1; 7: GPIO0_88 |
| P1.36 | V20 | 0: VOUT0_DATA10; 1: GPMC0_A10; 2: PR0_PRU1_GPO9; 3: PR0_PRU1_GPI9; 4: UART6_RTSn; 5: PR0_PRU0_GPO0; 6: PR0_PRU0_GPI0; 7: GPIO0_55 |
| P1.36A | B17 | 0: I2C1_SCL; 1: UART1_RXD; 2: TIMER_IO0; 3: SPI2_CS1; 4: EHRPWM0_SYNCI; 7: GPIO1_28; 8: EHRPWM2_A; 9: MMC2_SDCD |
| P2.01 | B20 | 0: MCASP0_ACLKX; 1: SPI2_CS1; 2: ECAP2_IN_APWM_OUT; 7: GPIO1_11; 8: EQEP1_A |
| P2.01A | AD24 | 0: MDIO0_MDC; 7: GPIO0_86 |
| P2.02 | U22 | 0: VOUT0_DATA0; 1: GPMC0_A0; 2: PR0_PRU1_GPO0; 3: PR0_PRU1_GPI0; 4: UART2_RXD; 5: PR0_PRU0_GPO8; 6: PR0_PRU0_GPI8; 7: GPIO0_45 |
| P2.03 | AB22 | 0: MDIO0_MDIO; 7: GPIO0_85 |
| P2.03A | B18 | 0: MCASP0_AXR1; 1: SPI2_CS2; 2: ECAP1_IN_APWM_OUT; 5: PR0_UART0_RXD; 6: EHRPWM1_A; 7: GPIO1_9; 8: EQEP0_S |
| P2.04 | V24 | 0: VOUT0_DATA1; 1: GPMC0_A1; 2: PR0_PRU1_GPO1; 3: PR0_PRU1_GPI1; 4: UART2_TXD; 5: PR0_PRU0_GPO9; 6: PR0_PRU0_GPI9; 7: GPIO0_46 |
| P2.05 | C15 | 0: MCAN0_TX; 1: UART5_RXD; 2: TIMER_IO2; 3: SYNC2_OUT; 4: UART1_DTRn; 5: EQEP2_I; 6: PR0_UART0_RXD; 7: GPIO1_24; 8: MCASP2_AXR0; 9: EHRPWM_TZn_IN3 |
| P2.05A | B5 | 0: MCU_UART0_RXD; 7: MCU_GPIO0_5 |
| P2.06 | W25 | 0: VOUT0_DATA2; 1: GPMC0_A2; 2: PR0_PRU1_GPO2; 3: PR0_PRU1_GPI2; 4: UART3_RXD; 5: PR0_PRU0_GPO10; 6: PR0_PRU0_GPI10; 7: GPIO0_47 |
| P2.07 | E15 | 0: MCAN0_RX; 1: UART5_TXD; 2: TIMER_IO3; 3: SYNC3_OUT; 4: UART1_RIn; 5: EQEP2_S; 6: PR0_UART0_TXD; 7: GPIO1_25; 8: MCASP2_AXR1; 9: EHRPWM_TZn_IN4 |
| P2.07A | A5 | 0: MCU_UART0_TXD; 7: MCU_GPIO0_6 |
| P2.08 | W24 | 0: VOUT0_DATA3; 1: GPMC0_A3; 2: PR0_PRU1_GPO3; 3: PR0_PRU1_GPI3; 4: UART3_TXD; 5: PR0_PRU0_GPO11; 6: PR0_PRU0_GPI11; 7: GPIO0_48 |
| P2.09 | A15 | 0: UART0_CTSn; 1: SPI0_CS2; 2: I2C3_SCL; 3: UART2_RXD; 4: TIMER_IO6; 5: AUDIO_EXT_REFCLK0; 6: PR0_ECAP0_SYNC_OUT; 7: GPIO1_22; 8: MCASP2_AFSX; 9: MMC2_SDCD |
| P2.09A | D4 | 0: MCU_MCAN1_RX; 1: MCU_TIMER_IO3; 2: MCU_SPI0_CS2; 3: MCU_SPI1_CS2; 4: MCU_SPI1_CLK; 7: MCU_GPIO0_16 |
| P2.10 | AD21 | 0: RGMII2_TD2; 2: MCASP2_AFSX; 3: PR0_PRU1_GPO4; 4: PR0_PRU1_GPI4; 5: PR0_ECAP0_IN_APWM_OUT; 7: GPIO0_91; 8: EQEP2_I |
| P2.11 | B15 | 0: UART0_RTSn; 1: SPI0_CS3; 2: I2C3_SDA; 3: UART2_TXD; 4: TIMER_IO7; 5: AUDIO_EXT_REFCLK1; 6: PR0_ECAP0_IN_APWM_OUT; 7: GPIO1_23; 8: MCASP2_ACLKX; 9: MMC2_SDWP |
| P2.11A | E5 | 0: MCU_MCAN1_TX; 1: MCU_TIMER_IO2; 3: MCU_SPI1_CS1; 4: MCU_EXT_REFCLK0; 7: MCU_GPIO0_15 |
| P2.17 | AC24 | 0: VOUT0_PCLK; 1: GPMC0_A19; 2: PR0_PRU1_GPO19; 3: PR0_PRU1_GPI19; 4: UART2_CTSn; 5: PR0_PRU0_GPO19; 6: PR0_PRU0_GPI19; 7: GPIO0_64; 8: PR0_ECAP0_IN_APWM_OUT |
| P2.18 | V21 | 0: VOUT0_DATA8; 1: GPMC0_A8; 2: PR0_PRU1_GPO16; 3: PR0_PRU1_GPI16; 4: UART6_RXD; 5: PR0_PRU0_GPO17; 6: PR0_PRU0_GPI17; 7: GPIO0_53 |
| P2.19 | AC20 | 0: RGMII2_TD3; 2: MCASP2_ACLKX; 3: PR0_PRU1_GPO16; 4: PR0_PRU1_GPI16; 5: PR0_ECAP0_SYNC_OUT; 6: PR0_UART0_CTSn; 7: GPIO1_0; 8: EQEP2_S |
| P2.20 | Y25 | 0: VOUT0_DATA4; 1: GPMC0_A4; 2: PR0_PRU1_GPO4; 3: PR0_PRU1_GPI4; 4: UART4_RXD; 5: PR0_PRU0_GPO12; 6: PR0_PRU0_GPI12; 7: GPIO0_49 |
| P2.22 | AC25 | 0: VOUT0_VSYNC; 1: GPMC0_A18; 2: PR0_PRU1_GPO18; 3: PR0_PRU1_GPI18; 4: UART2_RTSn; 5: PR0_PRU0_GPO18; 6: PR0_PRU0_GPI18; 7: GPIO0_63 |
| P2.24 | Y23 | 0: VOUT0_DATA6; 1: GPMC0_A6; 2: PR0_PRU1_GPO6; 3: PR0_PRU1_GPI6; 4: UART5_RXD; 5: PR0_PRU0_GPO14; 6: PR0_PRU0_GPI14; 7: GPIO0_51 |
| P2.25 | B14 | 0: SPI0_D1; 1: CP_GEMAC_CPTS0_HW2TSPUSH; 2: EHRPWM_TZn_IN0; 7: GPIO1_19 |
| P2.27 | B13 | 0: SPI0_D0; 1: CP_GEMAC_CPTS0_HW1TSPUSH; 2: EHRPWM1_B; 7: GPIO1_18 |
| P2.28 | AB24 | 0: VOUT0_HSYNC; 1: GPMC0_A16; 2: PR0_PRU1_GPO15; 3: PR0_PRU1_GPI15; 4: UART3_RTSn; 5: PR0_PRU0_GPO6; 6: PR0_PRU0_GPI6; 7: GPIO0_61 |
| P2.29 | A14 | 0: SPI0_CLK; 1: CP_GEMAC_CPTS0_TS_SYNC; 2: EHRPWM1_A; 7: GPIO1_17 |
| P2.29A | M22 | 0: GPMC0_DIR; 1: PR0_ECAP0_IN_APWM_OUT; 3: MCASP2_AXR13; 4: PR0_PRU0_GPO16; 5: PR0_PRU0_GPI16; 6: TRC_DATA14; 7: GPIO0_40; 8: EQEP2_S |
| P2.30 | AA24 | 0: VOUT0_DATA13; 1: GPMC0_A13; 2: PR0_PRU1_GPO12; 3: PR0_PRU1_GPI12; 4: UART5_CTSn; 5: PR0_PRU0_GPO3; 6: PR0_PRU0_GPI3; 7: GPIO0_58 |
| P2.31 | A13 | 0: SPI0_CS0; 2: EHRPWM0_A; 6: PR0_ECAP0_SYNC_IN; 7: GPIO1_15 |
| P2.31A | AA18 | 0: RGMII2_TD1; 1: RMII2_TXD1; 2: MCASP2_ACLKR; 3: PR0_PRU1_GPO3; 4: PR0_PRU1_GPI3; 5: MCASP2_AXR8; 7: GPIO0_90 |
| P2.32 | AB25 | 0: VOUT0_DATA12; 1: GPMC0_A12; 2: PR0_PRU1_GPO11; 3: PR0_PRU1_GPI11; 4: UART5_RTSn; 5: PR0_PRU0_GPO2; 6: PR0_PRU0_GPI2; 7: GPIO0_57 |
| P2.33 | AA25 | 0: VOUT0_DATA7; 1: GPMC0_A7; 2: PR0_PRU1_GPO7; 3: PR0_PRU1_GPI7; 4: UART5_TXD; 5: PR0_PRU0_GPO15; 6: PR0_PRU0_GPI15; 7: GPIO0_52 |
| P2.34 | AA21 | 0: VOUT0_DATA15; 1: GPMC0_A15; 2: PR0_PRU1_GPO14; 3: PR0_PRU1_GPI14; 4: UART4_CTSn; 5: PR0_PRU0_GPO5; 6: PR0_PRU0_GPI5; 7: GPIO0_60 |
| P2.35 | W21 | 0: VOUT0_DATA9; 1: GPMC0_A9; 2: PR0_PRU1_GPO8; 3: PR0_PRU1_GPI8; 4: UART6_TXD; 5: PR0_PRU0_GPO16; 6: PR0_PRU0_GPI16; 7: GPIO0_54 |
| P2.36 | C13 | 0: SPI0_CS1; 1: CP_GEMAC_CPTS0_TS_COMP; 2: EHRPWM0_B; 3: ECAP0_IN_APWM_OUT; 7: GPIO1_16; 9: EHRPWM_TZn_IN5 |

## 5. Inventory by peripheral

GPIO, VOUT0 (display), GPMC0 and TRC (trace) modes are left out. PRU GPO/GPI is listed by
header pin only.

Not usable as a full bus from the header alone: MCU_SPI0 (chip selects only) and MCU_SPI1
(CLK and chip selects, no data lines).

| Peripheral instance | Signal and header pin |
| --- | --- |
| AUDIO_EXT | AUDIO_EXT_REFCLK0 P1.02, AUDIO_EXT_REFCLK0 P1.21, AUDIO_EXT_REFCLK0 P2.09, AUDIO_EXT_REFCLK1 P1.04, AUDIO_EXT_REFCLK1 P2.11 |
| CLKOUT0 | CLKOUT0 P1.10 |
| CP_GEMAC | CP_GEMAC_CPTS0_HW1TSPUSH P2.27, CP_GEMAC_CPTS0_HW2TSPUSH P2.25, CP_GEMAC_CPTS0_RFT_CLK P1.10, CP_GEMAC_CPTS0_TS_COMP P2.36, CP_GEMAC_CPTS0_TS_SYNC P2.29 |
| ECAP0 | ECAP0_IN_APWM_OUT P1.10, ECAP0_IN_APWM_OUT P2.36 |
| ECAP1 | ECAP1_IN_APWM_OUT P1.10A, ECAP1_IN_APWM_OUT P1.32, ECAP1_IN_APWM_OUT P2.03A |
| ECAP2 | ECAP2_IN_APWM_OUT P1.12, ECAP2_IN_APWM_OUT P1.30, ECAP2_IN_APWM_OUT P2.01 |
| EHRPWM0 | EHRPWM0_A P1.06, EHRPWM0_A P2.31, EHRPWM0_B P1.08, EHRPWM0_B P2.36, EHRPWM0_SYNCI P1.36A, EHRPWM0_SYNCO P1.33 |
| EHRPWM1 | EHRPWM1_A P2.03A, EHRPWM1_A P2.29, EHRPWM1_B P1.02, EHRPWM1_B P2.27 |
| EHRPWM2 | EHRPWM2_A P1.32, EHRPWM2_A P1.36A, EHRPWM2_B P1.30, EHRPWM2_B P1.33 |
| EHRPWM_TZn | EHRPWM_TZn_IN0 P2.25, EHRPWM_TZn_IN3 P2.05, EHRPWM_TZn_IN4 P2.07, EHRPWM_TZn_IN5 P2.36 |
| EQEP0 | EQEP0_A P1.10A, EQEP0_B P1.12, EQEP0_I P1.02, EQEP0_S P2.03A |
| EQEP1 | EQEP1_A P2.01, EQEP1_B P1.04, EQEP1_I P1.08, EQEP1_S P1.06 |
| EQEP2 | EQEP2_A P1.23, EQEP2_B P1.21, EQEP2_I P2.05, EQEP2_I P2.10, EQEP2_S P2.07, EQEP2_S P2.19, EQEP2_S P2.29A |
| EXT | EXT_REFCLK1 P1.10 |
| I2C1 | I2C1_SCL P1.36A, I2C1_SDA P1.33 |
| I2C2 | I2C2_SCL P1.28, I2C2_SDA P1.26 |
| I2C3 | I2C3_SCL P2.09, I2C3_SDA P2.11 |
| MCAN0 | MCAN0_RX P2.07, MCAN0_TX P2.05 |
| MCASP0 | MCASP0_ACLKR P1.08, MCASP0_ACLKX P2.01, MCASP0_AFSR P1.06, MCASP0_AFSX P1.04, MCASP0_AXR0 P1.02, MCASP0_AXR1 P2.03A, MCASP0_AXR2 P1.12, MCASP0_AXR3 P1.10A |
| MCASP1 | MCASP1_ACLKR P1.26, MCASP1_AFSR P1.28, MCASP1_AXR4 P1.28, MCASP1_AXR5 P1.26 |
| MCASP2 | MCASP2_ACLKR P2.31A, MCASP2_ACLKX P2.11, MCASP2_ACLKX P2.19, MCASP2_AFSR P1.25, MCASP2_AFSX P2.09, MCASP2_AFSX P2.10, MCASP2_AXR0 P1.23, MCASP2_AXR0 P2.05, MCASP2_AXR1 P1.34, MCASP2_AXR1 P2.07, MCASP2_AXR12 P1.13, MCASP2_AXR13 P2.29A, MCASP2_AXR2 P1.27, MCASP2_AXR3 P1.19, MCASP2_AXR4 P1.02A, MCASP2_AXR5 P1.35, MCASP2_AXR6 P1.04A, MCASP2_AXR7 P1.25, MCASP2_AXR8 P2.31A |
| MCU_EXT | MCU_EXT_REFCLK0 P2.11A |
| MCU_MCAN0 | MCU_MCAN0_RX P1.28A, MCU_MCAN0_TX P1.26A |
| MCU_MCAN1 | MCU_MCAN1_RX P2.09A, MCU_MCAN1_TX P2.11A |
| MCU_SPI0 | MCU_SPI0_CS2 P2.09A, MCU_SPI0_CS3 P1.26A |
| MCU_SPI1 | MCU_SPI1_CLK P2.09A, MCU_SPI1_CS1 P2.11A, MCU_SPI1_CS2 P2.09A, MCU_SPI1_CS3 P1.28A |
| MCU_TIMER | MCU_TIMER_IO0 P1.28A, MCU_TIMER_IO2 P2.11A, MCU_TIMER_IO3 P2.09A |
| MCU_UART0 | MCU_UART0_RXD P2.05A, MCU_UART0_TXD P2.07A |
| MDIO0 | MDIO0_MDC P2.01A, MDIO0_MDIO P2.03 |
| MMC2 | MMC2_SDCD P1.36A, MMC2_SDCD P2.09, MMC2_SDWP P1.33, MMC2_SDWP P2.11 |
| PR0_ECAP0 | PR0_ECAP0_IN_APWM_OUT P1.02, PR0_ECAP0_IN_APWM_OUT P2.10, PR0_ECAP0_IN_APWM_OUT P2.11, PR0_ECAP0_IN_APWM_OUT P2.17, PR0_ECAP0_IN_APWM_OUT P2.29A, PR0_ECAP0_SYNC_IN P1.34, PR0_ECAP0_SYNC_IN P2.31, PR0_ECAP0_SYNC_OUT P2.09, PR0_ECAP0_SYNC_OUT P2.19 |
| PR0_IEP0 | PR0_IEP0_EDIO_DATA_IN_OUT28 P1.10A, PR0_IEP0_EDIO_DATA_IN_OUT29 P1.12 |
| PR0_PRU GPO/GPI | P1.02A, P1.04A, P1.13, P1.19, P1.20, P1.21, P1.23, P1.25, P1.27, P1.28, P1.29, P1.31, P1.33A, P1.34, P1.35, P1.36, P2.02, P2.04, P2.06, P2.08, P2.10, P2.17, P2.18, P2.19, P2.20, P2.22, P2.24, P2.28, P2.29A, P2.30, P2.31A, P2.32, P2.33, P2.34, P2.35 |
| PR0_UART0 | PR0_UART0_CTSn P2.19, PR0_UART0_RTSn P1.27, PR0_UART0_RXD P1.10A, PR0_UART0_RXD P1.12A, PR0_UART0_RXD P1.23, PR0_UART0_RXD P2.03A, PR0_UART0_RXD P2.05, PR0_UART0_TXD P1.02, PR0_UART0_TXD P1.06A, PR0_UART0_TXD P1.12, PR0_UART0_TXD P1.21, PR0_UART0_TXD P2.07 |
| RGMII1 | RGMII1_TD2 P1.12A, RGMII1_TD3 P1.06A |
| RGMII2 | RGMII2_RD0 P1.27, RGMII2_RD1 P1.25, RGMII2_RD2 P1.23, RGMII2_RD3 P1.21, RGMII2_RXC P1.34, RGMII2_RX_CTL P1.19, RGMII2_TD0 P1.04A, RGMII2_TD1 P2.31A, RGMII2_TD2 P2.10, RGMII2_TD3 P2.19, RGMII2_TXC P1.35, RGMII2_TX_CTL P1.02A |
| RMII2 | RMII2_CRS_DV P1.35, RMII2_REF_CLK P1.34, RMII2_RXD0 P1.27, RMII2_RXD1 P1.25, RMII2_RX_ER P1.19, RMII2_TXD0 P1.04A, RMII2_TXD1 P2.31A, RMII2_TX_EN P1.02A |
| SPI0 | SPI0_CLK P2.29, SPI0_CS0 P2.31, SPI0_CS1 P2.36, SPI0_CS2 P2.09, SPI0_CS3 P2.11, SPI0_D0 P2.27, SPI0_D1 P2.25 |
| SPI2 | SPI2_CLK P1.08, SPI2_CLK P1.33, SPI2_CS0 P1.06, SPI2_CS1 P1.36A, SPI2_CS1 P2.01, SPI2_CS2 P2.03A, SPI2_CS3 P1.04, SPI2_CS3 P1.10, SPI2_D0 P1.10A, SPI2_D0 P1.32, SPI2_D1 P1.12, SPI2_D1 P1.30 |
| SYNC1 | SYNC1_OUT P1.10 |
| SYNC2 | SYNC2_OUT P2.05 |
| SYNC3 | SYNC3_OUT P2.07 |
| SYSCLKOUT0 | SYSCLKOUT0 P1.10 |
| TIMER | TIMER_IO0 P1.36A, TIMER_IO1 P1.33, TIMER_IO2 P2.05, TIMER_IO3 P2.07, TIMER_IO4 P1.10, TIMER_IO6 P2.09, TIMER_IO7 P2.11 |
| UART0 | UART0_CTSn P2.09, UART0_RTSn P2.11, UART0_RXD P1.32, UART0_TXD P1.30 |
| UART1 | UART1_CTSn P1.10A, UART1_DTRn P2.05, UART1_RIn P2.07, UART1_RTSn P1.12, UART1_RXD P1.06, UART1_RXD P1.36A, UART1_TXD P1.08, UART1_TXD P1.33 |
| UART2 | UART2_CTSn P2.17, UART2_RTSn P2.22, UART2_RXD P2.02, UART2_RXD P2.09, UART2_TXD P2.04, UART2_TXD P2.11 |
| UART3 | UART3_CTSn P1.29, UART3_RTSn P2.28, UART3_RXD P2.06, UART3_TXD P2.08 |
| UART4 | UART4_CTSn P2.34, UART4_RTSn P1.31, UART4_RXD P1.28, UART4_RXD P2.20, UART4_TXD P1.20, UART4_TXD P1.26 |
| UART5 | UART5_CTSn P2.30, UART5_RTSn P2.32, UART5_RXD P2.05, UART5_RXD P2.24, UART5_TXD P2.07, UART5_TXD P2.33 |
| UART6 | UART6_CTSn P1.33A, UART6_RTSn P1.36, UART6_RXD P1.10A, UART6_RXD P2.18, UART6_TXD P1.12, UART6_TXD P2.35 |
| USB1 | USB1_DRVVBUS P1.03 |
| WKUP_TIMER | WKUP_TIMER_IO0 P1.26A |

## 6. MSPM0L1105 on the AIN header pins

The PB2-I carries a TI MSPM0L1105 (U11, VQFN-24) as its analog-input co-processor, on
VDD_3V3. It talks to the AM625 on MCU_SPI0 (PA3 CS, PA9 PICO, PA11 SCK, PA19 POCI) and I2C0
(PA0/PA1), with reset on GPIO1_50 and boot-loader invoke on MCU_GPIO0_1 (PA18)
[REF-SENSOR-021 sheet 15]. Eight of its pins are wired **directly** (no series resistor or
filter shown) to header pins that are also wired to AM625 balls. The table was read from a
450 dpi render of sheet 15; pin functions are from Table 6-1 [REF-SENSOR-051].

| Header pin | AIN | MSPM0 pin (VQFN-24 no.) | MSPM0 functions (Table 6-1) | AM625 ball(s) on the same pin | Pilot net (2026-10-17 generator) |
| --- | --- | --- | --- | --- | --- |
| P1-19 | AIN0 | PA26 / A1 (22) | A1, GPAMP_IN+; TIMG1_C0, UART0_RX, SPI0_POCI | AD22 | RMII2_RX_ER |
| P1-21 | AIN1 | PA25 / A2 (21) | A2; TIMG4_C1, UART0_TX, SPI0_PICO | AE22 | DSHOT3 |
| P1-23 | AIN2 | PA24 / A3 (20) | A3; SPI0_CS2, TIMG0_C1, UART0_RTS | AC21 | DSHOT0 |
| P1-25 | AIN3 | PA22 / A4 (18) | A4, GPAMP_OUT; UART0_RX, TIMG2_C1, UART0_RTS, CLK_OUT, UART1_RX (default BSL UART RX) | AB20 | RMII2_RXD1 |
| P1-27 | AIN4 | PA21 / A5 / VREF- (17) | A5, VREF-; TIMG2_C0, UART0_CTS, UART0_TX | AE23 | RMII2_RXD0 |
| P2-35 | AIN5 | PA20 / A6 / **SWCLK** (16) | A6; SWCLK, TIMG4_C0 | W21 | spare (no connect) |
| P1-2 | AIN6 | PA16 / A8 (12) | A8; SPI0_POCI, TIMG0_C0, FCC_IN | E18 + AA19 | RMII2_TX_EN |
| P2-36 | AIN7 | PA15 / A9 (11) | A9; UART1_RTS, SPI0_CS2, TIMG4_C1 | C13 | spare (no connect) |

PA23 / VREF+ goes only to test point TP7, and PA19 (SWDIO) is shared between MCU_SPI0_D1 and
test point TP6. Neither is on the header. P1-17/P1-18 (AIN VREF-/VREF+) are not MSPM0 pins.

What the sources establish:

- **Reset state is high-impedance, except SWCLK.** After power-up, "Serial wire debug (SWD)
  IO are configured in SWD mode (SWDIO is pulled high, and SWCLK is pulled low)" and "All
  other configurable I/O pins are high impedance (Hi-Z)" [REF-SENSOR-052 §2.4.1.2]; the
  default IOMUX state has PF, PC and input enable cleared and pulls disabled
  [REF-SENSOR-052 §8.2]. So **P2-35 carries a pull-down (RPD, 40 kΩ typ.
  [REF-SENSOR-051]) from the MSPM0 SWCLK** unless the MSPM0 firmware re-muxes PA20 or a
  boot-configuration policy disables SWD.
- **Load on every AIN pin.** Each adds an MSPM0 input (CI 5 pF typ. [REF-SENSOR-051]) plus
  the PB2-I trace stub to the AM625 ball's load. On the Pilot that applies to four RMII2
  signals (P1-2, P1-19, P1-25, P1-27, 50 MHz reference) and two DShot outputs (P1-21, P1-23).
- **Voltage limit.** Common-tolerance MSPM0 pins are rated -0.3 V to VDD + 0.3 V (4.1 V
  max) [REF-SENSOR-051 §7.1]. With VDD = 3.3 V, nothing on these header pins shall exceed
  3.6 V, even with the AM625 ball unused.
- **Firmware dependence.** Whether a pin stays Hi-Z after boot depends on the MSPM0 firmware
  BeagleBoard ships, which is not documented in the sources above. Under the owner's rule
  this firmware state cannot be the basis for a wiring decision; the Pilot must tolerate an
  MSPM0 pin that drives, pulls or samples.

> **CAUTION** — Drive no AIN header pin (P1-2, P1-19, P1-21, P1-23, P1-25, P1-27, P2-35,
> P2-36) above 3.6 V. Each is wired directly to an MSPM0L1105 pin whose absolute maximum is
> VDD + 0.3 V; overvoltage can damage the PB2-I's MSPM0 or AM625.

<!-- separate callouts -->

> **NOTE** — The MSPM0 also offers its own UART0/UART1, SPI0, TIMG captures, GPAMP and a
> 12-bit 1.68 Msps ADC on these pins [REF-SENSOR-051 §1, §8.12]. Using them would mean
> replacing BeagleBoard's MSPM0 firmware; that is recorded as a capability, not proposed.

## 7. Method

1. Converted SPRSP58C to text with `pdftotext -layout` (poppler).
2. Parsed Table 5-1 (ALW column) into ball → {mux mode: signal} by grouping each ball's rows
   as a run of ascending mux-mode numbers; balls B19, E5 and B14 were entered by hand from the
   table because their rows wrap across columns.
3. Joined the result to the header ball list in the SRM §4.2 tables and the PB2 schematic
   sheet "016_BP P1 & P2", then compared every mode against the SRM tables.
4. Checked the CPSW port-1/port-2 conclusions directly against Tables 5-2 to 5-5 and TRM
   §1.4.12.

Extraction by Claude Opus 5.5; every corrected assumption in §2 was re-read in the source
before this file was written.
