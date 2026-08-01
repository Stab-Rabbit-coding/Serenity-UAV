# Serenity UAV — Airframe Subsystem

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev S (2026-07-04)

> Structural design, 3D CAD, STL generation, and fabrication guidance for the Serenity UAV
> airframe: 24-inch CF-PETG printed fuselage, carbon-fiber wings with tilt-drive nacelles, and
> integrated landing gear.

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

- **X-axis:** +port (lateral); origin at centerline
- **Y-axis:** +aft (longitudinal); origin at nose
- **Z-axis:** +dorsal (vertical); origin at keel
- **Reference origin:** SerenityAssembly.FCStd world origin

All primary component STLs are **baked to hull frame** by `tools/bake_hull_frame.py` (header
marker: `SerenityUAV HULL-FRAME R1`); component positions are embedded in the STL vertex data.
See `AGENTS.md` "Airframe Geometry" for the validated component placement extents table.

## Structure Overview

| Section | Role | Length | Key Features |
|---------|------|--------|--------------|
| **Head** | Nose cone + sensor mount | ~90 mm | Bow sensor pod apertures; cockpit cap (GPS antenna access) |
| **Cargo Bay** | Payload + winch + door actuation | ~150 mm | Gondola shell; clamshell doors; STS3215 winch mount; DRV8833 H-bridge tray |
| **Middle / Neck** | Avionics + power + fuel (battery) | ~230 mm | Horseshoe ring frame; Kaylee PDB mount; battery bay; 4× avionics bays (A–D); foam fill; keel rod |
| **Rear** | Tail cone + tail boom | ~140 mm | Optional Phase 11 aft-EDF intake; twin rear-nozzle pods; landing-gear hard points |
| **Wings** | Port + stbd lift surfaces | 486 mm span (19.1 in) | Carbon-composite skin + foam core; tilt-servo mounts at roots; spar pocket inserts |
| **Nacelles** | Two tilting propulsion pods | ~200 mm each | 50 mm tandem EDF pair (X-Fly Galaxy X5, 12-blade, 3200 kV); variable-nozzle iris; tilt pivot (MF104ZZ bearing + 4 mm CF rod) |

## Mass Budget (Phase 5–10, Nacelles Only)

| Component | Mass (g) | Mass (oz) | Notes |
|-----------|----------|-----------|-------|
| Fuselage (printed) | ~350 | 12.3 | Includes all sections, access panels, bosses |
| Wings | ~180 | 6.3 | Span 486 mm, spar + skin, no cargo nacelles |
| Nacelle assembly (2× complete: EDFs + shells + pivot + iris) | ~625 | 22.0 | Includes 4× XFly Galaxy X5 (70g mass each), shells, hubs, pivot, iris mechanism |
| Tilt mechanism (servos, linkage, frame) | ~200 | 7.1 | 2× DS3218MG digital metal-gear servos (≥25 kg·cm @ 6V), rods, brackets |
| Landing gear (wire + mounts) | ~150 | 5.3 | 4130 steel wire, epoxy-bonded |
| Avionics (all 8 nodes, capes, TPM, SD cards) | ~280 | 9.9 | Includes cable, connectors |
| Power (battery + PDB + ESCs) | ~500 | 17.6 | 6S 4000 mAh LiPo + Kaylee PDB + 4× 40A BLHeli32 ESCs |
| Cargo bay internals (gondola, door, winch, servo) | ~180 | 6.3 | STS3215 servo winch, ratchet, latch, Dyneema line |
| Payload bay (empty) | — | — | Rated for 226 g (8 oz) cargo |
| **Total AUW** | ~2,768 | ~97.6 | Phase 5–10 (no aft EDF) |
| **Phase 11 addition (aft EDF, RCS)** | ~+362 | ~+12.8 | 55 mm EDF, RCS solenoids/valves, rear nozzle housing |
| **AUW Phase 11** | ~3,130 | ~110.4 | Full system with rear propulsion |

Thrust: 4,464 g (9.84 lbf) nacelles-only; T/W ≈ 1.61 (VTOL capable).

## Printing Specifications

**Material:** CF-PETG (carbon-fiber-filled polyethylene terephthalate)  
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
| `freecad-scripts/serenity_assembly.py` | FreeCAD Python script to regenerate/modify assembly | SerenityAssembly.FCStd | Updated FCStd, exported STLs, mass report |
| `blender-scripts/serenity_render_views.py` | Blender Python script (headless) to render isometric/cardinal views for build guides | STL geometry | PNG/SVG silhouettes for graphical build guide |
| `freecad-scripts/` (SCAD generators) | OpenSCAD → STL pipeline for non-printable parts (e.g., FreeCAD sketch exports, legacy compatibility) | *.scad scripts | *.stl files |

## STL Outputs

All generated STLs go to `stls/` subdirectories by section:

- `stls/fuselage/` — head_shell24.stl, cargo_sect_shell24.stl, middle_canonical_shell24.stl, rear_shell24.stl, access panels
- `stls/nacelles/` — nacelle_pod_50mm_tandem.stl (×2), nacelle_nozzle_iris.stl (×2), hub assemblies
- `stls/wings/` — wings_s1223_revo.stl (×2)
- `stls/landing_gear/` — [CF rod channels, bushing bosses embedded in fuselage; wire is procured]
- `stls/internals/` — battery_tray.stl, kaylee_pdb_tray.stl, avionics_bay_frames, cable_clips, bosses

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

- **Standards:** [REF-ISO-001] ISO 527-2 (polymers mechanical testing), [REF-ASTM-001] ASTM
  F963-17 (toy safety), [REF-AMS-001] AMS 2301 (electroplating standard)
- **Regulatory:** [REF-FAA-001] 14 CFR Part 48 (sUAS registration), [REF-FAA-002] Part 107
  (remote pilot cert)
- **Design reference:** [REF-CAD-001] QMx 2007 Firefly blueprints, [REF-CAD-002] Nick Henning
  Serenity renders, [REF-CAD-003] misubisu Thingiverse model (CC-BY-SA 4.0)

See root [`REFERENCES.md`](../REFERENCES.md) for complete reference catalog.

## License

**Airframe CAD, SCAD, STL files, and scripts:** CERN-OHL-W 2.0  
**Documentation:** CC BY 4.0  
**Third-party CAD references:** [REF-CAD-002] [REF-CAD-003] (see REFERENCES.md for license chains)

See root [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](../docs/attribution_and_licensing.md)
for full licensing details.

---

*"She's got a lot of spirit. You can't crush her." — Capt. Mal Reynolds*
