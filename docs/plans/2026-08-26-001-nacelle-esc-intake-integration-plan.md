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
### U4 ESC BAY ENVELOPE — MEASURED 2026-08-31

The owner is designing the ESCs as a matched pair so both can sit **aft of the
tilt pivot** (`Open-Secure-ESC/docs/design-single-end-wire-egress-variant.md`):

- **ESC2**, driving the aft EDF, keeps the as-built **opposite-ends** layout —
  power in at the forward end, phases out the aft end to a motor that is aft of
  it anyway.
- **ESC1**, driving the forward EDF, takes the **single-end** variant: power and
  phase both leave the forward edge, on opposite copper faces.

Board proportions are specifiable to some degree, so the question is not "does
the board fit" but **"what proportions does this pod reward?"** Now that Rev T4b
has hollowed the pod there is a real annulus to measure.

**Method.** Ray-cast the canonical shell over Z 80–170 at 5° azimuth; subtract
the minimum skin wall (2.5 mm) and the duct wall (`SLEEVE_BORE_R` 27.7 + 2.5);
then search every azimuth window for the longest axial run clearing each depth,
excluding the nav channel (azimuth 0°) and the disconnect bay / trunnion (180°).
This is the best case — it assumes the wall is thinned to the repo minimum
throughout the bay, so no wall-schedule change can beat it.

#### CORRECTED 2026-08-31 — the board must be NARROW and LONG, not wide and short

An earlier pass in this section recommended a wide, short board (≈ 60 × 38 mm).
**That was wrong, and the error was in the model, not the measurement.** It sized
the bay as an *annular sector* — a pocket that follows the curve. A PCB is
**flat**. A 61 mm chord on a 33 mm radius has a **sagitta of 20.4 mm**: the
corners of a flat board of that width stand 20 mm proud of the arc, and the
annulus is 7 mm deep. Wide is exactly the wrong direction.

**Corrected model.** The board is a flat slab between perpendicular distances
`d_in` and `d_out = d_in + t` from the duct axis, centred at azimuth φ. Its
innermost point is `d_in` (at the centreline) and must clear the duct wall; its
outermost points are the **corners of the outer face**, at radius
`√(d_out² + (w/2)²)` and azimuth `φ ± atan(y/d_out)`, which must stay inside the
skin less one minimum wall. Verified by hand at az 90 / Z 110 / w 30 / t 5: the
corner at y = 15 fouls by 0.93 mm, exactly as the search reports.

| stack height `t` | best flat board | area | azimuth | Z span |
|---:|---|---:|---:|---|
| **4.0 mm** | **24 × 66 mm** | **1584 mm²** | 55° / 235° | 74–140 |
| 5.0 mm | 18 × 54 mm | 972 mm² | 60° | 74–128 |
| 6.0 mm | 18 × 36 mm | 648 mm² | 90° | 96–132 |

*(as-built 32.0 × 66.1 = 2115 mm²; `t` = 1.6 board + components on both faces +
mounting)*

**So the as-built LENGTH is fine — it is the WIDTH that has to come down**, 32 →
24 mm, and the stack height is the dominant lever: every millimetre of height
costs about 6 mm of width. Two such bays exist and no more, at azimuth **55°**
and **235°**, each taking the full 66 mm run over Z 74–140.

**Both bays centre at Z 107, forward of `PIVOT_Z` 113.8**, so the conclusion of
the next subsection is unchanged and if anything slightly worse: ESC placement is
not a CG lever in this pod.

**Options if 24 × 66 × 4.0 mm is not buildable:**
1. **Split each ESC into two boards** — the single-end egress already groups the
   conductors by face, so a power-stage / logic-stage split along that seam is
   natural, and the thin logic card can live where the annulus is shallow.
2. **Bulge the cowl locally** — a documented mould-line deviation (plan
   2026-08-29-005 R7) buys depth directly.
3. **Curve the board** to the 33 mm radius. Real, but not for a 4-layer power
   board without a rigid-flex process this project has not costed.
4. Accept the 25 % area cut at 24 × 66.

#### EDF unit data — read from the manufacturer's page 2026-08-31

Source: <https://www.xfly-model.eu/en/edf-units/4833-edf-ducted-fan-xfly-galaxy-x5-xfly-model-50mm-12-blades-6s-motor-3200kv.html>

| item | published | repo currently says | note |
|---|---|---|---|
| motor | 2627, **3200 KV** | 2627-3200 KV | ✓ **CONFIRMED by the owner 2026-08-31** |
| motor OD | 26 mm | — | vs `R_HUB` 8 / `MOTOR_BOLT_R` 10 |
| shaft | Ø3 mm | Ø4 bore (`R_HUB_BORE` 2.0) | ✓ 1 mm clearance, as designed |
| blades | 12 | 12 | ✓ `N_FINS` 11 stays coprime |
| thrust | 1240 gf @ 6S | 1240 gf | ✓ |
| max current | 38 A @ 6S | 40 A branch fusing | ✓ |
| **unit weight** | **75 g complete** (EDF + lip + motor) | 70 g | see below |
| **bolt pattern** | **NOT STATED** | `MOTOR_BOLT_R` = 10.0 | **still UNVERIFIED, and the spider is built to it** |
| motor weight alone | **NOT STATED** | — | needed; see below |
| wire gauge / length | **NOT STATED** | 16 AWG Ø3 assumed | |

**Two things this changes.**

1. **KV — RESOLVED 2026-08-31, and my own claim above was overstated.** The
   owner confirms **2627-KV3200**. I wrote that "the repo says 2700 KV
   throughout"; it did not. `AGENTS.md`, `LICENSE_AND_ATTRIBUTION.md` and
   `generate_placeholders.py` already said 3200 KV, and the 2700 KV figures in
   `docs/README.md` / `PHASED_BUILD_GUIDE.md` belong to a **different part** —
   the 80 mm Changesun XRP 3660-2700KV of the archived Rev P / Phase 7 upgrade.
   Exactly **one** live line was wrong: the `nacelle_pod_50mm_tandem.scad`
   header. Fixed.

   **But it propagated into something that matters.** The stator vane angle was
   derived in `blender_stator_gen.py` from "~35,000 RPM", and the real figure is
   **71,040 rpm** no-load at 6S — 2.03×. Checking that derivation showed all
   three of its inputs are wrong (RPM, thrust 8.94 N vs the published 12.16 N,
   and area 0.00240 m² which is the Ø55.3 casing rather than the Ø50 bore), and
   that it used `atan(V_exit/U_tip)` — the relative flow angle from tangential,
   not the absolute swirl from axial that a stator removes. A first-pass Euler
   re-derivation gives ≈ 22°, not 33°, but it rests on a loaded RPM and a motor
   efficiency that are not published. **`VANE_ANGLE_DEG` is therefore flagged
   and left as built, not silently changed.** The 11-vane count is unaffected —
   Tyler–Sofrin cut-off is a relationship between counts, not frequencies.
2. **The owner is keeping the rotor and motor only**, using the nacelle tube as
   the thrust tube, so the *carried* mass is less than the 75 g combo. The page
   does not publish the motor-alone weight, so this is a sensitivity rather than
   a value:

| carried mass per EDF | `PIVOT_Z` | clr, 40 mm flaps | rotating assembly |
|---:|---:|---:|---:|
| 75 g (full combo) | 113.6 | −2.73 mm | 558.6 g |
| 70 g (repo assumption) | 113.8 | −2.57 mm | 548.6 g |
| 60 g | 114.1 | −2.21 mm | 528.6 g |
| 50 g | 114.5 | −1.83 mm | 508.6 g |

Discarding the housing is worth up to **40 g per nacelle** but almost nothing in
CG — EDF1 is forward of the pivot and EDF2 aft, so the two reductions nearly
cancel. It is a **weight** win, not a clearance one. **Weigh a motor + rotor
before this goes in the BOM**; do not infer it from the 75 g combo figure.

#### HINGED ESC — owner direction 2026-08-31, and it recovers the board

The board cannot narrow to 24 mm: 32 mm is already the floor set by
`isolation_envelope.py` (12.90 widest non-isolated part + 2 × (7.5 creepage +
1.43 inset) + 2 × 0.55 = 31.86 mm, off the ADM2582E/ADM2587E Table 6 clearance).
**The owner's answer is a hinge**: two panels, **8.45 mm + 23.65 mm = 32.10 mm**
total, folded so the assembly follows the annulus instead of chording it. One of
the three power rails goes on the narrow panel, two on the wide. Same for both
ESCs in a nacelle.

**This is the right fix and the geometry says so.** A flat board's problem was
its sagitta — the corners swinging out of a 7 mm annulus. Splitting the width
collapses it:

| | sagitta at R 33 |
|---|---:|
| one flat 32.10 mm board | **4.17 mm** |
| wide panel, 23.65 mm | 2.19 mm |
| narrow panel, 8.45 mm | 0.27 mm |

**Measured fit — two bays, one ESC each, at azimuth 56° and 236°:**

| stack height | board length | Z span | area | vs as-built 2115 mm² |
|---:|---:|---|---:|---:|
| 3.5 mm | **70 mm** | 74–144 | 2247 mm² | **106 %** |
| **4.0 mm** | **64 mm** | **74–138** | **2054 mm²** | **97 %** |
| 4.5 mm | 38 mm | 96–134 | 1220 mm² | 58 % |
| 5.0 mm | 32 mm | 96–128 | 1027 mm² | 49 % |

*(one flat 32.10 mm board, for comparison: 16 mm of length at 4.0 mm stack, and
it does not fit at all above 6.0 mm)*

**The hinge takes the usable length from 16 mm to 64 mm.** At a 4.0 mm stack the
as-built 32 × 66 board is essentially recovered — 97 % of its area — and at
3.5 mm it is exceeded.

**There is a cliff between 4.0 and 4.5 mm, and it is the whole design point.**
Half a millimetre of stack costs 26 mm of length. Hold the stack at **4.0 mm** —
1.6 mm of board leaves 2.4 mm for components across both faces plus mounting.

**Fold geometry to design the flex to:**

| | value |
|---|---|
| wide panel half-angle | 19.07° |
| narrow panel half-angle | 7.04° |
| **fold angle (panel-centre separation)** | **27.1°** — the boards sit at ~153° to each other, a shallow fold |
| hinge allowance | **≤ 1.0° (0.60 mm of arc) is free**; 1.5° costs 6 mm of length (64 → 58 mm) |
| mounting radius | outer faces at ≈ 34.2 mm from the duct axis |

**Both panels cap at 4.0 mm — the narrow one is not looser, which was worth
checking.** The obvious idea is to put the tall parts (bulk capacitance) on the
8.45 mm panel because its sagitta is negligible. Tested over the selected bay:
the narrow panel fails at 5.0 mm just as the wide one does, because the fold
carries it round into a region where the skin is closer. **Design for a uniform
4.0 mm stack on both panels.**

**CG — take the length, not the station.** The best bay's centroid is Z 106,
7.8 mm *forward* of `PIVOT_Z` 113.8. Forcing the centroid aft of the pivot costs
length:

| stack | best bay with centroid ≥ 113.8 | length | area |
|---:|---|---:|---:|
| 3.5 mm | Z 84–144 | 60 mm | 1926 mm² |
| 4.0 mm | Z 90–138 | 48 mm | 1541 mm² |

16 mm of length at 4.0 mm stack, to buy a station worth **~+0.4 mm** of hover
clearance (measured above). Not a good trade — let the board sit where it fits.

**Still needed before the pocket can be cut:** board **length** and **stack
height**. The width (32.10, split 8.45 + 23.65) and the fold are settled; the
pocket is one parametric block once those two numbers land.

#### BUILT 2026-09-06 — the bays, at the owner's final widths

The owner settled the split as **23.0 mm power + 10.0 mm signal = 33.0 mm**
(the analysis above had used a provisional 23.65 + 8.45), and named the panels:
the wide one carries the power stage, the narrow one the signal stage. Re-run at
those widths against the ray-cast shell:

| stack | length | Z span | area | vs as-built 2115 mm² |
|---:|---:|---|---:|---:|
| 3.0 mm | 74 mm | 74–146 | 2442 mm² | 115 % |
| 3.5 mm | 68 mm | 74–140 | 2244 mm² | 106 % |
| **4.0 mm** | **62 mm** | **74–134** | **2046 mm²** | **97 %** |
| 4.5 mm | 58 mm | 74–130 | 1914 mm² | 91 % |
| 5.0 mm | 50 mm | 74–122 | 1650 mm² | 78 % |
| 6.0 mm | 16 mm | 74–88 | 528 mm² | 25 % |

**The cliff is gone.** At the earlier 8.45 mm narrow panel, 4.0 → 4.5 mm of stack
cost 26 mm of length. At 10 mm it costs 4 mm, and 4.0 → 5.0 costs 12 mm rather
than everything. A slightly wider signal panel bought a materially more forgiving
design point, which is not what one would predict from the sagitta table alone.

**Built:** hinge azimuth **69° / 249°**, seat radius **30.2** (the sleeve-zone
duct wall, so the board lands on structure aft of Z 90 and on kept-solid shell
forward of it), fold **30.25°** — panels at **149.75°** to each other.

**Access is a cover, and that was forced by the hollowing.** Rev T4b created the
annulus; it also sealed it. A 33 mm folded board cannot be threaded in through a
4 mm vent, so each bay is cut radially through the skin and closed by
`nacelle_esc_cover.scad` — **four distinct parts**, because the shell is not
axisymmetric and port/stbd/bay-A/bay-B are four different surfaces. The cover's
outer face is the same ray-cast skin grid the pod's rebate is cut from, so the
joint is flush by construction; verified mesh-against-mesh at **0.008 mm³** of
interference (gate T9).

**U6 is now genuinely void, not merely superseded.** Its premise was ESC wires
forward of the pivot experiencing tension through the tilt range. The feeds run
inside the spar bore on the tilt axis, and the ESCs themselves sit in bays
centred at Z 104 — 3.5 mm forward of `PIVOT_Z` 107.5, which is as close to the
axis as anything in this pod gets.

**And U4's own CG conclusion is confirmed the hard way.** Plan 003 KTD8 banked
+3.91 mm of pivot station on relocating ESC1 aft to Z 150.6. Measured, no bay
exists there — the best bay wholly aft of Z 130 is 23 × 30 mm, which is not an
ESC. Siting both ESCs at the real centroid moves `PIVOT_Z` **113.8 → 107.5** and
costs **6.3 mm of hover clearance**. That lever was never available.

#### EDF mechanicals — the vendor listing, read 2026-08-31 (REF-EDF-002)

The manufacturer's page publishes no bolt pattern and no external dimensions
("nc" for both). The vendor listing image the owner supplied does carry a
dimension drawing and a packing-list photo, and it settles two things and
un-settles a third.

| quantity | value | panel |
|---|---|---|
| fan / rotor diameter | **Ø50 mm** | Product Size drawing |
| shroud (housing) length | **38.6 mm** | Product Size drawing |
| overall length incl. motor | **76 mm** | Product Size drawing |
| blade-tip to shell clearance | **0.4 mm** | body text |
| motor mounting screws | **4**, plus 1 longer spinner screw | Packing List photo |
| motor hub | disc, 4 round holes alternating with 4 slots | aft-view photo |
| **bolt circle diameter** | **STILL NOT PUBLISHED** | — |

**Caveat carried forward:** this is a marketplace listing, not a datasheet, and
it mixes the 3S/4S/6S variants — the motor photographed is labelled
**2627-KV4600**, the 4S unit. The owner's assessment is that the dimensions and
screw layout are common across variants; that is recorded as an owner assessment,
not a manufacturer statement.

**1. The Ø50 bore is now a running fit, not just a nominal.** The build keeps
only the rotor and motor and uses the nacelle bore as the thrust tube, so the
rotor turns against **printed plastic**. The vendor holds 0.4 mm blade-tip to
shell inside a 50 mm shroud ID, i.e. the rotor is ≈ Ø49.2. Our Ø50.0 bore
therefore reproduces the designed clearance exactly — **but only if it prints on
size.** Added to the post-print checks in both the pod and the aft sleeve:
**Ø50.0 +0.4 / −0.0** at the EDF1 rotor station (Z ≈ 27.5–40) and at the EDF2
rotor station (the aft sleeve bore). An undersize bore rubs the rotor.

**2. PRINT-BLOCKING — the aft spider's motor interface is the wrong pattern.**
`edf_aft_spider_sleeve.scad` mounts the motor on **three arms at 120°** with
three M3 pockets. The motor takes **four screws**. Three holes at 120° cannot be
made to coincide with four at 90°, and using three of the four would need them at
90/90/180 — which these arms are not at either. This is not a clearance problem.

`MOTOR_BOLT_R = 10.0` was *also* never verified and the listing does not publish
a bolt circle, so **both the count and the radius are unknown**. Changing 3 → 4
arms now would swap one unsupported assumption for another, so the sleeve is
flagged and left as-is. **Do not print it for flight.**

**What to measure off a physical motor — five minutes with a caliper:**
- bolt-circle diameter;
- screw thread (M2 / M2.5 / M3) and length;
- whether the four holes are on a square (90°) or a rectangular pattern;
- motor overall length (the "2627" designation implies 27 mm and the SCAD assumes
  ≈27 mm, but 76 − 38.6 = 37.4 mm of the drawing is motor *plus* spinner and hub,
  so it does not confirm it);
- motor-alone weight, which closes the mass question in the BOM row.

#### Phase-lead route matches the corrected bays

The EDF2 spider arms were re-clocked to 105/225/345 (below). Against the
corrected bay azimuths that still works, and works *better* for one side:

| | bay azimuth | nearest arm | circumferential run | annulus alive to |
|---|---:|---:|---:|---:|
| bay A | 55° | 105° | 50° ≈ 29 mm | Z 162.5 at the arm |
| bay B | 235° | 225° | **10° ≈ 6 mm** | Z 146.0 at the arm |

Both runs are in a live annulus. Putting **ESC2 in bay B** makes its phase run to
the EDF2 spider almost direct.

#### But the annulus straddles the pivot — it is not aft of it

This is the finding that matters more than the envelope, and it contradicts an
assumption this repo has been carrying since plan 003 KTD8.

**The bays are centred at Z 113. `PIVOT_Z` is 113.8.** An ESC placed there
contributes essentially **zero** CG offset. KTD8's "+3.91 mm from relocating
ESC1 aft" was computed with the ESC at Z 150.6 — a station no ESC can occupy.
Searched for a bay lying wholly aft of Z 130, the aft cowl gives at most:

| depth | best bay wholly aft |
|---:|---|
| 3.0 mm | 62 × 18 mm (1116 mm²) |
| 4.0 mm | 23 × 30 mm (690 mm²) |

Neither is an ESC. **There is no genuinely-aft ESC station in this pod.**

| ESC placement | `PIVOT_Z` | clr, 40 mm flaps | clr, 30 mm flaps |
|---|---:|---:|---:|
| KTD8 assumption — both at Z 150.6 | 113.8 | −2.57 | +7.43 |
| both in the real bay, centroid 113 | 110.1 | −6.21 | +3.79 |
| both in the 4.0 mm bay, centroid 117 | 110.5 | −5.82 | +4.18 |
| ESC1 in the bay, ESC2 at 150.6 *(if it can be sited)* | 112.0 | −4.39 | +5.61 |
| ESC1 forward at 59.4 (pre-KTD8) | 109.4 | −6.98 | +3.02 |

**So the ESC-aft lever is mostly unavailable, and the hollowing is carrying the
CG.** Of the two levers measured on 2026-08-31 — hollowing +6.16 mm, ESC1 aft
+3.91 mm — the second is worth about **+0.4 mm** at the station the pod can
actually offer, not +3.91. The remaining clearance gap has to come from the
nozzle stack (plan 005 R1's flap trim, KD5's deferred stator compression) or
from the landing gear.

**Recommended board target:** **60 × 38 mm, ≤ 5.0 mm total stack height**, two
bays at azimuth 25° / 205°, Z 94–132. If the height can be held to 4.0 mm the
bay grows to 61 × 46 mm and moves 8 mm aft (Z 94–140, centroid 117), worth a
further +0.4 mm of clearance.

#### The phase-lead path to the aft motor — measured, and it was closed

*"The power has to get to the motor."* It does, but only after one change.

EDF2's motor sits at the duct centre, so the **only solid bridge from the annulus
to it is a spider arm**. The phase bundle must therefore cross the bore wall
**at an arm azimuth** and **inside the arm's axial band** — Z 144–152 for
`EDF2_SPIDER_Z` = 148 with `SPIDER_ARM_H` = 8.0.

Measured aft limit of the annulus (depth ≥ 3.5 mm, enough for a 3 × Ø3 mm
16 AWG flat bundle — Ø3 mm per `docs/TILT_SPAR_ANALYSIS.md`):

| azimuth | 0 | 45 | **105** | 120 | 165 | 225 | 240 | **285** | 345 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| alive to Z | 135 | 146 | **163** | 146 | 136 | 146 | 147 | **163** | 136 |

At the as-built arm clocking of 0/120/240 the overlap with the arm band was
**0.0 mm (az 0), 1.5 mm (az 120), 2.5 mm (az 240)** — against ~3.5 mm needed.
**The route was effectively closed**, and the aft spider sleeve carries no wire
feature of any kind (no `wire`/`cable`/`ESC` geometry in the file).

**Fixed at Rev T4b: the EDF2 spider arms re-clock to 105/225/345.** 105° and 285°
are the pod's two deep lobes, alive to Z 163 at 6.2–6.4 mm — and they are where
the ESC bays land anyway (bay centres measured at azimuth **90°** and **270°**,
spans 25–155 and 205–335). An arm at 105° therefore sits directly beneath bay A,
so the crossing needs **no circumferential run at all**: the bundle drops out of
the bay, runs aft in the annulus at 6.2 mm depth, and crosses into the arm.

Nothing constrained the old clocking — the motor's own three-hole pattern rotates
with the arms (`MOTOR_BOLT_R` pockets are co-angular), and 105/225/345 stays 75°
clear of the key and retention angles at 30/150/270.

**Still to build, and it needs the outline first:** the bore-wall crossing slot
(≈ 9.5 × 3.5 mm at az 105, Z 144–152) and an open groove along the arm's forward
face carrying the bundle from r 26 in to the motor at r ≈ 10. The arm is 6.0 mm
wide × 8.0 mm tall, and a Ø6.5 through-hole would leave no wall — so it must be a
**surface groove, not a bore**, or the arm is locally widened.

**No seat geometry is built.** The above is an envelope; cutting a pocket before
the outline freezes would be building to a guess. It is one parametric block
once the outline is known.

- **U4 (parametric ESC seats) — still OPEN, now gated on the board outline
  rather than on missing data.** Its own
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
