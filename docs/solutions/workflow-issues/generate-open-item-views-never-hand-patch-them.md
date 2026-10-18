---
title: "A 'generated' open-items view that has no generator becomes the source of truth by accident"
date: 2026-09-15
category: workflow-issues
module: "WBS.md / TODO.md federation (AGENTS.md §10); tools/gen_todo_from_wbs.py"
problem_type: workflow_issue
component: development_workflow
severity: high
applies_when:
  - "a policy says file B is generated from file A, but nothing in the repo actually generates it"
  - "closing, adding, or reconciling items in any TODO.md / WBS.md pair"
  - "two views of the same task list disagree and you are deciding which to trust"
  - "an audit finds open items in the summary view with no home in the record"
related_components:
  - tools/gen_todo_from_wbs.py
  - TODO.md
  - WBS.md
  - docs/WBS_FEDERATION.md
  - docs/WBS.md
tags: [wbs, todo, federation, generated-files, drift, source-of-truth, documentation]
---

# A "generated" open-items view that has no generator becomes the source of truth by accident

## Context

Root `AGENTS.md` §10 has said since Rev S2 that every `TODO.md` is "a lean,
generated-from-`WBS.md` list … regenerated/pruned from there, never edited as the
source of truth." No generator existed. Every one of the 17 `TODO.md` files had
therefore been hand-edited for two months, and by 2026-09-15 the split had inverted in
several places:

- Root `TODO.md` §0.8/§0.8.1 carried ~25 wing-attach and mass-audit items that root
  `WBS.md` §0.8 had never received. The *only* record of that work was in the file that
  is supposed to be disposable.
- Root `TODO.md` §1.2d carried the entire 12-item MSPM0G351x retarget backlog; no
  `WBS.md` anywhere had it.
- `avionics/TODO.md` carried the nine units of plan 2026-08-25-001; `avionics/WBS.md`
  did not.
- The reverse failure too: `airframe/wings-nacelles/TODO.md` listed **4** open items
  while its `WBS.md` had **44** genuinely-open top-level entries, and root `WBS.md`
  §1.1.3 still indexed 11 lines that the owner file did not contain in any form.
- 43 % of root `TODO.md` lines were multi-paragraph prose against a one-line cap.

None of this was malicious or careless — each edit was locally reasonable. The
mechanism is simply that a file declared "generated" but maintained by hand is *edited
where the reader is looking*, and the reader looks at the short file.

## Guidance

**If a policy says a file is generated, the generator must exist and be run — or the
policy is fiction and will produce the exact drift it was written to prevent.**

In this repo, the order of operations for any task-list change is now:

1. Write or close the item in the **owning `WBS.md`** (full notes there).
2. If the root index tracks that branch, add/close the ≤70-char line in root `WBS.md`.
3. Run `/usr/bin/python3 tools/gen_todo_from_wbs.py` (or `--check` before committing).
4. Never edit a `TODO.md` by hand. If a `TODO.md` line has no `WBS.md` home, that is a
   defect in the record — move the content *into* the WBS, then regenerate.

The generator's promotion rule is worth knowing when you read its output: an open
sub-item under a **closed** parent is promoted to its own line (the parent no longer
represents it); an open sub-item under an **open** parent folds into the parent. A
parent whose text says "DONE" but whose checkbox is `[ ]` because sub-items remain is a
smell — re-title it to name the remaining work, per the never-leave-a-resolved-item-
unchecked rule (`feedback_todo_stale_items`).

## Why This Matters

The cost was not the two months of drift — it was what the drift hid. The 2026-08-22
documentation audit had already flagged root `TODO.md` as "the single largest compliance
gap" and deferred it as "a substantial editorial task". It was not editorial. Once the
generator existed the mechanical part took minutes; the real work was discovering that
~50 items had **no home in the record at all** and would have been lost the first time
someone did the "obvious" fix of regenerating `TODO.md` from `WBS.md` without checking
for orphans first.

A second-order effect: with the summary and the record disagreeing, every audit that
read one file and not the other produced confident, wrong counts
(`docs/FIRST_FLIGHT_READINESS.md` 2026-07-05 carried two stale-warning banners for a
month because nobody could say what the true numbers were).

## When to Apply

- **Before regenerating any derived file for the first time**, diff the old derived file
  against the new one and hunt for content that exists *only* in the derived file. Move
  it into the source, then regenerate. Deleting it "because it's generated" is how a
  record loses work.
- **When a policy names a generated artifact**, check that the generator is in the tree
  and wired into a check (`precommit_index.py --check` is the model here). If it is not,
  writing the generator is the fix; tightening the prose in the policy is not.
- **When two files disagree**, the one with the rationale and the closed items is the
  record; the short one is the view. But do not discard the view's extra content — it is
  evidence of where the record has holes.

## Examples

```text
# before: view carries work the record never received
root TODO.md §0.8.1 : 25 open WA-R*/MA-* lines
root WBS.md  §0.8   : 3 lines, no §0.8.1 at all

# fix order
1. write the 25 lines into root WBS.md §0.8/§0.8.1 (one-liners, → detail pointers)
2. /usr/bin/python3 tools/gen_todo_from_wbs.py
3. git diff TODO.md   → confirm nothing was lost, only reformatted

# guard
/usr/bin/python3 tools/gen_todo_from_wbs.py --check   # exit 1 on any drift
```
