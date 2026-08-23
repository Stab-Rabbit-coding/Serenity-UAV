# Serenity UAV — Flight Envelope Document

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Revision:** Rev S (2026-07-12)

Resolves `TODO.md` Phase 0 pre-print documentation gate item "Flight Envelope
Document." All measurements are imperial-primary with metric in parentheses
per `AGENTS.md`. Airspeed in knots (kt) with m/s in parentheses.

**Baseline used:** Phase 5–10 configuration (nacelles only, no rear fuselage
EDF) — the active build target, since the rear EDF is "an optional addition
once everything else works" per root `AGENTS.md`. Phase 11 (full system,
heavier AUW) figures are given alongside for reference where they change the
result materially.

**Design inputs (traced to source, not re-derived here):**

| Quantity | Value | Source |
|---|---|---|
| AUW, Phase 5–10 | 6.10 lbm (2,768 g) → 27.15 N weight | `README.md` Specifications |
| AUW, Phase 11 | 6.90 lbm (3,130 g) → 30.71 N weight | `README.md` Specifications |
| Nacelle count / layout | 2 (port + starboard), each 2× 50 mm 6S EDF in tandem | `README.md` "Nacelles" |
| Static thrust per nacelle | 2,232 gf (2× 1,240 gf EDF × 90% stacking efficiency) | root `AGENTS.md` "Design Mission / Powerplant" |
| Total nacelle static thrust | 9.84 lbf (4,464 g) → 43.79 N | `README.md` Specifications (= 2 × 2,232 gf, confirms T/W below) |
| T/W, Phase 5–10 (hover) | 1.61 | `README.md` |
| T/W, Phase 11 (hover, nacelles only) | 1.43 | `README.md` |
| Nacelle tilt range | −5° to 140° hard stops; 0° = cruise (horizontal), 90° = hover (vertical), 120° = backing thrust | `README.md` "Nacelles" |
| Wing area (both wings) | 19,025 mm² (0.019025 m², 0.2048 ft²) | `airframe/openscad/wings/wings_s1223_revo.scad` |
| Airfoil | Selig S1223, t/c = 12.14%, camber = 8.65% | `wings_s1223_revo.scad`; UIUC Airfoil Database |
| CL_max | ≈ 2.0 at Re = 100,000 | Selig & Guglielmo wind-tunnel data, cited in `wings_s1223_revo.scad` |
| Root/tip chord, semi-span | 129 mm / 93 mm, 85.7 mm | `wings_s1223_revo.scad` |
| Air density (ISA sea level) | ρ = 1.225 kg/m³ | Standard atmosphere |

---

## 1. V_min — Minimum Control Airspeed vs. Nacelle Tilt Angle

This is a tilt-rotor, not a fixed-wing aircraft: weight is supported by a
combination of wing lift and the vertical component of nacelle thrust. At
tilt angle θ (0° = horizontal/cruise, 90° = vertical/hover):

```text
T_vertical(θ) = T_total × sin(θ)
L_required(θ) = W − T_vertical(θ)          [wing lift needed, if any]
V_min(θ)      = sqrt( 2 × L_required(θ) / (ρ × S × CL_max) )   if L_required(θ) > 0
V_min(θ)      = 0  (thrust alone supports weight — no minimum airspeed)   otherwise
```

**Critical tilt angle** — above which nacelle thrust alone supports weight
with zero forward airspeed (θ_hover, solving sin(θ) = W/T):

- Phase 5–10: **θ_hover ≈ 38.3°**
- Phase 11: T/W (nacelles only) = 1.43 is still > 1.0, so θ_hover exists
  but at a higher angle (thrust margin is smaller); not tabulated separately
  below — use the Phase 5–10 table with the understanding that Phase 11
  V_min values are higher at every angle below θ_hover (see Phase 11 column).

### V_min table

| Tilt θ | V_min, Phase 5–10 | V_min, Phase 11 (reference) | Note |
|---|---|---|---|
| −5° (hard stop) | 70.9 kt (36.5 m/s) | 74.8 kt (38.5 m/s) | Highest V_min in the envelope — nacelles trim slightly past horizontal |
| 0° (cruise) | 66.3 kt (34.1 m/s) | 70.6 kt (36.3 m/s) | Wings alone carry 100% of weight |
| 10° | 56.3 kt (29.0 m/s) | 61.2 kt (31.5 m/s) | |
| 20° | 44.4 kt (22.9 m/s) | 50.5 kt (26.0 m/s) | |
| 30° | 29.2 kt (15.0 m/s) | 37.8 kt (19.4 m/s) | |
| 38.3° (θ_hover) | 0 kt | > 0, higher angle | Thrust alone now equals weight |
| 60° | 0 kt | 0 kt | Fully thrust-borne |
| 90° (hover) | 0 kt | 0 kt | Fully thrust-borne |
| 120° (backing thrust) | 0 kt | 0 kt | Vertical component still exceeds weight (sin 120° = 0.866) |
| 140° (hard stop) | 0 kt | ≈ 0 kt, thin margin | Vertical component only 1.0 N above weight at Phase 5–10 AUW — **do not rely on 140° for sustained hover margin**; treat as a transient/backing-thrust extreme, not a hover trim point |

**Important caveat on CL_max:** the 2.0 figure is wind-tunnel data at
Re ≈ 100,000; this airframe's cruise Reynolds number at the wing root is
≈ 177,000 at 40 kt (`wings_s1223_revo.scad`), where CL_max is expected to be
at least as good, typically better, for the S1223 — using the lower-Re
figure here is conservative (over-predicts V_min slightly rather than
under-predicting it). No wind-tunnel or CFD validation at the actual
operating Re has been performed for this specific planform; treat the table
above as a design estimate pending flight test, not a flight-tested limit.

**Design implication:** at 0° tilt (pure fixed-wing cruise), V_min (66 kt)
exceeds the 40 kt reference speed used for the wing's Reynolds-number
citation elsewhere in this repository — this airframe's tiny high-wing-loading
planform cannot sustain level flight at 40 kt on wing lift alone. This is
expected and consistent with the design intent: Serenity UAV is a
hover-centric VTOL platform (root `AGENTS.md` design mission profile) where
wings are a lift *assist* during transition, not the primary lift source.
Sustained forward flight below θ_hover ≈ 38° therefore requires either
airspeed at or above the table value for that angle, or a higher tilt angle.

---

## 2. V_max — Never-Exceed Speed vs. Structural Load Limit and EDF RPM Ceiling

Three independent candidate limits were evaluated; the **binding (lowest)
limit governs**.

### 2.1 Regulatory ceiling

[REF-FAA-002] 14 CFR §107.51(a): maximum groundspeed ≤ 87 kt (100 mph) for
all Part 107 small UAS operations, regardless of airframe performance. This
is a hard legal ceiling independent of the aircraft's actual capability.

### 2.2 EDF RPM ceiling

`avionics/firmware/fc/src/governor_config.h` already defines the software
redline for the 50 mm nacelle EDFs:

```text
EDF_RPM_MAX_50MM = 35,000 RPM   (software redline; ESC over-speed protection is the hardware backstop above this)
```

This bounds the propulsion system's operating point but does not, by
itself, convert to an airspeed without a validated thrust/drag model at
that RPM — no drag polar exists yet for this airframe (parasite drag
estimate is not in the repository). The RPM ceiling is therefore carried forward as a
**propulsion-system constraint**, not converted into a fabricated top-speed
number here. Actual achievable top speed is a Phase 9 WBS output ("Thrust
stand calibration," "T/W measured" pass criteria, `TODO.md` §3.0 Phase 9).

### 2.3 Wing spar structural margin (order-of-magnitude check)

Using the wing spar stock already specified for procurement (CF tube,
12 mm OD × 1.5 mm wall, current-specification BOM "Structural Hardware")
and the conservative allowable stress methodology already established in
`docs/structural_analysis.md` §3 (σ_u ≈ 1,500 N/mm² conservative pultruded
CF estimate, FOS 4.0 design-team judgment value pending supplier test
certificates):

```text
Section modulus, tube:  Z = π(D_o⁴ − D_i⁴) / (32·D_o) = 116.0 mm³
Allowable moment:        M_allow = Z · σ_u / FOS = 43.5 N·m
Moment arm (conservative, per-wing lift at spar mid-semi-span):  0.5 × 85.7 mm = 42.85 mm
Total wing lift capacity at that moment:  L_total = M_allow / (0.5 × arm) ≈ 2,030 N
Solving V from L_total = 0.5·ρ·V²·S·CL (CL = 1.0, a maneuvering condition, not CL_max):
  V_struct ≈ 417 m/s ≈ 811 kt
```

This is a rough-order-of-magnitude strength check only — it does not
account for spar deflection/flutter, the wing shell's own load-sharing
contribution, or a validated CF-tube modulus (none is in the repository; this uses
strength, not stiffness). **Conclusion: the spar is not the binding
constraint by a wide margin** at any speed this airframe's propulsion
system could plausibly reach — 811 kt is roughly 9× the regulatory ceiling
and far beyond what a 50 mm 6S EDF tilt-rotor of this AUW/thrust class can
achieve. A dedicated spar deflection/flutter analysis remains a valid
future task but is not gating V_max determination here.

### 2.4 V_max determination

**Design never-exceed speed: V_NE = 87 kt (REF-FAA-002 §107.51(a)).** This
is the regulatory ceiling, not a validated aerodynamic or propulsive top
speed — the airframe's actual achievable maximum speed is expected to be
well below 87 kt given its small high-drag hover-centric planform, and will
be established empirically during Phase 9 performance tuning (thrust-stand
calibration + flight test) per the existing WBS, not asserted here without
flight data.

---

## 3. Altitude Operating Limits (AGL and MSL)

### 3.1 AGL — regulatory

[REF-FAA-002] §107.51(b): maximum altitude ≤ 400 ft AGL (unless within
400 ft of a structure). §107.51(c): minimum visibility 3 statute miles from
the control station. §107.51(d): minimum cloud clearance 500 ft below,
2,000 ft horizontal. These are hard Part 107 operational ceilings/floors
independent of airframe performance.

### 3.2 MSL — density-altitude margin on hover T/W

400 ft AGL itself changes air density negligibly (< 1.5%). The more
relevant question for a T/W-limited hover VTOL is **site (launch)
elevation**, since a higher-elevation operating site reduces air density
and therefore static EDF thrust for a given RPM/pitch (approximately
linear with density at fixed RPM for a static/low-speed ducted fan — a
standard first-order simplification, not a validated fan performance
curve).

```text
T/W(σ) ≈ T/W(sea level) × σ            where σ = ρ/ρ0 (density ratio)
T/W = 1.0 (bare hover floor) when σ = 1/1.61 = 0.621
```

Standard atmosphere reaches σ ≈ 0.621 at approximately **15,000 ft density
altitude**. This gives an operating-site elevation margin far in excess of
any plausible mission site for this airframe — the T/W design margin is not
the limiting factor for realistic operating elevations. This is a linear
first-order estimate; it does not model EDF/ESC behavior at reduced air
density in detail (motor cooling, ESC thermal derating at altitude are not
modeled here) and should not be read as validation for actual high-altitude
operation.

**MSL ceiling for this document: governed by the AGL floor at the intended
operating site plus the 400 ft AGL regulatory ceiling (§3.1)** — no separate
absolute MSL limit is imposed by aircraft performance within any elevation
range this project's mission profile (root `AGENTS.md`) contemplates.

---

## 4. Maximum Demonstrated Crosswind per Nacelle Angle Increment

**Status: not yet flight tested.** The word "demonstrated" in the
originating WBS item means flight-test data, which does not exist for an
airframe that has not flown. Fabricating specific crosswind-kt figures for
0°/30°/60°/90° without wind-tunnel, CFD, or flight data would violate
`AGENTS.md`'s prohibition on unverifiable values. What follows is the
computable engineering bound available today, plus the existing WBS
acceptance target.

### 4.1 Hover (90°) — thrust-margin bank-angle bound

In full hover, lateral station-keeping against a crosswind is achieved by
banking to vector part of the nacelle thrust laterally, at the cost of
vertical thrust margin:

```text
T·cos(φ) ≥ W  →  φ_max = arccos(W/T) = arccos(1/1.61) ≈ 51.7°
```

This is the maximum bank angle available while still supporting weight
vertically — an **engineering control-authority bound**, not a validated
crosswind knot figure (it says nothing about achievable bank rate, gust
response time, or control-loop performance). It is provided as a sanity
check that the T/W margin leaves meaningful bank authority for gust
rejection, not as a crosswind limit.

### 4.2 Design acceptance target (existing WBS)

`TODO.md` §3.0 Phase 9 already specifies the acceptance bar: **"Cross-wind
hover — verify stable hover in ≥ 10 kt headwind; document max demonstrated
crosswind."** That flight test is the authoritative source for this
section once flown. Until then:

| Tilt θ | Status |
|---|---|
| 0° | Pending flight test (fixed-wing-like weathervaning expected to dominate; not computed here) |
| 30° | Pending flight test |
| 60° | Pending flight test |
| 90° | Engineering bound: φ_max ≈ 51.7° available bank authority (§4.1); design acceptance target ≥ 10 kt (Phase 9 WBS) |

This table is to be filled in with real values during Phase 9 and this
document updated at that time — do not treat the blanks as "TBD forever";
they are flight-test outputs, not omitted analysis.

---

## 5. Transition Corridor — Minimum Safe Altitude to Initiate 90°→0° Sweep

`TODO.md` §3.0 Phase 9 sets the **tuning target**: "Nacelle transition
tuning — refine tilt servo rate and cross-axis coupling compensation;
target altitude excursion ≤ 0.5 m during 90°→0° nacelle sweep." That figure
is an aspirational post-tuning target, not yet flight-validated.

**Documented pre-validation operational floor: initiate a 90°→0° (or
0°→90°) nacelle sweep no lower than 20 ft (6.1 m) AGL** until Phase 9
flight test confirms the ≤ 0.5 m (1.6 ft) excursion target is met. This
gives > 12× margin over the tuning target, standard conservative practice
for an unflown transition maneuver on a design with no flight history. Once
Phase 9 flight-validates the excursion target, this floor may be revisited
and lowered — that revision is a flight-test-informed decision, not made
here.

---

## Summary Table

| Parameter | Value | Status |
|---|---|---|
| V_min at 0° (cruise) | 66.3 kt | Computed from design data |
| V_min at θ_hover ≈ 38.3° and above | 0 kt (thrust-borne) | Computed from design data |
| V_NE (never-exceed) | 87 kt | Regulatory ceiling (§107.51(a)); actual top speed pending flight test (Phase 9) |
| AGL ceiling | 400 ft | Regulatory (§107.51(b)) |
| MSL / density-altitude margin | ≈ 15,000 ft density altitude before T/W < 1.0 | Computed, first-order estimate |
| Max demonstrated crosswind | Pending flight test | Phase 9 WBS acceptance target ≥ 10 kt (hover) |
| Transition corridor floor | 20 ft (6.1 m) AGL | Conservative pre-validation policy |

---

*"We're on the leading edge of a new age." Also, apparently, of a fairly
generous V_NE margin over what a 50 mm EDF tilt-rotor can actually manage.
— paraphrasing Skipper, not verifying his airspeed indicator*
