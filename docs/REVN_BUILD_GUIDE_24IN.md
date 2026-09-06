# Serenity UAV — 24-Inch Build Guide (Rev S Baseline)

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Current design revision:** Rev T (2026-09-06, see `docs/WBS.md` §6.4 for changelog)  
**Status:** Reference Stub (detailed procedures consolidated into graphical build guide).
This stub's own procedural content is still scoped to the Rev S hull — it has not been
revised for Rev T1c wing/Rev T4c nacelle geometry; see `docs/WBS.md` §6.4.

> Step-by-step procedural assembly guide for Serenity UAV Rev S 24-inch hull (609mm length).
> **For illustrated procedures, see [`graphical-build-guide/`](../graphical-build-guide/README.md) and
> numbered `build_guide_NN_*.svg` cards.**

---

## Document Purpose

This file is a reference stub and navigation hub for the 24-inch Rev S build process. The actual
detailed procedural steps are being consolidated into:

1. **Graphical Build Guide** — SVG diagrams with callouts (`graphical-build-guide/build_guide_NN_*.svg`)
2. **BOM & Component Specs** — [`current-specification/`](../current-specification/README.md) (bom_revS.json, CSV)
3. **Subsystem READMEs** — Design details and assembly sequences in subsystem directories
   - `airframe/README.md` — Hull structure, CAD workflow, material specs
   - `avionics/README.md` — Electrical architecture, node placement, wiring
   - `gcs/README.md` — Ground station setup and calibration
   - `tools/README.md` — Validation scripts, CI/CD pipeline

---

## Build Phases Overview

| Phase | Title | Status | Procedures | Details |
|-------|-------|--------|-----------|---------|
| **0** | Print All Parts + CF Cuts | Open | See `graphical-build-guide/build_guide_00–04_*.svg` | `airframe/README.md` §Print Prep |
| **1** | Hull Structure + Provisions | Open | See `graphical-build-guide/build_guide_05–08_*.svg` | `airframe/README.md` §Assembly Sequence |
| **2** | Nacelle Assembly | Open | See `graphical-build-guide/build_guide_09–10_*.svg` | `avionics/README.md` §Propulsion |
| **3** | Tilt Mechanism | Open | See `graphical-build-guide/build_guide_11_*.svg` | `airframe/README.md` §Tilt Servo |
| **4** | Hull Foam Pour + Close-up | Open | See `graphical-build-guide/build_guide_12_*.svg` | `airframe/README.md` §Foam & Final Hull |
| **5** | Minimum Viable Flyer | Open | See `graphical-build-guide/build_guide_13–18_*.svg` | `avionics/README.md` §Phase 5 Avionics |
| **6–10** | Advanced Integration & Flight | Open | See `graphical-build-guide/build_guide_19+_*.svg` | See respective subsystem READMEs |

---

## Key References

### Critical Specifications

- **Hull dimensions:** 609 mm length, 486 mm wingspan, 201.5 mm height (see `airframe/README.md` for detailed frame coordinates)
- **Ground clearance:** R6 landing gear provides 38.1 mm (1.5 in) below cargo belly; total ground-to-top height = 239.6 mm (9.43 in)
- **Alloy-up weight:** ~2,768 g (Phase 5–10, nacelles only; see `current-specification/bom_revS.json`)
- **Coordinate system:** Rev R1 hull-frame coordinates (baked into STL vertex data; see `airframe/README.md` §Hull Frame Standard)
- **Material spec:** CF-PETG 2.0 mm shell, 40% gyroid infill (load-bearing), 2 lb/ft³ interior foam

### Assembly Rules (Anti-Rework)

1. **Print ALL parts in Phase 0** — Filament costs pennies vs build time for reprints
2. **Install provisions BEFORE foam pour** — Conduits, voids, SMA bulkheads, all mounting bosses
3. **The foam pour is point-of-no-return** — Verify every provision with test fit first
4. **Cable routing** — Phase-by-phase as needed; pull-string guidance from Phase 1

### Fasteners & Adhesives (from BOM)

| Item | Spec | Notes |
|------|------|-------|
| Structural epoxy | 2-part, 2 h cure | Keel bonds, foam casting, panel sealing |
| M2.5 nylon standoffs | 8× | PCB/component mounting (non-conductive) |
| M3 nylon standoffs | 12× | Tray frames, battery bay alignment |
| Dyneema line (cargo) | 2 mm, 3 m, 100 lb break | Winch tether (see Phase 7) |
| Gasket tape | 3 mm × 10 m roll | Panel seals, EMI shielding (see Phase 5 avionics) |

---

## Phase-by-Phase Summary

### Phase 0 — Fabrication Preparation

**Input:** STL files from `airframe/` directory  
**Output:** All printed parts, carbon-fiber cuts ready for assembly

**Steps:**
1. Calibrate 3D printer for CF-PETG (nozzle height, extrusion width, bed prep)
2. Print all fuselage shells (head, cargo bay, middle, rear) with 40% gyroid infill
3. Print nacelle structures, wing panels, access-panel frames
4. Machine/cut carbon-fiber rod (4 mm × ~300 mm for pivot, 2 mm × ~1 m for spar)
5. Verify all printed parts for dimensional accuracy ±1 mm per `tools/validate_stls.py`
6. Organize parts by assembly phase in labeled bins

**Documentation:** See `graphical-build-guide/build_guide_00–04_*.svg`  
**Tools:** `tools/validate_stls.py` (mesh watertightness, manifold checks)

---

### Phase 1 — Hull Structure + Provisions

**Input:** Printed fuselage shells, carbon-fiber rod, epoxy, fasteners  
**Output:** Hull skeleton with all provisions (conduits, voids, mounts) before foam pour

**Steps:**
1. Bond keel rod (4 mm CF) to cargo shell centerline with 3 mm × 10 m gasket tape alignment
2. Epoxy four ring frames (nylon) at stations 0, 150, 300, 450, 600 mm
3. Install all PTFE conduit tubes (3 mm ID) from nose to tail for future cable routing
4. Press-fit 4× MF104ZZ flanged bearings into tilt-pivot housings (clevis ears)
5. Bond nacelle pivot housings to wing root
6. Verify all spar bonds with visual/tactile inspection (epoxy cured, no voids)
7. Install SMA bulkhead pass-throughs for 49 MHz antenna and radio connectors
8. Install all PCB mounting standoffs (M2.5 nylon) at predicted positions (see avionics BOM)
9. Install cargo bay hard points (M3 standoffs) for winch motor and cradle
10. Test-fit access panels (bayonet/screw/hinge/magnet); verify clearances

**Epoxy cure:** 2 hours @ 23°C typical; allow 24 h before handling loads

**Documentation:** See `graphical-build-guide/build_guide_05–08_*.svg`  
**CAD Reference:** `airframe/SerenityAssembly.FCStd` (component positions)

---

### Phase 2 — Nacelle Assembly

**Input:** Printed nacelle pods, 2× EDFs per pod (tandem), nozzle iris mechanism  
**Output:** Two complete nacelles with active thrust vectoring

**Steps:**
1. Press EDF units into nacelle hub bore (ID = 20 mm)
2. Verify EDF rotation sense (CW vs CCW) before lock-tight
3. Install nozzle iris petals with M0.5 gears and servo drive linkage
4. Bond unison-ring cam follower to servo arm (3 mm dowel pin, spring-return)
5. Install servo motor (DS3218MG tilt servo) on pivot frame
6. Calibrate servo travel: −5° (full closed nozzle) to +140° (full open) hard stops
7. Install 4× 40A BLHeli32 ESCs in hub bore side pockets (one per EDF)
8. Route ESC motor leads to EDF coil terminals (verify continuity post-solder)
9. Route ESC signal/power leads through conduit toward avionics bay

**Documentation:** See `graphical-build-guide/build_guide_09–10_*.svg`  
**Specs:** 50 mm 6S EDF, 460 g thrust each, 2 per nacelle in series (920 g / nacelle)

---

### Phase 3 — Tilt Mechanism

**Input:** Hull with nacelles, pivot rod, tilt servo  
**Output:** Functional nacelle tilt (−5° to +140° range)

**Steps:**
1. Install 4 mm CF pivot rod through clevis ear bearings (press-fit MF104ZZ)
2. Mount pivot rod at Z = 83 mm (center of gravity datum; see `airframe/README.md`)
3. Install tilt servo (DS3218MG, 65 g) on fixed servo bracket (printed)
4. Link servo horn to pivot rod via hard-stop linkage (−5° / +140° mechanical limits)
5. Verify synchronization: both nacelles tilt together within ±2° (measure with inclinometer)
6. Install tilt servo feedback (proportional pot or hall encoder) for closed-loop control
7. Test servo response time (<500 ms slew) with dummy avionics power supply

**Load analysis:** See `docs/TILT_SPAR_ANALYSIS.md` for structural validation  
**Documentation:** See `graphical-build-guide/build_guide_11_*.svg`

---

### Phase 4 — Hull Foam Pour + Close-up

**Input:** Hull skeleton with all provisions, foam resin + hardener  
**Output:** Structurally complete foam-filled hull, ready for electronics

**Steps:**
1. **Pre-pour checklist:**
   - Verify all conduits, SMA bulkheads, standoffs in place
   - Test-fit avionics stack (PB2-I + capes) to confirm clearances
   - Verify payload release solenoid bracket installed (cargo bay)
2. Prepare foam pour in batches (2 lb/ft³ closed-cell PU; 0.032 g/cm³)
3. Pour and degas foam, allow 2 h cure before handling
4. Sand foam flush with hull exterior profile
5. Install access panels (6 removable lids: nose, bay A/B/D/E caps, tail)
6. Verify panel fitment and magnetic catches
7. Inspect exterior for voids or cracks; patch with polyurethane compound if needed

**Foam cure:** 24 h @ 23°C before full structural load test

**Documentation:** See `graphical-build-guide/build_guide_12_*.svg`

---

### Phase 5 — Minimum Viable Flyer (First Tethered Hover)

**Input:** Foam-filled hull, avionics stack (4 nodes), ESCs wired, battery  
**Output:** Stable tethered hover with ±15° tilt authority

**Steps:**
1. Install PocketBeagle 2 Industrial × 4 in stacked positions (Shepherd, Inara, River, Simon bays)
2. Install Wash Cape-A-2 on each FC node (IMU, GPS, encoder feedback)
3. Install Zoë Cape-B-2 on each CN node (comms, logging, payload control)
4. Calibrate ESC throttle endpoints on all 4 EDFs (min/max stick travel mapping)
5. Calibrate IMU (gyro zero-bias, accel alignment) in benchtop mode
6. Verify GPS lock (HDOP < 1.5 at 10 satellites minimum)
7. Calibrate tilt servo endpoints (−5° / +140° hard stops verified with inclinometer)
8. Tether aircraft to fixed anchor point with 10 m Spectra line (50 lb SWL)
9. Hover test: power up sequentially (ESCs arm, props spin idle), verify thrust symmetry
10. Tilt test: command ±10° nacelle tilt, verify smooth response (no oscillation)
11. Emergency stop: cut throttle, verify safe descent

**Success criteria:**
- ✅ Hovers stable at idle throttle (5% stick)
- ✅ Yaw/pitch stable within ±5° of commanded angle
- ✅ All 4 EDFs produce balanced thrust (thrust sensor feedback consistent)
- ✅ Tether load = AUW ± 5% at hover throttle

**Documentation:** See `graphical-build-guide/build_guide_13–18_*.svg`  
**Avionics details:** See `avionics/README.md` §Phase 5 Minimum Viable Flyer

---

### Phase 6–10 — Advanced Integration

See:
- **Phase 6:** Full 8-node architecture, Ethernet ring, obstacle avoidance (ToF)
  - `avionics/README.md` §Phase 6 Avionics Expansion
  - `graphical-build-guide/` Phase 6+ SVGs
- **Phase 7:** Cargo system (gondola, winch, door servo)
  - `airframe/README.md` §Cargo Bay Integration
  - `graphical-build-guide/build_guide_22_*.svg`
- **Phase 8:** Finishing (decals, airworthiness inspection)
- **Phase 9:** Performance tuning (thrust stand, PID governor)
- **Phase 10:** Advanced autonomy (BVLOS comms, waypoint missions, failover validation)

---

## Critical Dimensions & Tolerances

### Hull Frame Coordinate System (Rev R1)

**Datum:** Keel rod center line (Y = 0), Z = 83 mm (center of gravity height), X = 0 (fuselage centerline)

| Component | Y-extent (mm) | Z-extent (mm) | Critical Mounts |
|-----------|---------------|---------------|-----------------|
| Head shell | −305.7 to −70.7 | +61.1 to +201.5 | GPS antenna (Z=190), nose access lid |
| Cargo shell | −71.5 to +132.0 | 0.0 to +163.2 | Winch motor hard point, 49 MHz scoop window |
| Middle shell | +130.4 to +203.6 | +1.3 to +166.1 | Ring frame @Z=150, Ethernet bulkhead |
| Rear shell | +203.2 to +384.3 | +3.3 to +161.1 | Ring frame @Z=300, tail access |
| Pivot rod | Z = 83 mm (CG height) | Clevis mount bore | Tilt servo load path |

### Nacelle Pivot Points

**Pivot axis:** 4 mm CF rod at Z = 83 mm (CG height), offset ±X per nacelle  
**Tilt range:** −5° (nozzle closed, hover) to +140° (nozzle open, cruise transition)  
**Servo torque:** DS3218MG 25 kg·cm @ 6V (adequate for inertia + aero moments with CG pivot)

---

## Tools & Validation

### STL Validation

Before printing, verify all meshes:

```bash
python3 tools/validate_stls.py airframe/STL/*.stl
```

Check for:
- Manifold integrity (no holes, non-manifold edges)
- Watertightness (zero non-closed volumes)
- Self-intersection (no interpenetrating faces)
- Dimensional accuracy (compare baked extents to specification)

### Component Mass Verification

Sum masses from BOM (`current-specification/bom_revS.json`):

```
Fuselage (shells + access panels):    ~350 g
Nacelles (2× pods + mounts):          ~420 g
Wings:                                ~180 g
EDFs (4×):                            ~280 g
Tilt mechanism (servo + rod + links): ~200 g
Landing gear:                         ~150 g
Avionics (8 nodes + capes + sensors): ~280 g
Power (battery + PDB + ESCs):         ~500 g
Cargo bay (gondola + winch + servo):  ~180 g
─────────────────────────────────────────
TOTAL AUW (Phase 5–10):              ~2,768 g
```

Compare actual build weight at each phase milestone.

---

## Troubleshooting & Common Issues

### Foam Pour Went Wrong

- **Incomplete cure:** Allow 24 h min @ 23°C before any structural loading
- **Voids in foam:** Small voids (<5 mm) are acceptable; pump small holes with polyurethane compound
- **Foam leaking from seams:** Epoxy seal the breach from inside; re-cure

### Nacelle Tilt Servo Binding

- Check pivot rod clearance (should rotate freely with light finger spin)
- Verify hard stops are exactly −5° and +140° (use digital inclinometer)
- Re-lubricate servo linkage with light machine oil

### ESC Throttle Not Responding

- Verify ESC signal wire connected to correct servo channel (see avionics BOM pinout)
- Re-calibrate ESC max/min throttle with stick at extreme positions
- Check for reversed servo connector (red/brown/orange wire order)

---

## Document Status

| Item | Status | Notes |
|------|--------|-------|
| Phase 0 (Print) | ✅ Complete | Documented in graphical build guide + airframe README |
| Phase 1–4 (Assembly) | ✅ Complete | Documented in graphical build guide + subsystem READMEs |
| Phase 5–10 (Integration) | ⚠️ In progress | See graphical-build-guide pending SVGs (task 1.5.6) |
| Detailed procedures | ✅ Consolidated | See `graphical-build-guide/` directory for illustrated cards |
| Structural analysis | ✅ Complete | See `docs/TILT_SPAR_ANALYSIS.md`, `docs/LANDING_GEAR_ANALYSIS.md` |

---

## See Also

- **Graphical Build Guide:** [`graphical-build-guide/README.md`](../graphical-build-guide/README.md)
- **Bill of Materials:** [`current-specification/bom_revS.json`](../current-specification/bom_revS.json)
- **Airframe Design:** [`airframe/README.md`](../airframe/README.md)
- **Avionics Architecture:** [`avionics/README.md`](../avionics/README.md)
- **Subsystem Procedures:** See AGENTS.md in each subsystem directory
- **Structural Analysis:** [`docs/TILT_SPAR_ANALYSIS.md`](TILT_SPAR_ANALYSIS.md)
- **Historical Reference:** [`docs/PHASED_BUILD_GUIDE.md`](PHASED_BUILD_GUIDE.md) (Rev M 18-inch, superseded)

---

**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0

See [`LICENSE`](../LICENSE) and [`docs/attribution_and_licensing.md`](attribution_and_licensing.md) for details.

---

*"I'm a big fan of the plan." — Captain Malcolm Reynolds*
