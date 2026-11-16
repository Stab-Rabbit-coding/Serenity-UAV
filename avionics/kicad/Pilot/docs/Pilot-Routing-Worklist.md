# Pilot hand-routing worklist

Generated from `kicads/Pilot.kicad_pcb`: **130 open connections on 68 nets**. Coordinates are board mm (KiCad y down).

Method: open the board in KiCad's PCB Editor, enable the ratsnest, route with the
interactive router (X) in push-and-shove mode, then run DRC with schematic parity.
The project rules in `Pilot.kicad_dru` are active in the editor: they forbid logic
copper in `ISO_BAND` and any foreign metal inside the two TI 13.1 bubbles. Plane nets
need only a 0.024 / 0.012 in (0.6 / 0.3 mm) via beside the pad (In1 is GND, In4 is +3V3).

## Signal nets

### `SPI0_CLK` (5)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [SPI0_CLK] on B.Cu, length 0.0500 mm | 144.28, 110.97 | track [SPI0_CLK] on B.Cu, length 0.1500 mm | 150.93, 113.33 |
| 19 [SPI0_CLK] of TPM | 155.15, 92.75 | track [SPI0_CLK] on F.Cu, length 0.1673 mm | 146.97, 97.55 |
| track [SPI0_CLK] on B.Cu, length 0.0500 mm | 144.18, 111.08 | 17 [SPI0_CLK] of 1553-XCVR | 134.45, 110.15 |
| track [SPI0_CLK] on B.Cu, length 0.1218 mm | 146.97, 97.67 | track [SPI0_CLK] on B.Cu, length 0.0500 mm | 144.28, 110.97 |
| 13 [SPI0_CLK] of IMU | 125.44, 95.86 | 17 [SPI0_CLK] of 1553-XCVR | 134.45, 110.15 |

### `NIC-USB1_AVDD33` (5)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [NIC-USB1_AVDD33] of C-USB1-A33H3 | 165.41, 97.99 | track [NIC-USB1_AVDD33] on F.Cu, length 0.9500 mm | 164.38, 98.62 |
| track [NIC-USB1_AVDD33] on In2.Cu, length 3.2527 mm | 163.47, 101.83 | 1 [NIC-USB1_AVDD33] of C-USB1-A33H2 | 166.40, 100.82 |
| 1 [NIC-USB1_AVDD33] of NIC-USB1 | 161.80, 97.10 | 29 [NIC-USB1_AVDD33] of NIC-USB1 | 162.40, 98.90 |
| track [NIC-USB1_AVDD33] on F.Cu, length 0.0500 mm | 160.62, 94.72 | track [NIC-USB1_AVDD33] on F.Cu, length 0.1414 mm | 161.82, 97.08 |
| 1 [NIC-USB1_AVDD33] of C-USB1-A33H1 | 160.61, 94.76 | 2 [NIC-USB1_AVDD33] of FB-USB1-A33 | 157.37, 95.25 |

### `+5V` (3)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [+5V] of C-CAN2 | 136.25, 98.75 | track [+5V] on In2.Cu, length 0.2722 mm | 132.57, 97.65 |
| 1 [+5V] of C-IN2 | 122.43, 103.90 | track [+5V] on F.Cu, length 0.2626 mm | 132.37, 97.46 |
| track [+5V] on F.Cu, length 0.2121 mm | 155.68, 102.78 | track [+5V] on B.Cu, length 0.0500 mm | 168.47, 105.42 |

### `SPI0_MOSI` (3)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 4 [SPI0_MOSI] of BARO | 143.78, 110.18 | 19 [SPI0_MOSI] of 1553-XCVR | 134.45, 109.35 |
| track [SPI0_MOSI] on In2.Cu, length 2.3500 mm | 156.68, 107.88 | 4 [SPI0_MOSI] of BARO | 143.78, 110.18 |
| 14 [SPI0_MOSI] of IMU | 125.44, 96.36 | 19 [SPI0_MOSI] of 1553-XCVR | 134.45, 109.35 |

### `NIC-USB1_DVDD11` (3)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [NIC-USB1_DVDD11] on In2.Cu, length 0.0707 mm | 159.28, 97.78 | 10 [NIC-USB1_DVDD11] of NIC-USB1 | 158.40, 98.10 |
| 1 [NIC-USB1_DVDD11] of C-USB1-D11 | 155.90, 98.82 | 1 [NIC-USB1_DVDD11] of C-USB1-LXB | 156.96, 98.51 |
| track [NIC-USB1_DVDD11] on In2.Cu, length 0.8485 mm | 159.22, 101.33 | 22 [NIC-USB1_DVDD11] of NIC-USB1 | 161.00, 101.10 |

### `ETH_RMII2_TXP` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [ETH_RMII2_TXP] on B.Cu, length 0.1000 mm | 174.78, 101.22 | track [ETH_RMII2_TXP] on B.Cu, length 0.6500 mm | 171.78, 100.97 |
| track [ETH_RMII2_TXP] on B.Cu, length 0.1414 mm | 171.07, 100.92 | 1 [ETH_RMII2_TXP] of T-RMII2-TX | 164.57, 111.36 |

### `M1553_IRQN` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [M1553_IRQN] of 1553-XCVR | 139.20, 112.50 | track [M1553_IRQN] on B.Cu, length 0.3000 mm | 137.53, 104.38 |
| 2 [M1553_IRQN] of 1553-XCVR | 139.20, 112.50 | 17 [M1553_IRQN] of PB2-P2 | 147.23, 115.22 |

### `RMII2_PHY_INTRN` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RMII2_PHY_INTRN] on In2.Cu, length 0.7071 mm | 166.62, 98.78 | track [RMII2_PHY_INTRN] on B.Cu, length 0.1414 mm | 169.53, 98.47 |
| track [RMII2_PHY_INTRN] on B.Cu, length 0.2500 mm | 151.22, 112.03 | track [RMII2_PHY_INTRN] on In2.Cu, length 0.0707 mm | 160.68, 115.38 |

### `RS485_A_F` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RS485_A_F] on F.Cu, length 0.3250 mm | 142.00, 119.65 | track [RS485_A_F] on F.Cu, length 0.0500 mm | 148.57, 117.58 |
| track [RS485_A_F] on F.Cu, length 0.0707 mm | 143.57, 110.53 | track [RS485_A_F] on F.Cu, length 0.0500 mm | 149.22, 115.58 |

### `RS485_DE` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 5 [RS485_DE] of RS485 | 155.15, 107.73 | 3 [RS485_DE] of RS485 | 155.15, 110.28 |
| 3 [RS485_DE] of RS485 | 155.15, 110.28 | 32 [RS485_DE] of PB2-P2 | 165.01, 120.17 |

### `SPI0_MISO` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [SPI0_MISO] on B.Cu, length 0.0707 mm | 143.12, 110.78 | 18 [SPI0_MISO] of 1553-XCVR | 134.45, 109.75 |
| 1 [SPI0_MISO] of IMU | 125.70, 97.12 | 18 [SPI0_MISO] of 1553-XCVR | 134.45, 109.75 |

### `EXT_SPI_5V` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [EXT_SPI_5V] of C-SPI5 | 168.29, 97.30 | 1 [EXT_SPI_5V] of J-SPI | 165.07, 92.90 |
| 2 [EXT_SPI_5V] of F-SPI | 170.49, 105.37 | 1 [EXT_SPI_5V] of C-SPI5 | 168.29, 97.30 |

### `EXT_SPI_MISO` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 3 [EXT_SPI_MISO] of J-SPI | 162.57, 92.90 | 2 [EXT_SPI_MISO] of ESD-SPI | 168.58, 89.03 |
| track [EXT_SPI_MISO] on B.Cu, length 1.1000 mm | 137.07, 94.78 | 3 [EXT_SPI_MISO] of J-SPI | 162.57, 92.90 |

### `NIC-USB1_VBUS` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [NIC-USB1_VBUS] of R-USB1-VBUS | 155.62, 97.53 | 6 [NIC-USB1_VBUS] of NIC-USB1 | 159.80, 97.10 |
| 6 [NIC-USB1_VBUS] of NIC-USB1 | 159.80, 97.10 | 31 [NIC-USB1_VBUS] of PB2-P1 | 165.01, 89.83 |

### `RMII2_RXD0` (2)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 18 [RMII2_RXD0] of PHY-RMII2 | 168.18, 101.33 | 2 [RMII2_RXD0] of R-RMII2-AD0 | 173.88, 103.60 |
| track [RMII2_RXD0] on In3.Cu, length 0.0707 mm | 160.07, 90.12 | 18 [RMII2_RXD0] of PHY-RMII2 | 168.18, 101.33 |

### `BARO_INT` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [BARO_INT] on B.Cu, length 0.7000 mm | 147.22, 120.17 | track [BARO_INT] on B.Cu, length 0.0500 mm | 144.82, 109.42 |

### `CAN_L_F` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [CAN_L_F] on F.Cu, length 0.0500 mm | 129.12, 120.47 | track [CAN_L_F] on F.Cu, length 0.9000 mm | 131.88, 115.22 |

### `CAN_STB` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 10 [CAN_STB] of PB2-P2 | 137.07, 120.17 | 4 [CAN_STB] of CAN-TR | 139.75, 109.00 |

### `DSHOT2` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [DSHOT2] on In3.Cu, length 0.1414 mm | 160.57, 92.03 | track [DSHOT2] on B.Cu, length 0.3536 mm | 162.47, 89.83 |

### `DSHOT3` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [DSHOT3] on F.Cu, length 0.0707 mm | 140.03, 95.03 | 21 [DSHOT3] of PB2-P1 | 152.31, 89.83 |

### `PHY-RMII2_RBIAS` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 14 [PHY-RMII2_RBIAS] of PHY-RMII2 | 170.00, 101.54 | 1 [PHY-RMII2_RBIAS] of R-RMII2-RBIAS | 172.48, 102.80 |

### `ETH_USB1_LINE_CTX` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [ETH_USB1_LINE_CTX] of R-USB1-BST | 171.02, 103.78 | track [ETH_USB1_LINE_CTX] on F.Cu, length 0.3500 mm | 164.68, 99.53 |

### `ETH_USB1_TXN` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 28 [ETH_USB1_TXN] of NIC-USB1 | 162.40, 99.30 | 2 [ETH_USB1_TXN] of T-USB1-TX | 164.57, 101.91 |

### `ETH_USB1_TXP` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 27 [ETH_USB1_TXP] of NIC-USB1 | 162.40, 99.70 | 1 [ETH_USB1_TXP] of T-USB1-TX | 164.57, 102.56 |

### `ETH_RMII2_RXN` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [ETH_RMII2_RXN] of T-RMII2-RX | 164.57, 106.31 | track [ETH_RMII2_RXN] on In3.Cu, length 1.6500 mm | 166.62, 100.22 |

### `ETH_RMII2_RXP` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [ETH_RMII2_RXP] on B.Cu, length 0.5000 mm | 171.03, 99.53 | track [ETH_RMII2_RXP] on B.Cu, length 0.3536 mm | 173.12, 98.28 |

### `ETH_RMII2_TXN` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [ETH_RMII2_TXN] on B.Cu, length 0.3598 mm | 171.40, 100.50 | 2 [ETH_RMII2_TXN] of T-RMII2-TX | 164.57, 110.70 |

### `IMU_INT1` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 4 [IMU_INT1] of IMU | 127.20, 97.12 | 19 [IMU_INT1] of PB2-P2 | 149.77, 115.22 |

### `IMU_INT2` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 9 [IMU_INT2] of IMU | 126.70, 94.60 | 22 [IMU_INT2] of PB2-P2 | 152.31, 120.17 |

### `M1553_N` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [M1553_N] on In3.Cu, length 0.1000 mm | 139.53, 99.78 | 43 [M1553_N] of 1553-XCVR | 140.35, 109.75 |

### `M1553_P` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [M1553_P] of 1553-XFM | 156.44, 101.04 | track [M1553_P] on B.Cu, length 0.0707 mm | 140.47, 110.53 |

### `M1553_SEC_P` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 4 [M1553_SEC_P] of 1553-XFM | 164.06, 111.96 | track [M1553_SEC_P] on B.Cu, length 0.1628 mm | 164.06, 109.57 |

### `MCAN0_RX` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 5 [MCAN0_RX] of CAN-TR | 139.75, 107.73 | 7 [MCAN0_RX] of PB2-P2 | 134.53, 115.22 |

### `MCAN0_TX` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 5 [MCAN0_TX] of PB2-P2 | 131.99, 115.22 | 3 [MCAN0_TX] of CAN-TR | 139.75, 110.28 |

### `MDC0` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [MDC0] of PB2-P2 | 126.91, 115.22 | 16 [MDC0] of PHY-RMII2 | 169.00, 101.54 |

### `MDIO0` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 3 [MDIO0] of PB2-P2 | 129.45, 115.22 | track [MDIO0] on B.Cu, length 0.2718 mm | 169.50, 101.54 |

### `RMII2_PHY_RSTN` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 20 [RMII2_PHY_RSTN] of PB2-P2 | 149.77, 120.17 | 5 [RMII2_PHY_RSTN] of PHY-RMII2 | 170.40, 98.46 |

### `RS485_RX` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 4 [RS485_RX] of RS485 | 155.15, 109.00 | track [RS485_RX] on B.Cu, length 0.5078 mm | 154.85, 120.17 |

### `RS485_TX` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RS485_TX] on B.Cu, length 1.6902 mm | 167.55, 113.53 | 2 [RS485_TX] of RS485 | 155.15, 111.55 |

### `SPI0_CS_1553` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 9 [SPI0_CS_1553] of PB2-P2 | 137.07, 115.22 | 15 [SPI0_CS_1553] of 1553-XCVR | 134.45, 110.95 |

### `SPI0_CS_BARO` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 11 [SPI0_CS_BARO] of PB2-P2 | 139.61, 115.22 | track [SPI0_CS_BARO] on B.Cu, length 0.2000 mm | 144.28, 109.42 |

### `SPI0_CS_TPM` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [SPI0_CS_TPM] of R-TPMCS | 154.08, 88.20 | 20 [SPI0_CS_TPM] of TPM | 155.15, 92.25 |

### `TPM_IRQN` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| via [TPM_IRQN] | 149.78, 94.78 | 18 [TPM_IRQN] of TPM | 155.15, 93.25 |

### `VCC2_RS485` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [VCC2_RS485] on F.Cu, length 0.2500 mm | 150.78, 115.88 | track [VCC2_RS485] on F.Cu, length 0.0500 mm | 146.78, 108.12 |

### `EXT_SPI_MOSI` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [EXT_SPI_MOSI] on F.Cu, length 0.0500 mm | 168.32, 90.12 | track [EXT_SPI_MOSI] on F.Cu, length 0.3536 mm | 161.43, 92.47 |

### `EXT_SPI_SCK` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 8 [EXT_SPI_SCK] of PB2-P1 | 134.53, 94.78 | track [EXT_SPI_SCK] on In2.Cu, length 0.0707 mm | 163.32, 92.67 |

### `NIC-USB1_AVDD11` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [NIC-USB1_AVDD11] on B.Cu, length 0.7000 mm | 164.53, 98.92 | track [NIC-USB1_AVDD11] on In3.Cu, length 0.2121 mm | 164.57, 100.08 |

### `NIC-USB1_LX` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 1 [NIC-USB1_LX] of L-USB1 | 156.88, 98.35 | 12 [NIC-USB1_LX] of NIC-USB1 | 158.40, 98.90 |

### `NIC-USB1_PME` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [NIC-USB1_PME] of R-USB1-PME | 154.82, 97.53 | 8 [NIC-USB1_PME] of NIC-USB1 | 159.00, 97.10 |

### `NIC-USB1_PU` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [NIC-USB1_PU] of R-USB1-PU | 155.47, 96.03 | 7 [NIC-USB1_PU] of NIC-USB1 | 159.40, 97.10 |

### `NIC-USB1_RSET` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 26 [NIC-USB1_RSET] of NIC-USB1 | 162.40, 100.10 | 1 [NIC-USB1_RSET] of R-USB1-RSET | 162.43, 99.26 |

### `NIC-USB1_XI` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 23 [NIC-USB1_XI] of NIC-USB1 | 161.40, 101.10 | 1 [NIC-USB1_XI] of Y-USB1 | 159.75, 104.95 |

### `NIC-USB1_XO_R` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 2 [NIC-USB1_XO_R] of R-USB1-XO | 163.36, 98.03 | 3 [NIC-USB1_XO_R] of Y-USB1 | 161.95, 103.25 |

### `RMII2_CRS_DV` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 20 [RMII2_CRS_DV] of PHY-RMII2 | 167.96, 100.50 | 35 [RMII2_CRS_DV] of PB2-P1 | 170.09, 89.83 |

### `RMII2_REF_CLK` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RMII2_REF_CLK] on B.Cu, length 0.2802 mm | 169.00, 98.46 | 34 [RMII2_REF_CLK] of PB2-P1 | 167.55, 94.78 |

### `RMII2_RXD1` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RMII2_RXD1] on B.Cu, length 0.0500 mm | 156.93, 90.83 | 17 [RMII2_RXD1] of PHY-RMII2 | 168.60, 101.54 |

### `RMII2_RX_ER` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 19 [RMII2_RX_ER] of PB2-P1 | 149.77, 89.83 | track [RMII2_RX_ER] on B.Cu, length 0.2716 mm | 167.96, 99.50 |

### `RMII2_TXD0` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 4 [RMII2_TXD0] of PB2-P1 | 129.45, 94.78 | 23 [RMII2_TXD0] of PHY-RMII2 | 167.96, 99.10 |

### `RMII2_TXD1` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RMII2_TXD1] on F.Cu, length 0.3536 mm | 164.62, 114.38 | track [RMII2_TXD1] on B.Cu, length 0.0500 mm | 168.18, 98.67 |

### `RMII2_TX_EN` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [RMII2_TX_EN] on B.Cu, length 0.1414 mm | 168.57, 98.42 | 2 [RMII2_TX_EN] of PB2-P1 | 126.91, 94.78 |

### `USB1_DM` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 9 [USB1_DM] of PB2-P1 | 137.07, 89.83 | 3 [USB1_DM] of NIC-USB1 | 161.00, 97.10 |

### `USB1_DP` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 11 [USB1_DP] of PB2-P1 | 139.61, 89.83 | 2 [USB1_DP] of NIC-USB1 | 161.40, 97.10 |

### `XI_25M` (1)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [XI_25M] on B.Cu, length 0.1000 mm | 170.53, 101.67 | track [XI_25M] on B.Cu, length 0.0500 mm | 170.68, 108.53 |


## Plane nets

### `+3V3` (17)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [+3V3] on B.Cu, length 0.9000 mm | 137.18, 105.67 | 31 [+3V3] of 1553-XCVR | 137.60, 106.60 |
| track [+3V3] on F.Cu, length 0.0500 mm | 154.43, 95.67 | via [+3V3] | 153.47, 95.28 |
| 18 [+3V3] of NIC-USB1 | 159.40, 101.10 | via [+3V3] | 158.28, 101.12 |
| track [+3V3] on B.Cu, length 0.3536 mm | 168.72, 102.62 | track [+3V3] on B.Cu, length 0.2614 mm | 169.92, 103.54 |
| 5 [+3V3] of IMU | 127.46, 96.36 | track [+3V3] on B.Cu, length 1.5000 mm | 126.67, 97.22 |
| 44 [+3V3] of 1553-XCVR | 140.35, 110.15 | 41 [+3V3] of 1553-XCVR | 140.35, 108.95 |
| via [+3V3] | 141.62, 110.03 | 44 [+3V3] of 1553-XCVR | 140.35, 110.15 |
| 1 [+3V3] of C-RMII2-IO1 | 166.34, 101.90 | track [+3V3] on B.Cu, length 0.0500 mm | 167.38, 100.83 |
| track [+3V3] on F.Cu, length 0.1414 mm | 157.72, 100.78 | 13 [+3V3] of NIC-USB1 | 158.40, 99.30 |
| 16 [+3V3] of 1553-XCVR | 134.45, 110.55 | track [+3V3] on B.Cu, length 0.0500 mm | 132.93, 111.42 |
| 5 [+3V3] of NIC-USB1 | 160.20, 97.10 | track [+3V3] on B.Cu, length 1.0500 mm | 160.97, 99.08 |
| 1 [+3V3] of CAN-TR | 139.75, 112.81 | 6 [+3V3] of 1553-XCVR | 137.60, 112.50 |
| track [+3V3] on F.Cu, length 0.2000 mm | 154.72, 88.40 | track [+3V3] on F.Cu, length 0.0500 mm | 152.03, 88.33 |
| track [+3V3] on B.Cu, length 0.0707 mm | 144.72, 111.03 | 1 [+3V3] of C-1553C | 142.10, 110.35 |
| track [+3V3] on F.Cu, length 0.0673 mm | 155.20, 91.30 | track [+3V3] on F.Cu, length 0.2000 mm | 154.72, 88.40 |
| 1 [+3V3] of C-USB1-IO5 | 162.20, 94.82 | 5 [+3V3] of NIC-USB1 | 160.20, 97.10 |
| 16 [+3V3] of 1553-XCVR | 134.45, 110.55 | 6 [+3V3] of 1553-XCVR | 137.60, 112.50 |

### `GND` (14)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [GND] on F.Cu, length 0.0500 mm | 137.82, 107.17 | 30 [GND] of 1553-XCVR | 137.20, 106.60 |
| track [GND] on F.Cu, length 0.1414 mm | 158.97, 95.92 | track [GND] on F.Cu, length 0.2828 mm | 158.57, 96.83 |
| via [GND] | 153.88, 98.78 | 2 [GND] of C-485-2 | 152.95, 98.75 |
| 3 [GND] of BARO | 143.78, 110.68 | track [GND] on B.Cu, length 0.9000 mm | 145.28, 110.17 |
| via [GND] | 141.18, 105.97 | track [GND] on B.Cu, length 0.0023 mm | 141.95, 104.50 |
| via [GND] | 141.57, 107.38 | 2 [GND] of C-1553D | 141.65, 109.07 |
| track [GND] on B.Cu, length 0.0707 mm | 146.18, 110.17 | 1 [GND] of X2Y-RS485 | 146.92, 108.60 |
| track [GND] on B.Cu, length 0.5000 mm | 143.82, 111.08 | track [GND] on B.Cu, length 1.3000 mm | 145.53, 113.58 |
| 1 [GND] of X2Y-RS485 | 146.92, 108.60 | 2 [GND] of X2Y-RS485 | 149.08, 108.60 |
| track [GND] on B.Cu, length 1.3500 mm | 136.65, 109.50 | 20 [GND] of 1553-XCVR | 134.45, 108.95 |
| track [GND] on F.Cu, length 3.2000 mm | 151.18, 90.47 | track [GND] on F.Cu, length 0.2000 mm | 153.18, 88.42 |
| track [GND] on B.Cu, length 0.3500 mm | 137.43, 109.58 | 7 [GND] of 1553-XCVR | 137.20, 112.50 |
| track [GND] on B.Cu, length 0.0500 mm | 131.43, 109.58 | 20 [GND] of 1553-XCVR | 134.45, 108.95 |
| track [GND] on B.Cu, length 1.2021 mm | 144.68, 114.42 | track [GND] on B.Cu, length 0.5208 mm | 152.31, 114.70 |

### `GND2_CAN` (4)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 4 [GND2_CAN] of X2Y-CAN | 126.23, 111.35 | 3 [GND2_CAN] of X2Y-CAN | 127.56, 111.35 |
| 3 [GND2_CAN] of X2Y-CAN | 127.56, 111.35 | 2 [GND2_CAN] of C-CAN6 | 128.75, 110.12 |
| 3 [GND2_CAN] of X2Y-CAN | 127.56, 111.35 | 1 [GND2_CAN] of CAN-FD | 132.53, 116.95 |
| 1 [GND2_CAN] of CAN-FD | 132.53, 116.95 | 3 [GND2_CAN] of TVS-CAN | 142.00, 115.80 |

### `GND2_RS485` (4)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| 3 [GND2_RS485] of X2Y-RS485 | 148.00, 109.27 | track [GND2_RS485] on B.Cu, length 1.8000 mm | 148.00, 107.94 |
| 15 [GND2_RS485] of RS485 | 145.85, 106.47 | via [GND2_RS485] | 147.43, 107.37 |
| 3 [GND2_RS485] of TVS-RS485 | 143.14, 120.45 | track [GND2_RS485] on F.Cu, length 0.8500 mm | 147.32, 116.75 |
| track [GND2_RS485] on F.Cu, length 0.8500 mm | 147.32, 116.75 | 3 [GND2_RS485] of X2Y-RS485 | 148.00, 109.27 |

### `PGND` (4)

| From | At (x, y) | To | At (x, y) |
| --- | --- | --- | --- |
| track [PGND] on In2.Cu, length 1.3661 mm | 128.20, 122.10 | track [PGND] on F.Cu, length 0.0500 mm | 130.18, 119.92 |
| track [PGND] on F.Cu, length 0.0707 mm | 167.22, 90.58 | track [PGND] on F.Cu, length 0.0707 mm | 170.88, 91.38 |
| track [PGND] on F.Cu, length 2.4000 mm | 147.78, 92.78 | track [PGND] on In2.Cu, length 0.0500 mm | 153.18, 90.33 |
| track [PGND] on F.Cu, length 0.3500 mm | 138.22, 120.08 | track [PGND] on F.Cu, length 0.0500 mm | 145.47, 119.92 |
