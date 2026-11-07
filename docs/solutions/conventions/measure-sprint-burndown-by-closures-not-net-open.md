---
title: "Measure a sprint by the items it closes, not by the net open count — or recording findings looks like failure"
date: 2026-11-07
category: conventions
module: "tools/wbs_burndown.py; docs/plans/2026-11-07-001-feat-rev-u-completion-execution-plan.md"
problem_type: convention
component: development_workflow
severity: medium
applies_when:
  - "setting a measurable exit criterion for a sprint over the WBS/TODO federation"
  - "writing a burndown or progress counter for the WBS files"
related_components:
  - tools/wbs_burndown.py
  - tools/gen_todo_from_wbs.py
tags: [burndown, sprint, metrics, wbs, federation, goodhart]
---

# Measure a sprint by closures, not the net open count

## Problem

The first `wbs_burndown.py` gated sprints on "the open total drops by n". `AGENTS.md` requires every finding
to be recorded in the owning WBS the same day, and the planning sprint itself added five items. Under a net
count, a sprint that closes 12 items and records 4 real defects shows −8 and fails a −12 target. The metric
pays agents to hold findings back.

## Convention

- Count **closures** (`closed+`: checked boxes not inside an open box, the same nesting rule as
  `gen_todo_from_wbs.extract_open_items`). Report `d_open` next to it, and list new findings in the PR.
- Reuse the federation's own file list (`gen_todo_from_wbs.PAIRS`) and open-item rule. A second glob
  drifts. The first version counted `tools/TODO.md` and `current-specification/TODO.md`, which are not
  WBS-generated.
- Report the root `WBS.md` on its own row. It repeats many subsystem lines and also owns project-wide
  items, so adding it double counts and leaving it out hides root-owned work.
- Close superseded duplicates. An open duplicate inflates the baseline, and whoever closes it later gets
  credit for work nobody did.
