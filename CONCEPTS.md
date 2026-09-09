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

## Tilt Spar

The transverse shaft a nacelle pivots about when it tilts between cruise and hover attitude, running along the hull X axis at the nacelle's pivot station.

The spar is **keyed to the nacelle**, so it rotates *with* the nacelle rather than remaining fixed to the wing. This is the single non-obvious fact about it: anything clamped to the spar therefore sits in the nacelle's own rotating frame and has no relative motion against other nacelle-mounted parts, so the spar is not a usable datum for a Passive Tilt Drive.

## Unison Ring

The single rotating ring inside a nacelle's nozzle that drives every nozzle flap together, so all flaps hold one common exit area rather than being actuated individually. It rotates about the duct axis, and its rotation angle is what sets the nozzle's exit area; a cam or lever profile on the ring converts that one rotation into each flap's swing.

## Passive Tilt Drive

The project's standing requirement that the nozzle's exit area be driven by nacelle tilt alone — no dedicated nozzle actuator, servo, or control channel. Nozzle position is a pure function of tilt angle, so tilt and nozzle schedule cannot disagree in flight.

Because the driven parts ride the tilting nacelle, a passive tilt drive must take its input datum from a body that does *not* tilt with the nacelle (the wing); a pickup fixed to any nacelle-mounted body, the Tilt Spar included, has zero relative motion against the Unison Ring and transmits nothing.
