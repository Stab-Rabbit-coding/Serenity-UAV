---
date: 2026-10-31
artifact_contract: ce-unified-plan/v1
artifact_readiness: requirements-only
product_contract_source: ce-brainstorm
status: draft
authors:
  - Stab-Rabbit-coding (owner decisions)
  - Claude Opus 5.5 (synthesis and screening numbers; AI-generated, unreviewed)
---

# Forward trim room by equipment relocation, minimum uniform scale

## Problem

The rail-lever baseline puts the CG at Y 343.0 mm (13.50 in). That is +16.3 mm
(+0.64 in) aft of the hover thrust line at SPAR_Y 326.7 mm (12.86 in)
[docs/CG_RELOCATION_STUDY.md]. The owner's mass and space audit found no free
volume in the head or cargo section to move batteries or other mass forward.
The planned 0.5 in (12.7 mm) aft pivot shift alone leaves no bench or field
trim authority. The airframe shall have adjustable trim room forward of the CG
while staying as close to canonical proportions as practicable.

## Product Contract

### Goal

The CG shall sit forward of the hover thrust line by enough margin to give
bench and field trim authority. The primary means shall be relocating
equipment. Fuselage stretch is the secondary means and shall be used only to
create the volume that relocation needs.

### Requirements

- **R1 Relocation first.** The CG shall be closed by moving equipment forward
  before any increase in scale is considered. Movable candidates in moment
  order:
    - Flight Engineer + can: 225 g at Y 467.7.
    - Simon stack: about 130 g at Y 494.7.
    - Aft node pair: about 85 g at Y 416.2.
    - Cargo Observer: 60 g at Y 424.2.
- **R2 Minimum uniform scale.** Any stretch shall be a uniform scale of the
  whole fuselage, at the smallest factor that fits the relocated equipment.
  The cap is 27 in (686 mm). A plug or a local bulge is not acceptable.
- **R3 Stack composition.** There are four control stacks: Shepherd, Inara,
  River and Simon.
    - At least three shall remain full stacks: Pilot cape + PB2-I + TACCO
    cape + PB2-I.
    - One stack may become a NoNFO-Pilot + PB2-I. That stack is the PACE
    Emergency path.
- **R4 Stack distribution.** The four stacks shall stay distributed one
  forward, one aft, one port and one starboard as far as practicable. This
  limits single points of failure. A relocation that closes the CG by
  collocating stacks is not acceptable unless the owner explicitly accepts the
  loss of separation.
- **R5 Nose Observer.** The nose Observer shall stay fully forward to keep its
  sensor field of view.
- **R6 Hoist alignment.** The cargo hoist line shall stay aligned with the
  thrust line and the CG. The cargo Observer board may move, but its sensors
  shall keep the required view of the clamshell aperture.
- **R7 Pivot.** One fixed aft pivot shift (nominal 0.5 in) is permitted.
  Indexed pivot stations are out of scope.
- **R8 Trim authority.** The finished layout shall give a measurable trim
  range by cell rail travel and/or a forward battery cell station (R10; it replaces the
  dead-ballast pocket). The
  required range is not yet known (A1).
- **R9 Port/starboard symmetry.** The port/starboard symmetry gate (0.5 mm)
  and the shared-parameter rule of the joint-audit plan (R1–R6) shall continue
  to apply.

### Success criteria

- The rolled-up CG is forward of the thrust line at hover, with payload and
  with the third cell, with margin at least equal to the trim range set by A1.
- R3 to R6 are all met, as shown by the fit tool on real meshes, not by
  bounding boxes.
- The scale factor is the minimum that passes the fit, and it is at most
  27/24.

### Scope boundaries

- Out of scope: indexed pivot stations; a forward plug or local bulge;
  material selection (see docs/SLS_MATERIAL_SELECTION_3DSYSTEMS.md); the
  joint scheme (see docs/SLS_27IN_TWO_SECTION_TRIM_STUDY.md).
- Deferred to planning: the target station of each relocated item, which stack
  takes the NoNFO option, harness rerouting, and antenna placement.

## CORRECTION (2026-10-31, reconciled with branch work)

The screening figure below ("roughly 8 mm forward") is **superseded**. Three pieces of
later work on this branch change it:

- **Aft skin thinning.** Handling, not strength, sets the skin thickness, and 1.5 mm is the
  minimum wall for SLS PA CF. Credit: 0 to −2 mm
  (`docs/AFT_SKIN_THINNING_STUDY.md`).
- **Skid U-frame.** The PA12-CF skid U-frame with a ventral strut at Y 620 adds about
  +0.8 mm aft (`docs/SKID_FAILURE_MODE_STUDY.md` §8).
- **Baseline.** The one-piece middle+rear as-is gives +16.2 mm. Hover AUW in SLS is 6,211 g
  (`tools/sls_auw_reconcile.py`).

With these, relocation at 24 in reaches only about −1.9 to +0.1 mm
(`docs/ideation/2026-10-31-forward-trim-relocation-ideation.md` §2a). That is about on
the thrust line, with no trim room.

Owner direction (2026-10-31) adds **R10**:

- **R10 Live ballast.** Trim mass forward of the CG shall be battery cells, not dead
  ballast. A forward cell adds endurance as well as moment. The nose ballast pocket in R8
  is replaced by a forward cell station.

The minimum stretch is sized by `tools/min_stretch_relocation.py` (results in §Sizing
below).

## Screening numbers (pre-planning, unverified — superseded, see CORRECTION)

These are ledger-based figures from tools/cg_relocation_study.py items at
24 in. They are not a fit result.

- Moment to close: about 101,700 g·mm.
- Flight Engineer, Simon stack and aft node pair moved to about Y 250 recover
  about 95,000 g·mm. The 0.5 in pivot shift adds about 55,000 g·mm
  (12.7 mm × (1 − f), f ≈ 0.297). The net is roughly 8 mm forward of the
  thrust line.
- If Simon becomes the NoNFO stack, its mass falls by about half. That adds
  margin, or lets Simon stay aft and keep R4.
- Uniform scale worsens the base offset: +11.4 mm after the 0.5 in pivot
  shift at 27 in [docs/SLS_27IN_UNIFORM_SCALE_ADDENDUM.md]. Stretch therefore
  only buys volume.

## Assumptions and open questions

- **A1** The required trim range is unknown. Plan a bench pitch-authority
  measurement to set it.
- **A2** The Flight Engineer keeps its ventral service access wherever it
  goes.
- **Q1** Is there a relocation that meets R4 (distributed stacks) and still
  closes the CG at 24 in, or at a scale under 27 in?
- **Q2** If R4 and the CG conflict, which stack position gives way first?
  Owner decision.
- **Q3** Moving the Simon stack moves the bus-end termination and the SMA
  whips on the middle crown. RF and bus termination need to be rechecked.

## Sources

- docs/CG_RELOCATION_STUDY.md (rail-lever baseline, relocation search).
- docs/SLS_27IN_UNIFORM_SCALE_ADDENDUM.md (scale effect on CG).
- tools/cg_relocation_study.py, tools/auw_ledger.py (ledger moments).
- Owner direction, 2026-10-31 session (R2–R7).

## Sizing (2026-10-31, `tools/min_stretch_relocation.py`)

This is a free-space fit on meshes uniformly scaled about the nose. Equipment envelopes
are translated proportionally, not scaled. The single pivot is 0.5 in aft, Simon is the
NoNFO-Pilot stack, and the skid U-frame is included. Skin thinning is not credited.

| Scale | Flight Engineer | Aft stack (2 pouches) | Third cell forward of the thrust line | Hover offset |
| --- | --- | --- | --- | ---: |
| 24 in | no fit | no fit | no fit | +16.9 mm |
| 25 in | no fit | no fit | no fit | +18.3 mm |
| 26 in | no fit | 1 of 2 to Y 138 (centreline) | no fit | +16.6 mm |
| 27 in | no fit | both, to Y 93 and Y 156 (centreline) | no fit | +14.4 mm |

**Finding.** Uniform stretch up to 27 in does **not** open a forward slot for the Flight
Engineer (75 × 36 × 94 mm can) or for a 116 mm cell. The volume a stretch adds is spread
in thin slices between proportionally moved equipment, never in one usable bay. The aft
pouches that do fit at 26–27 in land on the centreline in the head. That violates R4
(port/starboard separation) and is not accepted.

**Consequence for this plan.**

- R2's premise ("stretch buys volume") fails for the items that matter. Forward room
  shall come from **re-laying out the forward bays**, not from stretch: consolidate and
  repack the head and cargo envelopes so that one FE-sized slot and one cell-sized slot
  open forward of the thrust line.
- **R10 by upsizing, not adding.** The cheapest live-ballast move that needs no new bay is
  a larger-capacity head cell in the existing rail (more mass at Y 216). Each 100 g added
  there is about 2 mm of CG [CALC], and it adds endurance. This needs a cell-length fit
  check on the rail.

**Limits.** The absolute offsets use raw ledger stations, not the rail-lever arrangement
of `tools/cg_relocation_study.py`, so they read about 6 mm aft of that study. Only the
fit / no-fit result is the finding here. The scale is a geometric stand-in for rebuilding
the hull from the owner's sources.
