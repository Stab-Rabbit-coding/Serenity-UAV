# Landing-gear bellcrank load path: free-body study

**Status:** analysis complete; owner decision required (BUILD-BLOCKING, WBS LG-LOADPATH).
**Date:** 2026-10-26
**Author:** Claude (Claude Opus 5.5, Anthropic), under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3.
**License:** CC BY-SA 4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Numbers:** regenerate with `/usr/bin/python3 tools/lg_bellcrank_fbd.py --svg docs/images/lg_bellcrank`.

> **WARNING**
>
> The Rev R6 landing gear, as drawn and as resized by LG-REMASS, cannot carry
> its own internal loads. In a 4 ft crash the hip pin, the printed clevis ears
> and the printed wire sockets fail before the energy-absorber wires finish
> their stroke. A gear that breaks at the bay instead of at the wire fuse can
> let the aircraft strike on the nozzles or the belly. Do not build or fly the
> R6 bay until an option below is chosen, implemented and re-checked.

## 1. What was wrong

The thigh is a bellcrank. The ground pushes up on the foot at the horizontal
arm `R_H` = 80 mm from the hip pin. The energy-absorber wires push on a crank
of radius `r` = 6 mm around the same pin. `tools/landing_gear_r6_sizing.py`
solves the wire force from the **moment** balance, `F R_H = 2 P r`, so each
wire carries `P = F R_H / (2r)`, which is 13.3 times the foot force.

The sizing tool then checks the hip pin against the foot force `F` alone.
That is only correct if the two wires form a **pure couple**, meaning they push
in opposite directions on opposite sides of the pin. In the R6 layout both wires
of a row sit at the **same** crank azimuth and push the **same** way. The
**force** balance of the thigh therefore sends almost the whole wire pair, about
`2P`, through the pin, the clevis ears and the bay. The same error hides two
more failures:

- **Socket floors.** Each wire is a bowed column in compression. Its full
  end thrust `P` bears on the flat floor of a blind printed socket. That floor
  is about 28 mm² of CF-PETG.
- **Allowable.** The sizing used a 70 MPa CF-PETG "bearing" allowable. No
  source supports it. The repository's only CF-PETG compressive data is bulk
  ASTM D695 at 47–60 MPa [REF-MAT-001], and REFERENCES.md already flags a
  CF-PETG bearing allowable as "requires verification".

## 2. Load cases and dynamics (per leg, 13.0 lbm design mass)

The foot force is the same for every configuration. Only the internal load path
differs.

| Case | Definition | Touchdown speed | Energy per leg | Stroke | Foot force | Aircraft deceleration |
| --- | --- | --- | --- | --- | --- | --- |
| Static | stance, 25.1 % per-leg share (R2 ledger) | — | — | — | 3.3 lbf (15 N) | 1 g |
| **Normal** (LG-06) | 1.5 ft drop, stopped elastically inside the 13.7 mm hover nozzle clearance | 9.8 ft/s (2.99 m/s, 5.8 kt) | 4.9 ft·lbf (6.6 J) | 0.54 in (13.7 mm) | **218 lbf (969 N)** peak, linear spring | 67 g peak, level 4-point |
| **Crash** (LG-17) | 4 ft drop, tail-down 2-point, ductile plateau | 16.0 ft/s (4.89 m/s, 9.5 kt) | 26.0 ft·lbf (35.3 J) | 1.21 in (30.7 mm) | **258 lbf (1,148 N)** plateau | 40 g (2-point) / 79 g (level 4-point) |
| Hierarchy | owner rule: mounts ≥ 1.25 × the demand at the leg's own breaking moment (grown thigh 197.3 N·m) | — | — | — | 554 lbf (2,466 N) | — |

> **Note**
>
> The normal-landing peak of about 67 g is a direct consequence of the owner rule
> that a 1.5 ft drop must stop inside the 13.7 mm nozzle clearance: 9.8 ft/s
> arrested in 0.54 in. It is the same in every option. If 67 g is too much for
> the avionics mounts, the lever is the nozzle clearance (gear length or
> nacelle tilt at touchdown), not the bellcrank.

## 3. Free-body diagrams (4 ft crash, per leg, swing plane)

Hip pin at the origin. The foot force is blue, the wire forces green, the pin
reaction red. A red X and the red text mark each failure location.

| Current R6 + LG-REMASS (C0) | Option A: balanced couple | Option B: metal load path |
| --- | --- | --- |
| ![C0 FBD](images/lg_bellcrank/lg_bellcrank_fbd_C0.svg) | ![Option A FBD](images/lg_bellcrank/lg_bellcrank_fbd_A.svg) | ![Option B FBD](images/lg_bellcrank/lg_bellcrank_fbd_B.svg) |

Equilibrium of the thigh (planar rigid body, [REF-NCEES-009]):

- Moment about the pin: `F R_H = n P r`, with `n` the number of active wires.
- Force: `R_pin = -(F + Σ P_i)`. For C0 and B, `Σ P_i` ≈ `2P` along the
  chord, so `R_pin` ≈ 12.5 × `F`. For A, `Σ P_i` = 0, so `R_pin` = `-F`.

## 4. Results

Demand on each part is its failure-hierarchy demand: the 1.25 × leg-break
reaction for the pin and the ears, and 1.25 × the ductile plateau for the wire
path. "Margin" is capacity divided by demand, and 1.00 is the pass line.

### 4.1 Current design (C0): crank r 6 mm, same-side wire pair

| Location | Failure mode | Normal / crash / hierarchy pin reaction | Capacity | Margin |
| --- | --- | --- | --- | --- |
| Hip pin (M3 A2) | double shear | 2,718 / 3,221 / 6,918 lbf (12.1 / 14.3 / 30.8 kN) | 953 lbf (4,241 N) | **0.11, FAILS** |
| Clevis ears (printed, 2 × 3 mm) | pin bearing / crushing | as above | 203 lbf (902 N) | **0.02, FAILS** |
| Wire socket floor (printed, blind bore Ø5.92) | end-thrust crushing | 2,151 lbf (9,569 N) per wire | 291 lbf (1,294 N) | **0.14, FAILS** |

Even the **normal** 1.5 ft landing puts 2,718 lbf (12.1 kN) through the M3 pin,
2.9 times its capacity. The parts fail in this order: socket floors and ears
first, then the pin. The wire fuse never reaches its plateau.

### 4.2 Material preference (owner 2026-10-26)

Each load-path part takes the first material in this order that has a
**cited** allowable for its failure mode:

1. Printable composite (CF-PETG).
2. Pre-cut or laid-up CF, Kevlar or glass.
3. Aluminium, then brass.
4. Spring steel.
5. Stainless.

The energy-absorber **wires stay metal**, because the design relies on their
ductile and elastic behaviour.

- **Composites, skipped:** the repository has no cited pin-bearing, shear or
  through-thickness allowable for CF-PETG or for CF, Kevlar or glass plate.
  CF-PETG is used only in flat contact (47 MPa [REF-MAT-001]). The LG-11
  coupons would make the composites eligible.
- **Brass, skipped:** no verified allowable has been obtained yet.
- **Aluminium:** 6061-T6 [REF-MAT-007] is the first eligible metal for the
  pin, ear liners, side plates and spreaders.
- **Spring steel:** the wire end presses on its seat at 370–439 MPa, above
  6061's 276 MPa yield. The seat is therefore a short slug of ASTM A228 music
  wire (spring steel, Ø7 × 4 mm) [REF-MAT-008], sitting on a 6061 spreader
  disc.

### 4.3 Option A: balanced couple, crank r 10 mm

Each row (ductile, spring) puts one wire on each side of the pin with
antiparallel chords.

| Location | Failure mode | Part | Demand | Capacity | Margin |
| --- | --- | --- | --- | --- | --- |
| Hip pin | double shear | 6061-T6, Ø4 mm | 693 lbf (3,083 N) | 1,170 lbf (5,202 N) | 1.69 OK |
| Clevis ears | pin bearing | 6061-T6 liners, 2 × 1.5 mm | 693 lbf (3,083 N) | 745 lbf (3,312 N) | 1.07 OK |
| Wire end on seat | contact | A228 slug Ø7 × 4 | 53.7 ksi (370 MPa) | 230 ksi (1,586 MPa) min tensile | 4.29 OK |
| Slug on spreader | bearing | 6061-T6 disc | 21.6 ksi (149 MPa) | 40.0 ksi (276 MPa) | 1.85 OK |
| Spreader on bay | flat bearing on CF-PETG | 6061-T6 disc Ø13 × 1.5 | 1,291 lbf (5,741 N) | 1,402 lbf (6,238 N) | 1.09 OK |

- The pin reaction is the foot force alone: 218 / 258 / 554 lbf (normal / crash / leg-break).
- The wire force drops to 4,593 N per wire, so the ductile wire becomes about Ø4.44 instead of Ø5.27.
- The longer crank needs 3.84 mm of wire stroke for the 22° hip rotation. The 20 mm bow span gives 3.67 mm, so the span grows to about 21 mm.
- **Mass penalty: +12.0 g per leg, +32.2 g (+0.071 lbm) per aircraft**, net of the lighter wires.
- **Open packaging risk.** With the crank at 30°/210°, the lower wire's boss lies about 35 mm below the hip, and the hip is only 38 mm above the belly. The crank azimuth pair has to be re-screened in `tools/lg_wire_layout_study.py` and the 3-D census so that both bosses stay inside the canonical bay outline. This study has not proved that they can.

### 4.4 Option B: metal load path, R6 layout kept (r 6 mm)

The bay keeps its outline and the same-side wire pair. The 2P reaction is
carried in aluminium from the pin to the seats.

| Location | Failure mode | Part | Demand | Capacity | Margin |
| --- | --- | --- | --- | --- | --- |
| Hip pin | double shear | 6061-T6, Ø11 mm | 8,647 lbf (38.5 kN) | 8,845 lbf (39.3 kN) | 1.02 OK |
| Clevis side plates | pin bearing | 6061-T6, 2 × 6.5 mm | 8,647 lbf (38.5 kN) | 8,873 lbf (39.5 kN) | 1.03 OK |
| Wire end on seat | contact | A228 slug Ø7 × 4 | 63.7 ksi (439 MPa) | 230 ksi (1,586 MPa) min tensile | 3.62 OK |
| Slug on spreader | bearing | 6061-T6 disc | 36.1 ksi (249 MPa) | 40.0 ksi (276 MPa) | 1.11 OK |
| Spreader on bay | flat bearing on CF-PETG | 6061-T6 disc Ø17 × 1.5 | 2,151 lbf (9,569 N) | 2,398 lbf (10,668 N) | 1.11 OK |

- **Mass penalty: +32.2 g per leg, +128.8 g (+0.284 lbm) per aircraft.** In stainless it was +460.5 g.
- The 13.0 lbm target already lacks 0.34 lbm (handoff 2026-10-20), so Option B
  would nearly double the shortfall. Two 6.5 mm side plates and an Ø11 pin also
  do not fit the 14–16 mm lug and the bay aperture without re-drawing the bay.

## 5. Comparison

| | C0 current | A balanced couple | B metal load path |
| --- | --- | --- | --- |
| Worst margin | **0.02 (fails)** | 1.07 | 1.02 |
| Pin reaction, crash | 3,221 lbf (14.3 kN) | 258 lbf (1,148 N) | 3,221 lbf (14.3 kN) |
| Wire P, crash | 7,655 N | 4,593 N | 7,655 N |
| Ductile wire | Ø5.27 | about Ø4.44 | Ø5.27 |
| Load-path materials | printed only | 6061 pin / liners / spreaders, A228 seats | 6061 pin / plates / spreaders, A228 seats |
| Mass vs C0, per aircraft | 0 | **+32.2 g (+0.071 lbm)** | +128.8 g (+0.284 lbm) |
| Canonical outline | as drawn | thigh root ring grows; boss packaging **unproven** | side plates and pin do not fit the present bay |
| Failure hierarchy (fuse < leg < bay) | violated | met (as sized) | met (as sized) |

**Recommendation: Option A.** It meets the hierarchy at the lowest mass and
keeps the pin small enough for the present clevis. Its open item is geometric,
not structural: re-screen the crank azimuths so both bosses stay inside the
bay. If the LG-11 coupons give CF-PETG or CF-plate bearing allowables, the
6061 liners and spreaders become candidates for composite replacement, per
the owner's preference.

## 6. Ductile fuse material (owner 2026-10-26)

The ductile wire is a **fuse**: it must absorb the crash energy by yielding,
not spring back. `tools/landing_gear_r6_sizing.py` specifies it only as
"ductile-temper steel wire, flow stress ≈550 MPa", with no source.
`tools/lg_fuse_material.py` compares the candidates that have cited
properties. It uses the sizing tool's two-hinge bowed-wire model and judges
each one on the properties a fuse needs:

| Property | Why the fuse needs it | Check |
| --- | --- | --- |
| Yield (lower bound) | sets the plateau and the wire diameter | `d = (3 P h0 / Sy)^(1/3)` |
| Su / Sy | strain hardening raises the late-stroke plateau, and every mount demand with it (failure hierarchy) | ratio |
| Elongation | the wire must finish its stroke without cracking | middle-hinge strain ≈ Δφ (plastic-hinge length = one diameter, an assumption) |
| No ductile-brittle transition | a cold-day crash must still yield | FCC metals (Al, austenitic stainless, Cu) have none |
| Mass | eight ductile wires per aircraft | stock length × area × density |

Option A plateau (4,593 N per wire, 21 mm span, 3.84 mm stroke): estimated
hinge strain about **37 %**.

| Material | d (mm) | Mass, 8 wires | Su/Sy | Elongation | Strain margin | DBTT |
| --- | --- | --- | --- | --- | --- | --- |
| 6061-T6 [REF-MAT-007] | 5.59 | 21.7 g | 1.12 | 17 % | **0.5** | none |
| 304 annealed, ASTM A240 min [REF-MAT-006] | 6.17 | 77.6 g | **2.51** | 40 % | 1.1 | none |
| A228 music wire [REF-MAT-008] | — | — | — | — | — | yes |
| current "ductile steel 550" (uncited) | 4.44 | 39.9 g | unknown | unknown | unknown | yes |

**Findings:**

- **Music wire is right for the spring wires and the seat slugs, not the fuse.**
  It is a spring temper, and its source publishes no yield to size a plateau on.
- **6061-T6 has the flat plateau a fuse wants** (Su/Sy 1.12), but its 17 %
  elongation is half the estimated hinge strain. It would crack mid-stroke.
- **Annealed 304 is ductile enough** but work-hardens: Su/Sy 2.51. The
  late-stroke plateau can reach 2.5 times the design force, which multiplies
  every pin, ear and bay demand above by the same factor and breaks the
  failure hierarchy.
- **The bow geometry, not only the material, is the problem.** With the 3.5 mm
  pre-rise fixed, hinge strain falls only as about span^-1/2. Even an 80 mm
  span leaves 6061-T6 at margin 0.72. Option A's longer crank also needs
  more stroke (3.84 mm against 2.30 mm at r 6), which raises the strain.

**Brass and other metals (owner question, 2026-10-26).** No common metal gives
both a flat plateau and high elongation, because ductility comes with work
hardening.

- Annealed C26000 brass [REF-MAT-009] has 55 % elongation (margin 1.5 in
  bending) but Su/Sy up to 4.0, so the plateau can climb fourfold.
- Half-hard (H02) brass flattens the plateau (1.57) but drops to 15 %
  elongation (margin 0.4).
- Annealed 1008 steel [REF-MAT-010] has at least 35 % elongation but no
  published yield, and it has a ductile-brittle transition.

**Change the fuse's mode, not only its metal.** A straight wire yielding in
**axial tension** spreads its strain over the whole gauge length
(ε = stroke / L), instead of concentrating it in plastic hinges. At Option A's
plateau and stroke, with a 1.5× margin on total elongation:

| Tension fuse | d | Gauge length | Mass, 8 wires | Plateau rise Su/Sy | DBTT |
| --- | --- | --- | --- | --- | --- |
| **6061-T6** | 4.60 mm | 33.9 mm | **19.4 g** | **1.12** | none |
| 304 annealed | 5.34 mm | 14.4 mm | 48.7 g | 2.51 | none |
| C26000 brass H02 | 4.09 mm | 38.4 mm | 52.3 g | 1.57 | none |
| C26000 brass annealed | 7.65 mm | 10.5 mm | 95.5 g | 4.00 | none |

**6061-T6 in tension** meets all five properties on cited data, is the
lightest, and is the owner's preferred metal. It also suits Option A: a
balanced couple can be two **tension** fuses, one on each side of the pin.
Its open limit is that the flat plateau lasts only until the wire necks (the
uniform elongation). No cited source gives that figure for 6061-T6, so the
LG-15 bench firing has to measure it.

**What else would satisfy all five properties, not yet cited:**

- an annealed low-carbon steel or a work-hardening-limited aluminium (for
  example 5052 or 3003) with both a flat plateau and over 30 % elongation;
- or a different fuse architecture, such as a **crushable composite tube**
  (progressive crushing gives a flat plateau and is the owner's preferred
  material class).

Both need sources before they can be sized. The plastic-hinge-length
assumption needs a bench firing (LG-15), which is the real gate on any fuse
material.

## 7. Assumptions and verification needed

- **CF-PETG allowable.** 47 MPa, the low end of ASTM D695 bulk compression
  [REF-MAT-001], is used as the flat-contact limit under the 6061 spreaders. It
  is not a pin-bearing allowable. A real bearing coupon (LG-11, ASTM D953 or
  equivalent, printed in the part's own orientation) is still required. The
  spreader margins (1.09 and 1.11) are thin; the spreaders should grow one size
  when the layout is drawn.
- **Pin shear.** Pin shear uses 0.6 × the ISO 3506-1 tensile strength
  [REF-MAT-005]. That ratio is a design judgment and is marked "requires
  verification" in REFERENCES.md.
- **Metals.** 6061-T6 bearing uses its 276 MPa yield and shear its 207 MPa
  ultimate [REF-MAT-007]. The A228 seat contact is checked against the 230 ksi
  minimum tensile [REF-MAT-008], which publishes no yield. The slug mass uses
  the 7.90 g/cm³ steel density of [REF-MAT-006] as a proxy.
- **Load-case conventions.** Normal case is a linear spring with peak `2E/x`.
  Crash case is a constant ductile plateau `E/s`. Both are solved at the
  sizing tool's 25.1 % worst static share and the 50 % tail-down share.
- **Superseded check.** The sizing tool's `LG-02` / structure check of the hip
  pin against `F` alone, and its "bay boss bearing 6,300 N" (70 MPa × 90 mm²),
  are superseded by this study. Neither should be quoted as a margin.
