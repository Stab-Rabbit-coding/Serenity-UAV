# Serenity UAV — T/W Recovery, Stem to Stern

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Analysis and drafting:** Claude (Claude Opus 5.5, Anthropic) under the author's
direction, per `AGENTS.md` §3 "Attribution and Licensing"
**License:** CC BY-SA 4.0 — <https://creativecommons.org/licenses/by-sa/4.0/>
**Date:** 2026-09-29
**Status:** DRAFT — D-TW-2, D-TW-3, D-TW-4 and D-TW-5 resolved 2026-09-29 (M6 IMPLEMENTED as Rev T6, pivot re-datumed); D-TW-1 open (§6)

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation must be
> independently reviewed and accepted by a licensed Professional Engineer or an
> equivalently qualified authority before it is applied to any system carrying
> risk to life or safety. Reference material provided AS-IS; not a sealed,
> certified, or reviewed work product.

---

## 0. Headline

1. **True flight mass is ≈12.6 lbm (5,720 g), not 8.62 lbm (3,911 g).** Summed
   row by row from `current-specification/bom_revT.csv` (qty > 0, GCS and
   filament stock excluded, foam at its installed 22 g, alternate battery and
   removable void formers excluded, suspect superseded rows excluded, §2.2).
   Hover T/W = 9.84 lbf / 12.61 lbm = **0.78**. The 1.2 floor needs
   AUW ≤ **8.20 lbm (3,720 g)**, which means removing **≈4.4 lbm (2,000 g)**.
2. **Mass cuts alone that keep the canonical proportions and specified
   capabilities reach roughly T/W 0.99–1.04** (§4). That's short of 1.2.
3. **Closing to 1.2 therefore needs both** the mass program in this plan **and**
   a **+16–21 % verified thrust gain** inside the existing 50 mm nacelle
   envelope (§5), **or** an owner decision to relax one specified capability
   (§6).
4. **Scaling up does not help.** A full-scale 36 in hull fails
   (`docs/HULL_SCALE_36IN_EDF64MM_EVALUATION.md`). A proportional ≈30.7 in hull
   with 64 mm EDFs (64/50 = 1.28×) also fails, at T/W ≈0.81–0.94, because
   ≈50 % of AUW is structure that grows as k²–k³.

---

## 1. Constraints (from the request)

- **Canonical proportions are fixed.** Hull, nacelle diameter, wing planform and
  landing-gear look stay as they are. That rules out 64 mm fans on the 24 in
  hull, because the nacelles would grow ≈28 % in diameter.
- **Specified capabilities are fixed** unless the owner relaxes one (§6). That
  covers the 8-node redundant architecture, the 4×3×3 in internal cargo bay,
  the 5 ft (1.5 m) winch lower, the variable nozzle iris, the 500 W/m² EMI
  environment and endurance ≥ 8 min.
- Governing rule is 14 CFR Part 107 [REF-FAA-002]. The sUAS must stay
  < 55 lbm, which it does by a wide margin.

---

## 2. Stem-to-stern mass roll-up (Rev T BOM, flight mass)

### 2.1 By system

| System | Mass | Share |
| --- | ---: | ---: |
| Power (battery 750, Flight Engineer 158, fuses, shunts) | 2.07 lbm (938 g) | 16.4 % |
| Hull shells (head 178, middle 191, cargo 302, rear 243, collars 47) | 2.12 lbm (960 g) | 16.8 % |
| Nacelles excl. EDF (pods 264, nozzle iris 180, trunnion/bearings/covers/hw) | 1.16 lbm (526 g) | 9.2 % |
| Landing gear, 3.0 in flight article | 1.11 lbm (505 g) | 8.8 % |
| Avionics nodes (PB2-I ×8, Pilot ×4, TACCO ×4, Commo ×2, gateways, OSESC ×2) | 1.05 lbm (475 g) | 8.3 % |
| Wings + spar + root joint + tilt shaft | 0.95 lbm (429 g) | 7.5 % |
| Propulsion (4 × EDF, 4 × ESC) | 0.84 lbm (380 g) | 6.6 % |
| EMC / Faraday cages (4 cages, 4 fans, 8 vents, straps, FT panels, ferrites) | 0.80 lbm (364 g) | 6.4 % |
| Cargo system (winch, doors, servos, cradle, latch, brackets, gateway tray) | 0.79 lbm (360 g) | 6.3 % |
| Wiring | 0.51 lbm (233 g) | 4.1 % |
| Structure misc. (keel 30, CF ring plates 114, foam 22, piston fairings 50) | 0.48 lbm (216 g) | 3.8 % |
| Tilt drive (gearmotors, worm stage, brakes) | 0.40 lbm (184 g) | 3.2 % |
| Battery mounting / interior (cradle, straps, saddles, belly panels, fin) | 0.33 lbm (150 g) | 2.6 % |
| **Total** | **12.61 lbm (5,720 g)** | |

### 2.2 Suspect rows — not in the total, verification required

These rows have **qty > 0** in `bom_revT.csv`, but their own notes or the Rev T
record say they are superseded. I excluded them from §2.1. **Each one has to be
confirmed absent from the build (and set to qty 0) or confirmed present (and
added back).** Until that's done, the BOM sum overstates mass by up to
1.08 lbm (489 g):

| Row | Mass | Why suspect |
| --- | ---: | --- |
| `SPAR-TILT-4130` | 96 g | Retired Rev S1g (`MASS_AUDIT` §7), row still qty 2 |
| `PRINT-PYLON` | 104 g | Rev O pylon; Rev T wing carries the trunnion stub |
| `CF-TUBE-12MM` | 70 g | `SPAR-CF-20X16` note: "Supersedes … CF-TUBE-12MM" |
| Old nozzle gear train (`SECTOR-M1-R22`, `PINION-A`, `BEVEL-M1-14T`, `CROWN`, `BEVEL-HOUSING`, `SHAFT-CF-3MM`, `MR63ZZ`, PTFE) | 78 g | Gear train archived at Rev T (project record) |
| `PRINT-NECK-INTAKE-FRAME` | 85 g | Phase 11 rear-EDF hardware; not needed for Phases 5–10 |
| `CF-ROD-4MM`, `SPAR-TILT-CF4`, `BRG-MF104ZZ`, `BRG-F688ZZ` | 40 g | Pivot-rod/bearing parts replaced by the 6704ZZ trunnion |
| `PRINT-PUSHROD-CRANK` + pushrod + ball studs | 16 g | Crank clamps the rotating 8 mm spar, which no longer exists; passive drive retired (plan `2026-09-28-001` U1) |
| `PRINT-NACELLE-IDLER` + `-IDLER-BKT` | 10 g | Crown→idler→ring stage is the passive drive retired by plan `2026-09-28-001` U1 (row missed in §2.1 exclusion; it *is* in the §2.1 nacelle total, so §2.1 overstates by 10 g) |

**Known understatement (also verify):** Rev T4b hollowing gave 196 g/pod
(project record, 285 → 196 g), but `PRINT-NACELLE-PORT/STBD` still carry
132 g each. That's **+0.28 lbm (+128 g)** if the record is right, which puts
the credible AUW range at **12.61–12.89 lbm (5,720–5,848 g)**.

`FOAM-PU-2LB` still carries the 900 g *kit* mass. MA-3 says it was corrected
to 22 g, but the row was never changed. Fix it in the BOM.

---

## 3. Targets

| T/W | AUW ceiling at 9.84 lbf (4,464 gf) | Required cut from 12.61 lbm |
| ---: | ---: | ---: |
| 1.0 (bare hover) | 9.84 lbm (4,464 g) | −2.77 lbm (−1,256 g) |
| **1.2 (repo floor)** | **8.20 lbm (3,720 g)** | **−4.41 lbm (−2,000 g)** |
| 1.3 | 7.57 lbm (3,434 g) | −5.04 lbm (−2,286 g) |

---

## 4. Mass levers, stem to stern (canon-preserving)

Estimates are labelled. None of these is a measured result. Each lever is
gated on its own verification step.

| # | System | Lever | Est. Δ | Capability impact | Gate / verification |
| --- | --- | --- | ---: | --- | --- |
| M1 | Hull — head, middle, rear | Reprint the non-load-bearing shells in a **foaming lightweight filament** (LW-ASA preferred over LW-PLA for Tg). The cargo shell stays 20 % CF-PETG because it carries the LG bays, spar sockets and actuator pads. | −0.60 lbm (−270 g) | None; OML unchanged | Vendor density claims UNVERIFIED — print a density coupon plus ASTM D790 flexural coupon, then recheck the skid-arm and splice-collar FOS (`structural_analysis.md` §6–§7) |
| M2 | EMC | **One shared Faraday enclosure** instead of four per-bay cages. All nodes are in the cargo section at Rev T5e. Conduction-cool it through the enclosure wall instead of 4 fans + 8 honeycomb vents. | −0.53 lbm (−240 g) | Must still meet the §1.4 500 W/m² requirement | Re-derive the shielding effectiveness and thermal budget for one enclosure; fan-less needs a node-power thermal calc |
| M3 | Power | 6S 4000 → 6S 2800 mAh (`BATT-6S-2800`, already in the BOM) | −0.50 lbm (−225 g) | **Endurance ≥ 8 min at risk** | Hover-current model at the post-cut AUW. Lower AUW lowers hover throttle, which partly pays back the capacity loss |
| M4 | Avionics | **Phase-gate the node count to the WBS phases.** Phase 5 first flight is specified as 2 node pairs (CN1/FC1, CN2/FC2). Carry 4 pairs only from Phase 6. | −0.43 lbm (−194 g) at Phases 5–6 | 8-node capability unchanged at Phase 6+; mass returns then | None for first flight; for Phase 6+ this lever doesn't close the gap |
| M5 | Landing gear | Execute **LG-18** (target ≤ 350 g system) | −0.34 lbm (−155 g) | None | LG-06/LG-14 drop tests re-run after the lightening |
| M6 | Nacelle nozzle | **IMPLEMENTED Rev T6 (2026-09-29).** One-piece fixed open nozzle in place of the servo-driven iris (deferred to Phase 11b); `PIVOT_Z` re-datumed 107.5 → 103.5 mm. Mass measured from the mesh; see §6.1. | −0.19 lbm (≈ −85 g vs V1 servo iris) | **Variable iris is a specified capability** → D-TW-3 | Exit-area sweep on the thrust stand; a fixed exit tuned to hover may itself *gain* static thrust (§5 T3) |
| M7 | Cargo | Cradle redesign (80.6 g measured for a latch) plus end-effector simplification; see §4.1 | −0.12 to −0.22 lbm (−55 to −100 g) | None if the internal bay and winch are kept | Latch hold / release bench test (Phase 7 criteria) |
| M8 | Structure | Re-derive the CF ring plates at 1 mm. The keel is FOS 25+ from bending alone, and the rings are anti-ovalisation only. | −0.13 lbm (−57 g) | None | New anti-ovalisation calc; plate FOS vs the 4.0 joint target |
| M9 | Cargo shell | Hollow the tilt-actuator pads (**MA-5**, already quantified) | −0.07 lbm (−33 g) | None | Already analysed in `MASS_AUDIT` §6 |
| M10 | Tilt drive | 4 mm steel tilt shafts → **7075-T6 or pultruded CF** (0.050 N·m duty). Non-ferrous also *removes* a disturbance source inside the AK7455 keep-out. | −0.07 lbm (−32 g) | None | Wind-up: steel 0.27° → Al ≈0.79° at 250 mm, ≈0.22° referred to the nacelle, inside the closed nacelle-angle loop. Confirm against TILT-CTL spec |
| M11 | Nacelle fairings | `PRINT-PISTONS` (decorative) as a thin LW shell | −0.07 lbm (−30 g) | None | — |
| **Σ** | | **All levers** (M6 at −85 g measured, M7 at −100 g) | **−3.13 lbm (−1,421 g)** | | → AUW **9.48 lbm (4,299 g)**, **T/W 1.04** |
| | | **Excluding M4** (full 8-node aircraft) | **−2.71 lbm (−1,227 g)** | | → AUW **9.91 lbm (4,493 g)**, **T/W 0.99** |

### 4.1 Cargo attachment — gondola, claw, or magnet?

- **Printed cargo gondola: not needed.** The canonical cargo section *is* the
  bay. A separate gondola liner (`TODO.md` §1.1.1 "Cargo gondola shell";
  Phase 7 "Bond cargo gondola shell into belly void") adds mass and does
  nothing the section shell and cradle don't already do. **Recommend
  cancelling it.** It has no BOM row, so this is mass avoided rather than a
  saving in the table.
- **Claw at the line end: no.** A claw needs its own actuator and linkage
  hanging on the tether, plus power or a signal down a non-conductive Dyneema
  line. That puts mass at the worst possible place for pendulum dynamics.
- **Electro-permanent magnet (EPM) at the line end: conditional.** It holds
  with zero power and releases on a pulse. The unpowered state is *hold*,
  which is the safe state over people. It would replace the cradle, the
  release servo and the release bracket. There are two costs:
  1. **The payload must carry a ferrous strike plate.** That's an ops
     constraint.
  2. **The pulse must reach the hook**, which means either a conductive tether
     (heavier than 0.5 mm Dyneema, and it changes the line-shed / overload
     design of `CARGO_WINCH_SPECIFICATION.md` §3.8) or a battery-powered
     pendant.

  The EPM mass and hold force are **not verified**. Source a datasheet before
  any figure is used.
- **Recommendation:** keep the winch, the internal bay and the doors (canon +
  spec), cancel the gondola, and **redesign the cradle** (M7 low end,
  −55 g). Evaluate the EPM only if the owner accepts the strike-plate and
  tether constraints (D-TW-4).

---

## 5. Thrust levers (inside the 50 mm canonical envelope)

To reach T/W 1.2 at 9.50–9.93 lbm, thrust must rise from 9.84 lbf (4,464 gf)
to **11.40–11.91 lbf (5,171–5,404 gf), +16–21 %**. None of the levers below is
quantified in this repository. Each one is a thrust-stand task (Phase 9
"Thrust stand calibration" should be **pulled forward** to gate this plan).

| # | Lever | Why it might pay | Evidence needed |
| --- | --- | --- | --- |
| T1 | **Measure the tandem stacking efficiency.** 90 % is assumed, not measured. | If the counter-rotating pair with an 11-fin stator does better, the gain is free | Stand test, single fan vs tandem pair |
| T2 | **Alternative 50 mm 6S fan units** that fit the 55–56 mm nacelle bore | The XFly Galaxy X5 figure (1,240 gf) is one vendor point | Verified manufacturer tables only (same standard as the QX-Motor check) |
| T3 | **Hover-tuned fixed exit area** (pairs with M6) | EDF static thrust is sensitive to exit/FSA ratio, and the iris is a compromise across modes | Exit-area sweep on the stand |
| T4 | **Intake bellmouth lip radius** | Static thrust is sensitive to inlet losses at zero airspeed | A/B on the stand |
| T5 | **ESC timing / governor tuning** (U3 governor rewrite) | Current governor is a stub | Stand test at matched electrical power |

**Rejected:** using the Phase 11 rear EDF for hover lift. By spec it's
cruise-only, it sits well aft of the nacelle-pivot CG so it would need a
forward counter-lift, and it adds ≈0.29 lbm (130 g) of fan+ESC plus plenum.

---

## 6. Owner decisions (block the plan)

| ID | Decision | Mass/thrust at stake |
| --- | --- | --- |
| **D-TW-1** | Accept **T/W 1.2 as a gated result**, meaning mass program §4 **plus** a verified thrust gain §5, with no fly decision until both are measured? | Frames everything below |
| **D-TW-2** | ~~Is the 500 W/m² EMI requirement firm for Phase 5?~~ **RESOLVED 2026-09-29 (owner): lighter shielding is accepted for Phase 5.** M2 goes ahead as one shared enclosure; full 500 W/m² hardening is re-verified before the phase that needs it. | M2 −240 g |
| **D-TW-3** | ~~Fixed nozzle?~~ **RESOLVED 2026-09-29 (owner): fixed open nozzle for Phases 5–10; variable nozzle deferred to Phase 11b.** Implemented as Rev T6 (`nacelle_nozzle_fixed.scad`, BOM `PRINT-NACELLE-NOZZLE-FIXED`, `deferred/WBS.md` §Phase11b). | M6 −85 g |
| **D-TW-5** | ~~`PIVOT_Z` re-datum?~~ **RESOLVED 2026-09-29 (owner): pivot moved to the new CG, 107.5 → 103.5 mm.** Hover ground clearance on the 3.0 in flight-article gear stays +39.1 mm static, +11.6 mm over the 21 mm reserve (`tools/landing_gear_ground_clearance.py`, MEETS MINIMUM). | CG / clearance |
| **D-TW-4** | ~~EPM hook acceptable?~~ **RESOLVED 2026-09-29 (owner): EPM cargo hook accepted.** Consequences: payloads carry a ferrous strike plate (ops constraint), and the hook needs a conductive tether or a pendant battery (TW-5 has to choose, and the choice must be re-checked against the `CARGO_WINCH_SPECIFICATION.md` §3.8 line-shed/overload design). Removes the cradle, release servo and release bracket (≈100 g gross). EPM + tether/pendant mass is still unverified, so the net saving is open. | M7 −100 g gross |

### 6.1 Fixed nozzle vs. variable iris — the trade (for D-TW-3)

**What the iris does at hover today.** It opens to its 105 % bore-area target.
The 75 % target is the convergent cruise setting (`bom_revT.csv`
`PRINT-NACELLE-FLAP-MASTER`, "75 %/105 % bore targets"). A fixed nozzle built
at the same ≈105 % hover exit area therefore has the **same ideal hover exit
area**. From momentum theory at fixed shaft power, T³ = 2ρA_eP², so
T ∝ A_e^(1/3), and equal A_e means equal ideal static thrust. **A fixed nozzle
buys no ideal-thrust gain at hover.**

**Where a real gain could come from:** losses the iris has and a smooth fixed
nozzle doesn't. These are leakage through the flap shingle laps (0.2 mm
seal-lap gaps ×8), the seal-flap surface step (an open VERIFY item) and the
hinge-boss protuberances. None of them is measured. Plausibly **0–3 % static
thrust**, and that figure is an engineering estimate, not data. Settling it
takes an A/B on the thrust stand (TW-1).

**What it costs:** the 75 % convergent cruise setting goes away, so forward
flight runs at a lower exit velocity. That's a cruise-efficiency and top-speed
penalty, not quantified, since there is no drag polar in the repo
(`flight_envelope.md` §2.2).

**Recomputed 2026-09-29 against the servo-driven iris.** The first version of
this table was costed against the *passive* drive, which plan
`2026-09-28-001` U1 retired (commit `ef802c5c`). Under Option A the servo
holds 105 % over 90–145° tilt and fails open to 105 % (`airframe/AGENTS.md`),
so the hover exit area of iris and fixed nozzle is still identical.

Aircraft totals (2 nacelles), fixed open nozzle vs servo iris:

| Deleted | Mass | Source |
| --- | ---: | --- |
| Flaps, 4 master + 4 seal per nozzle | 56.8 g | `bom_revT.csv`; plan `2026-09-28-001` U5 (28.4 g/nozzle) |
| Unison ring | 13.4 g | `bom_revT.csv` (MA-audit 6.7 g/ea) |
| Hinge + follower pins (`PIN-3X18` ×16, `PIN-2X4` ×16) | 16.0 g | `bom_revT.csv` |
| Servo drive V1: servo 4.5 + link 1 + spring 1 + mount 1.5 + lead 0.5 + 6 V wiring 4.2 per nacelle | 25.4 g | plan `2026-09-28-001` "Gateway variants" table (estimates, VERIFY) |
| Throat liner 40 g, replaced by the fixed nozzle **67.6 g** (2 × 33.8 g, MEASURED from the mesh 2026-09-29; it must fill the same Ø72 pod pocket as the iris housing, so it's heavier than the 15–25 g first assumed) | **+27.6 g** | `bom_revT.csv` `PRINT-NACELLE-NOZZLE-FIXED` |
| **Total, V1 gateway** | **≈ −84 g (−0.19 lbm)** | earlier 127–137 g estimate withdrawn |
| **Total, V2 gateway** (+1 board + tray per nacelle, ≈+40 g) | **≈ −124 g (−0.27 lbm)** | D-NZ-1 now deferred |

Not counted: the idler, crown and pushrod are **already retired** by the servo
plan (they sit in the §2.2 suspect list), so the first version of this table
double-counted them as fixed-nozzle savings.

| | Fixed open nozzle vs servo iris |
| --- | --- |
| Mass | −127 to −137 g (V1) / −167 to −177 g (V2) |
| Thrust at hover | +0 to +3 % (unverified; ideal gain is zero, both at 105 %) |
| **Net ΔT/W** at ≈9.7 lbm (4,380 g) AUW | **≈ +0.02 (mass only, V1)**. Thrust: the fixed nozzle's flow exit is 26.25 mm against the modelled iris's measured 23.77 mm, so ideal theory bounds the gain at up to +6.8 % (T/W up to ≈ +0.07). That's an upper bound, pending the stand |
| Schedule / risk | Deletes servo plan U2–U8 from the first-flight path: the servo, spring cord, gateway choice D-NZ-1, the U8 bench load check (the 20 N placeholder currently *fails* the margin) and the fail-open logic |
| Capability | Loses the 75 % convergent cruise setting, so cruise efficiency and top speed drop (unquantified; no drag polar) |

**Bottom line (as implemented):** the fixed nozzle saves ≈ 0.19 lbm (85 g), worth
T/W ≈ +0.02 from mass. Its thrust upside is bounded, not measured. The bigger payoffs
are the schedule (an entire open mechanism off the first-flight path) and the
finding that the modelled iris never reached its own 105 % open exit.

---

## 7. Implementation units (for `docs/WBS.md` / root `WBS.md` once D-TW-1..4 close)

| Unit | Scope | Depends on |
| --- | --- | --- |
| TW-0 | **BOM truth:** resolve every §2.2 suspect row, fix `FOAM-PU-2LB` 900 → 22 g, reconcile the nacelle pod 132 vs 196 g, add the MA-7 `Installed` flag, and publish a scripted roll-up (replacing the non-existent `tools/update_bom.py`) | — |
| TW-1 | Thrust stand: pull Phase 9 calibration forward, then run T1, T3, T4 | procure stand |
| TW-2 | LW-filament coupons (density, D790), then reprint head/middle/rear (M1) | coupon results |
| TW-3 | Single-enclosure EMC redesign (M2) | D-TW-2 |
| TW-4 | LG-18 lightening (M5) + drop re-test | — |
| TW-5 | Cargo: cancel gondola, redesign cradle (M7), MA-5 pads (M9) | D-TW-4 |
| TW-6 | Structure: ring-plate re-derivation (M8), tilt-shaft material (M10), piston fairings (M11) | — |
| TW-7 | Nozzle: fixed hover exit (M6) | D-TW-3, TW-1 |
| TW-8 | **CG re-derivation.** Cutting nose/tail shell mass moves the CG, and the nacelle pivot is set *at* the CG (`PIVOT_Z` 107.5), so ballast or a pivot re-datum may claw mass back | TW-0..TW-7 |
| TW-9 | Endurance re-check with the post-cut AUW (M3 battery choice) | TW-1, TW-8 |

---

## 8. Sources

- `current-specification/bom_revT.csv` — every mass in §2 (Rev T, 2026-09-28).
- `docs/MASS_AUDIT_CARGO_WING_ROOT.md` — MA-1..MA-9, §6 pad lightening, §7 Rev S1g delta.
- `docs/FIRST_FLIGHT_READINESS.md` — blockers 1, 2, 4; independent 5.6–5.8 kg estimate.
- `docs/HULL_SCALE_36IN_EDF64MM_EVALUATION.md` — scale-up rejected.
- `docs/flight_envelope.md` — thrust and stacking methodology.
- `docs/structural_analysis.md` — FOS basis for M1, M8.
- `docs/CARGO_WINCH_SPECIFICATION.md` — winch/line-shed design constraining §4.1.
- 14 CFR Part 107 [REF-FAA-002].
