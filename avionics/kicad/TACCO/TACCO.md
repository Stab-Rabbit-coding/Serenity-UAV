# TACCO — EMI-Hardened Communications, Logging & Payload Cape

**Callsign:** TACCO (Tactical Coordinator)
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
see `docs/attribution_and_licensing.md`
**Revision:** R (Rev R baseline — TACCO naming finalized; EMI-hardened variant of TACCO Rev M, Ethernet PHY restored)
**Date:** 2026-06-07
**Update 2026-09-29 (area recovery + mLRS bare-chip radio + fab-ready layout, S. Griffing
decisions; implemented by Claude Fable 5.1):** see `avionics/WBS.md` §1.2a "TACCO area recovery,
mLRS bare-chip radio, non-stack rails, and fab-ready layout" for the full decision record.
- **Radio:** the Seeed Wio-E5 module (Chinese-built) is replaced by a bare ST **STM32WLE5JC**
  (`MLRS-MCU`) with an Epson TG2520SMN 32 MHz TCXO and a pSemi PE4259 antenna switch. mLRS pin
  map and the `UART_WIOE5_*` net names are unchanged. **RF matching values are placeholders
  pending ST AN5457 verification and bench tuning** — do not fly the radio before that.
- **Bead defect fixed:** the eight SDIO/UART signal beads were the 1812 5 A power bead
  (742792510); they are now 0402 600 Ω positions (MPN: owner to select). `FB1` keeps 742792510.
- **Smaller parts, same function:** boot/bind switch → C&K KMR2; SWD header → Tag-Connect
  TC2030-NL pads. PB2 rails are non-stack-through (Commo Rev T is standalone).
- **PB2 header map rebuilt from the real PocketBeagle 2 schematic** (owner-supplied,
  `avionics/datasheets/pocketbeagle2_sch.pdf`): the Rev S2 map had GND on the PB2's 5 V VIN pin
  and peripherals on the wrong balls. Verified map and allocation:
  `avionics/kicad/PB2_HEADER_PINMAP.md`. Ethernet is now RMII2 + MDIO0 (`RMII2_*` nets),
  CAN-FD on MCAN0 (P2-5/7), RS-485 on UART2 with hardware DE, mLRS on UART0, BT on UART1.
- **Wi-Fi host interface:** SDIO is not on the PB2 headers, so the Type 2EL WLAN core cannot
  be hosted; the SDIO beads are deleted. **Owner decision: Wi-Fi moves to a USB module on USB1
  (P1-9/11); module selection with datasheet is open and blocks fab** (WBS §1.2a).
- **DP83825I pin table corrected** against TI SNLS638C Table 4-1 (the previous table was not
  this part's pinout; Pilot shares the defect). Pin 2 (50MHzOut) drives `RMII2_REF_CLK`.
- **Layout:** owner authorized full auto-placement and autorouting; the §1/§11–13 layout
  constraints below still apply (outline now 60 × 35 mm, §13b). All 170 parts are placed on the 55 × 35 mm outline with 0 DRC
  errors before routing (isolation band and GND2 islands follow the transceiver positions;
  small bypasses use the top-face cells between the non-stack-through rail pins). Routing,
  Gerber and remaining gates are tracked in the WBS entry.

**Update 2026-09-28 (MIL-STD-1553C fleet swap, S. Griffing decision; implemented by Claude
Opus 5.5):** `1553-XCVR` is now the **Holt HI-6138** protocol engine on the SPI0_B bus,
replacing the HI-1573 and the PRU Manchester codec.
- **Generator:** `gen_tacco_sch.py` was first brought back in line with the committed
  schematic, proven netlist-identical. Then the swap was applied.
- **Gates:** ERC 0; DRC 169, equal to the pre-change baseline (no new violations), with 0
  schematic-parity issues.
- **Owner action:** the four new parts (`X-50M` 50 MHz MCLK oscillator, `C-50M`, `C-1553D`,
  `R-1553IRQ`) are **parked off-board**. No collision-free site exists on either side within
  20 mm, so they need manual placement (`avionics/WBS.md` §1.2a.3).
- **References:** pin table in `../HI6138_FOOTPRINT_VERIFICATION.md`.
**Status (2026-09-23 update, S. Griffing):** The Rev S1 reconciliation described below is
SUPERSEDED — the legacy schematic/PCB pair (169 sch refs vs 43 PCB footprints, 564 ERC
violations) was not patchable and has been replaced by a from-scratch schematic-first rebuild
(`avionics/kicad/TACCO/scripts/gen_tacco_sch.py` / `gen_tacco_pcb.py`), the same method used for Pilot.
**ERC is 0.** PCB placement is IN PROGRESS: board-area math showed the full component set does
not fit the 55x35mm two-sided envelope this section's §1 requires (confirmed by an actual
placement run, not just an area estimate); the winch and SG90 door servos were moved to
bus-networked (CAN-FD/RS-485) control per owner correction (they were never meant to be driven
locally — see WBS.md), and the 3 SMA antenna jacks became vertical MMCX — this recovered enough
area to get close, but the owner is finishing placement by hand in KiCad rather than continuing
to iterate the auto-placer. **Note:** this rebuild restored LoRa/RFM95W (contradicting this
section's old claim that Rev S1 removed it — TACCO.md's own §13 antenna-filter BOM already listed
RFM95W, a second internal contradiction in this doc alongside the Ethernet one below); see
avionics/WBS.md for the full rebuild trail and two flagged part-number defects (Johanson filter
MPNs, microSD connector MPN) that need owner confirmation. See WBS.md's "TACCO schematic-first
rebuild" and "TACCO PCB placement" items for the authoritative current state; the paragraphs below
describe the PRE-REBUILD Rev R/S1 history and are kept for record only.

**Status (2026-09-26 correction, S. Griffing / Claude Sonnet 5) — RADIO SWAP, supersedes the
"restored LoRa/RFM95W" claim above, which is wrong for the current schematic:** This board never
carries LoRa/RFM95W in its current, post-2026-09-21 form. The 2026-09-21 radio-relocation
(`avionics/WBS.md` §1.2a "APPROVED DIRECTION") did two things across two boards:

| | Before | After |
|---|---|---|
| **This board (XO, renamed TACCO 2026-09-22)** | SiK modem (RFD900ux-SMT) | **mLRS radio on a Seeed Wio-E5 (STM32WLE5) module** — refs `WIOE5`, `C-WIOE5-*`, `D-ANT-WIOE5`, `J-ANT-WIOE5`, `FB-WIOE5-*`, `LED-WIOE5-*`, `R-WIOE5-*`, `SW-WIOE5-BOOT` |
| **Commo** | LoRa modem (RFM95W) | **SiK modem (RFD900ux-SMT)**, the exact unit relocated from this board |

`avionics/kicad/TACCO/kicads/TACCO.kicad_sch` currently has **zero** `RFM95W`/`LORA` symbol
references (confirmed by grep) and 143 `WIOE5`-refixed component references. The "restored
LoRa/RFM95W" note above appears to have been written against a different/earlier schematic state
and does not describe the file as it exists now. Also fixed same-day: the 2026-09-22 XO->TACCO
repo-wide rename left `sym-lib-table` pointing at a now-nonexistent `XO.kicad_sym` under the
nickname `XO`, and every symbol instance's `lib_id` still read `"XO:S_*"` — this silently broke
ERC (**143 `lib_symbol_issues` violations**, not the "ERC is 0" this status block claims above).
Both the lib table and the 429 stale `"XO:` prefixes in `TACCO.kicad_sch` are now corrected;
`kicad-cli sch erc` genuinely reports **0 violations** as of this note. PCB DRC is unaffected by
the rename (`TACCO.kicad_pcb` never referenced the `XO` symbol library) and remains at 169
violations / 0 schematic-parity issues, per `avionics/WBS.md` §1.2a.

**Status (superseded, pre-2026-09-20):** Schematic complete — PCB layout pending. **Rev S1
reconciliation IN PROGRESS (2026-07-04):** the PCB is already at the intended end-state (LoRa
removed, P1/P2 +TOP passthrough rails placed) but the **schematic lags** — it still carries the
LoRa block, the now-obsolete `J_XCVR` Commo-cable connector, and an SBUS block, and uses a
**different reference-designator convention** from the PCB (only ~10 of ~50 refs match). A
load-blocking stray-`(comment)` bug in `TACCO.kicad_sch` was fixed 2026-07-04 (it now opens in
kicad-cli). The remaining schematic reconciliation needs a **user-confirmed sch↔pcb
reference-designator remap** before edits — see TODO.md §1.2b and `avionics/AGENTS.md`.

---

## Purpose

TACCO is the electromagnetic-environment-hardened communications, logging, and payload cape
designed for the same harsh nacelle and fuselage EM environment as Pilot.
The communications payload of this cape (SiK 915 MHz, LoRa 915 MHz, WiFi 2.4/5 GHz,
49 MHz Part 15 §15.235) is inherently more susceptible to radiated interference than the purely
digital Pilot, so hardening concentrates on conducted immunity for the wired
buses and supply rails, and on keeping the RF subsystem's susceptibility low through
better supply filtering and digital-interface isolation from the RF groundplane.

---

## Changes from CAPE-B (Rev M)

### 1. Ethernet PHY removal (space recovery)

Identical rationale to Pilot: both DP83825I PHYs, their magnetics, and the two
ETH-P/ETH-N JST-GH connectors are removed. The 22 P2 expansion-header pins formerly
allocated to RMII0/1, MDC, MDIO, and PHY control signals become no-connect.

The freed board area (approximately 20 × 12 mm) accommodates the new EMI filter components
without any overall board size increase from the TACCO 55 × 35 mm footprint.

### 2. CAN FD transceiver: ATA6561 → ISOW1044BDFMR

Identical substitution to Pilot. See Pilot.md §2 for full rationale.
The isolated transceiver (ISOW1044BDFMR, SOIC-16, DigiKey 296-ISOW1044BDFMRCT-ND)
provides 5 kV reinforced isolation, ±42 V bus fault tolerance, and an integrated DC/DC
converter that generates the isolated bus-side supply from the 3.3 V logic rail.

### 3. RS-485 transceiver: MAX3485E → ADM2795EBRWZ → ISOW1412 (REF-SENSOR-010)

Identical substitution to Pilot. See Pilot.md §3 for full rationale (ADM2795EBRWZ
superseded fleet-wide 2026-07-26 by TI ISOW1412, which integrates its own isolated
DC-DC — REFERENCES.md REF-SENSOR-010). Half-duplex direction-control via RS485_DE
(tied to both DE and RE_N) is preserved. XO's pre-existing ADM2795EBRWZ symbol had
the same incorrectly-numbered-pins defect as Pilot's, corrected in the same pass
(`avionics/kicad/fix_wash_zoe_isolators.py`). XO's PCB footprint has not yet been
swapped to ISOW1412 (open work, root `TODO.md` §1.2a).

### 4. Common-mode chokes on CAN and RS-485 bus lines

| Reference | Bus | Part | Spec |
| --- | --- | --- | --- |
| CM1 | CAN FD | Bourns SRF2012-100Y | 100 Ω @ 100 MHz, 800 mA |
| CM2 | RS-485 | Bourns SRF2012-100Y | 100 Ω @ 100 MHz, 800 mA |

### 5. TVS diode arrays on all external field connectors

| Reference | Connector | Part | Clamp |
| --- | --- | --- | --- |
| TVS-CAN | CAN-A JST-GH | PRTR5V0U2X | 5.5 V, bidirectional |
| TVS-485 | RS485-A JST-GH | PRTR5V0U2X | 5.5 V, bidirectional |
| TVS-1553 | 1553-A JST-GH | SMAJ33CA × 2 | 33 V, bidirectional, 400 W |
| TVS-XCVR-49MHZ | XCVR-49MHZ J1 header | PRTR5V0U2X | 5.5 V — on UART_TX/RX and PTT_N |

The XCVR-49MHZ 6-pin JST-GH header J1 adds TVS protection because the 49 MHz sub-module
cable run may be several cm long inside the bay, acting as a short antenna for
RF ingress into the UART lines.

### 6. SiK 915 MHz module supply and signal filtering

The SiK module (RFD900x form-factor UART-connected radio) has its power and control
lines treated as follows:

- **Supply:** A 10 µF + 100 nF MLCC decoupling pair placed ≤ 1 mm from the module

  VCC pin, in addition to the existing 100 µF + 100 nF bulk cap array (U16 in TACCO).

- **UART lines (UART_SIK_TX/RX):** A ferrite bead (Würth 742792510, 600 Ω @ 100 MHz,

  100 mA, 0402) in series with each line before the module header. These beads suppress
  RF currents at 915 MHz and above that could be conducted back from the SiK antenna
  onto the digital UART traces.

- **CTS/RTS:** Same ferrite bead on each handshake line.

### 7. LoRa (RFM95W) SPI bus filtering

The RFM95W module SPI lines are a potential EMI ingress path because the module PCB
antenna radiates at 915 MHz. A common-mode choke (CM3, Bourns SRF2012-100Y) is inserted
on the SPI clock + MOSI pair at the module side. The SPI chip-select (SPI1_CS_LORA)
and DIO interrupt lines (LORA_DIO0) each receive a 33 Ω series resistor (damping, not
filtering) to suppress RF common-mode currents — this is a minimal-footprint approach
that avoids adding inductors on timing-sensitive SPI lines.

### 8. WL1837MOD SDIO bus filtering

The TI WL1837MOD WiFi module uses SDIO at up to 50 MHz. The 2.4/5 GHz transmit power
(peak 550 mA on +3V3_RF) creates a strong local interference source. To prevent
WiFi TX switching noise from coupling into the digital SPI and UART lines:

- Ferrite beads (Würth 742792510) on SDIO_CLK, SDIO_CMD, and each SDIO_D0–D3 line

  at the module-to-SoC end. These attenuate 2.4 GHz common-mode ingress from the
  SDIO lines without significantly degrading SDIO eye quality at 50 MHz (ferrite bead
  impedance ≈ 600 Ω at 100 MHz vs. < 10 Ω at 50 MHz — negligible signal loss).

- A separate TPS63031 output LC filter stage: added 1 µH inductance in series with the

  existing SMPS output, followed by 47 µF MLCC, to reduce RF ripple on the +3V3_RF
  WiFi supply from the TPS63031 switch-mode regulator.

### 9. XCVR-49MHZ sub-module header (J1) EMI filter

The J1 6-pin JST-GH header connecting to the Commo sub-module has the following
protection:

- TVS-XCVR-49MHZ (PRTR5V0U2X): protects UART_49MHZ_XCVR_TX, UART_49MHZ_XCVR_RX, and PTT_N lines
- Ferrite beads (FB-XCVR-49MHZ, Würth 742792510) in series with the UART lines before J1:

  prevents 49 MHz RF energy from entering the SoC UART interface via the cable stub

- RSSI_ANA line: 1 nF C0G cap to ground for HF noise filtering (not ferrite bead, to

  avoid distortion of the DC–3 kHz RSSI analog signal)

- 5V power pin: 10 µF + 100 nF local decoupling at J1

### 10. Power entry filter

Identical to Pilot: π-filter (C11 = 47 µF, FB1 = Würth 742792512, C12 = 10 µF +
100 nF) on the +5V supply at J-PWR. See Pilot.md §6.

### 11. Chassis ground (PGND) implementation

Same single-point chassis ground topology as Pilot. PGND additional connections
specific to XO:

- SMA connector shields for all antenna ports (SMA-915-SIK, SMA-915-LORA, SMA-WIFI,

  SMA-49) — all connected to PGND, not GND, to keep RF return currents off the
  signal ground plane.

- Mounting holes × 4: PGND via 0 Ω solder-selectable links.
- PGND-to-GND star point: single 0 Ω / 10 Ω link at J-PWR under the bay mounting boss.

### 12. RF supply decoupling (upgraded from TACCO)

TACCO had 100 µF + 100 nF per radio VCC (U16 ferrite + bulk cap array). XO
upgrades to:

| Radio | Input supply filter | VCC bypass |
| --- | --- | --- |
| SiK RFD900x | 10 µH inductance + 47 µF (before module VCC) | 100 nF + 10 nF at module pin |
| RFM95W | 100 Ω ferrite + 10 µF + 100 nF | 100 nF + 10 nF at module pin |
| WL1837MOD | TPS63031 output + 1 µH + 47 µF (XO added) | 10 µF + 100 nF at module pin |
| XCVR-49MHZ J1 | 10 µF + 100 nF at J1 pin | (on Commo board) |

---

## PCB Layout Constraints (additions to TACCO rules)

The Pilot layout constraints apply equally here, including the ≥ 8 mm creepage / ≥ 1.5 mm
clearance requirement between GND1 and GND2 copper pours on the ISOW1044BDFMR and
ADM2795EBRWZ [REF-IEC-001 §5.5.2] [REF-VDE-001 Cl.4.3] — see Pilot.md "Isolation creepage."

> **Verification status (2026-06-22, `kicad-cli pcb drc` against `TACCO.kicad_pcb`,
> KiCad 9.0.2): NOT MET — BLOCKS PCB fab.** Same finding as Pilot, with different
> numbers: after excluding same-package pin-to-pin spacing, DRC found **9 genuine
> cross-domain clearance violations** between the `TMESH_P`/`TMESH_N` tamper-detect
> mesh (and, in one case, a primary-side Ethernet PHY ground pad) and the isolated
> `GND2_CAN`/`GND2_RS485` domains, with actual measured spacing as low as **0.0 mm**
> (direct contact) — short of the 0.5 mm `ISOLATION` netclass DRC minimum and the
> ≥ 8 mm physical creepage target. Tracked in `TODO.md` §1.2a alongside Pilot's
> equivalent finding. Not fixed here — referred to the user per `AGENTS.md`'s
> manual-footprint-placement policy.

Additional XO specifics:

- **RF groundplane moat:** The RFD900x and RFM95W occupy the same RF section as in

  TACCO (right 30 mm of board). The isolation moat between the RF groundplane and
  the digital groundplane shall be maintained; the moat capacitors (10 nF X2Y) bridge
  the moat at RF frequencies, referenced to PGND on the RF side and GND on the digital
  side.

- **SMA shield contacts:** All four SMA connectors shall have their shells soldered to

  a PGND copper pour, NOT to the digital GND pour. Route a 3 mm PGND pour around each
  SMA mounting footprint.

- **Ferrite bead orientation:** SDIO and SPI ferrite beads shall be oriented with their

  axis perpendicular to the associated RF trace runs (per Würth EMC design guide).

- **XCVR-49MHZ header J1:** Place within 5 mm of the board edge so the cable run to the

  Commo module is minimised. Apply a PGND guard pour around J1.

---

## 13. Antenna Port Filter Chains (Rev R baseline; introduced Rev A)

Each on-board RF transceiver has a dedicated antenna filter chain between its ANT pin
and the SMA panel-mount connector. The goal is to prevent out-of-band conducted RF
energy (from other transmitters sharing the bay) from reaching the receiver LNA or
the digital bus lines, while keeping in-band insertion loss below 1 dB.

### Topology (identical for all three chains)

```
 Module ANT pin
      |
  [LORA_ANT / WIFI_ANT / J_SIK_ANT]  ← global net label or U.FL
      |
  FL_xxx  (bandpass filter, series)
      |
      +----[D-ANT-xxx  ESD101-B1-02ELS]---- PGND   ← shunt ESD clamp
      |
  J_SMA_xxx  (SMA bulkhead connector)
      |
  PGND  (connector shell)
```

### Component selection rationale

**Bandpass filters:**

| Reference | Part | Pass-band | IL | Rejection |
|---|---|---|---|---|
| FL_LORA | Johanson 0915LP15B0100E | 902–928 MHz | ≤ 0.6 dB | > 25 dB @ 2× f |
| FL_SIK  | Johanson 0915LP15B0100E | 902–928 MHz | ≤ 0.6 dB | > 25 dB @ 2× f |
| FL_WIFI | Johanson 2450BP15B050E  | 2400–2500 MHz | ≤ 0.5 dB | > 20 dB flanks |

Both 915 MHz radios (LoRa and SiK) share the same BPF part number — they operate in
the same band and there is no benefit to using separate filters.

**RF ESD protection** (revised 2026-09-26, avionics/WBS.md U7.1):

| Reference | Board | Part | Capacitance | VRWM | Package |
|---|---|---|---|---|---|
| D-ANT-WIOE5 | TACCO | Infineon ESD101-B1-02ELS | 0.1 pF typ (1 GHz), 0.2 pF max (1 MHz) | ±5.5 V | TSSLP-2-4 (0201) |
| D-ANT-RADIO | TACCO | Infineon ESD101-B1-02ELS | 0.1 pF typ (1 GHz), 0.2 pF max (1 MHz) | ±5.5 V | TSSLP-2-4 (0201) |
| D-ANT-SIK | Commo | Infineon ESD101-B1-02ELS | 0.1 pF typ (1 GHz), 0.2 pF max (1 MHz) | ±5.5 V | TSSLP-2-4 (0201) |

Values from the Infineon ESD101-B1-02 Series datasheet Rev 1.4 (2017-10-26),
p. 4 and Sec. 4.1. The previous part, Semtech RCLAMP0502B, is deprecated (owner,
2026-09-26); its 0.15 pF figure quoted here earlier was never backed by a
datasheet in this repository. The suggested successor RClamp0504FA was
rejected for these ports: it is a 3 pF USB-class array (Semtech datasheet,
"no insertion loss to 2.0 GHz"), which as a 50 Ω shunt costs about 0.7 dB at
915 MHz and 3.7–8.8 dB on the 2.4/5 GHz Type2EL feed. At 0.2 pF worst case the
ESD101-B1 mismatch loss is about 0.04 dB at 2.45 GHz and 0.13 dB at 5.5 GHz.
The digital-line PRTR5V0U2X TVS is not suitable for RF antenna ports.

**SiK U.FL input (J_SIK_ANT):**

The RFD900x module carries an integrated U.FL antenna connector. A Hirose
U.FL-R-SMT-1 pad on the Cape (J_SIK_ANT) receives the module's pigtail. The filter
chain then routes from J_SIK_ANT through FL_SIK and D_ANT_SIK to J_SMA_SIK.
The U.FL GND pin connects to PGND (chassis ground), keeping RF return current off
the digital ground plane.

**SMA connectors (J_SMA_LORA, J_SMA_WIFI, J_SMA_SIK):**

Standard 50 Ω vertical SMA PCB bulkhead jacks. Shell (pin 2) connects to the PGND
copper pour, consistent with §11.

### PCB layout constraints (additions)

- **50 Ω trace geometry:** Route all traces from module ANT pin to BPF input and from
  BPF output to SMA as 50 Ω microstrip. For a standard 4-layer 1.6 mm FR-4 with
  0.2 mm dielectric to inner ground plane, 50 Ω microstrip width ≈ 0.35 mm.
- **BPF placement:** Place FL_LORA and FL_SIK as close as possible to the RFM95W and
  RFD900x module U.FL/antenna pads respectively (≤ 5 mm trace from ANT pin to filter
  pad). Place FL_WIFI ≤ 5 mm from WL1837MOD ANT pin.
- **Antenna ESD placement:** Place D_ANT_xxx immediately after the BPF (between BPF output
  and SMA pin 1). The shunt path to PGND shall be as short as possible (via directly
  to PGND plane, no daisy-chain routing).
- **Keep the RF trace in the BPF-to-SMA segment entirely within the RF groundplane
  moat region** (right 30 mm of board). Do not route it over the digital GND pour.
- **SMA pad PGND pour:** Each SMA footprint shell shall have a ≥ 3 mm PGND copper pour
  ring as specified in §11.

---

## Eliminated vs. TACCO Bill of Materials (delta)

### Removed

| Reference | Part |
| --- | --- |
| ETH1-PHY | DP83825I Ethernet PHY |
| ETH2-PHY | DP83825I Ethernet PHY |
| U11 (TPS62933) | 3.3→1.8 V SMPS for PHY AVDD |
| ETH-P connector | JST-GH 6-pin |
| ETH-N connector | JST-GH 6-pin |
| CAN-TR (ATA6561) | Non-isolated CAN FD transceiver |
| RS485 (MAX3485E) | Non-isolated RS-485 transceiver |

### Added

| Reference | Part | Function |
| --- | --- | --- |
| CAN-ISO | ISOW1044BDFMR | Isolated CAN FD (5 kV) |
| RS485-ISO | ISOW1412 | Isolated RS-485 (5 kV, ±42 V) |
| CM1 | Bourns SRF2012-100Y | CAN CMC |
| CM2 | Bourns SRF2012-100Y | RS-485 CMC |
| CM3 | Bourns SRF2012-100Y | LoRa SPI CMC |
| TVS-CAN | PRTR5V0U2X | CAN connector TVS |
| TVS-485 | PRTR5V0U2X | RS-485 connector TVS |
| TVS-1553 | SMAJ33CA × 2 | 1553 connector TVS |
| TVS-XCVR-49MHZ | PRTR5V0U2X | XCVR-49MHZ header TVS |
| FB1 | Würth 742792512 | 5V power entry bead |
| FB-SIK × 4 | Würth 742792510 | SiK UART + CTS/RTS beads |
| FB-XCVR-49MHZ × 3 | Würth 742792510 | XCVR UART + PTT beads |
| FB-SDIO × 6 | Würth 742792510 | SDIO bus beads |
| L1 | 1 µH / 1 A | WiFi supply added inductor |
| C11–C15 | Various MLCC | Power filter capacitors |
| C13, C14 | 4.7 nF X2Y | Isolation boundary CM caps |
| FL_LORA | Johanson 0915LP15B0100E | LoRa ANT bandpass filter |
| FL_SIK | Johanson 0915LP15B0100E | SiK ANT bandpass filter |
| FL_WIFI | Johanson 2450BP15B050E | WiFi/BT ANT bandpass filter |
| D-ANT-WIOE5 | Infineon ESD101-B1-02ELS | LoRa/mLRS ANT ESD shunt (0.1 pF) |
| D-ANT-SIK | Infineon ESD101-B1-02ELS | SiK ANT ESD shunt (0.1 pF) — on Commo |
| D-ANT-RADIO | Infineon ESD101-B1-02ELS | Wi-Fi/BT ANT ESD shunt (0.1 pF) |
| J_SIK_ANT | Hirose U.FL-R-SMT-1(10) | SiK module pigtail U.FL receptacle |
| J_SMA_LORA | SMA bulkhead jack (50 Ω) | LoRa 915 MHz antenna SMA output |
| J_SMA_WIFI | SMA bulkhead jack (50 Ω) | WiFi/BT 2.4 GHz antenna SMA output |
| J_SMA_SIK | SMA bulkhead jack (50 Ω) | SiK 915 MHz antenna SMA output |

---

## Power Budget (updated)

| Rail | Consumers | Max current |
| --- | --- | --- |
| +5V (filtered) | PB2 VIN, DRV8833 motor, radio modules | 3.0 A |
| +3V3_RF (SMPS) | RFD900x (1.2 A TX peak), RFM95W (120 mA TX), WL1837MOD (550 mA TX) | 1.5 A continuous, 2.0 A peak |
| +3V3 logic (LDO) | MAX3485E→ADM2795, ATA6561→ISOW1044B, DS26LV31/32, HX711, SLB9672, ATF16V8BQL | 350 mA |

DP83825I removal saves approximately 100 mA from the 3.3V logic rail, leaving additional
headroom absorbed by the new isolated transceivers (~80 mA combined increase).

---

## EMC Compliance Targets

Same as Pilot: IEC 61000-4-2 Level 4 [REF-IEC-003], IEC 61000-4-4 Level 4 [REF-IEC-004],
IEC 61000-4-5 Level 3 [REF-IEC-005], MIL-STD-461G RE102 Limit C, RS103 200 V/m [REF-MIL-002].

Additional RF susceptibility note: the RFD900x and RFM95W modules have their own
internal LNA protectors. The PRTR5V0U2X TVS arrays on J1 protect the UART interface,
not the antenna port. Antenna port protection is now provided by the ESD101-B1-02ELS ESD
shunts (D-ANT-WIOE5, D-ANT-RADIO; D-ANT-SIK on Commo) and by the BPF series filters (FL_LORA,
FL_WIFI, FL_SIK) as documented in §13. The SMA connector shell PGND connection and
antenna cable shielding provide the primary conducted shield path.

---

## §13a — PB2 Rail Sockets and Isolation Band (2026-10-05)

Decision record: `avionics/WBS.md`, "PB2 rail geometry correction", R3 ("Do 1+2").

**Geometry.** Rail centre-lines 4.80 mm (0.189 in) inside each long edge, 25.4 mm (1.00 in)
apart [REF-SENSOR-041 Fig. 3.45]. Sockets: Samtec **SSM-118-L-DV-LC**, bottom face,
`Serenity-Custom:PocketBeagle2_2x18_P{1,2}_SSM-DV-LC` built from `samtec_ssm_footprint.pdf`
Rev D Fig. 4 (pads 1.02 x 2.22 mm, centres +/-2.825 mm, outer pad edge 3.94 mm from the
centre-line, ~0.86 mm inside the board edge) [REF-SENSOR-042].

**Mechanical retention (owner request 2026-10-04).**
- The -LC locking clip puts one clip per socket end through a 1.19 mm (0.047 in) NPTH at
  +/-20.32 mm on the centre-line, so each socket is anchored through the board at both ends —
  the same "through-board only at the ends" pattern as the PB2's own SMT headers, which carry
  through-hole pins only at positions 1/2 and 35/36 [REF-SENSOR-041]. -LC needs manual
  placement (Samtec drawing note 8): the assembly order must call it out.
- The SSM catalog cites Severe Environment Testing aligned with MIL-DTL-55302; the mating
  TSW/SSW family is qualified to 7.56 G RMS random vibration (50–2000 Hz, 2 h/axis,
  EIA-364-28 V-B) and 100 G / 6 ms shock (EIA-364-27) [REF-SENSOR-042]. No SSM-specific
  vibration figure is archived; treat the rail as unqualified until the stack passes the
  airframe vibration test.
- Cape H1–H4 chassis holes remain the primary load path; the rails carry no structural load.
- Socket tails are SMT (no protruding tails). Conformal-coat the rail solder fillets with the
  rest of the board, masking the socket contacts.

**Isolation band.** CAN-TR / RS485 on the top face at v 20.6 mm; J-CAN / J-485 at the bottom
edge over the P2 rail. `ISO_BAND` covers F.Cu and In1–In4, u 7.2–37.6 mm, v 18.0 mm to the edge
keep-out; In1 carries the GND2 islands, In2–In4 are kept out. **B.Cu is not part of the band:**
no isolated pad sits on the bottom face, so B.Cu beneath the band carries logic copper
(two-pad parts, 1553-XFM and the Tag-Connect land) that must route on B.Cu alone, because no
logic via may enter the band. The isolated domain is separated from that copper by the
laminate (In1 to B.Cu), not by surface creepage — functional bus isolation, not a safety
barrier. The ≥ 8 mm creepage target in the layout constraints above applies to same-surface
spacing and is still to be verified on the routed board.

## §13b — Outline 60 x 35 mm (2026-10-06)

Owner decision 2026-10-06 ("option 2, 60x35 with 1.5 mm gap"); supersedes the 55 x 35 mm
hard constraint in §1 for TACCO only (Pilot stays 55 x 35).

**Why.** At 55 x 35 the placed board was about 95 % courtyard-full, and every routing attempt
left 60–90 connections unrouted on 6 layers and about 71 on 8, so the board was limited by area,
not layer count. 60 x 35 adds 175 mm² (0.27 in²).

**Where the extra 5 mm (0.20 in) goes.** On the PB2-I microSD (pin-1/2) end: the board spans
u = −5..55 in the generator's PB2 frame (`U_LO`, `gen_tacco_pcb.py`). The rails, H1–H4 (still
on the Pilot stacking pattern) and every fixed station are unchanged. The overhang stays clear
of the PB2's USB-C / JST-SH end. Bottom-face parts wholly past the PB2-I edge (u < −1.0) are
not held to the 5.04 mm rail-gap height budget; they are capped at 8 mm by the pouch stack.
The overhang sits 5.54 mm above the PB2-I microSD slot: the card can still be inserted, but
it is a bench operation.

**Airframe fit (all four TACCO stations, re-proved 2026-10-06).**

| Station | Mount | Change | Gate |
|---|---|---|---|
| Nose, CN1 | Faraday tray (with FC1) | tray 60 → 65 mm, access panel 62 → 67 mm (`head_shell24.scad`) | bare-shell section probe: ≥ 4.9 mm (0.19 in) to the skin |
| Cargo chin, CN2 / CN3 | flat on `chin_node_shelf`, connector edges inboard | pouch 63 mm long at Y −60.3..2.7, cable channel 10 → 9 mm, **static gap 2.0 → 1.5 mm** (owner-accepted), shelf aft lip dropped | `tools/cargo_layout_fit.py` PASS (Rev T5g) |
| Middle ring, CN4 | Simon saddle, standing, under FC4 | slots 58 → 63 mm, growth to starboard, FC4 port-justified | `tools/middle_layout_fit.py` PASS (Rev T6a) |

**Open (owner).**
- Re-export the printable STLs from the updated SCAD/params: `chin_node_shelf.stl`,
  `simon_node_saddle.stl`, `void_former_cargo_node_bay.stl` and `head_shell24.stl`. Neither
  `openscad` nor `build_head_shell.py`'s `manifold3d` version was available in the
  generating session.
- The nose-tray position in `head_shell24.scad` still uses the legacy axes (known issue), so
  the nose check is against the bare shell only.

## §14 — Field Connectors Summary

All field connectors are shielded JST-GH (or SMA/U.FL for RF). SHIELD pins connect to PGND.

| Designator | Type | Pins | Signal Assignment |
|---|---|---|---|
| J_PWR | SM04B-GHS-TB-1MP | 1=+5V_IN, 2=GND, 3=GND, 4=+5V_IN, MP=PGND | Power input |
| J_CAN | SM03B-GHS-TB-1MP | 1=CAN_B_H, 2=CAN_B_L, 3=GND, MP=PGND | CAN FD bus |
| J_485 | SM03B-GHS-TB-1MP | 1=RS485_B_P, 2=RS485_B_N, 3=GND, MP=PGND | RS-485 |
| J_1553 | SM04B-GHS-TB-1MP | 1=BUS_1553_B_P, 2=BUS_1553_B_N, 3=GND, 4=PGND, MP=PGND | MIL-STD-1553C |
| J_FAN | SM03B-GHS-TB-1MP | 1=GND, 2=+5V, 3=FAN_PWM_B, MP=PGND | Bay ventilation fan |
| J_SD | MicroSD (Molex 503182-1852) | SDIO: CLK/CMD/D0-D3/CD/WP | Logging microSD |
| J_SMA_LORA | SMA (50 Ω) | RF center conductor = LORA_ANT; shell = PGND | LoRa 915 MHz antenna |
| J_SMA_WIFI | SMA (50 Ω) | RF center = WIFI_ANT; shell = PGND | WiFi 2.4/5 GHz antenna |
| J_SIK_ANT | Hirose U.FL | RF center = SIK_ANT; shell = PGND | SiK 915 MHz module pigtail |
| J_SMA_SIK | SMA (50 Ω) | RF center via FL_SIK; shell = PGND | SiK 915 MHz antenna output |

Note: J_ETH_B and J_XCVR are absent from this table — confirmed removed from the as-placed
PCB (`TACCO.kicad_pcb`) even though both still appear in the lagging schematic (`TACCO.kicad_sch`,
PCB (`TACCO.kicad_pcb`) even though both still appear in the lagging schematic (`TACCO.kicad_sch`,
see status note above and TODO.md §1.2b); this table reflects the as-built board, not the
schematic.

Note: TACCO uses `_B_` net name suffixes on CAN, RS-485, and 1553 bus signals
(CAN_B_H/CAN_B_L, RS485_B_P/RS485_B_N, BUS_1553_B_P/BUS_1553_B_N) to distinguish
them from Pilot's `_A_` nets, allowing both boards to coexist on a shared
schematic bus ring without net name conflicts.

---

## Related Files

- `TACCO.kicad_sch` — schematic
- `TACCO.kicad_pcb` — PCB layout
- `Pilot.md` — EMI-hardened flight control cape
- `AVIONICS_PB2_REDESIGN.md` — system architecture

---

## References

1. TI Application Note SLLA337A — "Isolation Boundary Layout Guidelines for ISOW Devices"
2. Analog Devices ADM2795E Data Sheet Rev. B
3. Würth Elektronik EMC Design Guide (2023) — ferrite bead placement
4. TI WL1837MOD Hardware Design Guide (SWRU491) — supply filtering guidance
5. IEC 61000-4-5:2014+AMD1:2017 — surge immunity [REF-IEC-005]
6. MIL-STD-461G:2015 — EM emissions and susceptibility requirements for aircraft [REF-MIL-002]
7. Johanson Technology 0915LP15B0100E Data Sheet — 902–928 MHz bandpass filter
8. Johanson Technology 2450BP15B050E Data Sheet — 2.4 GHz bandpass filter
9. Infineon ESD101-B1-02 Series Datasheet Rev 1.4 (2017-10-26) — RF ESD protection, 0.1 pF, TSSLP-2-4 (replaces the deprecated Semtech RCLAMP0502B)

## Usage notices

**Intended use:** the Serenity-UAV avionics, including this board, are intended
for use only on uncrewed aircraft.

**Würth Elektronik usage notice** — applies to the Würth parts on this board
(749010012A, 742792510, WE-MAPI 3015). Quoted verbatim from Würth Elektronik
eiSos, *749010012A data sheet* rev 004.000 (2024-04-11), p. 1 [REF-SENSOR-028];
the same notice appears on every Würth product data sheet. Owner decision
2026-09-26: the Würth parts are retained (avionics/WBS.md U7.1d).

> This electronic component has been designed and developed for usage in general
> electronic equipment only. This product is not authorized for use in equipment
> where a higher safety standard and reliability standard is especially required
> or where a failure of the product is reasonably expected to cause severe
> personal injury or death, unless the parties have executed an agreement
> specifically governing such use. Moreover Würth Elektronik eiSos GmbH & Co KG
> products are neither designed nor intended for use in areas such as military,
> aerospace, aviation, nuclear control, submarine, transportation,
> transportation signal, disaster prevention, medical, public information
> network etc.. Würth Elektronik eiSos GmbH & Co KG must be informed about the
> intent of such usage before the design-in stage. In addition, sufficient
> reliability evaluation checks for safety must be performed on every electronic
> component which is used in electrical circuits that require high safety and
> reliability functions or performance.

<!-- /USAGE-NOTICE-2026-09-26 -->
