# CAPE-B-2 — EMI-Hardened Communications, Logging & Payload Cape

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** A (EMI-hardened variant of CAPE-B-1 Rev M)
**Date:** 2026-06-02
**Status:** Schematic complete — PCB layout pending

---

## Purpose

CAPE-B-2 is the electromagnetic-environment-hardened variant of CAPE-B-1 (Rev M),
designed for the same harsh nacelle and fuselage EM environment as CAPE-A-2. The
communications payload of this cape (SiK 915 MHz, LoRa 915 MHz, WiFi 2.4/5 GHz,
49 MHz RCRS) is inherently more susceptible to radiated interference than the purely
digital CAPE-A-2, so hardening concentrates on conducted immunity for the wired
buses and supply rails, and on keeping the RF subsystem's susceptibility low through
better supply filtering and digital-interface isolation from the RF groundplane.

---

## Changes from CAPE-B-1 (Rev M)

### 1. Ethernet PHY removal (space recovery)

Identical rationale to CAPE-A-2: both DP83825I PHYs, their magnetics, and the two
ETH-P/ETH-N JST-GH connectors are removed. The 22 P2 expansion-header pins formerly
allocated to RMII0/1, MDC, MDIO, and PHY control signals become no-connect.

The freed board area (approximately 20 × 12 mm) accommodates the new EMI filter components
without any overall board size increase from the CAPE-B-1 90 × 60 mm footprint.

### 2. CAN FD transceiver: ATA6561 → ISOW1044BDFMR

Identical substitution to CAPE-A-2. See CAPE-A-2.md §2 for full rationale.
The isolated transceiver (ISOW1044BDFMR, SOIC-16, DigiKey 296-ISOW1044BDFMRCT-ND)
provides 5 kV reinforced isolation, ±42 V bus fault tolerance, and an integrated DC/DC
converter that generates the isolated bus-side supply from the 3.3 V logic rail.

### 3. RS-485 transceiver: MAX3485E → ADM2795EBRWZ

Identical substitution to CAPE-A-2. See CAPE-A-2.md §3. Half-duplex direction-control
via RS485_DE (tied to both DE and RE_N) is preserved.

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
| TVS-RCRS | RCRS-49 J1 header | PRTR5V0U2X | 5.5 V — on UART_TX/RX and PTT_N |

The RCRS-49 6-pin JST-GH header J1 adds TVS protection because the 49 MHz sub-module
cable run may be several cm long inside the bay, acting as a short antenna for
RF ingress into the UART lines.

### 6. SiK 915 MHz module supply and signal filtering

The SiK module (RFD900x form-factor UART-connected radio) has its power and control
lines treated as follows:

- **Supply:** A 10 µF + 100 nF MLCC decoupling pair placed ≤ 1 mm from the module

  VCC pin, in addition to the existing 100 µF + 100 nF bulk cap array (U16 in CAPE-B-1).

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

### 9. RCRS-49 sub-module header (J1) EMI filter

The J1 6-pin JST-GH header connecting to the XCVR-49MHZ-2 sub-module has the following
protection:

- TVS-RCRS (PRTR5V0U2X): protects UART_RCRS_TX, UART_RCRS_RX, and PTT_N lines
- Ferrite beads (FB-RCRS, Würth 742792510) in series with the UART lines before J1:

  prevents 49 MHz RF energy from entering the SoC UART interface via the cable stub

- RSSI_ANA line: 1 nF C0G cap to ground for HF noise filtering (not ferrite bead, to

  avoid distortion of the DC–3 kHz RSSI analog signal)

- 5V power pin: 10 µF + 100 nF local decoupling at J1

### 10. Power entry filter

Identical to CAPE-A-2: π-filter (C11 = 47 µF, FB1 = Würth 742792512, C12 = 10 µF +
100 nF) on the +5V supply at J-PWR. See CAPE-A-2.md §6.

### 11. Chassis ground (PGND) implementation

Same single-point chassis ground topology as CAPE-A-2. PGND additional connections
specific to CAPE-B-2:

- SMA connector shields for all antenna ports (SMA-915-SIK, SMA-915-LORA, SMA-WIFI,

  SMA-49) — all connected to PGND, not GND, to keep RF return currents off the
  signal ground plane.

- Mounting holes × 4: PGND via 0 Ω solder-selectable links.
- PGND-to-GND star point: single 0 Ω / 10 Ω link at J-PWR under the bay mounting boss.

### 12. RF supply decoupling (upgraded from CAPE-B-1)

CAPE-B-1 had 100 µF + 100 nF per radio VCC (U16 ferrite + bulk cap array). CAPE-B-2
upgrades to:

| Radio | Input supply filter | VCC bypass |
| --- | --- | --- |
| SiK RFD900x | 10 µH inductance + 47 µF (before module VCC) | 100 nF + 10 nF at module pin |
| RFM95W | 100 Ω ferrite + 10 µF + 100 nF | 100 nF + 10 nF at module pin |
| WL1837MOD | TPS63031 output + 1 µH + 47 µF (CAPE-B-2 added) | 10 µF + 100 nF at module pin |
| RCRS-49 J1 | 10 µF + 100 nF at J1 pin | (on XCVR-49MHZ-2 board) |

---

## PCB Layout Constraints (additions to CAPE-B-1 rules)

The CAPE-A-2 layout constraints apply equally here. Additional CAPE-B-2 specifics:

- **RF groundplane moat:** The RFD900x and RFM95W occupy the same RF section as in

  CAPE-B-1 (right 30 mm of board). The isolation moat between the RF groundplane and
  the digital groundplane must be maintained; the moat capacitors (10 nF X2Y) bridge
  the moat at RF frequencies, referenced to PGND on the RF side and GND on the digital
  side.

- **SMA shield contacts:** All four SMA connectors must have their shells soldered to

  a PGND copper pour, NOT to the digital GND pour. Route a 3 mm PGND pour around each
  SMA mounting footprint.

- **Ferrite bead orientation:** SDIO and SPI ferrite beads must be oriented with their

  axis perpendicular to the associated RF trace runs (per Würth EMC design guide).

- **RCRS-49 header J1:** Place within 5 mm of the board edge so the cable run to the

  XCVR-49MHZ-2 module is minimised. Apply a PGND guard pour around J1.

---

## 13. Antenna Port Filter Chains (Rev A addition)

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
      +----[D_ANT_xxx  RCLAMP0502B]---- PGND   ← shunt ESD clamp
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

**RF ESD protection:**

| Reference | Part | Capacitance | Clamp voltage | Package |
|---|---|---|---|---|
| D_ANT_LORA | Semtech RCLAMP0502BTCL | 0.15 pF max | 5.5 V | SOD-882 |
| D_ANT_WIFI | Semtech RCLAMP0502BTCL | 0.15 pF max | 5.5 V | SOD-882 |
| D_ANT_SIK  | Semtech RCLAMP0502BTCL | 0.15 pF max | 5.5 V | SOD-882 |

The RCLAMP0502B is specified for RF antenna protection applications; its 0.15 pF
maximum capacitance causes negligible antenna detuning at 915 MHz (< 1° phase shift
at 50 Ω) and at 2.4 GHz (< 2° phase shift). The existing digital-line PRTR5V0U2X
TVS (capacitance ≈ 5 pF per channel) is not suitable for RF antenna ports.

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
- **RCLAMP placement:** Place D_ANT_xxx immediately after the BPF (between BPF output
  and SMA pin 1). The shunt path to PGND must be as short as possible (via directly
  to PGND plane, no daisy-chain routing).
- **Keep the RF trace in the BPF-to-SMA segment entirely within the RF groundplane
  moat region** (right 30 mm of board). Do not route it over the digital GND pour.
- **SMA pad PGND pour:** Each SMA footprint shell must have a ≥ 3 mm PGND copper pour
  ring as specified in §11.

---

## Eliminated vs. CAPE-B-1 Bill of Materials (delta)

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
| RS485-ISO | ADM2795EBRWZ | Isolated RS-485 (5 kV, ±42 V) |
| CM1 | Bourns SRF2012-100Y | CAN CMC |
| CM2 | Bourns SRF2012-100Y | RS-485 CMC |
| CM3 | Bourns SRF2012-100Y | LoRa SPI CMC |
| TVS-CAN | PRTR5V0U2X | CAN connector TVS |
| TVS-485 | PRTR5V0U2X | RS-485 connector TVS |
| TVS-1553 | SMAJ33CA × 2 | 1553 connector TVS |
| TVS-RCRS | PRTR5V0U2X | RCRS-49 header TVS |
| FB1 | Würth 742792512 | 5V power entry bead |
| FB-SIK × 4 | Würth 742792510 | SiK UART + CTS/RTS beads |
| FB-RCRS × 3 | Würth 742792510 | RCRS UART + PTT beads |
| FB-SDIO × 6 | Würth 742792510 | SDIO bus beads |
| L1 | 1 µH / 1 A | WiFi supply added inductor |
| C11–C15 | Various MLCC | Power filter capacitors |
| C13, C14 | 4.7 nF X2Y | Isolation boundary CM caps |
| FL_LORA | Johanson 0915LP15B0100E | LoRa ANT bandpass filter |
| FL_SIK | Johanson 0915LP15B0100E | SiK ANT bandpass filter |
| FL_WIFI | Johanson 2450BP15B050E | WiFi/BT ANT bandpass filter |
| D_ANT_LORA | Semtech RCLAMP0502BTCL | LoRa ANT ESD shunt (0.15 pF) |
| D_ANT_SIK | Semtech RCLAMP0502BTCL | SiK ANT ESD shunt (0.15 pF) |
| D_ANT_WIFI | Semtech RCLAMP0502BTCL | WiFi/BT ANT ESD shunt (0.15 pF) |
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
| +3V3 logic (LDO) | MAX3485E→ADM2795, ATA6561→ISOW1044B, DS26LV31/32, HX711, SLB9670, ATF16V8BQL | 350 mA |

DP83825I removal saves approximately 100 mA from the 3.3V logic rail, leaving additional
headroom absorbed by the new isolated transceivers (~80 mA combined increase).

---

## EMC Compliance Targets

Same as CAPE-A-2: IEC 61000-4-2 Level 4, IEC 61000-4-4 Level 4, IEC 61000-4-5 Level 3,
MIL-STD-461G RE102 Limit C, RS103 200 V/m.

Additional RF susceptibility note: the RFD900x and RFM95W modules have their own
internal LNA protectors. The PRTR5V0U2X TVS arrays on J1 protect the UART interface,
not the antenna port. Antenna port protection is now provided by the RCLAMP0502B ESD
shunts (D_ANT_LORA, D_ANT_WIFI, D_ANT_SIK) and by the BPF series filters (FL_LORA,
FL_WIFI, FL_SIK) as documented in §13. The SMA connector shell PGND connection and
antenna cable shielding provide the primary conducted shield path.

---

## Shielded JST-GH Connectors

All JST-GH connectors on Cape-B-2 now include a SHIELD pin (number "MP") bonded to the
PGND chassis ground net through the PCB mounting tab footprint.

| Reference | Type | Signals | SHIELD tap (absolute, mm) |
|---|---|---|---|
| J_XCVR | SM06B-GHS-TB-1MP | GND / +5V / UART_RCRS_TX / XCVR_RX_RAW / XCVR_PTT_N / +3V3 | (100.00, 570.16) |
| J_FAN | SM03B-GHS-TB-1MP | GND / +5V / FAN_PWM_B | (100.00, 646.35) |

**Cable assembly requirements for all JST-GH connectors (same as Cape-A-2):**

- Cable: foil + braid shielded (Belden 9533 or equivalent)
- Drain wire: terminate to connector PGND pad
- Ferrite clamp: Würth 74271222 ≤ 25 mm from body, both ends

**RF antenna cables (SMA ports J_SMA_SIK, J_SMA_LORA, J_UFL_WIFI):**

- RG-178 or RG-316 50 Ω coaxial cable, maximum 500 mm length
- SMA/UFL connector shells bonded to PGND at the board-side connector land
- No ferrite clamp on antenna cables (coaxial inherently shielded)

---

## Bay Fan Connector (J_FAN)

A 3-pin JST-GH connector J_FAN is provided for the bay Faraday enclosure ventilation fan.

| Pin | Net | Description |
|---|---|---|
| 1 | GND | Fan return |
| 2 | +5V | Fan power (80 mA max) |
| 3 | FAN_PWM_B | PWM speed control — PocketBeagle 2 EHRPWM output |
| MP | PGND | Cable shield drain |

**Fan:** Sunon MF40100V2-1000U-A99 (40 × 40 × 10 mm, 5 V, 90 mA, 4450 RPM, brushless).

**Note:** Cape-A-2 and Cape-B-2 each have an independent J_FAN connector within the
same avionics bay.  Both fan signals (FAN_PWM_A, FAN_PWM_B) may drive the same fan
or two fans (one per board), at the integrator's discretion.  For redundancy, wiring
both boards to the same fan via a Schottky OR diode circuit (BAT54S) is preferred.

---

## Wiring Harness Requirements — All Bay Cables

See CAPE-A-2.md §11 for the full wiring harness specification.  Cape-B-2 additionally
requires:

- **SiK/LoRa/WiFi RF cables:** RG-316 coaxial, max 500 mm, SMA bodies to PGND.
- **XCVR-49MHZ-2 harness (J_XCVR):** 6-conductor overall-shielded twisted-bundle,
  Belden 9533 or equivalent.  Ferrite clamp on both ends ≤ 25 mm from body.
- **RCRS receive audio output:** shielded coaxial or individually shielded 2-wire
  to the logging subsystem; drain to PGND.

---

## Avionics Bay Faraday Enclosure

Each of the 4 avionics bays contains one Cape-A-2 and one Cape-B-2.  The complete
Faraday enclosure specification (foil liner, fan, EMI gaskets, cable entry) is
defined in Cape-A-2.md §12.  Cape-B-2 specific requirements:

- The XCVR-49MHZ-2 sub-module (plugged into J_XCVR) must be located inside the
  Faraday enclosure.  Its SMA antenna port exits through a bulkhead SMA
  panel-mount connector bonded to PGND at the bay wall.
- WiFi, SiK, and LoRa antenna coaxial pigtails must exit through a coaxial
  bulkhead panel-mount at the bay wall, bonded to PGND.
- No antenna cable shall pass through the copper foil liner without a proper
  coaxial bulkhead connector.  Avoid pigtails longer than 100 mm inside the bay.

---

## Related Files

- `CAPE-B-1.kicad_sch` — standard (non-EMI-hardened) variant, Rev M baseline
- `XCVR-49MHZ-2.kicad_sch` — EMI-hardened 49 MHz transceiver
- `CAPE-A-2.md` — EMI-hardened flight control cape (Faraday enclosure spec §12)
- `AVIONICS_PB2_REDESIGN.md` — system architecture

---

## References

1. TI Application Note SLLA337A — "Isolation Boundary Layout Guidelines for ISOW Devices"
2. Analog Devices ADM2795E Data Sheet Rev. B
3. Würth Elektronik EMC Design Guide (2023) — ferrite bead placement
4. TI WL1837MOD Hardware Design Guide (SWRU491) — supply filtering guidance
5. IEC 61000-4-5:2017 — surge immunity
6. MIL-STD-461G:2015
7. Johanson Technology 0915LP15B0100E Data Sheet — 902–928 MHz bandpass filter
8. Johanson Technology 2450BP15B050E Data Sheet — 2.4 GHz bandpass filter
9. Semtech RCLAMP0502B Data Sheet — RF ESD protection, 0.15 pF, SOD-882
