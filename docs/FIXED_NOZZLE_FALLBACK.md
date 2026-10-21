# Fixed Open Nozzle — Weight-Cutting Fallback

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Status:** FALLBACK ONLY — not in the active design, BOM, or default build (2026-10-19)

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation must be
> independently reviewed and accepted by a licensed Professional Engineer or an
> equivalently qualified authority before it is applied to any system carrying
> risk to life or safety. Reference material provided AS-IS; not a sealed,
> certified, or reviewed work product.

## What this is

The active design uses the 64 mm nacelle with the servo-driven iris nozzle
(`airframe/openscad/nacelles/nacelle_nozzle_iris_64mm.scad`, plan
`docs/plans/2026-09-28-001-feat-nacelle-nozzle-servo-drive-plan.md` U11).

This file preserves the alternative that was designed and rendered for Rev T6 (2026-09-29): a
**one-piece fixed nozzle held at the hover (open) exit**, so that it does not have to be
re-invented if the iris has to be dropped to save weight.

## Files

| File | Purpose |
|---|---|
| `airframe/openscad/nacelles/nacelle_nozzle_fixed.scad` | Parametric source. Header explains the rationale and the geometry. |
| `airframe/stls/nacelles/nozzles/nacelle_nozzle_fixed.stl` | Rendered 50 mm part. Checked 2026-10-19 with trimesh: watertight, consistent winding, 32.15 cm³, extents 71.2 × 71.2 × 47.97 mm. |
| `docs/plans/2026-09-29-001-tw-recovery-stem-to-stern-plan.md` | The T/W analysis behind the decision (§6.1, D-TW-3 / D-TW-5). Historical; see its status note. |

## Key numbers (from the SCAD header, 50 mm baseline)

- Flow exit radius 26.25 mm = 105 % of the 25 mm bore radius (the hover exit required by
  `airframe/AGENTS.md`), reached with a 2.39° conical diffuser over 15 mm throat + ~30 mm cone.
- Mass 33.8 g per part as measured at Rev T6; the STL volume above is consistent with that at a
  CF-PETG density of about 1.05 g/cm³. Print × 2 (one per nacelle).
- Claimed saving about 85 g (0.19 lbm) per aircraft **against the 50 mm V1 servo iris**: it
  deletes 8 flaps, the unison ring, 32 pins and the servo drive. Not re-derived for the 64 mm iris.
- Ideal-momentum-theory upper bound on static thrust gain against the as-modelled iris: +6.8 %
  at equal power. This is an upper bound, not a prediction; it needs the thrust stand.
- The Rev T6 work also found the modelled 50 mm iris opens only to a flow radius of 23.77 mm
  (95 % of bore radius), because `NOZZLE_OPEN_R` sits on the flap hinge line. That finding is
  not carried into the 64 mm iris here; check it there before relying on the iris's open area.

## Cost of using it

- The 75 % convergent cruise setting is lost. The cruise efficiency and top-speed penalty is not
  quantified (no drag polar; `docs/flight_envelope.md` §2.2).
- The 2.39° diffuser half-angle is under the roughly 7° conical-diffuser separation guideline.
  That is a rule of thumb, not a cited standard: verify on the thrust stand.

## To adopt it, the work that remains

1. **Re-derive for 64 mm.** The file is the 50 mm baseline: bore radius 25.0, throat wall 2.5,
   housing outer radius 35.6 and the Ø72 pod exit pocket are 50 mm values. `main` now builds the
   64 mm nacelle (`nacelle_pod_64mm_tandem.scad`, `nacelle_64_scale.scad`). Set the radial
   parameters from the 64 mm bore the way `nacelle_nozzle_iris_64mm.scad` does, and re-check the
   pod pocket interface. Do **not** print the existing STL for the 64 mm pod.
2. **Re-run the mass/CG, trunnion, landing-gear and T/W tools** with the fixed nozzle in place of
   the iris. Rev T6 also moved `PIVOT_Z` from 107.5 to 103.5 mm for the 50 mm pod; that change is
   **not** applied on `main` and does not carry over to the 64 mm pod (`PIVOT_Z` 109.7 mm).
3. **BOM.** Rev T6 added `PRINT-NACELLE-NOZZLE-FIXED` and set the iris, retired passive-drive and
   archived gear-train rows to quantity 0. None of that is on `main`. Redo it against the current
   `bom_revT`.
4. **Makefile.** Rev T6 added an STL rule for the fixed nozzle and moved the iris to an on-demand
   `make nozzle-iris` target. Not applied here: the fixed nozzle is not part of any build.

## Provenance

Commit `8bc8e9e6` ("feat(nacelle): fixed open nozzle for Phases 5-10, defer iris to Phase 11b
(Rev T6)") on the former `feat/nacelle-nozzle-servo` branch, preserved as
`archive/feat/nacelle-nozzle-servo`. Only the new part files and the T/W plan were taken from it.
The BOM, TODO/WBS, pivot-datum and tool changes in that commit were not.
