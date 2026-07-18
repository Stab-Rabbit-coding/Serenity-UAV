# Serenity UAV — Documentation, Standards & Regulatory Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
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
| §0.1 | 0.1 — FCC Part 95 Section-Number Verification | 0 | — |
| §0.7 | 0.7 — CI Lint Scope and Repo-Wide Lint Debt | 0 | — |
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
      - `CLANG_FORMAT` — `clang-format -i` (repo's own `.clang-format`: 4-space,
        80-col, aligned macros/comments) across all 27 active firmware `.c`/`.h` files.
        Pure whitespace; syntax-verified with `gcc -fsyntax-only` wherever the
        environment's dependencies allow (libgpiod ≥2.0 and the mavlink SDK aren't
        installable in this sandbox — pre-existing gaps, unrelated to this change).
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
      - `CPP` (cpplint, distinct from `CLANG_FORMAT`) — 113 findings on the current
        ruleset (vs. historical 25 — again a different filtered config), but the majority
        are cpplint enforcing Google C++ style conventions this project has *never*
        followed and explicitly overrides elsewhere: short symbol-only header guards
        (`SI5351_H`, not `AVIONICS_FIRMWARE_CN_SRC_SI5351_H_`) used consistently
        repo-wide; CC BY 4.0 `Author:`/`License:` header blocks instead of a Google-style
        `Copyright` banner (`AGENTS.md` §3); `.clang-format` itself already documents a
        deliberate Google-style deviation (4-space indent, "CLAUDE.md mandates 4-space
        indentation ... overrides clang-format's Google-style default of 2"). A few
        residual "extra space before (" hits are cpplint's own column-counting getting
        confused by non-ASCII characters (µ) in comments, not real formatting bugs.
        Rewriting 25+ files' header guards and adding Copyright banners to match a style
        guide this project doesn't use would be pure churn against its own convention.
      - `JSCPD` — 142 clones at a 10-line/50-token threshold (vs. historical 39 at
        whatever threshold produced that count). The overwhelming majority are either
        intentional structural repetition — SVG build-guide diagram templates sharing
        icon/shape markup by design, and BOM revision snapshots (`bom_revP/Q/R.json`)
        that are supposed to largely restate the prior revision plus incremental changes
        per the Rev-letter archival policy (`AGENTS.md` §8) — or independent per-board
        KiCad automation scripts (e.g. `mod_vera_ds_pcb.py` / `mod_Jayne_ds_pcb.py`) that
        are deliberately self-contained so one board's generator can be modified without
        risking another's already-validated PCB. Real de-duplication candidates exist
        (that Vera/Jayne script pair is the clearest one) but extracting shared code from
        working, physically-validated PCB-generation scripts is an architectural decision
        with real hardware consequences — needs explicit user review, not a mechanical
        lint fix, matching the same caution applied to the RCRS rename in §0.1 above.
      - `JAVASCRIPT_STANDARD` / `JSX` — the sole active file
        (`current-specification/serenity-rev-r.jsx`) would need 2-space indent and no
        semicolons under JavaScript Standard Style, which directly contradicts
        `AGENTS.md` §6's explicit, project-wide "4-space indent, every language, always"
        override. Not applying a linter's default style over an explicit project rule.


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
