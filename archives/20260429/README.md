<!-- OpenDyslexic font for screen reading (CC BY 4.0) -->
<link rel="stylesheet" href="https://fonts.cdnfonts.com/css/opendyslexic">
<style>
body, p, li, td, th, code, pre {
  font-family: 'OpenDyslexic', 'OpenDyslexicMono', sans-serif !important;
  line-height: 1.8;
  letter-spacing: 0.03em;
}
/* Screen: dark background, high-contrast light text */
@media screen {
  body { background: #0d1117; color: #e6edf3; }
  a    { color: #58a6ff; }
  code { background: #161b22; color: #e6edf3; padding: 2px 6px; border-radius: 4px; }
  pre  { background: #161b22; padding: 12px; border-radius: 6px; }
  th   { background: #21262d; color: #79c0ff; }
  tr:nth-child(even) td { background: #161b22; }
  h1,h2,h3 { color: #58a6ff; border-bottom: 1px solid #30363d; padding-bottom: 6px; }
  blockquote { border-left: 4px solid #388bfd; color: #8b949e; padding-left: 12px; }
}
/* Print: light background, dark text, conserve ink */
@media print {
  body { background: #ffffff !important; color: #111111 !important; }
  a    { color: #003399 !important; }
  h1,h2,h3 { color: #000000 !important; }
  code,pre  { background: #f5f5f5 !important; color: #111111 !important; border: 1px solid #cccccc; }
  tr:nth-child(even) td { background: #f9f9f9 !important; }
}
</style>

# Serenity-Class Tiltrotor UAV

**Author:** Steve Griffing, PE(CSE) [Control Systems Engineering], CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/  
**Year:** 2026

> Fan engineering work inspired by the Firefly-class transport ship *Serenity*  
> from *Firefly* (Fox, 2002) and *Serenity* (Universal, 2005).  
> © Joss Whedon / Mutant Enemy Productions / Universal Pictures  
> **Not an officially licensed product.**

---

## Repository Contents

| Directory | Count | Contents |
|-----------|-------|----------|
| `diagrams/` | 27 | SVG engineering drawings + build guide + decal sheet |
| `pcb/` | 6 | KiCad 7.x PCB source files (3 boards) |
| `stl/` | 22 | 3D print files (ASCII STL) |
| `docs/` | 1 | License & attribution document |
| `artifacts/` | 11 | React/JSX interactive specification artifacts |

**Total: 69 files · 2,573,028 bytes**

---

## Quick Specs

| Parameter | Value |
|-----------|-------|
| Hull length | 365 mm (14.4") |
| Wingspan | 680 mm (26.8") |
| AUW — empty (rec.) | 1,002 g · 5S 4500mAh |
| AUW — cargo 250g (rec.) | 1,103 g · 5S 2800mAh |
| Nacelle thrust | 2× 70mm EDF · 1100g each · 2200g total |
| T/W (empty) | 2.20:1 |
| Cruise speed | 35–49 kts |
| Transition altitude | ≥26 ft AGL |
| SiK range | ≤1,094 yd LOS |
| RCRS range | ≤547 yd |

---

## Build Guide

The illustrated build guide (LEGO-style, 19 steps) is in `diagrams/build_guide_*.svg`.  
Open in any modern web browser or SVG viewer.

Steps:
1. Print preparation  6. Nacelle pivot & bearing  11. Inter-board wiring  16. Calibration
2. Print hull sections  7. Install 70mm EDF & LED  12. Security hardware  17. Ground test
3. Print nacelles & nozzle  8. Gear nozzle assembly  13. Navigation lights  18. First flight
4. Cut CF skeleton  9. Avionics installation  14. Antenna installation  **19. Decals ← NEW**
5. Assemble CF skeleton  10. Power wiring & ESCs  15. Software flash

---

## Decal Sheet

`diagrams/decal_sheet.svg` — Print on waterslide decal paper. Contains:

- **A**: SERENITY hull name lettering (port, starboard, nose, engine bell)
- **B**: FAA registration blocks — **REQUIRED** — replace N00000 with your issued number
- **C**: Firefly-universe markings (Alliance registry, 宁静 Chinese name, hull numbers, Companion Guild)
- **D**: Legally required safety labels (sUAS data plate, LiPo warning, operating limits, contact block)
- **E**: Weathering details, show-accurate stencils, fun Easter eggs

> **FAA Note:** Registration number N00000 is a placeholder. Aircraft registered under  
> 14 CFR Part 48 will receive an "FA" or "N" number from the FAA. Replace before first flight.

---

## Attribution

- **Hull:** "Serenity, Firefly Class" by Peter Farell — [printables.com/model/548545](https://www.printables.com/model/548545) · CC BY 4.0
- **Nozzle:** "Variable Area EDF Nozzles" by BamJr — [thingiverse.com/thing:2991269](https://www.thingiverse.com/thing:2991269) · CC BY 4.0
- **Visual inspiration:** *Firefly* (Fox, 2002) / *Serenity* (Universal, 2005)  
  © Joss Whedon · Tim Minear · Mutant Enemy Productions · Universal Pictures  
  Cast: Nathan Fillion, Gina Torres, Alan Tudyk, Morena Baccarin, Adam Baldwin, Jewel Staite, Sean Maher, Summer Glau, Ron Glass

See [`docs/LICENSE_AND_ATTRIBUTION.md`](docs/LICENSE_AND_ATTRIBUTION.md) for full details.

---

## File Integrity

All files are checksummed in `MANIFEST.json` (SHA-256).  
Verify with: `python3 -c "import json,hashlib; m=json.load(open('MANIFEST.json')); [print('OK',f['path']) for f in m['files'] if hashlib.sha256(open(f['path'],'rb').read()).hexdigest()==f['sha256']]"`

---

## Offline Viewer

An offline React viewer for the JSX artifacts is in `offline-viewer/`.  
See `offline-viewer/README.md` for setup instructions.

---

*CC BY 4.0 · 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP*
