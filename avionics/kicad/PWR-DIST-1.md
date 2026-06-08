# PWR-DIST-1 — Power Distribution Board

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Revision:** Q (initial design, 2026-06-06)
**Status:** Schematic complete — PCB layout pending

---

## Purpose

PWR-DIST-1 is the central power distribution board for the Serenity UAV.  It routes
6S LiPo power from the battery through a main ANL fuse and hall-effect current sensor
to five ESC outputs (4 nacelle + 1 rear fuselage EDF), and generates a dual-redundant
5 V regulated rail for all avionics, servos, and sensor nodes.

It also provides battery voltage and current telemetry to the Wash flight control
nodes via analog signal connectors, and terminates the PGND chassis bonding strap
from all Faraday enclosures at a single star point.

---

## Bill of Materials

| Ref | Value / MPN | Description | Package |
|---|---|---|---|
| J_BAT | AS150 or XT150 solder tabs | 6S LiPo battery input; 150 A continuous | Solder lug |
| F_MAIN | Littelfuse ANL 400 A (Phase 2–6) / 500 A (Phase 7) | Main blade fuse in ANL holder | ANL Keystone 3568 |
| ACS758_MAIN | Allegro ACS758ECB-300B | ±300 A hall-effect current sensor, 13.3 mV/A | SOIC-8 |
| C_ACS_VCC | 100 nF X5R ≥ 6.3 V 0402 | ACS758 VCC bypass | 0402 |
| C_ACS_FILT | 4.7 nF X5R ≥ 6.3 V 0402 | ACS758 FILTER pin RC cap; sets ~1 kHz bandwidth | 0402 |
| TVS_ESC1 | Littelfuse SMBJ27A | 27 V bidirectional TVS; clamps ESC1 back-EMF spikes | SMB |
| TVS_ESC2 | Littelfuse SMBJ27A | 27 V bidirectional TVS; ESC2 back-EMF clamp | SMB |
| TVS_ESC3 | Littelfuse SMBJ27A | 27 V bidirectional TVS; ESC3 back-EMF clamp | SMB |
| TVS_ESC4 | Littelfuse SMBJ27A | 27 V bidirectional TVS; ESC4 back-EMF clamp | SMB |
| TVS_ESC5 | Littelfuse SMBJ27A | 27 V bidirectional TVS; ESC5 back-EMF clamp | SMB |
| C_BULK1 | 1000 µF 35 V aluminium electrolytic | ESC1 bulk decoupling; ≥ 35 V rating required | Radial D10 P5.0 |
| C_BULK2 | 1000 µF 35 V aluminium electrolytic | ESC2 bulk decoupling | Radial D10 P5.0 |
| C_BULK3 | 1000 µF 35 V aluminium electrolytic | ESC3 bulk decoupling | Radial D10 P5.0 |
| C_BULK4 | 1000 µF 35 V aluminium electrolytic | ESC4 bulk decoupling | Radial D10 P5.0 |
| C_BULK5 | 1000 µF 35 V aluminium electrolytic | ESC5 bulk decoupling | Radial D10 P5.0 |
| J_ESC1 | AS150 or XT90 solder tabs | Port fwd nacelle ESC output; 8 AWG silicone | Solder lug |
| J_ESC2 | AS150 or XT90 solder tabs | Port aft nacelle ESC output; 8 AWG silicone | Solder lug |
| J_ESC3 | AS150 or XT90 solder tabs | Stbd fwd nacelle ESC output; 8 AWG silicone | Solder lug |
| J_ESC4 | AS150 or XT90 solder tabs | Stbd aft nacelle ESC output; 8 AWG silicone | Solder lug |
| J_ESC5 | XT60 solder tabs | Rear fuselage ESC output; 10 AWG silicone | Solder lug |
| UBEC1 | Hobbywing UBEC 5 V 10 A switching BEC | Primary 5 V avionics rail; input 6–25.2 V (6S) | Module |
| UBEC2 | Hobbywing UBEC 5 V 10 A switching BEC | Redundant 5 V avionics rail | Module |
| J_AVI_A | JST PH 2-pin or equivalent | 5 V output to avionics bays A + B | TH |
| J_AVI_B | JST PH 2-pin or equivalent | 5 V output to avionics bays D + E | TH |
| J_SRV | JST PH 2-pin or equivalent | 5 V output to tilt + nozzle servos | TH |
| R_VBAT_H | 100 kΩ 1 % 0402 | VBAT voltage divider high-side | 0402 |
| R_VBAT_L | 15 kΩ 1 % 0402 | VBAT voltage divider low-side; output to ADC | 0402 |
| J_SIG_I | 2-pin header | ACS758 VIOUT analog signal to Wash ADC | TH |
| J_SIG_V | 2-pin header | VBAT_MEAS voltage divider output to Wash ADC | TH |
| J_PGND | M3 lug terminal | PGND chassis bonding strap attachment point | TH |

---

## Schematic Description

### Power Path

```
Battery (+) ──► J_BAT Pin 1
                    │
                    ▼ VBAT_IN
              F_MAIN (ANL fuse)
                    │
                    ▼ VBAT_FUSED
            ACS758_MAIN IP+ (pins 1, 2)
            ACS758_MAIN IP- (pins 3, 4)
                    │
                    ▼ VBAT_BUS (main power bus)
        ┌───────────┼──────────┬──────────┬──────────┐
        ▼           ▼          ▼          ▼          ▼
     J_ESC1      J_ESC2     J_ESC3     J_ESC4     J_ESC5
  (Port Fwd)  (Port Aft)  (Stbd Fwd)(Stbd Aft)  (Rear EDF)
  +TVS+Cbulk  +TVS+Cbulk +TVS+Cbulk +TVS+Cbulk +TVS+Cbulk

Battery (−) ──► J_BAT Pin 2 ──► PGND (chassis star point)
```

### Net Definitions

| Net | Source | Destination | Voltage |
|---|---|---|---|
| VBAT_IN | J_BAT Pin 1 | F_MAIN Pin 1 | 22.2 V nom (6S) |
| VBAT_FUSED | F_MAIN Pin 2 | ACS758_MAIN IP+ | 22.2 V nom |
| VBAT_BUS | ACS758_MAIN IP- | J_ESC1–5; UBEC1/2 VIN+; R_VBAT_H | 22.2 V nom |
| +5V_AVI | UBEC1/2 VOUT+ | J_AVI_A, J_AVI_B, J_SRV, ACS758 VCC | 5.0 V regulated |
| GND | UBEC1/2 VOUT−; ACS758 GND; signal returns | All avionics signal returns | 0 V |
| PGND | J_BAT Pin 2; TVS_ESCn cathodes; C_BULKn (−); J_PGND | Chassis star = battery (−) | 0 V chassis |
| VIOUT_MAIN | ACS758_MAIN pin 8 | J_SIG_I Pin 1 → Wash ADC | 0.5–4.5 V |
| VBAT_MEAS | R_VBAT_H/R_VBAT_L junction | J_SIG_V Pin 1 → Wash ADC | 0–3.3 V (scaled) |
| FILTER_ACS | ACS758_MAIN pin 7 | C_ACS_FILT Pin 1 | RC filter node |

### ACS758_MAIN — Current Sensor

The Allegro ACS758ECB-300B measures main bus current in the VBAT_FUSED → VBAT_BUS
path.  IP+ (pins 1, 2) connect to VBAT_FUSED; IP- (pins 3, 4) connect to VBAT_BUS.
Current flows conductor-through from battery to ESC outputs.

- **Sensitivity:** 13.3 mV/A (−300B variant); 2.5 V quiescent = 0 A
- **Range:** −300 A to +300 A (positive = current flowing from battery to ESCs)
- **VIOUT output:** 0.5 V (−300 A) to 4.5 V (+300 A), 3.3 V mid-scale compatible
- **FILTER cap (C_ACS_FILT):** 4.7 nF sets bandwidth ≈ 1/(2π × 1200 × 4.7 nF) ≈ 28 kHz;
  adequate for ESC step response without aliasing in the ADC at 1 kHz sample rate.
- **VCC:** +5V_AVI, 100 nF bypass (C_ACS_VCC) within 2 mm of pin 6.

### VBAT Voltage Divider

R_VBAT_H (100 kΩ) and R_VBAT_L (15 kΩ) form a resistor divider from VBAT_BUS to GND.

- **Scale factor:** 15 / (100 + 15) = 0.130 → V_ADC = V_BAT × 0.130
- **At full 6S (25.2 V):** V_ADC = 3.28 V (within 3.3 V ADC input range)
- **At nominal 6S (22.2 V):** V_ADC = 2.89 V
- **ADC input:** Wash AIN0 (PocketBeagle 2 P1-2, 1.8 V ADC)

**Note:** Wash ADC input is 1.8 V max.  If using PocketBeagle 2 onboard ADC
(1.8 V full scale), revise divider to R_VBAT_H = 100 kΩ, R_VBAT_L = 8.2 kΩ:
scale = 8.2/108.2 = 0.0758 → V_ADC = 25.2 × 0.0758 = 1.91 V.
**PCB revision Q1:** Replace R_VBAT_L with 8.2 kΩ before board spin if PB2 native
ADC is used.  If an external 3.3 V ADC (e.g., ADS1015 on Wash) is used, the
15 kΩ value is correct.

### ESC Output Protection (TVS_ESCn + C_BULKn)

Each ESC output is protected by:
- **SMBJ27A bidirectional TVS:** Clamps bus voltage to ≤ 27 V during motor stop or
  ESC recirculation spike.  Crowbar response < 1 ps.  Located within 20 mm of ESC
  solder pad on PDB.
- **1000 µF 35 V electrolytic:** Absorbs energy during ESC PWM switching transitions.
  ESR target: ≤ 50 mΩ (low-ESR aluminium or polymer types preferred).

### Dual UBEC Architecture

UBEC1 and UBEC2 are both connected in parallel on the +5V_AVI rail.  Both draw from
VBAT_BUS independently:

- **Normal operation:** Both UBECs share the avionics load (~5.25 A each at 10.5 A total).
- **UBEC1 failure:** UBEC2 carries the full 10.5 A load (within its 10 A rating with
  minimal margin; the 0.5 A excess is absorbed by cable resistance and bulk cap).
- **UBEC2 failure:** Same — UBEC1 carries full load.
- **Both fail:** Avionics lose power; the PocketBeagle 2 nodes execute their power-loss
  interrupt handlers and commit the flight log before halting.

Each UBEC's GND_OUT is connected to GND (signal/avionics return), not PGND.  The
GND ↔ PGND bond occurs at the battery (−) terminal only.

### PGND Star Point

J_PGND provides the single-point chassis bonding terminal on PWR-DIST-1.  All PGND
nets on the board (battery (−), ESC bulk cap returns, TVS cathodes) terminate here.
The Belden 8663 daisy-chain bonding strap from avionics bays A → B → D → E also
terminates at J_PGND.

- **Terminal:** M3 × 10 mm machine screw through a tin-plated copper bus bar pad
- **Lug:** Crimped + soldered M3 tin-plated copper ring lug on Belden 8663 braid
- **Target resistance:** ≤ 2.5 mΩ total chain per MIL-B-5087B Class H

---

## PCB Physical Specification

| Parameter | Value |
|---|---|
| Board dimensions | 100 mm × 80 mm |
| Layer count | 4-layer (signal / GND plane / PGND plane / signal) |
| PCB material | FR4 TG150 |
| Copper weight | 4 oz (140 µm) layers 1 + 4 (main power); 1 oz layers 2 + 3 |
| Surface finish | ENIG (gold on pads and bus bars) |
| Solder mask | Black, both sides |
| Silkscreen | White, top only |
| Min trace width (signal) | 0.25 mm |
| Main power bus | 25 mm copper pour on layer 1 + 4 (VBAT_IN, VBAT_BUS, PGND) |
| Via stitching | VBAT_BUS and PGND planes connected with 0.8 mm vias on 5 mm grid |

### Mounting

- Four M3 standoff holes at corners, 5 mm from each edge.
- Standoffs: 10 mm length aluminium M3 (non-magnetic), M3 nylon screws.
- Location: keel rib at station 200 mm from nose.
- Orientation: battery connector face aft, avionics connectors port-side.

---

## Connector Pinout Summary

| Connector | Pin 1 | Pin 2 | Wire gauge | Mating connector |
|---|---|---|---|---|
| J_BAT | VBAT_IN (+) | PGND (−) | 4/0 AWG | AS150 or XT150 |
| J_ESC1 | VBAT_BUS (+) | PGND (−) | 8 AWG | AS150 or XT90 |
| J_ESC2 | VBAT_BUS (+) | PGND (−) | 8 AWG | AS150 or XT90 |
| J_ESC3 | VBAT_BUS (+) | PGND (−) | 8 AWG | AS150 or XT90 |
| J_ESC4 | VBAT_BUS (+) | PGND (−) | 8 AWG | AS150 or XT90 |
| J_ESC5 | VBAT_BUS (+) | PGND (−) | 10 AWG | XT60 |
| J_AVI_A | +5V_AVI | GND | 20 AWG | JST PH 2-pin |
| J_AVI_B | +5V_AVI | GND | 20 AWG | JST PH 2-pin |
| J_SRV | +5V_AVI | GND | 18 AWG | JST PH 2-pin |
| J_SIG_I | VIOUT_MAIN | GND | 28 AWG STP | JST PH 2-pin |
| J_SIG_V | VBAT_MEAS | GND | 28 AWG STP | JST PH 2-pin |
| J_PGND | PGND | PGND | 19 mm braid | M3 lug |

---

## EMI Hardening

| Measure | Implementation |
|---|---|
| TVS on each ESC output | SMBJ27A clamps motor spike to 27 V |
| Bulk capacitance per ESC | 1000 µF 35 V reduces PWM ripple amplitude |
| 4-layer PCB plane stack | Layer 2 = GND plane; layer 3 = PGND plane; full copper pour |
| Single-point PGND star | All chassis currents return to one point; eliminates ground loops |
| ACS758 FILTER cap | 4.7 nF limits VIOUT bandwidth to 28 kHz; rejects PWM switching noise |
| UBEC switching frequency | Hobbywing UBEC operates at 100 kHz; well above audio, well below ADC alias frequency |
| Faraday enclosure bonding | ≤ 2.5 mΩ chain from bays to PGND star at J_PGND |

---

## Installation Notes

1. **Bus bar soldering:** J_BAT and J_ESC1–4 pads carry 84–376 A peak.  Use 63/37 or
   SAC305 solder with a 80 W+ iron; preheat board pad area with heat gun to 80–100 °C
   before soldering to prevent cold joints.
2. **UBEC mounting:** Mount UBEC1 and UBEC2 with their heat-sink faces against the
   aluminium mounting plate.  Apply a 0.5 mm thermal pad between UBEC case and plate.
3. **ANL fuse access:** F_MAIN is accessible from below the belly access plate
   (60 × 80 mm cutout) without removing the PDB.  Replace fuse with rated ANL blade only.
4. **ADC divider revision:** Verify Wash ADC full-scale voltage before ordering PCBs.
   Replace R_VBAT_L with 8.2 kΩ (0402) if using PocketBeagle 2 native 1.8 V ADC.
5. **PGND strap torque:** M3 lug at J_PGND torqued to 0.5 N·m.  Verify bond resistance
   ≤ 2.5 mΩ with Kelvin 4-wire measurement after installation.

---

## Related Files

- `avionics/kicad/PWR-DIST-1.kicad_sch` — Schematic source
- `docs/POWER_SYSTEM_Q.md` — Complete power system analysis including VTOL thrust analysis
- `avionics/kicad/CAPE-A-2.md` — Flight control cape; receives +5V_AVI and ADC signals
- `avionics/kicad/CAPE-B-2.md` — Comms/logging cape; receives +5V_AVI

---

## References

1. Allegro ACS758ECB-300B Datasheet — allegromicro.com
2. Littelfuse SMBJ27A TVS Datasheet — littelfuse.com
3. Hobbywing UBEC 5 V 10 A Product Specification
4. MIL-B-5087B — Bonding, Electrical, and Lightning Protection for Aerospace Systems
5. IPC-2221B — Generic Standard on Printed Board Design (trace width and current)
6. AUVSI: UAS Best Practices for Electrical Systems Design (2022)
