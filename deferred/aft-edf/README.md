# Aft Fuselage EDF — Deferred to Phase 11

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Status:** DEFERRED — not archived; build pending after all other systems are proven.

> **STALE DESIGN — requires regeneration before Phase 11.** The files in this folder describe a
> superseded 120 mm EDF + 8-petal iris nozzle design. The current canonical fuselage EDF
> (per AGENTS.md) is a **55 mm 6S unit** feeding a **fixed** elliptical exit nozzle
> (2.06 in × 1.76 in / 52.3 mm × 44.7 mm — explicitly NOT an iris) plus 4 RCS bleed-air thrusters
> tapping ~15% of EDF mass flow. The OpenSCAD/STL files below have not yet been regenerated for
> this spec; see TODO.md §Phase 11 (`rear_nozzle_canonical.stl`, `rcs_thruster_nozzle.stl`,
> `rcs_distribution_manifold.stl`, `rcs_valve_bracket.stl`) for the replacement file list and
> required changes. Do not treat the 120 mm/iris description below as current.

## What This Is (legacy 120 mm design — see staleness notice above)

This folder holds all design files for the large fuselage (aft/rear) EDF system: the 120 mm
6S electric ducted fan mounted inside the engine bell section, fed by four radial intake scoops
at neck station ~310 mm via a CF-PETG intake frame ring and a PETG cross-shaped plenum manifold,
exhausting through an 8-petal iris variable-area nozzle at the aft end of the hull.

Per the project design philosophy (see AGENTS.md):
> "The large fuselage EDF … is now an optional addition once everything else works."

The nacelle EDFs (2× 50 mm tandem per nacelle) provide the primary propulsion.  The aft EDF adds
~3 500 g of additional thrust and is required for the full T/W of ~1.47 stated in the Rev Q specs.

**Baseline nacelle EDF:** XFly Galaxy X5 50mm 12-blade 6S 3200KV — **1240 g thrust per EDF**
(source: xfly-model.eu/en/edf-units/4833-…).  Per nacelle (2× tandem, 90% additive via stator):
1240 × 2 × 0.90 = **2232 g**.  Total nacelles (2×): **4464 g**.

**Aft EDF system deferred mass: ~840 g** (120mm EDF ~400g + 80A ESC ~130g + CF-PETG intake frame
~90g + PETG plenum ~80g + nozzle frame ~50g + 8 petals ~40g + servo/wiring/hardware ~50g).

**Revised Phases 5–10 AUW without aft EDF hardware:** ~2,768 g (down from ~3,608 g full build).

**Nacelle-only T/W (Phases 5–10):** 4,464 g / 2,768 g ≈ **1.61** — **full VTOL hover capable**.
The aft EDF is not required for hover; it raises the full-system T/W to ≈ **2.21** (7,964 g /
3,608 g), enabling heavier payload delivery, faster cruise speed, and better high-density-altitude
performance.

---

## File Inventory

### OpenSCAD source files (`openscad/`)

| File | Description |
|------|-------------|
| `rear_neck_intake_shell24.scad` | Rear hull neck section with 4 radial scoop window cutouts at station ~310 mm |
| `neck_intake_frame.scad` | CF-PETG structural intake frame ring; bonds into the 4 scoop windows |
| `aft_edf_plenum.scad` | Cross-shaped 4-to-1 PETG plenum manifold connecting intake arms to 120 mm EDF face |
| `edf_120_motor_mount.scad` | Motor mount ring for the 120 mm EDF inside Panel F |
| `edf_120_thrust_tube.scad` | Thrust tube / aft duct directing exhaust toward nozzle exit |

### STL files (`stls/`)

| File | Material | Notes |
|------|----------|-------|
| `neck_intake_frame.stl` | CF-PETG | Print at 0.15 mm / 40% gyroid / 4 walls |
| `aft_edf_plenum.stl` | PETG | Print at 0.20 mm / 20% gyroid; pressure-test before EDF install |
| `edf_120_motor_mount.stl` | CF-PETG | Motor mount ring |
| `edf_120_thrust_tube.stl` | CF-PETG | Thrust tube |
| `rear_nozzle_frame.stl` | CF-PETG | 8-rib structural nozzle ring; bonds to aft EDF duct exit |
| `rear_nozzle_petal.stl` | PETG + translucent-blue inner | Iris petal × 8 |
| `rear_nozzle_closed_asm.stl` | — | Assembly visualisation only; not printed |

---

## Build Sequence (Phase 11)

See the full Phase 11 build instructions in:
- `TODO.md` — Phase 11 section
- `docs/REVN_BUILD_GUIDE_24IN.md` — Phase 11 section

### High-level steps

1. Generate `rear_neck_intake_shell24.stl` from `openscad/rear_neck_intake_shell24.scad`
   (verify NECK_X station alignment in slicer — target ~310 mm from nose datum).
2. Replace the temporary Phase 0 rear neck hull section (if it was printed without windows)
   OR remove temporary window covers from the existing neck section.
3. Generate and print remaining STLs in `stls/` if not already done.
4. Install `neck_intake_frame.stl` into the 4 scoop windows (structural epoxy, 24 h cure).
5. Install `aft_edf_plenum.stl`; pressure-test before proceeding.
6. Bench-test 120 mm EDF (correct rotation, no vibration); install in plenum outlet.
7. Wire 80 A ESC in Panel F; route signal lead to FC2 PRU Ch.2.
8. Install `rear_nozzle_frame.stl` + 8 petals + piano wire link ring.
9. Install SG90 rear nozzle servo; calibrate: 0° = closed, ~90° = fully open.
10. Install aft 49 MHz (Part 15 §15.235) wire post on top of nozzle frame; extend 49 MHz top wire to aft hook.
11. Verify T/W with all 5 EDFs; commission full VTOL hover.

### Procurement (Phase 11)

| Item | Qty | Approx. Cost |
|------|-----|-------------|
| 120 mm 6S EDF | 1× | ~$60–80 |
| 80 A 6S BLHeli32 ESC | 1× | ~$25–35 |
| SG90 micro servo (rear nozzle) | 1× | ~$3 |
| 3 mm × 5 mm SS hinge pins | 8× | ~$2 total |
| 0.8 mm piano wire | ~200 mm | ~$1 |

---

## Notes on the Interim Build (Phases 0–10)

- The **hull neck shell** (`rear_neck_intake_shell24.stl`) still needs to be printed in Phase 0
  as it is a structural hull section.  The 4 scoop windows should be covered with temporary
  flat-plate covers (cut from 3 mm PETG sheet) and sealed with removable silicone for Phases 0–10.
  The covers are removed in Phase 11 when the intake frame is installed.
- The **49 MHz (Part 15 §15.235) aft wire post** (normally bonded to the top of `rear_nozzle_frame.stl`)
  is temporarily omitted.  For Phases 0–10 the 49 MHz antenna is a shorter end-fed wire from
  the forward post to a temporary hook bonded to the aft dorsal hull skin near station ~580 mm.
  The antenna performance is reduced; field strength must still be re-verified against the
  47 CFR Part 15 §15.235 limit (≈30 µW / −15.2 dBm EIRP-equivalent — not Part 95, which does
  not cover 49 MHz; see REF-FCC-003) with the shortened wire.
- The **Panel F bay** remains empty of EDF/ESC hardware until Phase 11.  Panel F still serves
  as an access panel; keep the bay clean and free of debris.

---

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*
