# Serenity UAV — Airframe Subsystem

**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)
**Last updated:** 2026-10-07

> Structural design, 3D CAD, STL generation, and fabrication guidance for the Serenity UAV
> airframe: 24-inch CF-PETG printed fuselage, carbon-fiber wings with tilt-drive nacelles, and
> integrated landing gear.

## Current Status (2026-10-07)

- **Hull:** all four fuselage SCAD shells are at the Rev S baseline and carry into Rev T
  unchanged. The cargo-shell mesh-validation defect (MESH-01) and several STL re-exports remain
  open (`TODO.md`, `fuselage-mid/TODO.md`).
- **TACCO envelope (2026-10-06):** the TACCO board grew to 60 × 35 mm, so the airframe
  stations were re-proved: nose Faraday tray 65 mm, cargo chin pouches 63 mm with a 1.5 mm
  static gap (`tools/cargo_layout_fit.py` Rev T5g), Simon's CN4 slot 63 mm
  (`tools/middle_layout_fit.py` Rev T6a). The printable STLs (`chin_node_shelf`,
  `simon_node_saddle`, `void_former_cargo_node_bay`, `head_shell24`) still need re-export
  (item TACCO-60); `tools/check_tacco_envelope_sync.py` reports them as pending.
- **Nacelles:** the 50 mm Rev S4c/S4d geometry is current. The 64 mm tandem-EDF nacelle
  (NAC-64-SERVO-01) is the active design: a servo-driven variable nozzle was designed and
  fit-closed 2026-10-04, and a uniform ×1.06 enlargement through a single source was wired
  2026-10-05. Pivot, CFD, mass/CG, and bench gates are open, so the 50 mm figures below stay the
  baseline until the 64 mm thrust, power, and mass verification passes.
- **Nozzle drive:** one sub-micro servo per nacelle (owner decision 2026-09-28) replaced the
  passive gear and linkage drives (`docs/NOZZLE_DRIVE_TRADE.md`).
- **Tilt drive:** Pololu 20D 25:1 motor with a six-start worm and a pin brake (Rev T5e,
  2026-09-16).
- **Landing gear:** the 3.0 in (76 mm) canonical leg is the flight article (2026-09-06); the
  1.5 in (38 mm) leg is retired to bench use (`docs/LANDING_GEAR_ANALYSIS.md`).
- **Cargo winch:** SPT5425LV with LibreServo v2 replaced the STS3215 on 2026-08-02; winch STL
  status is tracked in `fuselage-mid/WBS.md`.

## Design Philosophy

- **Printed structure:** All fuselage and nacelle shells (except landing-gear wire) are 3D-printed
  CF-PETG (carbon-filled polyethylene terephthalate) with 0.15 mm layer height, ≥4 perimeters,
  and ≥40% infill for load-bearing parts
- **Integrated provisions:** Cable runs, cooling ducting, battery bay, avionics racks, and
  mounting bosses are designed into the shell geometry; separate fastening is minimal
- **Watertight hull:** Outer shell hollow to 2.0 mm; interior foam-filled with 2 lb/ft³
  low-density polyurethane for buoyancy, flotation, and EMI shielding
- **Modular sections:** Four fuselage sections (head, cargo bay, middle neck/horseshoe ring,
  rear) plus wings and tilting nacelles allow field disassembly for transport and maintenance

## Coordinate Standard (Rev R1)

All design artifacts (SCAD, STL, Blender/FreeCAD scripts) use the **hull frame** coordinate
system:

- **X-axis:** +port (lateral)
- **Y-axis:** +aft (longitudinal); the nose tip is at Y ≈ −305.6 mm
- **Z-axis:** +dorsal (vertical)
- **Origin:** the `SerenityAssembly.FCStd` world origin

All primary component STLs are **baked to hull frame** by `tools/bake_hull_frame.py` (header
marker: `SerenityUAV HULL-FRAME R1`); component positions are embedded in the STL vertex data.
See `HULL_FRAME_REFERENCE.md` for the validated component placement extents table.

## Structure Overview

| Section | Role | Length | Key Features |
|---------|------|--------|--------------|
| **Head** | Nose cone + sensor mount | ~90 mm | Bow sensor pod apertures; cockpit cap (GPS antenna access) |
| **Cargo Bay** | Payload + winch + door actuation | ~150 mm | Clamshell doors; SPT5425LV/LibreServo v2 winch mount; DRV8833 H-bridge tray (the gondola shell was superseded 2026-09-15) |
| **Middle / Neck** | Avionics + power + fuel (battery) | ~230 mm | Horseshoe ring frame; Flight Engineer PDB mount; battery bay; 4× avionics bays (A–D); foam fill; keel rod |
| **Rear** | Tail cone + tail boom | ~140 mm | Optional Phase 11 aft-EDF intake; twin rear-nozzle pods; landing-gear hard points |
| **Wings** | Port + stbd lift surfaces | 486 mm span (19.1 in) | Carbon-composite skin + foam core; tilt-servo mounts at roots; spar pocket inserts |
| **Nacelles** | Two tilting propulsion pods | ~200 mm each | 50 mm tandem EDF pair (X-Fly Galaxy X5, 12-blade, 3200 kV; 64 mm redesign in progress); servo-driven variable nozzle; tilt pivot (MF104ZZ bearing + 4 mm CF rod) |

## Mass Budget (Phase 5–10, Nacelles Only)

| Component | Mass (g) | Mass (oz) | Notes |
|-----------|----------|-----------|-------|
| Fuselage (printed) | ~630 | 22.2 | 4 shells (head 83g + cargo 165g + middle 135g + rear 200g = 583g) + 3 joint splice collars (47g); bom_revS.json PRINT-HEAD-SHELL/PRINT-CARGO-SECT/PRINT-MIDDLE-CANONICAL/PRINT-REAR-NECK-INTAKE/PRINT-*-COLLAR |
| Wings | ~180 | 6.3 | Span 486 mm, spar + skin, no cargo nacelles |
| Nacelle assembly (2× complete: EDFs + shells + pivot + iris) | ~625 | 22.0 | Includes 4× XFly Galaxy X5 (70g mass each), shells, hubs, pivot, iris mechanism |
| Tilt mechanism (servos, linkage, frame) | ~200 | 7.1 | 2× SPT5425LV (converted with LibreServo v2, ≥25 kg·cm @ 6V), rods, brackets |
| Landing gear (wire + mounts) | ~436 | 15.4 | R6 canonical (1.5 in): leg+bay+foot 310g + wires 91g + pins/bolts 34g; see docs/LANDING_GEAR_ANALYSIS.md §11.6 (open item LG-18: target ≤300g pending mass-reduction pass) |
| Avionics (all 8 nodes, capes, TPM, SD cards) | ~432 | 15.2 | 8× PB2-I (104g) + 4× Pilot (124g) + 4× TACCO (160g) + Commo (Rev T: one standalone node, mass pending PCB roll-up; the two Rev S capes were 40g) + 4× microSD (4g); excludes cable/conduit |
| Power (battery + PDB + ESCs) | ~925 | 32.6 | 6S 4000 mAh LiPo (750g) + Flight Engineer PDB (75g) + 4× 40A BLHeli32 ESCs (100g) |
| Cargo bay internals (gondola, door, winch, servo) | ~180 | 6.3 | SPT5425LV winch servo (LibreServo v2), ratchet, latch, Dyneema line |
| Payload bay (empty) | — | — | Rated for 226 g (8 oz) cargo |
| **Total AUW** | ~3,911 | ~137.9 | Phase 5–10 (no aft EDF); corrected 2026-08-22 from a stale ~2,768g figure — see TODO.md §0.10.1 |
| **Phase 11 addition (aft EDF, RCS)** | ~+362 | ~+12.8 | 55 mm EDF, RCS solenoids/valves, rear nozzle housing |
| **AUW Phase 11** | ~4,273 | ~150.7 | Full system with rear propulsion |

Thrust: 9.84 lbf (4,464 g) nacelles-only; hover T/W ≈ 1.14 at 8.62 lbm (3,911 g) AUW — VTOL capable with a thin margin. The earlier 1.61 used the stale 2,768 g AUW. Phase 11 hover T/W is ≈ 1.04 at 9.42 lbm (4,273 g), because the rear EDF adds mass but no hover thrust. Both figures are provisional until the bottom-up AUW recompute closes (`docs/WBS.md` §0.10.1).

## Printing Specifications

**Material:** 20% CF-PETG (carbon-fiber-filled polyethylene terephthalate - 20% CF)  [REF-MAT-002]
**Nozzle temperature:** 240–250°C  
**Bed temperature:** 80–90°C  
**Layer height:** 0.15 mm (all parts)  
**Nozzle diameter:** 0.4 mm (hardened steel or tungsten carbide — CF abrades brass)  

**Shell design:**

- **Outer surface:** 2.0 mm hollow, watertight, no voids
- **Perimeters:** ≥4 (0.16 mm pitch) for structural integrity
- **Infill:**
  - Load-bearing parts (spar pockets, boss regions, tilt servo mounts): ≥40% gyroid
  - Non-structural (interior walls, access panels): 25% gyroid
- **Supports:** Print with support material; remove and sand smooth before assembly

**Post-print finishing:**

- Trim all support marks flush
- Epoxy-bond all section mating faces (2-part structural epoxy, 2 h cure)
- Fill voids with 2 lb/ft³ PU foam (inert, closed-cell, chemically neutral to CF-PETG)
- Sand outer mold line to ±0.5 mm if detail requires it (e.g., nacelle body fairings)
- Apply matte polyurethane clear coat (1–2 coats) for UV protection and dirt resistance

## Assembly Sequence (Phase 0–4)

See `graphical-build-guide/` for detailed visual assembly steps (SVGs + photos):

1. **Phase 0:** Print all parts; calibrate extrusion, pressure-advance, filament dry time
2. **Phase 1:** Bond keel, ring frames, access panels; install standoffs and cable runs
3. **Phase 2:** Assemble nacelles (EDFs, nozzle iris, gearing, hall encoder)
4. **Phase 3:** Install tilt mechanism (pivot rod, servo linkage, hard stops)
5. **Phase 4:** Foam pour and close hull; install access panel lids

Phases 5–10 add avionics, comms, cargo, and flight testing.

## CAD / Generation Scripts

| File / Tool | Purpose | Input | Output |
|-------------|---------|-------|--------|
| `freecad/assembly/SerenityAssembly.FCStd` | Master FreeCAD assembly (all components, bill of materials) | — | Placement reference, mass, CG, rendered views |
| `FreeCAD-scripts/serenity_assembly.py` | FreeCAD Python script to regenerate/modify assembly | SerenityAssembly.FCStd | Updated FCStd, exported STLs, mass report |
| `blender-scripts/serenity_render_views.py` | Blender Python script (headless) to render isometric/cardinal views for build guides | STL geometry | PNG/SVG silhouettes for graphical build guide |
| `FreeCAD-scripts/` (placeholder and flat-pattern generators) | OpenSCAD → STL pipeline for non-printable parts (e.g., FreeCAD sketch exports, legacy compatibility) | *.scad scripts | *.stl files |

## STL Outputs

All generated STLs go to `stls/` subdirectories by section:

- `stls/fuselage/` — head, cargo, middle, and rear shells; splice collars; access covers;
  wing-root flanges; battery tray; belly panel; bow sensor faceplate
- `stls/fuselage/cargo/` — cargo doors, hinges, latches, winch parts, FPV bezel, chin node shelf,
  tilt-actuator parts
- `stls/fuselage/landing-gear/` — landing-gear parts
- `stls/nacelles/` — 50 mm and 64 mm nacelle shells, trunnions, EDF sleeves and mounts,
  servo bracket; `esc/` and `nozzles/` subfolders
- `stls/wings/` — `wing_{port,stbd}_s1223_revo.stl`, tilt pinions

**Mesh validation:** All STLs are validated for watertightness, manifold topology, and correct
normals by `tools/validate_stls.py` before commit. Findings and any manual repairs are logged
in `TODO.md`.

## Documentation Files

| File | Purpose |
|------|---------|
| `AGENTS.md` | Airframe subsystem policy: design standards, coordinate system, fabrication specs |
| `WBS.md`, `TODO.md` | Work breakdown and open items (structures, CAD, STL generation, landing gear, cargo) |
| `fuselage-joints/WBS.md` | Bow sensor pod, fuselage-to-fuselage bond lines, access panel design |
| `fuselage-covers/WBS.md` | Access panel hinges, latch mechanisms, removable covers |
| `fuselage-mid/WBS.md` | Middle section (horseshoe ring), avionics bay layout, Kaylee PDB, cargo gondola, winch |
| `wings-nacelles/WBS.md` | Wing/nacelle pylon design, EDFs, nozzle iris, tilt drive mechanism |
| `landing-gear/WBS.md` | Wire selection, drop-height analysis, bay mounting, impact tests |

## References

- **Standards and materials:** [REF-ASTM-001] ASTM F2910-22 (sUAS design and construction),
  [REF-MAT-002] CF-PETG process-parameter study
- **Regulatory:** [REF-FAA-001] 14 CFR Part 48 (sUAS registration), [REF-FAA-002] Part 107
  (remote pilot cert)
- **Design reference** (authority order): [REF-CAD-003] QMx 2007 Official Serenity Blueprints
  Reference Pack, [REF-CAD-002] Nick Henning Serenity renders, [REF-CAD-004] misubisu
  Thingiverse model (CC BY-SA 4.0); [REF-CAD-001] BamJr variable-area EDF nozzle concept

See root [`REFERENCES.md`](../REFERENCES.md) for complete reference catalog.

## License

**Airframe CAD, SCAD, STL files, and scripts:** CERN-OHL-W 2.0  
**Documentation and images:** CC BY-SA 4.0  
**Third-party CAD references:** [REF-CAD-002] [REF-CAD-003] (see REFERENCES.md for license chains)

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full licensing details.

---

*"She's got a lot of spirit. You can't crush her." — Capt. Mal Reynolds*
