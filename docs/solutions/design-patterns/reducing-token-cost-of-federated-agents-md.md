---
title: Reducing token cost of a federated AGENTS.md set — relocate before you compress
date: 2026-08-08
category: design-patterns
module: agent-instructions
problem_type: design_pattern
component: documentation
severity: medium
applies_when:
  - Reducing the token cost of AGENTS.md, CLAUDE.md, or any federated agent-instruction set
  - Deciding whether to compress prose, deduplicate rules, or split content into sibling docs
  - Building a measurement harness for a documentation-optimization run
tags: [agents-md, token-cost, documentation, ce-optimize, instruction-files, llm-judge]
---

# Reducing token cost of a federated AGENTS.md set — relocate before you compress

## Context

The Serenity-UAV repository carries nine federated `AGENTS.md` files (root plus
eight subsystem files) totalling **22,324 tokens** (tiktoken `cl100k_base`). The
root file alone was 5,366 tokens and loads on *every* session via `CLAUDE.md`,
so its cost is paid far more often than any subsystem file's.

A `ce-optimize` run tested three competing strategies against that set, each as
an isolated full-set rewrite in its own git worktree, gated by a mechanical
harness and scored by independent LLM judges. The strategies were deliberately
run separately rather than blended, so the run would learn *which lever actually
pays* instead of just producing one smaller set of files.

The instinct going in was that these files were verbose and needed tighter
prose. That instinct was wrong, and measurably so.

## Guidance

**Rank the levers in this order. The order is not a preference — it is what the
measurements showed.**

### 1. Relocation (strongest)

Move content that is not agent *guidance* out of the instruction file into a
sibling reference doc, leaving a pointer that names the file and section.

Roughly **8,000 of the 22,324 tokens were never instruction at all**: design
specification tables, document templates, and sign-off checklists that happened
to live in an `AGENTS.md`. An agent reading instructions does not need a
telemetry-rate table inline; it needs to know the table exists and where.

Result: **−30.4%** with a perfect hard-gate sweep and **5.0/5 judge fidelity,
zero directives lost**.

### 2. Ownership deduplication (strong, but only *after* relocation)

Assign every duplicated rule exactly one owning file; reduce every other mention
to a pointer. Project-wide rules go to root; scope-specific rules to the
subsystem file.

Layered on top of relocation this delivered a further **−5.9%** (cumulative
−34.5%) and cut cross-file duplicate 6-word shingles from **272 to 101**.

### 3. Prose compression (weakest — and actively destructive here)

Rewriting expository prose into terser imperative prose bought **−13.0%** and
**failed the gates twice**.

**Order matters, and the failure mode is specific.** Run dedup *before*
relocation and it underperforms: dedup alone made the **root file grow**
(5,366 → 5,403), because absorbing the rules root now owns cost more tokens than
the duplicates removed from other files. The lever only pays once relocation has
already removed the non-guidance bulk.

**Build the harness to gate on preservation, not just size.** Size alone is
trivially gamed by deletion. Gate on:

| Gate | Threshold used | Catches |
| --- | --- | --- |
| REF-IDs / citations preserved | 100% | dropped standards references |
| Engineering quantities preserved | 100% | dropped masses, dimensions, frequencies |
| Section references preserved | ≥98% | dropped regulatory subsections |
| Repo file paths preserved | ≥97% | severed cross-references |
| Orphan docs | 0 | relocated content nothing points to |
| Min file size | ≥250 tokens | a file gutted to a stub |

Extract these sets **from the instruction files only**, then check survival
against instruction files **plus any newly created sibling docs**. That
asymmetry is what makes relocation count as preserved while deletion does not.
Extracting the baseline from the whole tree instead makes every gate pass
automatically on content no experiment can touch.

**Keep an LLM judge in the loop.** Mechanical gates cannot detect a *weakened*
rule — a `must` softened to `should`, or a pointer aimed at a section that does
not contain what it claims.

## Why This Matters

The naive approach to "make the instructions smaller" is to rewrite the prose,
and that is the one approach measured here that both saved the least and broke
the most.

**Compression destroyed cross-references reproducibly.** Two independent
compression runs landed on `paths_preserved: 0.8523` — the *identical* value —
the second despite a prompt explicitly warning about the first failure. Repo
paths live in exactly the connective "see *such-and-such file* for the current
revision" sentences that prose compression targets, so ~15% of them are shed as
a structural property of
the content, not as worker error. A reproducibility signal that clean is worth
more than either run alone.

**Relocation is nearly free in fidelity terms because it changes location, not
content.** Three independent judges scored 5.0/5 fidelity with zero directives
lost. Deletion and rewriting both risk meaning; moving does not.

**Root is worth more than its share.** Root fell 5,366 → 4,677 (−12.8%). Because
it loads every session while subsystem files load only in scope, a token cut in
root compounds across far more invocations than the same cut anywhere else.
Weight effort accordingly.

**The `restate-and-cite` anti-pattern is invisible to mechanical checks.** A file
names another as the authoritative owner of a rule *and then restates the rule in
full anyway*. Judges found four instances (`docs`→root §5 units,
`airframe`→root §7 joints, `avionics`→root §5 footprint placement,
root §10→`tools/TOOL_REFERENCE.md` invocations). Shingling sees reworded prose;
set-membership sees the value preserved, because it *is* preserved — twice.
Detecting it requires reading citing and cited file together, which is what an
LLM judge does and a harness cannot. Worth an estimated 400–700 further tokens.

**Deduplication surfaces latent contradictions, which is a feature.** Forcing a
rule to have one owner exposed a pre-existing conflict: the Inara stack's
secondary comms link was documented as LoRa in `avionics/AGENTS.md` but
SiK-MAVLink in root §9. Two files can disagree indefinitely; one owner cannot.
Expect consolidation to surface real defects, and route them to adjudication
rather than letting the consolidating agent silently pick a side.

## When to Apply

- Any federated instruction set (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`) that
  has grown past roughly 10k tokens
- Before reaching for prose compression as the default remedy for verbose docs
- When a root instruction file is loaded on every session and has become large
- When several subsystem instruction files restate the same project-wide rules

Do **not** apply the compression lever at all without a path-preservation gate
watching it.

## Examples

### Relocation — the pattern that worked

Before, in `gcs/AGENTS.md` (inline reference tables, ~1,700 tokens of the file):

```markdown
### Telemetry Data Rates

| Data Type | Rate (Nominal) | Rate (Degraded) | Priority |
| --- | --- | --- | --- |
| Flight state (attitude, altitude, airspeed) | 50 Hz | 10 Hz | Critical |
| Position (GPS) | 10 Hz | 2 Hz | High |
...
```

After — the table moves to `gcs/SKIPPER_SPEC.md` verbatim, and the instruction
file keeps only a pointer:

```markdown
Telemetry rates, command-priority levels, hardware requirements and SITL detail:
`gcs/SKIPPER_SPEC.md`.
```

The quantities still exist and still gate as preserved; they simply are not paid
for on every read of the instruction file.

### The `restate-and-cite` anti-pattern to avoid

```markdown
Units follow root `AGENTS.md` §5.

All measurements shall be expressed imperial-primary with metric in parentheses:
10 in (254 mm), 2.5 lbm (1.13 kg), 4.8 lbf (21.4 N). Use lbm for mass and lbf
for force; never write bare "lb"...
```

The pointer is correct and the restatement immediately undoes its benefit. Keep
the pointer, delete the restatement.

### Harness asymmetry that makes relocation measurable

```python
# Baseline captures the AGENTS.md set ONLY. Sibling docs are immutable during
# the run, so including them would let the gates pass on content no experiment
# can touch -- making them meaningless. Coverage is still *checked* against
# AGENTS.md + siblings, so relocating a fact into a sibling doc counts as
# preserved.
manifest = extract_sets(agents_texts)
```

Getting this backwards was a real bug in the first version of the harness: the
baseline initially swept 65 pre-existing sibling docs, which made the
preservation gates near-tautological.

## Related

- Run artifacts: `.context/compound-engineering/ce-optimize/agents-md-token-cost/`
  (`experiment-log.yaml`, `strategy-digest.md`, `judge-scores-exp005.yaml`,
  `judge-scores-exp007.yaml`) — local scratch, not tracked in git
- Commits on branch `optimize/agents-md-token-cost`: relocation pass, then the
  ownership-dedup pass layered on it
- `AGENTS.md` §11 — the conflict-resolution hierarchy that correctly routed the
  Inara contradiction to user adjudication instead of a silent fix
