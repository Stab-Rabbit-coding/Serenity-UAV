# Serenity UAV — Documentation, Standards & Regulatory Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY-SA 4.0 — creativecommons.org/licenses/by-sa/4.0
**Current design revision:** Rev T (2026-09-06)

> **Detail-holder for the root WBS.** The repository-root [`TODO.md`](../TODO.md)
> is a compact index — headings, subheadings, and short (<=70-char) checkbox items
> only, per root `AGENTS.md`. This file carries the full task detail for the WBS
> branches root indexes below. Close an item here first, then check it off in the
> root index as a commit prerequisite (root `AGENTS.md` "Revisions and Version
> Control"). **&#9733; = the branch is on the critical path to first flight (Phase 5).**

*"A special hell. — Shepherd Book"*

---

## Owned WBS branches — open-item summary

| Master § | Branch | Open | First flight |
|----------|--------|-----:|:------------:|
| §0.5 | 0.5 — Citation Completeness Audit (All Source Files) | 3 | — |
| §0.1 | 0.1 — FCC Part 95 Section-Number Verification | 0 | — |
| §0.7 | 0.7 — CI Lint Scope and Repo-Wide Lint Debt | 0 | — |
| §0.8 | 0.8 — Tilt-Spar Material Allowables + Hall Encoder | 3 | — |
| §0.9 | 0.9 — Licensing Updates | 1 | — |
| §0.10 | 0.10 — Update and Correct Documentation Touching Every Non-Archived File | 6 | — |
| §1.5 | 1.5 — Documentation | 3 | — |
| §1.6 | 1.6 — Rev Q: Repo-Wide Architecture Propagation | 0 | — |
| §1.7 | 1.7 — Rev R: Component Rev Sync + s_ Prefix Removal | 0 | — |
| §5.1 | 5.1 — FCC (external radio systems) | 1 | — |
| §5.2 | 5.2 — FAA (airworthiness and operations) | 6 | &#9733; |
| §5.3 | 5.3 — Industry Standards Compliance | 3 | — |
| §6.1 | 6.1 — Branch Reconciliation / Pre-Flight Compliance | 1 | &#9733; |
| §6.2 | 6.2 — STL Mesh Repair | 0 | — |
| §6.3 | 6.3 — Rev S Checkpoint | 0 | — |
| §6.4 | 6.4 — Rev T Checkpoint | 0 | — |
| | **Total open (this subsystem)** | **27** | |

---


## §0.5 — Citation Completeness Audit (All Source Files)

*(root `WBS.md` §0.5)*

    - [ ] `build_guide_18_first_flight.svg`'s Part 107/VLOS warning callouts (lines ~59–60)
    need citations but their fixed-width boxes are already near-full; requires either a
    layout change or rendering verification (see `/verify` skill) before editing text length.
    - [ ] Seven additional SVGs (`build_guide_09_avionics.svg`, `build_guide_11_inter_board.svg`,
    `build_guide_12_security_hw.svg`, `build_guide_20_node_placement.svg`,
    `build_guide_21_node_install.svg`, `build_plan.svg`, `components_overview.svg`) are
    built entirely or partly around the **archived** Cape-A-1/Cape-B-1 hardware instead of
    the Rev R1 baseline (all 8 nodes now carry Pilot/Cape-A-2 + XO/Cape-B-2 per CLAUDE.md).
    This is a content-currency problem independent of citations — needs a dedicated pass
    (likely a content rewrite, not a text-substitution fix) with visual verification.
    **Superseded by, and folded into, the "Rebuild `graphical-build-guide/`..." item in
    §1.5 Documentation** — that item replaces these cards' art wholesale rather than
    patching the hardware depiction in place.
    - [ ] The remaining ~30 non-priority SVGs were not individually swept for citations in
    this pass (only spot-checked); a full sweep with rendering verification is still open.
    **Partial progress 2026-06-29:** `build_guide_17_ground_test.svg` line 45 updated —
    appended `[REF-FCC-003]` to the "49MHz Part 15 §15.235 ground transmitter" text (text
    length verified safe vs. containing `<rect>` bounds before editing).
    `build_guide_18_first_flight.svg` Part 107/VLOS callout boxes remain at overflow; still
    requires layout change or rendering verification before citation text can be added.


## §0.1 — FCC Part 95 Section-Number Verification

*(root `WBS.md` §0.1)*

- [x] **Code-identifier "RCRS" naming renamed to "49MHZ_XCVR"/"XCVR-49MHZ"** *(done
    2026-07-18, user-approved naming — user explicitly specified the frequency-qualified
    form to avoid ambiguity with "Commo," the board that also carries LoRa)*. Every
    code-identifier/label use of "RCRS" as a naming convention (not a regulatory claim) was
    renamed; every legitimate regulatory-term use of "RCRS" (i.e. actually discussing 47 CFR
    Part 95 Subpart C, Radio Control Radio Service) was left untouched. Scope, beyond the
    four classes originally called out here:
    - Firmware: `SI5351_RCRS_*`/`si5351_set_rcrs_channel()`/`rcrs_channel_reg_t`/
      `s_rcrs_channels` → `SI5351_49MHZ_XCVR_*`/`si5351_set_49mhz_xcvr_channel()`/
      `xcvr_49mhz_channel_reg_t`/`s_xcvr_49mhz_channels` in
      `avionics/firmware/cn/src/si5351.{h,c}`, `xcvr_kiss.c`, `main.c`; `SKIPPER_RCRS_*` →
      `SKIPPER_49MHZ_XCVR_*` in `gcs/skipper/firmware/pb2i/src/skipper_config.h`.
    - KiCad: `UART_RCRS_TX`/`UART_RCRS_RX` → `UART_49MHZ_XCVR_TX`/`UART_49MHZ_XCVR_RX` in
      `avionics/kicad/add_sensors_sbus.py` and both `XO.kicad_sch`/`.kicad_pcb` and
      `Commo.kicad_sch`/`.kicad_pcb` (pure net-name text edits, occurrence counts verified
      1:1 before/after — no geometry, placement, or routing touched); `JST-GH-3P-RCRS` →
      `JST-GH-3P-XCVR-49MHZ`; the Commo board title comment dropped the redundant "RCRS".
      Also updated the two Commo migration scripts (`gen_commo_sch.py`, `mod_commo_pcb.py`) so
      a future re-run doesn't regress the renamed nets.
    - Docs: `RCRS-49`/`TVS-RCRS`/`FB-RCRS` → `XCVR-49MHZ`/`TVS-XCVR-49MHZ`/`FB-XCVR-49MHZ` in
      `Commo.md`/`XO.md`; same pattern in the active current-spec files
      (`current-specification/bom_revS.csv`, `serenity-rev-r.jsx` — excluding the one BOM row
      already self-labeled `ARCHIVED`, left as-is per the revision-archival policy) and
      `docs/PHASED_BUILD_GUIDE.md`.
    - Also found and fixed while auditing: two DTS pinctrl labels
      (`skipper_rcrs_uart_pins` → `skipper_xcvr_49mhz_uart_pins`), a `skipper_config.yaml`
      config key (`rcrs:` → `xcvr_49mhz:`, unused by any code yet), SCAD comment prose in
      `rcrs49_wire_post.scad`/`middle_canonical_shell24.scad`/`head_shell24.scad` (filenames
      left as-is — a physical-file rename is a separate, larger task), and a **stale/incorrect
      citation** in `avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`
      reference [4] that still cited "47 CFR Part 95 ... RCRS 49 MHz channel plan" — the exact
      claim REF-FCC-003 documents as superseded everywhere else; corrected to cite Part 15
      §15.235 per REF-FCC-003. Same stale-citation pattern found and fixed in
      `current-specification/serenity-rev-r.jsx`'s compliance table (`47 CFR 95.623`/
      `47 CFR 95.655` → §15.235, with the corrected ≈30 µW / −15.2 dBm field-strength-derived
      figure from REF-FCC-003 in place of the old 100 mW ERP figure).
    - **Not touched:** `avionics/rev-s1/WBS.md`'s dated `[x] DONE 2026-07-04` historical log
      entries (describe net names as they existed at that time — historical record, not live
      documentation); root `TODO.md`/`WBS.md` historical entries; `docs/bom_revP/Q/R.json`
      (already-archived historical BOM snapshots that self-document the same Part 95
      correction via `~~strikethrough~~` — rewriting them would erase that record); Gerber
      files under `avionics/kicad/XO/gerbers/` (fab output regenerated from source — net-name
      text embedded in them is informational only and doesn't affect the physical board;
      regenerate before sending to fab).
    - **ERC/DRC could not be re-verified in this environment**: `tools/validate_kicad.py`
      requires KiCad ≥8 (`kicad-cli sch erc`/`pcb drc` subcommands); only KiCad 7.0.11 was
      installable here (the KiCad 9 PPA and kicad.org direct downloads are both blocked by
      this environment's network policy). The rename is a pure net-name text substitution
      with verified matching occurrence counts, so it should not introduce new ERC/DRC
      violations, but CI (which provisions KiCad 9 as `ci.yml`/`tools/validate_kicad.py`
      require) must confirm before merge.


## §0.7 — CI Lint Scope and Repo-Wide Lint Debt

*(root `WBS.md` §0.7)*

- [x] **Repo-wide lint debt — remediation pass complete 2026-07-18** (file type by file
    type, per this item's own guidance, against the counts observed as of the PR #107
    full-codebase run: `EDITORCONFIG` 697, `PYTHON_BLACK` 72, `PYTHON_FLAKE8` 56,
    `PYTHON_ISORT` 47, `JSCPD` 39, `MARKDOWN` 32, `CLANG_FORMAT` 26, `CPP` 25,
    `PYTHON_MYPY` 7, `NATURAL_LANGUAGE` 17, `JAVASCRIPT_STANDARD` 5, `SHELL_SHFMT` 4,
    `CSS` 3, `PYTHON_PYLINT` 2, `JSX` 6, `JSON` 1, `GITHUB_ACTIONS` 1). Scope throughout:
    active files only, excluding `archives/`, `airframe/archive/`,
    `airframe/FreeCAD-scripts/` (already excluded from lint scope by `.super-lintignore`)
    and the vendored `node_modules/autopreview/` package.
    - **Fixed outright:**
      - `PYTHON_BLACK` — `black` reformatted 63 active files; `PYTHON_FLAKE8` was already
        0 (separately gated by `ci.yml`) and stayed 0 throughout.
      - `PYTHON_ISORT` — `isort --profile black` reordered imports in 11 files.
      - `PYTHON_MYPY` — 2 real findings fixed: a same-name function redefinition in
        `airframe/stls/fuselage/cargo/generate_cargo_doors.py` (renamed the early-return
        fallback closure `belly_z` → `belly_z_fallback`) and a confusing except-variable
        reuse in `generate_cargo_mounts.py` (renamed the loop variable `exc` → `err`). The
        3 remaining "missing yaml stubs" findings on the Skipper tracking scripts were a
        missing dev-tool dependency, not a code issue — installed `types-PyYAML`.
      - `PYTHON_PYLINT` (E/F classes only) — 5 real findings, all the same root cause:
        this dev sandbox's KiCad 7.0.11 `pcbnew` Python bindings don't have the KiCad 9
        per-layer `PCB_VIA.SetWidth(layer, width)` / enum-based `FOOTPRINT.Flip()` APIs
        the code is deliberately written against (project's actual target is KiCad 9, per
        `ci.yml`/`tools/validate_kicad.py`) — scoped `# pylint: disable=...` comments
        added with the version-mismatch explanation, not code rewrites, since the code is
        correct for the real target. One further pylint tuple-unpacking false positive
        (`mod_vera_ds_pcb.py`/`mod_Observer_ds_pcb.py`, `padnets.items()` mis-inferred as
        `float`/`str`) got the same treatment.
      - `CLANG_FORMAT` — root-caused via the PR #140 CI run: `clang-format -i` (repo's
        own `.clang-format`) locally against clang-format 18.1.3 left 7 lines across 7
        files still flagged by CI's actual gate. Root cause was **not** a stray edge
        case — the `github/super-linter@v4` image bundles some old, uncontrolled
        clang-format build, and cross-checking clang-format 9 through 22 (via `pip
        install clang-format==<ver>`) found `PointerAlignment: Left` changed meaning
        between clang-format 18 and 22 (star-attached-to-identifier vs.
        star-attached-to-type) — silently disagreeing with whatever CI actually runs.
        Fixed at the root: `.clang-format` now pins `PointerAlignment: Right` (verified
        byte-identical output across clang-format 18 and 22, and matches this codebase's
        actual established style everywhere — `char *foo`, not `char* foo`), **and**
        `ci.yml` gained a dedicated "C/C++ format" job that installs
        `clang-format==22.1.8` (pinned in `requirements-dev.txt`, the current latest
        stable LLVM release) and runs the authoritative check directly — the same
        version a local dev installs from `requirements-dev.txt`. `VALIDATE_CLANG_FORMAT`
        is now `false` in `super-linter.yml` (duplicate check against an uncontrolled,
        disagreeing version) with the rationale recorded there and in `.clang-format`.
        Re-ran `clang-format -i` under the pinned 22.1.8 across all 27 active files;
        `gcc -fsyntax-only` and the existing test suites re-verified clean.
      - `CPP` (cpplint) — root-caused via two successive CI runs (the first fix pass
        only addressed `legal/copyright`, having mis-scoped the CI log grep; the
        re-run's failure revealed the rest). Full breakdown across the 27 active
        firmware files: `legal/copyright` 25, `build/header_guard` 26,
        `build/include_subdir` 18, `runtime/int` 17, `build/include_order` 12,
        `whitespace/parens` 1, `readability/multiline_comment` 1.
        - `legal/copyright` — added a `Copyright 2026 Steve Griffing` line to each
          affected file's existing `Author:`/`License:` header block — additive,
          doesn't remove or contradict the project's CC BY 4.0 attribution convention.
        - `whitespace/parens` + `readability/multiline_comment` (both on the same line,
          `bmon_ina2xx.c`) — a Doxygen comment wrapped across 2 lines because the
          single-line form was 86 columns; cpplint's parens check misfired on the
          wrapped, non-ASCII (µ) continuation. Reflowed the comment text to fit under
          80 columns on one line, resolving both.
        - `build/header_guard`, `build/include_subdir`, `build/include_order`,
          `runtime/int` — added `CPPLINT.cfg` (cpplint's own, auto-discovered config
          mechanism) filtering these 4 categories, each because cpplint is enforcing
          Google **C++** Style Guide conventions this **C** codebase never followed and
          in some cases structurally cannot follow: short symbol-only header guards
          (`SI5351_H`) used consistently repo-wide; peer headers included by bare
          filename (matches the CMake include-path setup, not a subdirectory layout);
          `main.c` files that are leaf entry points with no matching `main.h`, which
          cpplint's "primary header" heuristic doesn't account for; and `long` used
          exclusively as `strtol()`/`strtoul()`'s own standard C return type. Full
          rationale recorded in `CPPLINT.cfg` itself. `readability/casting` (20 hits on
          the first-ever cpplint pass, for this codebase's C-style casts) turned out to
          no longer fire after the `clang-format 22` reformatting pass — verified
          empirically, not filtered, since the exact mechanism is cpplint's own
          cast-detection heuristic rather than a code change on this project's part.
        `cpplint` confirms 0 findings across the full 27-file set now.
      - `JSCPD` — root-caused via the same CI run: super-linter runs jscpd **per file**
        (self-comparison within one file), not the repo-wide cross-file scan used to
        produce the earlier 142-clone estimate below. Only 3 files had real *internal*
        duplication: `blender_edf_bore_and_petals.py` (two mesh-builder functions ending
        in the same 6-line "bake bmesh → new object" sequence — extracted into
        `finalize_bmesh_to_object()`), `tracker.py` (the haversine horizontal-distance
        calculation duplicated between `_slant_range_m()` and `_elevation_deg()` —
        extracted into `_haversine_horizontal_m()`, `pytest tests/test_tracker.py`
        still 11/11 passing), and `gen_hull_outlines.py` (`build_top_view()` /
        `build_bottom_view()` sharing the same range/canvas-size boilerplate —
        extracted into `top_bottom_view_geometry()`). All three verified 0 clones after
        the fix.
      - `GITHUB_ACTIONS` — `actionlint` flagged `actions/setup-python@v4` as outdated in
        `ci.yml`; bumped to `@v5`.
      - `SHELL_SHFMT` — `shfmt -i 4` on the 4 active `.sh` scripts; `bash -n` verified.
      - `JSON` — `previewConfig.json` was a committed 0-byte (invalid-JSON) file; no
        schema for it is documented anywhere in the repo, so rather than invent one, set
        it to `{}` — the minimal valid, behavior-neutral fix.
    - **Investigated, not applicable:**
      - `CSS` — the only `*.css` files in the repo are under `archives/` (frozen) or the
        vendored `node_modules/autopreview/` package; nothing in active scope.
    - **Investigated, intentionally not changed (documented per this item's own "resolve
      or document" standard) — each would either destroy real content, fight an explicit
      project-wide rule, or require an architectural judgment call outside a lint pass:**
      - `EDITORCONFIG` — `editorconfig-checker` (installed fresh, no config existed) fires
        697+ (in fact 1.47M once the tracked `node_modules/` is included) hits dominated by
        false positives: it does naive line-by-line indentation checking with no
        understanding of Python triple-quoted docstrings, so any docstring using a 2-space
        nested-list convention for prose (this project's own established comment style,
        `AGENTS.md` §6 "verbose comments in each language's native style") reads as an
        indentation violation. `flake8`, which *does* understand Python syntax, already
        confirms 0 real code-indentation issues. This matches `super-linter.yml`'s own
        existing comment that `EDITORCONFIG` "require[s] upstream super-linter config
        tuning" before it can be safely re-enabled — confirmed, not fixed here.
      - `MARKDOWN` — no `.markdownlint.yml` exists in the repo; the default ruleset fires
        8,489 hits across 88 active `.md` files (vs. the historical 32), almost entirely
        `MD013`/`MD022`/`MD009`-class house-style opinions with no config filtering them
        down to whatever subset super-linter's own run used. `VALIDATE_MARKDOWN` is
        already `false` in `super-linter.yml` with the same "requires upstream config
        tuning" note. Needs a committed `.markdownlint.yml` (or equivalent) authored and
        reviewed before re-enabling — guessing at one to hit a specific historical count
        isn't a real fix.
      - `NATURAL_LANGUAGE` — super-linter's prose linter (textlint-based) has no readily
        available standalone equivalent in this environment; also already `false` in
        `super-linter.yml` for the same reason.
      - Beyond the 3 real per-file duplicates fixed above, a repo-wide cross-file jscpd
        scan (not what CI actually runs) also surfaces ~142 clones at a 10-line/
        50-token threshold. The overwhelming majority are either intentional structural
        repetition — SVG build-guide diagram templates sharing icon/shape markup by
        design, and BOM revision snapshots (`bom_revP/Q/R.json`) that are supposed to
        largely restate the prior revision plus incremental changes per the Rev-letter
        archival policy (`AGENTS.md` §8) — or independent per-board KiCad automation
        scripts (e.g. `mod_vera_ds_pcb.py` / `mod_Observer_ds_pcb.py`) that are
        deliberately self-contained so one board's generator can be modified without
        risking another's already-validated PCB. Real de-duplication candidates exist
        (that Vera/Observer script pair is the clearest one) but extracting shared code
        from working, physically-validated PCB-generation scripts is an architectural
        decision with real hardware consequences — needs explicit user review, not a
        mechanical lint fix, matching the same caution applied to the RCRS rename in
        §0.1 above.
      - `JAVASCRIPT_STANDARD` / `JSX` — the sole active file
        (`current-specification/serenity-rev-r.jsx`) would need 2-space indent and no
        semicolons under JavaScript Standard Style, which directly contradicts
        `AGENTS.md` §6's explicit, project-wide "4-space indent, every language, always"
        override. Not applying a linter's default style over an explicit project rule.


## §0.8 — Tilt-Spar Material Allowables + Hall Encoder Verification

*(root `WBS.md` §0.8)*

- [ ] **Verify `REF-STD-GEAR-001` (ISO 53:1998) to clause level.** Added
    2026-08-31 with the nacelle tilt ring gear (Rev T4,
    `airframe/openscad/nacelles/nacelle_trunnion.scad`). The designation, title,
    issuing body and the three basic-rack proportions used (α = 20°,
    h_a = 1.00·m, h_f = 1.25·m) are recorded; the **direct ISO catalogue URL and
    the clause number are NOT verified** and are deliberately not guessed. Fetch
    both from iso.org and complete the entry before the gear is released for
    fabrication. Same standard also underwrites the fuselage-end 38T/38T stage in
    `merge_cargo_interior.py`, so closing this closes both citation sites.

Opened 2026-07-19 alongside the docs/TILT_SPAR_ANALYSIS.md §3.5 material trade
study and the wing/nacelle Hall tilt-feedback sensor. Both carry
"requires-verification" entries in `REFERENCES.md`.

- [ ] **Verify spar material allowables vs MMPDS-2023 / AMS.** §3.5 uses typical
    handbook values for the selected **AISI 4130** and the two carried alternates
    **17-4 PH H1075** and **7075-T6** (plus 6061/316/Ti reference points). Confirm
    the procured temper's design allowable against MMPDS/AMS or a mill cert and
    add `REF-MAT-*` catalog entries with validated URLs before spar procurement.
- [ ] **Add the 4130 corrosion-finish spec.** The bare 4130 tube rusts at the
    bearing journals — specify zinc/cadmium plate (journals ground) on
    `SPAR-TILT-4130` in the BOM and the build guide, or adopt the plating-free
    17-4 PH alternative. (docs §3.5 / §9.)
- [ ] **Verify the MT6701 off-axis geometry + pinout.** Encoder selected =
    `SKIPPER-TILT-ENC-PCB` (Magntek MT6701, I²C, off-axis; MA732/SPI fallback). Confirm
    against the MT6701 datasheet: pinout/protocol, off-axis air-gap (assumed
    1.5 mm), ring OD/ID, IC radial offset (R = 12 mm), and ferrous-through-shaft
    behavior; add a `REF-SENSOR-*` entry with a validated URL before PCB/harness
    sign-off. Bench-cal tracked in `avionics/emi-hardening/WBS.md` §1.4.6 and
    `avionics/WBS.md` §1.9.1.


## §0.9 — Licensing Updates

*(root `WBS.md` §0.9)*

Opened 2026-08-01 as `TODO.md` §0.9. **Numbering note:** this file's own §0.6 was already
the distinct, completed "IEC 62368-1 PCB Layout Isolation Verification" item, so the
"Update and correct documentation" item that both root `WBS.md` and `TODO.md` had mislabeled
as (variously) §0.9 / §0.6 was renumbered to §0.10 in both files as part of this same pass,
to free §0.9 cleanly for this item. See root `WBS.md` §0.9/§0.10 for the renumbering note.

The project's original license statement (root `AGENTS.md` §3, `README.md`, `REFERENCES.md`)
said all work was CC BY 4.0, but root `LICENSE` and `avionics/LICENSE` already carried the
full CERN-OHL-W 2.0 text before this audit — a stale-documentation gap (root `AGENTS.md`
§11.4: "actual code/model state outranks stale documentation"). This item formalizes and
completes the dual-license split those two files already implied, corrects a real
misattribution (misubisu hull license), and closes out the remaining structural/documentation
gaps. Full policy: `docs/attribution_and_licensing.md` (new).

- [x] **Correct misubisu Thingiverse model [REF-CAD-004] license to CC-BY-SA 4.0.** The
    upstream Thingiverse listing for Thing 7330462 is CC BY-SA 4.0, not the "CC BY 4.0" (and,
    in one place, garbled "CC BY 4.0 SA") stated in four locations:
    `REFERENCES.md` REF-CAD-004, `current-specification/LICENSE_AND_ATTRIBUTION.md` §2,
    `README.md` Component License Map + Attribution quote, and
    `docs/references/thingverse-serenity/LICENSE.txt` (which also had a stray/wrong
    Thingiverse ID, 482910 instead of 7330462 — fixed in the same pass). Logged in
    `REFERENCES.md` "Removed / Superseded Citations."
- [x] **Integrate REF-CAD-002/003/004 as Available Components under CERN-OHL-W 2.0 with
    clean IP boundaries.** `docs/attribution_and_licensing.md` §3 classifies each of the
    three canonical airframe references explicitly: misubisu (REF-CAD-004, CC BY-SA 4.0) and
    the BamJr nozzle concept are **Available Components** (CERN-OHL-W 2.0 §1.6) — openly
    licensed geometry actually incorporated into the project's Covered Source, keeping its
    own upstream terms. Nick Henning (REF-CAD-002, permission-only) and the QMx blueprints
    (REF-CAD-003, copyrighted commercial product) are **reference-only** — outside the
    Covered Source boundary entirely, never redistributed or treated as components. Added
    `REFERENCES.md` Part XV (REF-LIC-001 CERN-OHL-W 2.0, REF-LIC-002 OSHWA certification)
    to catalog the license standards themselves, consistent with how every other standard in
    this project is cataloged.
- [x] **License wings, nacelles, landing gear, cargo system, and all other original airframe
    components under CERN-OHL-W.** Created `airframe/LICENSE` (full CERN-OHL-W 2.0 text with
    a scope header naming these components).
- [x] **License all avionics under CERN-OHL-W.** `avionics/LICENSE` already carried the full
    CERN-OHL-W 2.0 text (predates this audit); added the same scope-header treatment as
    `airframe/LICENSE` for consistency (naming Pilot/XO/FlightEngineer/Commo/Observer/CAN-PERIPH-GW-1).
- [x] **License all documentation, code, scripts, drawings, and other non-hardware items
    under CC-BY-SA.** Created `docs/LICENSE`, `tools/LICENSE`, `current-specification/LICENSE`,
    `graphical-build-guide/LICENSE` (pure CC BY-SA 4.0), plus mixed `gcs/LICENSE` and
    `deferred/LICENSE` (both licenses, since each folder genuinely contains both hardware and
    software/docs). Swept the `**License:** CC BY 4.0` header stamp to `CC BY-SA 4.0` across
    71 non-archived documentation files project-wide (`WBS.md`, `REFERENCES.md`, every
    subsystem `TODO.md`/`WBS.md`, `docs/*.md` analysis documents, KiCad companion `.md`
    files, etc. — header metadata line only; in-body citations of genuinely CC BY 4.0
    third-party sources, e.g. BamJr's nozzle, were left untouched). Also corrected
    `current-specification/LICENSE_AND_ATTRIBUTION.md`'s own top-level license section,
    "Original Creative Work Covered by This License" list (split into CERN-OHL-W vs
    CC BY-SA subsections), and "Suggested Full Attribution Block" example, which all still
    stated a single project-wide CC BY 4.0 license.
- [x] **Create License files for each subsystem folder with clear, unambiguous federation
    from root License and `docs/attribution_and_licensing.md`.** All seven subsystem folders
    (`airframe/`, `avionics/`, `docs/`, `gcs/`, `tools/`, `current-specification/`,
    `graphical-build-guide/`, `deferred/` — eight, `avionics/` already existed) now carry a
    `LICENSE` file with a short scope header plus the full applicable license text(s),
    self-contained per folder rather than a bare pointer. Header template documented in
    `docs/attribution_and_licensing.md` §4.
- [x] **Create all other supporting documents for OSHW certification.** Created
    `docs/OSHW_CERTIFICATION.md` — a readiness checklist against the verified OSHWA
    self-certification requirements [REF-LIC-002] (own contributions open-sourced,
    third-party components distinguished with accessible datasheets, necessary software
    OSI-approved). Flags two real gaps that block an actual submission today: the TI Z-Stack
    Zigbee dependency is not OSI-licensed (TI TSPA), and Phase 7 firmware source doesn't
    exist yet (only the architecture spec does). Certification submission itself requires the
    human maintainer to act — this repository can only prepare the documentation.
- [ ] **Submit OSHW self-certification (root `TODO.md` §5.4).** Requires the human maintainer
    (Steve Griffing) to submit the OSHWA Certification Mark License Agreement — no repo change
    can close this. Blocked on the two gaps above (Zigbee Z-Stack licensing, Phase 7 firmware
    source) being resolved first; see `docs/OSHW_CERTIFICATION.md`.
- [x] **Rename avionics boards to non-trademarked names — CLOSED 2026-08-01.**
    Wash, Zoë, Kaylee, Emma, Jayne, and Malcolm ("Mal") were the original Firefly-character
    board names in the authoritative root `AGENTS.md` §9 naming table (PACE failover roles,
    Firefly quotes, referenced across ~284 files: KiCad silkscreens/schematics/PCB/gerbers,
    firmware, every subsystem doc). Per root `AGENTS.md` §11.2, this was first raised with the
    user before any rename was attempted; the user's initial call was to leave it open. The
    user then supplied replacement role names directly (Malcolm/Mal→Skipper, Wash→Pilot,
    Zoë→XO, Kaylee→Flight Engineer, Emma→Commo, Jayne→Observer) and directed the full rename,
    including the physical KiCad project files/folders.
    - Physical renames: `git mv` for all 198 board-folder paths (schematics, PCBs, gerbers,
      scripts, companion `.md` docs) plus the 6 shared `Jayne_*.kicad_sym` symbol libraries
      (authored under Jayne, reused fleet-wide) → `Observer_*.kicad_sym`, with every
      referencing `sym-lib-table`/`fp-lib-table`/embedded `lib_symbols` updated to match.
      Also caught: a second, separate `avionics/kicad/gerbers/{CAPE-B-2-S1,Emma-S1,Kaylee-S1}/`
      gerber export set not inside the per-board folders, and 4 STL BOM placeholders
      (`Kaylee_PDB_*.stl`, `Malcolm_enclosure_*.stl`, `Malcolm_tripod_*.stl`, `text_kaylee.stl`).
    - Content sweep: ~5,800 substitutions across ~330 tracked text files, using word-boundary
      regex for the safe general case (`\bWash\b`, `\bMAL\b`, etc.) plus a small set of
      hand-verified literal-substring rules for snake_case/compound identifiers (`Jayne_`,
      `mal_gimbal`, `mal_config`, `mal_telemetry`, `mal_com`, `mal_far`, `mal_aircraft`, etc.).
      **Deliberately did not** use a blanket substring replace for "mal_" or "emma" — verified
      first that would have corrupted real, unrelated tokens already in the repo: Blender
      `normal_z` surface-normal variables and KiCad `thermal_pads`/`thermal_gap`/
      `thermal_bridge_width` PCB thermal-relief settings (contain "mal" as a substring),
      "washer" fastener text, and "piezoelectric" (contains "zoe"). All four verified intact
      after the sweep.
    - **Not verified: KiCad ERC/DRC.** No `kicad-cli` in this build environment. Every renamed
      symbol/lib-id/net string was changed identically everywhere it appears (single global
      substitution pass), which preserves netlist topology by construction as long as no
      instance was missed — a full repo-wide grep confirms zero remaining old-name
      occurrences in tracked files — but the maintainer should still open each of the 5 boards
      in KiCad and re-run ERC/DRC before trusting them for fabrication.
    - `MAL-*` BOM/component designators (`MAL-TILT-ENC-PCB`, `MAL-CAPE-B-2`, etc.) were renamed
      to `SKIPPER-*` along with everything else — these are baked into `ENC-NACELLE-1` and
      `CAN-PERIPH-GW-1`'s own netlists as cross-board net names, updated consistently.
    - Root `AGENTS.md` §9 table rewritten: dropped the "Firefly line" column from the live
      naming table (keeping a mutated Firefly quote next to the new generic name would still
      visibly signal the original character, defeating the purpose) and added a "Naming
      history" subsection recording the former names, inspirations, and original quotes for
      attribution completeness. The 4 avionics bay names (Shepherd's Room, Inara's Shuttle,
      River's Room, Simon's Medbay) were **not** renamed — out of scope, not requested.
    - Found and fixed one casualty of the mechanical rename: `avionics/WBS.md`'s Inara's
      Shuttle bay quote had been auto-mutated from "Mal, I will never understand you." to
      "Skipper, I will never understand you." (word-boundary rule correctly fired on the
      quote text since "Mal" is a real word there) — restored to the genuine, unmodified
      Firefly line since the bay itself wasn't renamed. **Caution for anyone re-running a
      similar sweep:** the two "Naming history" tables (here and `AGENTS.md` §9) and this
      bullet's own prose *intentionally* contain the former names as historical record — a
      second blind sweep pass will corrupt them (it did, twice, while drafting this entry;
      both times fixed by hand). Do not re-run a global rename script after this kind of
      historical text has been written; fix any further stray old-name occurrences with
      targeted, reviewed edits instead. Other decorative Firefly footer quotes throughout the
      repo (e.g. "— Pilot", "— Skipper") were left as the mechanical rename produced them,
      consistent with root `AGENTS.md` §10's existing practice of sprinkling on-topic quotes
      through the docs.

**Also touched, stale-doc fixes surfaced during this audit (not separate TODO items, fixed
in place per root `AGENTS.md` §11.4):**

- Root `AGENTS.md` §3 said "All work is published under CC BY 4.0" — corrected to state the
  dual-license split and point to `docs/attribution_and_licensing.md`.
- `README.md` "License" section, Component License Map, and "What This License Covers" all
  restated a single CC BY 4.0 project license — corrected to the CERN-OHL-W 2.0 /
  CC BY-SA 4.0 split.
- `REFERENCES.md` "Project license (this work)" (under "Creative-Universe Attribution and
  Fan-Engineering Terms") had the same stale single-license statement — corrected.
- `TODO.md` header license stamp said "CC BY SA 4.0" with a URL pointing at
  `/licenses/by/4.0` (mismatched slug) — corrected to CC BY-SA 4.0 with the matching URL.
- Root `WBS.md` §0.9/`TODO.md` §0.6 numbering collision (see "Numbering note" above).

**Used in:** `docs/attribution_and_licensing.md`, `docs/OSHW_CERTIFICATION.md`,
`REFERENCES.md` Part XV, `airframe/LICENSE`, `avionics/LICENSE`, `docs/LICENSE`,
`gcs/LICENSE`, `tools/LICENSE`, `current-specification/LICENSE`,
`graphical-build-guide/LICENSE`, `deferred/LICENSE`.


## §0.10 — Update and Correct Documentation Touching Every Non-Archived File

*(root `WBS.md`/`TODO.md` §0.10)*

This detail entry did not previously exist — root `WBS.md` §0.10/§0.10.1/§0.10.2 and
`TODO.md` §0.10/§0.10.1/§0.10.2 all pointed here (`docs/WBS.md` §0.10`, `§1.10.1`, `§0.10.2`)
before any of those sections existed, a broken cross-reference discovered and closed as part
of this same audit (see "WBS/TODO federation sync" below). Predecessor audits exist under the
pre-renumbering "0.6" label: `airframe/SPEC_VERIFICATION_0.6.1.md` (Systems) and
`docs/DOC_VERIFICATION_0.6.2.md` (Documentation), both dated 2026-08-01, left "In Progress"
with open action-item lists — this pass picks up from there rather than starting cold.

**Scope of this pass (2026-08-22):** a full read-only audit across six areas (airframe,
avionics, software/firmware/scripts, engineering-assessment docs, BOM/system-spec files,
WBS/TODO federation + REFERENCES.md), followed by fixing every confirmed finding directly in
the working tree. Below is organized by the two root-index bullets' own sub-items, each
stating what was actually verified/fixed and — honestly, per root `AGENTS.md`'s "nothing is
TBD" principle — what specifically remains open rather than claiming a closure that isn't
real. **Neither §0.10.1 nor §0.10.2 is fully closed** — each has genuine residual items,
listed below, now individually tracked rather than buried in an unstarted mega-task.

### §0.10.1 Systems

#### 1. Airframe specifications vs. as-built

Resolved every open item in `airframe/SPEC_VERIFICATION_0.6.1.md`:
- **Hull length**: confirmed **24.0 in (609 mm) is canonical** (maintainer-confirmed
  2026-08-22, after an intermediate pass incorrectly derived 690 mm from a naive span over
  baked shell extents — reverted; see that file's §1.1 for the full account).
- **Wing geometry "asymmetry"**: not a bug — a transcription mix-up one row down in the
  extents table (the 82 mm figure belongs to `Nacelle_Stbd`, not `Wing_Stbd`); confirmed
  symmetric against the wing SCAD source directly.
- **EDF mass/thrust labeling**: already correctly resolved in current `airframe/README.md`
  ("nacelle assembly," not bare "EDFs") — no change needed.
- **Mass-budget rows** were materially understated vs. the current BOM and corrected:
  fuselage ~350g→~630g, landing gear ~150g→~436g, avionics ~280g→~432g, power ~500g→~925g;
  two stale part names (DS3218MG/STS3215 → SPT5425LV) fixed. **Total AUW recomputed
  2,768g→3,911g**, dropping hover T/W from ≈1.61 to ≈1.14 (still VTOL-capable, materially
  tighter margin) — propagated to `README.md` and `airframe/README.md`.
- **Mesh validation**: confirmed *not* currently passing (MESH-01 cargo-shell fragmentation
  defect is a known, already-tracked open item, `TODO.md §1.1.1.0b`/airframe WBS) — reported
  accurately rather than claimed clean.

**Still open** (cannot be closed from this pass alone):
- A full BOM-category sanity check (see §0.10.2 item 3 below) suggests the true AUW may be
  materially higher than the corrected 3,911g figure — the row-level corrections above are
  individually solid, but a complete bottom-up AUW ledger recompute is a larger effort not
  attempted here. **Flagging this prominently: hover-margin numbers should be treated as
  provisional until that recompute happens.**
- Landing-gear wire diameter: pending Phase 7 coupon test (physical, cannot be closed from
  docs).
- Tilt-servo torque: BOM self-reports 25–26 kgf·cm with no external datasheet citation —
  requires supplier datasheet verification.
- **RESOLVED 2026-09-06 (owner direction):** landing gear's "R6" label is retained as the
  leg design's own permanent generation name (like a PCB's "Rev S1"), not a pointer into the
  project's global letter chain — that chain now reads Rev T for landing gear like every
  other component (root `AGENTS.md` §8; `airframe/landing-gear/WBS.md` header).
- `docs/PHASED_BUILD_GUIDE.md`, `graphical-build-guide/TODO-old.md`, and 3 other
  build-guide/federation files still carry the pre-correction Bay-lettering scheme
  (River's Room as "Bay D", Simon's Medbay as "Bay E" — should be C/D per root `AGENTS.md`
  §9) baked into their own `ETH-DE`/`ETH-EA` connector/conduit identifiers. Every *other*
  occurrence repo-wide was corrected this pass; these were deliberately left alone because
  fixing the identifiers (not just the prose) needs a dedicated pass verified against the
  full wiring cross-reference — a rushed edit here risks producing a wiring guide that's
  wrong in a new way. **New, significant open item — do not fabricate against these
  documents' Bay-lettered conduit names until reconciled.**

#### 2. Avionics specifications vs. as-built

`avionics/AGENTS.md` and the per-board `.md` files (root `AGENTS.md`'s stated as-built
authorities) were themselves already current. `avionics/README.md` was comprehensively
stale — corrected (see "Fix avionics docs" commit): retired board names used as live
terminology throughout, Ethernet wrongly scoped to 4 nodes instead of 8, superseded CC BY 4.0
license text. Also fixed: stale/broken script and file references across 6 board files
(`WASH_FOOTPRINT_VERIFICATION.md`→`PILOT_FOOTPRINT_VERIFICATION.md`,
`gen_jayne*.py`→real `gen_observer_carrier_*.py` paths, `inject_kaylee_trust_module.py`→real
filename), a footer license mismatch, and `XO.md`'s connector table (confirmed directly
against `XO.kicad_pcb`, not just doc cross-referencing, that `J_ETH_B`/`J_XCVR` are absent
from the as-placed board though still in the lagging schematic — removed from the doc's
as-built table).

**Still open:** a TPM part-number history ambiguity across `FlightEngineer.md`/`Observer.md`/
`CAN-PERIPH-GW-1.md` (SLB9672 vs. SLB9670VQ2.0 as the pre-2026-08-03-retarget part) that
would need direct `.kicad_sch` inspection from 2026-08-02 to resolve — marked "requires
verification" rather than guessed. `Pilot.md` still describes the schematic (not as-placed
PCB) design for its Ethernet PHY/magnetics/regulator sections — this is an already-tracked,
still-open WBS item (`avionics/WBS.md` §1.2a); a banner was added pointing to it so a reader
hits the caveat before the stale detail, but the underlying rebuild is not done here.

#### 3. Assessment and engineering documents

Audited all 17 `docs/` engineering analyses. Fixed: pervasive Bay-letter mislabeling (River's
Room/Simon's Medbay, see item 1 above — fixed everywhere except the flagged build-guide
files), retired-name net labels (`J_JAYNE`/`5V_JAYNE`/`5V_VERA`/`F_VERA`→`J_OBS`/`5V_OBS`/
`F_OBS`), 4 stale CC BY 4.0 license footers, a **thrust double-count in
`docs/structural_analysis.md`** that inflated its AUW baseline to a fabricated 16.5 lbm
(corrected; flagged that every downstream load case in that document needs re-derivation, not
attempted here — real structural re-analysis is out of scope for a documentation pass), two
documents (`docs/FIRST_FLIGHT_READINESS.md`, `docs/PYLON_INTEGRATION_2026-07-18.md`)
instructing fabrication of a tilt/nozzle-drive mechanism superseded within a day of being
written (added superseded-mechanism banners), a stale sensor selection in
`docs/TILT_SPAR_ANALYSIS.md` (MT6701→AK7455, rejected the same day it was written but never
updated), an internal self-contradiction in `docs/OBSERVER_LASER_ANALYSIS.md` (§5
recommended a pattern §4.3 of the same document had already superseded), 3 stale revision
stamps, and 2 literal "TBD" values (root `AGENTS.md` forbids these for masses/loads).

**Still open, genuinely ambiguous — not resolvable from repo text alone:**
- **CG target contradiction**: `docs/POWER_DISTRIBUTION.md`/`docs/FIRST_FLIGHT_READINESS.md`
  say 190 mm from nose; `docs/BATTERY_MOUNT.md` derives 280 mm from a stated
  46%-of-fuselage-length target. Both dated the same Rev R day. **Needs the maintainer's
  authoritative call**, not a guess.
- **"Claude Fable 5" AI-attribution** in `docs/LANDING_GEAR_ANALYSIS.md` (and 4 other repo
  files) — an earlier audit pass flagged this as "not a real Anthropic model name"; per this
  session's own model roster, Fable 5 is in fact a real model family member, so that flag was
  a false positive and **no change was made**. Noted here only so the flag isn't silently
  re-raised by a future pass without this context.
- `docs/AVIONICS_PB2_REDESIGN.md` is comprehensively stale (predates Observer,
  `CAN-PERIPH-GW-1`, the current PHY architecture, and the 2026-08-01 board rename) —
  recommend archival or a full rewrite rather than incremental patching; not attempted here.

#### 4. Software, firmware, scripts, and their documentation

Fixed extensively: `avionics/firmware/README.md`'s bay table and directory-layout stub
description (the `fc/` daemon has real Phase 6 sensor/monitor work, not a Phase-7 stub as
documented), stale `serenity/firmware` paths (repo root has no `serenity/` directory) in 2
files, `avionics/firmware/dts/README.md`'s overlay table (pointed at the archived non-"2"
Cape-A-1/B-1 overlays instead of the current `-a2`/`-b2` ones) and the
`avionics/firmware/dts/Makefile`'s build targets (literally could not `make` — pointed at
files moved to `archive/`; now builds only the current, non-retired overlays).
`tools/README.md`/`TODO.md`/`TOOL_REFERENCE.md`: a retired-board-name CLI example, wrong
avionics/GCS script paths, a case-sensitivity bug (`freecad-scripts/` vs. the real
`FreeCAD-scripts/`), a citation of `tools/update_bom.py` which doesn't exist, and ~21
previously-undocumented `tools/*.py` scripts now listed. `gcs/README.md` was comprehensively
stale (wrong board names, phantom files like `malcolm_config.yaml`) — replaced with a pointer
into `gcs/skipper/README.md`, which is maintained far more often and was itself carrying a
license-footer contradiction and two stale planned-but-not-yet-built file references, both
fixed. A retired-name orphan directory (`avionics/kicad/Jayne/`, one leftover file) was moved
into `avionics/kicad/Observer/`.

**Still open:**
- `avionics/firmware/AK7455_CALIBRATION_SPECIFICATION.md` references
  `CAN-PERIPH-GW-1/src/tilt_encoder.c`, which doesn't exist — the gateway board's firmware
  tree hasn't been started at all yet. Not tracked anywhere else either. **New item: needs a
  real WBS entry** (`avionics/WBS.md`) tracking "write `CAN-PERIPH-GW-1` tilt-encoder
  firmware," or the spec doc should explicitly say "not yet implemented, no target path
  exists" instead of citing a phantom path.
- No `.shellcheckrc` exists for the repo's 4 shell scripts — a soft gap, not a clear-cut bug;
  left as a decision for the maintainer rather than asserted as missing.

### §0.10.2 Documentation

#### 1. Compliance and licensing documents

Found and fixed the headline issue: **`docs/attribution_and_licensing.md` (the file every
other policy document points to) was a duplicate of a still-existing, differently-spelled
file with materially wrong content** — CC BY 4.0 instead of the correct CC BY-SA 4.0,
pre-rename board names in example schematic paths, references to a nonexistent
`CONTRIBUTING.md` and `firmware/LICENSE`, and unfilled `[repo]`/`[Your Name]` template
placeholders. Removed the stale duplicate, fixed ~19 inbound references. Separately
standardized the *filename itself* to American spelling
(`attribution_and_licencing.md`→`attribution_and_licensing.md`, since the rest of the project
already writes "license" the American way) per the maintainer's explicit direction, and did a
repo-wide British→American spelling pass while in there (center/fiber/program/behavior/
maneuver/artifact/mold/aluminum/etc. — see the "Standardize British->American spelling"
commit for the full word list and the two deliberate exceptions: the CERN Open Hardware
Licence's own official proper name, and the ISO 11898-1 standard's official title, both left
as their source documents actually spell them).

**Still open:** none identified as clearly unresolved for this specific bullet.

#### 2. README files (root + subsystem)

Fixed: `docs/README.md`'s own "Design Documentation by Domain" *live navigation* section
(not history) still pointed at retired board paths
(`avionics/kicad/Wash/`, `Zoë/`, `Kaylee/`, `Emma/`, `Jayne/`) and its "Historical Revisions"
table used retired names to describe the *current* Rev S baseline; `avionics/README.md`
(see §0.10.1 item 2 above); `gcs/README.md` (see §0.10.1 item 4 above);
`current-specification/README.md`'s stale project-wide license claim and extensive stale
board naming throughout its Component Categories/Power Distribution/Revision History
sections. All READMEs already using current naming were left alone.

**Still open:** none identified as clearly unresolved for this specific bullet.

#### 3. System specification files and BOM

Per the predecessor `docs/DOC_VERIFICATION_0.6.2.md §0.6.2.3` open items:
- **JSX viewers**: archived `serenity-rev-r.jsx` to `archives/`, matching the existing
  precedent for `serenity-rev-p.jsx`/`serenity-rev-q.jsx` — `serenity-rev-s.jsx` is now the
  sole current viewer, and the 2 stale self-references to rev-r were fixed.
- **`docs/bom_revP.json`/`bom_revQ.json`**: archived, matching their already-archived CSV
  siblings. `bom_revR.json` deliberately left in place (still referenced by
  `tools/compact_bom_entries.py`, doesn't show the same clear signs of being frozen history).
- **`bom_revS.csv`↔`bom_revS.json` sync**: fixed the two most consequential rows (EDF thrust
  figure was off by ~2.7× in the CSV — the number that actually feeds the hover-thrust
  calculation used throughout the flight-safety docs; the nacelle nozzle flap row was a full
  design revision behind, still describing the superseded Rev S single-flap instead of the
  current Rev T3 master+seal split).

**Still open, significant:**
- **~15 more `bom_revS.csv` rows have unquoted-comma `Description`/`Notes` fields that
  misalign columns under any RFC-4180 parse** — confirmed via `csv.DictReader`, and 3 of them
  are corrupted badly enough that wrong values (a fragment of the description) landed in the
  `Category`/`Qty`/`Mass`/`Supplier` fields of whatever process last regenerated
  `bom_revS.json` from this CSV (`CF-PLATE-2MM`, `PRINT-PUSHROD-CRANK`, `BALLSTUD-M3`). This
  needs a dedicated quoting-and-reverification pass, not a rushed hand-fix — tracked here as
  a new item rather than silently left broken.
- **`current-specification/README.md`'s own mass-budget table doesn't sum to its own stated
  AUW total**, and a rough whole-BOM category sum suggests the true AUW may be substantially
  higher than even the §0.10.1-corrected 3,911g figure (as much as ~5.6–5.8 kg, per a
  category-level, not row-level, sanity check) — see the AUW caveat under §0.10.1 item 1
  above. This is the single most consequential open item from this entire audit and deserves
  the maintainer's direct attention before it's treated as resolved.
- `tools/update_bom.py`, cited by `current-specification/README.md` and `tools/README.md` as
  the CSV↔JSON sync mechanism, does not exist — noted in both places rather than left as a
  dangling reference to a script nobody can run.
- **`bom_revS.json`/`.csv` predate the Rev T checkpoint (§6.4) and were not recomputed for
  it.** Confirmed deltas not yet reflected: nacelle mass (Rev T4b/T4c hollowing, −179g/pair),
  wing spar (Rev T1c fixed 20x16.3mm CF tube replacing whatever the BOM currently prices/
  masses as the spar part), and the nozzle drive (Rev T2 pushrod/cam). Given the AUW figure
  is already flagged above as possibly understated by ~1.7–1.9 kg before any of these T-series
  deltas are applied, this BOM should not be treated as authoritative for mass/CG until a
  full recompute happens — see the caveat now stated at the top of
  `current-specification/README.md`.
- **`docs/img/assembled-iso.png`** (root `README.md` hero image) is dated 2026-08-23 —
  predates both Rev T1c and Rev T4c geometry. Re-render needed before it can be captioned as
  current; root `README.md` now says so explicitly rather than implying it's up to date.

#### 4. WBS and TODO files

Fixed four real cross-file checkbox disagreements (`WBS.md` §1.1.3 wing STLs and iris
flap-sign fix; `tools/TODO.md`'s two misattributed/already-closed entries) and one orphan
TODO item (`TODO.md` §5.4 "OSHW certification," which pointed at two nonexistent WBS
sections — added a real detail entry under `docs/WBS.md` §0.9 and repointed it). Corrected
this file's own "Owned WBS branches" summary table (two stale per-section counts, one stale
total). This entry itself — creating the missing `docs/WBS.md` §0.10/§0.10.1/§0.10.2 sections
that root `WBS.md`/`TODO.md` had pointed at since the 2026-08-01 renumbering without them
ever existing — is the other half of this bullet.

**Still open, significant:** root `TODO.md` is **not** the lean, generated, pruned artifact
root `AGENTS.md` §10 describes — it's close to a verbatim copy of `WBS.md`'s open items,
including multi-paragraph nested prose with no bullet marker at all in many places. Measured:
43% of its bullet lines exceed the ≤70-char/one-line/no-prose cap (230 of 531), with entire
multi-paragraph sections copied wholesale (e.g. §1.1.3 Nacelles, §1.2d Trust-Module
Retarget). Several subsystem `TODO.md` files have smaller versions of the same problem.
**This is the single largest compliance gap found in this audit** — regenerating `TODO.md`
correctly from `WBS.md` is a substantial, repo-wide editorial task in its own right (verified
line-by-line against ~15 files) and was not attempted in this pass; flagging it as its own
follow-up rather than a quick fix bundled in here.

#### 5. REFERENCES.md file

Fixed: a duplicate-REF-ID bug (`REF-SENSOR-013`/`014` were each defined twice — once for the
MSPM0G351x-Q1 trust-module MCU, once for the SPT5425LV servo/LibreServo v2 board; renumbered
the MCU pair to `REF-SENSOR-017`/`018` and updated all ~13 MCU-context citation sites,
leaving the servo meaning on 013/014 to match the ~50 sites that already used it that way);
3 missing catalog entries for citations that had no matching definition
(`REF-AMS-001`/`REF-WGS84-001`/`REF-HAVERSINE-001`, added as "requires verification" per root
`AGENTS.md` §4 rather than guessed); a stale-looking "REQUIRES VERIFICATION" banner on the
already-superseded REF-SENSOR-012 entry, clarified as moot; the "Last updated" stamp (bumped
to 2026-08-22).

**Still open:** the REF-SENSOR-017 (renumbered MCU) entry's "Used in" file-path list had two
more stale paths beyond the ID itself (fixed, see commit); no further gaps found in this
pass beyond what's listed as open elsewhere in this section (e.g. the 3 new "requires
verification" entries above still need an actual URL/section lookup, which this pass
deliberately did not fabricate).

### Summary

Both §0.10.1 and §0.10.2 have had a genuinely thorough, evidence-based pass — dozens of real,
independently-verified defects fixed across ~90 files, three of them safety-relevant enough to
flag prominently (the AUW/T-W correction, the structural-analysis thrust double-count, and the
two build-guide documents that described a superseded fabrication mechanism). Neither is
being marked `[x]` here: each retains a short, honestly-scoped list of remaining items above,
most of which are now real, individually-actionable WBS/TODO entries rather than an
unstarted mega-task. The single item most worth the maintainer's direct attention is the AUW
uncertainty flagged twice above (§0.10.1 item 1, §0.10.2 item 3) — the corrected 3,911g figure
is solid at the row level but a category-level check suggests the true number could be
meaningfully higher, and that bears on the aircraft's actual hover margin.


## §1.5 — Documentation

*(root `WBS.md` §1.5)*

- [ ] **Update PHASED_BUILD_GUIDE.md** from Rev M 18-inch to Rev S 24-inch specifications
    (hull 609.6 mm, 50mm EDFs, v2·v2·v2·v2 node placement, Rev S power system, cargo system).
- [ ] **Rebuild `graphical-build-guide/` (38 SVGs) from Blender/FreeCAD-derived platform
    graphics, replacing the pre-Rev-N hand-drawn line art.** Two stale-geometry problems,
    not one:
    - The 26 numbered `build_guide_XX_*.svg` step cards (antenna placement, node install,
    inter-board wiring, first flight, etc.) are hand-drawn schematic line art — the
    airframe silhouettes in them were never derived from actual model geometry at all,
    and (per the §0.5 audit above) several depict the **archived** Cape-A-1/Cape-B-1
    hardware instead of the Rev R1 Pilot/XO baseline
    (`build_guide_09_avionics.svg`, `build_guide_11_inter_board.svg`,
    `build_guide_12_security_hw.svg`, `build_guide_20_node_placement.svg`,
    `build_guide_21_node_install.svg`, `build_plan.svg`, `components_overview.svg`) —
    this item supersedes that follow-up.
    - The existing partial outline-derivation pipeline
    (`graphical-build-guide/gen_hull_outlines.py`, `update_overview_paths.py`) only
    covers the 4 `overview_*.svg` files, and sources from
    `thingverse-serenity/files-hollowed-18in/` — pre-Rev-N 18-inch geometry, not the
    current Rev R1 24-inch baked hull-frame STLs in `airframe/stls/`.
    - **Approach:** render the current canonical geometry (baked `airframe/stls/` per
    `airframe/AGENTS.md`'s Hull-Frame Coordinate Standard, or directly from
    `airframe/freecad/assembly/SerenityAssembly.FCStd` / `serenity_assembly.py`) using
    Blender (`airframe/blender-scripts/serenity_render_views.py` already does isometric/
    cardinal renders and is the natural starting point) or FreeCAD TechDraw, and use
    those renders/silhouettes as the new base art for every card, in place of hand-drawn
    shapes. Re-verify all standards citations and hardware depictions added in §0.5
    survive the rebuild (don't lose the `[REF-ID]` work doing this).
    - Large, multi-file effort — scope into phases (e.g. overview cards first, then
    per-system build-guide cards) before starting; do not attempt as one pass.
- [ ] **Sync `bom_revO.json` ↔ `bom_revO.csv`** — verify all XCVR-49MHZ-1 BOM items (Phase 5
    above) are reflected in both files once XCVR-49MHZ-1 Phase 5 is complete.

- [x] **1.5.7 Consolidate CLAUDE.md/AGENTS.md into a single, model-agnostic `AGENTS.md`**
    *(done 2026-07-18)*. Root `AGENTS.md` now merges the former root `AGENTS.md` +
    `CLAUDE.md` into one authoritative, token-lean policy file usable by any AI agent
    (Claude, GPT, Gemini, Grok, local models). Root `CLAUDE.md` is now a one-line pointer
    to `AGENTS.md`, kept only for tooling that looks for that filename. Every federated
    `<subsystem>/CLAUDE.md` was renamed to `<subsystem>/AGENTS.md` (airframe, avionics,
    current-specification, deferred, docs, gcs, graphical-build-guide, tools). Folded the
    concurrently-merged "WBS.md / TODO.md Federation" governance section (Rev S2, from
    this same day's PR #138) into the new `AGENTS.md` §10 Workflow, updating its internal
    `CLAUDE.md` references to `AGENTS.md`.
    - **Volatile single-subsystem detail replaced with pointers**, since it goes stale
      faster than the policy file gets edited: Observer's laser-indicator class/spread specs
      (→ `docs/OBSERVER_LASER_ANALYSIS.md`), the landing-gear post/wire design
      (→ `docs/LANDING_GEAR_ANALYSIS.md`), the nacelle nozzle-drive mechanism
      (→ `docs/NOZZLE_DRIVE_TRADE.md` — newly cross-referenced from
      `airframe/AGENTS.md`, previously undocumented there), and Commo/XO/FlightEngineer/Observer
      sch↔pcb reconciliation narratives (→ each board's own `.md` under
      `avionics/kicad/<board>/`, which is already updated more often than the policy file).
    - **Confirmed a real staleness case while auditing:** `avionics/CLAUDE.md`'s Observer
      section described a raw TI AM62A3/AM62A7 chip-level design; `avionics/kicad/Observer/
      Observer.md` (Rev S1, 2026-07-13) had already moved to a PCM-071 SoM carrier design —
      the policy file was out of date relative to the as-built board doc. Root cause of
      this class of drift: subsystem status belongs in the board's own `.md`/analysis doc,
      not duplicated into the instructions file.
    - Repo-wide `CLAUDE.md` → `AGENTS.md` reference sweep across `README.md`,
      `PROJECT_INDEX.md`, `REFERENCES.md`, `REPO_ENFORCEMENT.md`, and design docs that
      cited the old filename; historical dated entries inside `TODO.md`/subsystem
      `TODO.md`/`WBS.md` files were left as-is (work log, not live links).


## §1.6 — Rev Q: Repo-Wide Architecture Propagation

*(root `WBS.md` §1.6)*

*No open items — baseline complete; retained for traceability.*


## §1.7 — Rev R: Component Rev Sync + s_ Prefix Removal

*(root `WBS.md` §1.7)*

*No open items — baseline complete; retained for traceability.*


## §5.1 — FCC (external radio systems)

*(root `WBS.md` §5.1)*

- [ ] **XCVR-49MHZ-1/2 FCC Part 15 §15.235 compliance** — field strength ≤10,000 µV/m at 3 m
    (≈30 µW / −15.2 dBm EIRP-equivalent, requiring a firmware PA limit from the as-designed
    +20 dBm down to ≈ −13 dBm — see §0.1), harmonic suppression per §15.235(b)/§15.209. Document
    via pre-compliance checklist (1.3 Phase 4). Formal FCC equipment authorization (FCC ID grant
    via TCB) required before airborne transmission on 49MHz channels (47 CFR §2.803/§15.19, not
    Part 95 §95.603). **§15.203 antenna-connector gap resolved in design (RP-SMA, see §0.1);
    board re-spin pending.**


## §5.2 — FAA (airworthiness and operations) &#9733;

*(root `WBS.md` §5.2)*

- [ ] **Aircraft registration** — register under 14 CFR Part 48 (sUAS, AUW <55 lbs) at FAA DroneZone. Replace N00000 placeholder in `decal_sheet.svg`. Mark on airframe per 14 CFR 47 — visible without moving any part. **Complete before first untethered flight.**
- [ ] **Remote Pilot Certificate** — verify FAA Part 107 Remote Pilot Certificate is current (24-month knowledge test recurrency).
- [ ] **Navigation lights compliance** — verify 6-position WS2812C nav light implementation: port RED (≥3 SM visibility), stbd GREEN, tail WHITE steady, belly WHITE strobe. Compliant with ICAO Annex 2 and 14 CFR 91.209.
- [ ] **sUAS data plate** — attach to airframe: operator name, contact info, registration number. See `decal_sheet.svg` "D — safety labels" zone.
- [ ] **Pre-flight area check** — LAANC authorization for any Class B/C/D/E airspace. Verify no TFRs, NOTAM conflicts. File NOTAM if operating in uncontrolled airspace with public nearby.
- [ ] **Airspace waiver (if applicable)** — if operating above 400ft AGL or in controlled airspace without LAANC, apply for FAA Part 107 waiver (approval time 90 days typical).


## §5.3 — Industry Standards Compliance

*(root `WBS.md` §5.3)*

- [ ] **Structural validation** — wing spar, keel, pivot rod, and tilt servo torque analysis documented per REVN_BUILD_GUIDE_24IN.md structural summary. Verify at actual build dimensions (24" hull).
- [ ] **IEEE/ISA/AUVSI best practices** — validate all design decisions against AUVSI UAS best practices; document in build record.
- [ ] **Tamper-evident logging** — verify CPLD write-blocker (ATF16V8BQL) on all 4 CN nodes prevents post-flight log modification; function as hardware-enforced non-executable microSD per CLAUDE.md requirement.


## §6.1 — Branch Reconciliation / Pre-Flight Compliance &#9733;

*(root `WBS.md` §6.1)*

- [ ] **Delete stale feature branches** on GitHub after confirming this reconciliation PR merges
    cleanly. Branches to delete: all `claude/*` branches except `claude/pr-reconciliation-forced-merge-4yefsw`.


## §6.2 — STL Mesh Repair

*(root `WBS.md` §6.2)*

*No open items — baseline complete; retained for traceability.*


## §6.3 — Rev S Checkpoint

*(root `WBS.md` §6.3)*

## §6.4 — Rev T Checkpoint

*(root `WBS.md` §6.4)*

**2026-09-06.** Comprehensive checkpoint per root `AGENTS.md` §8: every component is current,
integrated, tested, and documented as of this letter — components not listed below carry
forward from Rev S unchanged.

Components carrying new work into Rev T (numbered sub-revisions superseded by this checkpoint):

- **Wings — Rev T1c** (`airframe/wings-nacelles/WBS.md` §1.1.2): fixed CF spar (20x16.3mm
  tube, bonded wing member, not a rotating shaft) at 35% root chord / station 45.15mm; root
  joint splits shear (socket) from moment (80x60mm flange); tilt drive is a >1 rev reduction
  (14T/50T), not a direct servo throw; SPAR-20-2 (U2) station moved 45.15→28.0mm.
- **Nacelles — Rev T4c** (`airframe/wings-nacelles/WBS.md` §1.1.3): trunnion skewer deleted
  from both the pod and stator sleeve; pods hollowed fwd-biased (285→196g each, −179g/pair);
  hinged 23+10mm ESC bays (62x33mm stack, az 69°/249°) with 4 distinct flush access covers;
  motor-mount spider pattern changed 3@120°→4@90° (15/105/195/285°); cooling ports (Rev T4d,
  4x Ø5.5mm teardrop holes/bay); CG pivot re-derived to Z≈107.5mm (1.5in gear variant found
  not viable at this pivot — see `airframe/wings-nacelles/WBS.md` §1.1.3.8).
- **Nozzle drive — Rev T2** (superseding the Rev S1 internal-ring-gear drive): Option B
  pushrod/cam drive (`docs/NOZZLE_DRIVE_TRADE.md`), flaps doubled 20→40mm.
- **Landing gear — folded into Rev T** (`airframe/landing-gear/WBS.md`): sponson-mounted
  gear bays CLOSED, canonical 1.5in leg retained alongside the extended 3.0in variant,
  minimum safe leg length re-derived from nozzle ground clearance rather than cargo-box
  height. Its "R6" component design-generation name is unchanged and permanent (like a
  PCB's own "Rev S1") — only the project-wide letter pointer moved, per owner direction
  2026-09-06.

Not yet part of a Rev T checkpoint (still Rev S or earlier, tracked open in their own
WBS/TODO): avionics PCB placement/routing (`avionics/WBS.md`), firmware Phase 7
(`avionics/WBS.md` firmware branches), cargo winch STLs (`WBS.md` §1.1.1.2.1), rear/Phase 11
EDF (`deferred/AGENTS.md`).

*No open items — baseline complete; retained for traceability.*
