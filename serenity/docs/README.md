<!-- OpenDyslexic font for screen reading (CC BY 4.0) -->
<link rel="stylesheet" href="https://fonts.cdnfonts.com/css/opendyslexic">
<style>
body,p,li,td,th,code,pre{font-family:'OpenDyslexic','OpenDyslexicMono',sans-serif!important;line-height:1.8}
@media screen{body{background:#0d1117;color:#e6edf3}a{color:#58a6ff}
  h1,h2,h3{color:#58a6ff;border-bottom:1px solid #30363d;padding-bottom:6px}
  code{background:#161b22;color:#e6edf3;padding:2px 6px;border-radius:4px}
  th{background:#21262d;color:#79c0ff}tr:nth-child(even)td{background:#161b22}}
@media print{body{background:#fff!important;color:#111!important}a{color:#003399!important}}
</style>

# Serenity-Class Tiltrotor UAV — Rev L (18" Canonical Build)

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Year:** 2026  |  **Status:** Public release

> Rev L supersedes Rev K. Adds per-EDF PID closed-loop RPM governor + cooperative nacelle equalization.
> Hardware identical to Rev K dual-EDF. Firmware-only update to AM6232 M4F coprocessor.

---

## Attribution

| Work | Author | License | Source |
|------|--------|---------|--------|
| Hull geometry | Peter Farell | CC BY 4.0 | printables.com/model/548545 |
| EDF nozzles | BamJr | CC BY 4.0 | thingiverse.com/thing:2991269 |
| Blueprint proportions | Mandel + Earls / QMx / Universal | © 2007 QMx | 269ft×170ft×79ft ratios |
| All other design | Steve Griffing | CC BY 4.0 | This project |
| Visual inspiration | Joss Whedon / Mutant Enemy / Universal | © reserved | Firefly (2002) / Serenity (2005) — Fan work |

---

## Quick Specs (Rev L — 18" Scale)

| Parameter | Value |
|-----------|-------|
| Hull length | 457.2 mm (18.00") · Canon 269 ft |
| Canonical beam (tip-to-tip) | 288.9 mm (11.375") · Canon 170 ft |
| Canonical height (landed) | 134.3 mm (5.286") · Canon 79 ft |
| Canon source | QMx Official Blueprints, Mandel/Earls 2007 |
| Hull structure | PETG thin shell + X-30 foam + CF skeleton |
| Propulsion | **2× (2× Changesun XRP 3660-2700KV 80mm 6S EDF, tandem series) per nacelle** · 1× XFLY X4 PRO 40mm 4S fuselage |
| Nacelle pod OD | **93.5 mm** canonical · Pod length **230 mm** (tandem) · ID 83 mm (XRP housing) |
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
| 49MHz RCRS dorsal | 365.8 mm from nose |
| Avionics | 8× PocketBeagle 2 (AM6232) · FC1–FC4 Cape-A · CN1–CN4 Cape-B |
| Navigation lights | ICAO Annex 2 · 14 CFR 91.209 · PCA9685 I²C PWM driver |
| FAA registration | **N00000 PLACEHOLDER — replace before flight** |

### Rev L Governor (New)

| Parameter | Value |
|-----------|-------|
| Governor | Per-EDF PID closed-loop RPM · 500 Hz (M4F coprocessor) |
| Feedback | BDSHOT RPM 1 kHz + BLHeli32 serial telem 10 Hz |
| PID gains (RPM) | Kp=3×10⁻⁴ · Ki=1×10⁻⁵ · Kd=8×10⁻⁵ |
| Nacelle equalization | FWD/AFT RPM matched · AFT +2% bias (inlet deficit) |
| Thermal derate | 85°C → linear derate to 0% cap at 110°C |
| Current limits | 80A soft (proportional) · 105A hard (latch) |
| Fault latch | Per-ESC · ground power cycle + GCS ack to clear |
| DSHOT channels | GP26–GP29 (PRU-ICSS 250 MHz) · freed GP29 via PCA9685 nav lights |
| Telem mux | 74HC4051 8:1 · MCP23017 3-bit select (SEL A/B/C) |

### Rev K → Rev L Changes

| Change | Rev K | Rev L |
|--------|-------|-------|
| Nacelle governor | Open-loop throttle pass-through | **PID closed-loop RPM per EDF + equalization** |
| M4F coprocessor | Unused for propulsion | **500 Hz governor loops** |
| Fault detection | Logged only | **Active latch + MAVLink + RTH** |
| Thermal derate | ESC firmware only | **Governor-level proportional derate** |
| EDF options | XRP only documented | **Budget / Standard / High-perf all documented** |
| Hardware | Dual-EDF Rev K | **Identical — firmware update only** |

### Rev J → Rev K Changes (historical)

| Change | Rev J | Rev K |
|--------|-------|-------|
| Nacelle EDF | 1× XRP per nacelle | **2× XRP tandem series per nacelle** |
| Nacelle ESC | 2× 120A total | **4× 120A (one per EDF)** |
| Nacelle thrust (each) | 2,900 g | **5,300 g** (+83%) |
| Total thrust | 6,450 g | **11,250 g** (+74%) |
| Nacelle pod length | 144 mm | **230 mm** (tandem) |
| Dry mass | 2,177 g | **3,197 g** (+1,020 g) |
| T/W empty | 2.49 | **3.12** |
| Max payload | 753 g | **1,406 g** (+87%)
