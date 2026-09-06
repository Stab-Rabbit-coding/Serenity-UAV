# Concepts

Shared domain vocabulary for this project — entities, named processes, and status concepts with project-specific meaning. Seeded with core domain vocabulary, then accretes as ce-compound and ce-compound-refresh process learnings; direct edits are fine. Glossary only, not a spec or catch-all.

## Hull Frame

The single coordinate system every airframe design artifact (SCAD source, generated STL, FreeCAD assembly) is authored or baked into: X positive toward port, Y positive toward aft, Z positive dorsal (up), with the origin at the full-assembly world origin. A part's own local modelling frame is distinct from hull frame until it has been explicitly baked into it — a raw generator output is not assumed to already be in hull frame.

## Fuselage Section

One of the four hull-frame body segments — head, cargo, middle, rear — each published as its own independent, individually watertight STL. Sections are joined end to end along the hull Y axis at three fuselage joints, in order: head/cargo, cargo/middle, middle/rear.

## Mating Face

The flat cross-section at one end of a Fuselage Section where it meets the adjacent section at a fuselage joint. A mating face must be a genuinely open bore — not a solid disk — so a Splice Collar can pass through it and bond to the section's inner wall; a mesh check that only confirms the section is watertight cannot tell an open mating face from one sealed shut by a thin membrane, because both report as watertight.

## Splice Collar

The internal bonded sleeve that joins two adjoining Fuselage Sections across a fuselage joint, inserted through both sections' open Mating Faces and bonded to each section's inner wall. A collar secures and aligns the joint; it is not a substitute for either section's own load path.
