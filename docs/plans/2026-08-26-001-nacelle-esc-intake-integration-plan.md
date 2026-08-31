---
title: "plan: Integrate nacelle ESCs and refine circular intakes"
date: 2026-08-26
plan_type: feature+mechanical
execution: geometry+serviceability
---

# Plan: Nacelle ESC integration and circular intake refinement

**Target repo:** Serenity-UAV

**Scope:** Integrate two Open-Secure-ESC boards into each tandem-EDF nacelle,
define a repeatable nacelle/ESC/EDF service sequence, compare nacelle removal
against spar removal, and refine the nacelle intake to a circular Ø50 mm flow
path with a constant-area transition into the EDF housing.

## Confirmed inputs

- Two ESC boards per nacelle, one at each EDF station.
- The committed KiCad board is 32.0 × 66.1 mm with 1.6 mm PCB thickness.
- The board has no mounting-hole pattern and no encoded component-height or
  thermal-interface data; these must be measured or sourced before a bracket is
  frozen.
- The existing BOM entry describing a generic 25 g ESC mounted in a 20 mm hub
  bore is stale and must not drive geometry.
- The nacelle uses a 50 mm internal duct, removable stator and aft-spider
  sleeves, an 8 mm rotating spar, F688ZZ root bearing, MF128ZZ wingtip bearing,
  and two fixed Ø7 mm wing EDF conduits.
- Normal service should remove the nacelle before either ESC is removed.
- Intake target is a circular Ø50 mm flow section. A Ø50 mm section has area
  $A = \pi(25\,\mathrm{mm})^2 \approx 1,963.5\,\mathrm{mm}^2$.

## Architecture decision to validate

Use nacelle-first service as the preferred architecture:

1. Power-isolate the aircraft.
2. Disconnect the wing-to-nacelle harness at the nacelle-off boundary.
3. Release accessible nacelle axial retention and the keyed spar interface.
4. Slide the nacelle off the rotating spar while leaving the spar, bearings,
   wing, servo indexing, Hall reference, and wing conduits installed.
5. Remove both EDF assemblies and their associated ESCs on the bench.

Evaluate spar removal as a fallback only. It would disturb bearing seats, servo
indexing, Hall calibration, harness routing, and wing access, so it must be
quantified rather than assumed equivalent.

The final interface must use a positive-stop shoulder and keyed torque transfer.
Friction-fit-only retention is prohibited by the airframe fabrication rules.

## Implementation units

### U1 — Verify the ESC mechanical envelope

Inspect the committed files under
`Open-Secure-ESC/builds/6s/50A/CAN_485_faraday/kicad/` and extract:

- Board outline and thickness
- Component heights on both sides
- Connector and cable projection
- Mounting-hole status
- Thermal surfaces and cooling requirements
- Actual mass and center-of-gravity contribution

Add a machine-readable report and fail the fit gate when a critical value is
unknown. Reconcile the 32.0 × 66.1 mm committed outline with any stale
25.4 × 60.1 mm documentation before bracket design.

### U2 — Audit current nacelle and EDF service geometry

Build a service-envelope model from:

- `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad`
- `airframe/openscad/nacelles/edf_stator_sleeve.scad`
- `airframe/openscad/nacelles/edf_aft_spider_sleeve.scad`
- `airframe/openscad/port_tilt_spar_assembly.scad`
- `airframe/openscad/wings/wings_s1223_revo.scad`
- `airframe/FreeCAD-scripts/serenity_assembly.py`

Include EDF1 and EDF2, thrust tube, stator spar fairing, nozzle, keyed hubs,
shaft and bearings, harness port, tool envelopes, and both fixed wing conduits.
Resolve the conflicting EDF1 insertion/tool-access descriptions by checking
the actual motor and fastener access. Preserve the documented EDF2 nozzle-end
retention sequence.

### U3 — Compare removal architectures

Create a parametric motion study for:

- **Option A: nacelle off spar.** Verify inboard and outboard removal paths,
  axial retention, keyed torque transfer, positive stops, harness release, and
  clearance from wing, pylon, bearings, spar, nozzle, and thrust tubes.
- **Option B: spar out of bearings.** Quantify wingtip/root bearing access,
  servo uncoupling, Hall recalibration, angular re-indexing, harness disruption,
  and reassembly inspection.

Select the direction with measured clearance and the lowest disturbance to the
calibrated rotating assembly. Do not move the wing or bearing seats solely to
make the service path easier to model.

### U4 — Add parametric ESC seats and service interfaces

Create an OpenSCAD source for one ESC seat per EDF station, mirrored for port
and starboard. Include:

- Board envelope plus measured fit tolerance
- Positive longitudinal and lateral stops
- Captive fasteners or a documented removable retention method
- Vibration restraint
- Connector and wire-bend relief
- Cooling clearance and thermal path
- Access only available after nacelle removal

Add separate EDF1 and EDF2 lead exits and strain relief while preserving the
fixed double-Ø7 mm wing conduits. Do not route high-current ESC conductors
through the rotating spar; its hollow route remains reserved for the nav-light
wiring.

Register the ESCs, seats, retainers, and service hardware in the FreeCAD
assembly using the existing nacelle-local transform and tilt functions. Update
the BOM only after the physical board data and printed geometry are verified.

### U5 — Refine the circular intake

Measure the published port and starboard nacelle meshes at the intake. Compare
the full-resolution external silhouette against the official blueprint pack.
Classify the apparent elliptical feature as an actual flow boundary, an
outer-shell projection, or a legacy/intermediate artifact before cutting mesh.

Preserve the canonical outer mold line and the existing internal EDF, stator,
spar-fairing, and wiring geometry unless measurements prove interference.
Implement a circular Ø50 mm internal flow entrance and a constant-area
transition into the EDF housing.

For sampled axial stations, report:

- Section shape
- Effective flow area
- Equivalent/hydraulic diameter
- Wall thickness
- Deviation from 1,963.5 mm²
- Local slope/curvature changes
- Obstruction from spar fairing, wiring, or structural features

An external expanding bellmouth may preserve the canonical silhouette, but it
must not be described as constant-area flow. The constant-area requirement
applies to the effective internal duct.

Validate the intake for 20% CF-PETG printability, including lip thickness,
overhangs, trapped supports, print split joints, and EDF insertion clearance.
If the canonical shell and exact constant-area path conflict, preserve the
canonical exterior and record the aerodynamic deviation as conditional for
owner review.

#### Fine tune the circular intake flange to the canonical shell.

The current shape intersects the canonical curve at multiple z values, creating a wavy profile.
Increase the convexity of the intake flange transition to ensure a smooth, monotonic intersection with the canonical shell, eliminating the wavy profile. Ensure the flange thickness remains consistent at 2.5 mm to maintain structural integrity while minimizing weight.

### U6 -- Verify ESC cable clearance for rotation through full tilt range.

ESC wires are forward of the pivot, and therefore will experience tension and binding during the nacelle tilt.  the 10AWG wires need room to move.

### U7 — Regenerate and close out

Regenerate port/starboard nacelle geometry and new ESC hardware through the
existing source/Makefile pipeline. Re-bake only artifacts that are not already
in hull coordinates. Update the owning WBS/TODO files, root tracking files,
`PROJECT_INDEX.md`, service documentation, and `current-specification/bom_revS.csv`.

Record mass and CG changes, print orientation, material, wall thickness,
fasteners, and unresolved primary-source gates.


## Verification contract

1. The ESC report matches the committed 32.0 × 66.1 mm board outline and
   explicitly reports missing height, mounting-hole, and thermal data.
2. The selected nacelle-removal path has zero solid overlap at all sampled
   positions and leaves the wing, spar, and bearings installed.
3. Both ESCs remain inaccessible until nacelle removal and are removable on the
   bench without dismantling the constant-area duct or damaging EDF wiring.
4. EDF1 and EDF2 installation/removal sequences are executable with documented
   tool directions and fasteners.
5. Run the changed-geometry gates:

   ```text
   python3 tools/validate_stls.py
   python3 tools/wing_root_deconflict.py
   python3 tools/wing_internal_clearance.py
   python3 tools/wing_spar_carrythrough.py
   python3 tools/cargo_bay_envelope.py
   python3 tools/landing_gear_wing_clearance.py --proud
   ```

6. The intake report confirms circular Ø50 mm sections, approximately
   1,963.5 mm² effective area, documented bounded deviation, smooth transition
   into the EDF housing, and no unacceptable local obstruction.
7. Headless OpenSCAD and FreeCAD renders are inspected at cruise, intermediate,
   and hover tilt configurations.
8. New Python tooling passes syntax/static analysis and every external claim is
   reconciled against the appropriate `REFERENCES.md` entry.

## Status 2026-08-31 (Rev T4)

- **U6 (ESC cable clearance through the tilt range) is VOID as written.** It
  assumed "ESC wires are forward of the pivot ... will experience tension and
  binding during the nacelle tilt", which was true of the Rev R2 architecture
  where the wing fed the nacelle through two Ø7 mm conduits offset 17.65 mm from
  the tilt axis. Under Rev T1 the four 10 AWG feeds run **inside the spar bore,
  on the tilt axis itself**, so the lever arm the unit was written about is zero.
  What replaces it is a service-loop question at the trunnion, and that is
  blocked behind WA-R10 (no route exists in a solid pod).
- **U4 (parametric ESC seats) — still OPEN and still correctly gated.** Its own
  open gate (ESC component height, connector projection, mounting arrangement,
  thermal interface) is unresolved, and `tools/nacelle_esc_service.py` is written
  to refuse to invent it. No seat was built at Rev T4; what was built is the
  disconnect bay the wing side reassigned here (WA-R10, partial).
- **U5 (circular intake) — unchanged.** The `circular_intake_fairing()` and its
  wavy-flange defect are untouched this pass; plan 2026-08-29-005 R5 supersedes
  the fine-tuning sub-item and is requirements-only.
- **U7 (regenerate and close out) — the regeneration half is DONE.** Both pods,
  both sleeves and the new trunnion are re-rendered, baked and validated; BOM,
  WBS and `PROJECT_INDEX.md` updated.

## Open gates

- ESC component-height envelope, connector projection, mounting arrangement,
  mass, and thermal interface.
- Final nacelle removal direction and axial-retention hardware.
- EDF1 motor insertion direction and tool reach.
- Intake measurement tolerance and any CFD or bench-flow evidence required to
  support a no-separation claim.
- Printed-part and airframe mass/CG deltas after geometry is frozen.
