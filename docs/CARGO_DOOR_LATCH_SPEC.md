# Cargo Clamshell Door — Cross-Link + Positive Mechanical Latch, Rev A (2026-09-21)

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (model: Claude Sonnet 5, Anthropic) under the author's
direction, 2026-09-21, per `AGENTS.md` §3 AI attribution. Uses the `statics-and-dynamics`
and `mechanical-engineering` skills.
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a qualified
> engineer.** Every result, calculation, and recommendation in this document **must be
> independently reviewed and accepted by a properly qualified individual** — a licensed
> Professional Engineer or an equivalently qualified authority for the jurisdiction and
> discipline — **before it is applied to any system carrying risk to life or safety.**
> This informs engineering judgment; it does not replace it. It is reference material
> provided AS-IS, not a sealed or certified work product for this or any project.

## 0. Scope and what closes

Closes the **DOOR-LATCH finding** recorded in `docs/CARGO_DOOR_GATEWAY_SPEC.md` §8
("the clamshell doors have no positive in-flight latch; retention is servo gear-train
friction, forbidden for a flight-critical joint by root `AGENTS.md` §7") and answers the
owner's direction: *"cross-link the doors and add the positive latch in such a way that
the servo's bell-crank or some other component of the mechanism engages a lip or mortise
instead of the gear train holding the weight."*

Two mechanisms, both required, neither a substitute for the other:

1. **Positive latch (§1–3):** each door's own servo-driven bell-crank carries a hook that,
   at the door-closed position, engages a mortise cut into a **fixed** frame bracket. The
   hook/mortise interference — not the SG90's gear train — reacts the door-closed load.
2. **Cross-link (§4):** the two doors are tied to each other, not to each other's servos.
   A signed single-frame command drives both doors together (software), and a
   tongue-and-groove seam at the mating (free) edges keys the two door panels to each
   other when closed (structural) — deliberately **not** a rigid link between the two
   independent bell-cranks (§4.1 explains why that was rejected).

## 1. Governing load (statics)

**Free-body diagram (each door, closed, level flight):** isolate one door panel. Forces:
its own weight `W` at the panel centroid; the belly pressure differential `P` over the
panel area; the hinge reaction (2 DOF, along the piano-hinge axis, at 4 knuckles — treated
as one continuous line reaction); the pushrod force `F_rod` at the horn. Unknowns: hinge
line reaction (resultant + line-of-action) and `F_rod` — **determinate** once the
mechanism's geometry fixes `F_rod`'s line of action, by moment equilibrium about the hinge
axis (one non-trivial scalar equation once weight/pressure moments are known).

**Governing case: aerodynamic pressure at V_max, not the door's own weight.**

```text
V_max = 87 kt (14 CFR §107.51(a), REF-FAA-002 — the binding limit per
        docs/flight_envelope.md §2.1; §2.2/§2.3 are not converted to a speed)
      = 44.76 m/s
q = 0.5 ρ V² = 0.5 × 1.225 × 44.76² = 1226.9 Pa   (ISA sea level)

Worst door (stbd, 55.7 × 106.0 mm, docs/CARGO_SECTION_LAYOUT.md geometry):
  A = 5904 mm² = 0.005904 m²
  Cp = 1.0   (conservative, worst-case pressure coefficient — VERIFY: no
              drag/pressure polar exists for this airframe,
              flight_envelope.md §2.3)
  F_aero = q · A · Cp = 7.24 N
  r_cg   = half-width = 27.9 mm = 0.0279 m
  M_aero = F_aero · r_cg = 0.202 N·m

Door self-weight moment (closed & level, gravity ⊥ hinge-line, opening sense):
  M_weight = 0.0148 kg × 9.81 m/s² × 0.0279 m = 4.04 mN·m   — negligible vs M_aero
```

**Idealisations:** rigid panel, uniform pressure at `Cp = 1.0` over the full panel
(conservative — real Cp on a faired belly panel at zero incidence is well below 1),
quasi-static (no dynamic/gust amplification applied beyond the FOS below), frictionless
hinge and pivot pins.

**A real, quantified finding — not just "friction is bad practice":**

```text
SG90 stall torque = 1.8 kgf·cm @ 4.8 V (REF-ACT-003) = 0.177 N·m
M_aero / stall     = 0.202 / 0.177 = 1.14
```

**The SG90's own stall torque is smaller than the door-opening moment at the regulatory
V_max — with zero safety factor.** The gear train cannot hold the door shut at cruise
speed even under ideal, undamaged conditions. A positive mechanical latch is a hard
structural requirement here, not a best-practice margin call.

**Design load:** `FOS = 3.0` (design-team judgment, consistent with this repository's
existing practice of stating FOS as an explicit call rather than a code mandate — e.g.
the tilt actuator and structural-pin FOS values elsewhere in `docs/structural_analysis.md`).

```text
M_design = 3.0 × 0.202 = 0.605 N·m per door
```

## 2. Mechanism kinematics

**Geometry** (hull frame; port shown, starboard is a mirror about `X_CL = −169.85`):

| Feature | Station |
|---|---|
| Door hinge axis (piano-hinge pin, from `generate_cargo_doors.py`) | port X −117.53, Z 3.00; stbd X −222.68, Z 3.49, along Y (re-read 2026-09-21 against the current shell — see §7a) |
| Bell-crank pivot bracket | Y 39.33 (the door's 2nd hinge knuckle station — clear of the aperture rim at Y 2 and of the `GW-CARGO-DOOR` tray at Y ≤ −2), inboard 10 mm of the hinge line, 14 mm above the hinge Z |
| Drive arm (crank → door horn, via pushrod) | `r_A` = 5 mm |
| Latch arm (crank → hook) | `r_B` = 10 mm |
| Door horn (bonded to the door panel, projects toward the crank) | `r_H` = 8 mm |

**Kinematics.** The bell-crank rotates through the SG90's ~180° native range: `φ = 0` =
door closed (hook fully engaged in the mortise); `φ → 180°` = door open (matches the
doors' own documented 180° swing, `airframe/WBS.md` §1.1.0). The drive arm and door horn
form a standard 4-bar (crank–rocker) linkage via the 2 mm steel pushrod — the same
part class already in procurement ("Steel pushrod 2mm, Z-bend ends"). The latch arm is
rigidly fixed to the *same* crank, `20°` offset from the drive arm (`ANG_LATCH = 20°`,
`ANG_DRIVE = 200°` in the SCAD) — so hook engagement and the door's closed position are
the *same* shaft angle, not two things that can fall out of step.

**Why the linkage is sized away from an over-centre (toggle) point.** An over-centre
geometry (near-zero moment arm at `φ = 0`) gives the *linkage itself* enormous mechanical
advantage — but that advantage is a first-order function of a dimension a 3D print holds
to ±0.1–0.2 mm at best; a few tenths of a millimetre of tolerance stack can move the toggle
point enough to flip the linkage's self-locking sign entirely. This design instead uses a
generous, ordinary (non-singular) arm (`r_A = 5 mm`) and puts the *entire* closed-position
load path through the **hard mechanical stop** (§3), which is insensitive to that kind of
tolerance — a print that's 0.2 mm off still has a mortise the hook can't rotate through.

```text
pushrod force, F_rod = M_design / r_A = 0.605 / 0.005 = 121.0 N
2 mm OD steel wire, A = π(1.0 mm)² = 3.14 mm²
σ_rod = 121.0 / 3.14 = 38.5 MPa
```

Failure mode: tensile/compressive yield of the pushrod wire. Allowable: mild steel wire
yield ≈ 250–350 MPa (piano/music wire, if used, ≈ 1500–2000 MPa — REF-ID pending wire
spec sourcing, tracked in §6). **FOS ≈ 6.5–9** even on the conservative mild-steel figure.
Buckling (compression half-cycle, opening direction) is not governing at this force and
the pushrod's short unsupported length (≈ 35 mm) — not computed in detail here; flag as a
bench-verification item (§6) rather than assumed.

## 3. Positive latch — hook, mortise, and the load path that bypasses the servo

**The hook is a physical interference, not a friction detent or a toggle lock.** At
`φ = 0` the hook's L-shaped foot has rotated **under** a `2.4 mm` overhanging lip on the
mortise boss (a feature fixed to the airframe, `mortise_boss()` in
`door_latch_mechanism.scad`). Any moment trying to open the door acts on the crank in the
*same* rotational sense that would drive the hook's foot **further** under the lip — the
lip is a hard stop against that rotation, full stop, independent of whether the servo has
power, signal, or any holding torque at all. To open, the servo *actively* rotates the
crank the other way (`φ` increasing from 0), which is the *same* motion that slides the
foot back out from under the lip — no separate release actuator, no detent to overcome
"the wrong way."

**Load path in the latched (closed, unpowered-servo) state:** door panel → horn → pushrod
(§2, 121.0 N, 38.5 MPa, FOS ≈ 6.5–9) → crank drive arm → crank pivot → crank latch arm →
hook foot → mortise lip → fixed bracket → airframe. **The servo and its gear train are not
in this load path** — the crank is prevented from rotating by the lip, not by the motor.

```text
lip reaction, r_lip (hook contact radius from the crank pivot) = 10 mm
F_lip = M_design / r_lip = 0.605 / 0.010 = 60.5 N
```

**Bearing check (lip contact pad, 4 × 4 mm = 16 mm², CF-PETG):**

```text
σ_bearing = 60.5 / 16 = 3.78 MPa
```

Failure mode: bearing/crush at the lip contact face. Allowable: this repository has **no
verified CF-PETG bearing-specific test** — `REF-MAT-001` (Batista et al., *Applied
Sciences* 2023, tensile 39.23 MPa for 20 % short-CF PETG FFF) is used here as a
**conservative proxy** for bearing, exactly the treatment already flagged for the CF-PETG
bearing allowable elsewhere in this repository (`airframe/fuselage-mid/WBS.md` CARGO-03c;
`REFERENCES.md` Open Standards Verification Items). **VERIFY** with a real bearing coupon
(ASTM D953-class pin-bearing) before flight-article procurement.

```text
FOS_bearing = 39.23 / 3.78 = 10.4
```

**Shear check (hook root, 5 × 2.4 mm = 12 mm² cross-section):**

```text
τ_nominal = 60.5 / 12 = 5.04 MPa
```

Failure mode: shear at the hook's root, at a re-entrant corner (stress concentration).
`K_t ≈ 1.5` (unfilleted inside corner, order-of-magnitude estimate — the SCAD models the
hook root as a square corner; **apply a real fillet, ≥ 1.5 mm radius, in the printed part**
per the header note in `door_latch_mechanism.scad`, since OpenSCAD has no native fillet
primitive and CSG attempts at one produced a non-manifold mesh, §7).

```text
τ_applied ≈ K_t × τ_nominal = 1.5 × 5.04 = 7.56 MPa
τ_allow (distortion-energy estimate, isotropic) = 0.577 × 39.23 = 22.6 MPa
FOS_shear ≈ 22.6 / 7.56 = 3.0
```

**Caveat — FDM parts are anisotropic, this is order-of-magnitude only.** A von-Mises
shear estimate from an isotropic tensile figure is a first-cut check, not a validated
allowable for a layered print (`mechanical-engineering` skill rule 6). **Print the crank
with the hook-root shear plane in-plane with the layer lines** (i.e., orient the part so
the hook loads the print *along* a bead direction, not across interlayer bonds) and
confirm with a bench pull-test to the design load (0.605 N·m equivalent, or 60.5 N applied
directly at the hook) before flight-article use.

**Pivot pin and boss (3 mm steel pin, matching the existing door-hinge CF-rod convention):**

```text
F_pin = √(F_rod² + F_lip²) = √(121.0² + 60.5²) = 135.3 N
A_pin = π(1.5 mm)² = 7.07 mm²  →  τ_pin = 19.1 MPa   (steel, FOS large — not governing)
A_boss (⌀3 × 6 mm bore, CF-PETG) = 18 mm²  →  σ_bearing = 7.52 MPa  →  FOS = 39.23/7.52 = 5.2
```

**Modes checked and not governing:** pushrod buckling (flagged for bench verification, not
computed — short column, low force, but not zero-risked here), pivot pin shear (steel,
large margin), pivot boss bearing (FOS 5.2, per the same VERIFY caveat as the lip).
**Governing mode: hook-root shear, FOS ≈ 3.0**, the tightest of the checked margins and the
one most sensitive to the un-modelled fillet and to FDM anisotropy — the bench pull-test
in §6 targets this specifically.

## 4. Cross-link

### 4.1 What was considered and rejected

A rigid rod tying the port and starboard bell-cranks' rotation 1:1 (matching each crank's
throw) was the first design tried (an early draft of `door_latch_mechanism.scad` included
a third crank arm, `ARM_XLINK`, for exactly this). **Rejected:** the two doors are driven
by two independent, open-loop hobby servos (SG90, PWM position command, no shared
encoder/closed-loop torque sharing). Even with both servos commanded from the *same*
`DOOR_COMMAND` frame (§4.2), their mechanical slew is not simultaneous — a rigid link
between the two cranks would then fight itself on every transition, loading the pushrods
and pins with whatever internal force it takes to force the lagging servo's crank to keep
pace, well outside the §2–3 sizing, and risking exactly the class of joint failure root
`AGENTS.md` §7 exists to prevent. Reused terminology note: this is unrelated to, and does
not reopen, the LibreServo v2 differential-RS-485 cross-link question tracked for the
winch/nacelle-tilt servos elsewhere (`CAN-PERIPH-GW-1.md` §7) — that is a different servo
class on a different bus topology.

### 4.2 What is delivered instead

**(a) Software cross-link — already specified, cross-referenced here.** One signed
`DOOR_COMMAND` frame (`docs/CARGO_DOOR_GATEWAY_SPEC.md` §4) carries `{port, stbd} ∈
{OPEN, CLOSE, HOLD}` and both channels are written by the gateway firmware in the same
control-loop tick — the two doors are commanded together, not as two independent servo
targets a supervisory node happens to send close in time.

**(b) Structural cross-link — tongue-and-groove seam at the door-to-door mating edges.**
The two doors' free (inboard) edges meet at `X_CL` when closed (`airframe/WBS.md` §1.1.0).
Add a shallow tongue on the port door's free edge and a matching groove on the starboard
door's free edge (or vice versa — handedness is arbitrary), running the full `Y 2..108`
seam length:

| Parameter | Value | Why |
|---|---|---|
| Tongue height / groove depth | 3.0 mm | > 1/3 of the door's 8.6–8.7 mm thickness — enough to transfer meaningful shear without thinning either door's own section below the printable-wall minimum |
| Tongue/groove width | 4.0 mm, running the seam length | wide enough to print cleanly at 0.4 mm nozzle (10 perimeters-equivalent), narrow enough to leave clearance margin either side |
| Clearance | 0.3 mm per side | matches this project's established FDM clearance convention (e.g. `GAP_MM`/`RAIL_CLR` elsewhere in the cargo section) |

**What this buys, and what it does not.** The seam does not add a new actuator or a new
failure-independent retention path of its own — each door is still held shut by *its own*
bell-crank latch (§3). What it adds is **load-sharing at the mating edge**: if one door's
latch were ever to fail (hook print defect, pin failure, etc.), the interlocked seam
transfers part of that door's opening moment into the *other*, still-latched door and its
own hinge/latch load path, rather than leaving the failed door's full moment on its hinge
line alone. This is a **redundancy improvement, not a primary retention feature** — it
does not change the §1–3 sizing, which is already closed against each door's own full
`M_design` independently.

**Not implemented in this revision:** the tongue/groove requires an edit to
`airframe/stls/fuselage/cargo/generate_cargo_doors.py` (the door-panel generator) and a
regeneration + re-verification of both door STLs — deferred to **DOOR-SEAM-1** (§8) rather
than rushed through the existing, working door generator in the same pass as this new
mechanism. The dimensions above are the design input for that item.

## 5. Parts and BOM

New printed parts, `airframe/openscad/fuselage/cargo/door_latch_mechanism.scad`
(`PART=` selector, matching this repo's existing multi-part-per-file convention):

| Part | STL | Mass (as-rendered) | Qty |
|---|---|---|---|
| Bell-crank + pivot bracket + mortise, port | `door_latch_bracket_port.stl` | 3.55 g | 1 |
| Bell-crank + pivot bracket + mortise, stbd | `door_latch_bracket_stbd.stl` | 3.55 g | 1 |
| Door horn | `door_horn.stl` | 0.92 g | 2 (one per door) |

New hardware (reuses existing BOM part classes — no new supplier line needed):

| Item | Qty | Notes |
|---|---|---|
| Steel pushrod, 2 mm OD, Z-bend ends | 2 | one per door, crank drive-arm → door horn; existing procurement row |
| Steel pin, 3 mm OD × ~10 mm | 2 | crank pivot pin, matches the door-hinge `PIN-3X18`-class stock already in the BOM |
| M3 heat-set insert + screw | 4 (2/bracket) | bracket-to-airframe mount |

**Mass:** `2 × 3.55 + 2 × 0.92 ≈ 8.9 g` (0.020 lbm) at hull (X_CL ± 52.25, Y 39.33, Z ≈ 19).
Negligible CG shift (< 0.2 mm) at the cargo-delivery AUW — fold into the next A0 ledger
pass rather than computed to a false precision here.

## 6. Open items

| ID | Item |
|---|---|
| **DOOR-LATCH-1** | Bench pull-test the hook to the design load (60.5 N applied at the hook, or the 0.605 N·m equivalent through the linkage) — verifies the governing hook-root shear margin (§3, FOS ≈ 3.0, order-of-magnitude only) and the bearing proxy (§3, FOS 10.4, `REF-MAT-001` used as a stand-in, not a bearing-specific allowable). |
| **DOOR-LATCH-2** | Source a real pushrod wire spec (mild steel vs. music/piano wire) and cite it (`REF-ID` + `REFERENCES.md` entry) — §2's FOS range (6.5–9) currently brackets both. |
| **DOOR-LATCH-3** | Column/buckling check on the 2 mm pushrod in its actual unsupported length once the bracket-to-horn geometry is dry-fit (flagged, not computed, §2/§3). |
| **DOOR-LATCH-4** | Print the hook root with a real ≥ 1.5 mm fillet (OpenSCAD CSG attempt produced a non-manifold mesh, §7) — via FreeCAD/slicer post-process, and print-orient so the governing shear plane runs with the layer lines, not across them. |
| **DOOR-LATCH-5** | Dry-fit the bracket against the printed door panel and the published cargo shell (`tools/cargo_layout_fit.py`-style boolean check) once `SERVO-PLACE` (`docs/CARGO_DOOR_GATEWAY_SPEC.md` §8) resolves the SG90 hull-frame station — this document's `BRACKET_Y = 39.33` places the mechanism at a hinge knuckle station but has not yet been checked against the actual servo body/horn envelope. |
| **DOOR-SEAM-1** | Implement the §4.2(b) tongue-and-groove seam in `generate_cargo_doors.py`, regenerate both door STLs, re-verify (watertight, coaxial hinge bores unaffected, no interference through the 180° swing). |
| **DOOR-LATCH-6** | Firmware: the gateway's `DOOR_COMMAND` handler must sequence CLOSE as "drive to `φ ≈ 5°`, then creep to `φ = 0`" (a soft final approach) rather than a single full-speed move, so the hook doesn't repeatedly slam the lip at full SG90 slew rate — a fatigue/wear item for the CF-PETG lip, not a static-strength one. |

## 7. Verification

```text
$ openscad --check ... door_latch_mechanism.scad          PASS (syntax)
$ openscad -D 'PART="bracket_port"' -o ... .stl            exported, 3384 mm³
$ openscad -D 'PART="bracket_stbd"' -o ... .stl             exported, 3384 mm³, WATERTIGHT
$ openscad -D 'PART="horn"' -o ... .stl                     exported, 877 mm³, WATERTIGHT
```

`door_latch_bracket_port.stl` carries **one non-manifold edge** (4 faces sharing one edge,
everywhere else clean) — a floating-point coincidence from the `mirror()` operation that
does not reproduce on the starboard part built from the same source geometry. This is a
cosmetic mesh artifact (constant volume before/after, no missing/extra geometry, no effect
on the statics above, which is derived from the parametric dimensions, not the mesh) —
**not** a design defect, but it does need a standard slicer repair pass (Prusa/Orca "fix
mesh" or an external mesh-repair tool) before it is sliced. Logged rather than chased
further in this revision; re-verify after the fillet is added (DOOR-LATCH-4), since that
edit touches the same CSG neighbourhood.

No boolean check against the published cargo shell or the door STLs has been run yet
(DOOR-LATCH-5) — `BRACKET_Y`/`PIVOT_H`/`PIVOT_IN` are derived from the documented hinge
and knuckle geometry, not yet cross-checked against the shell mesh the way the
`GW-CARGO-DOOR` tray was in `docs/CARGO_DOOR_GATEWAY_SPEC.md`.

### 7a. Hinge-coordinate correction (2026-09-21, same day)

The door hinge coordinates this document was first written against
(port X −117.6/Z 5.11, stbd X −222.5/Z 5.22) were `generate_cargo_doors.py`'s
2026-06-22 output. The cargo shell has been re-merged many times since
(Rev T5–T5f); running the door generator against the *current* shell — done
this same day, while fixing an unrelated `ModuleNotFoundError` report — found
the belly surface had drifted, moving the hinge Z down ≈2.1 mm (port Z
5.11 → 3.00, stbd 5.22 → 3.49) and X by ≈0.1–0.2 mm. **Both doors and the
shell-side hinge-retention blocks (`cargo_hinge_retention.stl`,
`generate_cargo_hinge_retention.py`) were regenerated against the current
shell and re-merged** so the physical CF rod hinge pin actually aligns
between the door knuckles and the fixed retention bores — they did not,
against the committed geometry, before this fix. `door_latch_mechanism.scad`'s
`HINGE_X_*`/`HINGE_Z_*` constants and the table in §2 above are updated to
match; the bracket STLs were re-rendered (dimensions unchanged, the whole
mechanism just translates ≈2.1 mm in Z with the hinge).

**CARGO-HINGE-SYNC (open, not fixed here):** both
`generate_cargo_hinge_retention.py`'s `ROD_AXES` and this mechanism's
`HINGE_X_*`/`HINGE_Z_*` are still hand-copied duplicates of a fact
`generate_cargo_doors.py` already computes and prints — the exact failure
mode that caused this drift. A follow-up should have the retention-block and
latch-mechanism generators import or read these figures from a single
source (matching this project's own established convention, e.g.
`cargo_layout_t5_params.scad` for the cargo layout) rather than restate
them.

## 8. References

- `docs/CARGO_DOOR_GATEWAY_SPEC.md` — the gateway this mechanism's servos hang off, `DOOR_COMMAND` frame
- `airframe/WBS.md` §1.1.0 — door geometry, 180° swing, hinge stations
- `airframe/stls/fuselage/cargo/generate_cargo_doors.py` — door panel + knuckle generator (DOOR-SEAM-1 target)
- `docs/flight_envelope.md` §2.1 — V_max = 87 kt (REF-FAA-002)
- `REFERENCES.md`: REF-FAA-002 (14 CFR §107.51(a)), REF-ACT-003 (TowerPro SG90), REF-MAT-001
  (CF-PETG tensile, bearing proxy)
- root `AGENTS.md` §7 — prohibition on friction retention for flight-critical joints
