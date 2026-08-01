# Serenity UAV — Documentation, Standards & Regulatory Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Last updated:** 2026-08-01
**Current design revision:** Rev S (2026-07-04)

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
| §0.1 | 0.1 — FCC Part 95 Section-Number Verification | 1 | — |
| §0.7 | 0.7 — CI Lint Scope and Repo-Wide Lint Debt | 1 | — |
| §0.8 | 0.8 — Tilt-Spar Material Allowables + Hall Encoder | 3 | — |
| §1.5 | 1.5 — Documentation | 3 | — |
| §1.6 | 1.6 — Rev Q: Repo-Wide Architecture Propagation | 0 | — |
| §1.7 | 1.7 — Rev R: Component Rev Sync + s_ Prefix Removal | 0 | — |
| §5.1 | 5.1 — FCC (external radio systems) | 1 | — |
| §5.2 | 5.2 — FAA (airworthiness and operations) | 6 | &#9733; |
| §5.3 | 5.3 — Industry Standards Compliance | 3 | — |
| §6.1 | 6.1 — Branch Reconciliation / Pre-Flight Compliance | 1 | &#9733; |
| §6.2 | 6.2 — STL Mesh Repair | 0 | — |
| §6.3 | 6.3 — Rev S Checkpoint | 0 | — |
| | **Total open (this subsystem)** | **17** | |

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
    the Rev R1 baseline (all 8 nodes now carry Wash/Cape-A-2 + Zoë/Cape-B-2 per CLAUDE.md).
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
    form to avoid ambiguity with "Emma," the board that also carries LoRa)*. Every
    code-identifier/label use of "RCRS" as a naming convention (not a regulatory claim) was
    renamed; every legitimate regulatory-term use of "RCRS" (i.e. actually discussing 47 CFR
    Part 95 Subpart C, Radio Control Radio Service) was left untouched. Scope, beyond the
    four classes originally called out here:
    - Firmware: `SI5351_RCRS_*`/`si5351_set_rcrs_channel()`/`rcrs_channel_reg_t`/
      `s_rcrs_channels` → `SI5351_49MHZ_XCVR_*`/`si5351_set_49mhz_xcvr_channel()`/
      `xcvr_49mhz_channel_reg_t`/`s_xcvr_49mhz_channels` in
      `avionics/firmware/cn/src/si5351.{h,c}`, `xcvr_kiss.c`, `main.c`; `MAL_RCRS_*` →
      `MAL_49MHZ_XCVR_*` in `gcs/malcolm/firmware/pb2i/src/mal_config.h`.
    - KiCad: `UART_RCRS_TX`/`UART_RCRS_RX` → `UART_49MHZ_XCVR_TX`/`UART_49MHZ_XCVR_RX` in
      `avionics/kicad/add_sensors_sbus.py` and both `Zoë.kicad_sch`/`.kicad_pcb` and
      `Emma.kicad_sch`/`.kicad_pcb` (pure net-name text edits, occurrence counts verified
      1:1 before/after — no geometry, placement, or routing touched); `JST-GH-3P-RCRS` →
      `JST-GH-3P-XCVR-49MHZ`; the Emma board title comment dropped the redundant "RCRS".
      Also updated the two Emma migration scripts (`gen_emma_sch.py`, `mod_emma_pcb.py`) so
      a future re-run doesn't regress the renamed nets.
    - Docs: `RCRS-49`/`TVS-RCRS`/`FB-RCRS` → `XCVR-49MHZ`/`TVS-XCVR-49MHZ`/`FB-XCVR-49MHZ` in
      `Emma.md`/`Zoë.md`; same pattern in the active current-spec files
      (`current-specification/bom_revS.csv`, `serenity-rev-r.jsx` — excluding the one BOM row
      already self-labeled `ARCHIVED`, left as-is per the revision-archival policy) and
      `docs/PHASED_BUILD_GUIDE.md`.
    - Also found and fixed while auditing: two DTS pinctrl labels
      (`malcolm_rcrs_uart_pins` → `malcolm_xcvr_49mhz_uart_pins`), a `malcolm_config.yaml`
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
      files under `avionics/kicad/Zoë/gerbers/` (fab output regenerated from source — net-name
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
        3 remaining "missing yaml stubs" findings on the Malcolm tracking scripts were a
        missing dev-tool dependency, not a code issue — installed `types-PyYAML`.
      - `PYTHON_PYLINT` (E/F classes only) — 5 real findings, all the same root cause:
        this dev sandbox's KiCad 7.0.11 `pcbnew` Python bindings don't have the KiCad 9
        per-layer `PCB_VIA.SetWidth(layer, width)` / enum-based `FOOTPRINT.Flip()` APIs
        the code is deliberately written against (project's actual target is KiCad 9, per
        `ci.yml`/`tools/validate_kicad.py`) — scoped `# pylint: disable=...` comments
        added with the version-mismatch explanation, not code rewrites, since the code is
        correct for the real target. One further pylint tuple-unpacking false positive
        (`mod_vera_ds_pcb.py`/`mod_Jayne_ds_pcb.py`, `padnets.items()` mis-inferred as
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
        scripts (e.g. `mod_vera_ds_pcb.py` / `mod_Jayne_ds_pcb.py`) that are
        deliberately self-contained so one board's generator can be modified without
        risking another's already-validated PCB. Real de-duplication candidates exist
        (that Vera/Jayne script pair is the clearest one) but extracting shared code
        from working, physically-validated PCB-generation scripts is an architectural
        decision with real hardware consequences — needs explicit user review, not a
        mechanical lint fix, matching the same caution applied to the RCRS rename in
        §0.1 above.
      - `JAVASCRIPT_STANDARD` / `JSX` — the sole active file
        (`current-specification/serenity-rev-r.jsx`) would need 2-space indent and no
        semicolons under JavaScript Standard Style, which directly contradicts
        `AGENTS.md` §6's explicit, project-wide "4-space indent, every language, always"
        override. Not applying a linter's default style over an explicit project rule.


## §0.6 — Update and Correct Documentation Touching Every Non-Archived File

*(root `WBS.md` §0.6)*

**Overview:** Comprehensive documentation accuracy pass across all non-archived
subsystems, ensuring specifications match as-built hardware, all engineering
documents are current, and all supporting documentation (compliance, licensing,
README files, BOM, WBS/TODO files, REFERENCES) is complete and consistent.
Two major streams: Systems (0.6.1) and Documentation (0.6.2).

### 0.6.1 — Systems Documentation Verification

- [ ] **Airframe specifications vs as-built** — verify each component's spec (weight,
    dimensions, material, finish, procure vs print, CG) against the actual build or
    most recent CAD/STL snapshot (current baseline: 24-inch hull, Rev S1 nacelles,
    tilt-spar/hall-encoder integration complete). Ensure `docs/PHASED_BUILD_GUIDE.md`,
    BOM files, and subsystem README files match the current airframe design revision.
    Scope: fuselage (hull sections, access panels, cargo gondola, door system, winch),
    wings (spar, leading edges, control surfaces), nacelles (EDFs, nozzle iris, tilt
    servo, hall tilt-feedback encoder), landing gear (wire schedule, mounting bosses),
    and all structural provisions (cable runs, cooling ducting, battery bay, avionics
    racks).

- [ ] **Avionics specifications vs as-built** — verify each PCB, cape, and comms node
    matches its current board revision (as of 2026-07-31: Wash/Cape-A-2, Zoë/Cape-B-2,
    Emma Rev S1, Kaylee Rev S1, Jayne Rev S1). Check pinouts, connector types, signal
    assignments, voltage rails, thermal specs, mass, and mounting footprints against
    the live schematic and PCB layouts (`avionics/kicad/<board>/`). Verify that
    `current-specification/bom_revS.csv`, `bom_revS.json`, and the build guide reflect
    current connector naming (XCVR-49MHZ, not RCRS — see §0.1) and component selections.
    Confirm all board markdown files (`avionics/kicad/<board>/<board>.md`) are up-to-date
    with the latest design changes (e.g., Jayne SoM upgrade to PCM-071).

- [ ] **Assessment and engineering documents** — verify all analysis and trade-study
    documents are current and cite the correct subsystem revisions:
    - `docs/TILT_SPAR_ANALYSIS.md` — verify material allowables against MMPDS-2023/AMS
      and update material references (see §0.8).
    - `docs/NOZZLE_DRIVE_TRADE.md` — confirm "DECISION AMENDMENT" reflects current nacelle
      nozzle-drive design (wing-fixed sun gear, nacelle pinion, geared bellcrank).
    - `docs/LANDING_GEAR_ANALYSIS.md` — verify wire schedule, drop-height selection,
      and coupon-test results against the current design (bay placements in middle section).
    - `docs/JAYNE_LASER_ANALYSIS.md` — confirm both Class 2 laser mount locations,
      specifications, and interlock logic.
    - `docs/PHASED_BUILD_GUIDE.md` — update from Rev M 18-inch to Rev S 24-inch across
      all Phase 0–4 structural and assembly details; update Phase 5+ avionics placement
      and electrical connections for all 8 nodes.

- [ ] **Software, firmware, and scripts documentation** — verify docstrings, inline
    comments, and README files match the actual code functionality:
    - Avionics firmware: `avionics/firmware/*/src/` — verify all module-level and
      function-level documentation describes current implementation (not stale prior
      versions).
    - GCS Malcolm: `gcs/malcolm/firmware/pb2i/src/` and `gcs/malcolm/firmware/host/` —
      ensure all subsystem init, telemetry, and tracking routines are documented and
      match the live code path.
    - Airframe/FreeCAD scripts: `airframe/freecad-scripts/` and
      `airframe/blender-scripts/` — verify docstrings describe the actual geometry
      transforms and output file locations.
    - Build/validation tools: `tools/` — update docstrings in `validate_kicad.py`,
      `validate_stls.py`, and any other active linting/verification scripts to match
      their current checks and pass/fail criteria.

### 0.6.2 — Documentation Structure and Consistency

- [ ] **Compliance and licensing documents** — verify each top-level and subsystem
    README includes:
    - Correct **CC BY 4.0** (or equivalent) license declaration per `docs/attribution_and_licensing.md`.
    - Attribution to **Steve Griffing** (as primary author) and any AI-model contributors
      (cite model name separately, e.g. "Claude Sonnet 5" rather than lumping all models
      together).
    - Links to `AGENTS.md`, `REFERENCES.md`, and any applicable design analysis docs.
    - For subsystems with original hardware designs (airframe, avionics, gcs): confirm
      CERN-OHL-W 2.0 hardware license is declared and tracked in separate license files
      per subsystem (as planned in §0.9).

- [ ] **README files — all levels** — update to reflect Rev S baseline and 8-node
    architecture:
    - Root `README.md` — ensure project scope, high-level architecture, and first-flight
      target (Phase 5) are current.
    - Subsystem READMEs:
      - `airframe/README.md` — 24-inch hull, CF-PETG printing, STL output directory structure.
      - `avionics/README.md` — 8-node PACE failover, PCB revisions (Wash/Cape-A-2, Zoë/Cape-B-2,
        Emma/Kaylee/Jayne Rev S1), comms topology (CAN FD, RS-485, Ethernet ring, 49 MHz / LoRa).
      - `gcs/README.md` — Malcolm hardware spec, 5-radio comms node, QGroundControl integration.
      - `docs/README.md` — pointer to AGENTS.md, REFERENCES.md, analysis docs, build-guide phases.
      - `current-specification/README.md` — BOM rev strategy, part cross-reference, Rev S baseline.
      - `tools/README.md` — build automation scripts, Blender/FreeCAD/KiCad pipeline tools.
      - `graphical-build-guide/README.md` — pointer to WBS/TODO, Phase 0–10 build sequence,
        link to Blender/FreeCAD source geometry.

- [ ] **System specification and BOM files** — verify consistency across all formats:
    - `current-specification/bom_revS.csv` and `bom_revS.json` — component count, part numbers,
      mass totals, supplier links, and footprint data match the current PCB/airframe state.
    - Component-level specs in subsystem directories (e.g., `avionics/kicad/Wash/Wash.md`,
      `airframe/stls/fuselage/README.md`) — ensure every component listed in the BOM has
      a corresponding README or `.md` file documenting its interface, mass, procurement source.
    - Procured vs. printed component split — update `current-specification/` and build guides
      to mark which parts are 3D-printed (with wall thickness / infill spec), purchased
      (with supplier/PN), or machined (with material/finish spec).

- [ ] **WBS and TODO file sync** — update both files to reflect completed work and reopen
    any tasks that are genuinely still open (do not mark complete until verified):
    - Delete any completed items from `TODO.md` (the lean, open-only view).
    - Verify that every open-item checkbox in root `TODO.md` has a corresponding detailed
      entry in `docs/WBS.md` with full context.
    - Regenerate subsystem TODO files from their corresponding WBS files per `AGENTS.md`
      "WBS.md / TODO.md Federation" (§10 Workflow) — run a script or manual pass to pull
      only unchecked items.
    - Confirm no stale or duplicate items exist across TODO/WBS splits.

- [ ] **REFERENCES.md file** — audit all citations for accuracy and coverage:
    - Verify every `[REF-ID]` cited in code/docs has a matching entry in `REFERENCES.md`
      with exact section number and a validated URL.
    - Update any "requires verification" placeholders (e.g., MMPDS-2023 material allowables,
      MT6701 sensor pinout per §0.8) with real source citations.
    - Add `REF-MAT-*` and `REF-SENSOR-*` entries for material standards and encoder specs
      once §0.8 procurement/verification is complete.
    - Correct the 49 MHz transceiver reference from the superseded Part 95 claim to Part 15
      §15.235 (completed as part of §0.1 but verify REFERENCES.md consistency).
    - Check for any broken/archived URLs and mark them "link obsolete, historical reference"
      if not replaceable.


## §0.8 — Tilt-Spar Material Allowables + Hall Encoder Verification

*(root `WBS.md` §0.8)*

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
    `MAL-TILT-ENC-PCB` (Magntek MT6701, I²C, off-axis; MA732/SPI fallback). Confirm
    against the MT6701 datasheet: pinout/protocol, off-axis air-gap (assumed
    1.5 mm), ring OD/ID, IC radial offset (R = 12 mm), and ferrous-through-shaft
    behaviour; add a `REF-SENSOR-*` entry with a validated URL before PCB/harness
    sign-off. Bench-cal tracked in `avionics/emi-hardening/WBS.md` §1.4.6 and
    `avionics/WBS.md` §1.9.1.


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
    hardware instead of the Rev R1 Wash/Zoë baseline
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
      faster than the policy file gets edited: Jayne's laser-indicator class/spread specs
      (→ `docs/JAYNE_LASER_ANALYSIS.md`), the landing-gear post/wire design
      (→ `docs/LANDING_GEAR_ANALYSIS.md`), the nacelle nozzle-drive mechanism
      (→ `docs/NOZZLE_DRIVE_TRADE.md` — newly cross-referenced from
      `airframe/AGENTS.md`, previously undocumented there), and Emma/Zoë/Kaylee/Jayne
      sch↔pcb reconciliation narratives (→ each board's own `.md` under
      `avionics/kicad/<board>/`, which is already updated more often than the policy file).
    - **Confirmed a real staleness case while auditing:** `avionics/CLAUDE.md`'s Jayne
      section described a raw TI AM62A3/AM62A7 chip-level design; `avionics/kicad/Jayne/
      Jayne.md` (Rev S1, 2026-07-13) had already moved to a PCM-071 SoM carrier design —
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

*No open items — baseline complete; retained for traceability.*
