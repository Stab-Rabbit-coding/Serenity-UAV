# Serenity UAV — Graphical Build Guide

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev S (2026-07-04)

> Step-by-step visual assembly guide for Serenity UAV, organized by build phase (0–10).
> SVG diagrams, checklists, and mechanical callouts for each major assembly milestone from
> printing all parts through autonomous flight operations.

## Guide Organization

The graphical build guide is organized by **build phase**, each corresponding to major system
integration checkpoints:

| Phase | Title | Stage | Status | Key Tasks |
|-------|-------|-------|--------|-----------|
| **0** | Print All Parts + CF Cuts | Fabrication | Open | STL export, calibration, cutting carbon-fiber components |
| **1** | Hull Structure + Provisions | Assembly | Open | Keel bonding, ring frames, cable routing, access panels |
| **2** | Nacelle Assembly | Assembly | Open | EDF installation, nozzle iris, gearing, hall encoder |
| **3** | Tilt Mechanism | Assembly | Open | Pivot rod, servo installation, hard stops, synchronization |
| **4** | Hull Foam Pour + Close-up | Fabrication | Open | Foam fill, panel lid installation, final hull closure |
| **5** | Minimum Viable Flyer | Flight Testing | Open | First 4-node avionics, ESC calibration, tethered hover ★ |
| **6** | Full 8-Node Architecture | Flight Testing | Open | All 8 nodes, Ethernet ring, ToF obstacle avoidance |
| **7** | Cargo System | Flight Testing | Open | Gondola installation, winch, door servo, delivery mission |
| **8** | Finishing | Documentation | Open | Decals, airworthiness inspection, documentation archive |
| **9** | Performance Tuning | Flight Testing | Open | Thrust stand, PID governor, endurance testing |
| **10** | Advanced Autonomy + LR Ops | Flight Testing | Open | BVLOS comms, 10-waypoint missions, node failover validation |

★ = Critical path to first flight (Phase 5)

Phases 11+ (aft EDF, cargo-bay battery module) are deferred. See [`deferred/`](../deferred/) directory.

## SVG Diagram Organization

### Overview Diagrams (Component-Level)

Located in root of this directory:

| SVG File | Content | Purpose |
|----------|---------|---------|
| `overview_port_view.svg` | Side view (port nacelle visible) | Dimensional reference, external profile |
| `overview_stbd_view.svg` | Side view (stbd nacelle visible) | Dimensional reference |
| `overview_isometric.svg` | 3D isometric view | Proportional understanding, nacelle tilt |
| `overview_exploded.svg` | Component breakdown (major assemblies) | Assembly sequence overview |
| `components_overview.svg` | All procured + printed + machined parts | BOM cross-reference |

### Phase-Specific Build Guide Cards (`build_guide_XX_*.svg`)

Numbered sequence of detailed assembly steps:

| Range | Type | Coverage |
|-------|------|----------|
| `00–04` | Fabrication prep | Phase 0: printing, calibration, carbon-fiber cuts |
| `05–08` | Hull & structure | Phase 1: keel, ring frames, cable routing, access panels |
| `09–15` | Subsystem integration | Phases 2–4: nacelles, tilt, nozzle, landing gear |
| `16–18` | Avionics & wiring | Phase 5: ESC power, node placement, inter-board wiring |
| `19–25` | Comms & sensing | Phase 6–7: antenna placement, ToF sensors, cargo system |
| `26+` | Flight operations | Phases 8–10: calibration, pre-flight, autonomous missions |

### Referenced Standard Files

- `flight_phases/build_guide_flight_phases.svg` — Overview of Phases 5–10 flight testing sequence
- `LEGEND.svg` — Color coding, symbol reference, callout format
- `REVN_BUILD_GUIDE_24IN.md` — Detailed text supplement (dimensions, fastener specs, epoxy cure times)

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

The original SVG files are hand-drawn in Inkscape with:

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

**Status:** Partial. The outline-derivation pipeline (`airframe/blender-scripts/gen_hull_outlines.py`)
currently covers 4 overview SVGs; the 26+ build-guide cards remain hand-drawn.

**Task 1.5.6 (Documentation)** plans to rebuild all 38 SVGs from Blender/FreeCAD-derived geometry.

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

## File Status & Maintenance

### Phase 0 (Fabrication)

- ✅ `build_guide_00_cover.svg` — Title page (updated 2026-07-15)
- ✅ `build_guide_01_print_prep.svg` — Calibration, filament, settings (current)
- ✅ `build_guide_02_print_hull.svg` — Hull printing sequence (current)
- ✅ `build_guide_03_print_nacelle.svg` — Nacelle printing (current)
- ✅ `build_guide_04_carbon_cuts.svg` — CF rod / skid channels (current)

### Phase 1–4 (Assembly)

- ✅ `build_guide_05_keel_bond.svg` — Keel installation (current)
- ✅ `build_guide_06_nacelle_pivot.svg` — Pivot mechanism (current)
- ✅ `build_guide_07_tilt_servo.svg` — Servo linkage (current)
- ✅ `build_guide_08_nozzle_gear.svg` — Nozzle iris gearing (current)
- ⚠️ `build_guide_09_avionics.svg` — **STALE** (depicts old Cape-A-1/B-1, not Rev S Wash/Zoë)

### Phase 5–7 (Electrical & Flight)

- ⚠️ `build_guide_10_power_wiring.svg` — **NEEDS REVIEW** (PDC harness updated; diagram may be stale)
- ⚠️ `build_guide_11_inter_board.svg` — **STALE** (old cape depictions)
- ⚠️ `build_guide_12_security_hw.svg` — **STALE** (TPM placement, old capes)
- ⚠️ `build_guide_13_nav_lights.svg` — **NEEDS REVIEW** (WS2812C light placement)
- ✅ `build_guide_14_antennas.svg` — 49 MHz antenna placement (current)
- ✅ `build_guide_15_ground_test.svg` — Bench testing (current)
- ✅ `build_guide_16_calibration.svg` — ESC & servo calibration (current)
- ✅ `build_guide_17_ground_test.svg` — Pre-flight checklist (current)
- ✅ `build_guide_18_first_flight.svg` — First flight profile (current)

### Phase 8+ (Finishing & Advanced)

- ⚠️ `build_guide_19_decals.svg` — **PLACEHOLDER** (FAA registration number pending)
- ⚠️ `build_guide_20_node_placement.svg` — **STALE** (old cape depictions)
- ⚠️ `build_guide_21_node_install.svg` — **STALE** (old cape depictions)
- 🔲 `build_guide_22_cargo_system.svg` — **PENDING** (Phase 7 cargo assembly)
- 🔲 `build_guide_23_obstacle_avoidance.svg` — **PENDING** (Phase 6 ToF sensors)
- 🔲 `build_guide_24_autonomous_mission.svg` — **PENDING** (Phase 9 mission planning)
- 🔲 `build_guide_25_obstacle_sensors.svg` — **PENDING** (ToF array placement)

### Status Summary

| Status | Count | Action |
|--------|-------|--------|
| ✅ Current | 12 | No action needed |
| ⚠️ Stale (Cape-A/B-1 depictions) | 7 | Regenerate from Rev S Wash/Zoë schematics (task 1.5.6) |
| ⚠️ Needs review | 2 | Verify against current design, re-render if needed |
| 🔲 Pending | 4 | Create new diagrams as phases progress |

**Overall:** ~30% of diagram set needs updating (7–9 out of 26 active cards).

## License

All SVG files and derivative graphics are **CC BY 4.0**.

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for details.

---

*"The world is worth fighting for." — Capt. Malcolm Reynolds*
