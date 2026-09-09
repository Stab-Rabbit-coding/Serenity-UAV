---
title: "Passive mechanisms: check the reference frames before sizing anything"
date: 2026-09-09
category: design-patterns
module: "airframe/openscad/nacelles (nozzle drive linkage)"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "designing or verifying a mechanism whose motion is driven passively by another body's motion (tilt, fold, retract, deploy) rather than by its own actuator"
  - "a dimension sweep or synthesis search over a linkage returns no feasible solution anywhere in a wide parameter range"
  - "picking up a mechanism whose source comments call its geometry first-pass, placeholder, or VERIFY"
related_components:
  - airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad
  - airframe/openscad/nacelles/nacelle_nozzle_iris.scad
  - tools/nozzle_linkage_check.py
  - docs/NOZZLE_DRIVE_TRADE.md
tags: [kinematics, linkage, reference-frames, passive-drive, nozzle-drive, rssr, design-verification]
---

# Passive mechanisms: check the reference frames before sizing anything

## Context

The Serenity nozzle is **passively driven**: the nozzle's variable-area iris is
supposed to open and close as a function of nacelle tilt alone, with no
dedicated actuator. The Rev T implementation
(`airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad`) tried to do that with
a crank clamped to the tilt spar, a rigid pushrod, and a lever ear on the
nozzle's unison ring — a spatial RSSR linkage. Its own header flagged the
numbers as first-pass and said *"do NOT print for flight hardware until
closed."*

Closing that VERIFY looked like a sizing problem: find the crank radius, rod
length, and mounting position that produce a monotonic, non-locking
0→90° tilt → 0→23.75° ring map. It was not a sizing problem. It was a **frame**
problem, and no dimension could have solved it.

## Guidance

**Before sizing any passively-driven mechanism, identify which rigid body each
end of the linkage is fixed to, and confirm the two bodies actually move
relative to each other.**

If the input pickup and the output link are both fixed in the *same* moving
frame, their relative motion is identically zero — the mechanism has no input at
all, no matter what lengths you choose.

That is exactly what happened here. The tilt spar is **keyed to the nacelle**,
so it rotates *with* the nacelle rather than against it. A crank clamped to that
spar therefore shares the nacelle's rotating frame with the unison ring it is
supposed to drive. Through the whole 0→90° tilt sweep the crank and the ring
swing together, rigidly, with zero relative motion between them, so the pushrod
never strokes the ring.

The corollary is the practical rule:

> **A passive, motion-driven mechanism must take its datum from a frame that
> does *not* move with the driven body.**

Here that means the non-tilting **wing**, which is what the adopted replacement
does: a sun gear fixed coaxial with the spar at the wing tip, meshed by a
nacelle-mounted pinion. As the nacelle tilts by θ, the fixed-sun/planet-pinion
pair spins the pinion by θ·(N_sun/N_pinion) *relative to the nacelle* — which
restores exactly the relative motion the spar-crank lacked. At a 1:1 mesh the
pinion tracks tilt 1:1 in the nacelle frame, so the original
crank → pushrod → cam-ring-lever geometry is reusable unchanged.

**Second rule, about search results:** an exhaustive parameter sweep that comes
back *completely* empty across a wide, physically generous range is evidence of
a structural or frame error in the model — not an invitation to widen the sweep.
A genuine sizing problem usually yields near-misses that improve toward some
region of the space. Uniform failure everywhere means the thing you are
searching for does not exist in that formulation.

## Why This Matters

The cost of skipping the frame check here was a purpose-built numerical tool
plus an exhaustive 336-combination search (crank radius 8.5–28 mm × rod length
58–90 mm × 24 mounting phases × 8 spar stations), all to rediscover — less
cleanly — something a one-paragraph frame argument settles immediately.

Worse, the sweep's empty result was initially read as a *new* topology finding
worth escalating, when the correct reading was "the model's frame assumption is
wrong, or the mechanism has no relative motion at all." A wrong diagnosis
written into a WBS is more expensive than no diagnosis, because the next person
inherits it as fact.

The frame check is close to free. It is a paragraph of reasoning and it runs
before any CAD, any tooling, and any search.

## When to Apply

Apply this before sizing, and again whenever a search disappoints:

- **Any passive/driven mechanism** — tilt-driven nozzles, fold-driven latches,
  retract-driven doors, gear-driven sequencing. Ask: *what is the input link
  fixed to, what is the output link fixed to, and do those two bodies move
  relative to one another?*
- **Shafts that may be keyed rather than free.** A shaft passing through a body
  is not automatically a fixed datum for that body. Whether it is keyed,
  bearing-mounted, or free is the single fact that decides whether a crank on it
  is an input or dead weight. Check it explicitly; do not infer it from the
  shaft's presence.
- **Empty search results.** Before widening bounds or loosening tolerances,
  re-derive the kinematic model's frames by hand for one configuration.

A cheap concrete test: freeze the driving motion at two different positions and
ask whether the input and output attachment points have moved *relative to each
other*. If they have not, stop — no dimensions will help.

## Examples

**The failing formulation (spar-crank, superseded):**

```
tilt spar  ──keyed to──>  nacelle
crank      ──clamped to──> tilt spar     ⟹ crank is in the NACELLE frame
unison ring ──mounted in──> nacelle       ⟹ ring  is in the NACELLE frame

relative motion between crank and ring = 0   ⟹ pushrod never strokes
```

Symptom in the checker: no reachable, monotonic solution anywhere —
`tools/nozzle_linkage_check.py --search-dimensions` returns zero passing
combinations out of 336.

**The working formulation (wing-fixed datum, adopted 2026-07-19):**

```
sun gear   ──fixed to──> WING (non-tilting)   ⟹ sun is in the WING frame
pinion     ──mounted in──> nacelle             ⟹ planet rides the tilting frame

nacelle tilts θ ⟹ pinion rotates θ·(N_sun/N_pinion) RELATIVE TO THE NACELLE
                ⟹ crank on the pinion now strokes the ring
```

At 1:1, 90° of tilt yields ≈23.9° of ring rotation, matching the iris cam's
required stroke, and the previously-designed crank(8.5 mm) → pushrod →
cam-ring-lever(32 mm) geometry carries over unchanged.

See `docs/NOZZLE_DRIVE_TRADE.md`, "DECISION AMENDMENT — hybrid A+B adopted
(2026-07-19)", which is the governing decision record for this mechanism.
