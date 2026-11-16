---
title: "A wire path that clears every wall can still kink below the minimum bend and run through its neighbour: test curvature and wire-to-wire overlap, not only wall clearance"
date: 2026-11-11
category: design-patterns
module: "tools/nacelle64_assembly_check.py, tools/nacelle64_optD_concept.py, nacelle_pod_64mm_tandem.scad"
problem_type: design_pattern
component: tooling
severity: medium
applies_when:
  - "routing a multi-wire bundle as polylines through a printed part and cutting channels along them"
  - "a minimum bend radius (3 x OD) is a requirement, not a hint"
related_components:
  - airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad
tags: [wire-routing, bend-radius, curvature, interference, od-17, wa-r10]
---

# Check a drawn wire path for kinks and wire-to-wire overlap

**Problem.** The OD-17 concept drew each 10 AWG wire as a polyline (bend arc, then straight "fan" and
"ease" segments). It reported wall clearance and wire/part overlap, and passed. Sprint 2 added
`--stage wires`, which takes the circumradius of every consecutive point triple. The tightest point of the
paths was 0.08-0.14 in (2.1-3.6 mm) against a 0.650 in (16.5 mm) minimum: the corners between the straight
segments. Smoothing the corners with a cubic Hermite tail then made the forward and aft wires converge on
the stud plane together and interpenetrate by 0.051 in³ (839 mm³) per pair, which only a wire-to-wire
boolean showed.

**Fix.** Three checks on every route, not one: (1) minimum circumradius along the whole polyline against
the bend limit, (2) pairwise wire overlap volume, (3) wire against every part, with channels already cut.
The overlap was removed by tilting the aft pair's bend plane 12° so it fans out inside the bend instead of
after it.

**Rule.** A route is not proven by clearance to walls. Gate its curvature and its self-interference, and
keep the path definition in one place that both the CAD (OpenSCAD) and the check read (the same numbers sit
in `OD17_OFFS` and `TAIL`; a drift between them is the next failure to guard).
