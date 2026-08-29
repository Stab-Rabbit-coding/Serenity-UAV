---
title: "fix: Nacelle ESC power routing across the tilt joint — decouple torque transfer from wire routing"
date: 2026-08-29
plan_type: fix
execution: geometry+mechanism, decision-support pre-implementation
---

# fix: Nacelle ESC power routing across the tilt joint

**Target repo:** Serenity-UAV (this repo)

**Status:** DECISION SUPPORT — pre-implementation, same posture as
`docs/TILT_SPAR_ANALYSIS.md` when it was first drafted. This plan verifies
the problem, quantifies three candidate architectures, and gates geometry
work on an owner decision (U4) before any SCAD is touched.

**Origin / supersession:** formalizes and corrects
`docs/plans/2026-08-27-nacelle-wiring-plan.md` (owner's draft, itself derived
from an external Gemini conversation). That draft's two problem statements
are **confirmed real** by the verification in Part A below; its proposed
numbers (`SPAR_OD = 16.0mm`, `SPAR_BORE_D = 11.0mm`) are **re-derived and
found still insufficient**. Also closes the open item **U6** in
`docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md`
("Verify ESC cable clearance for rotation through full tilt range").
Federated with, and does not touch, `docs/plans/2026-08-29-001-nacelle-nav-wire-hall-reconciliation-plan.md`
(nav-light + Hall-encoder signal wiring — separate wire, separate path,
unaffected by how this plan resolves).

**Scope:** `airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad`,
`airframe/openscad/wings/wings_s1223_revo.scad`,
`airframe/openscad/port_tilt_spar_assembly.scad`,
`docs/TILT_SPAR_ANALYSIS.md`, `docs/POWER_DISTRIBUTION.md`,
`current-specification/bom_revS.csv`.

---

## Part A — Verifying the problem (both claims confirmed real)

### A.1 — 4× 10 AWG power wires do not fit the existing Ø7 mm double-D conduit

`current-specification/bom_revS.csv` (`WIRE-10AWG`) specifies "10AWG silicone
wire red/black," generically sourced (Amazon/AliExpress) — **no OD is
recorded anywhere in the repo** (`REFERENCES.md`, `POWER_DISTRIBUTION.md`,
BOM all lack a dimensional spec). The wing conduit
(`wings_s1223_revo.scad`: `CABLE_BORE_D = 7.0mm`, two separate round bores,
`CABLE_BORE_SEP = 9.5mm` apart) was sized without checking wire OD against
bore area.

For *n* equal-diameter wires packed with **zero clearance** (touching each
other and the bore wall — the geometric floor, not a buildable tolerance)
inside a round bore, minimum bore ID = wire OD × a packing factor
(1.0 / 2.0 / 2.155 / 2.414 for n = 1/2/3/4, the known optimal circle-packing
results):

| Wire OD (typical 10 AWG silicone range) | 1 wire | 2 wires | 4 wires |
|---|---|---|---|
| 4.5 mm | 4.5 mm | 9.0 mm | 10.9 mm |
| 5.0 mm | 5.0 mm | 10.0 mm | 12.1 mm |
| 5.5 mm | 5.5 mm | 11.0 mm | 13.3 mm |

Even **one pair** (2 wires, one ESC's B+/B−) needs ≥9–11 mm at zero
clearance — the Ø7 mm bore is too small for 2 wires at any OD ≥ 3.5 mm, let
alone 4. **Confirmed: the existing conduit does not carry this wiring as
sized.**

### A.2 — The harness port cannot track the nacelle through its tilt sweep

`nacelle_pod_50mm_tandem.scad`'s `harness_exit_port()` is a **rigid
rectangular slot** cut through the nacelle shell at `HARNESS_PORT_Z =
93.85mm`, sized specifically to align with the wing conduit's fixed exit
point **at one configuration** (module comment: "must line up with the
wing's EDF double-D where it breaks out of the wing TIP face"). Tilt rotation
is about the spar axis at `PIVOT_Z = 111.5mm`, `Y = 0`. The harness port sits
at the same `Y = 0`, so it is a point at radius **r = 111.5 − 93.85 =
17.65mm** from the pivot, at the port's own angular reference. As the nacelle
rotates by θ, that point sweeps:

- arc length = r·θ, chord displacement = 2r·sin(θ/2)
- **95° operational sweep** (`TILT_SPAR_ANALYSIS.md`, −5°…90°): arc ≈ **29.3mm**, chord ≈ **26.0mm**
- **145° stale test-step figure** (`REVN_BUILD_GUIDE_24IN.md`, pre-Rev-T): arc ≈ **44.7mm**, chord ≈ **33.7mm**

Nothing in the SCAD models a service loop, flex boot, slip ring, or
disconnect to absorb this. **Confirmed: this is a real, unaddressed gap.**
It is the same gap flagged and never closed as U6 in
`docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md`: *"ESC
wires are forward of the pivot, and therefore will experience tension and
binding during the nacelle tilt."*

### A.3 — The owner's own proposed fix (16 mm OD / 11 mm bore) is also undersized

`docs/plans/2026-08-27-nacelle-wiring-plan.md` proposes `SPAR_OD = 16.0mm`,
`SPAR_BORE_D = 11.0mm` for the 4-wire bundle, routed **on-axis** (through the
rotating member, like the nav wire). From the A.1 table, 4 wires at a
plausible 5.5mm OD need **≥13.3mm at zero clearance** — 11mm falls short
before any real assembly margin is added. A workable on-axis bore, once
realistic clearance and jacket tolerance are included, is closer to
**15–18mm ID**, which on a 2–2.5mm-wall CF tube pushes OD to **~20–23mm** —
larger than either the rejected external "16mm" figure or the owner's own
draft number.

### A.4 — On-axis routing is not free for power gauge either

The nav-light routing (`TILT_SPAR_ANALYSIS.md` §5) works on-axis because
28 AWG stranded signal wire tolerates a ~0.5°/mm gentle twist over the
sweep with negligible fatigue risk — a twist-fatigue case that was
explicitly checked. **No equivalent check exists for 10 AWG power wire**,
which is far stiffer, and the same document explicitly excluded power from
the spar bore for this reason (§5: *"EDF power/signal do NOT use the
spar... too large"*). Moving power on-axis (Option B below) does not
inherit the nav-wire's feasibility finding — it needs its own twist-fatigue
derivation at the real 10 AWG construction and the real operational sweep
angle.

---

## Part B — Candidate architectures (unresolved — owner decision required, U4)

### Option A — Keep torque-transfer spar as-is; fix the wire path only

Leave the 8mm/5mm-ID AISI 4130 spar (`TILT_SPAR_ANALYSIS.md`, unchanged,
load-verified) as the sole torque member. Correctly size the **off-axis**
wing conduit for the real wire bundle (per A.1, with real clearance —
likely 2 separate ≥12–14mm bores rather than 2× Ø7mm, or a single larger
oval), and add a genuine flexible service loop/pigtail at the wing-nacelle
boundary sized for the confirmed 26–34mm chord sweep (A.2), with a checked
minimum bend radius for the real wire construction and a modeled clearance
envelope so the loop doesn't foul the pylon fairing through the full sweep.

- **Pro:** no change to the already load-verified spar, bearings, or fixed
  gear geometry; smallest blast radius.
- **Con:** the service loop is real, unmodeled mechanical design work (bend
  fatigue over the aircraft's service life, volume to package the loop,
  and it's also the natural disconnect point the nacelle-off-spar service
  plan already needs — worth designing once, not twice).

### Option B — Combined torque+wire member, on-axis (owner's 2026-08-27 draft, corrected)

Enlarge the spar itself to carry both torque and the wire bundle on-axis, per
A.3's corrected ~15–18mm ID / ~20–23mm OD. Requires:

- A full re-run of `TILT_SPAR_ANALYSIS.md` §3's bending/torsion/stiffness
  trade study at the new section — the existing 12mm "unified" candidate was
  already rejected there as "overbuilt, heavier, bigger duct crossing"; a
  20mm+ tube is well past that.
- A material re-decision: CF **cannot** take the keyed torque joint this
  mechanism needs (§3.5: "CF (either form) — fails the functional gate:
  delaminates" at a keyway) — so a torque-carrying tube this size in CF, as
  the 2026-08-27 draft proposes, reopens a gate that document already closed
  against CF. A metal tube this large is a significant mass/duct-blockage
  regression.
- The wingtip bearing (MF128ZZ, 12mm bore) and fixed-gear centerlines would
  need a full re-derivation, not a swap-in — same conflict already
  identified against the plain 16mm proposal.
- The A.4 twist-fatigue check for 10 AWG at the real sweep angle.

- **Pro:** single member, no separate wire-crossing joint to design.
- **Con:** reopens nearly every gate `TILT_SPAR_ANALYSIS.md` closed (material,
  bearing, gear, duct blockage) at a larger, less favorable size than the
  candidates already rejected there.

### Option C — Decouple torque transfer from wire routing (owner's stated preference)

Per the 2026-08-27 draft's second half: stop using the spar as the servo's
torque path. Replace it with a belt/sprocket drive from a fuselage/bulkhead
servo to a separate rotating ring/collar at the nacelle, and let the tube
through the wing/nacelle joint carry **only** wiring — sized for wire volume,
not torque, and not necessarily rotating with the nacelle at all if the ring
bearing takes the tilt motion instead.

This is the most promising direction **in principle** — it's the only option
that removes the fundamental tension driving every other candidate's
problems (the current 8mm spar is torque-optimized, not wire-volume-sized;
enlarging it for wire volume then breaks the torque-side gates it was
originally sized against). It needs, before any geometry is cut:

- **Torque/belt sizing:** re-use the grounded servo-torque requirement
  already derived in `TILT_SPAR_ANALYSIS.md` §2.1 (≈0.177 N·m grounded,
  gravity+inertia, aero explicitly out of scope pending real aero data) —
  size belt width/pitch and sprocket ratio against that figure plus the
  same 4g/1.5× ultimate margin convention `docs/structural_analysis.md` §3
  already establishes for this airframe.
- **Bearing arrangement for the now-non-torque tube:** it still needs
  mechanical support at the wingtip and root even if it isn't driving
  anything — likely still F688ZZ/MF128ZZ-class bearings, but the load path
  changes (radial/thrust only, no torque reaction) and needs re-deriving,
  not assumed.
- **Belt routing through the wing:** must be checked against everything
  already occupying that cross-section — the EDF double-D conduits, the
  Hall-sensor cableway (`hall_sensor_cableway()`), and the wing-root/CF
  thwart rework already in flight in
  `docs/plans/2026-08-24-001-fix-wing-repair-root-joint-plan.md` (same
  wing, same station range — this is a **hard scheduling dependency**, not
  just a citation: belt routing decided here needs to be checked against
  whatever thwart geometry that plan lands on).
- **Duct-core blockage re-check:** a wire-only tube can likely be smaller in
  OD than Option B's torque-carrying version (no keyway, no bending/torsion
  margin needed beyond supporting its own wiring and modest bearing loads),
  which is a real advantage for the `TILT_SPAR_ANALYSIS.md` §4 duct-blockage
  budget — but this needs to be shown, not assumed.
- **Mass/CG:** a belt+sprocket+bulkhead-servo arrangement is a different
  mass distribution than the current per-side spar+bulkhead-servo
  (`TILT_SPAR_ANALYSIS.md` §7 established the current spar's own mass/T-W
  impact); needs its own AUW/T-W re-check.
- **Service architecture:** re-examine whether "nacelle-off-spar" service
  (`docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md`) still
  makes sense once the tube no longer transmits torque — a non-rotating wire
  tube may change what disconnects where, and whether a wingtip access
  point (the rejected "garage" concept, reconsidered on its own merits under
  this different mechanism) becomes appropriate. Do not assume the answer;
  re-derive it against whatever tube/bearing arrangement U3 lands on.

- **Pro:** the only option that structurally resolves the wire-vs-torque
  sizing conflict instead of trading it for a different one.
- **Con:** largest scope — a new drive mechanism, new bearing loads, and a
  hard dependency on the concurrently-evolving wing-root structure.

---

## Requirements

- **R1** — Pin a real `WIRE-10AWG` product: OD, insulation material/rating,
  and (if available) a cyclic-flex/bend-radius figure. Update
  `current-specification/bom_revS.csv` and add a `REFERENCES.md` entry. This
  blocks every downstream sizing decision (R2–R5) and is the first thing to
  close.
- **R2** — Derive the minimum real wire-bundle envelope (not the zero-clearance
  theoretical packing floor) for whichever routing geometry Option A/B/C
  implies, including realistic pull-through/assembly clearance.
- **R3** — If Option A is chosen: size and geometry-check a real service
  loop/pigtail against the confirmed 26–34mm chord sweep (A.2), with a
  checked minimum bend radius for the real wire construction (R1) and a
  modeled clearance envelope through the full −5°…90° sweep (and ideally the
  145° stale figure as a margin check).
- **R4** — If Option B is chosen: re-run `TILT_SPAR_ANALYSIS.md` §3's full
  trade study at the corrected ~20mm+ section, including the CF-keyway
  functional-gate conflict, the wingtip-bearing/fixed-gear re-derivation, and
  the A.4 twist-fatigue check at the real construction and sweep angle.
- **R5** — If Option C is chosen: derive belt/sprocket sizing against the
  `TILT_SPAR_ANALYSIS.md` §2.1 grounded torque requirement (with the same
  margin convention), the tube's new (non-torque) bearing arrangement, belt
  routing checked against the concurrent wing-root/thwart rework, duct-core
  blockage, mass/CG, and the service-architecture question — matching
  `TILT_SPAR_ANALYSIS.md`'s own rigor (each candidate gets a real FOS, not an
  assumption).
- **R6** — No geometry (SCAD) changes are made until **U4** (owner decision
  among A/B/C) is resolved.
- **R7** — Whichever option is adopted, update `airframe/wings-nacelles/WBS.md`,
  `PROJECT_INDEX.md`/`tools/index_tags.json` (via `tools/precommit_index.py`),
  and close out U6 in the 2026-08-26 nacelle-ESC-intake plan.

## Implementation units

### U1 — Pin real wire product data

Source or measure an actual 10 AWG silicone wire product's OD and
flex/bend-radius rating; record in the BOM and `REFERENCES.md`. Blocks U2.

### U2 — Derive the real bundle envelope

Using U1's figures, compute the minimum practical (not zero-clearance)
envelope for the 4-wire bundle under each of Option A/B/C's routing
geometry, for direct comparison in U4.

### U3 — Option C feasibility study (belt/sprocket torque decoupling)

Work the full derivation in Part B's Option C bullet list: torque/belt
sizing, bearing re-arrangement, belt routing vs. the concurrent wing-root
rework, duct blockage, mass/CG, service-architecture impact. Produce FOS
figures matching `TILT_SPAR_ANALYSIS.md`'s style, not qualitative claims.

### U4 — Owner decision gate

Present Options A/B/C with U1–U3's real numbers; owner selects a direction.
**No SCAD geometry is touched before this gate closes** (R6).

### U5 — Geometry implementation (post-decision)

Scoped once U4 resolves — the specific SCAD/BOM/WBS edits depend entirely on
which option is selected and are not pre-specified here.

### U6 — Regenerate and verify

Standard pipeline re-render + the existing changed-geometry gates (below),
plus closing U6 in the 2026-08-26 plan explicitly.

## Verification contract

1. `WIRE-10AWG` BOM entry carries a real, cited OD and flex rating (R1).
2. The chosen option's wire-bundle envelope is verified against U1's real
   figures with realistic assembly clearance, not the zero-clearance
   theoretical floor.
3. Option A: service-loop clearance verified through the full −5°…90° sweep
   (no solid overlap at any sampled tilt angle), minimum bend radius met.
   Option B: full `TILT_SPAR_ANALYSIS.md`-equivalent trade study delivered
   with real FOS figures at the corrected section; CF-keyway conflict
   explicitly resolved (material change or torque-path redesign). Option C:
   belt/sprocket FOS delivered against the grounded torque requirement;
   bearing arrangement re-derived, not assumed.
4. No SCAD changes precede the U4 decision gate.
5. Run the changed-geometry gates once geometry is touched:

   ```text
   python3 tools/validate_stls.py
   python3 tools/wing_root_deconflict.py
   python3 tools/wing_internal_clearance.py
   python3 tools/wing_spar_carrythrough.py
   python3 tools/cargo_bay_envelope.py
   python3 tools/landing_gear_wing_clearance.py --proud
   ```

6. `docs/plans/2026-08-26-001-nacelle-esc-intake-integration-plan.md` U6 is
   marked closed, citing this plan's resolution.
7. Mass/CG and hover T/W re-checked against `docs/structural_analysis.md`'s
   convention if the adopted option changes airframe mass distribution
   (Options B and C both plausibly do; Option A should not).

## Open gates

- Real `WIRE-10AWG` OD/flex-rating — nothing below this can be finally sized
  without it (R1/U1).
- Owner decision among Option A/B/C (U4) — this plan does not pick one.
- If Option C: the belt-routing interface with
  `docs/plans/2026-08-24-001-fix-wing-repair-root-joint-plan.md`'s CF-thwart
  geometry, which is still in flight in the same wing station range.
- Whether the 145° tilt figure (`REVN_BUILD_GUIDE_24IN.md`) is a real
  commanded design range or stale pre-Rev-T test-step text (already flagged
  as unresolved in `TILT_SPAR_ANALYSIS.md` §2.1.2) — affects the sizing
  margin for whichever option is chosen.
