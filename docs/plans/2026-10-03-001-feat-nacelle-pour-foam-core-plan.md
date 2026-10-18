---
title: "feat: Pour-foam core for the 64 mm nacelle pod — weight reduction without loss of structural integrity"
type: feat
date: 2026-10-03
artifact_contract: ce-unified-plan/v1
artifact_readiness: implementation-ready
execution: code
depth: standard
---

**Owner:** Steve Griffing, PE(CSE), CISSP-ISSEP, CEH (GitHub `Stab-Rabbit-coding`) — request,
2026-10-03: "Plan for pour foam infill for non-heat sensitive areas if it will provide weight
reduction without losing structural integrity."
**AI contribution:** analysis and plan text by Claude (Claude Opus 5.5, Anthropic), per
`AGENTS.md` AI attribution.

---

## Goal Capsule

- **Objective:** Cut nacelle pod mass by replacing thick printed wall with a uniform printed skin
  plus a poured closed-cell foam core, only where the foam stays below its own and CF-PETG's
  temperature limits and only if the sandwich carries the pod's loads at least as well as the
  solid wall it replaces.
- **Authority:** owner decisions > `AGENTS.md` §7 fabrication standard (2.0 mm skins, 2 lb/ft³
  (32 kg/m³) closed-cell foam, void formers) > this plan.
- **Stop conditions:**
    - Stop if no foam product with a published density, compressive/shear strength, service
      temperature and cure exotherm can be catalogued in `REFERENCES.md`. Do not size against
      remembered values.
    - Stop if the structural check (U3) or the coupon test (U5) shows the sandwich below the solid
      wall's margin at any adopted load case.
    - Stop for owner decision before changing the forward-biased wall (U2): it reverses the
      2026-08-31 direction "take more from the forward end … to adjust CG".

## Why foam can save weight here — and where it cannot

Poured foam **adds** mass to an empty cavity: about 0.032 g/cm³ at 2 lb/ft³. It saves weight only
by **replacing denser printed material**. On the 64 mm pod
(`airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad`) that material is the forward-biased
wall, 2.5 mm forward ramping to 8 mm aft, which the pod carries for CG and load introduction. The
measured cavity and skin grids (`nacelle_hollow_profile.scad`, scaled 1.28× with the wall held)
give:

| Quantity | Value |
| --- | --- |
| Current 64 mm cavity | 12.65 in³ (207.3 cm³) |
| Cavity with a uniform 2.5 mm skin | 16.51 in³ (270.5 cm³) |
| Printed CF-PETG freed | 3.86 in³ (63.2 cm³), centroid Z 5.37 in (136.4 mm) |
| Printed mass removed (1.05 g/cm³ bulk) | 0.146 lbm (66.4 g) |
| Foam to fill the whole uniform cavity (32 kg/m³) | 0.019 lbm (8.7 g) |
| **Net per pod** | **−0.127 lbm (−57.7 g)**; −0.254 lbm (−115 g) per aircraft |
| PIVOT_Z effect (950 g assembly) | ≈ 0.11 in (2.9 mm) forward est.; hover clearance on the 3.0 in gear ≈ +0.84 in (+21 mm) est. |

Computed 2026-10-03 from the grids; `tools/nacelle_foam_core.py` (U1) makes it re-runnable.

## Heat-sensitive exclusions (foam-free, by void former)

Foam and CF-PETG both have temperature limits: CF-PETG heat deflection is 67 °C (152.6 °F)
[REF-MAT-002, Table 7]. Foam is excluded from:

- **ESC bays, covers, louvres and discharge ports.** These are heat sources and the aspirated
  cooling path.
- **The trunnion collar, register bore and ring-gear cavity.** Moving parts, the AK7455
  non-ferrous zone, and the pivot housing the hull WBS already excludes.
- **The 10 AWG disconnect bay, the nav channel and the phase-lead escape slots.** These are
  service paths (NAC-64-SVC-01); foam there would make the motors and harness irremovable.
- **The sleeve bores and the nozzle pocket.** The removable cartridges slide here.
- **Any region whose pour depth would put the cure exotherm above 67 °C at the CF-PETG wall.** U4
  sets the maximum lift height from the catalogued exotherm.

## Requirements

- **R1.** Net mass falls: printed mass removed minus foam added is greater than zero, measured on
  the rendered pod and on a weighed article.
- **R2.** Structural integrity holds. At every adopted load case (trunnion moment, EDF-2 thrust
  and torque into the aft sleeve seat, nozzle housing loads, hover/landing inertia), the
  skin-plus-foam sandwich has margin no lower than the solid wall it replaces. Check skin
  buckling, foam shear and core crushing.
- **R3.** No foam in any heat-sensitive or service region listed above. Void formers are derived
  from the pod mesh (CONCEPTS.md "Void Former").
- **R4.** The cure exotherm never raises the CF-PETG wall above 67 °C. Pour in measured lifts.
- **R5.** Vents and drains stay open. The pod must have no sealed voids (`AGENTS.md` §7 mesh
  rule).
- **R6.** Mass, CG and PIVOT_Z are re-derived by `tools/nacelle_mass_cg_64.py`, including the
  foam row, and hover clearance is re-checked.

## Implementation Units

### U1. Foam-core trade tool

**Files:** `tools/nacelle_foam_core.py` (new), with tests. It reads the cavity and skin grids and
the wrapper's RADIAL_K. It reports the freed printed volume per Z band, the foam volume, the net
mass and the CG shift for a chosen skin thickness, and it subtracts the void-former volumes.
**Verification:** it reproduces the table above for a 2.5 mm skin and no formers.

### U2. Owner decision: uniform skin aft of Z 100 (gate)

Present U1's result for skins of 2.0, 2.5 and 3.0 mm. Include the pivot shift, the hover-clearance
change and the load-introduction zones. **No geometry changes before this decision.**

### U3. Structural check of the sandwich

Use the project's adopted load cases (`docs/structural_analysis.md`) at the trunnion collar, the
aft-sleeve retention bosses and the nozzle pocket face. Apply sandwich-beam checks for face stress,
core shear, face wrinkling and local crushing under the M3 inserts. Use catalogued foam properties
(U4), and CF-PETG flexural strength from REF-MAT-002. Keep solid printed inserts (bosses, the
collar and a 3 mm minimum around every heat-set insert). If an allowable is missing, make a coupon
test a release gate.

### U4. Foam product selection and catalogue

Catalogue one 2 lb/ft³ two-part closed-cell pour foam in `REFERENCES.md` from its manufacturer
technical data sheet. It needs density, compressive and shear strength, service temperature,
expansion ratio and peak cure exotherm versus pour mass. Derive the maximum lift height from the
exotherm against the 67 °C limit. **No product or figure is cited until its data sheet is read.**
Until then this is a `REFERENCES.md` "requires verification" row plus a root TODO §0.x item.

### U5. Void formers, pour procedure and coupons

- Generate formers for each exclusion from the pod mesh.
- Write the pour order (lifts, cure intervals, vent orientation).
- Build two flat sandwich coupons and one aft-section segment, at the U2 skin thickness with the
  U4 foam. Test them in 3-point bending (ASTM D790 arrangement, matching REF-MAT-002) and insert
  pull-out against solid printed controls.
- **Pass:** each sandwich specimen at least matches its solid control, and its mass saving matches
  U1 within 10 %.

### U6. Integrate

Add a `FOAM_CORE` option to the pod wrapper. Re-run `nacelle_mass_cg_64.py` with the foam row,
iterate PIVOT_Z, and update the BOM (foam kit, formers) and WBS §1.1.4.

## Verification Contract

- U1 tests pass, and ruff is clean.
- The rendered pod validates as watertight, a single body, with no sealed void.
- U3 margins are at or above the solid-wall baseline at every load case.
- U5 coupons pass.
- `nacelle_mass_cg_64.py` converges, and the 3.0 in gear clears in hover.

## Scope boundaries

- Nacelle pod only. Hull foam is already planned (WBS Phase 4) and the wing is out of scope.
- Foam never replaces a fastener seat, bearing seat or load-introduction boss.
