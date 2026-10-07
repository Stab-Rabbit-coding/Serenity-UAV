# Serenity UAV — Graphical Build Guide

**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)  
**Last updated:** 2026-10-07

> Step-by-step visual assembly guide for Serenity UAV, organized by build phase (0–10).
> SVG diagrams, checklists, and mechanical callouts for each major assembly milestone from
> printing all parts through autonomous flight operations.

## Current Status (2026-10-07)

The 27 numbered cards (`build_guide_00`–`26`), `build_plan.svg`, and `components_overview.svg`
are hand-drawn pre-Rev-T art. Their last commit (2026-10-04) only stamped the license. Nothing has
been rebuilt from Rev T geometry, and no phase has been built or tested (every phase below is
Open). Rev T changes the cards do not yet show: the worm-driven tilt actuator with a pin brake,
the servo-driven nacelle nozzle (the passive gear drive was retired 2026-09-28), the 64 mm
nacelle redesign, TACCO at 60 × 35 mm on male TSM-DV-LC rails, MIL-STD-1553C (HI-6138), mLRS
on a bare STM32WLE5JC, and the standalone Commo node. The rebuild is task 1.5.6 in `WBS.md`.
Per-card status is under "File Status and Maintenance" below.

## Guide Organization

The graphical build guide is organized by **build phase**, each corresponding to major system
integration checkpoints:

| Phase | Title | Stage | Status | Key Tasks |
|-------|-------|-------|--------|-----------|
| **0** | Print All Parts + CF Cuts | Fabrication | Open | STL export, calibration, cutting carbon-fiber components |
| **1** | Hull Structure + Provisions | Assembly | Open | Keel bonding, ring frames, cable routing, access panels |
| **2** | Nacelle Assembly | Assembly | Open | EDF installation, servo-driven nozzle, hall encoder |
| **3** | Tilt Mechanism | Assembly | Open | Pivot, worm-drive tilt actuator, pin brake, hard stops, synchronization |
| **4** | Hull Foam Pour + Close-up | Fabrication | Open | Foam fill, panel lid installation, final hull closure |
| **5** | Minimum Viable Flyer | Flight Testing | Open | First 4-node avionics, ESC calibration, tethered hover ★ |
| **6** | Full 8-Node Architecture | Flight Testing | Open | All 8 nodes, Ethernet ring, ToF obstacle avoidance |
| **7** | Cargo System | Flight Testing | Open | Cargo shell, winch, door servo, delivery mission |
| **8** | Finishing | Documentation | Open | Decals, airworthiness inspection, documentation archive |
| **9** | Performance Tuning | Flight Testing | Open | Thrust stand, PID governor, endurance testing |
| **10** | Advanced Autonomy + LR Ops | Flight Testing | Open | BVLOS comms, 10-waypoint missions, node failover validation |

★ = Critical path to first flight (Phase 5)

Phases 11+ (aft EDF, cargo-bay battery module) are deferred. See [`deferred/`](../deferred/) directory.

## SVG Diagram Organization

### Overview Diagrams (Component-Level)

Located in the root of this directory:

| SVG File | Content | Purpose |
|----------|---------|---------|
| `overview_front.svg`, `overview_side.svg`, `overview_top.svg`, `overview_bottom.svg` | Silhouettes from the 24 in hull | Dimensional reference, external profile |
| `hull_front.svg`, `hull_side.svg`, `hull_top.svg`, `hull_bottom.svg` | Hull outlines derived by `gen_hull_outlines.py` | Outline source for the overview views |
| `overview_svgs/serenity_*.svg` | Ten rendered views (port, starboard, bow, stern, top, bottom, four isometrics) | Proportional understanding |
| `pngs/01_port.png` … `17_closeup_nacelle.png` | Rendered stills used by the root README and cards | Visual reference |
| `components_overview.svg`, `build_plan.svg` | Parts map and master construction sequence | BOM cross-reference; build sequence |
| `decal_sheet.svg` | Decal artwork | Phase 8 |

### Phase-Specific Build Guide Cards (`build_guide_NN_*.svg`)

| Card | Topic |
|------|-------|
| `00`–`04` | Cover, print prep, hull print, nacelle print, CF cuts |
| `05`–`08` | CF skeleton, nacelle pivot, EDF install, nozzle gear |
| `09`–`13` | Avionics, power wiring, inter-board wiring, security hardware, nav lights |
| `14`–`18` | Antennas, software, calibration, ground test, first flight |
| `19`–`21` | Decal placement, node placement, node install |
| `22`–`24` | Void formers, foam fill, access panels |
| `25`–`26` | Obstacle sensors, cargo bay winch |

The mapping of cards to build phases is in `WBS.md`; the card numbering is the drawing
sequence, not necessarily the build sequence.

### Referenced Files

- `flight-phases/WBS.md`, `flight-phases/TODO.md` — Phases 5–10 flight-testing record
- `REVN_BUILD_GUIDE_24IN.md` — detailed text supplement (dimensions, fastener specs, cure times)
- `BUILD_GUIDE_TEMPLATE.md` — authoritative template for every phase guide

## File Naming Convention

All SVG filenames follow the pattern:

```
build_guide_NN_topic.svg
```

Where:
- `NN` = two-digit phase/step counter (00–99)
- `topic` = brief descriptor (e.g., `print_nacelle`, `power_wiring`, `antennas`)

Example: `build_guide_06_nacelle_pivot.svg` = Phase 3, step 6, covering nacelle pivot assembly

## Design & Content Standards

### Visual Style

- **Isometric projection** for 3D clarity (not perspective; consistent at all angles)
- **Color coding:** Printed parts (blue), procured parts (gray), electronic components (red), tools/fixtures (yellow)
- **Callouts:** Dimensioned where critical; cross-referenced to BOM and part specifications
- **Annotations:** Torque specs, epoxy cure times, clearance checks in adjacent text boxes

### Component Cross-References

Every part shown in a build-guide diagram includes:

1. **Part ID** (e.g., SYS-001, PWR-001) — links to BOM
2. **Quantity** — how many, how many per nacelle, etc.
3. **Material/Spec** — CF-PETG wall thickness, servo torque, bearing size
4. **Reference docs** — links to TILT_SPAR_ANALYSIS, NOZZLE_DRIVE_TRADE, etc.

### Standards Citations

Where applicable, each diagram includes:

- **Structural loads** (e.g., "hard stops at −5° per FAA Part 107 compliance")
- **Electrical specs** (e.g., "5V ±0.05V @ 1A" for servo rail)
- **Regulatory callouts** (e.g., "Part 15 §15.235 antenna clearance" for 49 MHz wire)

## Generation & Maintenance

### Source Format

The numbered cards are hand-drawn in Inkscape with:

- **No external image links** (all geometry is vector)
- **Embedded fonts** (system fonts may not render; uses SVG text elements)
- **Symbolic components** (reusable shapes for EDFs, servos, boards)

### Regeneration Pipeline

An automated refresh pipeline (currently under development, task 1.5.6):

```
FreeCAD/Blender (3D CAD) 
  ↓
Silhouette + dimensional export (SVG)
  ↓
Inkscape template overlay (callouts, BOM links)
  ↓
Final diagram (build_guide_XX_*.svg)
```

**Status:** Partial. The outline-derivation pipeline (`graphical-build-guide/gen_hull_outlines.py`)
currently covers the four `hull_*.svg` outlines; the numbered build-guide cards remain hand-drawn.

**Task 1.5.6 (Documentation)** plans to rebuild all 38 SVGs (a count that predates the current file set) from Blender/FreeCAD-derived geometry.

### Updating the Diagrams

1. **Minor text corrections** (e.g., typo, ref-ID addition):
   - Edit directly in Inkscape
   - Save as `.svg` (plain text format)
   - Commit to repo

2. **Geometry/component changes** (e.g., nacelle redesign affects diagram):
   - If Phase 11+: mark as "deferred" in diagram (cross-hatched background)
   - If Phase 0–10: regenerate from latest CAD (requires FreeCAD/Blender silhouettes)
   - Submit to task 1.5.6 pipeline for full rebuild

3. **Hardware deprecation** (e.g., old cape design):
   - Archive diagram to `archives/` (keep for historical reference)
   - Regenerate new version from current PCB design
   - Update `graphical-build-guide/WBS.md` to note archival

## Related Documentation

| File | Relationship |
|------|--------------|
| `docs/PHASED_BUILD_GUIDE.md` | Text-based phase descriptions; cross-references to SVG diagrams |
| `docs/REVN_BUILD_GUIDE_24IN.md` | Detailed procedural steps, torque specs, fastener lists, dimensions |
| `airframe/WBS.md` | CAD generation status for each STL / diagram source |
| `WBS.md` (root) | Phase 0–10 task breakdowns (integrated with SVG milestone names) |
| `graphical-build-guide/WBS.md` | Detailed work on diagram generation, rebuild pipeline, archive management |
| `graphical-build-guide/TODO.md` | Open diagram work (staleness of artwork, missing callouts, etc.) |

## File Status and Maintenance

Status is judged against the Rev T design and the grep of each card's text on 2026-10-07. A card
marked "Rev T review" has not been compared with Rev T and is unverified, not known-good.

| Status | Cards | Defect or action |
|--------|-------|------------------|
| Stale — superseded hardware | `build_guide_09_avionics`, `11_inter_board`, `12_security_hw`, `20_node_placement`, `21_node_install`, `build_plan`, `components_overview` | Show archived capes or 1553B and, in the last two, LoRa/RFM95 and iris/gear nozzle; regenerate (task 1.5.6) |
| Stale — retired mechanism | `build_guide_08_nozzle_gear` | The passive gear nozzle drive was retired 2026-09-28; redraw for the servo drive |
| Stale — LoRa | `build_guide_14_antennas` | Names LoRa/RFM95W; Commo no longer carries LoRa and TACCO carries mLRS |
| Stale — 1553B wording | `build_guide_15_software` | Change to 1553C when the hardware matches (`avionics/WBS.md` §1.2a.3) |
| Placeholder | `build_guide_19_decal_placement`, `decal_sheet` | FAA registration number is a placeholder; replace before flight |
| Rev T review | `00`–`07`, `10`, `13`, `16`–`18`, `22`–`26` | Verify against Rev T (tilt actuator, 64 mm nacelle, TACCO size, winch); re-render if affected |

**Overall:** 9 of the 27 numbered cards, plus `build_plan.svg` and `components_overview.svg`, need
correction or a rebuild before any phase begins. The hull outline pipeline (`gen_hull_outlines.py`, in this
directory) produces the four `hull_*.svg` outlines; all other cards are hand-drawn.

## License

All SVG files and derivative graphics are **CC BY-SA 4.0** (images are documents under the by-output rule).

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for details.

---

*"The world is worth fighting for." — Capt. Malcolm Reynolds*
