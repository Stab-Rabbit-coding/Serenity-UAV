---
title: "Gate a per-part invariant at every selector value the part is published at, including the default the exporter uses"
date: 2026-10-10
category: design-patterns
module: "landing gear / airframe (any parametric part with variant selectors; first found at the 3.0in Rev R6 landing-gear bay)"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "a parametric part has a selector or variant flag (station, side, size, rev) that moves a datum or changes geometry"
  - "a source comment claims an invariant (body_count == 1, manifold, clearance) was checked, without saying at which selector value"
  - "an exporter renders the part without passing the selector, so the published STL is the SCAD default"
  - "one shared part file is used at more than one station or side"
related_components:
  - tools/landing_gear_bay_function.py
  - tools/export_landing_gear_stls.py
  - airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad
  - airframe/stls/fuselage/landing-gear/lg_r6_common_bay.stl
tags: [landing-gear, parametric, selector, variant, default-value, body-count, gate, census, openscad, export]
---

## Context

*Historical context (2026-10-10, before BHD-02). Since then the printed bays
are four conforming per-corner parts with mirrored starboard twins, generated
by `tools/generate_lg_bays.py`; see "After" below.*

At the time, the 3.0 in landing-gear bay was one printed part per station. A selector
picks the station: `BAY_STATION = "aft";` with `"fore" | "aft"` allowed
(`airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad:105`). The selector
sets the back-face datum. `BAY_STANDOFF` is now 6.07 mm fore (re-datumed at
hip Y −16; it was 4.91 at Y −1.28) and 1.85 mm aft
(`canonical_leg_r6_3_0in.scad:363`), and `BAY_BACK_X` is derived from it
(`canonical_leg_r6_3_0in.scad:364`). The aft datum came from a re-measure in
LG-10.6 on 2026-08-17. The comment block above the selector records it
(`canonical_leg_r6_3_0in.scad:314-362`).

The LG-10.3 block explains why the bay can split. The wells are cut open, so
the clevis and wire bosses no longer root on a solid plate. A carrier slab
and two gussets tie them into the liner walls instead. The block ends with a
claim: "Both are checked by body_count == 1 on the rendered bay, not by eye."
(`canonical_leg_r6_3_0in.scad:448-458`). No tool in the repo made that check.

On 2026-10-10 a new census tool, `tools/landing_gear_bay_function.py`,
rendered the bay at both stations. Its `census()` function
(`tools/landing_gear_bay_function.py:302`) renders every feature for both
`"fore"` and `"aft"` (`:306`), passing `-D BAY_STATION="<station>"` to
OpenSCAD (`:184`). It counts the bay's bodies (`:328`-`:332`) — on the
generated conforming bay with `decompose()` when one exists (`GENERATED`,
`:193`), otherwise with `trimesh` `split()` on the SCAD render — and records
`bay_bodies` per corner (`:337`). The run fails through `function_ok`
(`:132`) when any corner has `bay_bodies != 1`. The result at the time:

- Fore: 1 body.
- Aft: 2 bodies, 16,225.4 mm³ and 6,236.2 mm³. The second body's leg-local
  bounds are x 5.8 to 25.6, y −15 to 15, z 12.4 to 32.3 mm. That is the boss
  carrier and the wire bosses, which seat the spring and ductile wires.

At the aft datum the carrier does not reach the liner. The energy-absorber
seats float free.

The published part has the same defect.
`tools/export_landing_gear_stls.py` renders with only the part selector:
`cmd = ["openscad", "-o", out_path, "-D", f'PART="{part}"', scad]`
(`tools/export_landing_gear_stls.py:91`). It never sets `BAY_STATION`, so
the bay it writes is the default `"aft"` render. The bay is in the `COMMON`
set (`:65`) and is written as `lg_r6_common_<part>.stl` (`:163`). On
2026-10-10, `airframe/stls/fuselage/landing-gear/lg_r6_common_bay.stl` was
checked and splits into the same two bodies. The released print would have
had a loose block of wire bosses, behind a comment that said the check
existed.

Two things missed it:

- The earlier body-count check, if it was run, was evidently run at the fore
  datum, or before LG-10.6 moved the aft datum. Both leave the aft render
  untested.
- The bulkhead context gate, `tools/cargo_bulkhead_context.py`, loads the
  merged `lg_r6_3_0in_hull_legs.stl` (`tools/cargo_bulkhead_context.py:154`)
  and intersects it with other parts. It never splits a part into bodies.
  Its only `split` calls parse part names (`:304-305`). A loose body that
  clashes with nothing passes.

## Guidance

1. **Gate every per-part invariant at every value of every selector.** This
   covers body count, watertightness, minimum wall and clearance. A part is
   used or published at each selector or variant value, so check it at each
   one. Do not check one value and assume the rest.
2. **Check the value the exporter uses.** It is often an implicit default
   that no command line names. Read the exporter's command, list each
   variable it leaves unset, and check the part at those defaults.
3. **Put the check in a tool, not in a comment.** "Checked by body_count ==
   1" in a source comment is a claim, not a gate. If no tool runs it on every
   change, delete the claim or write the tool.
4. **Have the exporter assert the invariant on what it writes.** The
   exporter is the one place that sees the exact file that will be printed.
   If it counts bodies and checks watertightness before it writes, a split
   part cannot be published.
5. **Do not count on intersection gates to find disconnected bodies.** A
   clash check reports overlap between parts. It says nothing about whether
   one part is in one piece.

This is the same lesson as
[build-every-joint-in-context-through-its-full-motion.md](build-every-joint-in-context-through-its-full-motion.md),
from another side. That doc says to check solids in position, not
parameters. This one says to check every configuration the solid is built
in, and the one actually shipped.

## Why This Matters

A part that prints as two bodies is not one part. Here the loose body held
the wire seats, the gear's energy absorbers. The failure would have shown
up at assembly, or worse, in a hard landing. The comment made the gap
harder to see, because a reader had no reason to doubt it. A datum change
in one branch of a selector left the other branch's check stale, and the
exporter shipped the stale branch by default.

## When to Apply

- A SCAD or CAD part has a selector, flag or variant that changes geometry:
  station, side, size, revision or `PART`.
- An exporter or build script renders a part with fewer `-D` overrides than
  the part has selectors.
- A datum, standoff or dimension changes in one branch of a selector.
- A source comment says something "is checked" or "is gated". Find the tool
  that does it. If there is none, treat the claim as false.
- A part is listed as shared or common across variants.

## Examples

**Before.** `canonical_leg_r6_3_0in.scad` claimed a `body_count == 1` check
in a comment. `export_landing_gear_stls.py` rendered the bay with only
`PART="bay"`, so the default `BAY_STATION = "aft"` applied. No tool counted
bodies. The bulkhead gate intersected the merged hull-legs STL and passed.
`lg_r6_common_bay.stl` was published as two bodies.

**After.** `tools/landing_gear_bay_function.py` renders the bay at both
`"fore"` and `"aft"`, counts bodies per corner, and fails on any count other
than 1. It reports FAIL on both aft corners. The defect is found and gated.
Fixed 2026-10-12 (BHD-14, `airframe/fuselage-mid/WBS.md`): the printed bays
are now the conforming per-corner parts from `tools/generate_lg_bays.py`,
which checks every corner for one body and exits 2 on failure before it
writes `lg_r6_3_0in_bay_<corner>_print.stl` — so the exporter of the printed
part now asserts the invariant. `export_landing_gear_stls.py` still writes
the flat `lg_r6_common_bay.stl` with no body check; that file is now only a
design reference, and adding the assert there remains open.

## Related

- [envelope-gates-pass-while-real-parts-clash.md](envelope-gates-pass-while-real-parts-clash.md)
  — the same class of gap one axis over: the starboard copy was translated,
  not mirrored, so an invariant proved on one instance did not hold for the
  other.
- [build-every-joint-in-context-through-its-full-motion.md](build-every-joint-in-context-through-its-full-motion.md)
  — check the whole motion range; this doc says to check the whole selector
  range.
- [../logic-errors/mating-face-aperture-allowlist.md](../logic-errors/mating-face-aperture-allowlist.md)
  — precedent for enforcing a claimed invariant at export time.
- [../runtime-errors/curaengine-hangs-on-overlapping-mesh-faces.md](../runtime-errors/curaengine-hangs-on-overlapping-mesh-faces.md)
  — load STLs merged before counting bodies, or every unmerged triangle
  counts as a body.

AI attribution: drafted by Claude (Claude Opus 5.5, Anthropic) from the
2026-10-10 session, under the direction of Stab-Rabbit-coding.
