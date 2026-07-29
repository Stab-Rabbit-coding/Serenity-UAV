# Upstream submission package — kicad-cli `sch erc` SIGSEGV

Everything needed to file this with the KiCad project after the session that
found it. Full engineering analysis is in
[`../KICAD_CLI_ERC_SEGFAULT_BUG.md`](../KICAD_CLI_ERC_SEGFAULT_BUG.md); this file
is the **paste-ready issue text plus the pre-flight checklist**.

- **Tracker:** <https://gitlab.com/kicad/code/kicad/-/issues>
  (KiCad uses GitLab, not GitHub. A GitLab account is required.)
- **Choose the "Bug Report" issue template** — it asks for the version block,
  which is pre-filled in §3 below.

---

## 1. Before you submit — do these first

| # | Task | Why it matters |
| --- | --- | --- |
| 1 | Install `gdb` and `systemd-coredump` | A backtrace is the single most useful thing you can add; without it a triager has to reproduce from scratch |
| 2 | Capture the backtrace (§2) | Pinpoints the faulting frame |
| 3 | Re-test on the newest KiCad you can reach | 9.0.2 is what is pinned here (built May 2025). **If it is already fixed upstream, do not file.** |
| 4 | Search the tracker for an existing report | Keywords: `erc segfault lib_id`, `lib_symbols crash`, `SCH_SYMBOL UpdatePins null` |
| 5 | Attach the reproducers | Zip this directory; rename the two `.crashes` files back to `.kicad_sch` first (see §4) |

### Tool install

```sh
sudo apt install gdb systemd-coredump
```

`systemd-coredump` is optional but convenient — it captures the core
automatically so you can inspect it after the fact with
`coredumpctl gdb kicad-cli`. `gdb` alone is sufficient for §2.

**Debug symbols will make the backtrace far more useful.** Debian ships them via
the debug-symbol archive:

```sh
# add the debug repo (once)
sudo apt install debian-goodies    # provides find-dbgsym-packages
sudo find-dbgsym-packages $(which kicad-cli)
# then install whatever it names, typically:
sudo apt install kicad-dbgsym libkicad-dbgsym
```

If `kicad-dbgsym` is unavailable for this Parrot/Debian mix, say so in the issue
— a symbol-less backtrace with the right frame addresses is still worth
attaching, and triagers can map it against their own build.

---

## 2. Capturing the backtrace

Run from **this directory** after installing `gdb`:

```sh
# materialise the crashing variant under its real extension
cp D_absent_2pins.kicad_sch.crashes /tmp/D_absent_2pins.kicad_sch

gdb -q -batch \
    -ex run \
    -ex "bt full" \
    -ex "info registers" \
    --args kicad-cli sch erc -o /tmp/out.json --format json \
           /tmp/D_absent_2pins.kicad_sch \
    2>&1 | tee backtrace.txt
```

Paste `backtrace.txt` into the issue inside a fenced code block. If it is longer
than ~100 lines, attach it as a file and paste only the first 30 frames inline.

With `systemd-coredump` installed you can instead just run the crash and then:

```sh
coredumpctl gdb kicad-cli      # then: bt full
```

---

## 3. Paste-ready issue text

> Copy everything between the rules into the GitLab issue body. Replace the
> `PASTE BACKTRACE HERE` block with §2's output, and update the version block if
> you retest on a newer build.

---

#### Title

`kicad-cli sch erc: SIGSEGV with empty output when a symbol instance has pins but its lib_id is absent from lib_symbols`

#### Description

`kicad-cli sch erc` segfaults (SIGSEGV, shell exit 139) producing **completely
empty stdout and stderr** when a schematic contains a `(symbol (lib_id "X") …)`
instance that carries `(pin …)` child entries while `X` has no matching entry in
the file's `lib_symbols` block.

The crash occurs before the first ERC check line is printed, so there is no
indication of which symbol is responsible. Diagnosing it in a real 3800-line
schematic required bisecting the file by truncating at successive top-level
object boundaries and re-running ERC until the crash disappeared.

#### Steps to reproduce

1. Save the minimal schematic below as `crash.kicad_sch`.
2. Run `kicad-cli sch erc -o out.json --format json crash.kicad_sch`
3. Observe exit code 139 and no output.

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

#### Expected behaviour

An `lib_symbol_issues` ERC violation naming the unresolvable reference
designator, and a normal exit — which is exactly what already happens when the
same dangling `lib_id` appears **without** instance `(pin …)` entries.

#### Actual behaviour

SIGSEGV, exit 139, no stdout, no stderr, no ERC report written.

#### Isolation — both conditions are required

Five variants differing only in whether the library symbol is defined and
whether the instance carries `(pin …)` children:

| # | `lib_symbols` entry | instance `(pin …)` refs | `sch erc` |
| --- | --- | --- | --- |
| A | absent | none | exit 0 |
| B | present | none | exit 0 |
| C | **absent** | **1** | **exit 139 SIGSEGV** |
| D | **absent** | **2** | **exit 139 SIGSEGV** |
| E | present (declares pin `1` only) | `1` and `2` | exit 0 |

Variant **A** shows a dangling `lib_id` alone is survivable, so this is not
simply "symbol not found". Variant **E** shows an instance pin that cannot be
matched against a *present* library symbol is also survivable. The crash needs
the instance to hold pin references **and** the library symbol to be entirely
absent. One instance pin is sufficient.

#### Scope — only `sch erc` is affected

Against the identical input file:

| Command | Exit |
| --- | --- |
| `kicad-cli sch erc` | **139 (SIGSEGV)** |
| `kicad-cli sch export netlist` | 0 |
| `kicad-cli sch export bom` | 0 |
| `kicad-cli sch export pdf` | 0 |
| `kicad-cli sch export svg` | 0 |

Because the export paths all succeed, a generator script can produce and consume
a schematic that ERC cannot open. That is how this went unnoticed in our
repository for an extended period.

#### Backtrace

```text
PASTE BACKTRACE HERE
```

#### Speculation on root cause (unverified — a starting point only)

On load, each `SCH_SYMBOL` instance is bound to its `LIB_SYMBOL` and the
instance's `(pin …)` entries are reconciled against the library symbol's pin list
to build the `SCH_PIN` objects connectivity and ERC operate on. When the `lib_id`
resolves to nothing, that reconciliation may dereference a null `LIB_SYMBOL` (or
index an empty pin vector) while walking the instance pin list. The export paths
likely survive because they do not need that `SCH_PIN` set.

Possibly relevant: `SCH_SYMBOL::UpdatePins()`, the binding performed after
`SCH_IO_KICAD_SEXPR_PARSER::parseSchematicSymbol()` handles the `pin` token, and
the null-guard on `m_part` before the instance pin list is walked.

#### Version

```text
Application: kicad-cli x86_64 on x86_64

Version: 9.0.2+dfsg-1, release build

Libraries:
    wxWidgets 3.2.8
    FreeType 2.13.3
    HarfBuzz 10.2.0
    FontConfig 2.15.0
    libcurl/8.14.1 OpenSSL/3.5.6 zlib/1.3.1 brotli/1.1.0 zstd/1.5.7 libidn2/2.3.8 libpsl/0.21.2 libssh2/1.11.1 nghttp2/1.64.0 nghttp3/1.8.0 librtmp/2.3 OpenLDAP/2.6.10

Platform: Parrot Security 7.3 (echo), 64 bit, Little endian, wxBase, mate, x11

Build Info:
    Date: May 10 2025 09:34:36
    wxWidgets: 3.2.8 (wchar_t,wx containers) GTK+ 0.0
    Boost: 1.83.0
    OCC: 7.8.1
    Curl: 8.13.0
    ngspice: 44.2
    Compiler: GCC 14.2.0 with C++ ABI 1019
    KICAD_IPC_API=ON

Locale:
    Lang: en_US
```

*(Obtained with `kicad-cli version --format about`. Debian package
`9.0.2+dfsg-1`; `kicad-symbols 9.0.2-1`, `kicad-footprints 9.0.2-1`,
`kicad-libraries 9.0.2+dfsg-1`, `kicad-templates 9.0.0-1`.)*

---

## 4. Preparing the attachment

The two crashing variants are stored here as `*.kicad_sch.crashes` because this
repository's pre-commit guard rejects any `.kicad_sch` that `kicad-cli` cannot
load. Rename them back before zipping for upload:

```sh
mkdir -p /tmp/kicad-erc-repro && cp -r . /tmp/kicad-erc-repro/
cd /tmp/kicad-erc-repro
mv C_absent_1pin.kicad_sch.crashes  C_absent_1pin.kicad_sch
mv D_absent_2pins.kicad_sch.crashes D_absent_2pins.kicad_sch
rm -f UPSTREAM_SUBMISSION.md          # internal checklist, not for upstream
zip -r ~/kicad-erc-segfault-repro.zip .
```

Then attach `~/kicad-erc-segfault-repro.zip` to the issue.

---

## 5. If it turns out to be already fixed

Record that outcome in `../KICAD_CLI_ERC_SEGFAULT_BUG.md` (§Status) with the
version that fixed it, and close out the `TODO.md` item — the workaround note in
`Wash.md` should then say "fixed upstream in X.Y.Z" rather than implying it is
still live. Do not delete the reproduction set; it stays useful as a regression
check when this repo's KiCad is upgraded.

---

**Author:** Claude (Opus 5), 2026-07-28. License: CC BY 4.0.
