# kicad-cli 9.0.2 — `sch erc` SIGSEGV on an unresolvable `lib_id`

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**AI-assist:** Claude Opus 5 (Anthropic) — isolation and minimal reproduction during
the Wash schematic-first rebuild, 2026-07-28
**License:** CC BY 4.0
**Status:** Root cause understood and worked around in this repo; upstream fix wanted.

`kicad-cli sch erc` **segfaults (SIGSEGV, shell exit 139) with no output at
all** when a
schematic contains a `(symbol (lib_id "X") …)` instance that carries `(pin …)`
child
entries while `X` has **no matching entry in the file's `lib_symbols` block**.

The crash happens *before the first ERC check prints*, so the operator gets a
silent
death with an empty stdout/stderr and no indication of which symbol is at fault.
Every
other `kicad-cli sch` subcommand parses the identical file without complaint.

---

## 1. Environment

| Item | Value |
| --- | --- |
| OS | Parrot Security 7.3 (`Linux 7.0.13+parrot7-amd64`), Debian-derived |
| KiCad | `9.0.2+dfsg-1` (Debian package) |
| `kicad-cli --version` | `9.0.2` |
| Symbols / footprints | `kicad-symbols 9.0.2-1`, `kicad-footprints 9.0.2-1` |
| Libraries | `kicad-libraries 9.0.2+dfsg-1` |
| Templates | `kicad-templates 9.0.0-1` |
| Schematic format | `(kicad_sch (version 20240101) …)` |

`gdb` and `coredumpctl` are not installed on this host, so **no backtrace is
included**.
A researcher with a debug build should be able to get one immediately from §3.

---

## 2. Impact — only `sch erc` dies

Run against the **same** input file (`missing_with_pins.kicad_sch`, §3):

| Command | Exit |
| --- | --- |
| `kicad-cli sch erc` | **139 (SIGSEGV)** |
| `kicad-cli sch export netlist` | 0 |
| `kicad-cli sch export bom` | 0 |
| `kicad-cli sch export pdf` | 0 |
| `kicad-cli sch export svg` | 0 |

Because the four export paths succeed, a generator script can happily produce
and
consume a schematic that ERC cannot open — which is exactly how this went
unnoticed in
our repository for an extended period.

---

## 3. Minimal reproduction

`missing_with_pins.kicad_sch` — an otherwise valid, minimal schematic. Note the
**empty `lib_symbols` block** and the two `(pin …)` entries on the instance:

```text
(kicad_sch (version 20240101) (generator eeschema)
  (uuid "e2000000-0000-0000-0000-000000000001")
  (paper "A4")
  (lib_symbols
  )
  (symbol (lib_id "S_MISSING") (at 50.80 50.80 0) (unit 1)
    (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no)
    (uuid "e2000000-0000-0000-0000-000000000002")
    (property "Reference" "U1" (at 50.80 45.72 0) (effects (font (size 1.27 1.27))))
    (property "Value" "MISSING" (at 50.80 55.88 0) (effects (font (size 1.27 1.27))))
    (pin "1" (uuid "e2000000-0000-0000-0000-000000000003"))
    (pin "2" (uuid "e2000000-0000-0000-0000-000000000004"))
  )
  (sheet_instances (path "/" (page "1")))
)
```

```console
$ kicad-cli sch erc -o out.json --format json missing_with_pins.kicad_sch
$ echo $?
139
```

No stdout, no stderr, no partial ERC report. Compare a healthy run, which prints
`Checking sheet names…` and fourteen further check lines before its verdict.

---

## 4. Isolating the trigger

Five variants, differing only in whether the library symbol is defined and
whether the instance carries `(pin …)` children. **Both conditions are
required**, and a single instance pin is sufficient:

| # | `lib_symbols` entry | instance `(pin …)` refs | `sch erc` |
| --- | --- | --- | --- |
| A | absent | none | exit 0 — handled gracefully |
| B | present | none | exit 0 |
| C | **absent** | **1** | **exit 139 (SIGSEGV)** |
| D | **absent** | **2** | **exit 139 (SIGSEGV)** |
| E | present (declares pin `1` only) | `1` and `2` | exit 0 |

Variant **A** is the important control: a dangling `lib_id` on its own is
survivable, so
the fault is not simply "symbol not found". Variant **E** is the other important
control:
an instance pin that cannot be matched against a *present* library symbol is
also
survivable. The crash needs the instance to hold pin references **and** the
library
symbol to be entirely absent.

---

## 5. Likely root cause

On load, each `SCH_SYMBOL` instance is bound to its `LIB_SYMBOL`, and the
instance's
`(pin …)` entries — which exist to carry per-pin UUIDs and alternate-function
assignments — are reconciled against the library symbol's pin list to build the
`SCH_PIN` objects that connectivity and ERC operate on.

When the `lib_id` resolves to nothing, that reconciliation appears to
dereference a null
`LIB_SYMBOL` (or index an empty pin vector) while walking the instance pin list.
The
export paths survive because they either skip the unresolved symbol or do not
need the
`SCH_PIN` set that ERC's connectivity graph requires.

**Where to look:** `SCH_SYMBOL::UpdatePins()` and the `SCH_SYMBOL` ↔
`LIB_SYMBOL` binding performed after
`SCH_IO_KICAD_SEXPR_PARSER::parseSchematicSymbol()` handles the `pin` token —
specifically the null-guard on `m_part` before the instance pin list is walked.
The connectivity build (`CONNECTION_GRAPH::Recalculate`) invoked by the ERC
entry point is the first consumer that requires those `SCH_PIN`s.

---

## 6. Suggested fix

1. Null-guard the library-symbol dereference on the instance-pin
   reconciliation path.
2. Prefer a **graceful diagnostic** over a silent crash: KiCad already has an
   `lib_symbol_issues` ERC rule for exactly this class of problem — an instance
   whose `lib_id` cannot be resolved should raise that violation and continue,
   matching how variant **A** already behaves today.
3. At minimum, `kicad-cli` should exit non-zero *with a message naming the
   offending reference designator* rather than dying with empty output.

## 7. Reproduction set in this repository

`kicad_cli_erc_segfault_repro/` holds all five variants plus `run_repro.sh`,
which exercises them against the installed `kicad-cli`. Variants C and D are
stored with a `.crashes` suffix because this repository's pre-commit guard
rejects any `.kicad_sch` that `kicad-cli` cannot load; the script copies them to
a temp directory under the proper extension before running.

## 8. Verification for a fix

- Variants **C** and **D** in §4 must complete and report an
  `lib_symbol_issues`-class violation instead of crashing.
- Variants **A**, **B**, **E** must stay at exit 0 (no regression).
- The four export subcommands in §2 must stay at exit 0.

---

## 9. How this surfaced here

`avionics/kicad/Wash/kicads/Wash.kicad_sch` (the pre-rebuild, hand-authored
file, now under `archives/avionics-archives/kicad-archives/`) referenced two
generic passive symbols, `C_SMD` and `R`, that had never been added to its
`lib_symbols` block, while ten instances carried `(pin …)` entries. Once an
unrelated S-expression repair let KiCad parse the whole file for the first
time, `kicad-cli sch erc` began segfaulting with no output.

Diagnosis required bisecting the schematic by truncating it at successive
top-level
object boundaries and re-running ERC until the crash disappeared — which is
precisely
the debugging cost that the silent, message-free exit imposes. Adding the two
missing
`lib_symbols` definitions resolved it; the file has since been superseded by the
generated `Wash.kicad_sch`.

> *"Curse your sudden but inevitable betrayal."*
