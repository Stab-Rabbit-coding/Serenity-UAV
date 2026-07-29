# kicad-cli `sch erc` SIGSEGV — reproduction set

Five minimal schematics that isolate the KiCad 9.0.2 crash written up in
[`../KICAD_CLI_ERC_SEGFAULT_BUG.md`](../KICAD_CLI_ERC_SEGFAULT_BUG.md).

Run `./run_repro.sh` to exercise all five against the installed `kicad-cli`.

| File | `lib_symbols` entry | instance `(pin …)` refs | Expected on 9.0.2 |
| --- | --- | --- | --- |
| `A_absent_0pins.kicad_sch` | absent | none | exit 0 (control) |
| `B_present_0pins.kicad_sch` | present | none | exit 0 (control) |
| `C_absent_1pin.kicad_sch.crashes` | absent | 1 | **exit 139 SIGSEGV** |
| `D_absent_2pins.kicad_sch.crashes` | absent | 2 | **exit 139 SIGSEGV** |
| `E_present_extra_pin.kicad_sch` | present (pin `1`) | `1`, `2` | exit 0 |

The two controls matter: **A** shows a dangling `lib_id` alone is survivable,
and **E** shows an unmatched instance pin against a *present* symbol is also
survivable. The crash needs both conditions together — instance pin references
**and** a wholly absent library symbol.

A fixed build should raise an `lib_symbol_issues`-class ERC violation for C and
D rather than crashing, and must leave A, B and E at exit 0.

**Why C and D carry a `.crashes` suffix:** this repository has a pre-commit guard
that rejects any `.kicad_sch` / `.kicad_pcb` file `kicad-cli` cannot load, to
catch real design-file corruption. These two are deliberately unloadable and
would trip it on every commit, so they are stored with a neutral extension;
`run_repro.sh` copies them to a temp directory under the proper name before
running, so the reproduction is unaffected.

**Author:** Claude (Opus 5), 2026-07-28. License: CC BY 4.0.
