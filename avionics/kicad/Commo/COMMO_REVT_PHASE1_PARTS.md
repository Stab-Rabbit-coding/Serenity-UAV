# Commo Rev T — Phase 1 Part Selection, Power Budget, and RF-Chain Audit

**Plan:** `docs/plans/2026-09-29-001-feat-commo-standalone-bus-node-plan.md` (Phase 1),
`avionics/WBS.md` §1.2a.2.
**Prepared:** 2026-09-29 by Claude Opus 5.5 (Claude Code). Owner review pending
(S. Griffing, GitHub `Stab-Rabbit-coding`).
**Sources:** every value below cites an OEM datasheet in `avionics/datasheets/`. Seven PDFs
were added to that folder on 2026-09-29, either copied from the shared
`SecureControllers/datasheets` library or downloaded from the OEM:

- `Si5351-B.pdf` (Skyworks)
- `mcp4921.pdf` (Microchip DS21897B)
- `lmv331.pdf` (TI SLCS136V)
- `pe4259.pdf` (pSemi)
- `tps7a20.pdf` (TI)
- `MGA-82563-TR1G.pdf` (Avago/Broadcom)
- `2N3866_SERIES.PDF`

The folder also gained `TG2520SMN_en-2584158.pdf` (Epson), `nexperia-PMBT2222A.pdf`,
`mspm0g3519-q1.pdf`, and `tlv757p.pdf`.

## 1. Selected parts (bus, security, power)

| Function | Part | Basis |
|---|---|---|
| MCU | TI **M0G3519QRGZRQ1** (VQFN-48 RGZ) | Owner-approved 2026-09-28. TI SLASFA6B Table 5-1: 1 CAN-FD, 6 UART, 3 I²C, 2 SPI, 44 GPIO. |
| MIL-STD-1553C | Holt **HI-6138PCIF**, the fleet part since 2026-09-28 | DS6138 Rev S. Pin table and footprint in `../HI6138_FOOTPRINT_VERIFICATION.md`. |
| 1553 magnetics | Premier **PM-DB2791S** 1:2.5 + 2 × 55 Ω + 2 × SMAJ33CA | DS6138 Fig. 28; [REF-MIL-001 §4.5.1.5.2]. The coupling mode (direct or transformer) follows the stub length at the antenna site (Phase 4). |
| 1553 MCLK | ECS **ECS-2520MV-500-BN-TR** 50 MHz | DS6138 Table 1 requires 50.0 MHz ± 100 ppm; this part is ± 50 ppm. |
| Isolated CAN-FD | TI **ISOW1044BDFMR** | Fleet part (Pilot, TACCO, gateway). Pin table reused from `Pilot/scripts/gen_pilot_sch.py`. |
| Isolated RS-485 | TI **ISOW1412DFMR** | Fleet standard (the ADM2795E → ISOW1412 swap, 2026-07-26). The plan's "ADM2795E" is corrected here. |
| Security element | Infineon **OPTIGA Trust M** (SLS32AIA) | Fleet SE on non-cape boards (Observer, ESC, servo). Default I²C address **0x30**. |
| I²C address check | Si5351A **0x60** (Si5351-B "LSB pin option … default address is 0x60") vs. OPTIGA **0x30** | No conflict; both can share one I²C bus. |
| Logic 3.3 V | TI **TPS62933** buck, +5V → +3V3 | Fleet part (Pilot, TACCO). Sized by the HI-6138: ICC2 = 670 mA typical, **695 mA max** while transmitting at 100 % duty into 78 Ω, with VDD 3.15–3.45 V (DS6138 §24.3). An LDO cannot deliver that. |
| RF-analog 3.3 V | TI **TPS7A2033** LDO, 300 mA, from +5V_FILT | Replaces the MCP1703 (Microchip's site blocks downloads, and the "CB" package in the Rev S BOM is 3-pin while the board has a 5-pin land). TPS7A20 PSRR is **95 dB at 1 kHz** (TI datasheet §1), which meets the Rev S PSRR rationale for the DDS supply. |
| Power input | +5 V from the fleet 5 V / 10 A avionics bus (`docs/POWER_DISTRIBUTION.md` §3) through a shielded JST-GH 2P, the same as Observer's J_PWR | — |

## 2. Power budget (+5 V avionics bus)

| Load | Worst case | Source |
|---|---|---|
| RFD900ux-SMT, TX at 30 dBm | **1.0 A** peak at 5 V (5.0–5.5 V required) | RFD900ux datasheet v1.2 |
| RFD900ux, RX/standby | 45 mA | same |
| HI-6138, one bus transmitting at 100 % duty | 695 mA at 3.3 V ≈ **0.51 A at 5 V** (TPS62933 at about 90 % efficiency; confirm against the TPS62933 efficiency curves) | DS6138 §24.3 |
| HI-6138, idle | 25 mA max at 3.3 V | same |
| ISOW1044, bus dominant | 211 mA max (VDD) | ISOW1044 datasheet |
| ISOW1412, transmitting | 131 mA max | ISOW1412 datasheet |
| MCU, SE, DDS, DAC, comparators, TCXO | < 60 mA total | datasheet run currents |
| **Simultaneous worst case** | **≈ 1.9 A at 5 V (9.5 W)** | — |

Rev T replaces **two** Rev S Commo capes, each carrying an RFD900ux, with **one** node. The
fleet 5 V bus therefore loses one 1 A SiK transmitter peak. The HI-6138 transmit current is
new to Commo but is the same fleet-wide 1553 load Pilot and TACCO already carry. The input
connector, ferrite bead, and bulk capacitance are sized for 2 A continuous.

## 3. RF-chain audit — BLOCKER for Phase 2

The plan says to port the 49 MHz chain "unchanged". Checking the Rev S netlist, which was
exported from the as-placed PCB on 2026-07-04, against the OEM datasheets shows that the
chain **cannot work as wired**. Porting it unchanged would repeat these errors on a new board.

| Part (Rev S ref) | Rev S wiring | Datasheet | Verdict |
|---|---|---|---|
| Si5351A-B-GT (`49M DDS`) | 1 +3V3, 2 GND, 3 DDS_RF, 4 GND, 5 GND, 6 DDS_CLK, 7 DDS_DAT, 8 TCXO_OUT, 9 GND, 10 +3V3 | Si5351-B Table 20, 10-MSOP: 1 VDD, 2 XA, 3 XB, 4 SCL, 5 SDA, 6 CLK2, 7 VDDO, 8 GND, 9 CLK1, 10 CLK0 | **Wrong on 9 of 10 pins.** The TCXO drives GND, I²C is grounded, and the RF output comes from XB. Fixable: §6.6 allows a clock on XA through 0.1 µF with XB floating. |
| TG2520SMN (`TCXO 25M`) | 1 +3V3, 2 GND, 3 OUT, 4 +3V3 | Epson pin map: 1 N.C. ("keep OPEN or GND"), 2 GND, 3 OUT (clipped sine, DC-cut 0.01 µF), 4 VCC | Pin 1 is tied to VCC against the datasheet. Fixable. |
| PE4259 (`T/R Sw`) | 1 ANT, 2 GND, 3 RF_RX, 4 PTT_N, 5 RF_FILT, 6 GND | pSemi Table 7: 1 RF1, 2 GND, 3 RF2, 4 CTRL, 5 **RFC (common)**, 6 **VDD** | **VDD is grounded**, and the antenna is on RF1 instead of the common port. Fixable: RFC = ANT, RF1 = TX, RF2 = RX, VDD = +3V3. |
| MGA-82563 (`LNA`) | 1 RX_LNA, 2 RSSI_RAW, 3 RF_RX, 4 +3V3, 5 GND, 6 GND | Avago: 1, 2, 4, 5 GND; 3 INPUT; **6 OUTPUT and Vd** | Output and supply are grounded, and pin 1 is used as an output. It needs a bias-tee (RF choke + DC block), which the Rev S board lacks. Fixable, with new parts. |
| **RX demodulator** | LNA → "1.2k / 2.2k RC bandpass" → LM393 comparator | — | **No detector exists.** Audio-frequency RC filters sit directly on a 49 MHz RF signal, with no mixer, discriminator, or FM/AFSK detector. **Not fixable by re-pinning; needs an architecture decision.** |
| LM393 (`RX Demod`) | 5-pin SOT-23-5 | TI SLCS005AH: dual comparator, 8-pin only | No such part. Use an LMV331 (SOT-23-5, TI SLCS136V), the same part as `RSSI_CMP`. |
| MCP4921 (`TX DAC`) | "SOT-23-8" land | Microchip DS21897B: 8-pin PDIP / SOIC / MSOP only | Land does not exist. Use MSOP-8. |
| 2N3866 (`PA 100mW`) | SOT-89 land | 2N3866 series datasheet: **TO-39 metal can only**, 1 W at 28 V class | No SMD part exists. Also 1 W class against a §15.235 limit of about 48 µW conducted (Commo.md "Regulatory Constraints"). Needs an owner decision on the PA. |
| MCP1703T-3302E/CB (`LDO 3V3`) | 5-pin land | "CB" = SOT-23A-**3** | Replaced by the TPS7A2033 (§1). |
| PMBT2222A / MMBT2222A (`PA Drvr`) | 1 DDS_RF, 2 GND, 3 PA_INT | Nexperia Table 2: 1 B, 2 E, 3 C | Consistent (base drive, grounded emitter, collector out). |
| Passives | `PA Rb2`, `TX Bead`, `RX Bead`, `PTT Bead`, `ANT CMC`, `PGND 10n`, `GND X2Y`, `Th Hi` each have both pads on one net | — | These parts do nothing. Their intended nets are not recoverable from the Rev S record. |
| UART / SBUS path (`UART CMC`/`TVS`, `INV1`, `MUX1`, `S1`, beads) | Host UART to a "modem" that does not exist; `UART_TX_F` and `UART_RX_F` dangle | — | Obsolete in Rev T: the MCU runs AFSK in firmware. **Dropped.** |

**What Phase 2 can do without an owner decision:**

- the MCU, 1553, CAN-FD, RS-485, SE, power, and SiK sections;
- the TX chain (TCXO → Si5351A CLK0 → MCP4921 AFSK modulation), with the datasheet pin fixes
  above.

**What needs an owner decision:**

1. **49 MHz receive architecture.** Options:
   - (a) a discrete mixer and FM IF receiver, with AFSK decoded by the MCU ADC;
   - (b) a single-chip sub-GHz transceiver whose band reaches 49 MHz and that supports
     AFSK. The datasheet must be verified before selection; none is on file.
2. **49 MHz power amplifier.**
   - The TO-39 2N3866 class stage cannot be built as a surface-mount part.
   - It is also about 35 dB over what §15.235 permits.
   - A low-power stage, or driving the antenna match straight from the Si5351A CLK0
     (about 8 mA CMOS into the LPF), should be checked against the §15.235
     field-strength limit instead.
