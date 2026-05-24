# XCVR-49MHZ-1 — Design Notes

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Status:** STUB — schematic and layout not yet populated

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

## Proposed Subsystem BOM (candidates — not yet committed)

| Ref | Function | Candidate Part | Notes |
|-----|----------|----------------|-------|
| U1 | DDS carrier synthesiser | AD9833BRMZ (Analog Devices) | SPI, 0–12.5 MHz output — requires ×4 PLL or external multiplier to reach 49 MHz; *or* Si5351A-B-GT (I²C, any freq to 200 MHz, simpler) |
| U2 | AFSK modem | TCM3105NE (TI, SOIC-8) | Bell 202 1200/2200 Hz; UART interface; 5 V supply |
| U3 | PA | RA08H4047M (Mitsubishi) | 400–470 MHz module, *out of band* — evaluate RA07H4047M for 30–512 MHz range; or discrete 2N3866 BJT |
| U4 | LNA | MGA-82563 (Broadcom) | 50–6000 MHz, 2.4 dB NF, suitable for 49 MHz RX |
| U5 | TX/RX switch | PE4259-63 (pSemi SPDT) | −40 to +85 °C, 50 Ω, 100 mW TX path |
| FL1 | 5-element LPF | Discrete L/C | fc = 75 MHz Chebyshev; suppresses 2nd harmonic at 98 MHz by ≥ 40 dBc per Part 95 |
| J2 | Antenna SMA | Amphenol 132289 | Edge-mount SMA, 50 Ω |
| U6 | 3.3 V LDO | AMS1117-3.3 (SOT-223) | Supplies U2 modem and UART level shifter |

**Open design question:** The Si5351A is the simpler DDS option (I²C to CAPE-B, any
frequency in one hop, 8 mA drive).  The AD9833 requires a ×4 external PLL to hit
49 MHz cleanly from its 12.5 MHz max output.  Recommend Si5351A unless spectral
purity analysis shows it fails Part 95 stability requirements.

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
- **Thermal:** U3 PA requires exposed pad to In1.Cu via thermal vias; verify <85 °C case at 100 mW continuous TX

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
