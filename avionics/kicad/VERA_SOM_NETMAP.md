# Vera ↔ phyCORE-AM62A SoM — Pad-Level Net Map

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 4.8 (Anthropic) — net map from the verified symbol, 2026-07-11
**License:** CC BY 4.0
**Revision:** Rev A (2026-07-11)

Companion to `symbols/PHYCORE-AM62AX-DSC.kicad_sym` (SnapMagic/SnapEDA export of the PHYTEC
phyCORE-AM62Ax-DSC, 270-pad 0.8 mm direct-solder module; symbol loads in kicad-cli 9.0.2,
footprint has exactly 270 pads 1–270). **Every SoM pad number below was read directly from that
symbol file — none fabricated.** This is the wiring the Vera carrier schematic implements when
U1 (the raw TI AM62A7 placeholder) and U_PMIC (TPS65219) are replaced by the SoM (see
`docs/VERA_MANUFACTURING_READINESS.md` Rev C §3B and `gen_vera.py`).

Net names match the existing Vera net vocabulary in `gen_vera.py` so the carrier side
(KSZ9477, SLB9670, MSPM0G3507, ISOW1044, connectors) connects by label without change.

## Migration delta (schematic-first)

- **REMOVE:** U1 `TI_AM62A7`, U_PMIC `TI_TPS65219`, and power symbols `VDD_CORE`, `VDDR`,
  `VDDSHV` (the SoM integrates the SoC + LPDDR4 + PMIC + sequencing on-module).
- **ADD:** `U_SOM` = `PHYCORE-AM62AX-DSC`.
- **REWIRE:** the table below. Carrier sections unchanged.

## Power

| SoM pad(s) | SoM pin | Vera net | Note |
| --- | --- | --- | --- |
| 25, 26 | VIN | +5V | Main module input. **VERIFY VIN range in PHYTEC HW manual** before final. |
| 24 | VBAT | +3V3 (or RTC backup) | RTC/backup domain — **verify** intended source. |
| 23 | SOC_VDDSHV5_SDIO | +3V3 | SDIO I/O supply — **verify** if MMC used. |
| 91, 92, 93, 94 | VDD_3V3_OUT | +3V3 | Module **sources** 3V3 → feeds carrier logic (KSZ9477/TPM/MSPM0). |
| 189–270 (GND block) | GND | GND | All module grounds. |

## Camera — MIPI CSI-2 (to J_CAM1 / direct-solder land, §4)

| SoM pad | SoM pin | Vera net | Note |
| --- | --- | --- | --- |
| 81 | X_CSI0_RXCLKP | CSI_CLK_P | |
| 82 | X_CSI0_RXCLKN | CSI_CLK_N | |
| 89 | X_CSI0_RXP0 | CSI_D0_P | |
| 90 | X_CSI0_RXN0 | CSI_D0_N | |
| 83, 84 | X_CSI0_RXP1/RXN1 | CSI_D1_P/N | reserved — direct-solder 4-lane |
| 85, 86 | X_CSI0_RXP2/RXN2 | CSI_D2_P/N | reserved — direct-solder 4-lane |
| 87, 88 | X_CSI0_RXP3/RXN3 | CSI_D3_P/N | reserved — direct-solder 4-lane |
| 146, 147 | X_I2C1_SCL/SDA | CAM_SCL / CAM_SDA | camera control I²C |

CAM_RESET_N / CAM_PWDN ride WKUP GPIO — **assign a specific WKUP GPIO pad from the HW manual**.

## Ethernet ring — RGMII2 + MDIO to KSZ9477 (U2)

| SoM pad | SoM pin | Vera net |
| --- | --- | --- |
| 57, 58, 59, 60 | X_CPSW_RGMII2_TD0..3 | RGMII1_TXD0 (+TXD1..3 for full) |
| 56 | X_CPSW_RGMII2_TXC | RGMII1_TXC |
| 55 | X_CPSW_RGMII2_TX_CTL | RGMII1_TXCTL |
| 54, 53, 52, 51 | X_CPSW_RGMII2_RD0..3 | RGMII1_RXD0 (+RXD1..3 for full) |
| 50 | X_CPSW_RGMII2_RXC | RGMII1_RXC |
| 49 | X_CPSW_RGMII2_RX_CTL | RGMII1_RXCTL |
| 47 | X_MDIO0_MDC | MDC |
| 48 | X_MDIO0_MDIO | MDIO |

*(The module also has a second, ready Ethernet port on its on-board DP83867 PHY —
X_CPSW_ETH0_A/B/C/D± pads 63–70 + LED/INT 61,62,71,72 — available if a direct magnetics port
is ever wanted instead of / in addition to the KSZ9477 ring.)*

## TPM — SPI0 to SLB9670 (U5)

| SoM pad | SoM pin | Vera net |
| --- | --- | --- |
| 133 | X_SPI0_CLK | TPM_SPI_SCK |
| 134 | X_SPI0_D0 | TPM_SPI_MOSI |
| 135 | X_SPI0_D1 | TPM_SPI_MISO |
| 136 | X_SPI0_CS0 | TPM_SPI_CS |

TPM_RESET_N / TPM_PIRQ ride GPIO — **assign specific GPIO pads from the HW manual**.

## MCU link — UART0 to MSPM0G3507 (U3)

| SoM pad | SoM pin | Vera net | Note |
| --- | --- | --- | --- |
| 141 | X_UART0_TXD | UART_M2A path → MSPM0 RX | cross TX→RX |
| 140 | X_UART0_RXD | UART_A2M path ← MSPM0 TX | cross TX→RX |

CAN-FD trunk stays on **MSPM0** (native MCAN → ISOW1044 U4 → J_CANFD), matching the control-half
architecture. The SoM's own **X_MCAN0_TX/RX (pads 143/142)** are **reserved** (optional second
CAN / redundancy).

## Reset

| SoM pad | SoM pin | Vera net | Note |
| --- | --- | --- | --- |
| 183 | X_NRESET_IN | SOC_PORZ (reset in) | drive/pull per HW manual |
| 187 | X_PORZ_OUT | (reset status) | optional status |

Boot mode: on-module eMMC/OSPI boot — **BOOTMODE straps are set on the module**; the old
`SOC_BOOT0` net is likely vestigial (**confirm** against HW manual before removing).

## Open items (HW-manual verification — do not fabricate)

1. VIN voltage range (pads 25/26) and VBAT source (24), SOC_VDDSHV5_SDIO (23).
2. Specific WKUP/GPIO pad assignments for CAM_RESET_N, CAM_PWDN, TPM_RESET_N, TPM_PIRQ.
3. Whether BOOTMODE straps are exposed or module-fixed (SOC_BOOT0 disposition).
4. Wiring the 270-pad, 9-unit symbol: best done as GUI placement or a dedicated
   coordinate-parsing generator pass — the simplified `glabel_pin()` geometry in `gen_vera.py`
   does not apply to this multi-unit symbol.

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0. SoM symbol/footprint ©
PHYTEC / exported via SnapMagic (SnapEDA); see the .kicad_sym `SnapEDA_Link` property.*
