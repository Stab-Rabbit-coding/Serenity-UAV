# Serenity UAV — Licensing & Attribution

**Document Status:** Current  
**Date:** 2026-08-01  
**License:** CC BY 4.0 / CERN-OHL-W (dual)

---

## Overview

Serenity UAV uses a **dual-licensing strategy** to accommodate different classes of deliverables:

| Category | License | Scope | Rationale |
|----------|---------|-------|-----------|
| **Hardware design** | CERN-OHL-W (Weakly Reciprocal) | CAD files, STLs, schematics, PCB layouts, bill of materials | Open hardware; improvements must be shared |
| **Documentation** | CC BY 4.0 (Creative Commons Attribution) | READMEs, build guides, specifications, design docs, verification reports | Permissive attribution model |
| **Software/Firmware** | (See individual files) | Embedded C/C++, Python scripts, firmware, GCS code | Currently MIT/GPL per file; see `firmware/LICENSE` and `tools/LICENSE` |
| **Graphical assets** | CC BY 4.0 | SVG diagrams, photos, render images | Permissive; creator attribution required |

---

## Canonical License Files

### Root License

**File:** [`LICENSE`](../LICENSE) (CERN-OHL-W v2)

This is the **primary license** for the Serenity UAV hardware design. All CAD, STL, schematic, and PCB files are covered under CERN-OHL-W unless explicitly marked otherwise.

**Key obligations under CERN-OHL-W:**
- Modifications must make source available
- Derivative designs must indicate changes (date + brief description)
- Documentation of changes required if product is conveyed
- Weak reciprocity: allows use of proprietary components/External Material with compatible interfaces

### Documentation & Graphics

Most documentation is covered under **CC BY 4.0**. See:
- [`docs/attribution_and_licensing.md`](attribution_and_licensing.md) — This file
- Individual file headers (e.g., READMEs, specifications)

**Key permissions under CC BY 4.0:**
- Free use, remix, and redistribution
- Commercial use allowed
- Must provide attribution to original author/licensor
- No trademark rights transferred

---

## Subsystem-Specific Licensing

### Airframe (`airframe/`)

| File Type | License | Notes |
|-----------|---------|-------|
| STL, FreeCAD, SCAD | CERN-OHL-W | Hardware design; reciprocal obligations apply |
| README.md, docs | CC BY 4.0 | Documentation attribution model |
| LICENSE | CERN-OHL-W | Pointer to root LICENSE |

**Key files:**
- `airframe/SerenityAssembly.FCStd` — Main CAD assembly (CERN-OHL-W)
- `airframe/AGENTS.md` — Design policy & standards (CC BY 4.0)
- `airframe/README.md` — Airframe design philosophy (CC BY 4.0)

---

### Avionics (`avionics/`)

| File Type | License | Notes |
|-----------|---------|-------|
| KiCad schematics (.sch, .kicad_pcb) | CERN-OHL-W | PCB designs; reciprocal obligations |
| Gerber files | CERN-OHL-W | Fabrication output; derived from schematics |
| README.md, docs | CC BY 4.0 | Documentation |
| Firmware source code | See `firmware/LICENSE` | C code; separate licensing (typically MIT/GPL) |
| LICENSE | CERN-OHL-W | Pointer to root LICENSE |

**Key files:**
- `avionics/wash-cape-r-s1.kicad_sch` — Wash PCB (CERN-OHL-W)
- `avionics/zoe-cape-r-s1.kicad_sch` — Zoë PCB (CERN-OHL-W)
- `avionics/kaylee-pdb-r-s1.kicad_sch` — Kaylee power distribution (CERN-OHL-W)
- `avionics/README.md` — Avionics architecture (CC BY 4.0)
- `avionics/AGENTS.md` — PCB policy & pinout standards (CC BY 4.0)

---

### Firmware & Software (`firmware/`, `tools/`)

| File Type | License | Notes |
|-----------|---------|-------|
| C/C++ source | MIT or GPL v3 (per file) | See `firmware/LICENSE` for details |
| Python scripts | MIT (typical) | See `tools/LICENSE` for details |
| Shell/build scripts | MIT or GPL v3 | Per file header |
| docs | CC BY 4.0 | Documentation |

**Key files:**
- `firmware/LICENSE` — Software licensing policy
- `tools/LICENSE` — Tools & scripts licensing policy
- Individual files carry `// SPDX-License-Identifier: MIT` or similar headers

---

### Ground Control Station (`gcs/`)

| File Type | License | Notes |
|-----------|---------|-------|
| Hardware (schematics, PCBs) | CERN-OHL-W | GCS-specific capes and carrier boards |
| Software (Malcolm firmware, UI) | MIT or GPL v3 | See `gcs/LICENSE` |
| Documentation | CC BY 4.0 | READMEs, guides, interfaces |
| Gimbal CAD | CERN-OHL-W | Mechanical gimbal design |

**Key files:**
- `gcs/README.md` — GCS overview (CC BY 4.0)
- `gcs/AGENTS.md` — GCS design policy (CC BY 4.0)
- `gcs/LICENSE` — Pointer and software-specific notes

---

### Graphical Build Guide (`graphical-build-guide/`)

**All SVG files and diagrams:** CC BY 4.0

SVG diagrams are **not** hardware source per se (they are derivative documentation), so CC BY 4.0 is appropriate. Attribution to the designer (embedded in SVG metadata) is required.

**Required attribution format in SVG files:**
```xml
<!-- Design by Serenity UAV Project; CC BY 4.0 -->
<!-- See docs/attribution_and_licensing.md for details -->
```

---

### Deferred Design (`deferred/`)

**Phase 11+ design documents:** CERN-OHL-W (same as main airframe)

Deferred-phase CAD and schematics follow the same licensing as the baseline hardware. Phase 11 aft EDF integration, Phase 12 cargo-bay battery module, and speculative future designs are all CERN-OHL-W.

**Documentation:** CC BY 4.0

---

### Current Specification & BOM (`current-specification/`)

| File Type | License | Notes |
|----------|---------|-------|
| bom_revS.json, CSV | CC BY 4.0 | Bill of materials; data documentation |
| Viewer code (JSX) | MIT | Interactive BOM viewer |
| README.md, docs | CC BY 4.0 | Specification documentation |

**Key files:**
- `current-specification/bom_revS.json` — Primary BOM source (CC BY 4.0)
- `current-specification/bom_revS.csv` — Flat-file export (CC BY 4.0)
- `current-specification/serenity-rev-s.jsx` — BOM viewer (MIT)

---

### Tools & Validation (`tools/`)

| File Type | License | Notes |
|----------|---------|-------|
| Python scripts (validate_*.py, update_*.py) | MIT | Validation and maintenance scripts |
| Bash/shell scripts | MIT | Build and test automation |
| FreeCAD/Blender scripts | MIT | CAD model generation and export |
| Documentation | CC BY 4.0 | Tool usage and CI/CD guides |

---

## Attribution Requirements

### For Hardware Designs (CERN-OHL-W)

When creating derivative or built products based on Serenity UAV, you must:

1. **Retain license notice** — Include "Licensed under CERN-OHL-W v2" on or in the product design
2. **Document modifications** — If you modify a design, add a notice stating:
   - Date of modification
   - Brief description of changes
   - Your name or identifier as modifier
3. **Make source available** — Modifications to the design source must be made available to others under the same license
4. **Retain this documentation** — Preserve links to this file and the root LICENSE

**Example modification notice (in KiCad schematic or SCAD comment):**
```
Modified 2026-09-15 by [Your Name]: Changed capacitor footprint from 0805 to 1206
for improved thermal stability. Licensed under CERN-OHL-W v2.
See https://github.com/[repo]/docs/attribution_and_licensing.md
```

### For Documentation (CC BY 4.0)

When reproducing or adapting documentation:

1. **Credit the author** — "Serenity UAV Project" or similar attribution
2. **Link to license** — Include link to CC BY 4.0 summary (https://creativecommons.org/licenses/by/4.0/)
3. **Indicate changes** — If you modify the documentation, note what was changed
4. **Preserve notices** — Keep license notices visible

**Example attribution (footer of adapted document):**
```
Based on Serenity UAV documentation (https://github.com/[repo]).
Original work by Serenity UAV Project, licensed under CC BY 4.0.
Modifications: [brief description], [date].
```

---

## Third-Party Components & External Material

### Procured Parts (BOM)

Purchased components (EDFs, servos, batteries, connectors, etc.) retain their manufacturers' licenses and warranties. Serenity UAV licensing does **not** apply to third-party parts.

**References:**
- `current-specification/bom_revS.json` — Supplier links and part numbers
- Individual component datasheets — Manufacturer copyright and license terms

### Embedded Libraries & Frameworks

- **FreeCAD** (CAD): LGPL v2+ (not linked; CAD file format is open)
- **Inkscape** (SVG editor): GPL v3 (not linked; SVG is open format)
- **KiCad** (EDA): CERN-OHL-W, GPL v3+ (EDA tool; schematic is open format)
- **Zephyr RTOS** (firmware base, if used): Apache 2.0 / MIT (specific file headers; see `firmware/LICENSE`)

### Documentation Sources

External references cited in [`docs/REFERENCES.md`](REFERENCES.md) are:
- Third-party academic papers (copyright holders retain rights; fair use applied)
- Datasheets and technical notes (supplier copyright; educational use permitted)
- Standards documents (IEC, IEEE, FAA) (purchased or public versions; limited reproduction)

**All citations include attribution and source URLs** per [`docs/REFERENCES.md`](REFERENCES.md).

---

## Compliance & Verification

### License Headers

All source files should carry appropriate headers:

**Hardware (CAD, schematics):**
```
Licensed under CERN-OHL-W v2
See root LICENSE file and docs/attribution_and_licensing.md
```

**Documentation (Markdown):**
```markdown
**License:** CC BY 4.0
See root LICENSE and docs/attribution_and_licensing.md
```

**Software (C/C++, Python):**
```c
// SPDX-License-Identifier: MIT
// See firmware/LICENSE (or tools/LICENSE) for details
```

### Verification Checklist

- ✅ Root LICENSE file (CERN-OHL-W) present and current
- ✅ Subsystem LICENSE files reference root LICENSE
- ✅ READMEs carry CC BY 4.0 notices
- ✅ CAD/schematic files documented as CERN-OHL-W (AGENTS.md)
- ⚠️ Software license headers need audit (firmware/LICENSE and tools/LICENSE to be verified)
- ✅ REFERENCES.md citations attributed and sourced
- 🔲 GitHub releases to include complete LICENSE text (pending CI/CD update)

---

## Legal Disclaimer

**This document is informational.** For authoritative legal interpretation of CERN-OHL-W or CC BY 4.0, consult:

- **CERN-OHL-W:** https://ohwr.org/cern_ohl_w_v2
- **CC BY 4.0:** https://creativecommons.org/licenses/by/4.0/legalcode

The authors of Serenity UAV provide this project "as-is" under the chosen licenses, with no warranty of fitness for a particular purpose. See LICENSE file for full disclaimer.

---

## Questions & Support

- **License interpretation:** See [`LICENSE`](../LICENSE) and https://ohwr.org/
- **CC BY 4.0 guidance:** https://creativecommons.org/licenses/by/4.0/
- **Contributing:** See root [`CONTRIBUTING.md`](../CONTRIBUTING.md) (if present) or open an issue

---

## Revision History

| Date | Rev | Change |
|------|-----|--------|
| 2026-08-01 | 1.0 | Initial comprehensive licensing & attribution guide (Task 0.6.2) |

---

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](attribution_and_licensing.md) for details.

---

*"The work is done in the open, so anyone can see how it's made." — Serenity UAV Project*
