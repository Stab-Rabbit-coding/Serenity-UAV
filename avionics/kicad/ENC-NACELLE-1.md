# ENC-NACELLE-1 — Nacelle Tilt Angle Encoder Board

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Q (initial design, 2026-06-06)
**Status:** Schematic complete — PCB layout pending

---

## Purpose

ENC-NACELLE-1 is a miniature magnetic rotary encoder board that measures the tilt
angle of each nacelle in the Serenity UAV.  One board is installed per nacelle
(port and starboard) at the outboard end of the wing spar where the nacelle pivot
bearing is located.

The board reports 12-bit absolute angle data to the flight control Wash node
via a shielded I²C cable (ENC_SDA / ENC_SCL), allowing the PID controller to close
the tilt servo loop with continuous angle feedback.

---

## Design Rationale

### Sensor Technology Selection

Optical encoders were considered and rejected because the nacelle pivot is located in
the EDF exhaust stream where carbon fibre dust, moisture, and potential debris
contamination make optical sensing unreliable.

The AMS AS5600 12-bit magnetic rotary position sensor was selected:

- **No contact, no contamination path** — reads a diametrically magnetised diametric
  magnet through a gap of 0.5 – 3 mm; sealed from the environment.
- **Adequate resolution** — 12-bit = 4096 counts/revolution, 0.088°/LSB; the nacelle
  tilt servo requires ≤ 0.1° angular resolution for stable PID hover.
- **Sufficient RF immunity** — at 500 W/m² (E = 434 V/m), the associated magnetic
  field H = 1.15 A/m ≈ 1.45 µT.  The encoder reads a 50–100 mT permanent magnet;
  the external threat field is < 0.003 % of the sensor signal — completely negligible.
- **Simple I²C interface** — single fixed address (0x36), standard mode 100 kHz,
  compatible with PocketBeagle 2 I2C3 peripheral.
- **Small size** — SOIC-8 package, fits a 15 × 15 mm PCB.

---

## Bill of Materials

| Ref  | Value / MPN                       | Description                               | Package       |
|------|-----------------------------------|-------------------------------------------|---------------|
| U1   | AMS AS5600                        | 12-bit magnetic rotary position sensor    | SOIC-8        |
| D1   | Nexperia PRTR5V0U2X               | Dual-channel ESD protection, 5 V clamp    | SOT-363       |
| C1   | 100 nF X5R ≥ 6.3 V               | VDD bypass decoupling                     | 0402          |
| R_DIR| 10 kΩ 1 % 0402                    | DIR pull-down to GND (CCW direction)      | 0402          |
| R_PGO| 10 kΩ 1 % 0402                    | PGO pull-up to +3V3 (output disabled)    | 0402          |
| J1   | JST SM04B-GHS-TB (shielded body)  | 4-pin GH cable connector to Wash      | TH right-angle|
| —    | Diametrically magnetised magnet   | 6 mm diam × 2.5 mm axial, N42 grade      | Press-fit     |

### Magnet Specification

- **Type:** Diametrically magnetised cylindrical (axial field).
- **Dimensions:** 6 mm diameter × 2.5 mm height.
- **Material:** NdFeB N42 (B_r ≈ 1.32 T).
- **Air gap to IC:** 0.5 – 1.5 mm target; AS5600 AGCM AGC output used to verify gap.
- **Mounting:** Press-fit into a recess in the nacelle pivot shaft end cap;
  shaft made of non-magnetic aluminium or PETG.

---

## Schematic Description

### J1 — Cable Connector

JST SM04B-GHS-TB (shielded body), right-angle, mates with JST GHHR-04V-S on the
STP cable from Wash J_ENC.

| Pin | Signal   | Description                               |
|-----|----------|-------------------------------------------|
| 1   | GND      | Power and signal return                   |
| 2   | +3V3     | 3.3 V power from Wash                 |
| 3   | ENC_SDA  | I²C SDA (to/from Wash)               |
| 4   | ENC_SCL  | I²C SCL (from Wash)                   |
| MP  | SHIELD   | Cable shield; floating at this board end  |

**Shield note:** The cable drain wire connects to PGND at the Wash J_ENC MP pin
only.  The shield is left floating (not connected) at J1 MP on this board to prevent
ground loops.  The board GND is a clean signal ground, not chassis PGND.

### D1 — ESD / EMI Protection (PRTR5V0U2X)

The Nexperia PRTR5V0U2X dual-channel ESD / EMI protection device is inserted in
series on both SDA and SCL lines between J1 and U1.  Features:

- Bidirectional ESD protection per IEC 61000-4-2 Level 4 (±8 kV contact).
- Internal low-pass EMI filter (R = 10 Ω typ, C = 0.7 pF typ per channel).
- V_clamp = 5 V; compatible with 3.3 V I²C logic.
- V_cc pin tied to +3V3; GND pin tied to GND.

### U1 — AS5600 Magnetic Encoder

Connected to ENC_SDA / ENC_SCL directly from D1 outputs.

| Pin | Net       | Configuration                             |
|-----|-----------|-------------------------------------------|
| 1   | VDD       | +3V3; 100 nF C1 within 2 mm             |
| 2   | GND       | Signal ground                             |
| 3   | DIR       | Pulled to GND via R_DIR 10 kΩ (CCW)     |
| 4   | OUT       | Analog / PWM output — no connect (NC)    |
| 5   | GND2      | Signal ground (tied to pin 2)            |
| 6   | SDA       | I²C SDA via D1                           |
| 7   | SCL       | I²C SCL via D1                           |
| 8   | PGO       | Pulled to +3V3 via R_PGO 10 kΩ (output disable) |

**DIR = GND:** Defines angle counting direction as counter-clockwise when viewed from
the magnet face.  Direction is fixed at board level; software may negate if needed.

**PGO = +3V3:** Disables the OUT pin (pin 4) analogue/PWM output.  This pin is
high-impedance when PGO is high, reducing power and noise.

**I²C address:** Fixed at 0x36 (not configurable).

### R_DIR — Direction Pull-down

10 kΩ 0402, DIR (pin 3) to GND.  Sets CCW counting direction.

### R_PGO — Power / Output Mode

10 kΩ 0402, PGO (pin 8) to +3V3.  Disables OUT (pin 4) analogue output.

### C1 — VDD Bypass

100 nF 0402 X5R, +3V3 to GND, placed within 2 mm of U1 pin 1.

---

## PCB Physical Specification

| Parameter          | Value                                             |
|--------------------|---------------------------------------------------|
| Board dimensions   | 15 mm × 15 mm                                     |
| Layer count        | 2-layer (top + bottom)                            |
| PCB material       | FR4 TG130                                         |
| Copper weight      | 1 oz (35 µm) both layers                         |
| Surface finish     | HASL lead-free or ENIG                            |
| Solder mask        | Green, both sides                                 |
| Silkscreen         | White, top only                                   |
| Connector location | J1 on board edge for right-angle cable exit       |
| Magnet clearance   | Centre of board over U1; 15 mm × 15 mm keeps     |
|                    | the magnet centred over the pivot axis            |

### Mounting

- Four M2 standoff holes at corners (2.5 mm from each edge).
- Standoffs: 5 mm length aluminium M2 (non-magnetic), M2 nylon screws.
- The board mounts on the wing spar end cap with U1 facing the nacelle pivot shaft.
- The diametrically magnetised magnet is press-fit into the pivot shaft end cap
  directly above U1 at the correct air gap (0.5 – 1.5 mm).

---

## Cable Assembly

| Parameter             | Specification                                         |
|-----------------------|-------------------------------------------------------|
| Cable type            | Belden 9367 STP, 2 × 28 AWG twisted pairs, PVC jacket|
| Pairs                 | Pair 1: ENC_SDA + GND; Pair 2: ENC_SCL + +3V3        |
| Length                | 600 mm (nominal; measure per nacelle)                 |
| Wash end          | JST GHR-04V-S, drain wire crimped to MP contact        |
| ENC-NACELLE-1 end     | JST GHR-04V-S, drain wire cut back and not connected  |
| Ferrite chokes        | Würth 74271222 snap-on at both ends, over full bundle |
| Jacket colour         | Grey or natural (to distinguish from power cables)    |

---

## Installation Notes

1. **Pivot shaft material** must be non-magnetic (aluminium 6061, PETG, or fibreglass).
   A steel or ferrite shaft will distort the field and invalidate angle readings.
2. **Magnet alignment:** Orient the magnet so the diametric axis is perpendicular to
   the pivot rotation axis.  The AS5600 detects the in-plane field component.
3. **Air gap verification:** After assembly, read the AS5600 AGC register (0x1A).
   AGC = 0 (minimum gain) → magnet too close; AGC = 255 → too far away.
   Target AGC = 50 – 200 for best linearity.
4. **Zero angle calibration:** Use the AS5600 ZPOS / MPOS registers or the software
   calibration offset to zero the angle at the hover (0°) nacelle position.
5. **Direction verification:** In hover, commanding nose-up nacelle tilt should
   produce increasing angle count.  If not, set the firmware direction flag.

---

## EMI Hardening

This board operates in the EDF nacelle at up to 500 W/m² (E = 434 V/m) field
strength from external RF sources.

| Measure                        | Implementation                                   |
|--------------------------------|--------------------------------------------------|
| ESD/EMI protection             | PRTR5V0U2X on SDA and SCL lines                  |
| VDD bypass                     | 100 nF X5R within 2 mm of U1                     |
| Cable shielding                | Belden 9367 STP; single-point drain at Wash  |
| Ferrite chokes                 | Würth 74271222 at both cable ends                 |
| Magnet field vs. threat        | 50–100 mT magnet vs. 1.45 µT external H-field;   |
|                                | 34 000 : 1 signal-to-threat ratio                |
| Physical enclosure             | Nacelle EDF housing provides partial metal screen |

---

## Related Files

- `CAPE-A-2.kicad_sch` — host flight control cape; provides J_ENC connector
- `CAPE-A-2.md` — §13 documents the encoder interface, pull-ups, and GPIO assignment
- `XCVR-49MHZ-2.md` — companion 49 MHz transceiver board
- `CAPE-B-2.md` — companion comms/logging cape

---

## References

1. AMS AS5600 Datasheet v1-09 — ams-osram.com
2. Nexperia PRTR5V0U2X Datasheet — PRTR5V0U2X.pdf
3. Belden 9367 Cable Datasheet — belden.com
4. Würth 74271222 Ferrite Clamp Datasheet — we-online.com
5. IEC 61000-4-2:2008 — ESD immunity requirements
6. MIL-STD-461G:2015 — EM emissions and susceptibility requirements
