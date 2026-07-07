# Nozzle-Drive Mechanism Trade Study (Rev R1a, 2026-07-07)

> *"It's the tilt-nozzle. Passive. Elegant. Right up until a gear's hanging off
> the side of the ship." — design review, this session.*

## Purpose

The variable-diameter exhaust nozzle on each tilt nacelle is driven **passively
by nacelle tilt** (canonical requirement, root `CLAUDE.md`): as a nacelle tilts
0 → 90°, the nozzle exit opens from 75 % → 105 % of bore (radius 18.75 →
26.25 mm). The Rev R1 mechanism does this with a spur-gear train, but the
**compound idler protrudes ~10 mm past the Ø82 mm nozzle housing / nacelle OD**
(shaft at R43.6 mm, Idler-Out teeth reach R≈51 mm) — the "steampunk accessory"
flagged in review. This study compares two redesigns that eliminate the
protrusion. Author: AI (Claude, Opus 4.8), reviewed by @reepicheep-hakx.

## Common downstream (identical for both options)

The nozzle **unison ring** must rotate **23.86°** over 0 → 90° tilt
(`THETA_RING_REF_OPEN`, `nacelle_nozzle_iris.scad`). The ring → follower-pin →
flap kinematics (`pin_r` 31 → 35 mm) that convert ring rotation to exit radius
are unchanged in both options. Only the **tilt → ring-rotation** stage differs.

## Rev R1 baseline (the problem)

Path: fixed **sector gear** (R22) → **Pinion A** (R6, orbits pivot) → tilt ×4.67
+ orbital = **420°** shaft rotation → **bevel pair** (1:1, 90° redirect) →
longitudinal shaft → **Crown Pinion** (R6) → **compound idler** (44T/15T) →
**external ring gear** (72T, R36). Net 420° → 23.86° = **17.6:1 reduction**.
The large reduction exists only because the front stage first multiplies tilt
×4.67, then divides it back ×17.6 — a wasteful path whose idler must sit
*outside* the external ring to mesh it. **9 moving parts.**

## Option A — Internal ring gear, re-architected reduction

Put the ring-gear teeth on the **bore side** (internal 72T) and drive it with a
**single ~13T pinion** at R≈29.5 mm — fully inside the Ø82 housing. The oversized
compound idler is **deleted**. Because a single 13T→72T pinion is only 5.5:1, the
front sector/pinion stage is **re-ratioed to ~1.5×** (instead of 4.67×) so the
net tilt → ring stays 90° → 23.86°. Bevel redirect retained.

- **Envelope:** all gearing inside Ø82 (no protrusion). ✔
- **Parts:** ~6 (sector, Pinion A, bevel pair, shaft, drive pinion, internal ring).
- **tilt → diameter:** **linear** (constant gear ratio) — exact, repeatable.
- **Backlash:** gear-defined, small; sector adjustment slots preload the mesh.
- **Sync (fwd/aft EDF, both nacelles):** rigid, positive.
- **Risk:** internal ring gear is harder to print cleanly (SLA preferred);
  re-ratioing the front stage must be re-verified for orbital "+1" term.
- **Effort:** moderate — re-tooth ring + iris housing, resize sector/pinion,
  delete idler + bracket, update `serenity_assembly.py`, re-derive ratio.

## Option B — Pushrod / bellcrank linkage

Delete the **entire** aft train (sector, Pinion A, bevel pair, shaft, Crown
Pinion, idler, ring gear). A **fixed crank** on the non-rotating pivot spar drives
a **pushrod** to a **lever** on the unison ring; nacelle tilt directly strokes the
ring. Spatial (RSSR-class) linkage — tilt axis (X) ⟂ ring axis (Z).

- **Envelope:** rod runs inside the nacelle skin; no radial protrusion. ✔
- **Parts:** ~4 (pivot crank, pushrod + 2 ball ends, ring lever; ring keeps no teeth).
- **tilt → diameter:** **nonlinear** (~sinusoidal): slow near closed, faster near
  open — often desirable (fine control near hover), but must be synthesised.
- **Backlash:** ball-joint + rod compliance — more slop than gears; the two
  nacelles are no longer rigidly geared to a common ratio.
- **Sync:** depends on rod stiffness / individual linkage matching.
- **Risk:** transmission angle over the full 90° input must be kept away from
  dead points; departs from the canonical "**gear train**" wording in `CLAUDE.md`
  (spec text would need updating).
- **Effort:** moderate — linkage synthesis (crank/rod/lever lengths for 90°→23.86°
  with good transmission angle), new brackets, delete 5+ gear parts.

## Comparison

| Criterion | Rev R1 (baseline) | A — Internal ring | B — Pushrod linkage |
| --- | --- | --- | --- |
| Radial protrusion | ~10 mm proud | none | none |
| Drive parts | 9 | ~6 | ~4 |
| tilt → diameter | linear | **linear (exact)** | nonlinear (tunable) |
| Backlash / slop | low | low | moderate |
| Nacelle-to-nacelle sync | rigid | rigid | rod-dependent |
| Print difficulty | med (SLA teeth) | med-high (internal ring) | **low (FDM rod/brackets)** |
| Canon spec fidelity | "gear train" ✔ | "gear train" ✔ | departs (needs spec edit) |
| Dominant failure mode | tooth strip / idler jam | tooth strip | rod buckle / ball pop-out |

## Recommendation

**Option A** if the priorities are canon fidelity ("passive **gear train**"),
positive/repeatable sync between the tandem EDFs and both nacelles, and a linear
map — at the cost of an internal ring gear (SLA) and re-ratioing the front stage.

**Option B** if minimum part count, FDM-friendliness, and guaranteed
zero-protrusion with the least mechanism are paramount — accepting linkage slop,
a nonlinear map, and a `CLAUDE.md` spec-wording update.

Kinematic prototypes and the tilt→ring map are in
`docs/img/nozzle_drive_trade.png` (schematics + curves). Full production CAD of
the selected option is pending user decision — see TODO.md §1.1.3.3.

## References

- `airframe/openscad/nacelles/nacelle_nozzle_iris.scad` — ring sweep 23.86°,
  `pin_r` map, Ø82 housing, `IDLER_SLOT`.
- `airframe/openscad/nacelles/nacelle_nozzle_idler.scad` — 17.6:1 compound ratio
  derivation, 44T/15T tooth counts.
- `airframe/openscad/nacelles/nacelle_sector_gear.scad` — sector R22, 420° Pinion A.
- `airframe/openscad/nacelles/nacelle_bevel_pair.scad` — 1:1 90° redirect.
- Root `CLAUDE.md` — "variable diameter exhaust nozzle, driven passively by gear
  train, based on nacelle tilt."
