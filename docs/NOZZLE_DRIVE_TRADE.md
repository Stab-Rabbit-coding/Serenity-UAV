# Nozzle-Drive Mechanism Trade Study (Rev R1a, 2026-07-07)

> *"It's the tilt-nozzle. Passive. Elegant. Right up until a gear's hanging off
> the side of the ship." — design review, this session.*

## Purpose

The variable-diameter exhaust nozzle on each tilt nacelle is driven **passively
by nacelle tilt** (canonical requirement, `airframe/AGENTS.md` "Nacelle Nozzle Drive"): as a nacelle tilts
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
  dead points; departs from the canonical "**gear train**" wording previously in root `AGENTS.md`
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

## DECISION — Option B ADOPTED (2026-07-18)

> **User decision 2026-07-18: Option B (pushrod / bellcrank) is adopted.**
> Driver: even the Rev S1 internal ring gear (Option A) floored the ring at
> ≈Ø73 (Ø50 bore + Ø55 throat + M0.5 pinion clearance) and the housing at ≈Ø79,
> so it could not seat inside the canonical nozzle pocket — it stood proud of
> the aft cowl.  Option B deletes the ring gear, freeing the now cam-only ring
> to shrink to Ø66 (housing Ø71), which tucks under the cowl.
>
> Implementation (Rev T, 2026-07-18): the entire tilt-to-nozzle gear train
> (sector gear, Pinion A, bevel pair, bevel housing, Nozzle Drive Pinion) is
> archived; the ring becomes cam-only with a single pushrod lever ear
> (`nacelle_nozzle_iris.scad` Rev T); a spar crank + COTS ball-link pushrod is
> added (`nacelle_nozzle_pushrod.scad`).  The current pod spar ROTATES with
> tilt, so the crank is a direct tilt-angle input (a simplification over this
> study's "fixed crank on a non-rotating spar" assumption).
>
> OPEN / VERIFY: the spatial RSSR linkage synthesis (crank radius, ball
> positions, rod length for a monotonic 0→90° tilt → 0→23.75° ring map) is
> first-pass only — must be solved before flight hardware (WBS §1.1.3).  The
> baked pod shells need re-baking for the grown Ø72 nozzle pocket.

## DECISION AMENDMENT — hybrid A+B adopted (2026-07-19)

> **The pure Option-B "spar crank" is kinematically INVALID and is superseded by
> a hybrid.**  Flaw (user-caught, 2026-07-19): the tilt spar is **keyed to the
> nacelle**, so a crank clamped to the spar shares the nacelle's rotating frame
> with the unison ring — they swing together through the whole 0→90° tilt with
> **zero relative motion**, so the pushrod never strokes the ring.  A passive,
> tilt-driven nozzle **must take its datum from the non-tilting WING**; the Rev T
> header's "rotating-spar pod makes the crank a plain driven link" was the error.
>
> **Adopted (user 2026-07-19): "a gear at the wingtip that engages a bellcrank in
> the nacelle cowl — best of both."**  Keep Option A's positive **wing-fixed
> datum** and Option B's compact **cam-only ring** (no internal ring gear):
>
> + A gear **fixed coaxial with the spar at the wing tip** (already stubbed in
>   `wings_s1223_revo.scad` Rev R2d as the relocated fixed R22 sector).
> + A nacelle **pinion** (Pinion A) meshes it; as the nacelle tilts θ about the
>   spar, the fixed-sun / planet-pinion pair spins the pinion by
>   θ·(N_sun/N_pinion) **relative to the nacelle** — restoring the relative motion
>   the spar-crank lacked.  A **1:1 mesh** makes the pinion track tilt 1:1, so the
>   Option-B crank (8.5 mm) → pushrod → cam-ring lever (32 mm) geometry is reused
>   UNCHANGED (90° tilt → ≈23.9° ring).
> + The pinion's arm is the **geared bellcrank**; the cam-only ring keeps the
>   nozzle under the cowl (Option B's win).
>
> **Joint coordination (required):** the ~8 mm wing-tip↔nacelle gap houses a
> coaxial-spar stack — wing-tip **MF128ZZ bearing** → wing-fixed **sun gear** →
> **Hall ring magnet** (nacelle non-ferrous stub) / **MT6701** (wing, off-axis
> R11).  The pinion sits OFF the spar axis (≈26 mm aft) so it clears the on-axis
> Hall stack; the MT6701 is off-axis chord-aft.
>
> Illustrated in `airframe/openscad/port_tilt_spar_assembly.scad` §6 (pitch
> cylinders).  OPEN (WBS §1.1.3): module + tooth counts + exact pitch radius,
> crank/pushrod lengths + transmission angle over 0..90°, ring-lever azimuth
> (relocate iris 22.5°→157.5°, inboard flap gap), gap width vs. the stack.
> SOURCE follow-ups: reconcile the wing R22 sector to the chosen 1:1 sun; move the
> `nacelle_nozzle_pushrod.scad` crank from the spar onto the pinion.

## Recommendation (historical — see DECISION above)

**Option A** if the priorities are canon fidelity ("passive **gear train**"),
positive/repeatable sync between the tandem EDFs and both nacelles, and a linear
map — at the cost of an internal ring gear (SLA) and re-ratioing the front stage.

**Option B** if minimum part count, FDM-friendliness, and guaranteed
zero-protrusion with the least mechanism are paramount — accepting linkage slop,
a nonlinear map. (Root and airframe AGENTS.md now describe the mechanism as an open trade study rather than fixing "gear train," so this concern is resolved regardless of which option is chosen.)

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
- `airframe/AGENTS.md` "Nacelle Nozzle Drive" — variable diameter exhaust nozzle, driven passively by gear
  train, based on nacelle tilt."
