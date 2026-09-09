---
title: "A source file's 'first-pass / VERIFY' comment may be stale — read the decision record first"
date: 2026-09-09
category: workflow-issues
module: "docs/ decision records; repo-wide investigation workflow"
problem_type: workflow_issue
component: development_workflow
severity: medium
applies_when:
  - "about to build a verification tool, run an expensive search, or re-derive geometry for a component whose source comments say first-pass, placeholder, TBD, or VERIFY"
  - "picking up an open VERIFY/WBS item whose subsystem has a trade study or decision record in docs/"
  - "a source file's own header is the only thing framing the problem you are about to solve"
related_components:
  - docs/NOZZLE_DRIVE_TRADE.md
  - airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad
  - airframe/wings-nacelles/WBS.md
  - tools/nozzle_linkage_check.py
tags: [decision-records, trade-study, stale-source, investigation-order, verify-items, wbs]
---

# A source file's "first-pass / VERIFY" comment may be stale — read the decision record first

## Context

`airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad` carried a clear,
well-written header flagging its own geometry as first-pass and instructing:
*"MUST be solved with a kinematic study / motion sim before this geometry is
relied upon... Do NOT print for flight hardware until closed."*

Taken at face value, that reads as an open engineering question with a defined
next step. So the next step got taken: a purpose-built checker
(`tools/nozzle_linkage_check.py`), then an exhaustive 336-combination sizing
sweep, then a written-up conclusion recommending the subsystem's trade study be
reopened.

The trade study had already been amended to answer it — on 2026-07-19,
seven weeks earlier. `docs/NOZZLE_DRIVE_TRADE.md` contains a "DECISION
AMENDMENT — hybrid A+B adopted" section that diagnoses the same defect more
cleanly *and* records the adopted replacement. The SCAD file was a stale
implementation of a superseded decision, and its honest-looking header was
describing a world that no longer existed.

## Guidance

**Before building verification tooling or running an expensive search against a
component flagged first-pass/placeholder/VERIFY, read that subsystem's decision
record.**

Concretely, in this repo, before acting on such a flag:

1. Look for a governing document — `docs/*TRADE*.md`, a decision record, or the
   subsystem's own `docs/` write-up.
2. **Read to the end of it.** The answer here lived in a *later amendment
   section*, not the original decision — a document can be superseded by its own
   tail. Reading the top-line "DECISION — Option B ADOPTED" and stopping would
   have produced the same miss.
3. Check the WBS entry for the item, which may cite the amendment.
4. Only then decide what tooling, if any, the open question actually needs.

The underlying asymmetry is what makes this worth a rule: **source comments and
decision records drift in opposite directions.** A decision record is updated
when the decision changes. A source comment is updated when someone edits that
file — which, for superseded geometry nobody is building, is *never*. So the
staler the component, the more confidently wrong its header becomes, and the
more it looks like a trustworthy open question.

## Why This Matters

The direct cost was a tool plus an exhaustive search to rediscover, less
cleanly, a conclusion already written down.

The larger cost was nearly a **wrong entry in the WBS**. The sweep's empty
result was written up as a possible new topology finding recommending the trade
study be reopened — pointing a future reader at a question that was already
answered, and framing settled work as unsettled. Bad documentation of this kind
is worse than none: it is inherited as fact and it sends the next person in a
circle. It had to be corrected in a follow-up commit.

There is a salvage worth noting, though, so the lesson is not "never verify":
the checker built along the way is genuinely useful and now encodes the
constraint permanently, and the search independently *re-confirmed* the
amendment's diagnosis. The error was one of **order**, not of effort — the same
work sequenced after reading the decision record would have been cheap,
targeted, and correctly framed.

## When to Apply

- **Any `[OPEN — VERIFY]` or first-pass item you are about to close.** Treat the
  source file's framing as a hypothesis to check, not as the problem statement.
- **When source and a decision record disagree, the decision record wins** —
  and the mismatch is itself a finding: it means a SOURCE follow-up was never
  applied. Record that explicitly (here, the amendment had already named the
  exact follow-up: *"move the `nacelle_nozzle_pushrod.scad` crank from the spar
  onto the pinion"*, which had not been done).
- **When an investigation contradicts an existing document**, check whether the
  document already agrees with you before reporting the finding as new. Fresh
  confirmation of a known result is a fine outcome — but it must be labelled as
  confirmation, not discovery.

## Examples

**What was done (costly order):**

```
read SCAD header ("first-pass, VERIFY, do NOT print")
  → build tools/nozzle_linkage_check.py
  → exhaustive sweep: 336 combinations, 0 pass
  → write up as possible new finding, recommend reopening the trade study
  → [later] read docs/NOZZLE_DRIVE_TRADE.md → already answered 2026-07-19
  → corrective commit to fix the WBS and SCAD notes
```

**The cheap order:**

```
read SCAD header ("first-pass, VERIFY, do NOT print")
  → read docs/NOZZLE_DRIVE_TRADE.md, including its amendments
  → find "DECISION AMENDMENT — hybrid A+B adopted (2026-07-19)"
  → note the SOURCE follow-up it names was never applied
  → implement the adopted design; optionally build the checker to guard it
```

Same tools, same conclusions, none of the rework and none of the wrong WBS
entry.
