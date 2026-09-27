---
title: "pcbnew: FOOTPRINT.Flip()/SetLayerAndFlip() segfaults if called before board.Add()"
date: 2026-09-21
category: runtime-errors
module: "avionics/kicad (any board's PCB-sync script using pcbnew Python scripting)"
problem_type: runtime_error
component: tooling
severity: high
symptoms:
  - "Python process exits with code 139 (SIGSEGV), no traceback, while placing a freshly `pcbnew.FootprintLoad()`-ed footprint onto the back copper layer"
  - "Crash reproduces identically whether the flip call is `fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)` or `fp.SetLayerAndFlip(pcbnew.B_Cu)`"
  - "The same call succeeds immediately once `board.Add(fp)` runs first"
root_cause: wrong_api
resolution_type: code_fix
related_components:
  - avionics/kicad/Observer/PCBNEW_SWIG_BUG.md
  - avionics/kicad/Commo/kicads/Commo.kicad_pcb
tags: [kicad, pcbnew, swig, segfault, footprint, flip, back-layer, python-scripting]
---

# pcbnew: FOOTPRINT.Flip()/SetLayerAndFlip() segfaults if called before board.Add()

## Problem

A `pcbnew` Python script that loads a footprint via `pcbnew.FootprintLoad()` and
immediately flips it to the back layer (`FOOTPRINT.Flip()` or the higher-level
`FOOTPRINT.SetLayerAndFlip()`) segfaults the interpreter — no Python exception, no
traceback, just `rc=139`. This happened while placing a new `RFD900ux-SMT` SiK
radio footprint on Commo's back copper (`Commo.kicad_pcb`), one step in the
XO/Commo radio-relocation PCB sync (see the `pb2-cape-datasheet-verified-footprints`
convention doc and `avionics/kicad/Observer/PCBNEW_SWIG_BUG.md`, a related but
distinct pcbnew SWIG-binding defect report from the Jayne PCB rebuild).

## Symptoms

- `fp = pcbnew.FootprintLoad(lib_dir, fp_name); fp.SetPosition(...); fp.SetOrientationDegrees(90); fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)` — segfaults on the `Flip()` line, confirmed by `-u` unbuffered stdout showing every print up through `orient set` / `flipped? False` and then nothing.
- Same crash with `fp.SetLayerAndFlip(pcbnew.B_Cu)` in place of `Flip()`.
- No Python-level `TypeError`/`AttributeError` — this is a native crash, not a wrapper-typemap defect like Defects B/C in `PCBNEW_SWIG_BUG.md`.

## What Didn't Work

- Passing a bad `aFlipDirection` value (e.g. `True`, or a nonexistent
  `pcbnew.FLIP_DIRECTION_N_TO_S`) also segfaults `Flip()` — this looked like the
  root cause at first, but fixing the enum to the real
  `pcbnew.FLIP_DIRECTION_TOP_BOTTOM` (confirmed via `dir(pcbnew)` — only
  `FLIP_DIRECTION_LEFT_RIGHT` and `FLIP_DIRECTION_TOP_BOTTOM` exist in this
  build) still segfaulted. The enum-mismatch theory was a red herring; bisecting
  further (adding `flush=True` prints between every call) isolated the real
  trigger to call order, not argument value.

## Solution

Call `board.Add(fp)` **before** `fp.Flip(...)` / `fp.SetLayerAndFlip(...)`, not
after:

```python
import pcbnew

board = pcbnew.LoadBoard("Commo.kicad_pcb")
fp = pcbnew.FootprintLoad(lib_dir, fp_name)
fp.SetReference("SIK")
fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(110.0), pcbnew.FromMM(117.0)))

board.Add(fp)                          # <-- must happen before flip/layer-move

fp.SetLayerAndFlip(pcbnew.B_Cu)        # now safe
fp.SetOrientationDegrees(90)
```

Confirmed via an isolated repro: the identical `Flip()`/`SetLayerAndFlip()` call
segfaults on a `FootprintLoad()`-returned object with no board owner, and succeeds
on the same object immediately after `board.Add(fp)`.

## Why This Works

`FOOTPRINT::Flip()` (and the `SetLayerAndFlip()` convenience wrapper around it) is
implemented in KiCad's C++ core to touch board-relative state (net/connectivity
bookkeeping, possibly the board's design-rule/units context) that only exists once
the footprint is owned by a `BOARD`. A `FOOTPRINT` fresh out of `FootprintLoad()`
has no board pointer set. In the GUI this ordering constraint is invisible because
placement UI always operates on footprints already on the board; the raw Python
API exposes the same call with no guard, so calling it on an orphan object walks a
null/dangling board reference in C++ and crashes instead of raising a catchable
Python exception.

This is a different class of defect from the three cataloged in
`avionics/kicad/Observer/PCBNEW_SWIG_BUG.md` (which are wrapper/typemap issues —
`FootprintLoad`-after-`Remove` leaking `FOOTPRINT*`, `Pads()` returning a raw
`SwigPyObject`, `FindPadByNumber()` returning an unwrapped object) — those crash or
misbehave regardless of add-order. This one is a genuine call-order precondition on
an otherwise-working method, not a wrapper bug. Notably, `PCBNEW_SWIG_BUG.md`'s own
listed workaround already calls `SetLayerAndFlip` — but only *after* its `board.Add`
call in the same sequence, which is why that script never hit this crash: the safe
order was already accidentally in use there.

## Prevention

- **Always sequence pcbnew footprint placement as: `FootprintLoad` → set
  reference/value/position → `board.Add(fp)` → flip/layer-move → orientation →
  pad/net assignment.** Never call `Flip()`, `SetLayerAndFlip()`, or any other
  board-relative mutator on a footprint object before it has been added to a
  `BOARD`.
- When bisecting a pcbnew segfault with no Python traceback, run the script
  unbuffered (`python3 -u`) with a `flush=True` print after every pcbnew call —
  the crash gives no stack trace, so the last-printed line is the only localization
  signal available.
- Because this project's own established convention
  (`feedback_generator_drift_and_freerouting` memory note) already favors
  non-destructive, targeted `pcbnew` scripting over full PCB regeneration for
  drifted boards, this exact load→add→flip pattern will recur on every future
  PCB-sync script — worth checking this doc before writing a new one.
