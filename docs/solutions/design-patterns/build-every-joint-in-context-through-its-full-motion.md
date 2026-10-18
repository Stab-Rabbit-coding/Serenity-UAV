---
title: "Build every joint in context, through its full motion, with its non-printed parts and air paths, before release"
date: 2026-10-03
category: design-patterns
module: "airframe (all joints and interfaces; first found at the nacelle tilt joint)"
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "releasing any part that mates with, moves against, or routes through another part"
  - "a fit checker passes on parameters (module, ratio, centre distance, bore, bolt circle) but no assembled mesh has been checked"
  - "a joint moves (tilt, fold, retract, door, nozzle) and anything crosses it: shaft, gear, harness, connector, sensor"
  - "a part carries or encloses a non-printed component (PCB, ESC, bearing, magnet, insert, fastener, harness, connector)"
  - "a required air path crosses or sits inside the part (pitot line, ESC cooling inlet and discharge, intake, exhaust)"
related_components:
  - airframe/openscad/nacelles/nacelle_tilt_joint_context.scad
  - airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad
  - airframe/openscad/nacelles/nacelle_trunnion_64mm.scad
  - airframe/openscad/nacelles/nacelle_tip_gear_variants.scad
  - tools/nacelle_trunnion_fit.py
tags: [assembly, in-context, clash, motion-sweep, harness, pcb, cooling, pitot, manifold3d]
---

# Build every joint in context, through its full motion

## Context

On 2026-10-03, during the 64 mm EDF nacelle work, the tilt joint's tip gear
stage passed `tools/nacelle_trunnion_fit.py`, which checks module, ratio and
centre distance. Then the joint was assembled in position: the real starboard
wing mesh, the rendered pod, the trunnion, the spar stub, and the wing-fixed
pinion with its shaft (`airframe/openscad/nacelles/nacelle_tilt_joint_context.scad`).
The real meshes were swept through the tilt range of −5 to 140° with
manifold3d booleans. That assembly found defects the parameter check had
missed:

- The wing pinion had no swept clearance through the pod shell. It
  intersected the shell by 474–1127 mm³, depending on the gear variant.
- The pinion drive shaft cut both the trunnion flange (28 mm³) and the pod
  collar (18 mm³).
- The collar's threaded-insert bores were patterned about the duct axis, not
  the spar axis, so 2 of 3 were in the wrong place.
- The navigation-light wire port sat inside the shaft's sweep, so the harness
  would have been sheared.
- In the 50 mm trunnion, the load path from barrel to flange ran through the
  bonded encoder magnet.

All five defects were already in the 50 mm design. They survived several
revisions because every check compared numbers and none compared solids in
position. Two related learnings found the same class of problem from
different directions:
[passive-mechanism-check-frames-before-dimensions.md](passive-mechanism-check-frames-before-dimensions.md)
and
[probe-the-published-hull-and-change-the-placement-class-not-the-margins.md](probe-the-published-hull-and-change-the-placement-class-not-the-margins.md).

## Guidance

Before a part is released, build each joint and intersection **in context**.
That means four things:

1. **Assemble the real mating parts.** Use rendered STLs or the real SCAD
   modules, not idealised stand-ins. Place each part by **geometry measured on
   its own mesh**, such as a bore centre, a pad face or a shaft axis, and
   record the measured values in the context file header. Do not rely on bake
   or placement transforms that may be stale. The tilt-joint context places
   the wing by its measured Ø20.4 spar bore and tip-pad face.
2. **Model the non-printed parts as solids.** Include bearings, magnets and
   sensors, inserts and fasteners with tool access, PCBs and ESC boards at
   their real stack height, connectors with mating clearance, and wiring
   harnesses. Model each harness as a swept tube along its route, with a
   service loop wherever it crosses a moving joint. Include the minimum bend
   radius and the stroke or tilt range the loop must absorb.
3. **Model the required air paths as keep-out solids.** Include the nose
   pitot and static line from port to sensor, the ESC cooling inlet, the
   path across the heatsink, and the discharge port in the nacelle, and the
   intake and exhaust ducts. A clash with an air path counts as a failure,
   the same as a clash with a solid.
4. **Sweep the full motion range.** Check every moving part over its range,
   for example −5 to 140° of tilt, the full travel of the nozzle petals, or a
   door from open to closed. Check each step, or union the swept volumes.
   Report the intersection volume for every pair. Render cutaways that show
   the clash volumes in red. Then add the check to a gate so it re-runs
   whenever a part changes.

The relief is cut from the same swept volume that the check uses. In the 64
mm pod, `tilt_drive_relief()` subtracts the swept pinion and shaft envelope
over the part-frame arc −7.2° to 149.8°. The nav port was moved to 210°,
outside that arc, and the insert bolts were moved to 175°, 255° and 335° to
clear the shaft slot.

## Why This Matters

A parameter check proves that two features agree on paper. It cannot prove
that the solids clear each other in position, through the motion, or that
the parts around them are not in the way. The defects listed above were
fit-critical and build-blocking. Two of them, the sheared harness and the
load path through the bonded magnet, would have failed in service, not on
the bench. Wiring, PCBs and cooling air are usually added late and are
rarely modelled, so they are where in-context checks find the most
surprises.

## When to Apply

- Before releasing any printed or procured part that touches another part.
- Whenever a mating part's revision changes. Re-run the context sweep, not
  only the parameter checker.
- For every moving joint, and for every harness, duct or line that crosses
  one.
- Interfaces still to be swept include: the nose pitot line to the air-data
  sensor; nacelle ESC cooling inlets and discharge ports against the pour-foam
  core and the ESC bay covers; harness service loops across the tilt trunnion;
  and the cargo door and winch.

## Examples

**Before.** The fit checker reported the tip gear stage as PASS on centre
distance and ratio. No assembled model existed.

**After.** `nacelle_tilt_joint_context.scad` imports the pod STL, the wing
mesh placed by measured geometry, the trunnion and the pinion, and accepts
`-D CLASH_STL=...` to draw a precomputed interference mesh in red. A
manifold3d sweep over the tilt range reports the intersection volume for
every pair: pinion and shaft against the pod, the trunnion and the wing, and
the nav-harness port against the shaft sweep. Option A (a 10.5 mm gear face)
plus relief 1 has been implemented, and its re-sweep against this gate is
pending in WBS item NAC-64-TILT-03 until the pod render finishes.

AI attribution: drafted by Claude (Claude Opus 5.5, Anthropic) from the
2026-10-03 session, under the direction of Stab-Rabbit-coding.
