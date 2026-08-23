# pcbnew 9.0.2 Python (SWIG) Binding Defects — PCB-Build Crash Report

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Fable 5 (Anthropic) — diagnosis during the Jayne PCB rebuild, 2026-07-13
**License:** CC BY 4.0
**Status:** Worked around in `scripts/gen_Jayne_carrier_pcb.py`; upstream fix wanted.

This documents three distinct defects in the **pcbnew Python (SWIG) bindings** that
crashed `gen_Jayne_carrier_pcb.py` while it rebuilt `Jayne.kicad_pcb` from the
schematic netlist (place real footprints + assign pad nets). All three are in the
Python wrapper layer, not in KiCad's C++ core or the board data — the same
operations succeed in the KiCad GUI. A researcher should be able to reproduce each
in isolation from the minimal cases below.

---

## 1. Environment

| Item | Value |
| --- | --- |
| OS | Parrot OS 7 (`Linux 7.0.9+parrot7-amd64`), Debian-derived |
| KiCad | `9.0.2+dfsg-1` (Debian package) |
| `pcbnew` Python | `pcbnew.Version()` → `9.0.2`, `GetBuildVersion()` → `9.0.2+dfsg-1` |
| Module path | `/usr/lib/python3/dist-packages/pcbnew.py` (system SWIG binding) |
| Python | CPython `3.13.5` |
| Packages | `kicad-footprints 9.0.2-1`, `kicad-symbols 9.0.2-1`, `kicad-libraries 9.0.2+dfsg-1` |

**Note on Python 3.13:** this KiCad 9.0.2 SWIG binding predates official CPython
3.13 support. Two of the three defects below are classic SWIG-on-newer-CPython
ownership/typemap regressions and may be specific to the 3.13 pairing. The
researcher should record whether they reproduce on the CPython version KiCad 9.0.2
was built/tested against (3.11/3.12).

---

## 2. Defect A — `FootprintLoad()` segfaults if called after `board.Remove()`

### Symptom
Calling `pcbnew.FootprintLoad(lib, name)` **after** any `board.Remove(footprint)`
on the loaded board segfaults the interpreter (`rc=139`), preceded by a flood of:

```
swig/python detected a memory leak of type 'FOOTPRINT *', no destructor found.
```

The identical `FootprintLoad(...)` call **succeeds** if made *before* the first
`board.Remove(...)`.

### Minimal reproduction
```python
import pcbnew
b = pcbnew.LoadBoard("board.kicad_pcb")

# WORKS before any Remove:
assert pcbnew.FootprintLoad(
    "/usr/share/kicad/footprints/Inductor_SMD.pretty", "L_Taiyo-Yuden_NR-20xx")

for f in list(b.GetFootprints()):
    b.Remove(f)                       # each Remove leaks a FOOTPRINT*

# SEGFAULT here (rc=139):
pcbnew.FootprintLoad(
    "/usr/share/kicad/footprints/Inductor_SMD.pretty", "L_Taiyo-Yuden_NR-20xx")
```

### Likely root cause
`BOARD.Remove()` is exposed to SWIG **without transferring C++ ownership back to
Python** (hence "no destructor found" — the wrapper knows it leaked but can't free
it). The subsequent `FootprintLoad` re-enters the IO/plugin manager while those
orphaned `FOOTPRINT*` wrappers are in an inconsistent GC state; the plugin's cache
or the SWIG director table is corrupted and dereferenced.

**Where to look:** the `%newobject` / ownership annotations on `BOARD::Remove`
(and `BOARD::Delete`) in the pcbnew SWIG interface (`pcbnew/python/swig/*.i`,
`board.i`), and the `PLUGIN`/`IO_MGR` (`FootprintLoad`) wrapper's interaction with
those orphaned objects.

### Workaround used
Resolve placement and call **every** `FootprintLoad` up front, before any
`board.Remove(...)`. See `gen_Jayne_carrier_pcb.py` `main()` ("load EVERY footprint
instance FIRST … then remove + add").

---

## 3. Defect B — `FOOTPRINT.Pads()` returns a non-iterable `SwigPyObject`

### Symptom
```python
for pad in footprint.Pads():
    ...
TypeError: 'SwigPyObject' object is not iterable
```
`Pads()` should return an iterable container of `PAD*` (it does in the GUI scripting
console and in earlier KiCad releases). Here it returns a bare, unwrapped
`SwigPyObject` with no Python iterator protocol and no element typemap.

### Minimal reproduction
```python
import pcbnew
f = pcbnew.FootprintLoad(
    "/usr/share/kicad/footprints/Resistor_SMD.pretty", "R_0402_1005Metric")
list(f.Pads())          # TypeError: 'SwigPyObject' object is not iterable
```

### Likely root cause
The `std::deque<PAD*>` (or `PADS`) return typemap for `FOOTPRINT::Pads()` is not
being applied in this build — the return degrades to an opaque `SwigPyObject`
instead of a wrapped, iterable sequence. Consistent with a container-typemap
(`%template`/`std_deque.i`) mismatch under CPython 3.13.

---

## 4. Defect C — `FOOTPRINT.FindPadByNumber()` returns an unwrapped `SwigPyObject`

### Symptom
```python
pad = footprint.FindPadByNumber("1")
pad.SetNet(net)
AttributeError: 'SwigPyObject' object has no attribute 'SetNet'
```
The returned object is a raw `SwigPyObject`, not a `pcbnew.PAD` proxy, so **none** of
the `PAD` methods are reachable. `pad is not None` still passes, so the failure only
surfaces at the first method call — easy to mistake for a logic error.

### Minimal reproduction
```python
import pcbnew
f = pcbnew.FootprintLoad(
    "/usr/share/kicad/footprints/Resistor_SMD.pretty", "R_0402_1005Metric")
type(f.FindPadByNumber("1"))     # <class 'SwigPyObject'>, not pcbnew.PAD
```

### Likely root cause
Same class of defect as B: the `PAD*` return of `FindPadByNumber` is not run through
the `PAD` out-typemap, so it is handed back as an untyped `SwigPyObject`. Because B
and C both involve `PAD*` results, a single typemap/`%template` regression for the
`PAD` type (and its containers) likely explains both.

**Where to look:** `PAD` class registration and the `PAD*` typemaps in the pcbnew
SWIG interface; whether `pad.i`/`footprint.i` are `%include`d/`%import`ed in the
right order for CPython 3.13; the generated `pcbnew.py` proxy for `PAD`.

---

## 5. Combined impact and the workaround shipped

Because A, B, and C make the ordinary "load footprint → add to board → set pad nets
→ save" pipeline unusable, `gen_Jayne_carrier_pcb.py` uses a **hybrid** approach:

1. **pcbnew (only the working calls):** `LoadBoard`, `FootprintLoad` (all up-front,
   Defect A), `board.Add`, `SetPosition`, `SetOrientationDegrees`,
   `SetLayerAndFlip`, `SaveBoard`. No pad access.
2. **Text post-pass** (`inject_pad_nets`): re-reads the saved `.kicad_pcb`,
   rebuilds the `(net …)` table from the schematic netlist, and writes
   `(net <code> "<name>")` into every pad's s-expression by `(reference, pad#)` —
   bypassing the broken `PAD` wrapper entirely.

A secondary quirk that forced step 2 to own the whole net table: **`SaveBoard()`
prunes every net that has zero pads at save time.** Since the pcbnew phase adds
`NETINFO_ITEM`s but cannot attach them to pads (Defect C), all of them were pruned
on save, so the text pass must regenerate the full net table, not merely reference
the saved one.

## 6. Suggested verification for a fix

- Re-run the three minimal reproductions above; each should return a proper
  `pcbnew.PAD`/iterable and `FootprintLoad` should survive a prior `Remove`.
- Regression-test on the CPython version KiCad 9.0.2 targets vs 3.13 to localize
  whether this is a 3.13 typemap regression or a Debian `+dfsg` packaging artifact.
- End-to-end: delete the `inject_pad_nets` text pass in `gen_Jayne_carrier_pcb.py`,
  restore the native `pad.SetNet(...)` loop, and confirm a DRC-parity-clean board.

> *"She's a good gun." — but the sights need adjusting.*
