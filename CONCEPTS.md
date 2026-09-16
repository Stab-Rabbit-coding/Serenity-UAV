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

The transverse carbon-fibre member at the wing root that carries the nacelle's loads into the fuselage, running along the hull X axis at the spar station. Since Rev T1 it is a **fixed, bonded wing member**, not a rotating shaft: the nacelle pivots on its own trunnion bearings, and tilt torque travels a separate, smaller Tilt Drive Shaft. (Through Rev S it was keyed to the nacelle and rotated with it, which is why older documents treat "spar" and "tilt axis" as the same thing — they no longer are.)

## Tilt Drive Shaft

The Ø4 steel shaft, parallel to the Tilt Spar, that carries tilt torque from the fuselage-mounted actuator out to the nacelle. It turns more than one revolution over the nacelle's sweep because the tip stage is a reduction, so the nacelle angle is read by an absolute sensor on the nacelle itself rather than inferred from the shaft.

## Tilt Drive Train

The two-stage path from the tilt actuator to the nacelle: a fuselage stage on the Tilt Drive Shaft (a worm since Rev T5b; six-start on a Ø20 gearmotor since Rev T5e) and a tip stage at the nacelle. A train is either self-locking or it is not; when it is not, a Tilt Brake — never the motor's own drag — is what holds the nacelle unpowered. For a motor coaxial with its worm, the motor's clearance to the wheel tip is set by the worm's pitch diameter alone — not by the centre distance and not by where the worm sits on the wheel — so the worm's inboard reach caps the motor diameter.

## Layout Envelope

A simple solid — box or cylinder — standing in for a piece of equipment, a moving part, a cable zone or a keep-out inside a Fuselage Section, used to prove a layout by boolean intersection against the section's published shell and against every other envelope, rather than by eye. Each envelope carries its own clearance budget (larger for moving parts than for static ones) and a declared list of the envelopes it is allowed to touch; anything a bracket or cradle carries must be an envelope too, because a part drawn only in its own source file is invisible to the proof.

## Void Former

A removable printed shape, cut to the exact cavity of a published shell, that is placed before an optional foam pour and withdrawn after cure so that the volume it occupied — a collar seat, an equipment bay, a harness way — stays foam-free. Formers are derived from the shell mesh, not drawn by hand, because a hand-drawn shape is either too big to insert or leaves a foam fillet where the equipment must later go.

## Chin Node Shelf

The printed plate on the cargo-section chin floor, under the battery nose and forward of the hoisted payload, that carries the two remaining control nodes lying flat side by side with a shared cable channel on the centreline. It exists because the chin flanks beside the battery were measured too narrow three times; the chin floor was clear first try.

## Tilt Brake

The spring-applied, power-released mechanical lock that holds a nacelle at its last commanded angle when its actuator loses power. It is flight-critical because every propulsion path is fused independently so the aircraft can descend on the remaining units; the brake must survive the actuator's own path failing during that descent.

## Unison Ring

The single rotating ring inside a nacelle's nozzle that drives every nozzle flap together, so all flaps hold one common exit area rather than being actuated individually. It rotates about the duct axis, and its rotation angle is what sets the nozzle's exit area; a cam or lever profile on the ring converts that one rotation into each flap's swing.

## Passive Tilt Drive

The project's standing requirement that the nozzle's exit area be driven by nacelle tilt alone — no dedicated nozzle actuator, servo, or control channel. Nozzle position is a pure function of tilt angle, so tilt and nozzle schedule cannot disagree in flight.

Because the driven parts ride the tilting nacelle, a passive tilt drive must take its input datum from a body that does *not* tilt with the nacelle (the wing); a pickup fixed to any nacelle-mounted body, the Tilt Spar included, has zero relative motion against the Unison Ring and transmits nothing.
