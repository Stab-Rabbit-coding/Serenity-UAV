---
title: "A gate's checks and its exit code come from one list, so a check can never be printed and not enforced"
date: 2026-10-11
category: conventions
module: "tools (every gate script; first found in the landing-gear bay census)"
problem_type: convention
component: tooling
severity: high
applies_when:
  - "a gate script computes several checks and prints each one"
  - "a new check is added to an existing gate"
  - "a second tool reuses another tool's checks (wrapper gates, CI shims)"
related_components:
  - tools/landing_gear_bay_function.py
  - tools/landing_gear_wing_clearance.py
tags: [gate, fail-open, exit-code, census, landing-gear, ci]
---

## Context

On 2026-10-10, `tools/landing_gear_bay_function.py` gained new function
checks: wires against the stop pin, wires against the bay, wires against
the leg at rest, and the stop pin against the leg sweep. Each one was
computed and printed on every run. The PASS/FAIL line and the exit code
still tested only the two older checks (bay body count and leg sweep against
its own bay). A background security review on 2026-10-11 flagged this as a
fail-open gate. A wire running through the stop pin would print a number and
still exit 0.

The same commit put the wires and the stop pin on the census's
`BUILD_ONLY` list, which keeps generator inputs out of the target census.
So they were never checked against the hull, the wing or the cargo
interior either.

`tools/landing_gear_wing_clearance.py` check 5 reused the census but
re-implemented its own narrower body-count test. That was a second copy
that could drift.

## Guidance

1. **Keep one list of limits.** In the census it is `FUNCTION_LIMITS`. A
   single predicate, `function_ok()`, tests the body count and every key in
   it.
2. **Drive the printout, the exit code and every reuse from that predicate.**
   The census `main()` prints `OK` / `FAIL` with `function_ok(f)` and exits 2
   when any corner fails it. The wing-clearance wrapper calls the same
   predicate and reports each key that failed.
3. **Treat "build-only" lists as exclusions that need a reason.** A
   procured part (wire, pin, fastener) is a census target, not a generator
   input. Only true generator inputs (outline prisms, cut bodies) are
   excluded.
4. **Prove a new check can fail before trusting it.** Run it on a design
   that is known to be bad. Here the Rev R6 single-row wire layout (wires
   inside each other) now fails the run.

## Why This Matters

A gate that prints a failing number and exits 0 is worse than having no
check. It produces green CI and a log that looks thorough. Nobody reads the
log of a passing gate. This repo has already been bitten by gates that
looked green and hid real defects; see the related docs below.

## When to Apply

- Every time a check is added to a gate, or a gate is wrapped by another.
- In review: search for any computed metric that does not appear in the
  exit condition.

## Examples

**Before.** `ok = f["bay_bodies"] == 1 and f["leg_sweep_vs_own_bay_mm3"] < CLASH_MM3`
decided the printout, while the four wire and stop-pin checks were only
formatted into the line.

**After.** `FUNCTION_LIMITS` lists all six interference keys.
`function_ok(f)` requires one body and every key under `CLASH_MM3`. Both
gates call it.

## Related

- [gate-a-part-invariant-at-every-selector-value-it-is-published-at.md](../design-patterns/gate-a-part-invariant-at-every-selector-value-it-is-published-at.md)
  — the sibling failure: an invariant claimed in a comment, never gated.
- [envelope-gates-pass-while-real-parts-clash.md](../design-patterns/envelope-gates-pass-while-real-parts-clash.md)
  — gates that stay green on an idealisation.

AI attribution: drafted by Claude (Claude Opus 5.5, Anthropic) from the
2026-10-11 session, under the direction of Stab-Rabbit-coding.
