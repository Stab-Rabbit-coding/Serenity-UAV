# XCVR-49MHZ-1 — Design Notes

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Status:** Phase 1 complete — ICs selected 2026-05-31; Phase 2 schematic in progress

---

## Purpose

AX.25 packet radio transceiver operating on FCC Part 95 Subpart D (Remote Control Radio
Service) channels.  Provides the 49 MHz comms link called out in the Serenity UAV
architecture.  Connects to CN nodes via CAPE-B's J1 6-pin header.

---

## Regulatory Constraints

| Parameter | Requirement | Reference |
|-----------|-------------|-----------|
| Frequency | 49.830 / 49.845 / 49.860 / 49.875 / 49.890 MHz | 47 CFR 95.623 |
| Max TX power | 100 mW ERP | 47 CFR 95.631 |
| Spurious emissions | ≥ 40 dB below carrier (below 30 MHz); ≥ 60 dB (above 1 GHz) | 47 CFR 95.655 |
| Modulation | AM/FM permitted; AFSK 1200 baud (Bell 202) chosen for AX.25 compatibility | 47 CFR 95.633 |
| Frequency stability | ±0.005% of assigned frequency | 47 CFR 95.625 |
| Type acceptance | Required before operation; FCC ID must be marked on board | 47 CFR 95.603 |

---

## Interface to CAPE-B

J1 is a 2×3, 2.54 mm pitch header (Würth 61300311121 or equivalent).

| Pin | Net | Direction | Description |
|-----|-----|-----------|-------------|
| 1 | +5V | In | 5 V supply, 200 mA max |
| 2 | GND | — | Common ground |
| 3 | UART_TX | In (host→XCVR) | AX.25 KISS framed data, 57600 baud 8N1, 3.3 V LVTTL |
| 4 | UART_RX | Out (XCVR→host) | Received KISS frames, 3.3 V LVTTL |
| 5 | PTT_N | In | Active-low push-to-talk; assert ≥ 5 ms before first bit |
| 6 | RSSI_ANA | Out | 0–3.3 V analog; 0 V = −120 dBm, 3.3 V = −20 dBm |

Protocol framing: KISS over UART (TNC2 mode).  The AX.25 stack runs on the CN node
(CAPE-B host CPU); this board is purely a physical-layer modem + transceiver.

---

## Phase 1 Design Decisions (2026-05-31)

Three blocking IC-selection items resolved.  All decisions reflected in the Committed
BOM table below.

### U1 — DDS Carrier Synthesiser: Si5351A-B-GT

**Selected:** Silicon Labs Si5351A-B-GT + 25 MHz TCXO reference (EPSON TG2520SMN ±0.5 ppm
or equivalent ±1 ppm 25 MHz SMD TCXO)

**Rationale:**

- Generates 49.830–49.890 MHz directly over I²C; no external PLL or multiplier required.
- Firmware driver `serenity/firmware/cn/src/si5351.c/.h` already written and field-tested
  (Phase 6 complete); all five Part 95 Subpart D channels are software-configurable at
  runtime via `si5351_set_rcrs_channel()`.
- ±0.5 ppm TCXO + Si5351A fractional-N PLL → effective system stability < ±1 ppm,
  meeting Part 95 ±0.005% (±2450 Hz at 49 MHz) with greater than 25× margin.
- Eliminated: AD9833BRMZ (max 12.5 MHz output; requires ×4 external PLL to reach
  49 MHz; adds BOM cost and layout complexity with no compensating benefit).

### U3 — Power Amplifier: Two-Stage Discrete BJT

**Selected:** MMBT2222A (SOT-23, NPN driver) + 2N3866 (SOT-39, NPN final stage)

**Rationale:**

- Both devices operate directly from the +5 V supply available at J1 pin 1; no boost
  converter required.
- MMBT2222A provides ≈ 15 dB gain as a Class-A driver; 2N3866 provides ≈ 10 dB gain in
  Class-AB final stage, achieving 100 mW ERP with a standard emitter-degeneration bias
  network.
- Total PA BOM cost ≈ $1.60; both devices are well-characterised at 49 MHz and held in
  volume stock at Digi-Key and Mouser.
- Harmonic suppression requirement (≥ 40 dBc per 47 CFR 95.655) is met by FL1 Chebyshev
  LPF; SPICE/QUCS-S verification required in Phase 4 before board spin.
- Eliminated: RA07H4047M RF power module (requires 7.2–13.6 V supply, necessitating a
  boost converter from the 5 V rail; center band nominally 400–470 MHz, requiring
  retuning for 49 MHz operation).

### U2 — AFSK Modem: Software Bell 202 on Cape-B MCU

**Selected:** Software implementation on AM6254 Cape-B host CPU

- **TX path:** MCP4921 SPI 12-bit DAC (SOT-23-8, 5 V, ≤ 2.86 MHz SPI) → audio into U3
  modulator input.
- **RX path:** Passive RC bandpass filter (1200 / 2200 Hz) → LM393 dual comparator
  (SOT-23-5) → digital threshold output → Cape-B GPIO / MCU UART RX.

**Rationale:**

- TCM3105NE confirmed discontinued by TI; no in-production package-compatible drop-in is
  available in prototype quantities (MC14412 is PDIP-only; Onsemi MC145443 is minimum-50
  MOQ; neither is footprint-compatible).
- Software Bell 202 AFSK executes on one AM6254 MCU core (≈ 200 lines C); fits cleanly
  alongside existing `serenity/firmware/cn/src/xcvr_kiss.c` Phase 6 KISS framer.
- MCP4921 (≈ $1.20) replaces a discontinued $4+ modem IC and eliminates sourcing risk
  for all future board spins.
- LM393 comparator + passive RC bandpass performs hardware-threshold RX demodulation
  without DSP overhead on the real-time control path.

---

## Committed Subsystem BOM

Phase 1 IC selections committed 2026-05-31.  Remaining entries (U4–U6, FL1, J1–J2)
confirmed for Phase 2 schematic.

| Ref  | Function               | Selected Part                   | Package    | Notes |
|------|------------------------|---------------------------------|------------|-------|
| U1   | DDS carrier synthesiser | Si5351A-B-GT (Silicon Labs)    | MSOP-10    | I²C 400 kHz; 3.3 V; 8 mA drive; firmware driver written |
| X1   | TCXO reference          | EPSON TG2520SMN 25 MHz ±0.5 ppm | SMD-2520  | Si5351A reference; < ±1 ppm system stability |
| U2a  | AFSK modem TX DAC       | MCP4921 (Microchip)             | SOT-23-8   | SPI 12-bit DAC; 5 V; Bell 202 1200/2200 Hz audio to U3 |
| U2b  | AFSK modem RX demod     | LM393 (dual comparator)         | SOT-23-5   | Passive RC bandpass input; hardware threshold; CD to Cape-B GPIO |
| U3a  | PA driver stage         | MMBT2222A (NPN BJT)             | SOT-23     | Class-A; ≈ 15 dB gain at 49 MHz; +5 V supply |
| U3b  | PA final stage          | 2N3866 (NPN BJT)                | SOT-39     | Class-AB; ≈ 10 dB gain; 100 mW ERP; collector tab to GND pour |
| U4   | LNA                     | MGA-82563 (Broadcom)            | SOT-363    | 50–6000 MHz; 2.4 dB NF; suitable for 49 MHz RX |
| U5   | TX/RX switch            | PE4259-63 (pSemi SPDT)          | SC-70-6    | −40 to +85 °C; 50 Ω; 100 mW TX path; ≥ 35 dB TX→RX isolation |
| FL1  | 5-element Chebyshev LPF | Discrete L/C (Coilcraft SER + C0G caps) | — | fc = 75 MHz; ≥ 40 dBc at 98 MHz; shielded ferrite cans |
| J1   | Host interface          | Würth 61300311121 (2×3, 2.54 mm) | THT       | Mated to CAPE-B J1 counter-connector |
| J2   | Antenna SMA             | Amphenol 132289                 | Edge-mount | 50 Ω edge-mount SMA |
| U6   | 3.3 V LDO               | AMS1117-3.3                     | SOT-223    | Supplies MCP4921, LM393, and UART level shifter |

---

## PCB Layout Constraints

- **Board size:** 55 × 35 mm — matches Cape-A/B footprint (potential stacking)
- **Layer stack:** 4L — F.Cu signal | In1.Cu GND plane | In2.Cu power | B.Cu signal
- **RF section** (right 25 mm of board): unbroken ground plane on In1.Cu;
  no copper pours on F.Cu or B.Cu within RF section; guard-ring vias every 5 mm
- **50 Ω microstrip** on F.Cu: 2.75 mm trace width on 1.6 mm FR4 (εr = 4.5, h = 0.36 mm to In1.Cu)
- **Digital section** (left 30 mm): UART traces ≥ 5 mm from RF traces; ferrite bead on +5V at section boundary
- **LPF inductors:** must be shielded (ferrite can, e.g., Coilcraft SER series) and oriented perpendicular to each other to minimise mutual coupling
- **SMA J2:** flush to right board edge; 3 mm copper keep-out on both sides of feed line from edge to U5 switch
- **J1 header:** on left board edge, 2.54 mm pitch, 3 mm from corner
- **Thermal:** U3b (2N3866, SOT-39) — collector tab must contact a 15×15 mm Cu pour on F.Cu tied to In1.Cu GND via ≥ 9× 0.3 mm thermal vias; verify < 85 °C case temperature at 100 mW continuous TX

---

## Security Requirements

Per project architecture, all messages on this link must be digitally signed.
Authentication is handled in the AX.25 payload layer by the CN node firmware (CAPE-B
host).  This board carries no TPM; it is a dumb modem — the CN node owns all
cryptographic operations before bytes reach the KISS framer.

---

## Related Files

- `CAPE-B-1.kicad_sch` — host board; J1 counter-connector is on CAPE-B
- `serenity/docs/REVN_BUILD_GUIDE_24IN.md` — Phase 7 avionics installation
- `TODO.md` — full development task list for this board
