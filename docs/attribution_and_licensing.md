# Serenity UAV — Attribution and Licensing Policy

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Scope:** Project-wide licensing split, subsystem `LICENSE` federation, and the CERN-OHL-W
2.0 "Available Component" IP boundary around upstream canonical-reference geometry.
**Status:** Rev 1 — 2026-08-01 (closes TODO.md §0.9 "Licensing Updates" items 1–6)

> This file is the **policy** document — the split, the reasoning, and the federation map.
> For the full **per-asset** remix/attribution chain (every upstream model, author, and
> license, with remix-attribution text blocks), see
> [`current-specification/LICENSE_AND_ATTRIBUTION.md`](../current-specification/LICENSE_AND_ATTRIBUTION.md).
> For the standards-catalog entries, see `REFERENCES.md` REF-LIC-001/002 and Part XIV
> (REF-CAD-002/003/004).

---

## 1. The dual-license split

All original work in this repository is © Steve Griffing, PE(CSE), CISSP-ISSEP, CPP, released
under **two** licenses depending on content type — there is no single project-wide license:

| Content type | License | Full text |
|---|---|---|
| Hardware / CAD / PCB design files — airframe SCAD/STL/FCStd (wings, nacelles, landing gear, cargo system, fuselage, all other original airframe components), avionics KiCad schematics/PCB layouts/Gerbers (Pilot, XO, Flight Engineer, Commo, Observer, CAN-PERIPH-GW-1) | **CERN-OHL-W 2.0** (CERN Open Hardware Licence v2, Weakly Reciprocal) | `LICENSE` (root), `LICENSES/CERN-OHL-W 2.0` |
| Documentation, code, scripts, drawings, and all other non-hardware items — build guides, firmware/tooling source, SVG diagrams, specifications, this file | **CC BY-SA 4.0** (Creative Commons Attribution-ShareAlike 4.0 International) | `LICENSES/CC-BY-SA 4.0`, <https://creativecommons.org/licenses/by-sa/4.0/> |

Rationale: CERN-OHL-W is purpose-built for hardware design files (it defines "Source,"
"Product," "Make," and "Available Component" in hardware terms that CC licenses don't
address), and its weak-reciprocity means using an unmodified board or part in a larger
product does not pull the whole product under the license — appropriate for PCBs and
airframe components others may want to integrate into different builds. CC BY-SA keeps
documentation, firmware specs, and build guides under the same share-alike terms the
project's upstream CC BY-SA source (the misubisu hull model, REF-CAD-004) already carries,
which also resolves the license-compatibility question in §3 below.

This supersedes the plain "CC BY 4.0, all original work" statement that appeared in earlier
`AGENTS.md`/`README.md`/`REFERENCES.md` revisions — root `LICENSE` and `avionics/LICENSE`
already carried the full CERN-OHL-W 2.0 text before this policy document was written; §1
here documents that state rather than changing it, and the other files have been corrected
to match (root `AGENTS.md` §3, `README.md` "License", `REFERENCES.md` "Project license (this
work)").

**Not covered by either license** (third-party terms apply, see
`current-specification/LICENSE_AND_ATTRIBUTION.md` "Third-Party Software and Firmware" for
the full list): third-party commercial hardware (EDFs, ESCs, PocketBeagle 2, etc.), SiK radio
firmware (GPL-3.0), ArduPilot/QGroundControl/Mission Planner (GPL-3.0), tpm2-tools/tpm2-tss
(BSD-2-Clause), the CPLD write-blocker Verilog RTL (separately MIT licensed).

---

## 2. Subsystem `LICENSE` federation map

Every subsystem folder carries its own `LICENSE` file so a reader who clones or copies just
that folder still has correct terms without needing the repo root. Each subsystem file is a
**short header naming its scope**, followed by the applicable license's full text (mirroring
the pattern `avionics/LICENSE` already established) — never a bare pointer, so the file is
self-contained and license-scanner-friendly.

| Folder | License | Basis |
|---|---|---|
| `airframe/` | CERN-OHL-W 2.0 | Wings, nacelles, landing gear, cargo system, fuselage — all original hardware/CAD |
| `avionics/` | CERN-OHL-W 2.0 | PCB schematics/layouts/Gerbers (already in place; header added 2026-08-01 for consistency) |
| `docs/` | CC BY-SA 4.0 | Documentation, standards references, build/compliance records |
| `gcs/` | **Mixed** — CERN-OHL-W 2.0 (Skipper enclosure/gimbal STLs, comms-node hardware) + CC BY-SA 4.0 (firmware, Python control scripts, docs) — both stated in one `LICENSE` file since the folder is genuinely mixed | `gcs/skipper/` contains both hardware and software |
| `tools/` | CC BY-SA 4.0 | Build-automation Python/Blender/FreeCAD scripts — code, not hardware |
| `current-specification/` | CC BY-SA 4.0 | Active specs, BOM, revision `.jsx` design documents |
| `graphical-build-guide/` | CC BY-SA 4.0 | Build guide, SVG fabrication diagrams |
| `deferred/` | **Mixed** — CERN-OHL-W 2.0 (Phase 11 aft-EDF SCAD/STL hardware) + CC BY-SA 4.0 (docs) | `deferred/aft-edf/` contains hardware design files alongside its README |

Root `LICENSE` (CERN-OHL-W 2.0 full text, unmodified for license-scanner detection) plus this
file together are the parents every subsystem `LICENSE` federates from — per subsystem file,
a one-line pointer back to both (see §4 for the exact header template used).

---

## 3. Available Component boundary (CERN-OHL-W 2.0 §1.6)

The airframe's hull/nacelle/wing/landing-gear geometry traces back to three external
canonical-accuracy sources (full detail: `REFERENCES.md` Part XIV, "Canonical-accuracy
reference hierarchy"; `current-specification/LICENSE_AND_ATTRIBUTION.md` §1a/§2/§2c). Each
sits in a different position relative to the project's CERN-OHL-W 2.0 Covered Source, and
mixing them up would blur the IP boundary — so each is classified explicitly:

| Source | REF-ID | License | Boundary treatment |
|---|---|---|---|
| misubisu — "Serenity Firefly with landing gear and swivel engines" (Thingiverse Thing 7330462) | REF-CAD-004 | **CC BY-SA 4.0** | **Available Component**, CERN-OHL-W 2.0 §1.6 — a component not itself licensed under CERN-OHL that is legitimately referenced/incorporated without relicensing. This is the actual geometric origin of the project's `s_*`-lineage STLs (hull, nacelle, wing, landing-gear shells). The project's own adaptation (scaling, hollowing, CF skeleton/foam-fill, structural redesign) is original CERN-OHL-W 2.0 Covered Source; the upstream mesh keeps its own CC BY-SA 4.0 terms, and any redistribution of the *upstream* geometry itself (not the project's derivative Covered Source) must stay CC BY-SA 4.0 share-alike. |
| Nick Henning render collection | REF-CAD-002 | Permission-based (not CC-licensed) | **Reference-only — outside the Covered Source boundary entirely.** No mesh, CAD model, or proprietary geometry from the author is redistributed; used only as visual reference imagery for wing/landing-gear surface detail, under a direct email permission grant (2026-07-06), not as an Available Component. |
| QMx *Official Serenity Blueprints Reference Pack* (2007) | REF-CAD-003 | Copyrighted commercial product — NOT CC-licensed, NOT open | **Reference-only — outside the Covered Source boundary entirely.** Retained in-repo for internal design reference only; no page, image, or derivative is redistributed under any open license or treated as an Available Component. Most-authoritative canonical-accuracy source, but never incorporated into Covered Source. |
| BamJr — "Variable Area EDF Nozzles" (Thingiverse Thing 2991269) | — | CC BY 4.0 | **Available Component**, CERN-OHL-W 2.0 §1.6, same treatment as REF-CAD-004 — nozzle mechanism concept incorporated into original nacelle/fuselage nozzle Covered Source; upstream concept keeps CC BY 4.0 terms. |

**Clean IP boundary rule:** only sources that are themselves openly licensed (CC BY / CC
BY-SA) are ever integrated as Available Components into CERN-OHL-W Covered Source. The two
copyrighted/permission-only sources (QMx, Nick Henning) never cross that boundary — they
inform design decisions and geometry verification, but no line of their content is
redistributed, referenced as a component, or claimed as licensed material in this project.

---

## 4. Subsystem `LICENSE` header template

Each subsystem `LICENSE` file (§2) opens with a short header before the full license text:

```text
Serenity UAV — <folder> — License

Scope: <one-line description of what this folder's original content is>.
License: <CERN-OHL-W 2.0 | CC BY-SA 4.0 | Mixed, see below>.

This file federates from the project root LICENSE and
docs/attribution_and_licensing.md (the dual-license policy and the
CERN-OHL-W 2.0 Available Component boundary for upstream reference
geometry). Third-party components and Available Components referenced
from this folder keep their own terms — see REFERENCES.md and
current-specification/LICENSE_AND_ATTRIBUTION.md for the full chain.

---

<full license text>
```

---

## 5. Open Source Hardware certification

Preparing this project for OSHWA self-certification is tracked separately in
[`docs/OSHW_CERTIFICATION.md`](OSHW_CERTIFICATION.md) (TODO.md §0.9 item 7) — see REF-LIC-002.
Certification itself requires the human maintainer (Steve Griffing) to submit the
Certification Mark License Agreement; this repository can only get the documentation ready.

## 6. Board naming (resolved 2026-08-01)

TODO.md §0.9 item 8, "Rename avionics boards to non-trademarked names," was initially flagged
open (2026-08-01) because it conflicted with the then-canonical Firefly-character naming table
in root `AGENTS.md` §9, referenced across ~284 files. The user subsequently supplied
replacement role names and directed the rename to proceed, including the physical KiCad
project files/folders (unverified in this environment — no `kicad-cli` available; the
maintainer should confirm ERC/DRC on each board before trusting it for fabrication).

The six boards are now named **Skipper** (GCS), **Pilot** (flight control/sensor cape), **XO**
(comms/logging/payload cape), **Flight Engineer** (power distribution board), **Commo** (49 MHz
+ LoRa transceiver cape), and **Observer** (cargo-handling/vision/ToF/laser board) — generic
role names, no longer Firefly character names. The four avionics bay names (Shepherd's Room,
Inara's Shuttle, River's Room, Simon's Medbay) were **not** renamed. See root `AGENTS.md` §9
for the live naming/role table and `docs/WBS.md` §0.9 for the work item.

### 6.1 Naming history (TODO.md §0.9, closed 2026-08-01)

Relocated here from root `AGENTS.md` §9, which points at this subsection.

The six board names above (Skipper, Pilot, XO, Flight Engineer, Commo, Observer) are
**generic role names**, chosen 2026-08-01 to replace the project's original Firefly-character
board names (TODO.md §0.9 item 8 — avoiding trademark exposure on hardware that "may be
offered commercially beyond this project," root `AGENTS.md` §3). The four bay names (Shepherd's
Room, Inara's Shuttle, River's Room, Simon's Medbay) were **not** part of that rename and are
unchanged.

For attribution completeness (root `AGENTS.md` §3 — "derivative files carry the full
attribution chain"), the original names and their inspiration are recorded here rather than on
the live table in root `AGENTS.md` §9, since restating the character quotes next to the new
generic names would just re-attach the same recognizable Firefly branding the rename was meant
to remove:

| Current name | Former name | Inspiration | Firefly line |
|---|---|---|---|
| Skipper | Malcolm ("Mal") | Malcolm Reynolds, captain | "I aim to misbehave." |
| Pilot | Wash | Hoban "Wash" Washburne, pilot | "I'm a leaf on the wind." |
| XO | Zoë | Zoë Washburne, first mate | "Big Damn Heroes, sir." |
| Flight Engineer | Kaylee | Kaylee Frye, ship's mechanic | "Everything is shiny." |
| Commo | Emma | — (not a character name) | — |
| Observer | Jayne | Jayne Cobb, hired muscle | "She's a good gun." |

This table is historical only — do not use the former names anywhere in new work. See
`docs/WBS.md` §0.9 for the full renaming record.

---

*This document is released under CC BY-SA 4.0.*
