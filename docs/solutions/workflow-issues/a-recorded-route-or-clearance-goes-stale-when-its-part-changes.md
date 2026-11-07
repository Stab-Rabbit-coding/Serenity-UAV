---
title: "A recorded 'route exists' or '0 in³ (0 mm³) sweep' goes stale the moment the part it was measured on changes — re-measure on the live mesh before building on it"
date: 2026-11-07
category: workflow-issues
module: "airframe/wings-nacelles/WBS.md (WA-R10, NAC-64-GEOM-04); tools/nacelle64_assembly_check.py"
problem_type: workflow_issue
component: development_workflow
severity: high
applies_when:
  - "a WBS item says a route, clearance or sweep is UNBLOCKED / EXISTS / 0 in³ (0 mm³) and you are about to plan or build on it"
  - "the part behind that claim has since been scaled, hollowed, flattened, re-datumed or re-baked"
  - "two WBS entries about the same requirement disagree"
related_components:
  - airframe/wings-nacelles/WBS.md
  - tools/nacelle64_assembly_check.py
  - docs/NACELLE_64MM_VERIFICATION.md
  - docs/solutions/design-patterns/build-every-joint-in-context-through-its-full-motion.md
tags: [stale-record, clearance, wbs, cable-route, tilt-sweep, re-measure, hollowing, scale]
---

# A recorded route or clearance goes stale when its part changes

## Context

Two WA-R10 entries said the 4 × 10 AWG route was "UNBLOCKED" and "now EXISTS" once the pod was hollowed.
NAC-64-GEOM-04 recorded "pinion vs pod 0 in³ (0 mm³)" over the full tilt sweep. Both claims were reasoned from
an earlier pod. Since then the pod gained the ×1.06 enlargement, the cowl change and the flattened
source. When the live render was assembled (2026-11-07):

- the spar-bore mouth sits about 0.04 in (1 mm) from the cartridge wall, and the largest free sphere there is
  0.059 in (1.5 mm) against the 0.261 in (6.64 mm) the bundle needs. There is no route at all.
- 0.137 in³ (2,237 mm³) of pod material lies inside the pinion's swept volume.
- the disconnect bay had lost its floor, and a skin covered its mouth.

## Rule

1. A route or clearance claim is a measurement tied to one mesh. Record which mesh (render date, scale,
   commit), not only the result.
2. Before planning on such a claim, re-run the measuring tool on the live render, on both sides. The port pod
   is not an exact mirror (10 % symmetric difference).
3. When the measurement disagrees, add a dated note to every entry that carries the old claim and close the
   duplicates. Do not quietly fix one of them.

## Same failure, other direction: a mating part's comment promises a change its partner never got

OD-1 (2026-11-07). `nacelle_nozzle_iris_64mm.scad` said "the stage-2 cartridge ends 3 mm short for it" (0.12 in).
`edf_motor_mount_64mm.scad` still ended at `P64_Z_NOZ`, so the throat spigot sat inside the cartridge
wall (0.095 in³ (1,562 mm³)). When a source states something about another part, grep that part for it, or better,
derive one from the other (`Z_AFT = P64_Z_NOZ - NZ_SPIGOT_L`). Then the assembly check, not the comment,
is the proof.

## Cost of skipping it

A sprint plan built on "route exists" would have scheduled harness drawing before the geometry had any place
for the harness. That is a full sprint of work against a part that cannot accept it.
