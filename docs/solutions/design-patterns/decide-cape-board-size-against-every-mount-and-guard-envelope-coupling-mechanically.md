---
title: "Decide a multi-station cape's board size against every mount, and couple board size to airframe envelopes mechanically"
date: 2026-10-06
category: design-patterns
module: avionics/kicad/TACCO
problem_type: design_pattern
component: tooling
severity: high
applies_when:
  - "Growing a cape PCB that flies at more than one airframe station (nose tray, cargo chin shelf, middle-ring saddle) with different orientations"
  - "A routing-bound board (~95% courtyard fill, connections unrouted even after adding layers) needs more area"
  - "Choosing whether to grow board length or width when one station sits against an asymmetric/narrow hull wall"
  - "Pouch, tray, panel or shelf envelopes in SCAD/fit scripts are derived by hand from board dimensions"
  - "Running layout what-ifs through a wrapper that shifts a global reference such as X_CL"
symptoms:
  - "TACCO 55 x 35 mm left 60-90 connections unrouted on 6 layers and ~71 on 8 layers"
  - "55 x 40 mm failed the chin and middle-ring fits; only 58 x 35 fit all four stations as drawn"
  - "A 'bias the pair 0.5 mm to port' experiment shifted X_CL and silently moved the whole layout"
root_cause: missing_validation
resolution_type: tooling_addition
related_components:
  - avionics/kicad/TACCO/gen_tacco_pcb.py
  - tools/check_tacco_envelope_sync.py
  - tools/cargo_layout_fit.py
  - tools/middle_layout_fit.py
  - airframe/openscad/fuselage/cargo/chin_node_shelf.scad
  - airframe/openscad/fuselage/head_shell24.scad
  - .githooks/pre-commit
  - .github/workflows/ci.yml
tags: [tacco, board-size, multi-station, envelope-sync, cargo-section, middle-ring, ci-guard, cape-layout]
---

# Decide a multi-station cape's board size against every mount, and couple board size to airframe envelopes mechanically

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI note:** Drafted by Claude (Anthropic) under the author's direction, 2026-10-06, per `AGENTS.md` §3 AI attribution.
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0 (SPDX-License-Identifier: CC-BY-SA-4.0)

## Context

TACCO, the comms-node cape, flies at several airframe stations, and its orientation is different at each one. The nose (CN1) holds it in a Faraday tray. On the cargo chin (CN2/CN3) it sits as a pair of foil pouches on the chin shelf. In the middle ring (CN4) it goes in the Simon saddle slot. Each envelope is written in a different file (`tools/check_tacco_envelope_sync.py:4-11`). At 55 x 35 mm the board was routing-bound: courtyard fill was about 95%, 60-90 nets stayed unrouted on 6 layers, and about 71 stayed unrouted on 8 layers. The board needed more area. The open question was which dimension should grow, and how to keep every airframe mount and every printable STL in step with the change.

The owner chose 60 x 35 mm (`avionics/kicad/TACCO/scripts/gen_tacco_pcb.py:78`). The fix is open in PR #234, which has not merged. The earlier PR #229 is merged. See `avionics/kicad/TACCO/TACCO.md` §13b and `docs/CARGO_SECTION_LAYOUT.md` §0b (Rev T5g).

## Guidance

1. **Check each candidate size with the repo's fit gates at every station. Do not use area math.** Each candidate (58x35, 60x35, 55x38, 55x40) was tested on a scratch copy of `tools/cargo_layout_fit.py` and `tools/middle_layout_fit.py` with only the TACCO envelope changed. The nose was checked with section probes of `head_shell24_2mm_repaired.stl`. The results:
   - 58x35 was the only candidate that fit as drawn.
   - Length beat width because the starboard chin wall is the hull's narrow side, at 2.7 mm (`tools/cargo_layout_fit.py:269-271`).
   - 55x40 has roughly the same area as 58x35, but it failed both the chin and the middle station.
2. **Perturb only the envelope under test.** One wrapper "biased" the chin pair by shifting `X_CL`, which moved the whole layout (battery, brackets) relative to the shell. That result was invalid; it was a dead end.
3. **Record accepted trade-offs as named constants.** The owner chose 60x35. To make it pass, the owner accepted these changes:
   - A 1.5 mm chin gap (`CHIN_GAP`, `tools/cargo_layout_fit.py:274`).
   - The cable channel shrinks from 10 to 9 mm (`CHIN_CABLE`, `:275`).
   - The chin pair moves 2.7 mm aft (`N_CHIN_Y1 = 2.7`, `N_CHIN_Y0 = N_CHIN_Y1 - TACCO_L`, `:276-277`).
   - The shelf's aft lip is dropped (`:300`). Without that, only 0.4 mm remained to the payload.

   The chin nodes apply `gap=CHIN_GAP` at `:537-558`. The middle station derives its slot from the cargo tool: `SIMON_X0 = SIMON_X1 - cargo.TACCO_L` (`tools/middle_layout_fit.py:147`), while the FC4 slot stays at `FC4_X0 = SIMON_X1 - NODE_L` (`:148`).
4. **Grow the board so fixed stations stay put.** `U_LO = -5.0` (`gen_tacco_pcb.py:79-81`) places the extra 5 mm over the PB2-I's microSD end. The PB2 frame, rails and every fixed station keep their positions.
   - Bottom-side parts in that overhang are limited by `B_OVERHANG_MAX_H = 8.0` (`:367`), not by the PB2-I. The check is in `b_height_ok`, using `PB2_U_EDGE` (`:366`, `:382-385`).
   - Pilot stays at 55 x 35 mm. Where the two share a station, the slot is sized to TACCO and the 58 mm Pilot pouch is port-justified in it (`FC4_X0`, `tools/middle_layout_fit.py:148`); the nose tray widens to the TACCO width (`airframe/openscad/fuselage/head_shell24.scad:307`).
5. **Enforce the board-size-to-envelope coupling in code.** `tools/check_tacco_envelope_sync.py` reads `BW, BH`, re-derives every envelope and compares each one with its written value. Both of these run it:
   - the pre-commit hook (`.githooks/pre-commit:22`)
   - CI (`.github/workflows/ci.yml:120-121`)
6. **Report pending STL re-exports; do not drop them.** The re-exports could not run in this session: openscad was missing, and manifold3d's API did not match. The check lists each stale printable as PENDING instead. That is a warning by default and fails with `--strict`.

## Why This Matters

Area math said 55x40 was as good as 58x35, but only the fit gates showed that it hits the hull's narrow starboard chin wall. The envelope for one board appears in about 11 places across fit tools, SCAD parameters, the head-shell SCAD and its Python builder (`check_tacco_envelope_sync.py:92-105`). Any one of them can drift silently. When STLs could not be rebuilt in a session, the re-export used to live only in someone's memory. The check turns both drift and a forgotten re-export into visible output. It was negative-tested by setting `BW` to 62: 4 envelope checks failed and the check returned rc=1 (session-reported count).

## When to Apply

- Any part that mounts at more than one station or orientation, when you are considering a resize.
- Choosing which dimension to grow when a board is routing-bound.
- Any dimension copied across SCAD, a Python builder and a fit tool.
- Any session that cannot regenerate printable STLs.

## Examples

The check derives each envelope from the board size and compares it with the written value (`tools/check_tacco_envelope_sync.py:88-111`):

```python
bw = num(GEN, r"^BW, BH = ([\d.]+), [\d.]+")
checks = [
    ("cargo TACCO_L (fit tool)", num(CARGO_FIT, r"^TACCO_L" + flt), bw + POUCH_L),
    ("nose FARADAY_ENC_X (SCAD)", num(HEAD_SCAD, r"^FARADAY_ENC_X" + flt), bw + TRAY_X),
    ...
]
for name, got, want in checks:
    ok = abs(got - want) < 0.01
```

The allowances are named constants: `POUCH_L = 3.0`, `POUCH_H = 2.0`, `TRAY_X = 5.0`, `PANEL_CLR = 2.0` (`:44-47`). At 60 mm these give `TACCO_L = 63.0` (`cargo_layout_fit.py:273`), `FARADAY_ENC_X = 65.0` (`head_shell24.scad:307`) and `BOOK_PANEL_X = 67.0` (`:328`).

The PENDING rule (`check_tacco_envelope_sync.py:115-125`) maps each STL to its sources (`:58-66`). An STL counts as stale when its last git commit is older than the newest commit of any of its sources, or when the file is missing:

```python
newest = max(last_commit(s) for s in srcs)
if not (REPO / stl).exists():   print(f"  PENDING {stl}: not exported yet")
elif last_commit(stl) < newest: print(f"  PENDING {stl}: older than ... — re-export")
...
return 1 if a.strict else 0      # warn by default, fail under --strict
```

An envelope mismatch always returns 1 (`:127-133`).

## Related

- `docs/solutions/design-patterns/one-module-is-the-single-source-of-layout-stations.md` — the single-source rule this extends across the PCB/airframe boundary.
- `docs/solutions/design-patterns/probe-the-published-hull-and-change-the-placement-class-not-the-margins.md` — origin of the chin-floor placement; its 2 mm result was for the 55 mm board.
- `docs/solutions/logic-errors/mesh-boolean-layout-proofs-silent-zero-volumes-and-shared-profiles.md` — pitfalls in the fit proofs used here.
- `docs/solutions/workflow-issues/generate-open-item-views-never-hand-patch-them.md` — the same "derived artefact goes stale" problem in another form.
- `docs/solutions/conventions/pb2-cape-datasheet-verified-footprints-and-courtyard-budget-before-layout.md` — the courtyard budget that showed 55 x 35 was area-bound.
- Tracking: TACCO-60 in `airframe/fuselage-mid/WBS.md`; decision record `avionics/kicad/TACCO/TACCO.md` §13b.
