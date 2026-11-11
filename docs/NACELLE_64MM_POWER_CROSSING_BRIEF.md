# Owner Decision Brief OD-17 — How the 4 × 10 AWG feed crosses the tilt joint (WA-R10)

**Revision:** Rev U, 2026-11-08 (Sprint 2, plan `docs/plans/2026-11-07-001-…`)
**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP (owner) — analysis and brief by Claude
(Anthropic, Claude Opus 5.5) under the author's direction.
**License:** CC BY-SA 4.0 — see LICENSES/CC-BY-SA-4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Format:** Owner Decision Brief (`docs/DOC_TEMPLATES.md`). Units: inches first, millimetres in parentheses.

## The problem in one paragraph

The four 10 AWG power conductors run from the wing to the nacelle inside the fixed Ø0.79 in (Ø20 mm)
CF spar, as the design intended (`docs/WING_ATTACH_INTERFACE.md` §2.3, WA-R11). The spar's open end is
inside the pod and **0.05 in (1.3 mm) from the duct wall** (measured 2026-11-07/08 on both live renders,
`tools/nacelle64_assembly_check.py --stage cable`). The two 6804 trunnion bearings ride directly on the
spar from X 1.49 to 2.04 in (37.8 to 51.8 mm), so the tube wall cannot be slotted there either. There is
**no path** for the wires out of the spar inside the current joint, at any wire size. The disconnect
bay they have to reach is now built (NAC-64-ASM-03). It sits 1.91 in (48.6 mm) forward of the tilt
axis and is open to the joint gap, and it travels 4.68 in (119 mm) along an arc as the nacelle tilts
through 140°.

![Joint section and the bay's path about the tilt axis](figures/nacelle64_war10_options.png)

*Left: Y = 0 section through the joint, with option paths drawn. Right: looking inboard along the tilt
axis; the red arc is the bay's path from −5° to +135°, the black arrows are its velocity direction when
tilting toward hover, and the wing-tip section is in cyan.*

## Options

- **A — Clock-spring (flat-conductor) ring in the joint gap around the trunnion flange.** The feed
  leaves the spar inside the wing, crosses the wing-tip face at r ≥ 1.15 in (29.3 mm), and wraps in a
  rolling loop inside a ring chamber at r 1.06–1.38 in (27–35 mm), 0.28 in (7 mm) long axially.
- **B — Enclosed free loop across the gap.** The feed leaves the spar inside the wing, exits a port on
  the wing-tip face near the leading edge, and runs as a flexible loop to the bay mouth inside a boot
  that spans the 0.35–0.48 in (8.8–12.3 mm) gap.
- **C — Through-bore slip ring at the tilt axis.** Four circuits of ≥ 28 A on the Ø0.79 in (Ø20 mm) spar.
- **D — Move the joint 0.91 in (23 mm) outboard** (first written as 0.71 in (18 mm); corrected 2026-11-08, see below). This opens a 0.96 in (24.3 mm) bend chamber between
  the spar mouth and the duct. The twist stays inside the spar bore, which is what the 0.06 in (1.5 mm)
  radial clearance there was sized for. The wires turn radially in the pod and run in the annulus to the
  bay.

## The six checks

| Check | A clock-spring | B enclosed loop | C slip ring | D joint +0.91 in (corrected) |
|---|---|---|---|---|
| **Statics and dynamics** | One conductor's 0.0082 in² (5.26 mm²) in a 0.28 in (7 mm) wide strip is 0.030 in (0.75 mm) thick. Rolled at the ~0.16 in (4 mm) radius the chamber allows, the bending strain is about 9 %, far past copper's yield, every cycle. **Fails.** | The loop is pulled through 4.68 in (119 mm) of arc per tilt cycle; port-to-bay distance 1.06 → 2.59 in (27 → 66 mm). Wire stiffness for 10 AWG silicone fine-strand is not in the repo, so the torque against the 16.0 lbf·in (1.81 N·m) tilt-drive limit **requires verification** (bench pull). | Not assessed beyond fit (below). | Hover thrust per nacelle ≈ 7.1 lbf (31.4 N). Moving it 0.91 in (23 mm) outboard adds ≈ 6.4 lbf·in (0.72 N·m) of bending at the wing spar root per side. Bearing loads unchanged. |
| **Function** | — | Works if the loop survives the flex cycles. 10 AWG fine-strand fatigue life over 140° cycles **requires verification** (cycle test). Exposed to FOD and debris in the gap unless the boot is sealed. | — | Wires bend once, statically. Twist (140°) is taken along the spar-bore length. Service is unchanged: slide the nacelle off the spar, and the bay is the junction. |
| **Structural integrity** | — | Boot attachments only; no load path change. | — | Longer spar overhang; pylon boss grows 0.91 in (23 mm); wire channels cut through the trunnion plug, collar and one bulkhead (0.42 in³ (6,907 mm³) removed in the concept); spar-root allowable not verified (`allowables.json`, SPAR-20-ALLOW). Re-check the trunnion register, collar inserts and wing-tip pad. |
| **Mechanism and component interactions** | Chamber r 27–35 mm collides with the wing-fixed pinion and its sweep (tip r 1.26 in (32.1 mm)) and the Ø0.16 in (Ø4 mm) shaft. **Fails.** | The loop must clear the pinion shaft (r 0.90–1.12 in (22.9–28.5 mm), aft of the axis), the trunnion flange, and the AK7455 encoder pad. The EMI spec asks for power-to-signal separation (`TILT_ENCODER_WIRING_EMI_SPEC` §2.3, not re-verified here). | Axial length of a 4 × 28 A slip ring is far more than the 0.35–0.48 in gap; no product verified. **Does not fit.** | The whole joint shifts together, so the gear mesh, bearings and encoder keep their relations. Every hull-frame placement of the nacelle, trunnion and pinion moves; the wing-tip pad and stub (`SPAR_TIP_PROTRUSION_64N`) change. |
| **Weight and balance** | — | +0.007–0.013 lbm (+3–6 g) per nacelle (longer feed plus boot, ESTIMATE). On the pivot station, so pitch CG barely moves. | Slip ring mass not verified. | Concept model: boss +0.076 lbm (+34.5 g) solid, channels −0.017 lbm (−7.7 g), spar +0.0083 lbm (+3.8 g): about +0.067 lbm (+30.6 g) per nacelle (ESTIMATE, boss not hollowed). Lateral CG moves outboard 0.91 in (23 mm), which raises roll inertia; pitch CG and pivot residual are unaffected because the mass sits at the pivot station. |
| **Canonical shape** | A ring fairing in the gap (inside the Ø2.76 in (Ø70 mm) collar footprint). | A boot visible in the 0.35–0.48 in gap between the pylon face and the wing tip. | — | The nacelle sits 0.91 in (23 mm) further from the wing tip, which visibly changes the wing–nacelle spacing against REF-CAD-003. Owner judgement. |

## Side by side

| | A | B | C | D |
|---|---|---|---|---|
| Feasible | No (copper strain, pinion) | Yes, if the loop passes a flex/fatigue test | No (does not fit) | Yes |
| Work | — | Wing-tip port and in-wing exit from the spar, boot, loop retention; bench flex test | — | Re-datum the joint: pod pylon, spar stub, wing pad, bake/assembly placements, re-sweep, re-converge the pivot |
| Risk | — | Fatigue; FOD; exposed in the gap | — | Canonical proportion; spar-root moment +6.4 lbf·in (0.72 N·m) |
| Mass per nacelle | — | +0.007–0.013 lbm (+3–6 g) | — | ≈ +0.067 lbm (+30.6 g) concept estimate |

## Option D, modelled (2026-11-08)

**Correction.** The 0.71 in (18 mm) shift was sized for one 0.217 in (5.5 mm) wire. The four wires
leave the spar as a 2 × 2 group, so the aft pair bends on a 0.87 in (22 mm) centreline radius when the
forward pair is at the 0.65 in (16.5 mm) minimum (3 × OD). At 18 mm the aft pair would leave the bend at
X 1.33 in (33.8 mm), inside the duct wall. **The minimum shift is 0.91 in (23 mm)**. That makes the spar
mouth X 2.39 in (60.81 mm), the bend chamber 0.96 in (24.3 mm), and both pairs clear the duct wall: they
leave the bend at X 1.53 and 1.74 in (38.8 and 44.3 mm). If the four are bound as one harness and must
bend at 3 × the bundle OD, 1.57 in (39.8 mm), the shift roughly doubles. That variant is not modelled.

Concept model (`tools/nacelle64_optD_concept.py --shift 23`, manifold3d booleans): the pod collar boss is carried 0.91 in
(23 mm) outboard; trunnion, spar, wing and pinion move with it; each wire runs from the spar bore around its
bend, forward in the annulus, fanning out to its stud; channels are cut through the pod. Results:
- The wires do not cross. Neighbours touch only where they run as the bundle; the closest non-adjacent
  pair is 0.090 in (2.27 mm) apart.
- The wires (which tilt with the pod) never touch the wing or the wing-fixed pinion from −5° to +135°.
- Channels remove 0.42 in³ (6,907 mm³) of pod material (trunnion plug, collar, one bulkhead web).
- Inside the spar the bundle takes the tilt as twist. The model spreads it over 2.76 in (70 mm) of spar
  bore; the real bore is longer, so the twist rate is lower.

![Option D, nacelle horizontal: top, bottom, front, back](figures/nacelle64_od17_optD_horizontal.png)

![Option D, nacelle vertical: top, bottom, front, back](figures/nacelle64_od17_optD_vertical.png)

*Pod, cartridge, wing and spar are drawn translucent so the wires show. Red ESC A +, blue ESC A −, orange
ESC B +, magenta ESC B −; gold studs in the disconnect bay; brown the wing-fixed pinion. The view window
is about 3.5 in (88 mm) tall.*

## Option D with the airfoil extended to the nacelle (owner question, 2026-11-10)

*Can the wing's airfoil be carried outboard, ahead of and behind the pivot, to the nacelle so the joint
is not a bare cylinder?* **Partly, and the gap can be kept small at every tilt angle.**

![Option D with a wing-fixed airfoil extension, top and front, 0 and 90 deg](figures/nacelle64_od17_optD_tip_extension.png)

*Tan: the airfoil extension (wing-fixed), modelled by extruding the wing's full-chord tip section from
X 3.32 in (84.3 mm) down to X 1.93 in (49.0 mm). Dark gray: the rotating collar boss, Ø2.13 in (54 mm),
that carries the trunnion in option D. Pod translucent.*

| Check | Finding |
|---|---|
| **Statics and dynamics** | The tilt axis runs spanwise, so tilting rotates every pod point about it without changing its spanwise X. The extension's outboard face can sit 0.04 in (1 mm) off the pod's inboard face (pod max X 1.89 in (48.0 mm) for r ≥ 1.18 in (30 mm)) and that gap stays 0.04 in at every tilt from −5° to +135°. The extension is wing-fixed and carries only its own air load, cantilevered 1.39 in (35.3 mm) off the tip. |
| **Function** | The joint is covered except for the collar. The collar is Ø2.13 in (54 mm) against an airfoil that is about 1.0 in (26 mm) thick at the tip, and it spans the front 58 % of the 3.7 in (94 mm) chord. **80 % of the collar's volume, 1.52 of 1.89 in³ (24,935 of 31,031 mm³), stands outside the airfoil**, above and below the forward half of the extension. |
| **Structural integrity** | The extension has to be bored for the collar (r 1.10 in (28 mm), 0.04 in clearance). That leaves only thin slivers ahead of the collar; most of the extension sits aft of it. |
| **Mechanism and component interactions** | The wing-fixed pinion reaches r 1.26 in (32.1 mm), outside the collar, so the extension needs a pocket for it as the pod relief does now. The wires stay inside the pod and are unaffected. The disconnect bay (r 1.91 in (48.6 mm)) never passes under the extension at any tilt, because the airfoil is only about ±0.5 in (±13 mm) thick. |
| **Weight and balance** | Extension 0.42 in³ (6,867 mm³) solid, 0.017 lbm (7.6 g) per side in PA CF before hollowing; wing-fixed, so the nacelle pivot is unaffected. |
| **Canonical shape** | The gap between wing and nacelle closes to 0.04 in (1 mm) along the chord, but a round hub about twice the airfoil thickness still shows above and below the leading half. Compare it to the canonical wing–nacelle junction (REF-CAD-003) yourself; I have not checked the reference images for this. |

**Ways to fair the collar as well:**
1. A body of revolution (spinner-like) on the collar. It rotates with the nacelle but looks the same at
   every tilt, and the wing-fixed extension wraps it with a constant gap. This is the cleanest fit to the
   constant-gap geometry.
2. Thicken the wing tip locally into a pylon fairing about 2.3 in (58 mm) thick that blends into the
   airfoil. This changes the canonical shape more.
3. Neck the collar down where it passes through the extension. The trunnion's register bore is Ø1.50 in
   (38.1 mm), so the collar cannot get below about Ø1.6 in (40 mm), still about 1.5 times the airfoil.

## Option D with an aft fairing behind the collar (owner direction, 2026-11-11)

*Fairing behind the collar, trailing edge on the line of the wing's trailing edge, thickened to the
best shape for airflow.* Built with `tools/nacelle64_optD_aft_fairing.py`.

**Shape.** A NACA 4-digit symmetric section puts its maximum thickness at 30 % of chord. Here the rotating
collar's widest point falls at 29–30 % of the room between the collar front and the wing TE line, so the
collar becomes the section's round nose and the fairing is the NACA tail behind it. The fairing's
half-thickness at the axis equals the collar radius + 0.04 in (1 mm), so it meets the collar tangent with
no step. Its trailing edge lies on the wing's TE line extended outboard. That line is swept: 6.85 in
(173.9 mm) at the wing tip, 6.35 in (161.2 mm) next to the nacelle. The TE is truncated at 0.08 in (2 mm),
the `AGENTS.md` §7 minimum wall.

![Aft fairing sections with cruise airflow](figures/nacelle64_od17_aft_fairing_section.png)

![Aft fairing, nacelle horizontal: top, bottom, front, back](figures/nacelle64_od17_aft_fairing_horizontal.png)

![Aft fairing, nacelle vertical: top, bottom, front, back](figures/nacelle64_od17_aft_fairing_vertical.png)

| Check | Finding |
|---|---|
| **Statics and dynamics** | The fairing is wing-fixed, loft-bonded 0.28 in (7 mm) into the wing's full-chord section (0.042 in³ (691 mm³) of overlap). It carries only its own air load over a 1.39 in (35.3 mm) span. Tilting rotates the pod about the spanwise axis, so its 0.04 in (1 mm) face gap cannot close. |
| **Function (airflow)** | Thickness 2.21 in (56 mm). The section's t/c is 0.61 at the wing tip and 0.76 next to the nacelle, fineness (chord ÷ thickness) 1.64 and 1.31. That is the best NACA-type tail that fits between the collar and the TE line, but it is still a thick, bluff section. Carrying the tail past the TE line to a fineness of about 3 would cut pressure drag further; the TE-line constraint is what limits it. No drag figure is computed here. |
| **Structural integrity** | Solid it is 1.77 in³ (29,011 mm³). As a 0.08 in (2 mm) SLS skin it can be hollowed; not modelled. There is a pocket for the wing-fixed pinion and a stepped bore that clears the pod's own collar (X ≤ 2.04 in (51.8 mm) within r 1.18 in (30 mm)). |
| **Mechanism and component interactions** | 0 in³ against the pod, collar, trunnion and cartridge at every 5° from −5° to +135° on the starboard model. Nearest gap to the pod and collar at 0°: 0.038 in (0.96 mm). 0 in³ against the pinion. The wires and the disconnect bay are inside the pod and unaffected. |
| **Weight and balance** | 0.071 lbm (32.2 g) per side solid in PA CF, wing-fixed, so the nacelle pivot is unaffected. Hollowing would reduce it. |
| **Canonical shape** | The joint reads as a round hub with a teardrop tail running to the TE line. The fairing is 2.21 in (56 mm) thick against the wing's ~1.0 in (26 mm) at the tip, so there is a thickness step where the fairing meets the wing (front view). A short spanwise glove blending the fairing down to the wing section over 1.5–2 in (38–51 mm) of wing would remove the step; that is a wing change and is not modelled. Owner judgement against REF-CAD-003. |

## Recommendation



**D**, if the 0.91 in (23 mm) change in the wing–nacelle spacing is acceptable to you against the
canonical references. It keeps the 28 A conductors inside protected structure, and it takes the tilt as
twist in the spar bore, which is what that bore was sized for. Nothing then flexes in bending each
cycle. Otherwise **B**, gated on a bench flex test of 10 AWG fine-strand silicone through the 140° cycle
before any part is drawn.

**Still unverified:** the conductor OD (SPAR-20-WIREOD; 0.217 in (5.5 mm) is assumed); the NASA-STD-8739.4A
bend-radius clause the repo cites; the 10 AWG loop stiffness and fatigue life; the spar-root allowable;
and every mass marked ESTIMATE.
