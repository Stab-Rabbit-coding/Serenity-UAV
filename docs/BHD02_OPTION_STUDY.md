# BHD-02 Option Study — Landing-Gear Bays vs Wing Root

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation here
> **must be independently reviewed and accepted by a properly qualified
> individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.** It informs
> engineering judgment; it does not replace it.

Status: **analysis complete, three owner decisions open** (2026-10-10).
Parent finding: BHD-02 in
[CARGO_BULKHEAD_FIT_CHECK.md](CARGO_BULKHEAD_FIT_CHECK.md); WBS
`airframe/fuselage-mid/WBS.md` §1.1.1.2.2 item BHD-02.

## 1. What the per-feature census found

`tools/landing_gear_bay_function.py` renders each gear-bay feature alone from
the real SCAD modules, poses it at all four corners as `hull_legs()` does,
sweeps the leg 0–26° (22° full stroke + 4° margin) and intersects every
feature with every bulkhead-context solid. Run 2026-10-10, gear SCAD sha
`e0c7d6239ef3f097`.

- **The fore bays sit entirely inside the wing-root flange footprint.** The
  bonded flange (80 × 60 mm, Rev T1c) was added after LG-10 sited the fore
  bays and was never cut for the well. Bay ∩ flange is 954 mm³ (port) and
  1,616 mm³ (stbd).
- **The swinging thigh hits the flange**: 607 / 542 mm³ over the sweep. No
  change to the gear can clear it, because the thigh has to swing.
- **The fore bays' top flange and upper M3 sit on the CF spar**: cowl ∩ spar
  956 / 950 mm³, bolt keep-out ∩ spar 477 mm³ each side.
- **The wire-seat clusters hit the wing**, at all four corners. Aft: carrier
  646 / 697, bosses 329 / 355, seats 78 / 83 (functional), pads 40 / 45 mm³.
  Fore: carrier 262 / 428, pads 43 / 85 mm³.
- **The aft-station bay prints as two bodies** (new, see §5). The published
  `lg_r6_common_bay.stl` has 16,225 + 6,236 mm³ disconnected: the boss
  cluster that carries the wire seats is not joined to the liner at the aft
  datum (`BAY_STANDOFF` 1.85). At the fore datum (4.91) it is one body.

## 2. Option A — cut the root flange for the fore well

Picture: [A_flange_cut_port.png](images/bhd02/A_flange_cut_port.png). Tan is
the flange that stays, red is the cut, green is the gear through the
flange's thickness, and black is the CF spar.

**Geometry.** The cut is the wall-plane projection of everything the fore
gear puts through the flange slab: the option-C reshaped bay, the relocated
M3 keep-outs, and the leg swept 0–26°. It is offset 1.5 mm and taken through
the full thickness, so the part stays a clean, printable through-pocket.

- Removed per flange: 8,705 / 8,369 mm³, 4.5 / 4.4 g at 40 % infill.
- Two islands fall off and are dropped: 765 / 656 mm³ at the aft-lower
  corner, plus a 41 mm³ chip inside the aperture.
- Gear ∩ cut flange: 0 mm³ through the whole sweep.
- The cut touches the spar bore edge (2.2 mm³ ∩ the Ø20 spar envelope). The
  socket shear is carried by the shell spar boss, not the flange
  ([WING_ATTACH_INTERFACE.md](WING_ATTACH_INTERFACE.md) §3.3), so this nick
  does not cost shear capacity. It does cost the flange's local bond ring.

**Loads.** The load is the ultimate wing root moment, 14.60 N·m
(129.2 lbf·in), from [WING_ATTACH_INTERFACE.md](WING_ATTACH_INTERFACE.md)
§2.1. It is reacted by the bonded footprint, about the hull Y axis. The
footprint is rasterised at 0.25 mm and three models are evaluated:

- *doc* — the generator docstring's own method, F = 3M/(2h) over A/3. It
  reproduces the published baseline: FOS 26.4–26.7 on the measured bored
  area vs 29.2 on the 80 × 60 nominal.
- *bonded* — linear stress about the net footprint's centroidal axis,
  σ = Mc/I. The bond in tension (peel) is the honest case and governs.
- *bearing* — a rigid plate rocking on either edge, with triangular pressure
  over the material actually present.

Results, intact → cut (port; stbd within 6 %):

- Area 4,353 → 2,756 mm² (6.75 → 4.27 in²). The centroid moves up from
  Z 66.9 to 76.1, away from the fore well.
- I 2.55 × 10⁶ → 1.51 × 10⁶ mm⁴.
- σ bonded 0.228 → 0.475 MPa (33 → 69 psi), which governs.
- σ bearing 0.122 → 0.284 MPa.
- **FOS 21.9 → 10.5 (stbd 11.1) vs the 4.0 target: passes.**

The allowable is 5 MPa, bond-limited CF-PETG, from
[structural_analysis.md](structural_analysis.md). That document says the
figure predates any cited test value: **ASSUMED, not verified**. The FOS 4.0
target is the project's response to the §23.2265 special-factor requirement
of 14 CFR Part 23 [REF-FAA-004]. Part 107 imposes no structural basis, so
this criterion is self-adopted.

The cut is the only change that clears the thigh. The flange keeps more than
2.5× the margin it needs. The cost is a different bonded part shape, and the
wing-attach interface document must be revised to match.

## 3. Option B — wire-seat clusters vs the wing

### B1 — rotate the wire cluster down (rejected)

The whole cluster (crank socket and chord, `CRANK_AZ` and `CHORD_AZ`
together) was rotated about the hip pin by Δ. That keeps the 90° crank-to-
chord transmission angle, so every load is unchanged by construction. The
full census was re-run at each Δ:

- Δ 15°: wing clash 3,161 mm³ total. The thigh already strikes the bay
  (21.6 mm³).
- Δ 20°: wing clash 2,577 mm³. Thigh strike 100.2 mm³.
- Δ 30°: the aft clusters clear the wing (seats 0 mm³). Thigh strike
  563.1 mm³.

The clear-of-wing angle and the clear-of-thigh angle do not overlap. At every
Δ tried, the cluster also separates from the liner (2 bodies). Rotating the
cluster also drives the **fore** clusters further into the wing leading-edge
root (carrier 262 → 543–691 mm³). **Rejected.** Picture:
[B1_rejected_thigh_strike.png](images/bhd02/B1_rejected_thigh_strike.png),
where red is the swept thigh ∩ bay at Δ 30°.

### B2 — relieve the wing around the cluster (recommended)

The pocket in each wing is the dilated (1.5 mm) cluster ∩ the wing.

- **Aft corners:** convex-hull pocket, one clean cut. The raw union shatters
  the section into about 50 slivers.
  - Pocket 2,062 / 2,264 mm³, 1.1 / 1.2 g. It sits under the root trailing
    edge (Y 75–122, Z 58–73) and is 14.9 mm deep.
  - 43.9 / 43.4 mm clear of the CF spar.
- **Fore corners:** a conforming pocket on the option-C reshaped bay. A hull
  here would bridge the spar relief and break the wing's spar-bore wall
  (0.2 mm left).
  - Pocket 588 / 807 mm³ at the root leading edge.
  - **Wall left to the spar bore: 4.1 / 3.5 mm.**

**Loads.** The upper bound puts the whole 14.60 N·m on the printed wing
section at the pocket station, as if the CF spar carried none of it. In
reality the spar alone already gives FOS 9.0
([WING_ATTACH_INTERFACE.md](WING_ATTACH_INTERFACE.md) §2.2).

- σ intact 4.6 MPa → relieved 4.7 (aft) / 5.3–5.8 (fore) MPa, vs the repo's
  27.5 MPa CF-PETG allowable (`SIGMA_ALLOW_PETG`,
  `tools/landing_gear_r6_sizing.py`; source [REF-MAT-002]).
- **FOS ≥ 4.8 even in that bound.**
- Torsion at the 0.41 N·m ultimate: τ ≈ 0.14 MPa, negligible.
- Section-area loss: 10.4–10.6 % (aft), 6.7–9.1 % (fore).

Pictures: [B2_aft_port_wing_relief.png](images/bhd02/B2_aft_port_wing_relief.png)
and [B2_fore_port_wing_relief.png](images/bhd02/B2_fore_port_wing_relief.png).

**Aerodynamic note.** The pockets are filled by the bay hardware they clear,
so the open area is the 1.5 mm clearance band plus the boss gaps. They sit on
the lower surface at the wing–body junction, where the flow is already
dominated by the junction. No drag figure is claimed: none has been computed.

## 4. Option C — shared vs handed fore bays

The starboard corners are **rotated** (az 180 − port), not mirrored. So the
CF spar crosses the fore bay's top flange at leg-local +y on port and −y on
starboard. The spar relief (Ø20 + 2 × 1.5 mm) costs the upper M3 on that
side. That bolt drops 24 mm down its side flange, to plate z +7. Bolt loads
use the LG-02 method of `tools/landing_gear_r6_sizing.py`: hip moment
48.8 N·m prying about the lower bolt line, and F_leg 610 N shared by 4 bolts.
The baseline reproduces the sizing script exactly: T 359 N, V 152 N,
R 390 N, bearing FOS 5.39.

- **Handed** (2 part numbers; one upper bolt moved per part):
  - Levers 68 / 44 mm; T 506 / 327 N (114 / 74 lbf).
  - Tension FOS 7.0. **Bearing FOS 3.97.**
  - 1,304 mm³ removed; 1 body.
- **Shared** (1 part number; both upper bolts moved):
  - Levers 44 / 44 mm; T 555 N (125 lbf) each.
  - Tension FOS 6.3. **Bearing FOS 3.65.**
  - 2,608 mm³ removed; 1 body.

Both fall just short of the 4.0 bolt-bearing target. Bearing capacity scales
with the bearing stack, which is 10 mm today (wall + 5 mm boss + 3 mm backing
plate, 2,100 N). A **4 mm backing plate** (11 mm stack, 2,310 N) gives FOS
4.38 handed and 4.02 shared. The relocated bolt has 4 mm to the plate's outer
edge at y 22 (e/d 1.2). It should move to the flange centre at y 21, which
gives 5 mm each side (e/d 1.5).

The hull pocket bores in `merge_cargo_interior.py` (`LG_BOLT_*`) must follow
whichever pattern is chosen, per corner.

Picture: [C_handed_vs_shared.png](images/bhd02/C_handed_vs_shared.png),
leg-local from outboard. Left is the handed port part, right is the shared
part; red is the material removed.

## 5. Gear defect found on the way (any option)

The aft-station bay (`BAY_STATION="aft"`, which is also the default, so it
is what `lg_r6_common_bay.stl` publishes) is **two disconnected solids**.
The boss carrier no longer reaches the liner walls at that datum. That means
the wire bosses, and so the energy absorber, would print as a loose block.
The body-count check the SCAD comments claim was evidently last run at an
older datum. The census tool now gates it on every run, at both stations.

## 6. Not studied

Moving the fore bay station clear of the flange footprint (Y −9…51) is the
alternative named in the WBS. It would put the fore hips forward of
Y ≈ −36. That moves the feet, the stance and the static share, so it is a
landing-gear re-layout, not a BHD fix. It was not sized here.

## 7. Recommendation (for owner decision)

- **A: cut the flange.** FOS 10.5 vs 4.0, and it is the only way to clear
  the thigh.
- **B: B2, relieve the wing.** B1 has no feasible angle.
- **C: handed bays plus a 4 mm backing plate.** Bearing FOS 4.38. Shared
  reaches only 4.02 and loses both upper bolts.

## 8. Reproduce

```sh
/usr/bin/python3 tools/landing_gear_bay_function.py --export BASE
/usr/bin/python3 tools/landing_gear_bay_function.py -D CRANK_AZ=-52 \
    -D CHORD_AZ=38 --json b1_30.json --export b1_30
/usr/bin/python3 tools/bhd02_option_study.py --export DIR \
    --json docs/images/bhd02/bhd02_option_study.json --b1 30=b1_30.json
```

The pictures come from
`airframe/openscad/fuselage/cargo/bhd02_options_context.scad`, which is
import-only; the cameras are in its header. The numbers are in
[bhd02_option_study.json](images/bhd02/bhd02_option_study.json) and
[bhd02_b2_wing_section.json](images/bhd02/bhd02_b2_wing_section.json).

## 9. BHD-10 — Pilot aft-strip nodes vs the splice collar (pictures)

The Pilot nodes (FC2 port, FC3 stbd; pouched PocketBeagle 2 + cape,
58 × 22 × 37 mm, `tools/cargo_layout_fit.py`) reach 0.5 mm into the
cargo/middle splice collar. The overlap is **only at each node's
upper-outboard corner** (X −124.6…−110.8 port, Z 103.7…124), where the
collar ring follows the skin. The rest of the face is clear.
`tools/bhd10_aft_strip_options.py` builds each option against every
bulkhead-context solid. The static-gap target is 2 mm.

- **Baseline:** collar ∩ nodes 22 / 24 mm³, ∩ cable zones 19 / 19 mm³. The
  tilt controller boards are 1.6 mm forward.
  [BHD10_baseline.png](images/bhd02/BHD10_baseline.png)
- **O1, move the pair 2.5 mm forward:** clears the collar, but ∩ tilt
  controller boards 201 / 216 mm³ and ∩ tilt brackets 43 / 43 mm³.
  **Rejected.**
  [BHD10_O1_shift_fwd.png](images/bhd02/BHD10_O1_shift_fwd.png)
- **O2, relieve the collar ring behind each corner:** the pocket is the
  corner overlap plus 5 mm each side and 2 mm deep. It removes 596 mm³,
  8.9 % of the collar's cargo-side bond band (6,702 mm³, Y 121–129), and
  the collar stays one body. Every clash is gone. The minimum gap is
  1.05 mm, short of the 2 mm target. Closing that means a bigger pocket and
  more lost bond band. The collar's bond capacity has not been
  re-evaluated: do that before choosing this.
  [BHD10_O2_collar_relief.png](images/bhd02/BHD10_O2_collar_relief.png)
- **O3, a 2.5 mm thinner pouched stack (22 → 19.5 mm):** clears everything,
  with only the existing 1.6 mm to the boards. It is legal only if the
  first-article stack measures that. `cargo_layout_fit.py` marks the 22 mm
  figure VERIFY, and nobody has measured it yet.
  [BHD10_O3_thin_stack.png](images/bhd02/BHD10_O3_thin_stack.png)

Recommendation: **measure the first-article stack (O3) first.** It costs
nothing if the stack is ≤ 19.5 mm. Fall back to O2 only after a bond check
on the collar. Numbers are in
[bhd10_aft_strip_options.json](images/bhd02/bhd10_aft_strip_options.json).

## 10. Owner decisions (2026-10-10) and what they imply

Decided by Stab-Rabbit-coding on 2026-10-10:

- **A: move the fore bay station.** Not the flange cut.
- **B: redesign the wire geometry.** Not a wing relief.
- **C: handed fore bays plus a 4 mm backing plate.**

### Fore station sweep

`bhd02_option_study.py --sweep fore-port` slides the hip along Y. It checks
the posed bay, the M3 keep-outs and the leg swept 0–26°.

- The first clear station is **hip Y −36**: 0 mm³ to the flange, spar,
  wing, head/cargo collar, chin nodes, cradle, harnesses and tilt drive.
- At −32 there is 1 mm³ into the flange, and at −28, 116 mm³.
- The feet move about 35 mm forward with the hip, so the wheelbase goes
  from 170 to 205 mm.
- The level four-point aft share rises from 43.1 % to 44.3 % per leg
  (24.2 → 24.9 J at 6 ft). The governing 6 ft tail-down case is unchanged
  (50 %, 28.07 J), so the wire schedule holds.
- **Consequence for C:** at that station the bay no longer touches the CF
  spar (spar 0 mm³ for hip Y ≤ −16). The relocated upper bolt that C
  answered for is not needed there. That has to be confirmed with the
  owner before any handed part is drawn.
- Still to check at the new station: the hull's sponson seat, the swept
  doors, and the re-cut hull pocket.

### Aft corners

Moving the aft station does not clear the wing. The wing clash is 874 mm³
at Y 100 and still 43 mm³ at Y 132. Rotating the whole wire cluster about
the hip by a large angle (crank and chord together, transmission angle
held) gives:

- 120°: the thigh strikes the cluster (2,729 mm³). Rejected.
- 180°: the cluster clears the wing and the bay is 1 body, but the bosses,
  carrier and pads hit the hull wall (189–211 mm³). The hull pocket would
  have to grow.
- **240°: the cluster clears the wing, the hull and the thigh sweep.** The
  carrier separates from the liner (2 bodies) and needs a new path to it.
  The wires and the extension-stop pin, now close together, are not yet
  checked.

At every angle, the **aft bay's top flange band and upper M3 keep-out still
hit the wing** (cowl 267 / 339 mm³, keep-out 60 / 61 mm³). That is the
plate height, not the wires. Dropping the upper bolts to plate z ≈ 20
(lever 57 mm) gives T 428 N. With the 4 mm backing plate (2,310 N) that is
bearing FOS 5.1, assuming the same 152 N shear.

### Fore station at the seat-solved hip X (correction)

The first sweep held hip X at −103.87, and it left the hull out of the
targets. Forward of Y −20 the cargo hull narrows and the belly rises (belly
Z 0 at Y −20, 19 at −30, 44 at −40). The hip X was therefore re-solved per
Y so the seat sits at today's depth (seat median −0.15 mm in the plate
frame, `mci.seat_offset`). At Y −38 the hip comes to **X −125.5**
(stbd −214.3), 21.6 mm inboard of today's.

- The bay is 50 % inside the hull envelope (today 51 %). The leg still
  reaches Z −80, so the 3 in belly clearance is kept at hip Z 38.
- **New clash:** the upper-forward liner corner and its upper M3 keep-out
  hit the TACCO CN2 chin pouch (237 + 64 mm³, up to 7.7 mm into its
  outboard edge at X −127.8). They also hit the chin shelf (20 mm³). The
  chin pair cannot move inboard: 2 × 37 mm plus the 10 mm channel fills the
  chin. This needs an **upper-forward corner trim** and a relocated upper
  M3 on the forward side only.
- **Seat curvature:** p10–p90 is 17.1 mm (today 10.8). The hull's flange
  rebate is 12 mm deep, so a flat-backed bay would leave skin standing
  proud. The rebate must deepen, or the back face must conform again.
- **Stance:** the feet move with the hip. The track narrows by about 43 mm
  (port foot 140 → 118 mm from the centreline) and the wheelbase grows from
  170 to 207 mm. The rollover margin has to be re-checked
  (`tools/landing_gear_foot_stance.py`).

Seat-solved hip X by station: Y −34 → −124.0, −36 → −125.0,
−38 → −125.5, −40 → −126.5, −42 → −127.5. TACCO overlap at those Y:
350, 357, 298, 294, 331 mm³. At Y −40 and −42 the head/cargo collar is
also touched (0.6 and 7.6 mm³).

Census JSONs:
[120°](images/bhd02/bhd02_wire_rot_120.json),
[180°](images/bhd02/bhd02_wire_rot_180.json),
[240°](images/bhd02/bhd02_wire_rot_240.json).

AI attribution: analysis, tools and text by Claude (Claude Opus 5.5,
Anthropic) on 2026-10-10, under the direction of Stab-Rabbit-coding.
Method: [build every joint in context through its full motion](solutions/design-patterns/build-every-joint-in-context-through-its-full-motion.md).
