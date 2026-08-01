# Serenity UAV — Documentation Index

> **Rev S Baseline (2026-07-04):** 24-inch CF-PETG hull, 8-node cooperative avionics,
> 50mm tandem EDF nacelles, cargo system, autonomous flight capability. See below for
> links to all design documents, build guides, and technical analysis.

## 📋 Quick Navigation

- **[Root README.md](../README.md)** — High-level project overview, mission profile, architecture
- **[AGENTS.md](../AGENTS.md)** — Authoritative project policy (standards, coding, fabrication,
  licensing, attribution)
- **[REFERENCES.md](../REFERENCES.md)** — Master citation catalog (all standards, regulations,
  suppliers, datasheets)
- **[PHASED_BUILD_GUIDE.md](./PHASED_BUILD_GUIDE.md)** — Rev S phases 0–10 assembly steps (with
  material quantities and time estimates)
- **[REVN_BUILD_GUIDE_24IN.md](./REVN_BUILD_GUIDE_24IN.md)** — Detailed Phase 1–4 guidance for
  24-inch hull structure

## 📁 Design Documentation by Domain

### Airframe & Structures
- **[airframe/README.md](../airframe/README.md)** — Fuselage, wings, nacelles, landing gear
- **[airframe/AGENTS.md](../airframe/AGENTS.md)** — CAD standards, STL generation, printing specs
- **[TILT_SPAR_ANALYSIS.md](./TILT_SPAR_ANALYSIS.md)** — Material selection, stress analysis for
  tilt pivot rod (AISI 4130, 17-4 PH, 7075-T6)
- **[NOZZLE_DRIVE_TRADE.md](./NOZZLE_DRIVE_TRADE.md)** — Nacelle nozzle iris actuation mechanism
  design decisions
- **[LANDING_GEAR_ANALYSIS.md](./LANDING_GEAR_ANALYSIS.md)** — Wire schedule, drop-height testing,
  fail-safe design

### Avionics & Electronics
- **[avionics/README.md](../avionics/README.md)** — 8-node PACE failover, PCB boards, firmware
  architecture
- **[avionics/AGENTS.md](../avionics/AGENTS.md)** — PCB design standards, security, EMI hardening
- **[avionics/kicad/Wash/Wash.md](../avionics/kicad/Wash/)** — Flight control cape (IMU, ESC
  drive, servo outputs)
- **[avionics/kicad/Zoë/Zoë.md](../avionics/kicad/Zoë/)** — Comms/logging cape (radios, μSD,
  payload GPIO)
- **[avionics/kicad/Kaylee/Kaylee.md](../avionics/kicad/Kaylee/)** — Power distribution board
  (fuses, 5V BEC, main bus)
- **[avionics/kicad/Emma/Emma.md](../avionics/kicad/Emma/)** — 49 MHz + LoRa transceiver cape
  (optional Phase 10+)
- **[avionics/kicad/Jayne/Jayne.md](../avionics/kicad/Jayne/)** — Vision/ToF/laser board (nose +
  cargo sensors)
- **[JAYNE_LASER_ANALYSIS.md](./JAYNE_LASER_ANALYSIS.md)** — Laser indicator class, safety
  interlocks, eye-safety compliance

### Ground Control Station
- **[gcs/README.md](../gcs/README.md)** — Malcolm hardware spec, 5-radio comms, antenna gimbal
- **[gcs/AGENTS.md](../gcs/AGENTS.md)** — GCS firmware, QGroundControl integration, tracking

### Build Tools & Automation
- **[tools/README.md](../tools/README.md)** — Validation scripts (STL mesh, KiCad ERC/DRC),
  CI pipeline, design automation
- **[tools/AGENTS.md](../tools/AGENTS.md)** — Build tool specifications and usage guidelines

### Bill of Materials & Procurement
- **[current-specification/README.md](../current-specification/README.md)** — Rev S BOM
  (JSON/CSV), parts list, revision history
- **[current-specification/bom_revS.json](../current-specification/bom_revS.json)** —
  Structured BOM (suppliers, mass, CG, cost tracking)
- **[current-specification/bom_revS.csv](../current-specification/bom_revS.csv)** — Flat BOM
  (import to spreadsheet)

## 📊 Regulatory & Compliance

- **[attribution_and_licensing.md](./attribution_and_licensing.md)** — CC BY 4.0 / CERN-OHL-W 2.0
  licensing strategy; third-party attribution chains
- **Regulatory checklist** (under development):
  - FAA Part 48 (sUAS registration)
  - FAA Part 107 (remote pilot cert)
  - FCC Part 15 §15.235 (49 MHz unlicensed)
  - IEC 62368-1 (safety / EMI)
  - AUVSI / ASTM F38 (best practices)

## 📈 Historical Revisions

| Rev | Hull | Nacelle EDFs | Avionics | Build Status | Archive |
|-----|------|--------------|----------|--------------|---------|
| S | 24" | 50mm X-Fly tandem | 8-node Wash/Zoë/Kaylee/Emma/Jayne (Rev S1) | Current baseline (Phase 5 ready) | — |
| R1 | 24" | 50mm X-Fly tandem | 8-node (pre-S1) + hull-frame baking | Design complete | `git log` |
| R | 24" | 50mm X-Fly tandem | 8-node (first 24" iteration) | Archived | `git log` |
| Q | 24" | 50mm X-Fly tandem | 8-node architecture finalized | Archived | `git log` |
| P | 18" | 80mm Changesun 2700KV | 4-node prototype | Archived | `git log` |
| M & earlier | 18" | Various | 2–4 node prototypes | Archived | `git log` |

**⚠ SUPERSEDED for builds:** Rev M (18", dual 80mm EDFs) and earlier are **not** the current
design baseline. All new work targets Rev S (24", 50mm tandem EDFs, 8-node Wash/Zoë). The Rev M
design documents are retained for historical reference only; see links below.

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Year:**2026  |**Status:** Superseded — historical reference only (see banner above)

> Rev M supersedes Rev L. Hardware upgrade: all 8 PocketBeagle 2 (AM6232) replaced by PocketBeagle 2 Industrial (AM6254).
> AM6254 quad Cortex-A53 1.4GHz · 1GB DDR4 · 64GB eMMC · −40°C to 85°C industrial. Propulsion + governor unchanged from Rev L.

---

## Attribution

| Work | Author | License | Source |
| ------ | -------- | --------- | -------- |
| Hull geometry | Peter Farell | CC BY 4.0 | printables.com/model/548545 |
| EDF nozzles | BamJr | CC BY 4.0 | thingiverse.com/thing:2991269 |
| Blueprint proportions | Mandel + Earls / QMx / Universal | © 2007 QMx | 269ft×170ft×79ft ratios |
| All other design | Steve Griffing | CC BY 4.0 | This project |
| Visual inspiration | Joss Whedon / Mutant Enemy / Universal | © reserved | Firefly (2002) / Serenity (2005) — Fan work |

---

## Quick Specs (18" Scale — propulsion unchanged Rev L → Rev M; compute board upgraded)

| Parameter | Value |
| ----------- | ------- |
| Hull length | 457.2 mm (18.00") · Canon 269 ft |
| Canonical beam (tip-to-tip) | 288.9 mm (11.375") · Canon 170 ft |
| Canonical height (landed) | 134.3 mm (5.286") · Canon 79 ft |
| Canon source | QMx Official Blueprints, Mandel/Earls 2007 |
| Hull structure | PETG thin shell + X-30 foam + CF skeleton |
| Propulsion | **2× (2× Changesun XRP 3660-2700KV 80mm 6S EDF, tandem series) per nacelle** · 1× XFLY X4 PRO 40mm 4S fuselage |
| Nacelle pod OD | **93.5 mm**canonical · Pod length**230 mm** (tandem) · ID 83 mm (XRP housing) |
| Nacelle tip-to-tip | 288.9 mm (11.375") — CANONICAL |
| Nacelle C-to-C | 195.5 mm (7.70") |
| Pylon datum from CL | 82.2 mm (1/3 from nacelle inner edge) |
| Arm stub | 10.4 mm hull edge → nacelle inner edge |
| Nacelle thrust (each) | **5,300 g** (2× XRP 2700KV tandem series, ~91% efficiency) |
| Fuselage thrust | 650 g @ 4S · 30A (XFLY X4 PRO 5850KV) |
| Total hover thrust | **11,250 g** |
| Airframe dry mass | **3,197 g** |
| AUW empty (6S 4000mAh 410g) | **3,607 g (7.95 lb) · T/W 3.12** |
| AUW cargo 250g (6S 2800mAh 295g) | **3,742 g (8.25 lb) · T/W 3.01** |
| Max payload (T/W=2.0) | **1,406 g (3.10 lb)** |
| T/W one EDF failed | **2.29:1** — partner EDF continues (fault latched) |
| T/W one nacelle lost | **1.65:1** — FC RTH · controlled descent |
| CG target | 190 mm (7.48") from nose |
| GPS patch | 59.4 mm from nose |
| SiK 915MHz belly | 253.7 mm from nose |
| 49MHz Part 15 dorsal | 365.8 mm from nose |
| Avionics | **8× PocketBeagle 2 Industrial (AM6254)** · FC1–FC4 Cape-A · CN1–CN4 Cape-B · DK 2820-100003007-ND · $51.03 ea |
| Navigation lights | ICAO Annex 2 · 14 CFR 91.209 · PCA9685 I²C PWM driver |
| FAA registration | **N00000 PLACEHOLDER — replace before flight** |

### Rev M Changes (Hardware Upgrade)

| Change | Rev L | Rev M |
| -------- | ------- | ------- |
| Compute board | PocketBeagle 2 (AM6232) | **PocketBeagle 2 Industrial (AM6254)** |
| SoC | Dual Cortex-A53 1.0GHz | **Quad Cortex-A53 1.4GHz** |
| RAM | 512MB DDR4 | **1GB DDR4** |
| eMMC | Not populated | **64GB eMMC (OS boot + storage)** |
| OS microSD | 8× required | **Eliminated — eMMC handles OS boot** |
| Log microSD (Cape-B) | 4× write-blocked | **Unchanged — retained** |
| Temperature | Commercial 0–70°C | **Industrial −40°C to 85°C** |
| Onboard MCU | None beyond A53/M4F/PRU | **MSPM0L1105 + 12-bit ADC (future use)** |
| Cape-A / Cape-B PCBs | Rev K design | **Unchanged — 72-pin header compatible** |
| Propulsion / governor | Rev L dual-EDF PID | **Unchanged** |
| Part number | — | **100003007 · DK 2820-100003007-ND · $51.03 ea** |

### Rev L Governor (Unchanged in Rev M)

| Parameter | Value |
| ----------- | ------- |
| Governor | Per-EDF PID closed-loop RPM · 500 Hz (AM6254 M4F coprocessor) |
| Feedback | BDSHOT RPM 1 kHz + BLHeli32 serial telem 10 Hz |
| PID gains (RPM) | Kp=3×10⁻⁴ · Ki=1×10⁻⁵ · Kd=8×10⁻⁵ |
| Nacelle equalization | FWD/AFT RPM matched · AFT +2% bias (inlet deficit) |
| Thermal derate | 85°C → linear derate to 0% cap at 110°C |
| Current limits | 80A soft (proportional) · 105A hard (latch) |
| Fault latch | Per-ESC · ground power cycle + GCS ack to clear |
| DSHOT channels | GP26–GP29 (PRU-ICSS 250 MHz) · freed GP29 via PCA9685 nav lights |
| Telem mux | 74HC4051 8:1 · MCP23017 3-bit select (SEL A/B/C) |

### Rev K → Rev L Changes (historical)

| Change | Rev K | Rev L |
| -------- | ------- | ------- |
| Nacelle governor | Open-loop throttle pass-through | **PID closed-loop RPM per EDF + equalization** |
| M4F coprocessor | Unused for propulsion | **500 Hz governor loops** |
| Fault detection | Logged only | **Active latch + MAVLink + RTH** |
| Thermal derate | ESC firmware only | **Governor-level proportional derate** |
| EDF options | XRP only documented | **Budget / Standard / High-perf all documented** |
| Hardware | Dual-EDF Rev K | **Identical — firmware update only** |

### Rev J → Rev K Changes (historical)

| Change | Rev J | Rev K |
| -------- | ------- | ------- |
| Nacelle EDF | 1× XRP per nacelle | **2× XRP tandem series per nacelle** |
| Nacelle ESC | 2× 120A total | **4× 120A (one per EDF)** |
| Nacelle thrust (each) | 2,900 g | **5,300 g** (+83%) |
| Total thrust | 6,450 g | **11,250 g** (+74%) |
| Nacelle pod length | 144 mm | **230 mm** (tandem) |
| Dry mass | 2,177 g | **3,197 g** (+1,020 g) |
| T/W empty | 2.49 | **3.12** |
| Max payload | 753 g | **1,406 g** (+87%)
