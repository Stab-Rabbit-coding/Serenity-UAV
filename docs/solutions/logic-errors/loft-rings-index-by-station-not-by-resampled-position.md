---
title: "Lofting rings of unequal length: resample each half to a fixed count, and build vertex indices before Trimesh(process=True) renumbers them"
date: 2026-11-11
category: logic-errors
module: "tools/nacelle64_optD_aft_fairing.py, tools/nacelle64_optD_glove.py, tools/od17_junction_cfd/geom.py"
problem_type: logic_error
component: tooling
severity: low
applies_when:
  - "lofting section rings whose point count changes along the span (for example a truncated trailing edge)"
  - "adding cap faces by index after building a trimesh"
related_components:
  - tools/nacelle64_optD_aft_fairing.py
tags: [trimesh, loft, process-true, vertex-merge, manifold3d]
root_cause: "a ring was resampled by one linspace over [top, bottom] concatenated, which shifts the top/bottom split when the lengths differ; caps were indexed as i*N+j against a mesh whose vertices process=True had already merged and renumbered"
---

# Loft rings: keep correspondence and index before merging

Found by `/code-review` on the OD-17 sprint diff. The geometry still came out watertight, because the
rings differed by only a few points and the volume check passed, but the numbers were fragile.

- **Resample each half separately** (top, then bottom) to the same count, so ring index *j* means the same
  chord fraction at every station.
- **Build `V` and `F` including the cap centres first**, then call `trimesh.Trimesh(V, F, process=True)` once.
  `process=True` merges and renumbers vertices, so indices written against `i*N+j` afterwards point at the wrong
  vertices.
- Re-check after any change: `status` NoError, watertight, and the bond-overlap volume still matches
  (0.042 in³ (691 mm³) for the aft fairing).
