---
title: "A merged CGAL render can still be non-manifold where two shell sheets touch along an edge — split the edge by pairing faces, don't 'repair' the mesh"
date: 2026-11-07
category: logic-errors
module: "tools/nacelle64_assembly_check.py (fix_nonmanifold); any manifold3d boolean on an OpenSCAD render"
problem_type: logic_error
component: tooling
severity: medium
applies_when:
  - "manifold3d returns Error.NotManifold / volume 0 on an OpenSCAD STL even after trimesh merge_vertices()"
  - "the render log says 'PolySet has nonplanar faces. Attempting alternate construction'"
  - "a hollowed or multi-wall part (pod cavity, thin skin over a pocket) is about to be used in booleans"
related_components:
  - tools/nacelle64_assembly_check.py
  - airframe/openscad/nacelles/nacelle_pod_64mm_tandem.scad
  - docs/solutions/logic-errors/mesh-boolean-layout-proofs-silent-zero-volumes-and-shared-profiles.md
tags: [manifold3d, trimesh, cgal, openscad, non-manifold, pymeshfix, boolean, silent-failure]
root_cause: "two sheets of the hollowed pod touch along 63 edges, so each such edge has 4 faces; merging vertices cannot fix topology, and a general repair tool closes the cavities instead"
---

# A merged CGAL render can still be non-manifold where two sheets touch

## Context

The live 64 mm pod render (367,237 mm³, 124,864 faces) has no open edges, but 63 of its edges carry four
faces. The hollowing leaves the cavity wall and the outer skin touching along a line. manifold3d rejects the
mesh (`NotManifold`, volume 0), so every boolean against it returns zero. This is the same silent-zero trap
as the unmerged-STL case in the related solution. Here, though, `merge_vertices()` is already done, and that
is exactly what produces the shared edge.

## What did not work

- **pymeshfix `clean_from_arrays`** made the mesh watertight, but at **765,291 mm³**, double the real
  volume. It closed the cavities. Any clearance result from that mesh is wrong.
- **Splitting each bad vertex into face fans** using only the 2-face edges opened 260 new holes. The two
  faces that belong to the same sheet across the bad edge were put in different fans.

## What works

For every edge with more than two faces, sort its faces by the angle of their opposite vertex around the
edge. Then pair neighbours whose directions are opposite (one traverses a→b, the other b→a). Each pair is
one sheet. Run the per-vertex fan union-find with those pairs added as links, and give each fan its own copy
of the vertex. Result: 0 open edges, manifold3d `NoError`, 367,225 mm³. That is within 0.003 % of the
input, and the difference is float32.

## Prevention

- Check `Manifold(...).status()` and compare the boolean-ready volume against `trimesh.volume` before
  trusting any overlap of 0.
- Never accept a "repaired" mesh whose volume moved by more than a rounding error.
