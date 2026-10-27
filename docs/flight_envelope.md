# Serenity UAV — Flight Envelope Document

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Revision:** Rev T-SB (2026-10-26) — numbers recomputed for the split-battery aircraft by Claude (Claude Opus 5.5, Anthropic) under the direction of Stab-Rabbit-coding, per `AGENTS.md` §3. Rev S text by the author above; recompute tool `tools/flight_envelope_endurance.py`.

Resolves `TODO.md` Phase 0 pre-print documentation gate item "Flight Envelope
Document." All measurements are imperial-primary with metric in parentheses
per `AGENTS.md`. Airspeed in knots (kt) with m/s in parentheses.

**Baseline used (Rev T-SB):** the split main pack, two Tattu 6S 2200 95C cells
(cargo cradle + head), with the 8.0 oz (226.8 g) mission payload aboard. The
optional third cell is **unavailable on a payload mission**, because it occupies
the payload hooks (plan `docs/plans/2026-10-26-001-feat-split-battery-head-rail-plan.md`
R10). The three-cell case is given in §6 only as the maximum hover endurance with
no payload.

**Design inputs (traced to source, not re-derived here):**

| Quantity | Value | Source |
| --- | --- | --- |
| AUW, two cells + payload (governing) | 13.93 lbm (6,318 g) → 62.0 N weight | `docs/BATTERY_SPLIT_OPTIONS.md` §4 S1 (6,091 g) + 226.8 g payload (`README.md`) |
| AUW, two cells, no payload | 13.43 lbm (6,091 g) → 59.7 N | `docs/BATTERY_SPLIT_OPTIONS.md` §4 S1, built on `current-specification/auw_ledger.json` |
| AUW, three cells, no payload | 13.97 lbm (6,336 g) → 62.1 N | `docs/BATTERY_SPLIT_OPTIONS.md` §4 |
| Nacelle count / layout | 2 (port + starboard), each 2× 64 mm QX QF2822-2400KV EDF in tandem, co-rotating | `tools/auw_ledger.py`; memory/WBS NAC-64 |
| Rated thrust per fan | 4.71 lbf (2,135 gf, 20.9 N) at 57.0 A, 1,265.4 W, 22.2 V | [REF-EDF-003] manual sheet, QF2822-2400KV row |
| Total nacelle thrust | 18.83 lbf (8,540 gf) → 83.7 N | `tools/auw_ledger.py` (4 × 2,135 gf). **No tandem stacking loss is applied** (the Rev S doc used 90 %); if one exists, every T/W below is optimistic by it |
| T/W, two cells + payload | **1.35** | computed (8,540 / 6,318) |
| T/W, two cells, no payload | 1.40 | computed |
| Nacelle tilt range | −5° to 145°; 0° = cruise (horizontal), 90° = hover | `README.md` "Nacelles" |
| Wing area (both wings) | 19,025 mm² (0.019025 m², 0.2048 ft²) — planform unchanged | `airframe/openscad/wings/wings_s1223_revo.scad` |
| Airfoil | **S1223/t17.7 (root) / S1223/t26.7 (tip)** — S1223 camber line, thickness envelope scaled ×1.46 / ×2.20. **NOT an S1223.** | `wings_s1223_revo.scad`; `docs/WING_ATTACH_INTERFACE.md` §4A |
| CL_max | **UNKNOWN for the built section** — see the banner below; 2.0 (true-S1223) is used only so the numbers stay reproducible | Selig & Guglielmo, for the *unmodified* S1223 |
| Root/tip chord, semi-span | 129 mm / 93 mm, 85.7 mm | `wings_s1223_revo.scad` |
| Battery | 6S, 22.2 V nominal; pair 4.4 Ah; third cell 1.6 Ah; RTL trigger 3.30 V/cell | `docs/POWER_DISTRIBUTION.md` §2; `docs/failsafe_thresholds.md` |
| Air density (ISA sea level) | ρ = 1.225 kg/m³ | Standard atmosphere |

---

> ## ⚠ EVERY AERODYNAMIC RESULT IN THIS DOCUMENT IS UNVERIFIED AS OF REV S1e
>
> **The wing section changed on 2026-08-29 and this document has not been
> re-derived against it.** The Rev S1e spar migration scales the thickness
> envelope ×1.46 at the root and ×2.20 at the tip to swallow a Ø20.4 spar, so
> the built sections are **S1223/t17.7** and **S1223/t26.7** — not S1223.
>
> The **camber line is preserved exactly** (8.67 % at 49.0 % chord), which is
> the reason to expect the change to be less severe than the thickness numbers
> alone suggest: thin-airfoil theory makes zero-lift angle and lift-curve slope
> depend on the camber line and not on thickness. But that theory is valid for
> *thin* sections, and at 26.71 % t/c the tip is far outside its range.
>
> **`CL_max ≈ 2.0` does not carry over.** `c_l,max` depends on the thickness
> distribution, the leading-edge radius (now 2.1× the baseline at the root and
> 4.8× at the tip), and the laminar separation bubble — all three changed. It
> can only come from measurement or computation at the actual Re, never from
> theory and never from a different section.
>
> Every V_min, stall-speed, and lift figure below therefore rests on an input
> that no longer describes the aircraft. They are retained unchanged so the
> derivations stay reproducible and so re-running them is a substitution rather
> than a rewrite. **Do not fly to these numbers.**
>
> Closing this needs XFOIL or a transition-sensitive RANS run at
> Re 1.3–1.8 × 10⁵ (the operating range — a fully-turbulent model will
> misrepresent the bubble), or a bench/tunnel result. Tracked in `TODO.md` §0.8.

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

- Two cells + payload: **θ_hover ≈ 47.7°**
- Two cells, no payload: θ_hover ≈ 45.5°

### V_min table

| Tilt θ | V_min, two cells + payload | V_min, two cells, no payload | Note |
| --- | --- | --- | --- |
| −5° (hard stop) | 106.0 kt (54.5 m/s) | 104.2 kt (53.6 m/s) | Above V_NE (87 kt) |
| 0° (cruise) | 100.2 kt (51.6 m/s) | 98.4 kt (50.6 m/s) | Wings alone carry the weight; **above V_NE** |
| 10° | 87.7 kt (45.1 m/s) | 85.6 kt (44.0 m/s) | At V_NE |
| 20° | 73.5 kt (37.8 m/s) | 71.0 kt (36.5 m/s) | |
| 30° | 57.1 kt (29.4 m/s) | 53.8 kt (27.7 m/s) | |
| 40° | 36.3 kt (18.7 m/s) | 30.9 kt (15.9 m/s) | |
| 47.7° / 45.5° (θ_hover) | 0 kt | 0 kt | Thrust alone equals weight |
| 60°–90° | 0 kt | 0 kt | Fully thrust-borne |
| 120° (backing thrust) | 0 kt (vertical T/W 1.17) | 0 kt (1.21) | |
| 140° | **vertical T/W 0.87 — cannot hold altitude** | 0.90 | Transient only |
| 145° (hard stop) | **0.77** | 0.80 | Transient only |

**Important caveat on CL_max — strengthened at Rev S1e.** The 2.0 figure is
wind-tunnel data at Re ≈ 100,000 for the **unmodified** S1223. This airframe's
cruise Reynolds number at the wing root is ≈ 182,000 at 40 kt (ISA SL;
≈ 177,000 at 20 °C), and for a *true* S1223 the higher Re would make the
lower-Re figure conservative.
**That argument no longer applies**, because the built section is not an S1223
(see the banner at the top of this document). The Re comparison is still valid;
the section comparison is not, and the section change is the larger effect.
Treat CL_max as UNKNOWN rather than conservative. No wind-tunnel or CFD validation at the actual
operating Re has been performed for this specific planform; treat the table
above as a design estimate pending flight test, not a flight-tested limit.

**Design implication (Rev T-SB):** at 0° tilt, V_min (100 kt) now exceeds
the 87 kt Part 107 ceiling (§2), so wing-borne flight at 0° is not available
legally at any weight in this document; below about 10° tilt it is not
available at all. V_min also exceeds the 40 kt reference speed used for the wing's Reynolds-number
citation elsewhere in this repository — this airframe's tiny high-wing-loading
planform cannot sustain level flight at 40 kt on wing lift alone. This is
expected and consistent with the design intent: Serenity UAV is a
hover-centric VTOL platform (root `AGENTS.md` design mission profile) where
wings are a lift *assist* during transition, not the primary lift source.
Sustained forward flight below θ_hover ≈ 48° therefore requires either
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
T/W = 1.0 (bare hover floor) when σ = 1/1.35 = 0.740
```

Standard atmosphere reaches σ ≈ 0.740 at approximately **9,900 ft density
altitude** (two cells + payload; 11,100 ft without payload). Against the
WA-R18 T/W floor of 1.2 the margin is smaller: σ = 1.2/1.35 = 0.888, about
**3,900 ft density altitude**, which a hot day at a moderate-elevation site
can reach. This is a linear
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
T·cos(φ) ≥ W  →  φ_max = arccos(W/T) = arccos(1/1.35) ≈ 42.3°   (two cells + payload)
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
| --- | --- |
| 0° | Pending flight test (fixed-wing-like weathervaning expected to dominate; not computed here) |
| 30° | Pending flight test |
| 60° | Pending flight test |
| 90° | Engineering bound: φ_max ≈ 42.3° available bank authority (§4.1); design acceptance target ≥ 10 kt (Phase 9 WBS) |

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

## 6. Hover Endurance and the Mission Endurance Target

No endurance target was ever specified, and the `README.md` Nominal Mission
Profile gives no durations (owner, 2026-10-26). This section derives one. Every
duration is an **ASSUMED** design figure, listed so the owner can replace it.

### 6.1 Hover power and current

Only one fan operating point is cited: 2,135 gf at 1,265.4 W [REF-EDF-003].
Momentum theory gives P ∝ T^1.5 for a fixed disc at constant figure of merit, so

```text
P_fan(T) = 1,265.4 W × (T / 2,135 gf)^1.5        ASSUMED: FM and motor/ESC efficiency
                                                   unchanged at part throttle (optimistic)
I_hover  = 4 × P_fan / 22.2 V + 3.9 A avionics    (FlightEngineer.md "Power Budget")
t_hover  = 0.80 × capacity / I_hover               ASSUMED: 80 % usable to the 3.30 V RTL trigger
```

| Case | Per-fan thrust | Hover current | C rate | Hover endurance |
| --- | --- | --- | --- | --- |
| Two cells + payload | 3.48 lbf (1,579 gf) | **149 A** | 33.9C | **85 s (1.4 min)** |
| Two cells, no payload | 3.36 lbf (1,523 gf) | 141 A | 32.1C | 90 s (1.5 min) |
| Three cells, no payload, all retained | 3.49 lbf (1,584 gf) | 150 A | 24.9C | 116 s (1.9 min) |
| Three cells, third drained first then jettisoned (plan 002 R13) | — | 150 → 141 A | — | 31 s + 90 s = **120 s (2.0 min)** |

The 149 A figure confirms the WBS PWR-CONN-01 value (≈ 150 A) and supersedes the
76 A in `avionics/kicad/FlightEngineer/FlightEngineer.md`, which was computed for
50 mm fans at a 2,768 g AUW.

### 6.2 Mission duration budget

| Step (README profile) | Airborne | Ground | Basis (ASSUMED) |
| --- | --- | --- | --- |
| 1 Take off, climb to 20 ft (6.1 m) | 15 s | — | 0.5 m/s climb + settle; §5 transition floor |
| 2 Land, load and secure payload | 15 s | 60 s | landing; 60 s on the ground, propulsion idle |
| 3 Take off with payload | 15 s | — | as step 1 |
| 4 Transit into the RF environment | 30 s | — | 150 m at about 10 kt (5 m/s); distance not in the profile |
| 5 Lower and release payload | 30 s | — | 1.5 m line (`docs/CARGO_WINCH_SPECIFICATION.md`) at 0.1 m/s + release |
| 6 Identify payload on moving platform | 20 s | — | one Observer pass |
| 7 Synchronise with platform | 20 s | — | station-keeping convergence |
| 8 Attach hoist and lift | 30 s | — | lower, hook, take load |
| 9 Reel in, close clamshells | 25 s | — | 1.5 m at 0.1 m/s + doors |
| 10 Exit, return, land | 45 s | — | 150 m + landing |
| **Total** | **245 s** | 60 s | |

With a 30 % reserve (ASSUMED; Part 107 sets none), the **derived endurance
target is 318 s (5.3 min) airborne, two cells, payload aboard.**

> **WARNING**
>
> The aircraft as specified does **not** meet the derived target. Two cells with
> the payload give about 85 s of hover, **27 % of the 318 s target**. The 30 %
> reserve alone (74 s) is nearly the whole flight. Meeting the target at 149 A
> would take about 16.5 Ah of 6S capacity (now 4.4 Ah), or the hover current
> would have to fall to about 40 A on the present pack. Do not plan a full
> mission profile flight on this configuration; the first flights are hover
> tests sized to the 85 s figure, less reserve.

### 6.3 What would close the gap (for owner decision; not adopted here)

- **Shorter mission legs.** Steps 4 and 10 (transit) and the ground time are the
  only budget lines the airframe does not set; a 30 m stand-off instead of 150 m
  saves about 40 s. This does not close the gap.
- **More capacity.** Every 1 Ah of 6S at 95C-class density adds about 145 g, which
  raises hover power by the 1.5 power of the weight ratio; capacity alone
  converges slowly at T/W 1.35.
- **Less hover power.** Thrust-stand data may show the part-throttle point is better
  or worse than the (T/T_ref)^1.5 scaling; that measurement (Phase 9) is the first
  priority, because every number in this section rests on it.
- **Wing-borne transit.** Not available: V_min at 0° tilt exceeds V_NE (§1).

---

## Summary Table

| Parameter | Value | Status |
| --- | --- | --- |
| T/W, two cells + payload | 1.35 (no stacking loss applied) | Computed from design data |
| V_min at 0° (cruise) | 100.2 kt — above V_NE | Computed; CL_max unverified |
| V_min at θ_hover ≈ 47.7° and above | 0 kt (thrust-borne) | Computed from design data |
| V_NE (never-exceed) | 87 kt | Regulatory ceiling (§107.51(a)); actual top speed pending flight test (Phase 9) |
| AGL ceiling | 400 ft | Regulatory (§107.51(b)) |
| Density altitude at T/W = 1.0 / 1.2 | ≈ 9,900 ft / ≈ 3,900 ft | Computed, first-order estimate |
| Hover current, two cells + payload | 149 A | Computed, (T/T_ref)^1.5 scaling ASSUMED |
| Hover endurance, two cells + payload | 85 s (1.4 min) | Computed |
| Max hover endurance, three cells, no payload | 120 s (2.0 min), third cell jettisoned | Computed |
| Derived mission endurance target | 318 s (5.3 min) airborne | **Not met** (§6.2 WARNING); durations ASSUMED |
| Max demonstrated crosswind | Pending flight test | Phase 9 WBS acceptance target ≥ 10 kt (hover) |
| Transition corridor floor | 20 ft (6.1 m) AGL | Conservative pre-validation policy |

---

*"We're on the leading edge of a new age." Also, apparently, of a fairly
generous V_NE margin over what a 50 mm EDF tilt-rotor can actually manage.
— paraphrasing Skipper, not verifying his airspeed indicator*
