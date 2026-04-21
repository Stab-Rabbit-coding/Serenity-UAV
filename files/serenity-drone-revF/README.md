# Serenity-Class Tiltrotor UAV

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/

> Fan engineering work inspired by the Firefly-class transport ship *Serenity*  
> from *Firefly* (2002) and *Serenity* (2005).  
> © Joss Whedon / Mutant Enemy Productions / Universal Pictures  
> **Not an officially licensed product.**

---

## Repository Contents

```
serenity-drone/
├── README.md                          ← this file
├── docs/
│   └── LICENSE_AND_ATTRIBUTION.md     ← full license + attribution
├── diagrams/                          ← SVG engineering drawings
│   ├── overview_top.svg
│   ├── overview_side.svg
│   ├── overview_front.svg
│   ├── overview_bottom.svg
│   ├── components_overview.svg
│   └── build_plan.svg
├── pcb/                               ← KiCad 7.x PCB source files
│   ├── TRIHAT-1/
│   │   ├── TRIHAT-1.kicad_pcb        ← Pico 2 sensor hat 65×48mm
│   │   └── TRIHAT-1.kicad_sch
│   ├── CM4-CARRIER-1/
│   │   ├── CM4-CARRIER-1.kicad_pcb   ← CM4 carrier Rev E 65×52mm
│   │   └── CM4-CARRIER-1.kicad_sch
│   └── COMPHAT-1/
│       ├── COMPHAT-1.kicad_pcb       ← CM4 companion hat Rev E 65×48mm
│       └── COMPHAT-1.kicad_sch
└── stl/                               ← 3D print files (ASCII STL)
    ├── hull_*.stl                     ← Serenity hull sections (PETG)
    ├── nacelle_*.stl                  ← 70mm EDF nacelle pods (CF-PETG)
    ├── nozzle_*.stl                   ← BamJr remix nozzles (PETG/CF-PETG)
    ├── sector_gear_22mm.stl           ← Nacelle nozzle gear (PETG/resin)
    ├── tilt_bracket_cf_petg.stl       ← Nacelle pivot bracket (CF-PETG)
    ├── dorsal_antenna_fin.stl         ← 49MHz antenna fin (PETG)
    ├── payload_bay_door.stl           ← Belly door (PETG)
    ├── landing_skid_foot.stl          ← Skid pads (TPU 95A)
    └── cockpit_dome_clear.stl         ← Clear cockpit (clear PETG)
```

---

## Quick Specs

| Parameter | Value |
|-----------|-------|
| Hull length | 365 mm (14.4") |
| Wingspan | 680 mm (26.8") |
| AUW — empty (rec.) | 1,002 g · 5S 4500mAh |
| AUW — cargo 250g (rec.) | 1,103 g · 5S 2800mAh |
| Nacelle thrust | 2× 70mm EDF · 1100g each |
| T/W (empty) | 2.20:1 |
| Cruise speed | 35–49 kts |
| Transition altitude | ≥26 ft AGL |
| SiK range | ≤1,094 yd LOS |
| RCRS range | ≤547 yd |

---

## Attribution

- **Hull:** "Serenity, Firefly Class" by Peter Farell — [printables.com/model/548545](https://www.printables.com/model/548545) · CC BY 4.0
- **Nozzle:** "Variable Area EDF Nozzles" by BamJr — [thingiverse.com/thing:2991269](https://www.thingiverse.com/thing:2991269) · CC BY 4.0
- **Visual inspiration:** *Firefly* (Fox, 2002) / *Serenity* (Universal, 2005) · © Joss Whedon / Mutant Enemy Productions / Universal Pictures

See [`docs/LICENSE_AND_ATTRIBUTION.md`](docs/LICENSE_AND_ATTRIBUTION.md) for full details.

---

## KiCad PCB Notes

Open `.kicad_pcb` files in **KiCad 7.x or later**.  
Component placement is provided; routing is a starting point — complete DRC-clean routing in KiCad before fabrication.  
4-layer stackup: F.Cu (signals) · In1.Cu (+3V3 plane) · In2.Cu (GND plane) · B.Cu (signals).  
Order from JLCPCB / OSHPark at 4-layer 1oz Cu ENIG finish.

## STL Print Notes

| Filename | Material | Infill | Layer |
|----------|----------|--------|-------|
| hull_*.stl | PETG | 8% gyroid | 0.20mm |
| nacelle_*.stl | CF-PETG | 25% | 0.15mm |
| nozzle_*.stl | PETG | 20% | 0.20mm |
| sector_gear_22mm.stl | Resin or PETG | 40% | 0.10mm |
| tilt_bracket_*.stl | CF-PETG | 40% | 0.15mm |
| cockpit_dome_clear.stl | Clear PETG | 15% | 0.20mm |
| landing_skid_foot.stl | TPU 95A | 20% | 0.30mm |

> **Note:** Gear STLs are mathematically-generated approximations.  
> Refine tooth profiles in FreeCAD/Fusion 360 using a proper involute gear generator  
> (e.g., FreeCAD Gear workbench) before printing or sourcing commercial M0.5 gears.

---

*CC BY 4.0 · 2025 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP*
