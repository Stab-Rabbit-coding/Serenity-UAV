# Wash (CAPE-A-2) — Footprint-vs-Datasheet Verification

**Author:** Claude (Opus 4.8), 2026-07-13
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Board:** `avionics/kicad/Wash/kicads/Wash.kicad_pcb`
**Method:** Every placed footprint's pad geometry (count, pitch, body, EP) was
extracted from the PCB and compared against the manufacturer datasheet in
`avionics/datasheets/`. Datasheets were text-extracted with `pdftotext`.

> *"It's just reputation" — so every land pattern here is checked against the
> silicon it must actually solder to, not a placeholder.*

---

## Summary verdict

**7 of 46 footprints are NOT manufacturable as drawn** (5 wrong land patterns +
2 placeholders). The board **cannot be fabricated** until these are rebuilt. A
further group is package-correct but needs a pinout/part-number confirmation.

| Verdict | Count | Refs |
| --- | ---: | --- |
| ❌ Wrong land pattern | 5 | CAN-TR, TPM, ETH1-PHY, ETH2-PHY, RS485, BARO |
| ❌ Placeholder (2-pad stub) | 2 | GPS, 1553-XFM |
| ❗ Land OK but net map broken | 2 | U-ISO-RX, U-ISO-TX (ISO6442) |
| ⚠ Land OK, needs part number | 3 | T-ETH/T-ETH2, X2Y-CAN/RS485, PWR-IN |
| ✅ Verified correct | rest | incl. all JST GH connectors — see tables |

Note: BARO plus the two ETH-PHYs make the "wrong" list 6 refs across 5 part types.

---

## ❌ Confirmed wrong land patterns

| Ref | Part | PCB footprint (WRONG) | Datasheet says | Source |
| --- | --- | --- | --- | --- |
| **CAN-TR** | ISOW1044BDFMR | `SOIC-16W_7.5x10.3mm` — **16 pads** | **20-pin DFM** (SOIC-20 land) — "DFM (20)", "20 PINS", Fig 7-1 | `isow1044.pdf` §7 |
| **TPM** | SLB9670 | `QFN-32-1EP_4x4mm_**P0.4mm**_EP2.65` | **VQFN-32, 0.5 mm pitch**, ~5×5 body, **EP 3.6×3.6** | `SLB_9670VQ20_Infineon.pdf` p.15 ("7 × 0.5 = 3.5"; "3.6 ±0.1") |
| **ETH1-PHY / ETH2-PHY** | ADIN1300BCPZ | `QFN-48-1EP_**7x7mm**` — **48 lead** | **40-lead LFCSP, 6×6 mm** (CP-40-26), 0.5 mm pitch, w/ EP | `adin1300.pdf` ("40-lead, 6 mm × 6 mm LFCSP") |
| **RS485** | ADM2795EBRWZ | `SOIC-**20W**_7.5x12.8mm` — **20 pads** | **16-lead SOIC_W (RW-16)** | `adm2795e.pdf` Table 3/4/7 ("16-Lead … RW-16") |
| **BARO** | BMP388 | `Bosch_LGA-**8**_2x**2.5**mm_P0.65` — **8 pads** | **10-pin metal-lid LGA, 2.0 × 2.0 mm** | `bst-bmp388-ds001.pdf` ("10-pin … 2.0 × 2.0 mm") |

Each of these is a hard fabrication defect: wrong pad count and/or wrong pitch
means the pads do not land on the part's leads. **Correcting them remaps
which net lands on which pin** — a flight-hardware footprint↔symbol change that
must be done against the confirmed schematic pinout, not guessed (root
`CLAUDE.md`, avionics `CLAUDE.md`).

## ❌ Placeholder footprints (2-pad stubs, not real)

| Ref | Part | Footprint | Real package (datasheet) |
| --- | --- | --- | --- |
| **GPS** | SAM-M10Q-00B | `Package` — 1 dummy + 8×8 mm body blob | u-blox SAM-M10Q, LGA patch-antenna module (~15.5×15.5 mm, ~20+ LGA pads; `SAM-M10Q_DataSheet_UBX-22013293.pdf` §3.1) |
| **1553-XFM** | SM-1553-11 | `Package` — 1 dummy + 4.8×3.36 mm body blob | Beta/SM1553-series data-bus pulse transformer — **thru-hole**, multi-pin (`SM1553-Series...RevD.pdf`) |

Both need real footprints authored from the datasheet pinouts before layout.
Note the SM1553 series is **through-hole**, which changes the PCB (THT pads +
drills) versus the current SMD stub.

---

## ❗ ISO isolators — land pattern OK, but net mapping is non-functional

**U-ISO-RX / U-ISO-TX (ISO7642FDWRR → ISO6442, per TI EOL/replacement guidance):**

- **Land pattern `SOIC-16W` is CORRECT** for the Wide-SOIC **DW-16** package
  (`iso6442.pdf` — "Wide-SOIC (DW-16)"). ✅
- **The ISO7642 → ISO6442 substitution is a valid drop-in:** both are 4-channel,
  **2-forward / 2-reverse**, DW-16, pin-compatible. ✅ (BOM string / `Wash.md` /
  `REFERENCES.md` should be updated ISO7642FDWRR → ISO6442; fold into the rework below.)
- **BUT the placed net→pin assignment does not work** (checked against ISO6442
  Table 5-1). Two hard errors:
  1. **Power/ground pins carry signal nets** — e.g. pin 2 (`GND1`) = `RMII0_RXD0`,
     pin 15 (`GND2`) = `RMII0_RXD0`, pin 2 of U-ISO-TX (`GND1`) = `RMII0_REF_CLK`.
     The device cannot power up or function like this.
  2. **Every channel is shorted across the isolation barrier** — the *same* net
     sits on the side-1 input pin and the side-2 output pin of each channel
     (RMII0_RXD1 on pins 3 & 14, CRS_DV on 4 & 13, etc.). That defeats the
     galvanic isolation entirely; there are no separate primary/secondary nets.
  3. **Architecture concern:** RMII `REF_CLK` is 50 MHz and is routed through a
     general-purpose digital isolator; continuous-clock isolation at that rate is
     marginal-to-unworkable and adds skew that breaks RMII timing. The whole
     "isolate RMII with two 4-channel digital isolators" scheme needs design review.

  This is a **schematic/net-correctness defect, not a land-pattern defect** — but
  it means the ETH-isolation subcircuit as drawn is non-functional and must be
  re-architected + re-netted, not merely routed. Depends on a clean ERC (§1.2a).

## ❗ Net→pin maps are wrong on multiple parts (schematic-rooted, not geometry)

Verifying pinouts surfaced that the **net-to-pin assignments are wrong**, independent
of the land-pattern errors. Confirmed on two parts so far:

- **TPM (SLB9670)** vs. datasheet Fig 1 (PG-VQFN-32-13): TPM_RSTN on pin 1 (=NCI/VDD;
  RST# is pin 17), SPI0_MISO on pin 22 (=VDD; MISO is 24), SPI0_CLK on pin 23 (=GND;
  SCLK is 19), TPM_IRQN on pin 24 (=MISO; PIRQ# is 18), SPI0_CS_TPM on pin 28 (=NC;
  CS# is 20). Only SPI0_MOSI (pin 21) is right. Correct map: 17→TPM_RSTN, 18→TPM_IRQN,
  19→SPI0_CLK, 20→SPI0_CS_TPM, 21→SPI0_MOSI, 22→+3V3, 23→GND, 24→SPI0_MISO, EP→GND.
- **U-ISO-RX / U-ISO-TX (ISO6442)** — signals on power/ground pins, every channel
  shorted across the barrier (documented above).

These are **schematic/netlist errors**, not land-pattern errors: the wrong pin→net
associations originate in the symbols that drive the netlist. **Fixing only the PCB
footprints would fight the schematic on the next sync and re-create the exact
sch↔pcb divergence documented for Emma/Zoë.** The rebuild must therefore be
**schematic-first** (author correct symbols/pinouts → correct footprints follow →
re-sync PCB), or explicitly accept a PCB-first patch with the schematic to catch up.

## ⚠ Package correct, but needs a part number

| Ref(s) | Part | Note |
| --- | --- | --- |
| T-ETH, T-ETH2 | Würth 749010012A | Custom 8-pad `ETH_XFMR_8P_5x3.5mm`. Part confirmed (WE-LAN 10/100 SMT). Verify the 8-pad pinout/pin-1 orientation against `749010012A.pdf`. |
| X2Y-CAN, X2Y-RS485 | 4.7 nF X2Y | Custom `X2Y_Cap_4T_0402`. **No manufacturer part number / datasheet supplied** — cannot verify the 4-terminal land. Need the actual X2Y device (e.g. Johanson) part number. |
| PWR-IN | Molex Nano-Fit 4P | Pitch consistent (2.5 mm), but no Nano-Fit datasheet supplied to confirm pad/keying. |

## ✅ Connectors verified correct against `eGH.pdf`

JST **GH** series confirmed: 1.25 mm pitch, SM03B/SM04B/SM05B/SM06B-GHS-TB all
listed in `eGH.pdf`. The custom `JST_GH_4P` / `JST_GH_3P` lands (1.25 mm pitch)
and the standard `JST_GH_SM05B-GHS-TB…Horizontal` (ESC-PWM) all match — CAN-FD,
RS-485, ETH1, ETH2, MIL-1553, ESC-TLM, GPIO-A…F connectors verified. (The earlier
`SM04B-SRSS-TB.pdf` was the wrong series and is superseded by `eGH.pdf`.)

---

## ✅ Verified correct against datasheet

| Ref(s) | Part | Footprint | Datasheet confirms |
| --- | --- | --- | --- |
| 1553-DRV | DS26LV31 | `SOIC-16_3.9x9.9mm` | `ds26lv31qml.pdf` — SOIC (D), 16 |
| 1553-RCV | DS26LV32 | `SOIC-16_3.9x9.9mm` | `ds26lv32at.pdf` — "SOIC (D) 16" |
| IMU | ICM-42688-P | `LGA-14_3x2.5mm_P0.5mm` | `ds-000347...pdf` — "2.5×3.0×0.91 mm 14-pin LGA" |
| U-GPIO | PCA9555DB | `SSOP-24_5.3x8.2mm_P0.65mm` | `PCA9555.pdf` — SSOP24 (DB) |
| TVS-1553 | SMAJ33CA | `DO-214AC_SMA` | standard SMA — matches |
| TVS-CAN, TVS-RS485 | PRTR5V0U2X | `SOT-363_SC-88` | standard 6-pin SOT-363 — matches |
| CMC-CAN, CMC-RS485 | SRF2012-100Y | `Bourns_SRF2012_4T` | `SRF2012A.pdf` — 2012 4-terminal CMC |
| FB1 | 742792512 | `C_0805_2012Metric` | 0805 2-terminal ferrite — acceptable |
| C-GPIO | 100 nF | `C_0805_2012Metric` | standard 0805 |
| SERVO-PWM | 1×8 header | `Connector_PinHeader_2.54mm` | standard 2.54 mm header |
| PB2-P1, PB2-P2 | PB2-I P1/P2 | `2x18_*_Socket` | 2.54 mm 2×18 — matches PocketBeagle 2 header |

---

## ❗❗ Schematic and PCB are two different designs (root cause)

Confirmed 2026-07-13 by inspecting `Wash.kicad_sch` lib_symbols/instances:

- **The schematic is a DP83825I design; the PCB is an ADIN1300 design.** The
  schematic instantiates `DP83825I` ×2 + `HX1188NL` ×2 + `TPS62933` ×2 (matching
  `Wash.md`). The PCB instead has `ADIN1300` ×2 + `749010012A` + ISO isolators and
  **no** DP83825I/HX1188NL/TPS62933. The Ethernet front-end was reworked on the PCB
  and never captured in the schematic. So the ADIN1300 "wrong footprint" finding is
  only meaningful if ADIN1300 is the intended architecture.
- **The schematic symbols are partial/wrong-pinout, not datasheet-accurate:**
  ISOW1044BDFMR symbol = **9 pins** (real = 20), ADM2795EBRWZ = **10** (real = 16),
  SLB9670 = **8** (real = 32), SAM-M10Q = **7** (real = 16+), BMP388 = **7** (real =
  10). They draw only the pins the designer chose to wire, and (per the TPM/ISO
  checks above) some of those are on the wrong physical pins.
- The schematic also carries parts not stuffed on the PCB (MMC5983MA + QMC5883L
  compasses, INA219/INA226 monitors) — further evidence the two files are different
  board revisions.

**Neither file is currently a clean source of truth.** A proper schematic-first
rebuild must (1) pick the Ethernet architecture (DP83825I vs ADIN1300), (2) author
datasheet-accurate full-pinout symbols for each IC, (3) wire them correctly,
(4) associate correct footprints, (5) regenerate/re-sync the PCB, (6) ERC/DRC clean.

## Cross-cutting: documentation vs. as-built architecture

The supplied datasheets (ADIN1300, ADM2795E, ISO-series, Würth 749010012A)
confirm the **PCB's** Ethernet front-end is authoritative and **`Wash.md` §1 is
stale**. `Wash.md` still documents a DP83825I + HX1188NL + TPS62933 design that
is not on the board. `Wash.md` §§1–3 need to be rewritten to the as-built
ADIN1300 + 749010012A + ISO6442 + ADM2795E (RW-16) design, and the §3 claim that
the ADM2795E is "SOIC-20W" with an "internal DC/DC" must be reconciled with the
16-lead RW-16 datasheet.

## Recommended fix order

1. Resolve the ⚠ part-number/datasheet gaps (ISO7642 vs ISO6442; X2Y P/N; JST
   GH drawing; Molex Nano-Fit) so every land pattern maps to a confirmed part.
2. Confirm the schematic pinout for each ❌ part (the schematic ERC is not clean;
   see §1.2a), then rebuild the 5 wrong land patterns with correct pin→net mapping.
3. Author real footprints for GPS (SAM-M10Q LGA) and 1553-XFM (SM1553 THT).
4. Re-run `kicad-cli pcb drc --schematic-parity` and proceed to routing.
