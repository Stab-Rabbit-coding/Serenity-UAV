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

# Serenity-Class Tiltrotor UAV — Rev J (18" Canonical Build)

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Year:** 2026  |  **Status:** Public release

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

## Quick Specs (Rev J — 18" Scale)

| Parameter | Value |
|-----------|-------|
| Hull length | 457.2 mm (18.00") · Canon 269 ft |
| Canonical beam (tip-to-tip) | 288.9 mm (11.375") · Canon 170 ft |
| Canonical height (landed) | 134.3 mm (5.286") · Canon 79 ft |
| Canon source | QMx Official Blueprints, Mandel/Earls 2007 |
| Hull structure | PETG thin shell + X-30 foam + CF skeleton |
| Propulsion | 2× Changesun XRP 3660-2700KV 80mm 6S EDF nacelle · 1× XFLY X4 PRO 40mm 4S fuselage |
| Nacelle pod ID | **83 mm** (XRP 2700KV housing OD) · Pod OD 93.5 mm canonical |
| Nacelle tip-to-tip | 288.9 mm (11.375") — CANONICAL |
| Nacelle C-to-C | 195.9 mm (7.71") |
| Pylon datum from CL | 82.5 mm (1/3 from nacelle inner edge) |
| Arm stub | 10.4 mm hull edge → nacelle inner edge |
| Nacelle thrust (each) | **2,900 g @ 6S · 84A · 1,864W** (XRP 2700KV) |
| Fuselage thrust | 650 g @ 4S · 30A (XFLY X4 PRO 5850KV) |
| Total hover thrust | **6,450 g** |
| Airframe dry mass | 1,884 g |
| AUW empty (6S 4000mAh 410g) | **2,294 g (5.05 lb) · T/W 2.81** |
| AUW cargo 250g (6S 2800mAh 295g) | **2,429 g (5.36 lb) · T/W 2.66** |
| Max payload (T/W=2.0) | **1,046 g (2.31 lb)** |
| CG target | 190 mm (7.48") from nose |
| GPS patch | 59.4 mm from nose |
| SiK 915MHz belly | 253.7 mm from nose |
| 49MHz RCRS dorsal | 365.8 mm from nose |
| 8-node avionics | Nodes 1–4: 77–283 mm from nose |
| Navigation lights | ICAO Annex 2 · 14 CFR 91.209 |
| FAA registration | **N00000 PLACEHOLDER — replace before flight** |

### Rev I → Rev J Changes

| Change | Rev I | Rev J |
|--------|-------|-------|
| Nacelle EDF | Freewing 2836-2150KV | **Changesun XRP 3660-2700KV** (highest KV for 80mm 6S) |
| Nacelle ESC | 50A BLHeli32 | **Hobbywing Platinum PRO V4 120A** (mandatory — XRP draws 84A) |
| Nacelle thrust (each) | 1,700 g | **2,900 g** (+71%) |
| Total thrust | 4,050 g | **6,450 g** (+59%) |
| Nacelle pod ID | 80 mm (nominal) | **83 mm** (XRP housing OD) |
| Dry mass delta | — | +624 g (EDF +466g, ESC +158g) |
| T/W empty | 2.38 | **2.81** |
| Max payload | 462 g | **1,046 g** |
