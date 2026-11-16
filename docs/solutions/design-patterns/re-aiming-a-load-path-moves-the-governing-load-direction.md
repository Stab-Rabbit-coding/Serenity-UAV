---
title: Re-aiming a load-carrying member moves the governing load direction; re-run the combined check
date: 2026-11-02
category: design-patterns
module: landing gear / sizing gates
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "Rotating or re-aiming a leg, strut or spar to satisfy a packaging or appearance goal"
  - "A sizing tool checks one load plane (for example in-plane thigh bending) and passes"
  - "Scoping a failure study for a crash case rather than an operating case"
tags: [landing-gear, load-path, sizing-gate, side-load, pa12-cf, crash-case, allowable]
---

# Re-aiming a load-carrying member moves the governing load direction; re-run the combined check

## Context

On PR #276 the fore landing-gear swing azimuth went from −22.4° to −65° (toward the bow) so the CF backbone plates could sit flush inside the canonical gear box.  The change was made for fit and appearance.  It also turned the fore leg's swing plane nearly edge-on to a lateral load.  The out-of-swing-plane share of a side load is |sin az|: 0.38 at −22.4°, 0.91 at −65°.

The sizing gate `tools/landing_gear_r6_sizing.py` has no combined in-plane + out-of-plane thigh check, so it kept passing.  It also still carries a CF-PETG allowable (`SIGMA_ALLOW_PETG`, 27.5 MPa) while the legs are now SLS PA12-CF.  The combined check in `tools/lg_side_hit_study.py` shows the fore thigh reaching the PA 602-CF in-plane tensile strength (85 MPa) at a bank of 10.4° at crash energy, and the "grown" thigh variant failing the 27.5 MPa allowable even at the old azimuth (0.79×).

## Guidance

- **After any change that re-aims a load path, recompute every load component, not only the one the gate checks.**  The geometry change decides how a fixed external load splits between planes.  Here the leg force is fixed by the fuse plateau, so the split is the only thing that changed.
- **Resolve the load into the member's own frame.**  In-plane M = R cos φ · R_H.  The lateral force R sin φ acts out of plane in proportion to |sin az|.  The thigh then takes bending and torsion about its axis.  Combine with von Mises.
- **When a force limiter caps the load, failure depends on the attitude, not the energy.**  The ductile fuse plateau caps leg force, so the critical bank is independent of drop height.  Report it as a bank angle.
- **State every allowable with its material, direction and source.**  The PA 602-CF datasheet gives XY values only.  A Z-loaded print may fail lower.  Do not carry a different material's allowable across a material migration.
- **Scope the study to the owner's use.**  A nacelle strike is a crash, so the study predicts what to repair or replace.  It is not an operating envelope.
- **Reuse the repo's model.**  `tools/tail_strike_requirement.py` `co_strike()` (two-contact plateau, elastic second contact) works in the roll plane about the port feet line, with the real nacelle mesh rotated per tilt.

## Why This Matters

A packaging change is cheap to verify geometrically and easy to approve.  Its structural side effect is silent when the gate only covers the old governing case.  Here it moved the weakest point of the gear from the thigh's in-plane bending to its out-of-plane bending and torsion.

## When to Apply

- Re-aiming any leg, strut or spar for fit, appearance or a canonical envelope.
- Migrating a part's material: re-derive every allowable.
- Writing a failure study: ask first whether the event is operating or a crash.

## Examples

Port side, crash plateau (1,218 N per leg), thigh root, von Mises, MPa:

| Bank | Fore (−65°) | Aft (+28°) |
|---|---|---|
| 5° | 66.5 | 58.4 |
| 10° | 83.6 | 66.4 |
| 20° | 118.3 | 82.2 |

Full tables, co-strike cases at 0/45/90/135° nacelle tilt, and assumptions: `docs/LG_SIDE_HIT_FAILURE_MODES.md`.
