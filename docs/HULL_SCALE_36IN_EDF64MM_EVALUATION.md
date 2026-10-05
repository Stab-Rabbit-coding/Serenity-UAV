# Serenity UAV — 36in Hull / 64mm EDF Scale-Up Evaluation

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**Analysis and drafting:** Claude (Claude Sonnet 5, Anthropic) under the author's
direction, per `AGENTS.md` §3 "Attribution and Licensing"
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)
**Date:** 2026-09-28

> ⚠️ **ENGINEERING REVIEW REQUIRED — this output is not a substitute for a
> qualified engineer.** Every result, calculation, and recommendation produced
> with this skill **must be independently reviewed and accepted by a properly
> qualified individual** — a licensed Professional Engineer or an equivalently
> qualified authority for the jurisdiction and discipline — **before it is
> applied to any system carrying risk to life or safety.** This informs
> engineering judgment; it does not replace it, and it carries no professional
> liability.

---

## 0. Question and headline finding

**Question:** would scaling the hull from 24in to 36in (1.5× linear) and
swapping the 50mm EDFs for QX-Motor 64mm 12-blade EDFs (same 2-nacelle × 2-EDF
tandem configuration, 90% stacking efficiency) close the hover T/W deficit
identified earlier this session (corrected Rev T T/W ≈ 0.98–1.01 against a
1.2 floor, `docs/FIRST_FLIGHT_READINESS.md` blocker 1 / `TODO.md` "★ WA-R18")?

**No.** Recomputed T/W lands at **0.69–0.93**, worse than the current
corrected baseline. The reason isn't the fans — the new fans genuinely
produce more thrust — it's that hull-stretching grows airframe mass on a
squared-to-cubed law while this specific fan family's thrust ceiling is
fixed by the motor/cell combination, not free to scale further. Structure
mass grows faster than thrust does.

---

## 1. Verified propulsion inputs

Source: QX-Motor 64mm EDF(12) instruction manual, product page
<https://qx-motor.co/product/64mm-edf-12-blade-2822-brushless-motor-set/>
(fetched 2026-09-28; performance table confirmed against the user-supplied
datasheet photograph, same session). **REQUIRES VERIFICATION** entry in
`REFERENCES.md` before further citation — external commercial datasheet,
not yet catalogued with a REF-ID.

| Parameter | Value | Note |
|---|---|---|
| Motor | QF2822, 9N6P, KV 2200/2400/3500/3800/4300 options | |
| Motor weight | **135 g** | motor only — excludes fan blades, duct, housing hardware |
| Motor dimensions | body Ø27.8mm × 58mm, overall 68.7mm w/ shaft, shaft Ø3.0mm | mounting bolt circle Ø16.00mm, 4×M3, per user-supplied dimension drawing |
| Selected variant | **QF2822-2400KV at 6S (22.2V)** | highest thrust figure in the entire table across all KV options |
| Thrust at 6S | **2,135 gf** | 57.0 A, 1,265.4 W, efficiency 1.69 g/W |
| ESC pairing (mfr recommendation) | 60A | only ~5% margin against the 57.0A continuous draw — see §4 |

**Not verified anywhere:** the complete EDF unit mass (fan blades + duct
housing + hardware, beyond the bare 135g motor). This is the single biggest
unknown in this analysis and should be bench-weighed or sourced from a
seller listing before this evaluation is trusted for a procurement decision.

---

## 2. Thrust recompute

Same architecture as current: 2 nacelles, 2 EDFs tandem per nacelle, 90%
stacking efficiency (per `README.md` "Nacelles", `AGENTS.md` "Powerplant" —
same methodology applied to the current 50mm design, `docs/flight_envelope.md`
design-inputs table).

```
Per-nacelle thrust = 2 x 2,135 gf x 0.90 = 3,843 gf
Total thrust        = 2 x 3,843 gf       = 7,686 gf (16.94 lbf, 75.4 N)
```

vs. current 4,464 gf (9.84 lbf) — **+72%**.

---

## 3. Mass recompute

### 3.1 Propulsion hardware

| Item | Current (50mm) | New (64mm), assumed | Basis |
|---|---:|---:|---|
| EDF unit mass, each | 70 g (`bom_revS.csv` `EDF-50-6S`) | **200 g (ASSUMED, bracket 180–230g)** | motor alone is 135g; complete-unit mass scaled by analogy to the 50mm unit's ratio of complete-mass/thrust — **not a vendor figure, needs bench verification** |
| EDF units, qty | 4 | 4 | same 2×2 tandem config |
| EDF hardware total | 280 g | **800 g** | +520 g |
| ESC, each | 25 g (40A class, `ESC-40A-6S`) | **42 g (ASSUMED, 80A class)** | 57A continuous draw against a 60A-rated ESC is only 5% margin — sized to 80A here, matching the datasheet's own upsizing pattern at higher KV/current variants |
| ESC total | 100 g | **168 g** | +68 g |
| **Propulsion hardware total** | **380 g** | **968 g** | **+588 g** |

### 3.2 Airframe structure scaling (k = 1.5× linear, 24in→36in)

No validated scaling law exists in this repository for this airframe (no
FEA, no parametric structural model tied to hull length). Two bounding
cases, both physically defensible:

- **Optimistic — thin-shell / area scaling (k² = 2.25×):** valid if wall
  thickness holds at the repo's established 2mm print-wall floor
  (`docs/MASS_AUDIT_CARGO_WING_ROOT.md` §3) and mass is dominated by shell
  surface area, not by spars/gears sized against load.
- **Conservative — geometric similarity / volume scaling (k³ = 3.375×):**
  valid if primary structure (spars, ring frames, gear trains, landing gear)
  must grow proportionally to react proportionally higher loads at the
  larger scale — the physically conventional assumption for a structural
  member sized against its own loads, not just its own skin.

Baseline non-propulsion, non-avionics structure mass, backed out of the
corrected Rev T AUW established earlier this session:

```
Corrected AUW (MA-1 only, clean basis)      = 4,432.6 g
less current propulsion hardware (§3.1)     = -380 g
less avionics/battery/servos (est., §3.3)   = -1,462 g
= structure mass baseline                   = 2,590.6 g  ~2,591 g
```

| Scaling law | Structure mass at 36in |
|---|---:|
| Optimistic (k²=2.25) | 5,830 g |
| Conservative (k³=3.375) | 8,745 g |

### 3.3 Avionics / battery / servos

Per the question's own scope: **avionics stays the same except the Flight
Engineer PDB**, which needs to scale for the higher power/current load (see
§4). Rough current-BOM roll-up of this category (PB2-I×2, Pilot×4, TACCO×4,
Commo×2, Flight Engineer at its corrected 158g, CAN-PERIPH-GW-DOOR, microSD,
battery, tilt-drive servo chain, misc sensors) ≈ **1,462 g**, held constant
except a Flight Engineer growth allowance — see §4. This figure is a rough
category sum from `current-specification/bom_revT.csv`, not a fresh
line-by-line audit; treat it as ± a few hundred grams.

### 3.4 New AUW and T/W

| | Optimistic (k²) | Conservative (k³) |
|---|---:|---:|
| Structure | 5,830 g | 8,745 g |
| Avionics/battery/servos (+FE growth) | 1,502 g | 1,502 g |
| Propulsion (§3.1) | 968 g | 968 g |
| **New AUW** | **8,300 g (18.3 lbm)** | **11,215 g (24.7 lbm)** |
| Thrust (§2, fixed) | 7,686 g | 7,686 g |
| **T/W** | **0.93** | **0.69** |

**Self-consistency check (floor, optimistic case):** solving for the T/W≥1.2
floor at the optimistic k² structure-scaling assumption —

```
AUW_max for T/W>=1.2 = 7,686 / 1.2 = 6,405 g
Structure + avionics + ESCs (no EDF mass at all) = 5,830 + 1,502 + 168 = 7,500 g
```

Structure + avionics + ESC alone already **exceed** the 6,405 g budget
before a single EDF is bolted on — the required EDF mass to close T/W to 1.2
is **negative**. This confirms the negative finding is not sensitive to the
unverified 200g/EDF assumption: it holds even in the limit of zero-mass fans.

---

## 4. Flight Engineer / power-system implications (flagged, not sized)

Full current draw at 4 EDFs full throttle: **4 × 57.0 A = 228 A continuous**,
against the current design's:

- 150A MAXI main fuse (`current-specification/bom_revT.csv` `FUSE-MAIN-150A`) —
  **undersized**
- 6AWG main leads, rated 120A continuous / 200A burst
  (`WIRE-6AWG`) — **undersized for sustained 228A**
- 1mΩ 3W Kelvin current-sense shunts (`SHUNT-1MOHM`) — at 60A per branch,
  P = I²R = 3.6 W, **exceeds the 3W rating**; at 80A, 6.4 W, well over
- 40A mini blade ESC branch fuses (`FUSE-ESC-40A`) — need to move to the
  60–80A class matching the new ESCs

This is exactly the "FE board needs to scale" item named in the question.
It is flagged here as a real, quantified consequence, not sized — a proper
power-system redesign (fuse ratings, conductor gauge, shunt values, BEC
headroom, battery C-rating for 228A continuous) is its own follow-on task
and is out of scope for this mass/thrust evaluation.

---

## 5. Physical fit (not evaluated in depth)

The 64mm EDF's motor mounting bolt circle is **Ø16.00mm, 4×M3** (per the
user-supplied dimension drawing) — different from the nacelle's existing
open item `TODO.md` §1.1.3.8 "`MOTOR_BOLT_R` is still 10.0 mm and still...
[PRINT-BLOCKING]" for the *current* 50mm motor. A 64mm fan in a
correspondingly larger nacelle would need its own bolt-pattern and duct-bore
re-derivation from scratch — not assessed here.

---

## 6. Conclusion and recommendation

Scaling the hull to 36in with these 64mm/2400KV/6S EDFs **does not close the
T/W gap — it widens it**, in both the optimistic and conservative structural
scaling cases. The fans themselves are not the problem (they nearly double
total thrust); the hull stretch is: airframe structure mass scales
faster than a fixed-thrust-ceiling fan family can keep up with.

Two directions worth pursuing instead, neither evaluated in this document:

1. **Upsize the EDFs without stretching the fuselage** — mount the 64mm fans
   on the existing 24in hull's nacelles if they physically fit (see §5 open
   item), avoiding the k²–k³ structure penalty entirely. The thrust gain
   (+72%) would then apply against something close to the current
   structure mass, which — even accounting for the unresolved +520g EDF
   hardware delta — is far more likely to clear T/W 1.2 than the 36in case.
2. **Attack the mass side of the ratio directly** — the current airframe
   already carries ~520g of unreconciled BOM understatement (MA-1,
   `docs/MASS_AUDIT_CARGO_WING_ROOT.md`) plus the Rev S1g +102.8g delta
   (WA-R18). Closing that gap moves T/W by more than this propulsion swap
   does, without touching the propulsion system at all.

---

## 7. Sources

- `docs/FIRST_FLIGHT_READINESS.md` blocker 1 — mass truth / T/W baseline.
- `docs/MASS_AUDIT_CARGO_WING_ROOT.md` — MA-1 mass correction, §7 Rev S1g delta.
- `current-specification/bom_revT.csv` — current propulsion/avionics/structure masses (this session's Rev T update).
- `docs/flight_envelope.md` — thrust/stacking-efficiency methodology.
- QX-Motor 64mm EDF(12) product page and instruction-manual performance
  table, <https://qx-motor.co/product/64mm-edf-12-blade-2822-brushless-motor-set/>
  (fetched 2026-09-28) — **not yet catalogued in `REFERENCES.md`; add before
  further citation elsewhere in the repo.**
- This session's prior weight/thrust/flight-limits recalculation (same
  conversation, 2026-09-28).
