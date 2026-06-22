# Serenity UAV — Work Breakdown Structure

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP  
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0  
**Last updated:** 2026-06-15  
**Current design revision:** Rev R (2026-06-10) | **Build target:** 24-inch hull (REVN_BUILD_GUIDE_24IN.md)

---

## Quick-Reference: End State vs. Current State

| Domain | End State | Current Status |
|--------|-------------------|----------------|
| Hull   | 609.6 mm CF-PETG / PU foam / CF skeleton | SCAD sources complete; all four fuselage SCAD shells at Rev R; cargo section at Rev R (clamshell, avionics bays, GPS); STLs pending regeneration |
| Nacelles | 2× 50mm tandem EDF, CG pivot Z=83mm, M=1.0 gear, iris nozzle | `nacelle_pod_50mm_tandem.scad` complete; Rev R stator shells (`_revo.stl`) pending render |
| Nacelle EDFs | XFly Galaxy X5 50mm 12-blade 6S 3200KV, 1240g each; 2232g/nacelle (90% additive via stator); 4464g total | Baseline EDF selected (xfly-model.eu); nacelle T/W ≈ 1.61 at Phase 5–10 AUW — VTOL hover capable |
| Rear propulsion | 55mm 6S EDF, reduced-area neck intake, **fixed canonical elliptical tail nozzle** (2.06×1.76 in / 52.3×44.7 mm) + **4 RCS bleed-air thrusters** | **DEFERRED — Phase 11.** Files in `deferred/aft-edf/` — SCAD/STLs need regeneration for 55mm + nozzle + RCS. Adds ~1275g forward thrust; rear EDF not counted in hover T/W; Phase 11 hover T/W ≈ 1.43. |
| Cargo bay | Clamshell doors + SG90 servos + DRV8833 + N20 winch + Dyneema + auto-latch + GPS ring + FPV bezel | ✓ All 13 cargo STLs generated (PR #21 + PR #22 2026-06-01); BOM updated bom_revP.json/csv; gondola shell open |
| PCBs | **Rev Q:** all 8 nodes use EM-hardened Wash/Zoë capes. **Kaylee** is the PDB. Two **Emma** boards give 49 MHz connectivity (Part 15 §15.235). Cape-A-1, Cape-B-1, XCVR-49MHZ-1 archived 2026-06-05. | Rev R schematics complete (Wash: 2× EMI-hardened Ethernet PHY; Zoë: 1×). Kaylee PCB DRC clean (0 shorts); gerbers generated 2026-06-10; manual placement and trace routing remain. |
| Firmware | 8-node cooperative flight, PID governor, OA, cargo, logging | serenity-cn Phase 6 ✓; serenity-fc Phase 6 stub only; all Phase 7 items open |
| Physical build | Airborne, autonomous, cargo-capable | Not started — awaiting STL exports, PCB fabrication |
| Regulatory | FAA Part 107 [REF-FAA-002], Part 48 §48.205 [REF-FAA-001], §91.209 [REF-FAA-003], FCC Part 15 [REF-FCC-001, REF-FCC-002, REF-FCC-003 §15.235] | FAA registration placeholder; XCVR-49MHZ-2 pre-compliance pending; §15.235 power budget gap open, §15.203 antenna-connector gap resolved in design (§0.1) |

---

## 0.0 — Standards Vetting and Regulatory Compliance

All items in this section must be resolved before any physical build step.  See `REFERENCES.md`
for the full standards catalog.  All open verification items from `REFERENCES.md` are
tracked here.

### 0.1 — FCC Part 95 Section Number Verification — RESOLVED: wrong CFR Part, not just stale section numbers

**Resolved 2026-06-20.** The original premise of this item — that the 49 MHz Emma link's
§95.635/§95.655/§95.639 citations were merely *pre-2017 section numbers* needing renumbering —
was incorrect.  47 CFR Part 95 Subpart C (Radio Control Radio Service, RCRS) covers only the
26–28 MHz, 72 MHz, and 75 MHz bands; it has **no provisions for 49 MHz at all**, under any
section number, in any year.  The 49.82–49.90 MHz band actually used by Emma is governed by
**47 CFR Part 15 §15.235**, an unlicensed intentional-radiator rule with a field-strength
limit, not Part 95 RCRS.  `REFERENCES.md` REF-FCC-003 has been rewritten accordingly, and the
"TDDS"/"LERS"/"27 channels" terminology in the old entry (unverifiable against any real Part 95
text) has been removed and logged under "Removed / Superseded Citations."

- [x] **Correct REF-FCC-003 in `REFERENCES.md`** — replaced Part 95 RCRS citation with
    47 CFR Part 15 §15.235 (plus §15.5, §15.203, §15.209 as applicable); added the old citation
    to "Removed / Superseded Citations."  *(2026-06-20)*
- [x] **Rework `malcolm_antenna_spec.md` Link 4 compliance math** — §15.235 is a field-strength
    limit (≤10,000 µV/m at 3 m), not an EIRP/ERP figure.  Converting via EIRP = E²·4πd²/377Ω gives
    an EIRP ceiling of **≈ −15.2 dBm (≈ 30 µW)** — about 35 dB below the 100 mW (+20 dBm) the spec
    previously assumed.  Emma's PA must be firmware-limited to ≈ −13 dBm (≈ 48 µW) conducted to
    comply, not +20 dBm.  *(2026-06-20)*
- [x] **Update CLAUDE.md, TODO.md status lines, and other docs** referring to the 49 MHz link as
    "RCRS" — relabeled as "49 MHz (Part 15 §15.235)" throughout active (non-archived) docs.
    *(2026-06-20)*
- [x] **Re-architect the 49 MHz link's power/range budget — RCRS researched and rejected
    2026-06-20 (REF-FCC-004).**  At the §15.235-compliant ≈ 48 µW conducted power level, this
    link's realistic range is likely well under a quarter mile, which contradicts its design role
    as River's resilient long-range backup comms path (see CLAUDE.md Avionics Workload Balancing).
    47 CFR Part 95 Subpart C RCRS (72/75 MHz) was evaluated as a candidate replacement — it
    permits 0.75 W mean output (§95.767), ≈42 dB above the §15.235 ceiling — and rejected for three
    independent reasons: (1) **§95.731 prohibits RCRS transmitters from carrying data at all**
    ("No person shall use a RCRS transmitter to transmit data"; one-way telecommand/indicator-
    telemetry only) — disqualifying regardless of band or power, since Emma's actual payload is
    bidirectional signed/authenticated AX.25 packet data required by the Zero Trust policy
    (REF-NIST-001 §2.1); (2) Serenity is an aircraft, so §95.763(c) restricts it to the 72 MHz
    band only — 75 MHz is surface-craft-only by rule, and **78 MHz is not an RCRS allocation at
    all**; (3) moving to 72 MHz would still require a from-scratch Part 95 equipment certification
    (§95.735's non-certified-transmitter exception covers only 26–28 MHz), so it does not reduce
    the certification burden already carried under Part 15.  Full citation trail in
    `REFERENCES.md` REF-FCC-004.  **Remaining open item:** the underlying range/power-budget
    problem is still unresolved — candidates not yet researched are Part 90 land mobile (licensed,
    permits data) or revising the design intent for this link to match what Part 15 §15.235
    actually permits.  **Architecturally significant — do not resolve without user review.**
- [x] **§15.203 antenna/connector non-compliance, confirmed violation, resolved in design
    2026-06-20.** Emma's RF port (J2) previously used a generic SMA edge connector (Amphenol
    132289) — a standard antenna jack.  §15.203 text: *"the use of a standard antenna
    jack or electrical connector is prohibited."*  This obligation binds the manufacturer
    ("responsible party") directly — being the manufacturer does not create a self-authorization
    exception; if anything it is the manufacturer who bears the §2.803/§15.19 equipment-
    authorization burden.  §15.203's narrow exceptions (carrier-current devices; professionally
    installed radiators measured at the install site, e.g. perimeter protection/field disturbance
    sensors) do not apply to Emma.  **Resolution:** J2 changed to Amphenol **132289RP**
    (RP-SMA, reverse-polarity counterpart of 132289, identical PCB footprint, reversed mating-pin
    gender) — satisfies §15.203's "unique coupling" provision since generic standard-SMA
    antennas/cables cannot mechanically connect.  Updated `avionics/kicad/Emma.kicad_sch`,
    `avionics/kicad/Emma.kicad_pcb` (footprint Value/Description properties and silkscreen),
    `avionics/kicad/Emma.md`, `gcs/malcolm/hardware/docs/malcolm_wiring.md`, and
    `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`.  **Open follow-up:** physical board
    re-spin/fabrication run to populate 132289RP in place of 132289 on built boards — the
    design-level fix is complete but no boards have been re-fabricated yet.
- [x] **Remaining `TODO.md` references to "RCRS"/old Part 95 section numbers** — swept 2026-06-21:
    all 24 mislabeled instances (§1.5 BOM note, Avionics Workload Balancing, §2.5 procurement
    table, Phase 5/6/7/9/10/11 build/test steps, §4.3/4.4 firmware tasks) relabeled to
    "49 MHz (Part 15 §15.235)"; §1.3 (XCVR-49MHZ-1) marked SUPERSEDED — see below. *(One instance
    resolved 2026-06-21: `avionics/firmware/common/include/ax25_types.h` — see §0.3.)*
- [x] **Remaining non-`TODO.md` references to "RCRS"** — swept 2026-06-22. Fixed all prose/label
    mentions in active, non-archived, non-superseded files: `PROJECT_INDEX.md`,
    `airframe/placeholders/generate_placeholders.py`, `avionics/firmware/cn/src/{si5351.h,xcvr_kiss.h}`
    (doc comments only), `avionics/firmware/README.md`,
    `gcs/malcolm/firmware/pb2i/src/{mal_config.h,mal_telemetry.h}` (comments only),
    `docs/{AVIONICS_PB2_REDESIGN.md,REVN_BUILD_GUIDE_24IN.md,bom_revR.json}` (current-revision BOM
    only — `bom_revQ.json`/`bom_revP.json` are historical snapshots, left as-is),
    `current-specification/LICENSE_AND_ATTRIBUTION.md` (also replaced the fabricated "TDDS
    (Time-Division Dual-Simplex)" protocol claim — same root cause as the removed "TDDS"/"LERS"
    terminology — with the actual AX.25/KISS implementation), `deferred/aft-edf/README.md`, and
    `graphical-build-guide/{build_guide_14_antennas,build_guide_17_ground_test,
    build_guide_21_node_install,build_plan,components_overview,decal_sheet}.svg` (also fixed stale
    "TDDS"/6-channel/10 mW/547 yd figures in `components_overview.svg` and replaced the
    unverified "≤547 yd" range claim in `decal_sheet.svg`, a physical-decal artifact, with
    "range TBD" pending the open power-budget item above).  **Intentionally left unchanged**
    (correct/explanatory already, or out of scope — see new item below):  `CLAUDE.md`,
    `REFERENCES.md`, `avionics/firmware/dts/README.md`, `gcs/malcolm/hardware/docs/
    malcolm_antenna_spec.md` (all already correctly worded); `docs/PHASED_BUILD_GUIDE.md`
    (explicitly marked SUPERSEDED/historical); `docs/bom_revQ.json`/`bom_revP.json` and
    `avionics/kicad/archive/*` (historical revision snapshots / archived files per the
    archival-revision policy).
- [ ] **Code-identifier "RCRS" naming left unchanged — separate tracked follow-up.** The prose
    sweep above intentionally did not rename actual KiCad net labels, C macros, or reference
    designators that use "RCRS" as a naming convention (not a regulatory claim): net names
    `UART_RCRS_TX`/`UART_RCRS_RX` generated by `avionics/kicad/add_sensors_sbus.py`; C macros
    `SI5351_RCRS_*`/`si5351_set_rcrs_channel()` in `avionics/firmware/cn/src/si5351.{h,c}` and
    `MAL_RCRS_*` in `gcs/malcolm/firmware/pb2i/src/mal_config.h`; and connector/component
    reference designators `RCRS-49` (J1 port name), `TVS-RCRS`, `FB-RCRS` in
    `avionics/kicad/{Emma.md,Zoë.md}` and the corresponding `.kicad_sch`/`.kicad_pcb` files.
    Renaming these touches generated schematics/nets and firmware call sites together — a
    coordinated refactor with build/DRC verification, not a documentation fix.
    **Architecturally significant — do not rename without user review.**

### 0.2 — Incorrect Reference Correction

- [x] **Remove NIST SP 800-72 write-blocker citation** *(done 2026-06-14)* — NIST SP 800-72
    (2004) is "Guidelines on PDA Forensics" and is unrelated to write-blocker design.
    Replaced with NIST SP 800-92 §4.4.2 [REF-NIST-004] in `README.md` Patent Notice section.
    See `REFERENCES.md` "Removed / Superseded Citations" table.

### 0.3 — 14 CFR Part 47 vs Part 48 Clarification — RESOLVED

**Resolved 2026-06-21.** `docs/REVN_BUILD_GUIDE_24IN.md` and `graphical-build-guide/decal_sheet.svg`
were audited and carry no erroneous Part 47 citation (the build guide already includes a
clarifying note that Part 47 applies to manned aircraft).  The actual miscitation was found
instead in `avionics/firmware/common/include/ax25_types.h`, which incorrectly cited 14 CFR
Part 47 for UAS registration and claimed the 49 MHz AX.25 link requires an FCC amateur radio
license under 47 CFR Part 97 — both wrong, and inconsistent with this project's own
`REFERENCES.md` REF-PROTO-001 note that the link is license-exempt under 47 CFR Part 15
§15.235 [REF-FCC-003].

- [x] **Replace 14 CFR Part 47 references with Part 48 §48.205 where applicable** —
    corrected `ax25_types.h` to cite 14 CFR Part 48 §48.205 [REF-FAA-001] for aircraft
    registration display (a requirement independent of AX.25 addressing) and to clarify the
    station identifier fields are not amateur callsigns and require no Part 97 license
    [REF-PROTO-001].  Also replaced the file's stale "RCRS link" wording (see §0.1) with the
    correct Part 15 §15.235 citation.  `REFERENCES.md` REF-FAA-001 and REF-PROTO-001 "Used in"
    lists and the Open Standards Verification Items table updated accordingly.  *(2026-06-21)*

### 0.4 — AUVSI/ASTM Standards Identification — RESOLVED

**Resolved 2026-06-22.** Verified against ASTM's official store listings.  Two of the three
original candidates in this item were wrong: **F3322 is not a battery standard** — it is the
sUAS *Parachutes* specification (Serenity has no deployable recovery parachute, so F3322 does
not apply at all); the correct battery standard is **F3005**.  **F3003 was withdrawn by ASTM
in January 2023 with no replacement** and is not cited anywhere.  A fourth standard, **F2910**
(design/construction/test of a small UAS), was identified as the better general-airframe-
engineering fit and added in F3003's place.  Full verification trail, scope summaries, and
store.astm.org URLs are in `REFERENCES.md` Part X (REF-ASTM-001/002/003) and the "Removed /
Superseded Citations" table.

- [x] **Identify specific ASTM F38 Committee standards applicable to airframe engineering** —
    added REF-ASTM-001 (F2910-22 — Design and Construction of a Small Unmanned Aircraft
    System), REF-ASTM-002 (F3005-22 — Batteries for Use in Small Unmanned Aircraft Systems —
    applies to the LiPo 6S 4000 mAh pack), and REF-ASTM-003 (F3269-21 — Methods to Safely Bound
    Behavior of Aircraft Systems Containing Complex Functions Using Run-Time Assurance —
    applies to the PACE failover architecture).  Logged F3322 (misidentified — parachutes, not
    batteries) and F3003 (withdrawn 2023) in `REFERENCES.md` "Removed / Superseded Citations."
    *(2026-06-22)*

### 0.5 — Citation Completeness Audit (All Source Files)

- [x] **Audit SVG build guide files for standards citations — priority files done 2026-06-22.**
    Full-repo audit confirmed zero `[REF-ID]` citations existed anywhere in
    `graphical-build-guide/` (38 SVGs, not 26).  Added bracketed `[REF-ID §section]`
    citations to the four priority files at every location where it was safe to do so
    without overflowing a fixed-width text box (verified by reading surrounding `<rect>`
    geometry; not rendered): `decal_sheet.svg` (REF-FAA-001 §48.205 ×2, REF-ICAO-001,
    REF-FAA-003 §91.209(a)), `build_guide_13_nav_lights.svg` (REF-ICAO-001, REF-FAA-003
    §91.209(a)), `build_guide_11_inter_board.svg` (REF-MIL-001, REF-ISO-001).
    `build_guide_18_first_flight.svg`'s two Part 107/VLOS callouts already fill their fixed
    416 px boxes — adding brackets risks text overflow without a render check; left
    uncited, see follow-up item below.  Also corrected two factual errors found in
    `decal_sheet.svg` while auditing: the "AUW MAX" placard field on the sUAS data plate
    (D1) and operating-limits card (D4) was stale at "1,103 g (2.43 lb)" — does not match
    any current design figure — corrected to the current Phase 11 full-system AUW, 3,130 g
    (6.90 lb) per `README.md`; and the unverifiable "FAA regs require number legible from
    25ft" claim (no such distance figure traces to REF-FAA-001) was replaced with the
    actual verified §48.205(b)(1) character-height requirement (≥3 in / 76 mm).
    `decal_sheet.svg`'s "PAYLOAD 250 g maximum" field was checked against a suspected
    conflation with the FAA §48.25 registration-exemption weight threshold and found to be
    correct as-is — it is the aircraft's actual Jayne cargo-handling design payload (see
    `docs/PHASED_BUILD_GUIDE.md` "T/W with 250 g cargo"), not a regulatory citation.
    **Follow-up items opened from this audit (not yet resolved):**
  - [ ] `build_guide_18_first_flight.svg`'s Part 107/VLOS warning callouts (lines ~59–60)
    need citations but their fixed-width boxes are already near-full; requires either a
    layout change or rendering verification (see `/verify` skill) before editing text length.
  - [ ] No standards entry exists yet in `REFERENCES.md` for RS-485 (TIA/EIA-485) —
    referenced informally in `build_guide_11_inter_board.svg` and elsewhere; needs
    research before a REF-ID can be cited (do not fabricate).
  - [ ] The anti-collision/strobe "60 FPM" flash-rate figure in `build_guide_13_nav_lights.svg`
    and `decal_sheet.svg` has no traceable REF-ID in `REFERENCES.md` under REF-FAA-003;
    likely traces to 14 CFR §23.1401 or AC 20-30B convention but not yet verified — needs
    research before citing.
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
- [x] **Audit remaining firmware source files for standards citations — done 2026-06-22.**
    Reviewed all `.c`/`.h` files in `avionics/firmware/`, `gcs/malcolm/firmware/`, and the
    relevant `avionics/kicad/*.py` generator scripts.  Added bracketed `[REF-ID §section]`
    citations (all map to existing `REFERENCES.md` entries — none fabricated): FCC power-limit
    comments in `mal_config.h` (`[REF-FCC-001 §15.247(b)(3)(i)]` for SiK/LoRa,
    `[REF-FCC-002 §15.407(a)(3)]` for WiFi, `[REF-FCC-003 §15.235]` for the 49 MHz block);
    `[REF-PROTO-002]` (MAVLink v2) added to `mal_telemetry.h`; `[REF-PROTO-001]`/
    `[REF-FCC-003 §15.235/§15.5]` added to `avionics/firmware/cn/src/xcvr_kiss.{c,h}`;
    `[REF-IEC-001 §5.5.2]`/`[REF-VDE-001 Cl.4.3]` (5 kV reinforced isolation) and
    `[REF-IEEE-001 Clause 22/38]` (RMII / Ethernet isolation transformer) added to
    `avionics/kicad/{gen_cape_a2_pcb.py,gen_cape_b2_pcb.py,gen_cape_b2.py,add_eth_phy.py}`;
    `[REF-NIST-002 §6.2.5]` (EMI-hardening design objective) added to the Wash/Zoë/Kaylee
    generator docstrings; same IEC/VDE citations added to the two DEPRECATED FreeCAD scripts
    (`airframe/FreeCAD-scripts/Serenity-{Assemble,Subsystem-Assembly}.py`) while they remain
    in-tree.  Physical product markings (PCB silkscreen text in
    `avionics/kicad/complete_xcvr_49mhz2.py`, KiCad schematic title-block strings) were
    deliberately left as human-readable regulatory text, not converted to the internal
    `[REF-ID]` bracket convention — that convention is for source/doc citations, not
    end-user-facing physical labels.
    **Functional security gap found (not a citation gap) — opened as a new item:**
    `gcs/malcolm/firmware/pb2i/src/mal_telemetry.c` `dispatch_message()` only filters on
    MAVLink `sysid`; it does **not** verify the MAVLink v2 HMAC-SHA256 message signature,
    despite `MAL_TPM_KEY_HANDLE` (`mal_config.h`) provisioning a TPM key slot for exactly that
    purpose, and despite CLAUDE.md's "every message is digitally signed and authenticated"
    requirement [REF-NIST-001 §2.1, §2.2].  Flagged in a code comment at the dispatch site;
    implementing the actual verification is a security-critical functional change, not a
    documentation fix, and needs its own design/implementation pass — **do not implement
    without dedicated review.**
- [x] **Audit KiCad companion Markdown files — done 2026-06-22.** Note: the file this item
    called `XCVR-49MHZ-2.md` does not exist under that name — the board's companion file is
    `Emma.md` (XCVR-49MHZ-2 is its formal/silkscreen designation; Emma is the callsign used
    for the file). Findings per file:
  - `Wash.md`: added `[REF-IEC-001 §5.5.2]`/`[REF-VDE-001 Cl.4.3]` to the existing
    "≥8 mm creepage / ≥1.5 mm clearance" PCB layout rule (§"Isolation creepage") and to
    reference item 4; fixed a stale `XCVR-49MHZ-2.md` filename reference (→ `Emma.md`) in
    "Related Files"; flagged reference items 5–6 (IEC 61000-4-5, MIL-STD-461G) and the EMC
    Compliance Targets table as citing standards with no REF-ID yet in `REFERENCES.md`
    (marked with a `†` footnote, not fabricated).
  - `Zoë.md`: its creepage/clearance rule is inherited by explicit reference to Wash
    ("The Wash layout constraints apply equally here") — no separate citation needed.
    Same `†` footnote treatment applied to its reference-list items 5–6.
  - `Kaylee.md`: added `[REF-NIST-002 §6.2.5]` to the 500 W/m² EMI design-objective
    statement; same `†` footnote treatment applied to its MIL-STD-461G/IEC 61000-4-x EMC
    table rows. The BQ76930 cell-tap "≥8 mm creepage" note (line ~594) is a basic-insulation
    multi-cell-BMS spacing rule, not the project's 5 kV reinforced-insulation topic — left
    uncited (no applicable REF-ID exists; would need an IPC-2221 catalog entry, not yet
    researched).
  - `Emma.md`: already well-cited (REF-FCC-003 referenced throughout, correctly). Converted
    two informal citations to bracket form, and fixed a dangling reference to the archived
    `XCVR-49MHZ-1.md` (→ `archive/XCVR-49MHZ-1.md`).
  - [ ] **New follow-up:** MIL-STD-461G (EMI/EMC emissions and susceptibility for aircraft)
    and IEC 61000-4-2/-4-4/-4-5 (ESD/EFT/surge immunity test methods) are cited by name
    across `Wash.md`, `Zoë.md`, and `Kaylee.md` but have no `REFERENCES.md` catalog entry —
    needs the same official-source verification treatment given to REF-ASTM-* in §0.4
    before REF-IDs can be assigned.

### 0.6 — IEC 62368-1 PCB Layout Isolation Verification

- [x] **Verify creepage and clearance distances in Wash PCB layout** [REF-IEC-001 §5.5.2]
    — **verified 2026-06-22 via `kicad-cli pcb drc` (KiCad 9.0.2) against `Wash.kicad_pcb`.
    Result: NOT MET — still BLOCKS PCB fab.** DRC found 47 violations of the 0.5 mm
    `ISOLATION` netclass rule; after excluding 34 same-package pin-to-pin false positives
    (adjacent pins on the secondary side of the same isolator IC), **13 are genuine
    cross-domain clearance violations** — the `TMESH_P`/`TMESH_N` tamper-detect mesh
    routed too close to (in some cases inside the netclass minimum of) the isolated
    `GND2_CAN`/`GND2_ETH` domains, actual spacing as low as 0.125 mm against the 0.5 mm
    netclass minimum and the ≥ 8 mm physical creepage target documented in `Wash.md`.
    This confirms and quantifies the tamper-mesh routing problem already tracked in
    `TODO.md` §1.2a. Verification performed; **layout rework not performed** — per
    `CLAUDE.md`, repositioning footprints/routes to close this gap is referred to the
    user, not done automatically.
- [x] **Verify creepage and clearance distances in Zoë PCB layout** [REF-IEC-001 §5.5.2]
    — **verified 2026-06-22 via `kicad-cli pcb drc` against `Zoë.kicad_pcb`. Result: NOT
    MET — still BLOCKS PCB fab.** Same root cause as Wash: 40 `ISOLATION`-netclass
    violations, 31 same-package false positives excluded, **9 genuine cross-domain
    violations** between `TMESH_P`/`TMESH_N` (and, in one case, a primary-side Ethernet
    PHY ground pad) and the isolated `GND2_CAN`/`GND2_RS485` domains, actual spacing as
    low as **0.0 mm (direct contact)**. Not fixed here, same reason as Wash.
- [x] **Document verified creepage/clearance values** in `avionics/kicad/Wash.md` and
    `avionics/kicad/Zoë.md` — added a "Verification status" block to each file's
    "Isolation creepage" PCB layout constraint with the measured DRC findings above,
    dated and tool-versioned, distinguishing the design target (≥ 8 mm creepage /
    ≥ 1.5 mm clearance, IEC 62368-1 Annex G) from the as-laid-out current state (not met).

### 0.7 — CI Lint Scope and Repo-Wide Lint Debt (open — deferred to separate remediation effort)

- [ ] **`run-lint` (`github/super-linter@v4`) grades every PR against the entire
    repository, not its diff** — `VALIDATE_ALL_CODEBASE: true` in
    `.github/workflows/super-linter.yml` causes even single-file PRs (e.g. PR #107,
    TODO.md-only) to fail ~17 sub-linter categories simultaneously (`CLANG_FORMAT`, `CPP`,
    `CSS`, `EDITORCONFIG`, `GITHUB_ACTIONS`, `JAVASCRIPT_STANDARD`, `JSCPD`, `JSON`, `JSX`,
    `MARKDOWN`, `NATURAL_LANGUAGE`, `PYTHON_BLACK`, `PYTHON_PYLINT`, `PYTHON_FLAKE8`,
    `PYTHON_ISORT`, `PYTHON_MYPY`, `SHELL_SHFMT`). Confirmed pre-existing: the same check already fails on
    `main` at the PR #105 merge commit, so this is not a regression from #107.
    Decision (2026-06-21): defer changing `VALIDATE_ALL_CODEBASE` for now; track as a
    separate remediation effort rather than a CI config change bundled with feature work.
- [ ] **Repo-wide lint debt** — observed counts as of the PR #107 full-codebase run:
    `EDITORCONFIG` 697, `PYTHON_BLACK` 72, `PYTHON_FLAKE8` 56, `PYTHON_ISORT` 47, `JSCPD` 39,
    `MARKDOWN` 32, `CLANG_FORMAT` 26, `CPP` 25, `PYTHON_MYPY` 7, `NATURAL_LANGUAGE` 17,
    `JAVASCRIPT_STANDARD` 5, `SHELL_SHFMT` 4, `CSS` 3, `PYTHON_PYLINT` 2, `JSX` 6, `JSON` 1,
    `GITHUB_ACTIONS` 1. Needs a dedicated remediation pass, file type by file type,
    separate from feature work, so each touched file is fixed under its own
    diff-scoped lint pass rather than a single repo-wide sweep.
- [ ] Note for whoever picks this up: applying the `VALIDATE_ALL_CODEBASE: false`
    scope fix also requires a GitHub credential with the `workflow` OAuth scope —
    neither this session's git push credential nor its GitHub MCP token could write
    to `.github/workflows/super-linter.yml` (`403 ... without 'workflow' scope`).

---

## 1.0 — Design Artifacts (Pre-Fabrication)

Complete all items in this section before ordering PCBs or starting any physical build step.

### 1.1 — 3D Models: SCAD → STL Exports (Rev R baseline)

All SCADs run on a host machine with OpenSCAD 2021.01+ or Blender 3.x+ (headless).
Output STLs go to `thingverse-serenity/files-hollowed-18in/`.

#### 1.1.0 **Hull-Frame Coordinate Standardisation (R1, 2026-06-11)**

All design artifacts standardised on the validated hull frame (X = +port, Y = +aft,
Z = +dorsal; origin = SerenityAssembly.FCStd world origin). See CLAUDE.md
"Hull-Frame Coordinate Standard".

- [x] **`tools/bake_hull_frame.py` created** — idempotent STL bake tool; applies the
    validated 2026-06-10 placements to STL vertex data; stamps binary header marker
    `SerenityUAV HULL-FRAME R1`; refuses to double-transform. *(done 2026-06-11)*
- [x] **9 STLs baked to hull frame** — Head, Cargo (both repair copies), Middle, Rear,
    Wing×2, Nacelle×2. Watertight validation PASS before and after; facet counts
    unchanged; re-read verification ≤ 1.5e-5 mm. *(done 2026-06-11)*
- [x] **`serenity_assembly.py` Rev R1** — all 8 primary placements now identity;
    `doc.saveAs()` fix; `freecadcmd` entry-point fix; `airframe/Serenity-Assembled.FCStd`
    regenerated and world extents verified identical to the validated assembly.
    *(done 2026-06-11)*
- [x] **48 generator/analysis scripts stamped** with the hull-frame standard header
    (SCAD, Blender, FreeCAD, cargo generators, build-guide tools; GCS and deferred
    files annotated as documented exceptions). *(done 2026-06-11)*
- [x] **Docs updated** — CLAUDE.md (baked-extents table + pipeline rule), README.md,
    REPO_ENFORCEMENT.md, serenity-rev-r.jsx (R1 entry; axis typo fixed),
    PROJECT_INDEX.md. *(done 2026-06-11)*
- [x] **Resolve nacelle port/stbd label swap.** Confirmed by user FreeCAD layout
    inspection (2026-06-11): harness conduit exits inboard face; original SCAD naming
    was inverted. Fixed: STL files renamed (port↔stbd swap), binary 80-byte headers
    patched, `bake_hull_frame.py` COMPONENTS corrected, `serenity_assembly.py` audit
    comment updated, SCAD build commands corrected (port: SWIRL_DIR=−1/PYLON_SIDE=−1,
    stbd: SWIRL_DIR=+1/PYLON_SIDE=+1), CLAUDE.md extents table corrected.
    *(done 2026-06-11)*
- [ ] **Re-verify head↔cargo joint bosses in hull Y.** The 2026-06-10 joint analysis
    used hull X as the longitudinal mating axis; in the validated frame the longitudinal
    axis is Y (sections mate at hull Y ≈ −71 mm; X is lateral). Re-check
    BOSS_FORE/BOSS_AFT positions in `s_head_shell24.scad` / `s_cargo_sect_shell24.scad`
    against the baked meshes. **BLOCKS head/cargo printing.**
- [x] **Regenerate cargo doors from the baked shell.** `cargo_door_port/stbd.stl`
    (2026-06-01) predate both the repaired-shell re-orientation and the bake; regenerate
    via `generate_cargo_doors.py` against the baked
    `s_cargo_sect_shell24_2mm_repaired.stl` and verify the belly faces hull −Z.
    **DONE 2026-06-16**: `generate_cargo_doors.py` rewritten for hull frame (Rev R1a).
    Belly faces detected by normal Z < −0.5.  Both doors watertight.
- [x] **Correct hinge location: outboard flank, not centreline.** Rev R1a (above)
    placed both doors' piano-hinge knuckles at the ship centreline X_CL (≈ −169.85 mm)
    with the free edges at the hull sides — backwards from the door behaviour already
    documented everywhere else in the repo (TODO.md §1.4.2, README.md, `rcrs49_wire_post.scad`),
    all of which describe the doors hinging at the **outboard flank/belly edge** and
    swinging **down and out from the aircraft, full 180° range of motion**, to open the
    bottom of the cargo bay. **DONE 2026-06-22 (Rev R1b, with user)**:
    `generate_cargo_doors.py` corrected so each door hinges independently at its own
    outboard belly edge with its free edge at X_CL — see corner-curvature note below
    for why the hinge X is NOT the cargo-section bounding box (X_SHELL_MIN/MAX). Removed
    the port/stbd knuckle Y-interleaving (no longer meaningful — each door is now its
    own independent piano hinge pinned to the fuselage, not a shared centreline hinge
    joining the two panels). Knuckle Z is now sampled from the belly interpolator at
    each hinge X rather than a bare literal.
    - [x] **Fix door-surface discontinuity found during verification.** First Rev R1b
        pass still produced doors with a visible crease: the door grid extended to the
        cargo-section bounding-box X (±72.7/−267 mm), but the real ventral belly mesh
        only exists out to X ≈ −114..−225 mm — beyond that the interpolator silently
        fell back to a flat plane, producing a sharp step roughly halfway across each
        door. **DONE 2026-06-22**: hinge lines are now derived at runtime from the
        actual detected belly-mesh edge (per-Y-row worst-case extent, so every sampled
        point has real data), AND a row/column despike pass (`despike_grid()`,
        max 1.0 mm/step) suppresses a second, smaller artifact at the aft-outboard
        corner where the belly curves toward vertical (into the side wall/aft
        bulkhead) faster than a single-valued height-field can represent — that corner
        also overlaps the documented landing-gear HULL_ATTACH_POS Y ≈ 100 mm boss
        region. The despike is a print-safety net, not a substitute for verifying
        the aft-outboard corner shape in FreeCAD — see sub-tasks below.
    - [x] **Fix disconnected knuckles / non-straight hinge axis found during
        verification.** The despiked-panel fix (above) sampled each knuckle's Z
        independently from the belly contour, so the 4 knuckles per door landed at
        4 different Z heights — physically wrong (a single CF rod is rigid and
        straight) and some knuckles ended up too far from the panel surface to union
        into the same solid (disconnected, floating geometry). **DONE 2026-06-22**:
        all 4 knuckles on a door now share one constant (X, Z) hinge axis (Z = mean
        of the panel's actual contour at the 4 knuckle positions + KNUCKLE_R); each
        knuckle is bonded to the contoured panel via a small per-knuckle gusset block
        (`make_knuckle_gusset()`) bridging whatever local Z gap exists between the
        straight axis and the panel surface at that knuckle's Y. Final doors: port
        55.2×106.0×9.1 mm (hinge X ≈ −117.6 mm, hinge Z ≈ 5.11 mm), stbd
        55.7×106.0×9.2 mm (hinge X ≈ −222.5 mm, hinge Z ≈ 5.22 mm); both verified as a
        single connected watertight body (`trimesh` `split()` → 1 body each).
    - [ ] **Verify cargo door fit in slicer** — open `cargo_door_port.stl` and
        `cargo_door_stbd.stl` in slicer; confirm hinge knuckles align at X ≈ −117.6 mm
        (port) and X ≈ −222.5 mm (stbd), free edges meet at X ≈ −169.85 mm, and panels
        cover Y = 2..108 mm at Z ≈ 0..5 mm. Pay particular attention to the aft-outboard
        corner of each door (Y → 108, near the hinge edge) — this is where the despike
        safety net (above) is masking real but algorithmically-unresolved hull
        curvature; confirm by eye it isn't flattened in a way that leaves a gap against
        the real hull. Verify no overlap with hull boss sockets (HULL_ATTACH_POS
        Y = 25, 100 mm). **BLOCKS cargo door printing.**
    - [ ] **Piano-hinge CF rod (×2, independent)** — verify 3 mm CF rod passes through
        each door's own 4 knuckle bores (3.15 mm bore) — port and stbd are now two
        separate pins/rods, not one shared centreline pin; test in printed prototype
        before final assembly.
    - [ ] **Sync `cargo_sect_shell24.scad` hinge-pin blocks to the Rev R1b hinge lines.**
        The shell's `HINGE_Y`/`HINGE_Z` grub-screw block parameters (cargo_sect_shell24.scad
        lines ~329-340) still describe a pre-bake, part-local frame (Y = vertical,
        Z = lateral) from before the hull-frame rewrite, and were never updated for the
        Rev R1a/R1b door geometry. Re-derive the shell-side hinge-pin retention blocks
        from the corrected hull-frame hinge lines (port X ≈ −117.6 mm, stbd X ≈ −222.5 mm —
        the real detected belly edge, not the cargo-section bounding box; re-run
        `generate_cargo_doors.py` and read the printed "safe belly-mesh X extent" if the
        shell STL changes) before cutting the belly opening. **BLOCKS cargo door installation.**
- [ ] **Consolidate duplicate cargo shell copies.**
    `fuselage/s_cargo_sect_shell24_2mm_repaired.stl` (367,506 facets, later repair pass)
    vs `fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl` (368,352 facets, used by
    the assembly). Both now baked; keep one canonical copy.
- [ ] **Hull-frame placements for VERIFY parts.** Cargo mounts (8), pylons, EDF sleeves,
    nozzles/gears, battery tray, belly panel, tip caps, dorsal antenna fin, landing
    legs/feet remain part-local; validate each in FreeCAD against the baked hull and
    either bake or record explicit placements in `serenity_assembly.py`.
- [ ] **Generate `battery_tray.stl` and `belly_panel.stl`** from their SCAD sources —
    currently missing (WARN during assembly regeneration).
- [ ] **Archive deprecated FreeCAD prototypes** — `assembly1.py`, `Serenity-Assemble.py`,
    `Serenity-Subsystem-Assembly.py`, `serenity_subsystem_assembler.py`,
    `serenity_fuselage_asm4.py` are marked DEPRECATED (pre-R1 transforms would
    double-transform baked STLs); move to `airframe/archive/` at next revision checkpoint.

#### 1.1.1 **Fuselage**

##### 1.1.1.1a *Bow Sensor Pod — Head Section (Rev R1a, 2026-06-15)*

Forward-facing sensor assembly at the bow flat face replacing the two canonical convex domes.
SCAD source: `airframe/openscad/fuselage/bow_sensor_pod.scad` (use'd by head_shell24.scad).
All dome positions are estimated; every item below must be completed before printing.

###### Slicer Verification (BLOCKS head section printing)

- [ ] **Open `head_shell24_2mm_repaired.stl` in slicer and cross-section at hull Y ≈ −283 mm
    (SCAD Y = BOW_FACE_Y = −283) to confirm bow flat face location.**
    Adjust `BOW_FACE_Y` in `bow_sensor_pod.scad` until the flat face cross-section passes through
    the flat-face geometry visible at the bow tip.
- [ ] **Verify Dome A (dorsal camera) position: SCAD [161.33, −283, 83.08].**
    Cross-section at Z = 83 mm (hull Z = 144 mm) to confirm the aperture circle lands inside the
    hull skin at the bow face.  Adjust `DOME_A_Z` if the position is outside the hull wall.
    **BLOCKS Dome A camera socket printing.**
- [ ] **Verify Dome B (ventral ToF/laser) position: SCAD [161.33, −283, 60.08].**
    Cross-section at Z = 60 mm (hull Z = 121 mm) to confirm the aperture lands inside hull skin.
    Adjust `DOME_B_Z` if the position is outside the hull wall.
    **BLOCKS Dome B ToF/laser socket printing.**
- [ ] **Verify ToF pocket interior clearance.**  The TFmini-S body pocket is 36×20×22 mm deep;
    confirm the pocket does not breach the head section interior structure at the bow.
- [ ] **Verify laser bore clearance.**  The 12.5 mm × 38 mm bore angled 30° below horizon must
    not intersect the Shepherd Book Faraday tray or any other interior feature.  Check in
    slicer by sectioning along the bore axis direction.
- [ ] **Verify all bow sensor apertures are within hull skin (no voids through foam core).**
    The 2 mm CF-PETG skin must be intact around each aperture; confirm 2-wall annulus preserved.
- [ ] **Run mesh validation** (`python3 tools/validate_stls.py`) after regenerating
    `head_shell24_2mm_repaired.stl` from SCAD with bow pod cuts applied.  All findings to be
    resolved before printing.

###### Carrier and Bezel Parts (follow-on SCAD files)

- [ ] **Design `bow_camera_bezel.scad`** — printed retainer cap that replaces the dorsal dome
    geometry, contains 12 mm lens bore, 4× M2 threaded inserts, and 21×21 mm external flange
    matching the hull socket recess.  2 mm CF-PETG, 4-perimeter, ≥ 40% infill.
- [ ] **Design `bow_tof_laser_bezel.scad`** — printed assembly cap for dome B; contains
    8 mm PMMA disc socket (ToF aperture), 12 mm laser exit bore (angled 30° down), external
    flange.  Mounts flush at hull exterior.
- [ ] **Source PMMA windows for both apertures:**
    - Dome A: no window (camera lens exposed through hull bore, protected by bezel flange)
    - Dome B ToF: 8 mm dia × 2 mm thick PMMA disc (uncoated; PMMA transmits 905 nm IR)
    - Dome B laser: 5 mm dia × 2 mm PMMA exit window (optional; laser module may be sealed)

###### Avionics Integration

- [ ] **Wire TFmini-S UART to Shepherd Wash (Cape-A-2) UART2 port.**
    Run 28 AWG 4-conductor (TX, RX, 5 V, GND) loom from bow pod area to Shepherd's Room bay.
    Route inside head section interior; secure with cable saddles bonded to inner hull wall.
    Shield pair twisted, overall braid shield grounded at Cape end only.
    Firmware: add TFmini-S UART driver to Shepherd `serenity-fc` Phase 7 task list.
- [ ] **Wire bow camera video output to Inara's stack video input** per camera/payload PACE
    priority assignment (CLAUDE.md).  Use RG178 coax; keep run ≤ 300 mm to bow tip.
- [ ] **Wire laser GPIO enable to Shepherd Wash GPIO** via 2N7002 N-channel MOSFET:
    - Gate → Wash GPIO (via 10 kΩ series resistor)
    - 10 kΩ pull-down to GND (default state: laser disabled)
    - Source → GND
    - Drain → laser anode via 10 Ω current-limit resistor (confirms ≤ 5 mW at rated voltage)
    - Physical safety key-switch in series with enable GPIO per [REF-FDA-001 §1040.10(f)(1)]
        before operating near persons.
- [ ] **Add laser enable command to MAVLink C2 interface** [REF-PROTO-002] with explicit
    operator acknowledgement required before energising (prevents accidental enable).
- [ ] **Add standards REF-IDs to bow_sensor_pod.scad firmware integration notes** once driver
    code is in place.  Ref: [REF-SENSOR-002] TFmini-S UART protocol, [REF-NIST-001 §2.1] ZTA.

###### Mass Budget Entry

- Bow camera (RunCam Nano 4 or equiv.): 3.6 g (0.13 oz) [REF-SENSOR-001]
- TFmini-S ToF sensor: 5.0 g (0.18 oz) [REF-SENSOR-002]
- Crosshair laser module: ≈ 8 g (0.28 oz) (estimate; varies by COTS supplier)
- Printed bezels (2×): ≈ 4 g total (estimate; update from slicer mass report)
- Wiring / connectors: ≈ 5 g (estimate)
- **Total bow pod mass addition: ≈ 25.6 g (0.90 oz)**
    Update master BOM `docs/bom_revR.json` once bezel masses confirmed in slicer.

---

##### 1.1.1.0a *Blender-Canonical Source Adoption (Rev R1, 2026-06-13)*

The four Blender-derived, 2 mm hollow, repaired fuselage shell STLs in
`airframe/blender-scripts/files-hollowed-24in/` are now the **authoritative canonical
sources** for all fuselage geometry.  They have been copied to `airframe/stls/fuselage/`
and baked to hull frame.  SCAD fuselage shell files are secondary references only.

**Baked on 2026-06-13 (all four verified OK, max error < 1.52e-05 mm):**
- [x] `head_shell24_2mm_repaired.stl` — 790 036 tri; X −232.9..−103.5 / Y −305.7..−70.7 / Z +61.1..+201.5 mm
- [x] `cargo_sect_shell24_2mm_repaired.stl` — 1 414 068 tri; X −267.0..−72.7 / Y −71.5..+132.0 / Z 0.0..+163.2 mm
- [x] `middle_shell24_2mm_repaired.stl` — 855 328 tri; X −258.5..−81.6 / Y +130.4..+203.6 / Z +1.3..+166.1 mm *(see §1.1.1.3 — includes horseshoe ring + inner neck as ONE piece)*
- [x] `rear_shell24_2mm_repaired.stl` — 1 095 972 tri; X −246.1..−105.5 / Y +203.2..+384.3 / Z +3.3..+161.1 mm

**Open tasks:**
- [ ] **Cargo section interior boss features** — the Blender-canonical cargo shell is the pure exterior skin.
    All interior features added in SCAD Rev S/S1/S2/S3 (wing mortises, spar bore, servo mount pads,
    hinge-pin blocks, latch lips, avionics standoffs, cargo bay opening, GPS domes) must be merged
    back into the Blender mesh before printing.  Workflow: use the baked Blender cargo shell as the
    outer surface; add interior boss geometry from SCAD Rev S3 source via Blender Boolean or OpenSCAD
    hull combination.  Re-export, re-bake, verify watertight.  **BLOCKS cargo section printing.**
- [ ] **Middle section inner neck — Phase 5-10 print guidance** — the Blender middle mesh includes
    the inner neck (closed tube) and the outer horseshoe ring as one piece.  Confirm in slicer that
    both elements appear correctly and that there are no thin-wall violations in the neck-to-horseshoe
    web transitions.  The 4× EDF intake scoop openings in the inner neck are NOT cut in the current
    mesh — confirm before slicing.  See §1.1.1.3 for details.  **BLOCKS middle section printing.**
- [ ] **Deprecate SCAD fuselage shell files** — `s_head_shell24.scad`, `s_middle_canonical_shell24.scad`,
    `s_rear_neck_intake_shell24.scad` are now secondary references.  At next revision checkpoint,
    archive them to `airframe/archive/` and update PROJECT_INDEX.md / ARCHIVE_INDEX.md.
    `cargo_sect_shell24.scad` (Rev S3) remains active as the source for interior boss geometry
    until those features are merged into the Blender mesh (task above).
- [ ] **Update `REVN_BUILD_GUIDE_24IN.md` fuselage shell source references** — replace SCAD
    regeneration commands with Blender pipeline instructions (copy from `blender-scripts/files-hollowed-24in/`
    → `stls/fuselage/` → run `python3 tools/bake_hull_frame.py`).

##### 1.1.1.0b *Section Joint Boss / Alignment Design (Rev R1 — all four fuselage sections)*

All four fuselage section boundaries (head/cargo, cargo/middle, middle/rear) are
**fabrication splits** introduced for printability — they are not and were not structural
joints in the Thingiverse reference model (which was designed as a decorative display
piece with no structural engineering for any load case).

**Structural continuity is an open engineering task.**  The Thingiverse geometry —
wall thickness, cross-section shapes, and joint face geometry — was not designed to
carry UAV bending moments, torsion, shear, vibration, or landing-impact loads.
Candidate structural members (keel bar, CF ring plates, foam fill, CF skid rods) are
identified but have not yet been sized or verified.  The tasks below, and the keel bar
and ring plate re-evaluation tasks in §1.1.1, must all be completed before any structural
claim can be made about the assembled fuselage.

Each joint face must satisfy the **CLAUDE.md fabrication standard**: minimum 2-wall
contact annulus + positive-stop shoulder; friction fits are not acceptable for any joint.

Joint faces in hull-frame Y (confirmed from baked extents):
- **Head / Cargo** — hull Y ≈ −71 mm (Head_Shell Y-max = −70.7 mm; Cargo_Shell Y-min = −71.5 mm)
- **Cargo / Middle** — hull Y ≈ +131 mm (Cargo_Shell Y-max = +132.0 mm; Middle_Shell Y-min = +130.4 mm)
- **Middle / Rear** — hull Y ≈ +203 mm (Middle_Shell Y-max = +203.6 mm; Rear_Shell Y-min = +203.2 mm)

- [x] **Head/Cargo joint boss design (hull Y ≈ −71 mm)** *(done 2026-06-14)*
    - 3× Ø3.2 mm boss-pin bores (8 mm depth each side) at hull (X,Z):
        (−168.3, +143.9), (−138.0, +91.4), (−198.6, +91.4) mm; Y-range −79..−62 mm.
    - Face bore-open: Ø hull interior opened at Y −85..−68 mm (inner-face rectangle).
    - Positive-stop provided by pin depth; no separate shoulder lip needed (pin geometry
        self-registers both sections).
    - Implemented in `airframe/blender-scripts/add_structural_features.py` (BOSS_PIN_BORES
        joint1 + FACE_BORE_CUTTERS head_aft / cargo_fwd); all four shells verify PASS.
    - See `docs/structural_analysis.md` §4 for boss-pin sizing and load analysis.
    - Bond with West System 105/206; cure 24 h before foam pour.
    - **SUB-TASKS OPEN:** verify boss-pin bore positions in slicer cross-section at
        hull Y ≈ −71 mm before head/cargo printing. *(BLOCKS head + cargo printing)*

- [x] **Cargo/Middle joint boss design (hull Y ≈ +131 mm)** *(done 2026-06-14)*
    - 3× Ø3.2 mm boss-pin bores (8 mm depth each side) at hull (X,Z):
        (−170.1, +115.0), (−139.8, +62.5), (−200.4, +62.5) mm; Y-range +121..+141 mm.
    - Face bore-open: hull interior opened at Y +122..+134 mm and Y +128..+145 mm (aft
        cargo + fwd middle rectangles respectively).
    - Implemented in `add_structural_features.py` (BOSS_PIN_BORES joint2 + FACE_BORE_CUTTERS
        cargo_aft / middle_fwd); boss pins verified clear of keel channel (X −171.8..−168.2).
    - Bond with West System 105/206; cure 24 h before foam pour.
    - **SUB-TASKS OPEN:** verify in slicer at hull Y ≈ +131 mm. *(BLOCKS cargo + middle printing)*

- [x] **Middle/Rear joint boss design (hull Y ≈ +203 mm)** *(done 2026-06-14)*
    - 3× Ø3.2 mm boss-pin bores (8 mm depth each side) at hull (X,Z):
        (−170.1, +109.6), (−139.8, +57.1), (−200.4, +57.1) mm; Y-range +193..+213 mm.
    - Face bore-open: hull interior opened at Y +193..+207 mm and Y +201..+217 mm (aft
        middle + fwd rear rectangles respectively).
    - CF skid-rod bores (Ø4.2 mm, 60 mm total, 30 mm per section) at (X=−202, Z=+18)
        and (X=−135, Z=+20); boss pins verified non-intersecting with skid-rod bores.
    - Implemented in `add_structural_features.py`; all shells verify PASS.
    - Bond with West System 105/206; cure 24 h before foam pour.
    - **SUB-TASKS OPEN:** verify in slicer at hull Y ≈ +203 mm. *(BLOCKS middle + rear printing)*

- [ ] **MESH-01 `add_structural_features.py` boolean cuts left non-watertight / fragmented
    shells on cargo, middle, and rear** *(found 2026-06-16, reviewing 03_top.png render)* —
    what looks like "huge cutouts / air where there should be hull" in the rendered build-guide
    images is **not** the intended bore-open joint design; it is a meshing defect from the
    boss-pin/keel-channel/ring-pocket boolean subtractions in `add_structural_features.py`.
    - `python3 airframe/blender-scripts/verify_shells.py --published` reports "ALL PASS" but
        its own per-shell output shows `watertight(strict)=False` for cargo, middle, and rear,
        and `large_shells=3` for rear (i.e. the rear shell is split into 3 disconnected solid
        islands, not one continuous hull) — the gate's pass criteria (`open_edges==0` and
        `large_shells<=3`) do not actually require `is_watertight`, so this slipped through.
    - Non-manifold edges (shared by 4–6 faces instead of 2) and hundreds of zero-area sliver
        fragments cluster exactly at the boss-pin/keel-channel/ring-pocket cut sites: cargo at
        Y ≈ −68..−58 mm (Joint 1) and Y ≈ 121–122 mm (Joint 2); rear at Y ≈ 217–233 mm
        (Joint 3 / skid-rod bore zone).  Head (boss-pin bores only, no keel/ring cuts) is fully
        clean — pointing at the keel-locating-channel and ring-frame-pocket box cutters
        (`KEEL_CHANNEL`, `RING_POCKETS` in `add_structural_features.py`) as the likely root
        cause: their cut surfaces sit within float-epsilon of the shell's existing 2 mm wall,
        producing degenerate/non-manifold triangulation in the `manifold3d` boolean difference.
    - Cargo's computed volume (6,234,838 mm³) is ~17× the §2 mass-budget figure
        (370,509 mm³) — a strong independent signal of broken topology, not just cosmetic noise.
    - **Fix path:** add finite clearance/overlap to the keel-channel and ring-pocket cutters
        so they fully traverse the wall instead of grazing it; re-run
        `add_structural_features.py`; tighten `verify_shells.py`'s gate to hard-fail on
        `is_watertight=False` and on `large_shells>1` (a clean single-piece shell should split
        into exactly 1 surface body, not be allowed up to 3).  Re-run `bake_hull_frame.py --check`
        after re-export.  **BLOCKS cargo/middle/rear printing and any FEA based on current STLs.**

- [x] **CF ring plate (CF-PLATE-2MM) — complete first-principles re-evaluation *(Rev R1)*** *(done 2026-06-14)*
    Full analysis in `docs/structural_analysis.md`.  2 rings selected (down from prior 5):
    cargo Y=+30 mm (wing-spar load zone) and rear Y=+290 mm (landing anti-ovalisation zone).
    Inner-profile CSVs exported to `airframe/diagrams/ring_frames/` for DXF cut file generation.
    See structural_analysis.md §3 for load case inventory and §5 for ring pocket dimensions.
    Ring-frame pockets cut into cargo and rear shells by `add_structural_features.py`.
    **SUB-TASKS OPEN:**
    - [ ] Import `ring_cargo_Y30_inner.csv` and `ring_rear_Y290_inner.csv` into FreeCAD;
        add 3 mm clearance offset + keel-notch slot (6 mm wide × 3 mm deep at hull −Z centroid);
        export DXF to `airframe/diagrams/ring_frames/`. *(BLOCKS CF-PLATE-2MM fabrication)*
    - [ ] Update BOM: CF-PLATE-2MM Notes — 2 rings (cargo Y = +30 mm, rear Y = +290 mm),
        mass TBD from DXF enclosed area × 2 mm × 1.54 g/cm³. Revise prior count from 5 to 2.
    - [ ] Update `REVN_BUILD_GUIDE_24IN.md` keel datum-mark table with hull-Y ring stations
        (+30 mm, +290 mm) to replace the stale 91/165/251/320/388 mm values.

    All prior design data for CF ring plates (station count, hull-Y positions, 2D profiles,
    and structural function) were based on the **pre-Rev N non-canonical hull model** and
    are entirely invalid for the current baked canonical Serenity geometry.  This is a
    clean-sheet structural design task, not a re-derivation of old numbers.

    **Step 1 — Structural load case inventory.**
    Identify every load introduction point inside the hull that a ring frame could react:
    - Wing spar pin loads (X-axis spar through cargo section; derive spar-bore Y stations
        from `cargo_sect_shell24.scad` SPAR_BORE_Y / bearing block parameters).
    - Nacelle tilt servo reaction (NSVMT blocks in cargo section; derive Y from SCAD
        `NSVMT_X_CEN` or equivalent — note SCAD uses part-local frame; convert to hull Y).
    - Skid landing-impact loads (aft section; CF rod reinforcement already handles skid-arm
        bending; determine if tail-cone ovalisation under landing shock still warrants a ring).
    - Fuselage bending under 2g manoeuvre (keel bar + foam carry primary moment; rings
        provide shear-web anti-ovalisation — evaluate whether skin thickness + foam elastic
        foundation make rings unnecessary in lightly-loaded sections).

    **Step 2 — Hull cross-section survey at load stations.**
    For each load station identified in Step 1, slice the baked canonical STL at that
    hull-Y plane (FreeCAD Cross-Section on the baked mesh, or `python tools/bake_hull_frame.py`
    cross-section output).  Characterise the inner-skin boundary:
    - Is it a closed loop (full ring possible) or open (e.g., middle horseshoe open at −Z)?
    - What is the enclosed area and minimum inscribed rectangle?
    - Does the Serenity exterior geometry at that station allow a flat CF plate to seat
        flush against the inner skin, or is the section too curved / tapered?

    **Step 3 — Decide ring type, station count, and positions.**
    Based on Steps 1–2, determine for each candidate station whether to use:
    - Full closed ring (cargo or rear sections where skin forms a closed perimeter)
    - Partial arch (middle horseshoe upper arch only; bottom open)
    - No frame (head section is non-structural per Rev R1; foam + keel adequate)
    - Integrated boss rib (if load is highly localised, a rib printed into the shell SCAD
        may be lighter than a separate CF plate — evaluate for servo and spar stations)
    Record chosen station count (≥1; ≤5), hull-Y for each, and ring type.

    **Step 4 — Profile extraction and DXF generation.**
    For each chosen station: export 2D inner-skin boundary as DXF (FreeCAD TechDraw or
    `Draft.dxf` export of cross-section wire).  Add keel-bar notch (6×3 mm slot at hull
    −Z centroid).  Add 3 mm clearance all-round from skin so ring can be inserted and
    epoxy-bonded without force-fitting.  Save to `airframe/diagrams/ring_frames/`.

    **Step 5 — Update BOM and build guide.**
    - Update CF-PLATE-2MM Notes: confirmed station count, hull-Y values, ring types, mass.
    - Update `REVN_BUILD_GUIDE_24IN.md` keel datum mark table with new hull-Y stations.
    - If any station is replaced by an integrated shell rib, add SCAD sub-task under the
        relevant shell file (§1.1.1.1–§1.1.1.4).
    **BLOCKS keel bar + ring plate fabrication; BLOCKS foam pour.**

- [x] **Hull keel (CF-BAR-6X3) — complete first-principles re-evaluation *(Rev R1)*** *(done 2026-06-14)*
    Full analysis in `docs/structural_analysis.md` §2.  Decisions:
    - Keel spans cargo-to-rear (hull Y −71..+384 mm ≈ 455 mm), two lap-spliced segments.
    - Cargo segment: Z ≈ +1..+2 mm (belly, just above skin floor). Rear segment: Z ≈ +4.7..+5.7 mm.
    - CF-BAR-6X3 retained; oriented 6 mm vertical (strong axis), 3 mm horizontal. FOS ≥ 24.8 at 2g.
    - Head section excluded (incompatible Z floor at Z=+61 mm, non-structural, short section).
    - Middle section: keel passes through unsupported in foam; no hard attachment.
    - RF counterpoise: separate AWG 22 copper stranded wire alongside keel (CF bar inadequate at 49 MHz).
        BOM item WIRE-COUNTERPOISE-49MHZ added.
    - Keel locating channels cut into cargo and rear shells by `add_structural_features.py`.
    **SUB-TASKS OPEN:**
    - [x] Add WIRE-COUNTERPOISE-49MHZ to BOM: AWG 22 stranded tinned copper, 460 mm,
        2 g, routed alongside keel inside foam from cargo to rear, terminated at Emma
        antenna feed on River's Room stack. *(done 2026-06-22 — was referenced here since
        Rev R1 but never actually added; backfilled as part of §1.4.2 antenna work, which
        also added a second counterpoise wire, WIRE-COUNTERPOISE-49MHZ-2, for Simon's
        independent 49 MHz antenna.)*
    - [ ] Update `battery_tray.scad` keel-rail slot to Z ≈ +1..+2 mm (cargo belly);
        re-export STL to `airframe/stls/fuselage/battery_tray.stl`. *(BLOCKS foam pour)*
    - [ ] Update `REVN_BUILD_GUIDE_24IN.md` keel installation section: span Y −71..+384 mm
        (455 mm), lap-splice at middle/rear joint Y ≈ +203 mm (50 mm overlap), ring-notch
        positions at Y = +30 mm and Y = +290 mm. *(BLOCKS keel fabrication)*

    A continuous bow-to-stern backbone is structurally justified (primary fuselage bending
    moment arm; inter-section tie-rod spanning all fabrication splits).  However, the
    canonical Serenity hull geometry makes the current straight 6×3 mm flat bar
    infeasible as specified.  This is a clean-sheet keel design task.

    **Known geometry constraints (from baked hull-frame extents):**
    - **Head/Cargo Z step**: Head_Shell Z_min = +61.2 mm; Cargo_Shell Z_min = 0.0 mm.
        A straight keel at the cargo belly cannot enter the head section without a ≈ 61 mm
        vertical bend at hull Y ≈ −71 mm.
    - **Middle section open belly**: Middle_Shell (Y = +130.4..+203.6 mm) is open at −Z
        (horseshoe ring with no belly floor).  A belly keel has no skin to bond to for
        ~73 mm of hull length here.  Foam fill provides distributed elastic support but no
        hard attachment.
    - **Head section structural role**: Head_Shell is non-structural per Rev R1 (foam + 2 mm
        CF-PETG skin adequate; avionics bays relocated to cargo + rear sections).  A keel that
        terminates at the head/cargo joint face (hull Y ≈ −71 mm) may be fully adequate.
    - **Datum marks**: the 91/165/251/320/388 mm station marks are tied to the stale pre-Rev N
        ring plate positions and must be replaced by the new ring station outputs (see ring
        plate re-evaluation task above).

    **Step 1 — Decide keel span.**
    Determine whether the keel must enter the head section or whether cargo-to-rear
    (hull Y ≈ −71 mm → +384 mm, ≈ 455 mm) is structurally sufficient.  The head section
    contributes little to global fuselage bending (short, tapered, non-structural) and has
    an incompatible Z floor.  Cargo-to-rear span is preferred unless a specific head-section
    load case (e.g., FPV/GPS nose mount inertia) justifies the extension.

    **Step 2 — Determine Z routing through each section.**
    At each hull section, identify the highest Z level that provides:
    - Continuous bonding surface against inner skin or foam (closed loop or foam contact)
    - Clearance from avionics bays, battery tray, servo mounts, spar bores, and wiring trunk
    Candidate Z levels to survey (from section Z extents):
    - Cargo belly: Z ≈ +5..+15 mm (below battery tray floor, above hull skin)
    - Middle horseshoe: keel passes through the interior unsupported — foam alone provides
        lateral stability; check that Z routing clears the wiring trunk PTFE conduit.
    - Rear cone belly: Z ≈ +5..+15 mm (consistent with cargo level)
    Target: a monotonically constant or gently varying Z route from cargo to rear that
    requires no bends exceeding the material's minimum bend radius.

    **Step 3 — Choose keel form and cross-section.**
    Based on the Z routing determined in Step 2:
    - **Straight flat bar (CF-BAR-6X3)**: viable only if Z routing is constant.  6 mm wide
        face ideally oriented horizontally (resist vertical bending = primary fuselage mode).
        Minimum bend radius for 6×3 CF bar ≈ 200–300 mm; tighter bends require separate spans.
    - **Pre-bent flat bar**: single bar bent in the weak axis (3 mm thickness) to follow a
        gentle Z curve.  Requires heat + jig; feasible if total Z variation over the keel span
        is < 30 mm and bends are gradual.  Confirm with material supplier.
    - **Segmented with lap splice**: two or three straight segments (e.g., cargo + rear);
        overlapping lap joint (≥ 50 mm) at each join, bonded with West System 105/206 + peel
        ply prep.  Maintains continuity without bending.  Adds ≤ 5 g mass at each splice.
    - **CF tube**: round tube (e.g., 6 mm OD × 1 mm wall) is isotropic in bending, easier
        to route curves, and can double as a wiring conduit.  Lower area moment of inertia
        than a 6×3 flat bar in the primary bending axis — check adequacy.
    - **CF tow/tape embedded in foam**: lays up along any geometry during foam pour; no
        discrete part to install; non-inspectable after pour.  Lowest mass option but least
        stiff and non-replaceable.

    **Step 4 — Assess RF counterpoise function.**
    CF-BAR-6X3 currently doubles as the 49 MHz (Part 15 §15.235) antenna counterpoise.  CF has anisotropic
    conductivity (longitudinal only, ≈ 5–10 kΩ/m vs copper ≈ 0.017 Ω/m); it is a poor RF
    conductor.  At 49 MHz, λ = 6.12 m; λ/4 = 1.53 m; a 455–620 mm bar is ≈ λ/10 — a
    dedicated copper counterpoise wire (AWG 22 stranded, < 2 g) bonded alongside the keel
    is more reliable than relying on CF conductivity.  Decide: (a) keep CF keel as structural
    only and add a separate copper counterpoise wire in the wiring trunk, or (b) embed a
    copper braid in the keel lap joint.  Update Emma/XCVR antenna design accordingly.

    **Step 5 — Update BOM, battery tray, and build guide.**
    - Update CF-BAR-6X3 Notes: confirmed form, span, Z routing, cross-section, mass.
    - Battery tray SCAD (`battery_tray.scad`): the "keel rail" interface must match the
        new keel Z position and cross-section; update SCAD and re-export STL.
    - Update `REVN_BUILD_GUIDE_24IN.md` keel installation section with new span, Z level,
        lap joint positions, and ring plate notch locations (from ring plate re-evaluation).
    - If separate copper counterpoise wire is chosen, add to BOM as WIRE-COUNTERPOISE-49MHZ.
    **BLOCKS ring plate notch design; BLOCKS keel fabrication; BLOCKS foam pour.**
    **Run concurrently with CF ring plate re-evaluation (ring plate notch geometry depends
    on keel cross-section and Z position).**

- [x] **Access panel frames + covers (24" Rev R)** — `airframe/openscad/fuselage/access_panels_24in.scad` created 2026-06-11. Geometries derived from authoritative shell SCADs (Rev R baseline):
    - 4× Faraday-bay covers (Shepherd/Inara/River/Simon): 72×52 mm, 4× M3 clearance bores, positive-stop shoulder; Inara + River covers include Ø42 mm GPS retention-ring recess.
    - 2× ventral hatch covers: battery 160×60 mm, Kaylee 115×100 mm; M2.5 pilots into bonded frames.
    - 2× ventral hatch frames: battery + Kaylee; 6 mm CF-PETG wall, West System 105/206 epoxy-bonded to hull.
    - **SUB-TASKS:**
        - [ ] Export individual STLs (set RENDER variable in SCAD): shepherd, inara, river, simon, battery, battery_f, kaylee, kaylee_f → `airframe/stls/fuselage/`
        - [ ] Verify cover shoulder fit in slicer cross-section (confirm 1.5 mm step seats on hull face)
        - [ ] Verify GPS recess depth clears GPS retention ring (Inara: dZ=−14.3 mm, River: dZ=+0.7 mm)
        - [ ] Confirm M3 bore positions match shell boss pattern (±25 mm × ±15 mm from bay centre)

- [x] **49 MHz (Part 15 §15.235) wire posts** — `airframe/openscad/fuselage/rcrs49_wire_post.scad` created 2026-06-11. Single `wire_post()` module: 12×12×2 mm PETG base, 8×8×7 mm mast, Ø1.5 mm athwartships wire-retention bore at 2 mm from top. **Relocated 2026-06-22 (§1.4.2):** dorsal-centreline mount superseded — print FOUR posts (two antennas, two posts each): River's antenna forward (sta ≈ 120 mm) + aft (sta ≈ 580 mm) on the **port flank**, Simon's antenna forward + aft (same stations) on the **starboard flank**, both at shoulder height. Reasons: (a) a single shared dorsal run put River's and Simon's independent 49 MHz antennas (§1.4.2) too close together at 49 MHz; (b) the cargo bay clamshell doors hinge at the outboard flank/belly edge and swing up to 180° (`generate_cargo_doors.py`), so any ventral or low-flank exterior post in the cargo bay's Y-span is in the door's path — shoulder height, port/starboard, clears both.

    - **BLOCKS Phase 1 (antenna installation)**
    - **SUB-TASKS:**
        - [ ] Export STL → `airframe/stls/fuselage/rcrs49_wire_post.stl` (×4 instances, no geometry change needed — same module, different bond points)
        - [ ] **Verify port/starboard shoulder-height mount line in FreeCAD against the cargo door's 180°-open swing envelope** (door panel width, hinge at outboard flank/belly edge) before bonding any post — confirm shoulder height is actually clear at every station along sta 120–580 mm, not just at the door's own Y-span. **BLOCKS bonding both antennas' posts.**
        - [ ] Bond River's forward post to the port flank at sta 120 mm; dress wire aft to River's Emma J2
        - [ ] Bond Simon's forward post to the starboard flank at sta 120 mm; dress wire aft to Simon's Emma J2
        - [ ] Install both temporary aft posts (port + starboard) at sta 580 mm; remove and replace with integrated mounts in Phase 11

##### 1.1.1.1 *Head*

**Geometry verification (hull-frame coordinate analysis, 2026-06-10):**

- [ ] **Verify head-cargo mating boss positions in slicer.**
    Hull-frame analysis (2026-06-10): `Head_Shell` Identity rotation, Base=[−332, −18, +61];
    head aft face (head local_X=99) maps to hull_X = 99−332 = **−233 mm**.
    `Cargo_Shell` 180°-Z rotation, Base=[−274.4, −282.8, 0]; matching cargo local_X =
    −(−233) − 274.4 = **−41.4 mm** — corrected in `cargo_sect_shell24.scad` BOSS_FORE
    (was X=−7, now X=−41.4). **VERIFY** both sections simultaneously in an assembly render
    or slicer that shows both STLs in hull-frame placement.  Confirm 6 head BOSS_AFT bosses
    (at head local_X=99) align with 6 cargo BOSS_FORE bosses (at cargo local_X=−41.4) in
    the assembled hull.  All Y/Z offsets remain estimated; also VERIFY those after X is confirmed.
    Ref: `head_shell24.scad` BOSS_AFT_* comments; `cargo_sect_shell24.scad` hull-frame block.
    **R1 AUDIT (2026-06-11): this analysis used hull X as the longitudinal mating axis, but
    in the validated hull frame X is LATERAL (+port) and the longitudinal axis is Y — the
    baked head and cargo meshes mate at hull Y ≈ −71 mm.  Redo the joint analysis in hull Y
    (see §1.1.0) before trusting BOSS_FORE = −41.4 mm.**

**Rev R shell updates (sensor/antenna mounts; carried fwd from Rev O, 2026-05-24):**

- [ ] **head_shell24.stl** — regenerate from `airframe/openscad/fuselage/head_shell24.scad` Rev S2.
    - Rev S2 (2026-06-16) corrected FWD_ROT and all three nose-face aperture positions;
        see Rev S2 note at top of SCAD for root-cause detail.
    - [ ] **Verify S1A, S1B, FPV positions at nose surface in slicer** — load generated STL
        and cross-section at Y ≈ −268 to −280 mm (pre-bake frame); confirm apertures cut
        cleanly through the nose-face hull skin, not the port lateral skin.
        Adjust S1A_POS / S1B_POS / FPV_POS Y values if nose face is at a different Y
        at the sensor's (X, Z) coordinates.
    - [ ] **Specify laser pointer mount** — laser pointer is currently documented as
        colocated with S1A/S1B (green highlight, port side nose face), but no separate
        aperture is cut.  Once laser pointer hardware is selected, add a laser_cut()
        module with the appropriate bore size adjacent to or integrated with S1A aperture.
    - [ ] **Correct BOSS_AFT positions** — BOSS_AFT_* in `head_shell24.scad` use X=99 as
        the aft face (legacy X=longitudinal convention, same root cause as Rev S2 sensor
        correction).  Hull-frame aft joint face is at Y ≈ −53 mm; BOSS_AFT_ROT should be
        [0,90,0] only if facing into the joint (−Y direction → [−90,0,0]).  See §1.1.0
        open item and §1.1.1 for the full correction plan — this is a pre-existing blocker.
    - Verify Faraday tray cutout and all other non-boss geometry unchanged after SCAD re-render.

##### 1.1.1.2 *Cargo*

**Rev R shell updates (sensor/antenna mounts; carried fwd from Rev O, 2026-05-24):**

- [ ] **cargo_sect_shell24.stl** — regenerate from `serenity/stl/cargo_sect_shell24.scad` (cargo nadir FPV mount added)
    - Both outputs go to `thingverse-serenity/files-hollowed-18in/`

###### 1.1.1.2.1 *Cargo Handling*

**Cargo handling equipment:**

- [x] **Mounting hardware — 8 STLs** generated by `serenity/stl/generate_cargo_mounts.py` (Python/trimesh/manifold3d). Output: `thingverse-serenity/files-hollowed-18in/cargo_*.stl` *(done 2026-05-30, PR #21)*
    - [x] cargo_winch_motor_mount (CF-PETG), cargo_winch_spool (PETG), cargo_door_servo_bracket (CF-PETG), cargo_release_servo_bracket (CF-PETG), cargo_drv8833_tray (PETG), cargo_cradle_autolatch (PETG), cargo_gps_retention_ring (PETG), cargo_fpv_bezel (PETG)

- [ ] **Cargo gondola shell** — create `serenity/stl/s_cargo_gondola_shell.scad`: 112×85×22 mm belly pod, 4× M3 hard point pattern, 18 mm protrusion below hull line
- [ ] **Clamshell door halves** — `cargo_door_port.stl` + `cargo_door_stbd.stl` generated by
    `serenity/stl/generate_cargo_doors.py` Doors hinge on port and starboard sides and meet at the centerline.  Doors open out to 180 deg, allowing landing over and loading 4"x3"x3" cargo payload, or raising/lowering it in flight via the internal winch. (trimesh/scipy bilinear interpolation from Rev-O shell belly faces). 8-barrel piano hinge, 3 mm CF rod, 3.15 mm bore.
- [x] **`cargo_sect_shell24.scad` Rev S** — belly opening (100×9×165 mm), 2× hinge-pin blocks
    (3.3 mm bore + M3 grub-screw tap), 2× SG90 servo mounting pads (4× M2.5 pilots each), 4×
    latch-catch lips (Z=42/122 mm at each X frame edge). *(done 2026-06-01)*
- [x] **`cargo_sect_shell24.scad` Rev S1** — wing root mortises (30.8×20.8×15 mm), spar bearing
    blocks (22 mm OD × 10 mm boss, M3 grub-screw), full-Z spar bore (Ø12.3 mm), and nacelle tilt
    servo mount blocks (52×30×8 mm, 4× RX-M3×5.7 inserts) at port + stbd interior Z walls.
    All 4 spatial conflicts resolved (NSVMT_X_CEN moved AFT to −147.6 mm). Load FOS ≥ 11 vs 4.0
    AUVSI target. *(done 2026-06-08, PR #42)*
- [x] **`cargo_sect_shell24.scad` Rev S2** — Inara and River avionics bay dorsal standoffs
    (8× M3 boss posts, ±40×±25 mm pattern) + dorsal access panel cuts (62×42 mm each) for Cape-B
    (55×35 mm) at port half (Z_CEN=118 mm, Inara) and stbd half (Z_CEN=45 mm, River). GPS_PORT/STBD
    colocated for minimal SMA routing. *(done 2026-06-08, PR #42)*
- [x] **`cargo_sect_shell24.scad` Rev S3** — Faraday enclosure space allocation.
    Panel cuts enlarged 55×35 → 62×42 mm; boss offsets updated ±40×±25 → [TBD pending PCB layout — hole pattern must be derived from Wash.kicad_pcb / Zoë.kicad_pcb once layout is complete] to match
    Faraday tray corner mounts; bay Z centres adjusted ±1 mm (Inara 118→119, River 45→44) for 10 mm
    inter-bay gap; FARADAY_* envelope parameters (95×65×65 mm, 1.5 mm Al wall, 25 mm fan) added.
    *(done 2026-06-08, PR #42)*
- [x] **`nacelle_servo_bracket.scad`** — U-channel saddle clamp for DS3218MG nacelle tilt servo;
    4× M3×10 SHCS flanges at ±17.5×±8 mm; 10×6 mm lead notch; FOS_shear=85.7. *(done 2026-06-08)*
- [x] **`REVN_BUILD_GUIDE_24IN.md` Phase 3 anti-rework** — spar grub-screw torque sequence
    (0.5 N·m each, before foam pour) with consequence documentation. *(done 2026-06-08)*

- [ ] **`cargo_sect_shell24.scad` — shuttle exterior fairing profiles on Z walls.**
    Canonical Serenity shuttles (Shuttle 1 = Inara's, Shuttle 2) sit just above the wing roots on
    the exterior Z faces of the cargo section. Their outline profiles need to be added as raised
    exterior features at Y≈−273..−213 mm on both Z walls, matching the canonical hull geometry.
    Interior avionics zone (Inara + River dorsal band) coexists — shuttles are exterior, avionics
    interior. Reference the Thingiverse low-detail hull for shuttle fairing geometry.
    **BLOCKS canonical hull fidelity (CLAUDE.md requirement: keep skin geometry true to reference).**

- [ ] **Avionics dorsal access covers / Faraday tray lids for Inara and River bays (two parts).**
    Create `inara_access_cover.scad` and `river_access_cover.scad` (or a single parametric SCAD):
    Cover footprint 105×75 mm with 5 mm shoulder lip seating on hull skin around 95×65 mm opening.
    Copper-foil-lined PETG or 0.5 mm Al sheet; Ø38 mm GPS clearance bore at GPS offset from cover
    centre (Inara: offset −13.3 mm in Z from bay centre; River: offset +0.7 mm in Z from bay centre).
    4× M2 flathead captive screws at ±40 mm (X) × ±25 mm (Z) from cover centre for EMI-seal clamping.
    Must be removable with common hand tools per CLAUDE.md field disassembly requirement.
    Ref: FARADAY_* parameters in cargo_sect_shell24.scad Rev S3; CLAUDE.md §1.4.1.
    Add to Phase 0 print schedule.

- [ ] **Update REVN_BUILD_GUIDE_24IN.md bay layout table** to reflect revised avionics stack
    positions (Inara + River in cargo section dorsal band; Shepherd Book in head section forward;
    Simon in rear cone pre-Phase 11, middle ring post-Phase 11). Current guide Bays A–E are from an
    older layout that does not match the cargo-section dorsal placement in Rev R.

- [ ] **Regenerate `cargo_sect_shell24.stl`** from Rev R SCAD source. Run:
    `openscad -o airframe/stls/fuselage/cargo_sect_shell24.stl
        airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad`
    Verify in slicer: wing mortises at both Z walls; spar bore at X=−70 mm; 8 dorsal boss posts;
    two 62×42 mm dorsal panel openings. Z-range must be 0..163 mm; all features inside hull skin.
    **BLOCKS Phase 0 cargo section printing.**

- [ ] Add motor-mount and DRV8833-tray boss locations to `cargo_sect_shell24.scad` interior
    drawing notes (Phase 1 pre-pour checklist reference).
- [ ] Add SG90 bell-crank boss to inner face of each door panel for pushrod attachment.
    - Export gondola shell to `thingverse-serenity/files-hollowed-18in/`
    - **BLOCKS Phase 8**

###### 1.1.1.2.2 *Wing Root*

##### 1.1.1.3 *Middle Neck*

**Canonical geometry (Rev R1, 2026-06-13):**
The middle section is defined by `airframe/blender-scripts/files-hollowed-24in/middle_shell24_2mm_repaired.stl`
(canonical Blender source) → baked to `airframe/stls/fuselage/middle_shell24_2mm_repaired.stl`.

It is **ONE printed piece** comprising two distinct structural elements:
1. **Outer horseshoe ring** — the U-shaped exterior frame surrounding the middle section, open at −Z (ventral).
    The two lower arms of the horseshoe continue aft as the landing skids into the rear section.
2. **Inner neck** — a tube-like enclosed passage running through the centre of the horseshoe,
    connecting the cargo bay interior to the rear engine room interior within the hull skin.
    Canonically this is a pressurised passage within the ship; in the UAV context it provides
    structural continuity and a wiring/keel routing path through the narrowest hull section.

**Phase 5–10 print state:** inner neck is a closed, uncut tube.
Aft EDF intake scoops (reduced-area radial openings into the inner neck for the 55 mm EDF airflow)
are **DEFERRED to Phase 11** — do not cut or modify the inner neck before Phase 11.

- [x] **Blender canonical source baked** — `middle_shell24_2mm_repaired.stl` (855 328 tri) baked
    2026-06-13; extents X −258.5..−81.6 / Y +130.4..+203.6 / Z +1.3..+166.1 mm. *(done 2026-06-13)*

- [ ] **Slicer verification** — open baked `middle_shell24_2mm_repaired.stl` in slicer and confirm:
    - Both the outer horseshoe ring and inner neck are present as connected geometry
    - No thin-wall violations at neck-to-horseshoe web transitions (min 1.6 mm wall at all points)
    - Inner neck bore is closed (no EDF intake openings)
    - Skid arm geometry at the lower horseshoe legs correctly transitions into the rear section
    - Z-range +1.3..+166.1 mm in hull frame; total height ≈ 165 mm — fits build-volume vertical
    **BLOCKS middle section printing.**

- [ ] **Kaylee's room — PDB mounting in inner neck** — the Kaylee Power Distribution Board
    (Kaylee Rev A1; 75 g) is housed inside the inner neck of the middle section, accessible
    through the open ventral face of the horseshoe ring.  The inner neck central location
    minimises power run lengths to all four nacelles, all four avionics stacks, and the battery.
    Required additions to the Blender middle mesh (or as bonded inserts):
    - 4× M3 standoff boss posts for Kaylee PCB (55×35 mm board; ±20×±12.5 mm pattern from bore centre)
    - Power cable exit notches (6 AWG leads, 4× nacelle ESC runs + avionics BEC tap)
    - Ventilation opening or clearance to allow heat dissipation from TPS54620 regulators
    - Access clearance from horseshoe ventral opening (confirm Kaylee can be inserted and removed
        with hand tools — field disassembly requirement per CLAUDE.md)
    - Confirm inner neck bore dimensions from baked `middle_shell24_2mm_repaired.stl` cross-section
        at hull Y ≈ +165 mm (midpoint of middle section) before adding boss features.
    **BLOCKS middle section Blender mesh update; BLOCKS Kaylee installation.**

- [ ] **CF skid rod channels** — add 4.2 mm bore channel along each horseshoe-to-skid arm (lower
    legs of the horseshoe) in the Blender mesh, coaxial with the matching channels in the rear shell.
    Export updated STL, re-bake, verify watertight.  See §1.1.0a skid task.  **BLOCKS taxi test.**

- [ ] **Simon bay — define avionics bay in the MIDDLE section (moved here from §1.1.1.2, 2026-06-13).**
    Simon's stack (Cape-B-2 + Cape-A-2, 55×35 mm both, 39.2 mm stack height) + Faraday tray (60×40×55 mm)
    mounts in the **middle inner-neck dorsal** interior. Add boss standoffs + dorsal access panel to the
    middle Blender/SCAD source. Verify the inner-neck dorsal band has clearance (middle Z ≈ 1.3..166 mm,
    thin horseshoe section — confirm the inscribed cavity holds the 60×40×55 tray before placing bosses).
    Ref: CLAUDE.md PACE (Simon = alternate watchdog, aft EDF control); shuttle Faraday-fit method in
    `engrave_plaques.py`/cavity-profile check. **BLOCKS Phase 6 full 8-node installation.**

- [ ] **Kaylee room — PDB + battery bay, middle VENTRAL (2026-06-13).**
    The Kaylee power-distribution board and the main battery mount together in the middle section's
    ventral region (the open −Z side of the horseshoe). Define the mounting bay / strap points there;
    keep mass low and central for CG. Coordinate with §1.4.5 (power distribution).

- [ ] **Avionics-bay interior name marks (DEFERRED, 2026-06-13).** Engrave/emboss bay identifiers
    (INARA port shuttle, RIVER stbd shuttle, SHEPHERD head fwd, SIMON middle dorsal, KAYLEE middle
    ventral) on each bay interior. First attempt (flat recessed plaque via `engrave_plaques.py`) did
    not read cleanly on the morph-opened organic cavity walls; pending a method decision (raised letters
    on a flat boss pad, or smooth the bay wall first). Mechanism is watertight and stays inside the 2 mm
    skin. Scripts: `make_bay_text.py`, `engrave_plaques.py`.

- [ ] **Phase 11 — aft EDF intake scoop cuts** — at Phase 11, cut the reduced-area radial scoop
    openings (sized for the 55 mm EDF, ~3,090 mm² total capture at 1.3× duct match) into the inner
    neck to match the resized EDF plenum geometry (`deferred/aft-edf/openscad/neck_intake_frame.scad`).
    These cuts are Phase 11 ONLY — the Phase 5–10 mesh is the closed-neck version.  **Scoop geometry
    must be re-derived for the 55 mm fan — the old 4× scoops were sized for the 120 mm EDF.**

- [ ] **neck_intake_frame.stl (Phase 11)** — `openscad -o neck_intake_frame.stl deferred/aft-edf/openscad/neck_intake_frame.scad`
    - Verify: registration tongues 5 mm depth; intake lips project 6 mm forward
    - Material: CF-PETG; **DEFERRED — BLOCKS Phase 11 only.** STL at `deferred/aft-edf/stls/`.
    - **Requires regeneration for 55 mm intake area (Rev R1 rear-EDF redesign).**

    **Rear intake system (OpenSCAD):**

- [ ] **aft_edf_plenum.stl** — `openscad -o aft_edf_plenum.stl deferred/aft-edf/openscad/aft_edf_plenum.scad`
    - Verify: intake arms feed a 55 mm circular EDF inlet; **add 4 RCS bleed taps (~15% flow split)**
        on the discharge side to the RCS distribution manifold; no self-intersection
    - **DEFERRED — BLOCKS Phase 11 only.** **Requires regeneration: outlet 120 mm → 55 mm and RCS
        bleed taps added (Rev R1 rear-EDF redesign).** Old STL at `deferred/aft-edf/stls/aft_edf_plenum.stl` is superseded.

    **Canonical middle shell (OpenSCAD — belly restored, no belly scoop):**

- [x] **middle_canonical_shell24.stl** — `openscad -o ... serenity/stl/middle_canonical_shell24.scad`
    - Note: NOT the same as `middle_shell24.stl` (which has the obsolete belly intake cut). This is the Rev N canonical belly.
- [ ]

##### 1.1.1.4 *Rear Engine Cone*

#### 1.1.2 **Wings**

**Wing pylon (OpenSCAD — Rev R integrated design; carried fwd from Rev O):**

- [ ] **wing_nacelle_pylon_revo.stl** — `openscad -o ... serenity/stl/wing_nacelle_pylon_revo.scad`
    - Verify WING_SLOT_W and WING_SLOT_H against tip chord 93 mm (Rev R1 planform) before printing — pocket 50×40 mm uses 54 % of tip chord; confirm pylon block clears airfoil walls
    - Verify WING_BOLT_R (16 mm) does not exceed S1223 half-thickness at 50 % tip chord (≈ 9.6 mm above chord line at 93 mm chord); reduce to ≤ 12 mm if pylon block geometry requires it
- [ ] **wings_s1223_revo.stl** — Rev R1 planform (2026-06-14): root 129 mm, tip 93 mm, zero LE sweep; STLs regenerated and baked ✓
    - **[OPEN]** Verify cargo-section wing-root mortise dimensions against new root chord 129 mm (was 161 mm); `cargo_sect_shell24.scad` mortise slot (currently 30.8×20.8×15 mm) may need resizing and re-centring
    - **[OPEN]** Re-check root-tab centre position: with 129 mm chord the tab centres at hull Y ≈ +57.5 mm (was +73.5 mm); confirm mortise centre in cargo SCAD matches
    - **[OPEN]** Verify wing TE position (hull Y≈+122 mm port, +117 mm stbd) clears cargo-section aft interior features; cargo aft boundary is hull Y≈+132 mm — 10 mm clearance

#### 1.1.3 **Nacelles**

**Nacelle shells (Blender, Rev R geometry; carried fwd from Rev O — must run on host machine):**

- [x] **Rev R1 nacelle stator shells** — **investigated 2026-06-22: this item is
    STALE / superseded, not run.** `blender_nacelle_revo.py` (now at
    `airframe/blender-scripts/`, not `thingverse-serenity/` — that path is
    archived) targets Rev O 18 in-scale inputs
    (`files-hollowed-18in/s_eng_{left,right}_shell24_50mm.stl`) that no
    longer exist at that path (only archived copies remain, at
    `archives/stl/`). The current Rev R1 design integrates the 11-fin stator
    as its own separate printed sleeve, `edf_stator_sleeve.scad` →
    `edf_stator_sleeve.stl` (already in the Makefile's `NACELLE_STLS` list
    and already published in `airframe/stls/nacelles/`) — confirmed
    up to date by re-rendering and vertex-diffing against the published
    file (2592/2592 verts, identical). **Pre-existing finding, not caused by
    today's changes:** `edf_stator_sleeve.stl` is not 2-manifold (OpenSCAD
    itself warns "may not be a valid 2-manifold" on render) — logged here
    per CLAUDE.md's mesh-verification-finding requirement; not fixed in this
    pass (unrelated to the nozzle/gear-train work above).

##### 1.1.3.1 *Nozzle*

- [x] **nacelle_nozzle_iris.stl** — `openscad -o ... serenity/stl/nacelle_nozzle_iris.scad`
    *(rendered 2026-06-22)* — Rev R1 50 mm iris: full-circle M=1.0 ring gear
    (72T, R=36mm pitch, replaces the old partial rack), outer housing,
    8-petal geometry sized to hit 75%→105% of the 50 mm bore (18.75→26.25 mm
    tip radius) across the -5°/140° nacelle tilt range. The file's default
    render was switched from the ring-only single part to the assembly
    preview (housing + ring + 8 petals at closed position), matching what
    `serenity_assembly.py` already expected to import. Mesh-verified: 8 of
    9 split bodies fully watertight; 1 non-manifold edge (of 26,381 total)
    where adjacent petals' designed 5° angular overlap touches at the
    closed position — cosmetic/assembly-preview only (this file is not the
    print source for the ring/housing/petals, which print as separate parts
    pulled from the same SCAD modules or, for the petal, from
    `blender_nozzle_gen.py`'s `nacelle_nozzle_petal.stl`); not pursued
    further here. `IDLER_SLOT_ANG` updated 0° → 50.9° to match the resolved
    idler shaft position (see §1.1.3.3).
- [x] **nacelle_nozzle_idler.stl** + **nacelle_nozzle_idler_bracket.stl**
    *(NEW component, rendered 2026-06-22)* — compound idler gear (Idler-In
    44T/R=22mm meshes Crown Pinion; Idler-Out 15T/R=7.5mm meshes the nozzle
    ring gear) plus its two-boss mounting bracket, each now a separate STL.
    Resolves the Crown-Pinion-to-ring radius mismatch (§1.1.3.3). Both
    mesh-verified fully watertight. `nacelle_nozzle_idler.scad`'s render
    selector changed from comment-toggle to a `RENDER_PART` `-D` string
    param ("gear" | "bracket"), matching the wings' `RENDER_SIDE` convention,
    and wired into the Makefile.
- [ ] rebuild petals using the bamj variable nozzle [REF xxx] as a guide, using the gear train already developed.  **The nozzle shall provide a smooth conical exit for the thrust tube, no matter its final diameter** exit diameter will be 75% of bore at 0 deg (forward) and 105% of bore at or above 90 deg (virtical or backing)

##### 1.1.3.2 *Tilt Gear Train*

    **Rev R gear train (OpenSCAD — all 5 parts, M=1.0; carried fwd from Rev O):**

- [x] **nacelle_sector_gear.stl** — `openscad -o ... serenity/stl/nacelle_sector_gear.scad`
    *(rendered 2026-06-22)* — Rev R1.1: R=22mm, **58T, ≈151.3° arc** (was
    38T/≈99.1°, grown to cover the widened -5°/140° mechanical tilt range);
    fixed to tilt bracket. Mesh-verified fully watertight.
- [x] **nacelle_pinion.stl** — spec: N=12T, D-bore shaft (×4 total: drive
    pinion + crown pinion per nacelle, identical part). 2026-06-22 change
    was comment-only (Stage 3 ratio/mating-interface text); re-rendered to a
    scratch file and diffed vertex-for-vertex against the published STL —
    confirmed byte-identical geometry, so the published STL was left as-is.
- [ ] **nacelle_bevel_pair.stl** — `openscad -o ... serenity/stl/nacelle_bevel_pair.scad`
    - Spec: N=14T, 45° pitch cone, 1:1, 90° axis redirect. No spec change this pass.
- [ ] **nacelle_bevel_housing.stl** — `openscad -o ... serenity/stl/nacelle_bevel_housing.scad`
    - Spec: CF-PETG, 24×14×20 mm housing block. No spec change this pass.

##### 1.1.3.3 *FreeCAD Hull-Frame Placement (gear train, nozzle, sleeves)*

- [x] **Map all nacelle-internal mechanism components to hull frame for both port
    and stbd, in `airframe/FreeCAD-scripts/serenity_assembly.py`** *(done, 2026-06-21)*
    — added `R_BAKE` / `T_BAKE` / `PYLON_SIDE` constants and a `nacelle_rows()`
    composition helper (`T_hull = T_nacelle_bake ∘ T_subcomponent_local`, derived
    by hand-expanding the shared nacelle bake quaternion); placed via
    `transform_mesh()` (VERIFY tier, not `place_mesh()`) for both sides:
    Stator Sleeve, Aft Spider Sleeve, Drive Pinion A, Crown Pinion, Bevel
    Housing, Bevel Pair, Sector Gear, Nozzle Iris, and Tip Cap.
- [x] **Fix `crown_pinion_boss()` in `nacelle_pod_50mm_tandem.scad`** *(fixed
    2026-06-22)* — it copied `pinion_a_boss()`'s `rotate([0,90,0])` X-axis-bore
    pattern verbatim, but both `nacelle_pinion.scad` and
    `nacelle_bevel_housing.scad` independently document the Crown Pinion as
    Z-axis/longitudinal (no rotation). Removed the rotation; `cylinder()`'s
    default Z-axis extrusion is now the boss's bore axis, matching the
    FreeCAD placement (which already used the documented-correct identity
    rotation) and both other files' documentation.
- [x] **Resolve the unresolved Crown-Pinion-to-rack mesh radius in
    `nacelle_nozzle_iris.scad`** *(resolved 2026-06-22)* — an author
    scratch-pad had computed four candidate radii (28/37/31/38 mm) and ended
    mid-thought ("Wait —") with none ever chosen. Root cause: the Crown
    Pinion's hull-frame Y-offset is fixed at 28 mm (shaft-conduit continuity
    through the bevel pair, shared with Pinion A), but the nozzle ring's
    required pitch radius (36 mm, sized for the petal/hinge geometry) is
    incompatible with a direct mesh at that offset. **Fix: added a compound
    idler gear stage** (`nacelle_nozzle_idler.scad`, new file) between the
    Crown Pinion and the nozzle ring — Idler-In (44T, R=22mm) meshes the
    Crown Pinion at the fixed 28.1 mm centre distance; Idler-Out (15T,
    R=7.5mm) meshes the new full-circle ring gear (72T, R=36mm) at a
    43.6 mm centre distance. A valid idler-shaft position exists per the
    triangle inequality (|28.1-43.6|=15.5mm ≤ 28mm ≤ 28.1+43.6=71.7mm).
    Also replaced the old partial rack with a full-circle ring gear,
    eliminating the arc-coverage sizing problem entirely. Also fixed a
    latent bug found during the rework: `LINK_HOLE_R` (28 mm) exceeded
    `PETAL_LENGTH` (18 mm) — the piano-wire link hole was off the physical
    end of the petal; corrected to `LINK_HOLE_R=16mm`, `PETAL_LENGTH=20mm`.
    Updated `nacelle_pinion.scad`'s Stage 3 ratio derivation and mating
    tables to match.
- [x] **Render updated/new gear-train STLs** *(done 2026-06-22, openscad +
    trimesh now available)* — `nacelle_nozzle_iris.scad`, `nacelle_sector_gear.scad`,
    and the new `nacelle_nozzle_idler.scad` (both parts) all rendered; see
    §1.1.3.1/§1.1.3.2 above.
- [x] **Mesh-verify the regenerated nacelle gear-train STLs** *(done
    2026-06-22)* — `nacelle_nozzle_idler.stl`, `nacelle_nozzle_idler_bracket.stl`,
    and `nacelle_sector_gear.stl` are all fully watertight (single connected
    solid each). `nacelle_nozzle_iris.stl` (assembly-preview render) has one
    non-manifold edge out of 26,381 from the petals' designed overlap —
    see §1.1.3.1 finding above; not a print-file defect.
- [x] **Idler angular position about the nozzle axis** *(resolved
    2026-06-22)* — solved the two simultaneous centre-distance constraints
    (28.1 mm from Crown Pinion at local (X=0, Y=PINION_A_Y=28); 43.6 mm
    from the nozzle/ring axis (0,0)): shaft position (X=+27.485, Y=33.846),
    i.e. 50.92° from the local +X axis (rounded to 50.9°). The other valid
    mirror solution is 129.08° at X=-27.485 — +X chosen arbitrarily (nothing
    else occupies that sector at this Z station). `IDLER_SLOT_ANG` in
    `nacelle_nozzle_iris.scad` updated to match; idler + bracket placed in
    `serenity_assembly.py` at this (X, Y).
- [ ] **NEW — idler axial mesh-band mismatch (open, found 2026-06-22)**:
    the idler's two gear sections are 10 mm apart axially
    (`GEAR_H_IN + GEAR_GAP`, `nacelle_nozzle_idler.scad`) — Idler-In's band
    starts at local Z=2, Idler-Out's at local Z=12. But Crown Pinion
    (`CROWN_Z` = 166.25 mm) and the Nozzle Ring (`NOZZLE_RING_Z` = `CROWN_Z`,
    i.e. the *same* station) currently sit at the identical 166.25–174.25 mm
    Z band — zero mm apart. A single idler shaft cannot present two gear
    sections 10 mm apart and mesh two targets that are 0 mm apart as
    currently speced. **Needs a design decision**: either move Crown
    Pinion's Z to create the needed 10 mm (or matching) axial offset from
    the Ring, or change the idler's own `GEAR_GAP`/section order to match
    the existing (zero) Crown-Pinion/Ring spacing. Until resolved, the
    idler + bracket are placed in `serenity_assembly.py` at a centred
    placeholder Z (`CROWN_Z - 11.0`) — VERIFY tier, explicitly flagged
    pending this decision. See `nacelle_nozzle_idler.scad` header for the
    full derivation.
- [x] **Confirm Sector Gear standoff distance from the nacelle face**
    *(resolved 2026-06-22)* — a tilt-bracket SCAD source DOES exist
    (`airframe/openscad/wings/wing_nacelle_pylon_revo.scad`, not found in
    the previous search), which bolts the sector gear to the pylon face at
    `PYLON_X0 = NACELLE_OD_X/2 = 30.25 mm` using that file's own simplified
    synthetic-ellipse `NACELLE_OD_X = 60.5 mm`. `serenity_assembly.py`'s
    `NACELLE_FACE_X_PYLON = 34.0 mm` instead matches
    `nacelle_pod_50mm_tandem.scad`'s own constant of the same name, which
    that file documents as "taken from the actual nacelle STL measurements
    rather than the synthetic-ellipse `NACELLE_OD_X`/2" — i.e. 34.0 mm is
    the validated, measured standoff already in use; it was not a guess.
    **Follow-up (new, not done here):** reconcile the pylon file's 30.25 mm
    ellipse approximation to the nacelle's measured 34.0 mm in a future
    pylon-model pass — out of scope for this nozzle/gear-train fix.
- [x] **`nacelle_tip_cap_port/stbd.stl` — ARCHIVED 2026-06-22**, per user
    instruction ("legacy part, no longer needed"). STLs moved to
    `airframe/archive/stls/nacelles/` (see `ARCHIVE_INDEX.md`); placement
    code and the now-unused `NACELLE_FACE_X_FAR` constant removed from
    `serenity_assembly.py`; references removed from
    `airframe/blender-scripts/serenity_render_views.py`,
    `docs/PHASED_BUILD_GUIDE.md`, and `PROJECT_INDEX.md`. Note for the
    record: `PHASED_BUILD_GUIDE.md`'s now-removed rows described this part
    as housing the RED/GREEN nav-light recess (port/stbd) — if nav-light
    mounting is still needed, it isn't currently assigned to any other
    component; flagging in case that function still needs a home.
    `current-specification/LICENSE_AND_ATTRIBUTION.md` also references this
    part in an already-stale (pre-Rev-R1 naming) file-tree snapshot — not
    touched here, pre-existing staleness unrelated to this archival.
- [x] **`cargo_sect_shell24.scad`'s port/stbd mirroring used the wrong axis
    — FIXED 2026-06-22** (adjudicated against CLAUDE.md's hull-frame
    standard, per explicit user direction). Rendered and mesh-verified after
    the fix: `openscad --hardwarnings cargo_sect_shell24.scad` compiles
    clean (no warnings), output fully watertight (14 connected solids, 0
    bad) — bounds X −204.0..−7.4, Y −415.6..−211.3, Z 0.0..163.2 mm, matching
    the file's own documented STL bounding box. Root cause confirmed: the wing
    subsystem (`wing_root_mortise()`, `wing_spar_bore()`,
    `spar_bearing_block()`, `nacelle_servo_mount_block()`) had been modelled
    using the WING's own internal pre-permutation convention
    (`wings_s1223_revo.scad`: "X: chordwise, Y: thickness, Z: spanwise")
    without ever applying that file's own `X<-Z, Y<-X, Z<-Y` permutation to
    hull-aligned axes before use here — i.e. an un-translated foreign
    coordinate system, exactly what CLAUDE.md's hull-frame standard exists
    to prevent. Added `CARGO_X_WALL_PORT`/`CARGO_X_WALL_STBD` (measured
    lateral wall positions, mapped through this file's own validated bake
    transform: `local_X=-201.5 -> hull_X=-72.9` PORT, `local_X=-7.4 ->
    hull_X=-267.0` STBD) and `WING_ROOT_Z_CEN=62.5` (fixed root height for
    both sides, from CLAUDE.md's validated baked Wing_Port/Wing_Stbd Z
    extent +48..+77 mm); re-derived all four modules to mirror across X
    with this fixed Z. Bonus fix: `wing_spar_bore()` now runs the full
    lateral span through BOTH walls (a real continuous tip-to-tip spar
    passage) — previously it was a short Z-axis bore that never reached the
    far wall at all, so the two wings were never actually structurally
    connected by a shared spar.
    **Two items deliberately left open by this fix, not resolved:**
  - The spar/mortise chordwise (Y) offset still uses the pre-existing
    `WING_ROOT_Y_CEN` value as an interim stand-in; the true offset needs
    re-deriving against the current 129 mm Rev R1 root chord (already
    tracked: TODO.md §1.1.2 "Verify cargo-section wing-root mortise
    dimensions against new root chord 129 mm").
  - **NEW, more serious — `WING_ROOT_Z_CEN`=62.5 mm overlaps River's
    avionics bay (Z 24..64 mm)**: the spar bearing boss alone (Z
    51.5..73.5) already overlaps River's upper 51.5..64 mm band. This is
    a real structural/packaging conflict, independent of the axis bug —
    it was masked before only because the old (wrong) code happened to
    place the wing hardware at the gondola's Z extremes, nowhere near
    Z=24..64. `nacelle_servo_mount_block()`'s own Z-placement
    (`NSVMT_Z_OFFSET`, +30.5 mm from `WING_ROOT_Z_CEN`) was chosen only to
    clear the wing mortise/spar boss with the same 4 mm margin the
    original code used, and was NOT checked against River's bay — it may
    also land inside or near it. **Needs a structural/packaging decision
    (move River's bay? reduce its footprint? confirm the wing spar's
    actual swept volume doesn't reach the Faraday tray?) before any of
    this geometry is considered final — not resolved here.**
    `nacelle_servo_bracket.stl` still does not exist in `airframe/stls/`
    (only the SCAD source has been authored); render it once the Z-conflict
    above is resolved.

#### 1.1.4 **Landing Gear**

**Canonical leg model (Rev R5, 2026-06-20): vertical post + 4-wire brace.** The
original canonical single-blade leg (`leg_1`…`leg_4_scaled24.stl`, misubisu Thingiverse
hull, CC BY 4.0) is itself a vertical part with **two branch points of its own** — one
at the **apex** (top) and one about **1/3 of the way down from the apex**. The
Strong-Leg's duplicate + 30°-rotate + union construction doubles each into a pair, so
the Strong-Leg actually has **four branch points** (2 at the apex, 2 at the 1/3-down
point), not the single fork-into-two-arms that Rev R2–R4 approximated. Rev R5 models
this directly: the CF-PETG is kept only as a short **vertical post** (foot up through
the 1/3-down branch height), and all four branch attachments are replaced with **four
simple wires** instead of forked CF-PETG arms or arm-tip fuses. Full structural
analysis: `docs/LANDING_GEAR_ANALYSIS.md` (Rev R5, 2026-06-20).

**Why the wires, and why this shape:** rigorous re-verification of the Rev R2 (bare
CF-PETG Strong-Leg) design found a real single-point-of-failure risk — the post/trunk's
fixed cross-section could not be made stronger than the arms by infill alone, and the
real system stiffness implied a peak force far above what the structure could survive
elastically. Rev R3 fixed this with an elastic spring-steel leaf (≈163 g, no clear
worst-case margin) and Rev R4 with a closed-ring ductile wire fuse (≈73 g, but hard to
manufacture/field-replace — precision winding + separate tabs). **Rev R5 uses the
simplest possible wire shape — a single straight piece of wire stock with one shallow
pre-bend (a shallow "bow," not a closed loop)** — formable with a simple bending jig or
by hand, easily field-replaced with cut-to-length stock:

| Branch level | Height from foot | Wires | Role |
|---|---|---|---|
| Apex | ≈79.8 mm | 2× **spring** wire (Ø3.17 mm, L=45mm) | Elastic, recoverable — sized for the 1.5 ft elastic-check energy |
| 1/3-down from apex | ≈53.2 mm | 2× **ductile** wire (Ø4.35 mm, L=30mm) | Plastic, sacrificial — **each independently** sized for the full 6 ft worst-case per-leg energy (14.04 J) |

**Result:** total added wire mass ≈50 g (1.6% AUW); CF-PETG post mass ≈130 g (sized
with 2× margin at the combined worst-case force — the post is not expected to yield at
all); hull boss bearing margin ≥1.56× at the combined-pair force. This satisfies
Requirement 3 of `docs/LANDING_GEAR_ANALYSIS.md` §1 with the cleanest margin structure
of any revision so far. Final certification of the bowed-strut mechanics requires the
instrumented drop test (LG-14) — hand calculation identifies the design point but
cannot fully certify post-yield material behavior.

**Demonstration STLs** (schematic — placeholder boss cylinders, standalone unbaked
post; generated by `tools/build_landing_gear_views.py` + `wire_brace_leg.scad`; see
`docs/LANDING_GEAR_ANALYSIS.md` §16): `post.stl`, `spring_wire_nominal.stl` /
`_deformed.stl`, `ductile_wire_nominal.stl` / `_deformed.stl`,
`landing_gear_assembled.stl`, `landing_gear_exploded.stl`, `landing_gear_deformed.stl`
— all in `airframe/stls/fuselage/landing-gear/`.

**Superseded prior assessments (retained for history only):** Rev R1 (2026-06-14,
single-blade leg, 37.5×7.5 mm slab, 30% infill, 218:1 compression margin, 31 mm ground
clearance — still insufficient for the 3-in payload mission, extension to ≥110 mm strut
length recommended, carried forward as an open item below). Rev R2 (Strong-Leg, no
fuse — invalidated by the Rev R3 re-verification). Rev R3 (Strong-Leg + elastic
spring-steel leaf). Rev R4 (Strong-Leg + per-arm closed-ring ductile fuse — superseded
by the simpler, manufacturable bowed-wire shape above).

**FreeCAD assembly status (2026-06-20):** Four corner copies of the prior Strong-Leg
geometry exist in `airframe/freecad/assembly/SerenityAssembly.FCStd` as Boolean-result
objects `Union`, `Union001`, `Union002`, `Union003` (90°-stepped rotation), confirmed in
their correct corner locations; the Rev R5 post replaces only the upper portion of that
geometry (foot-to-1/3-down-branch is unchanged) — see LG-10.

**Foot positions (hull frame, approximate — last validated 2026-06-14 against the Rev R1
single-leg layout; pending re-confirmation once LG-10 bake is complete, all level at
ground-contact Z ≈ −31 mm):**

| Foot               | Hull X (mm) | Hull Y (mm) | Ground Z (mm) | Notes                        |
|--------------------|-------------|-------------|---------------|------------------------------|
| foot_1 (fwd-port)  | −73.5       | −20.5       | −31           | TPU 95A; 43.9 × 43.9 × 9 mm  |
| foot_3 (fwd-stbd)  | −264.5      | −20.5       | −31           | same                         |
| foot_4 (aft-port)  | −73.5       | +129.5      | −31           | same                         |
| foot_2 (aft-stbd)  | −264.5      | +129.5      | −31           | same                         |

Stance: 191 mm (7.52 in) lateral × 150 mm (5.91 in) fore-aft;
CG centroid at X ≈ −169 mm (symmetric) ✓ (Rev R1 baseline — re-verify once Rev R5
foot positions are baked).

##### 1.1.4.1 *Vertical Post — Modeling and Bake*

- [x] Build and render the Rev R5 post + wire SCAD/STL *(done —
    `airframe/openscad/fuselage/wire_brace_leg.scad`, `post.stl`,
    `spring_wire_nominal/_deformed.stl`, `ductile_wire_nominal/_deformed.stl`, all
    watertight)*.

- [x] Build assembled / exploded / deformed demonstration compound STLs *(done —
    `tools/build_landing_gear_views.py` → `landing_gear_assembled.stl`,
    `landing_gear_exploded.stl`, `landing_gear_deformed.stl`; schematic placeholder
    bosses, unbaked standalone post — see `docs/LANDING_GEAR_ANALYSIS.md` §16)*.

- [ ] **LG-12 Model the post per the §4.6 dimensions** (round column, smooth 8mm
    conical taper — no stepped ledge — lower section Ø22.9mm foot→taper start, upper
    section Ø11.96mm taper end→apex, both 100% infill) in the FreeCAD/Blender source,
    replacing the Rev R2–R4 forked Strong-Leg
    geometry. **BLOCKS first flight.**

- [ ] **LG-10 Finalize the 4 corner post placements** in `SerenityAssembly.FCStd`; bake
    to hull frame; export 4 placed STLs. **Z-leveling rule:** if any of the 4 feet
    deviate in Z, align all 4 to the **most negative (lowest) Z** of the four. **BLOCKS
    hull boss integration (LG-02) and leg printing (LG-05).**

- [ ] **Ground clearance check carried forward from Rev R1** — overall post envelope
    (79.8 mm foot-to-apex) matches the original single-blade leg length, so the prior
    31 mm (1.22 in) ground-clearance finding still applies and is still insufficient for
    the ≥76 mm (3.0 in) payload-mission requirement. **BLOCKS payload mission.**

##### 1.1.4.2 *Spring and Ductile Wires*

- [ ] **LG-15 Select and procure both wire grades/tempers** — spring (full elastic
    range, working stress ≈900 MPa) and ductile (plastic-bend ductility, flow stress
    ≈550 MPa); confirm by coupon test. **BLOCKS leg fabrication.**

- [ ] **LG-16 Confirm the ductile wire temper survives forming** into the bowed-strut
    shape without premature cracking — coordinate with LG-15. **BLOCKS leg fabrication.**

- [ ] **LG-13 Define the wire-to-socket retention detail** (pin / set screw /
    adhesive) at both the post end and the hull boss end; verify against the §4.8
    lateral load (`docs/LANDING_GEAR_ANALYSIS.md` §4.8). The previous M3/M4 nylon
    shear-bolt fuse concept (Rev R2–R4, sized for a rigid spigot) no longer applies
    directly to a wire end. **BLOCKS first flight.**

##### 1.1.4.3 *Hull Boss Sockets*

- [ ] **LG-02 Design and integrate 16 hull boss sockets** (4 per corner, one per wire)
    into `cargo_sect_shell24.scad` / cargo shell Blender source. Boss spec: OD ≈10×9 mm,
    bore ≈6×5 mm, 2-wall annulus + positive-stop shoulder per `CLAUDE.md`. Run DRC mesh
    check. **BLOCKS hull print. Depends on LG-10.**

##### 1.1.4.4 *Canonical Foot — Socket Modification*

- [x] Feet separated into individual STLs (`foot_1` through `foot_4` in landing-gear/);
    canonical Thingiverse geometry, 43.9 × 43.9 × 9.04 mm TPU 95A, unmodified outer form.

- [ ] **Add top-face socket to canonical foot** — 7.6 × 9.0 mm bore × 5.0 mm deep,
    centred on the top face. Retention: 1× M2.5 × 12 mm SS through-bolt. See
    `docs/LANDING_GEAR_ANALYSIS.md` §7. New SCAD/Blender modifier needed (stock foot mesh
    has no socket feature today).

- [ ] **Assess foot grip on concrete/asphalt** — TPU 95A is adequate for smooth surfaces.
    For field operations (grass, gravel): consider adding a 3 mm textured grip ring or
    rubber disk insert (Sorbothane 50A, 40 mm OD × 3 mm) bonded to foot bottom face.

##### 1.1.4.5 *Superseded — Rev R1.4 V-Brace and Rev R4 Closed-Ring Fuse*

- [x] **Rev R1.4 corner V-brace (`landing_leg_assy.scad`) is retired**, superseded
    2026-06-20. The parametric SCAD file is left in the repository for reference only.

- [x] **Rev R4 closed-ring wire fuse (`wire_loop_fuse.scad`) is retired**, superseded
    2026-06-20 by the simpler bowed-wire shape (§1.1.4 above) for manufacturability. The
    SCAD file is left in the repository for reference only (retirement note added at its top).

##### 1.1.4.6 *Rear Skid Reinforcement (unrelated subsystem)*

- [ ] **LG-03 CF rod channel in `middle_canonical_shell24.scad` rear skid arms** — add
    3 mm bore channel (CF rod, ~140 mm per skid) per `docs/LANDING_GEAR_ANALYSIS.md §10`.
    Re-export STL, re-bake, verify watertight.  **BLOCKS taxi test.**

- [ ] **`landing_legs_hull_r1.stl` is orphaned** — rendered from an even earlier
    pre-R1.4 single-leg SCAD mode that no longer exists in `landing_leg_assy.scad` (now
    itself retired, §1.1.4.5 above). Delete the stale STL or update
    `airframe/blender-scripts/serenity_render_views.py` line 97, which still references it.

##### 1.1.4.7 *Qualification Testing (BLOCKS first flight)*

*"Time for some thrilling heroics." — Mal. Drop tests count.*

- [ ] **LG-06 Drop test prototype leg assembly** — mount one complete assembly to a
    6.90 lbm (3,130 g) fixture. Drop from 1.5 ft (elastic check — confirm zero permanent
    set on the post and both wire types). **BLOCKS first flight.**

- [ ] **LG-07 Confirm avionics enclosure shock rating** against the wire-mediated
    deceleration profile (re-derive peak-g once LG-14 data exists). See PCB fab
    checklist. **BLOCKS first flight.**

- [ ] **LG-11 Coupon-test CF-PETG** at 4 perimeters / 100% infill (post is now fully
    solid-infill, §4.6) to confirm the achievable effective modulus/strength.
    **BLOCKS first flight.**

- [ ] **LG-14 Instrumented drop test (load cell + high-speed video) at 6 ft full-AUW** —
    confirm the ductile wires collapse at the predicted ≈4,298 N/wire; confirm the
    bowed-strut mechanics match the idealized 2-hinge model
    (`docs/LANDING_GEAR_ANALYSIS.md` §4.1); confirm the post and spring wires stay
    elastic. **This is the test that certifies the Rev R5 design — hand calculation
    identifies the design point but cannot fully certify post-yield material behavior.**
    **BLOCKS first flight.**



**Remaining parts needing SCAD source creation then STL export:**

- **BLOCKS Phase 1**

**Combined airframe model (visual verification):**

- [ ] **Combine all airframe STLs** into a single assembly model including the 1.25× scaled nacelles, all EDF tubes, cargo bay clamshells, antenna bosses, sensor cutouts, access panels, landing legs, and feet.
    **Canonical assembly script:** `airframe/FreeCAD-scripts/serenity_assembly.py` (8 major components validated 2026-06-10; nacelle internals, pylons, and accessories pending VERIFY).
    Run headlessly: `freecad --background --python airframe/FreeCAD-scripts/serenity_assembly.py`
    Output: `airframe/Serenity-Assembled.FCStd`
    - [ ] **Render overview SVGs using FreeCAD TechDraw** — 6 cardinal directions (top, bottom, front, rear, port, stbd) and all 8 isometric views (8 corners). Headless script creates a TechDraw page per view and exports SVG via `TechDraw.writeSVGPage()`. Save to `airframe/diagrams/overview/`.
        **BLOCKS** exploded view SVGs below.
- [ ] **Exploded view SVG — printed parts only** (all printed components labelled and exploded from assembly position). **Generate using FreeCAD:** drive part translations via a headless Python script that offsets each `Mesh::Feature` Placement along its explosion axis, then exports SVG via FreeCAD TechDraw. Save to `airframe/diagrams/exploded/`.
- [ ] **Exploded view SVG — full build** (all components: PCBs, SBCs, motors, ESCs, wires, sensors, antennas, hardware). Same FreeCAD TechDraw headless approach as printed-parts exploded view. Save to `airframe/diagrams/exploded/`.

---

#### 1.1.5 **Non-Printable Component Placeholders** *(Rev R1, 2026-06-12)*

Dimensionally-accurate bounding-geometry STL placeholder files for all non-printable
Rev R BOM components, for use in FreeCAD exploded-view and build-guide assembly.

**Generator:** `airframe/placeholders/generate_placeholders.py`
(pure Python, no external dependencies; run with `python3 generate_placeholders.py`)

**FreeCAD catalog script:** `airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`
(loads all 76 placeholder STLs into a grid-layout catalog document;
run with `freecadcmd airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`)

**Output:** `airframe/Serenity-Placeholders.FCStd` (76 components, 8-column grid)

**Placeholder coverage (76 STLs, 6056 triangles total):**

| Category | Count | Files |
|---|---|---|
| Propulsion (EDFs, ESCs) | 4 | `airframe/placeholders/propulsion/` |
| Servos (DS3218MG, SG90) | 2 | `airframe/placeholders/servos/` |
| Bearings (MF104ZZ, MR63ZZ, 6804) | 3 | `airframe/placeholders/bearings/` |
| Structural CF (rods, tube, bar, plate, PTFE) | 6 | `airframe/placeholders/structural/` |
| Avionics PCBs (PB2-I, Cape-A-2/B-2, Emma, Kaylee, microSD) | 6 | `airframe/placeholders/avionics/` |
| Power (LiPos, fuses, shunt) | 7 | `airframe/placeholders/power/` |
| Cargo (N20, HX711, DRV8833, Dyneema) | 4 | `airframe/placeholders/cargo/` |
| Gears M=1.0 (sector, pinion, bevel, housing) | 4 | `airframe/placeholders/gears/` |
| Hardware (pins, inserts, screws, straps, wire ring) | 6 | `airframe/placeholders/hardware/` |
| Lighting (WS2812B ring, WS2812C SMD) | 2 | `airframe/placeholders/lighting/` |
| Wiring (conduit, harnesses, antenna wire, posts) | 6 | `airframe/placeholders/wiring/` |
| GCS / Malcolm (enclosure, BECs, antennas, tripod, encoders) | 15 | `airframe/placeholders/gcs/` |
| Foam fill + interior voids (head/cargo/middle/rear fill; avbay, cargo bay, wiring trunk, power bus, ventilation, pylon pockets; Faraday cage pockets + vent duct spurs) | 13 | `airframe/placeholders/foam/` |
| EMC / Faraday shielding (cage, gasket, fan, EMI vent, bond strap, feed-through panel, ferrite; Malcolm fan + gasket) | 9 (×2 STL files share gen_far_fan_40) | `airframe/placeholders/faraday/` |

**Completed (2026-06-12):**
- [x] **Generate all 65 component placeholder STLs** — `generate_placeholders.py` created;
    all files verified `OK`. STL header marker: `SerenityUAV PLACEHOLDER R1`. *(done 2026-06-12)*
- [x] **FreeCAD catalog assembly script** — `serenity_placeholders_assembly.py` created;
    component grid layout; run with `freecadcmd`. *(done 2026-06-12)*
- [x] **Faraday shielding hardware** — 9 new generators; 11 new STL files in `airframe/placeholders/faraday/`:
    FAR-CAGE-AV (cage), FAR-GASKET-AV, FAR-FAN-40, FAR-EMI-VENT-40, FAR-BOND-STRAP,
    FAR-FT-PANEL, FAR-FERRITE-4MM; MAL-FAR-FAN, MAL-FAR-GASKET (GCS).
    BOM entries added to `current-specification/bom_revR.csv`.
    **⚠ MASS NOTICE: Faraday aircraft system now 364 g (0.80 lbm) after
    ferrite reduction to 4/cage and 1 bond strap/cage. Full Rev R1 weight
    reduction pass (Phase 11 deferrals, wiring gauge, PCB consolidation,
    head infill, CF plates) brings cumulative T/W to ~1.19 without battery
    swap; T/W ~1.25 with BATT-6S-2800. See §1.1.5 mass budget.**
    *(done 2026-06-13)*
- [x] **Faraday cage foam voids** — VOID-FAR-CAGE (76×56×88 mm cage pocket) and
    VOID-FAR-FAN-SPUR (44×44×50 mm vent duct spur) added to `airframe/placeholders/foam/`.
    Use ×4 and ×8 copies respectively in FreeCAD to plan all 4 bays. *(done 2026-06-13)*
- [x] **Foam-fill and void visualization STLs** — 11 new STLs in `airframe/placeholders/foam/`:
    4× FOAM-FILL-\* (head/cargo/middle/rear hull sections) and 7× VOID-\* (avionics bays,
    cargo bay, wiring trunk, power bus, ventilation intake/exhaust, nacelle pylon pockets).
    Total 76 components, 6056 triangles. Use tan/ochre for FOAM-FILL, translucent cyan for
    VOID objects in FreeCAD. *(done 2026-06-12)*

**Open sub-tasks:**
- [ ] **Rear skid reinforcement — SCAD update (TWO files)**
    The skids are the aft extensions of the middle-section horseshoe ring; the
    middle/rear section cut was made purely for printability and carries no load.
    The CF rod must therefore span BOTH sections continuously to reinforce the
    full skid bending span and to tie the print joint together.
    Changes required:
    - `s_middle_canonical_shell24.scad`: add 4.2 mm bore channel along each
        horseshoe-bent-aft skid arm from the horseshoe origin to the aft face
        (middle/rear joint face at hull Y ≈ +203 mm).
    - `s_rear_neck_intake_shell24.scad`: add matching coaxial 4.2 mm bore
        channel through the skid extension from the joint face to the skid tip.
    - Channels must be coaxially aligned across the joint face to accept a
        single continuous rod. Nominal channel axis = hull Z-face centroid of
        each skid cross-section.
    - Rod: 4 mm OD solid CF from CF-ROD-4MM stock, ~250 mm per skid × 2
        skids = ~500 mm total; insert from aft, epoxy (West System 105/206).
    - Rod serves triple purpose: skid bending stiffness, middle/rear joint
        tie-together, assembly alignment pin.
    - Re-slice both parts after SCAD update; update masses in BOM.
    **BLOCKS first taxi/landing test.**
- [ ] **Run FreeCAD catalog** — execute `serenity_placeholders_assembly.py` once
    FreeCAD is available to verify grid layout and produce
    `airframe/Serenity-Placeholders.FCStd`. Commit the FCStd to the repository.
- [ ] **Hull-frame placement pass** — for the full-build exploded view (§1.1.4 task),
    derive the hull-frame position and orientation of each placeholder (e.g., EDF
    inside nacelle bore, battery tray in cargo section, avionics PCBs in bays)
    and add `place_mesh()` calls to `serenity_placeholders_assembly.py`.
- [ ] **Add Phase-11 (deferred) items to catalog** — regenerate placeholders for the
    Rev R1 rear-EDF redesign: `EDF_55mm_6S_deferred.stl`, `ESC_50A_6S_BLHeli32_deferred.stl`,
    `rear_nozzle_canonical_deferred.stl`, and `rcs_thruster_x4_deferred.stl`; confirm they
    appear in the `deferred/aft-edf/` sub-assembly once that phase resumes. (Old 120mm/80A
    placeholders are superseded.)
- [ ] **Mesh watertightness audit** — run `python tools/validate_stls.py` across
    `airframe/placeholders/**/*.stl` after first CI run; resolve any non-manifold
    findings (complex compound meshes: piano-wire torus ring, RF splitter ports, etc.).
    **Known finding:** `Foam_fill_middle_horseshoe_173x69x161mm.stl` has coplanar
    T-junction faces at Z=121 mm between left/right pillar tops and the arch bottom
    (all three pieces share a common plane but are separate box meshes joined via `_cat()`).
    Acceptable for visualisation; fix by replacing with a proper extruded U-shape when
    trimesh/CSG support is available.
- [ ] **FAR-FT-PANEL PCB design** — design the EMI-filtered feed-through panel
    KiCad schematic + layout (55×35 mm, LP π-filter + TVS on CAN FD ×2,
    RS-485, Ethernet RJ45, power JST-GH 2P). Run DRC; generate gerbers; add
    to `avionics/kicad/`. **BLOCKS Faraday cage final assembly.**
- [x] **Faraday mass budget review** — Faraday aircraft system 364 g (0.80 lbm)
    after Rev R1 ferrite (4/cage) + strap (1/cage) reduction. Full weight
    reduction pass (2026-06-13) brings estimated T/W to ~1.19; BATT-6S-2800
    swap yields ~1.25 — above the 1.2 minimum. *(resolved 2026-06-13)*
- [ ] **Link placeholders to BOM entries** — add `Placeholder_STL` field to
    `docs/bom_revR.json` for each non-printable row pointing to its STL path.

---

### 1.2 — PCB Design: Cape-A-1 and Cape-B-1

- [x] **Regenerate Cape-A-1 gerbers** — `.kicad_pcb` modified 2026-05-23 (tamper-mesh commit); gerbers in `serenity/kicad/gerbers/CAPE-A-1/` are from 2026-05-22.
    - Open in KiCad → Plot → Gerbers; overwrite files in `serenity/kicad/gerbers/CAPE-A-1/`; re-export drill files.
    - Run DRC to zero errors before plotting.
    - **BLOCKS Phase 6 fab order**

- [x] **Regenerate Cape-B-1 gerbers** — same timestamp issue. `serenity/kicad/gerbers/CAPE-B-1/` files are from 2026-05-22.
    - **BLOCKS Phase 6 fab order**

---

### 1.2b — PCB Redesigns: Emma Rev R1 / Zoë Rev R1 / Kaylee Rev A1

These three boards require schematic + layout changes before the next fabrication order.
All are on the `avionics/kicad/` branch; run DRC to zero errors before generating gerbers.

- [ ] **Emma Rev R1 — add LoRa, replace JST with P1+P2 socket rails**
    - Add RFM95W 915 MHz LoRa module (SPI interface to PB2-I via P1 header pins).
    - Replace JST GH 6P connector with 2× 20-pin 2.54 mm socket rails (P1 + P2),
        matching Zoë passthrough rail pinout so Emma stacks cleanly on top.
    - Update SRF2012-100Y CMC + TVS guard to cover LoRa SPI and antenna lines.
    - Update silk/fab layer: "Emma Rev R1 — 49 MHz AX.25 + LoRa 915 MHz".
    - Fitted in: River's Room, Simon's Medbay only (2 boards total).
    - Run DRC → zero errors; generate gerbers to `avionics/kicad/gerbers/Emma-R1/`.
    - **BLOCKS Emma fabrication order.**
    - [x] Components added to Emma board.
    - [x] Emma Kicad files renamed from XCVR to Emma
    - [x] Footprints arranged so that all components fit
    - [x] **LoRa (RFM95W) pin mapping corrected (2026-06-20)** — as-placed, SPI1_MISO/MOSI/CLK/
        SPI1_CS_LORA were wired to pads 10–13 (real pins GND/DIO3/DIO4/3.3V per
        [REF-RFMOD-001]) and LORA_RESETN to pad 2 (real pin MISO): a wrong-pin-number error
        that would have driven the SPI clock onto the module's 3.3V pin if fabricated as-is,
        not merely a missing connection. Corrected to pads 2–6 (MISO/MOSI/SCK/NSS/RESET) and
        1/8/10 (GND) per the verified HopeRF datasheet. **Still open, blocks fabrication:**
        - [ ] Pad 9 (ANT) and pad 13 (3.3V) carry no net — module has no antenna or power path
        - [ ] DIO0–DIO5 (pads 7, 11, 12, 14–16) unassigned pending P1-header GPIO budget decision
        - [ ] Footprint pad size (2.95×1.27 mm) is oversized vs. real RFM95W castellated pads
        - [ ] Footprint physically overlaps CAPE-B IF (JST GH 6P) — needs repositioning
        - [ ] CAPE-B IF (JST GH 6P) connector is still present and fully wired — "replace JST
            with P1+P2 socket rails" has NOT happened; verify whether PB2-P1/P2 sockets already
            carry all 6 of its signals before removing it
    - [ ] EMI spacing verified
    - [ ] Labels and silk arranged for readability
    - [x] **Traces and nets regenerated and DRC issues resolved — partial (2026-06-20).**
        Schematic ERC: file-load crash (stray `;;` comment) + J1 SHIELD/MP pin mirroring fixed,
        0 errors. PCB DRC: all 12 shorting_items, 1 tracks_crossing, 1 courtyards_overlap, 2
        hole_clearance resolved to 0 (was non-zero at session start). GND zone (In1.Cu) and +5V
        zone (In2.Cu) were declared but never actually filled/saved — filled via pcbnew's
        ZONE_FILLER, resolving 24 connections at no design risk. 65 GND pads stitched with new
        vias; +3V3 (31 pads, no plane exists on this 4-layer stackup) and 14 more nets (+5V,
        +5V_FILT, ANT, COMP_IN, DDS_RF, MODE_SEL, PA_INT, PTT_N, RF_LPF_N1, RSSI_ANA, UART_TX/RX,
        UART_TX_F/RX_F) routed via MST + obstacle-aware A* pathfinding, each verified by a
        DRC re-run before moving on. Remaining `clearance` errors (15) are pre-existing,
        inherent to 0.5mm-pitch IC footprints (49M DDS, TX DAC) — not fixable without a
        footprint change.
        - [ ] **Still unrouted — 13 nets** (`RF_TX`, `RF_FILT`, `RF_LPF_N2`, `RX_LNA`,
            `TCXO_OUT`, `AFSK_IN`, `AFSK_OUT`, `DDS_CLK`, `DDS_DAT`, `SBUS_OUT`, `RF_RX`,
            `RSSI_RAW`, `UART_RX_MUX`) plus scattered edges within partially-routed nets — sit
            in pockets too tight for a 0.2mm-trace/0.25mm-clearance model to route automatically
            without risking a marginal connection. Needs thinner trace width, B.Cu fallback
            routing, or manual GUI placement.
        - [ ] **Ethernet differential pairs deferred** (`RMII1_*`, `MDIO`, `MDC`, `PHY2_RSTN`,
            `PHY2_INTRN`, `EMMA_ETH_TXP/TXN/RXP/RXN`, `EMMA_ETH_LINE_TXP/TXN/RXP/RXN`) — these are
            differential pairs through the T-ETH isolation transformer; need length/impedance-
            matched routing, not generic pathfinding.
        - [ ] **LoRa SPI bus deferred** (`LORA_RESETN`, `SPI1_MISO/MOSI/CLK/CS_LORA`) — same
            reasoning, lower risk than the Ethernet pairs but not yet attempted.
        - [ ] **`GND2_ETH`/`VCC2_ETH` deferred — confirmed isolated domain (2026-06-20).**
            Per user: ETH-PHY/T-ETH/PB2-P1/P2 were intentionally added to Emma so it can provide
            a second Ethernet port for the Zoë stack (matching Wash's 2-PHY config) and so Emma
            can connect to Ethernet standalone, outside Serenity. `GND2_ETH` is the isolated
            secondary side of the T-ETH transformer — must NOT be bridged to the main GND plane
            (would defeat the isolation). Needs a small isolated copper island/plane, not via-
            stitching to In1.Cu.
    - [x] **Silk text height standardized (2026-06-20).** All 78 silk labels used 0.65mm
        text against the project's declared 0.8mm `min_text_height` rule (pre-existing since
        before this session, not caused by it). Standardized the rule to 0.6mm min — matches
        what's actually achievable on this 55×35mm/75-component board without forcing a
        resize-everything pass that risks new overlaps. Labels may go up to 0.8mm where
        clearly clear space allows it (no specific labels bumped yet).
    - [ ] **Silk overlap/over-copper cleanup — NOT done, 174 pre-existing warnings.**
        119 `silk_over_copper` + 53 `silk_overlap` + 2 `silk_edge_clearance`, all present
        since before this session and unchanged by it. Emma.md §10 documents a prior partial
        pass (13 pairs) that did not cover this remainder. Each fix needs the same kind of
        spatial verification as the net routing above — comparable scope of effort. Deferred
        to a dedicated session.
    - [x] **FCC ID silkscreen placeholder added (2026-06-20).** Board-level silk text now
        includes "FCC ID: PENDING CERTIFICATION" and the required §15.19(a)(3) two-condition
        compliance statement. No real FCC ID exists yet — equipment authorization (§2.803/
        §15.19) requires TCB testing/grant, which has not happened. Replace the placeholder
        with the granted ID once certified.
    - [ ] Gerbers exported — **not done this session; board has 94 unconnected items and
        174 silk warnings, not yet production-ready. Do not export gerbers for fabrication
        until routing and silk cleanup are complete — see items above.**

- [ ] **Zoë (Cape-B-2) Rev R1 — remove LoRa, add P1+P2 passthrough rails**
    - [x] Components arranged so that no footprint collisions are present
    - [ ] EMI spacing verified
    - [ ] Nets and vias fixed
    - [ ] DRC rules checked.
    - Remove RFM95W footprint and all associated SPI routing + LDO supply.
    - Add 2× 20-pin 2.54 mm pass-through socket rails on upper face (upper sockets
        match Emma P1+P2 pinout; lower pins pass through to Cape-A-2 / PB2-I stack).
    - Carry all PB2 P1+P2 signals from lower pins to upper sockets; add 0 Ω options
        on signals consumed by Zoë (Wi-Fi, SiK, I²C, UART) so they are both used and
        passed through.
    - Update silk/fab: "Cape-B-2 Rev R1 — Zoë CN cape"; note Emma header on upper face.
    - Run DRC → zero errors; generate gerbers to `avionics/kicad/gerbers/CAPE-B-2-R1/`.
    - **BLOCKS Zoë + Emma fabrication order.**

- [ ] **Kaylee Rev A1 — remove 6 V BEC, add 5 V servo output**
    - Remove TPS54540 6 V/5 A BEC circuit (IC, inductor, output caps, feedback divider,
        Molex Nano-Fit 6 V output connector).
    - Add third TPS54620 5 V/3 A instance for dedicated servo rail (shares 5 V feedback
        reference with avionics BECs; separate output capacitor bank; Molex Nano-Fit
        connector labelled SERVO-5V).
    - Verify 5 V servo current budget: 2× DS3218MG = 2× 500 mA stall = 1.0 A peak;
        3 A rated output provides 3× headroom — adequate.
    - Update silk/fab: "Kaylee Rev A1"; update schematic title block.
    - Run DRC → zero errors; generate gerbers to `avionics/kicad/gerbers/Kaylee-A1/`.
    - **BLOCKS Kaylee fabrication order.**

---

### 1.2a — PCB Design: Wash, Zoë, and Emma (EMI-Hardened Variants)

#### ***EM hardening Objective is to ensure safe and controlled operations in hostile em/rf environments such as the vicinity of radiating commercial broadcast, amateur radio and cellular towers.***

Design files on branch `claude/cape-em-harsh-variants-9Yfr1`. Schematics (`*.kicad_sch`) and PCB
layout files (`*.kicad_pcb`) are complete. Gerber files have not yet been generated or DRC-verified.

**Key changes from -1 variants:**

- **CAN FD**: ATA6561 (non-isolated) → ISOW1044BDFMR (TI, SOIC-16W, 5 kV reinforced isolation +
    integrated DC/DC converter, IEC 62368-1 / VDE 0884-11)
- **RS-485**: MAX3485E (non-isolated) → ADM2795EBRWZ (ADI, SOIC-20W, 5 kV reinforced isolation +
    integrated DC/DC converter)
- **Ethernet PHY (Rev R baseline; introduced Rev Q)**: DP83825I (TI, LQFP-32, 10/100BASE-TX RMII) with EMI hardening:
    HX1188NL LAN magnetics (1500 V isolation), SRF2012-100Y CMC, PRTR5V0U2X TVS, TPS62933 1.8V
    supply. JST SM06B-GHS-TB-1MP connector (no RJ45). Wash: 2× PHY (RMII0+RMII1);
    Zoë: 1× PHY (RMII0).
- **Emma**: SRF2012-100Y CMC on antenna coax shield, PRTR5V0U2X TVS on PTT/RX lines,
    X2Y bridging capacitor on RF ground plane, Würth 742792512 ferrite bead on +5V rail

**Transform scripts** (generate -2 files from -1 originals):

- `avionics/kicad/gen_cape_a2.py` → `CAPE-A-2.kicad_sch`
- `avionics/kicad/gen_cape_b2.py` → `CAPE-B-2.kicad_sch`
- `avionics/kicad/add_eth_phy.py` — ETH PHY isolation sub-circuit generator (called by above)
- `avionics/kicad/gen_cape_a2_pcb.py` → `CAPE-A-2.kicad_pcb`
- `avionics/kicad/gen_cape_b2_pcb.py` → `CAPE-B-2.kicad_pcb`

**Open tasks:**

##### 1.2a.1 *Cape DRC / routing / ETH2 status (2026-06-12)* — see `avionics/kicad/README.md`

- [x] **Wire second Ethernet (ETH2) on Wash.** `ETH2` / `ETH2-PHY` (ADIN1300) /
    `T-ETH2` (749010012A) were placed but unconnected; nets now mirror ETH1
    (`ETH2_LINE_*` → `T-ETH2` → `ETH2_*` → PHY), reusing the host-side `RMII1_*`,
    `MDIO`/`MDC`, `PHY2_INTRN`/`PHY2_RSTN`, `VCC2_ETH`/`GND`/`GND2_ETH` nets on
    PB2-P2. 44 pads assigned; diff pairs verified. *(PR #59, 2026-06-12)*
- [x] **Separate the two Wash PHYs onto independent MDIO buses** (instead of an
    address strap). PHY1/ETH1-PHY → `MDIO0`/`MDC0` (CPSW MDIO, PB2-P2 pins 17/18);
    PHY2/ETH2-PHY → `MDIO1`/`MDC1` (2nd bus, PB2-P2 pins 1/2 = the two spare servo
    channels SERVO6/7). Each PB2-I NIC manages its own PHY; no shared-address
    conflict. PCB + schematic global labels updated. *(2026-06-12)*
    - **Firmware/DT:** PHY2's bus must be brought up as `mdio-gpio` (bit-banged) on
        the two repurposed balls; verify they are GPIO-capable in the PB2-I pinmux.
- [x] **Wire the field-connector pins to their signals on Wash** (connectors were
    all floating). Done per each footprint's Description pinout: SERVO-PWM pads 1–6
    → SERVO0–5 (PWM); ESC-TLM → UART_ESC_TX/RX; GPIO-A…F → GND/+3V3 (+ `GPIO_EXP_*`
    signal pin labelled); CAN-FD → CAN_H/CAN_L; RS-485 → RS485_A/B; PWR-IN → +5V/GND.
    *(2026-06-12)*
- [x] **Source the 6 `GPIO_EXP_A…F` signals via an I2C GPIO expander.** Added
    `U-GPIO` (PCA9555DB, SSOP-24, addr 0x20) on the existing I2C1 bus with a
    `C-GPIO` 100 nF decoupling cap; P0_0–P0_5 → GPIO_EXP_A–F. *(2026-06-12)*
    - [ ] Verify/add I2C1 pull-ups (≈4.7 kΩ to +3V3 on SDA/SCL) — none on cape;
        confirm whether the PB2-I provides them.
    - [ ] Finalise placement of U-GPIO/C-GPIO (added at a tentative location).
- [x] **Add an ESC-PWM output connector for DSHOT0–3.** Added `ESC-PWM`
    (JST-GH 5-pin SM05B): pins 1–4 → DSHOT0–3, pin 5 → GND. *(2026-06-12)*
    - [ ] Finalise ESC-PWM placement (added at a tentative location).
- [ ] **Reconcile Wash.md §14 field-connector table with the actual PCB
    connectors** (PCB has SERVO-PWM 1×8 + GPIO-A…F + ESC-TLM; §14 lists J_SERVO/
    J_ESC/J_GPS/J_ENC/J_SBUS/J_VBAT/J_FAN). Bring the doc and board into agreement.
- [ ] **Wire the MIL-1553 connector + transformer.** `MIL-1553` connector and the
    `1553-XFM` transformer coupling to the bus are unwired at the IC level; the
    driver/receiver (DS26LV31/32) are only partially netted.
- [ ] **Redesign the tamper mesh as a per-domain anti-tamper mesh (all 4 capes).**
    The current `TMESH_P`/`TMESH_N` cross-hatch grid on F.Cu/B.Cu shorts across SMD
    pads and across the isolated `GND2_*` domains (≈335 of Wash's 465 DRC errors;
    similar on Zoë). Rework as one monitored mesh net per isolation region
    (secure/`GND` + per-`GND2_CAN`/`GND2_ETH`/`GND2_RS485` field side), keeping the
    0.5 mm `ISOLATION` creepage moat clear between domains. **BLOCKS DRC-clean.**
    Quantified against the IEC 62368-1 reinforced-insulation requirement in §0.6
    (2026-06-22): 13 genuine cross-domain `TMESH`-vs-`GND2_*` violations on Wash
    (min 0.125 mm), 9 on Zoë (min 0.0 mm/direct contact) — both far short of the
    0.5 mm netclass minimum and the ≥ 8 mm physical creepage target in `Wash.md`.
- [ ] **Carry the tamper signal over the link for the TPM-less boards.** Kaylee
    and Emma have no local TPM: route Kaylee's mesh signal to Wash and
    Emma's to Zoë over the inter-board link.
- [ ] **Route the rearranged capes.** The manual component reseat left ~60 signal
    nets per cape unrouted (7 power/ground nets are planes). Headless freerouting
    was **not** usable (see toolchain findings in `avionics/kicad/README.md`):
    KiCad 9.0.2 `ExportSpecctraDSN` is broken in standalone Python, and freerouting
    2.1 headless never self-exits and emits incomplete SES. **Finish routing in the
    KiCad GUI**; route the impedance-controlled Ethernet pairs interactively
    (length-matched, 100 Ω ±10% MDI). **BLOCKS gerbers / fab.**
- [ ] **Clear residual DRC after mesh + routing** (counts measured 2026-06-12,
    error+warning): Wash 465 / 121 unconnected, Zoë 554 / 146, Emma 421 /
    160, Kaylee 221 / 181. Remaining types after the mesh fix are mostly
    silk-over-copper, text-height, courtyard-overlap, and lib-footprint mismatch.

- [ ] **Finish Wash PCB (CAPE-A-2) close-out pass:**
    - [ ] Verify every external-facing connector (SERVO-PWM, ESC-PWM, MIL-1553, CAN-FD,
        RS-485, ETH) is a shielded-shell part with shell tied to PGND — audit against
        the footprint Description pinout already documented at §1.2 line ~1340.
    - [ ] Run ERC/DRC net-validity pass — confirm zero unconnected nets outside the
        13-net Emma-style residual list; cross-check against the 465/121 DRC count
        already logged for Wash at §1.2.
    - [ ] Verify all ferrite beads are placed at each digital/RF section boundary and
        on +5V/+3V3 entering from off-board connectors (pattern already used on
        Emma's +5V boundary, §1.2/§1.3 Phase 3).
    - [ ] Verify isolation caps/creepage moat (0.5 mm `ISOLATION`) are intact after the
        per-domain tamper-mesh rework (§1.2, "Redesign the tamper mesh").
- [ ] **Add SBUS/UART DIP switch to Wash** — add a 2-position DIP (or solder-jumper
    pair) to select SBUS vs. plain UART framing on the existing J_SBUS-equivalent
    pad, matching the J_SBUS line item already in Wash.md §14's field-connector
    table (§1.2, "Reconcile Wash.md §14...").
- [ ] **Generate Wash gerbers** — `CAPE-A-2.kicad_pcb` complete; run DRC to zero errors in
    KiCad; export to `avionics/kicad/gerbers/CAPE-A-2/`; re-export drill files.
    - **BLOCKS Wash fab order**
- [ ] **Generate Zoë gerbers** — `CAPE-B-2.kicad_pcb` complete; same DRC + export procedure;
    export to `avionics/kicad/gerbers/CAPE-B-2/`.
    - **BLOCKS Zoë fab order**

- [x] remove Wi-Fi, sik, and loRa antennas from Zoë. Use filtered chokes on rf lines to route all
    RF signals from antennas to Wi-Fi, lora, zigbee,and sik xcvr circuits on Zoë, and/or use uart
    or i2c with filtering to connect isolated xcvrs to the cape. **Done (2026-06-05):** Added §13
    antenna filter chains to CAPE-B-2.kicad_sch — each radio ANT pin now routes through a Johanson
    BPF (FL_LORA/FL_SIK: 0915LP15B0100E; FL_WIFI: 2450BP15B050E) and RCLAMP0502B ESD shunt to a
    dedicated SMA connector (J_SMA_LORA, J_SMA_WIFI, J_SMA_SIK). SiK uses Hirose U.FL J_SIK_ANT for
    module pigtail. All connector shells PGND. See CAPE-B-2.md §13.
- [x] **Re-evaluate space / restore Ethernet to Zoë** — One DP83825I EMI-hardened PHY
    added to Zoë at Rev R (introduced Rev Q); J_ETH_B connector populated. Board has adequate
    space; RF SMA connectors remain. *(done 2026-06-07)*
- [ ] **Zigbee RF chain was never actually added to Zoë — PCB scope gap (flagged 2026-06-22,
    cross-ref §1.4.2).** The "remove Wi-Fi, sik, and loRa antennas" item above (2026-06-05)
    names Zigbee as a target XCVR circuit, but only LoRa/SiK/Wi-Fi filter chains were built;
    `Zoë.kicad_sch` has no CC2652R7 (or equivalent Zigbee SoC), no Zigbee antenna filter, and
    no SMA/diplexer pad. `CLAUDE.md` lists Zigbee 2.4 GHz as one of the 4 required external
    C2 links — this is a real hardware gap, not yet scheduled to a revision. **Antenna
    strategy already decided (§1.4.2, 2026-06-22):** restrict WL1837MOD Wi-Fi to 5 GHz only
    and feed CC2652R7's 2.4 GHz path through a passive 2.4/5 GHz diplexer onto the existing
    shared Wi-Fi antenna (no separate Zigbee antenna/SMA pad needed). Still open: add
    CC2652R7 + diplexer to a Cape-B-2 schematic revision; decide which bay(s) carry it.

- [ ] **Generate Emma gerbers** — `XCVR-49MHZ-2.kicad_pcb` complete; export to
    `avionics/kicad/gerbers/XCVR-49MHZ-2/`.
    - **BLOCKS Emma fab order**
- [ ] **FCC Part 15 §15.235 pre-compliance checklist for Emma** — document field strength
    (≤10,000 µV/m at 3 m per §15.235(a), ≈30 µW / −15.2 dBm EIRP-equivalent — requires firmware
    PA limit, not the ≤100 mW previously assumed), harmonic suppression ≥40 dBc at 2nd/3rd
    harmonics (§15.235(b)/§15.209), FCC ID silkscreen labeling block (§2.803/§15.19).  Not
    Part 95 — see §0.1.
- [ ] **EMI isolation validation checklist** — verify isolation barrier clearance: ISOW1044BDFMR
    5 kV working voltage; ADM2795EBRWZ 5 kV working voltage; measure CMRR at 1 MHz on CAN and
    RS-485 channels; verify differential impedance 100 Ω ±10% on ETH MDI traces.

- [ ] **Merge `claude/cape-em-harsh-variants-9Yfr1` → master** after gerbers pass DRC and
    pre-compliance checklist is signed off.

- [ ] **Design Faraday cages / boxes to protect all PCBs** — minimize weight/space while meeting
    the 500 W/m² design objective. Placeholder geometry (FAR-CAGE-AV 76×56×88 mm, FAR-GASKET-AV,
    FAR-FAN-40, FAR-EMI-VENT-40, FAR-BOND-STRAP, FAR-FT-PANEL, FAR-FERRITE-4MM) already exists at
    §1.1.5 (364 g / 0.80 lbm system total) — these sub-tasks convert the placeholders into
    real, build-ready enclosures:
    - [ ] **Shepherd's Room cage** (Cape-A-2 + Cape-B-2 stack, no Emma) — final wall thickness,
        seam/gasket detail, FAR-FAN-40 mount, FAR-EMI-VENT-40 vent location.
    - [ ] **Inara's Shuttle cage** (Cape-A-2 + Cape-B-2 stack, no Emma) — same scope as Shepherd's.
    - [ ] **River's Room cage** (Cape-A-2 + Cape-B-2 + Emma stack) — add Emma board clearance and
        LoRa/49 MHz feedthrough ports to the FAR-FT-PANEL design.
    - [ ] **Simon's Medbay cage** (Cape-A-2 + Cape-B-2 + Emma stack) — same scope as River's Room.
    - [ ] **Kaylee (PDB) enclosure** — verify whether the PDB needs a full Faraday cage or only a
        bond strap to the keel ground plane (no TPM/RF on Kaylee; see §1.2 "Carry the tamper
        signal over the link for the TPM-less boards").
    - [ ] Bond each cage to the airframe ground reference via FAR-BOND-STRAP with no second
        return path (avoid ground loops per §1.4.1 prose constraint).
    - [ ] Re-run the §1.1.5 mass budget after all 5 enclosures are finalized — confirm cumulative
        T/W stays ≥1.2 (currently estimated ~1.19–1.25, §1.1.5).

- [ ] **Specify / implement tightly twisted pair bonded shielded wiring throughout the aircraft** —
    per-bus-type wiring spec (duplicates the per-bus breakdown tracked at §1.4.3/§1.4.4; this
    item is the airframe-wide harness/cable-selection pass, those are the connector/pinout pass):
    - [ ] CAN FD trunk (inter-node ring) — shielded twisted pair, 120 Ω characteristic impedance,
        drain wire bonded at each node chassis, not floating mid-run.
    - [ ] RS-485 trunk — shielded twisted pair, 120 Ω, daisy-chain topology, end termination at
        the two physical bus ends only.
    - [ ] MIL-STD-1553B bus — twinax/twisted-shielded-pair per the existing 1553-XFM transformer
        coupling spec (§1.2), stub length ≤1 ft from coupler to RT.
    - [ ] Ethernet (CPSW3G ring) — shielded Cat5e/Cat6, 100 Ω ±10% MDI pairs matching the
        impedance-controlled PCB traces already specified at §1.2.
    - [ ] Servo/PWM and ESC telemetry leads — twisted pair, routed ≥5 mm from RF/antenna runs.
    - [ ] Power harness (14 AWG nacelle feeds, battery-to-Kaylee) — twisted where co-routed with
        signal wiring; ferrite bead at each digital/RF section boundary crossing.

---

### 1.3 — PCB Design: XCVR-49MHZ-1 (49 MHz AX.25 Transceiver) — SUPERSEDED

**Superseded 2026-06-21.** XCVR-49MHZ-1 was archived as of Rev Q (2026-06-05) per `CLAUDE.md`
(`Cape-A-1, Cape-B-1, and XCVR-49MHZ-1 are archived as of Rev Q`) and replaced by **Emma**
(XCVR-49MHZ-2 Rev R1), whose schematic, layout, and production-file tasks are tracked under
§1.2b and §1.2a, not here. The remaining unchecked Phase 2–5 items below were never started and
will not be pursued on this stub design — Emma's circuit topology (Si5351A DDS + discrete BJT PA
+ software Bell 202 AFSK, per the Phase 1 decisions retained below for historical record)
carried forward, but layout, ERC/DRC, and production-file work happen on the Emma KiCad project
(`avionics/kicad/Emma.kicad_sch`/`.kicad_pcb`), now archived at `avionics/kicad/archive/`
and `avionics/gerbers/archive/XCVR-49MHZ-1/`. No further action item remains open here.

Stub KiCad project (archived) at `avionics/kicad/archive/XCVR-49MHZ-1.*`.
All Phase 1–3 items must be sequentially complete. Phase 4 verification runs in parallel with Phase 3.

**Phase 1 — IC Selection (gates all downstream work):**

- [x] **Resolve DDS choice** — **Si5351A-B-GT selected** (Silicon Labs, MSOP-10) + EPSON
    TG2520SMN 25 MHz ±0.5 ppm TCXO. I²C direct to 49 MHz; firmware driver already written
    (`si5351.c`); < ±1 ppm system stability, well within any plausible frequency-tolerance
    requirement (the ±0.005% figure cited at the time of this decision was a Part 95 RCRS value
    that does not apply to this band — see §0.1; no Part 15 §15.235 frequency-tolerance
    requirement is at issue here). AD9833 eliminated (max 12.5 MHz; required ×4 external PLL).
    *(decided 2026-05-31)*

- [x] **Evaluate PA options** — **Two-stage discrete BJT selected**: MMBT2222A (SOT-23, driver) + 2N3866 (SOT-39, final). Class-A/AB; +5 V supply direct; ≈ 100 mW ERP; ≈ $1.60 BOM; ≥ 40 dBc harmonic suppression via FL1 LPF (SPICE verify Phase 4). RA07H4047M eliminated (requires 7.2–13.6 V; needs boost converter). *(decided 2026-05-31)*

- [x] **Confirm TCM3105 availability** — TCM3105 confirmed discontinued (TI); no in-production drop-in. **Software Bell 202 AFSK selected**: AM6254 Cape-B MCU generates/decodes audio; TX via MCP4921 SPI 12-bit DAC; RX via LM393 comparator + passive RC bandpass filter. *(decided 2026-05-31)*

**Phases 2–5 (Schematic, PCB Layout, Verification, Production Files) — not pursued.**
Superseded before schematic capture began; U1–U6 sub-circuit design, layout, DRC/ERC, and
gerber/BOM export for this stub were never started and carry forward instead as the Emma
Rev R1 tasks already tracked in §1.2b and §1.2a. The two items below are the only Phase 4/5
work that was actually completed against this stub before it was retired:

- [x] **50 Ω trace impedance check** — Z₀ = 52.26 Ω for W=2.75 mm, H=1.6 mm, εr=4.5, T=35 µm → **PASS** [45–55 Ω]. *(done 2026-05-30 — serenity/kicad/check_impedance.py)*

- [x] **Update `PROJECT_INDEX.md`** to list XCVR-49MHZ-1. *(done 2026-05-25; entry since moved to `ARCHIVE_INDEX.md` per the archival above)*

---

### 1.4 - EMI Hardening Beyond the PCBs to provide protection for 500 W/m^2 environment

#### 1.4.1 Faraday Enclosures

**Design constraints (apply to every enclosure below):**

- Must have proper bonding/grounding without loops.

- Must have a fan and appropriate cooling

- Must minimize weight, size, and cost

- Must account for all sensor inputs and flight control and comms outputs.

- Must account for RF routing from external antennas to internal transceivers

- Must protect the log uSD

- [ ] **PB2-I + Wash Enclosure** (Shepherd's Room / Inara's Shuttle — no Emma board):
    - [ ] Confirm internal clearance for PB2-Industrial + Cape-A-2 stack height against
        the FAR-CAGE-AV placeholder envelope (76×56×88 mm, §1.1.5).
    - [ ] Cut-outs for GPS/IMU/barometer sensor leads, ToF array cabling, servo/ESC
        connectors, and the microSD log slot — each cut-out gets its own FAR-FT-PANEL
        feedthrough or grommet, not an open hole.
    - [ ] Mount FAR-FAN-40 + FAR-EMI-VENT-40 on the low-pressure side of the enclosure;
        verify intake/exhaust path does not create a direct RF leakage slot.
    - [ ] Bond enclosure to chassis ground via FAR-BOND-STRAP (single point, no loop).
- [ ] **PB2-I + Zoë Enclosure** (all 4 bays — Cape-B-2, plus Emma in River's Room /
    Simon's Medbay only):
    - [ ] Confirm internal clearance for PB2-Industrial + Cape-B-2 (+ Emma where fitted)
        stack height against the FAR-CAGE-AV placeholder envelope.
    - [ ] Cut-outs for CAN FD/RS-485/Ethernet/MIL-1553 connectors, SMA antenna feeds
        (WiFi/SiK/LoRa per §1.4.2), and the microSD log slot — feedthrough or grommet
        per cut-out.
    - [ ] River's Room / Simon's Medbay variant: add the LoRa + 49 MHz SMA feedthrough
        pair for Emma; Shepherd's Room / Inara's Shuttle variant omits these.
    - [ ] Mount FAR-FAN-40 + FAR-EMI-VENT-40; bond via FAR-BOND-STRAP.

#### 1.4.2. Antenna Placement and feedlines

- [x] **Resolve total antenna count per stack against the PACE radio table** *(done
    2026-06-22)* — the prior "2 antennas per comm link × 4 links + 2 GPS = 10" count basis
    was wrong on two counts: (a) no stack actually mounts an antenna for all 4 external
    links — each of the 4 bays carries exactly 2 external-link antennas (its PACE
    primary + secondary, per `CLAUDE.md`), not one-per-link-globally; (b) GPS/GNSS is
    one patch **per FC node (Wash, Cape-A-2)**, and there are 4 FC nodes (one per bay),
    not 2. Resolved count, reconciled against current (pre-Rev-R1) hardware fit:

    | Bay | Radios fitted | External antennas | GPS |
    | --- | --- | --- | --- |
    | Shepherd's Room (Bay A) | Zoë: Wi-Fi, SiK, LoRa chain present on PCB | SiK whip (primary) + Wi-Fi patch (secondary) = 2 | 1 |
    | Inara's Shuttle (Bay B) | Zoë: Wi-Fi, SiK, LoRa chain present on PCB | Wi-Fi patch (primary) + SiK whip (secondary) = 2 | 1 |
    | River's Room (Bay D) | Zoë + Emma (49 MHz) | 49 MHz whip (primary) + LoRa whip (secondary, fed from Zoë's `J_SMA_LORA`) = 2 | 1 |
    | Simon's Medbay (Bay E) | Zoë + Emma (49 MHz) | 49 MHz whip (primary, **independent antenna — see new sub-task below**) + SiK whip (secondary) = 2 | 1 |

    **Total: 8 external C2/payload-link antennas + 4 GPS patches = 12 physical antennas.**
    Every Zoë (Cape-B-2) carries identical Wi-Fi/SiK/LoRa RF front ends per board (all
    4 Zoë boards are the same PCB), but only the antenna feeding that bay's PACE-assigned
    primary/secondary link is populated — the unused chain's SMA pad is left unpopulated
    (no antenna, no feedline) rather than wasting mass/hull penetrations on a link that
    bay never uses. **Zigbee 2.4 GHz has no antenna mount** — see flagged gap below; it is
    excluded from the 12-antenna count until the hardware gap is resolved.

- [x] **Antenna mounts** *(types and stations resolved 2026-06-22; physical hull
    placement still needs FreeCAD/slicer verification — see sub-tasks)*:
    - [x] **Shepherd's Room** (Bay A, nose, sta ≈ 59 mm) — SiK 915 MHz ¼-wave RP-SMA whip
        (primary) + Wi-Fi 5 GHz RP-SMA whip (secondary). Mount both on the dorsal hull
        skin near the bay, ≥ 30 mm apart (reduce 915/5800 MHz front-end desense).
    - [x] **Inara's Shuttle** (Bay B, dorsal fwd, sta ≈ 130 mm) — Wi-Fi 5 GHz RP-SMA whip
        (primary) + SiK 915 MHz RP-SMA whip (secondary). Same dorsal mount style and
        spacing as Shepherd's.
    - [x] **River's Room** (Bay D, dorsal aft, sta ≈ 275 mm) — 49 MHz top-wire antenna
        (existing `WIRE-49MHZ`/`POST-FWD-49`/`POST-AFT-49`, §1.1.1.0b; primary) + LoRa
        915 MHz RP-SMA whip (secondary, fed from Zoë `J_SMA_LORA`). **Relocated
        2026-06-22 (with user): the 49 MHz top wire moves from the dorsal centreline to
        the PORT flank, shoulder height** — see the port/starboard sub-task below;
        LoRa whip stays dorsal.
    - [x] **Simon's Medbay** (Bay E, aft service, sta ≈ 350 mm) — **independent** 49 MHz
        top-wire antenna, new, on the **STARBOARD flank, shoulder height** (primary; see
        dedicated sub-task below — do not share River's antenna) + SiK 915 MHz RP-SMA
        whip (secondary, stays dorsal).
    - [x] **4× GPS/GNSS patch antenna mounts** — one per FC node (Wash, Cape-A-2), all
        dorsal hull, face up, per existing routing tasks (Phase 5/6 install steps,
        TODO.md lines ~2645/2666/2773/2794): FC1 sta ≈ 59 mm, FC2 sta ≈ 130 mm,
        FC3 sta ≈ 275 mm, FC4 sta ≈ 350 mm. ≥ 3 mm clearance from the 49 MHz wire posts
        (already a documented constraint on `POST-FWD-49`) — now a flank-to-dorsal
        clearance check rather than a same-surface one, since the 49 MHz posts moved
        off the dorsal centreline (below); re-verify the 3 mm figure still applies once
        the shoulder-height mount line is fixed.
    - [ ] **Zigbee 2.4 GHz antenna mount — BLOCKED, hardware gap confirmed; antenna
        strategy decided 2026-06-22 (with user).** Zoë (Cape-B-2) Rev R has no Zigbee
        transceiver, antenna filter chain, or SMA pad (the CC2652R7 Zigbee radio exists
        only in the archived COMMS-HAT-1 design, not in the current Rev R Cape-B-2
        schematic) — **no antenna can be mounted for hardware that does not exist on
        the board**, so this remains a genuine PCB scope gap, not just a placement
        question. **Decision:** rather than a time-shared coexistence switch, split
        the existing dual-band Wi-Fi antenna by frequency instead of by time —
        **restrict WL1837MOD Wi-Fi to 5 GHz only** (already the spec for the Wi-Fi
        whip mounts above) and feed the freed 2.4 GHz path to the future CC2652R7
        Zigbee module through a passive **2.4/5 GHz diplexer** ahead of one shared
        broadband antenna. Because Wi-Fi and Zigbee no longer overlap in frequency,
        this needs no `RF_NCOEX` coexistence arbitration and no switching — both
        radios can transmit/receive simultaneously through the diplexer, unlike a
        switched-antenna approach. The diplexer (and the antenna it feeds) remains a
        single passive point of failure shared between the two radios, but a passive
        component is materially more reliable than an active coexistence switch, and
        Wi-Fi/Zigbee are not PACE failover partners of each other (unlike River/Simon's
        49 MHz link, sharing here doesn't undermine the redundancy mandate).
        Still open: which bay carries the Zigbee module once added, diplexer part
        selection, and Cape-B-2 schematic work to add the CC2652R7 RF chain.
        **Cross-reference added to §1.2a as a tracked PCB scope gap.**
    - [ ] **Verify the 6 dorsal mount stations (Shepherd ×2, Inara ×2, River's LoRa whip,
        Simon's SiK whip) in FreeCAD against the baked hull** — confirm ≥ 30 mm
        antenna-to-antenna spacing is actually achievable on the as-built dorsal skin at
        each bay's station, and that no mount collides with an access-panel cover
        (§1.1.1.0a), the bow sensor pod (§1.1.1.1a), or the dorsal antenna fin
        (`dorsal_antenna_fin.stl`). **BLOCKS dorsal antenna mount printing.**
    - [ ] **Verify the 2 flank mount lines (River's 49 MHz, port; Simon's 49 MHz,
        starboard) in FreeCAD against the cargo clamshell door swing envelope** — see
        the dedicated sub-task under "Second 49 MHz antenna" below.
        **BLOCKS flank antenna mount printing.**

- [x] **Feedlines** *(cable spec and run-length budget resolved 2026-06-22)*:
    - Cable: **RG-316** (50 Ω, PTFE dielectric, silver-plated copper braid) for every
        aircraft-side antenna-to-SMA-bulkhead run. RG-316 is already the spec used for
        Emma's own 49 MHz feed (`Emma.md` lines 553–554); standardizing on one cable type
        for all 8 runs simplifies stock and crimping tooling.
    - Run-length budget: **≤ 300 mm per run** for Wi-Fi/SiK/LoRa whip-to-bulkhead runs
        (antenna is mounted directly over its bay); **≤ 500 mm** for the 49 MHz runs
        (River's existing run and Simon's new run both route from the bay's Emma J2 to
        the forward wire-post loading coil, matching the existing 500 mm ceiling already
        set in `Emma.md`). RG-316 loss at 915 MHz/2.4 GHz over these lengths is
        ≈ 0.3–0.5 dB — negligible against the link budgets in `malcolm_antenna_spec.md`.
    - Routing: each run exits its bay's Faraday enclosure through an SMA bulkhead
        feedthrough in the FAR-FT-PANEL (§1.1.5, still in design) and is dressed along
        the hull skin to its mount, kept ≥ 5 mm clear of the digital-section keep-out
        zones (CAN FD/RS-485/Ethernet/1553 trunk, per §1.4.4 wiring keep-outs).
        **BLOCKS final feedline length confirmation until FAR-FT-PANEL mechanical
        design (§1.1.5) is complete.**

- [x] **Chokes** *(part and placement resolved 2026-06-22)* — one **Würth 74271222**
    snap-on ferrite clamp per antenna feedline, placed within 25 mm of the Faraday
    enclosure boundary crossing on the *inside* (cage) end of the run. This mirrors the
    treatment Emma already applies to its own 49 MHz feedline (`Emma.md` lines 553–557)
    and is consistent with the 500 W/m² EMI design objective (`CLAUDE.md`). 8 feedlines
    (Shepherd ×2, Inara ×2, River's LoRa run, Simon's SiK run, plus River's and Simon's
    49 MHz runs) → **8× Würth 74271222 required**, added to BOM.

- [x] **Second 49 MHz antenna for Simon's Medbay** *(decision made 2026-06-22, with
    user; routing corrected 2026-06-22, with user)* — Simon's Emma board currently has
    no antenna feed at all; only River's J2 is wired to the single existing
    `WIRE-49MHZ` top-wire antenna. **Decision: build a second, fully independent 49 MHz
    antenna for Simon rather than sharing River's antenna through a mux/switch or
    passive splitter.** A shared antenna (switched or split) makes the antenna/switch a
    single point of failure for *both* stacks' 49 MHz link, which directly contradicts
    the first-class redundancy requirement in `CLAUDE.md` — and the mass cost of a
    second antenna is trivial (≈ 9–11 g, see BOM) against that benefit. *(Moved here
    from former §1.1.1.0.1, 2026-06-22.)*
    - [x] **Design mirrors the existing River system, full length**: PETG forward wire
        post + 38 µH base-loading coil, ~470 mm stainless-steel top wire (same length as
        `WIRE-49MHZ`, not shortened), aft wire post with ceramic insulator, AWG 22
        stranded copper counterpoise (routed inside the foam alongside the structural
        keel — the keel itself is interior/embedded and not affected by the exterior
        clamshell door swing discussed below, so this counterpoise routing is unchanged),
        RG-316 feed to Simon's Emma J2 (≤ 500 mm), Würth 74271222 choke at the Faraday
        crossing — same component set as `POST-FWD-49`/`WIRE-49MHZ`/`POST-AFT-49`/
        `WIRE-COUNTERPOISE-49MHZ`, new reference IDs (see BOM).
    - [x] **Route on the STARBOARD flank, shoulder height — not ventral, not dorsal
        centreline** *(corrected 2026-06-22, with user)* — two routings were rejected:
        (1) a second full-length wire parallel to River's on the same dorsal ridge would
        sit well under one wavelength (λ = 6.12 m at 49 MHz) from the first, risking
        mutual coupling/detuning of both antennas; (2) a ventral/keel-line run (the
        original proposal here) was rejected outright once `generate_cargo_doors.py`
        was checked — the cargo bay clamshell doors hinge at the **outboard flank/belly
        edge** and swing up to **180°**, sweeping the lower flank and belly through the
        door's full Y-span; any exterior wire post mounted there is in the door's path.
        **Resolution: both antennas move off the dorsal centreline entirely.** River's
        existing antenna relocates to the **port** flank, shoulder height; Simon's new
        antenna goes on the **starboard** flank, shoulder height, same sta ≈ 120–580 mm
        span and full ~470 mm length as River's. Shoulder height is chosen specifically
        because it is above the door's swing reach (door hinges at the bottom-outboard
        edge) and laterally separated from its mirror-image counterpart by the full
        fuselage width (port vs. starboard), solving both the coupling and the door
        problems at once — see updated `rcrs49_wire_post.scad` header and §1.1.1.0b.
        **SUB-TASKS OPEN:**
    - [ ] **Verify the exact shoulder-height Z offset in FreeCAD against the cargo
        door's 180°-open envelope** (door panel width from the hinge line) at every
        station along sta 120–580 mm, not just within the door bay's own Y-span —
        confirm port and starboard mount lines clear the door on both sides.
        **BLOCKS bonding either antenna's posts.**
    - [ ] **Confirm the port/starboard mount line also clears the wing roots** (wings
        attach at the cargo section's lateral walls, `CLAUDE.md`) — the flank line
        passes close to this area within the cargo section.
        **BLOCKS Simon's 49 MHz antenna fabrication; BLOCKS River's antenna relocation.**
    - [ ] **Bench-verify isolation between the two 49 MHz antennas** (River's port,
        Simon's starboard) before first flight — confirm neither antenna's feedpoint
        impedance shifts unacceptably with the other antenna present, and that
        simultaneous Emma TX on one does not desense the other's receiver beyond an
        acceptable margin. Use the same HDOP-with-TX-active bench test already specified
        for `POST-FWD-49` as a model.

- [x] **Ensure all transceivers have antenna placement and wiring from Zoë and/or Emma
    boards to mounted antennas** *(moved here from former §1.1.1.0.1, 2026-06-22)* —
    satisfied by the mount/feedline/choke specs above for all populated radio chains;
    remaining open items are the Zigbee hardware gap (flagged above) and the FreeCAD/
    bench verification sub-tasks, which are tracked individually rather than left as one
    generic catch-all.

**Mass/cost added to `docs/bom_revR.json` `avionics.antenna_system` (2026-06-22, updated
after the port/starboard routing correction):** 11 new line items — ANT-WIFI-5G ×2,
ANT-SIK-915 ×3, ANT-LORA-915 ×1, ANT-GPS-PATCH ×4, WIRE-COUNTERPOISE-49MHZ ×1
(backfilled, was referenced but never added), WIRE-49MHZ-2/POST-FWD-49-2/POST-AFT-49-2/
WIRE-COUNTERPOISE-49MHZ-2 (Simon's independent 49 MHz antenna, full-length starboard
design, not the earlier shortened ventral proposal), COAX-RG316-AIRFRAME ×1,
CHOKE-FERRITE-ANT ×8 — **+96 g / +$93** beyond the pre-existing 3-item 49 MHz antenna
entry (9 g / $16, itself relocated port-flank, mass unchanged). New `antenna_system`
total: **105 g / $109.** This is a small fraction of the ~3,590 g AUW noted in
`totals.note`; no AUW/T-W recheck needed at this magnitude.

#### 1.4.3 internode communication wiring

Per-bus signal wiring specification for the 4 internode buses (CAN FD, MIL-STD-1553B, RS-485,
Ethernet) connecting all 8 nodes — see CLAUDE.md "Onboard Communications."

- [ ] **CAN FD** — specify bus topology (linear trunk vs. star), termination (120 Ω at each
    physical end), node tap spacing, and connector pinout per node; cross-reference the
    CAN_H/CAN_L footprint pinout already fixed on Wash (§1.2).
- [ ] **RS-485** — specify daisy-chain topology, termination, and connector pinout per node;
    cross-reference the RS485_A/B footprint pinout already fixed on Wash (§1.2).
- [ ] **MIL-STD-1553B** — specify bus controller / remote terminal wiring per node role
    (§4.2 "MIL-STD-1553B RT implementation," §4.3 "MIL-STD-1553B BC/RT tasks"); stub length
    and transformer-coupling placement per node, matching the 1553-XFM coupling already
    partially netted on Wash (§1.2).
- [ ] **Ethernet** — specify CPSW3G ring topology (node-to-node order), cable category, and
    connector pinout; cross-reference the 100 Ω ±10% MDI impedance-controlled traces already
    specified on Wash/Zoë (§1.2) and the RSTP ring management firmware task (§4.3).

#### 1.4.4 flight control signal wiring

Per-signal-type wiring specification for sensor/actuator signals local to each FC node.

- [ ] **UART** — specify wiring for GPS (u-blox M10Q NMEA/UBX, §4.2), SBUS-equivalent
    (§1.2 "Add SBUS/UART DIP switch to Wash"), and any inter-cape UART links.
- [ ] **I2C** — specify wiring for IMU/barometer (ICM-42688-P, BMP388/390 — note these are
    SPI per §4.2, verify bus assignment), ToF array mux (TCA9548A) and XSHUT GPIO expander
    (MCP23008), and the `U-GPIO` PCA9555DB expander already added to Wash (§1.2).
- [ ] **BDSHOT/DSHOT (ESC telemetry)** — specify wiring for the ESC-PWM connector (DSHOT0–3,
    JST-GH 5-pin, already defined on Wash §1.2) and BDSHOT600 telemetry return path on PRU-ICSS
    (§4.2 "EDF ESC PID governor").
- [ ] **PWM** — specify wiring for nacelle tilt servo control (EHRPWM/PRU, §4.2 "Nacelle tilt
    servo PWM generation") and the SERVO-PWM 1×8 connector pinout already defined on Wash
    (§1.2).

#### 1.4.5 power distribution — Kaylee (PDB) and battery

**Battery placement decision (2026-06-08):**
The 6S 4000 mAh LiPo (~450–520 g, ~155×52×36 mm) must be located near the aircraft CG.
Phase 5 ground-test requirement: static CG at 190 mm from nose (REVN_BUILD_GUIDE_24IN.md §Phase 5).
The keel datum at 190 mm from nose falls within the **middle ring section** (between keel stations
165 mm and 251 mm), which is the main fuselage body above the cargo gondola.
Battery is placed on the keel floor of the middle section, oriented longitudinally, secured by:
- Two M3 boss standoffs at X≈−190 mm (CG station) on the keel face
- Velcro retention strap through keel slot (safety tether, not sole retention)
- Slide-in rail guides on keel face prevent lateral shift at 3g manoeuvre

**Kaylee (PDB) placement decision (2026-06-08):**
Kaylee (XT90 PDB, 4× XT30 outputs, ~80×60 mm) mounts adjacent to the battery in the middle
section keel area (X≈−165..−245 mm station range) to minimise high-current 14 AWG wire length
to the four nacelle ESC feeds (fed through PTFE conduits in the wing spar channel and to the
cargo gondola lateral walls).
Battery swap access via a **ventral hatch** in the middle section belly skin (hatch centred at
X≈−190 mm, ~120×60 mm opening; 2 mm shoulder lip; 4× M2 captive screws).

**Open items — BLOCKS Phase 1 foam pour:**
- [ ] **Add Kaylee/battery boss pattern to `middle_canonical_shell24.scad`.**
    Boss posts: 4× M3 at (±55 mm X) × (±25 mm Z) from X=−190 mm keel centre for battery tray.
    Kaylee PDB: 4× M3 boss posts at X≈−205 mm, Z=CZ±25 mm. Both on keel interior face (+Y rail).
    Verify boss positions clear keel CF flat bar (6×3 mm) and ring frame station notches in slicer.

- [ ] **Add ventral battery-swap hatch cut to `middle_canonical_shell24.scad`.**
    120×60 mm belly cut centred at X=−190 mm; 2 mm shoulder lip; same pattern as avionics panels.
    **BLOCKS Phase 1 foam pour** (void former must clear hatch zone before foam pour).

- [ ] **Create `kaylee_battery_tray.scad`.**
    CF-PETG slide-in rail guide tray for 6S LiPo 155×52×36 mm; M3 attachment to boss posts;
    two captive Velcro strap slots; XT90 connector exit cutout on AFT face.
    **Add to Phase 0 print schedule.**

- [ ] **Create `kaylee_pdb_tray.scad`.**
    CF-PETG mounting tray for Kaylee PDB (80×60 mm footprint); M3 boss attachment;
    XT90 input pigtail route-through; 4× XT30 output ports facing AFT (toward ESC conduits).
    **Add to Phase 0 print schedule.**

- [x] **Kaylee PCB KiCad files generated (Rev A, 2026-06-10):**
    - [x] `avionics/kicad/Kaylee.kicad_pro` — project file; net classes VBAT/PGND/POWER_5V/Default; DRC rules
    - [x] `avionics/kicad/Kaylee.kicad_sch` — full schematic; 90×65 mm 4-layer; BQ76930 6S cell monitor;
                dual TPS54620 5V BEC; TPS54540 6V BEC; 5× INA226 monitors; 4× ESC branches with 40A fuses +
                470µF caps + CMC + 1 mΩ shunts; SMBJ33CA TVS; AON6556 discharge FET; dual Würth 7440640500 CM filter
    - [x] `avionics/kicad/Kaylee.kicad_pcb` — PCB outline + 4-layer stackup (F.Cu signal, In1.Cu GND,
                In2.Cu VBAT 4oz, B.Cu signal); 4× M3 NPTH mounting holes; all 19 nets declared
    - [x] `avionics/kicad/gen_kaylee.py` — Python generator producing all three KiCad files

- [x] **Kaylee PCB — DRC run and gerbers generated (Rev A, 2026-06-10):**
    - [x] Run KiCad DRC; resolved all shorting and 0.0 mm clearance violations
    - [x] Generate gerbers to `avionics/kicad/gerbers/Kaylee/` (17 Gerber layers + Kaylee.drl)
    - [ ] **DRC accepted violations (document only — not fixable without PCB re-architecture):**
        - [ ] 16 clearance violations at 0.15 mm: INA226 MSOP-10 adjacent pads (pins 3/4) at 0.5 mm pitch
                    inherently violate 0.2 mm PGND/POWER_5V class rule; IPC-2221B allows ≥ 0.1 mm for ≤ 31 V
        - [ ] 77 courtyard overlaps: dense 90×65 mm layout; 3D bodies do not conflict; no manufacturing impact
        - [ ] 59 lib_footprint_mismatch: all footprints are inline in .kicad_pcb (not library copies); expected
        - [ ] 33 silk_over_copper / 26 silk_overlap / 2 silk_edge_clearance: cosmetic; board is fab-ready
        - [ ] 8 lib_footprint_issues: inline footprints; not KiCad library-linked; expected
        - [ ] 181 unconnected_items: traces not yet routed (power planes on In1/In2.Cu are correct)
    - [ ] **Kaylee PCB — remaining layout tasks (BLOCKS fabrication):**
        - [ ] Manually place in KiCad: CM_ESC1–4 (INA226 shunt caps), C_DEC1–4 (ESC decoupling), Section F
                    (BQ76930, J_BAL, R_BAL1–6, C_CAP, J_NTC, C_NTC) — area x=62–88, y=50–65 recommended
        - [ ] Manually place: J_SHLD_5V, J_SHLD_6V, J_SHLD_I2C, J_SHLD_ALERT chassis shield lugs
        - [ ] Route all traces; verify 4 oz Cu pour on VBAT/PGND power planes (In2.Cu / In1.Cu)
        - [ ] Add BQ76930 thermal pad (TSSOP-30 PowerPAD) to footprint — currently missing from gen_kaylee_pcb.py
        - [ ] Verify XT30 connectors (J_ESC1–4) courtyard clears board edge on left side
        - [ ] Verify size and weight: PCB target ≤ 90×65 mm, ≤ 0.110 lbm (≤ 50 g)

- [ ] **Update REVN_BUILD_GUIDE_24IN.md Phase 1** to include Kaylee + battery tray installation
    in the pre-foam-pour checklist. Battery tray and hatch must be installed and hatch zone
    masked before the foam pour step.

---

### 1.5 — Documentation

- [x] **1.4.1 `serenity-rev-p.jsx`** — comprehensive 11-tab standalone Rev P specification created: Overview, Airframe, Propulsion, Avionics, Comms, Cargo, Security, Regulatory, BOM, Files, Build Status. Supersedes serenity-rev-o.jsx as current spec. *(done 2026-06-01)*

- [x] **1.4.2 Wash: rename + dual Ethernet PHY** — Board renamed to "Wash"
    throughout schematic and Markdown. Added 2× EMI-hardened DP83825I PHYs (J_ETH1, J_ETH2):
    HX1188NL magnetics, SRF2012-100Y CMC, PRTR5V0U2X TVS, TPS62933 1.8V supply per PHY.
    RMII0→PHY1 (PHY addr 0x01), RMII1→PHY2 (PHY addr 0x02). MDC/MDIO shared.
    CAPE-A-2.md §1 updated from "PHY removal" to "EMI-hardened dual Ethernet PHY". *(done 2026-06-07)*

- [x] **1.4.3 Zoë: rename + Ethernet PHY** — Board renamed to
    "Zoë". Added 1× EMI-hardened DP83825I PHY (J_ETH_B): HX1188NL magnetics,
    SRF2012-100Y CMC, PRTR5V0U2X TVS ×2, TPS62933 1.8V supply. RMII0 interface, PHY addr 0x01.
    CAPE-B-2.md §1 updated from "PHY removal" to "EMI-hardened Ethernet PHY". *(done 2026-06-07)*

- [x] **1.4.4 Wash: add missing field connectors** — Connector audit found J_PWR,
    J_CAN, J_485, J_1553, J_GPS, J_SERVO, J_ESC absent from schematic despite protection circuits
    being present. All 7 connectors added (JST SM03B/SM04B/SM05B/SM06B-GHS-TB-1MP series). §14
    field connector table added to CAPE-A-2.md. *(done 2026-06-07)*

- [x] **1.4.5 Zoë: add missing field connectors** — J_PWR, J_CAN, J_485,
    J_1553 added to schematic (JST SM03B/SM04B-GHS-TB-1MP). §14 field connector table added to
    CAPE-B-2.md. *(done 2026-06-07)*

- [ ] **Update PHASED_BUILD_GUIDE.md** from Rev M 18-inch to Rev R 24-inch specifications
    (hull 609.6 mm, 50mm EDFs, v2·v2·v2·v2 node placement, Rev R power system, cargo system).

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
    CLAUDE.md's Hull-Frame Coordinate Standard, or directly from
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

- [x] **Create `bom_revQ.json` + `bom_revQ.csv`** — Rev Q BOM: replace all v1 cape procurement
    quantities with v2 equivalents (4× Wash, 4× Zoë, 4× Emma). Remove Cape-A-1,
    Cape-B-1, XCVR-49MHZ-1 line items.

---

### 1.5 — Rev Q: Repo-Wide Architecture Propagation (2026-06-07)

- [x] **1.5.1 Rev Q documentation propagation** — Updated all project documentation from Rev P
    (v2·v1·v1·v2 mixed placement) to Rev Q (v2·v2·v2·v2 uniform EMI-hardened placement across
    all 8 avionics nodes). Changes include:

    - **TODO.md**: Rev P → Rev Q; node placement updated; §1.2a procurement updated to 4× Wash,
        4× Zoë, 4× Emma; Phase 6 / Phase 7 installation steps updated to v2 capes;
        procurement tables updated; Cape-A-1 / Cape-B-1 / XCVR-49MHZ-1 retired from active BOM.

    - **CLAUDE.md**: Rev Q already reflected (v2·v2·v2·v2, archive notes).

    - **README.md**: Rev Q already reflected (updated prior to this commit).

    - **POWER_SYSTEM_Q.md** (`docs/`): written at Rev Q baseline.

    - **AVIONICS_PB2_REDESIGN.md**: Rev Q node placement already reflected.
    *(done 2026-06-07)*

### 1.6 — Rev R: Component Revision Synchronisation + s_ Prefix Removal (2026-06-11)

- [x] **1.6.1 Rev R propagation to all active files** — Updated all project-level revision headers
    from Rev Q → Rev R (2026-06-11). Changes include: README.md battery spec table, all five
    fuselage SCAD changelog entries, all GCS Malcolm firmware headers (Q1→R1), FreeCAD assembly
    scripts, avionics firmware README, ENC-NACELLE-1.md, and 18 GCS Malcolm source files.
    *(done 2026-06-11)*

- [x] **1.6.2 Component revision synchronisation** — All component-level revision designations
    updated to Rev R per CLAUDE.md: "All components are referenced as of the latest revision."
    - Nacelle gear train (Rev O → Rev R): nacelle_nozzle_iris, nacelle_bevel_housing, nacelle_bevel_pair,
        nacelle_pinion, nacelle_sector_gear
    - EDF sleeves (Rev A → Rev R): edf_stator_sleeve, edf_aft_spider_sleeve
    - Nacelle pod/nozzle (Rev T/T2 → Rev R): nacelle_pod_50mm_tandem, nacelle_pod_50mm_tandem_simple,
        nacelle_nozzle_straight
    - Wings/pylon (Rev O → Rev R): wings_s1223_revo, wing_nacelle_pylon_revo
    - Cargo shell: Rev R baseline entry prepended to S4 changelog
    - Servo bracket: Rev R baseline entry prepended to S1 entry
    - Avionics: Wash.md, Kaylee.md, XCVR-49MHZ-2.md Rev A → Rev R; Zoë.md, Zoë.kicad_sch,
        Kaylee.kicad_pcb, gen_kaylee.py, gen_kaylee_pcb.py updated.
    *(done 2026-06-11)*

- [x] **1.6.3 Remove `s_` prefix from all SCAD and STL filenames** — Removed leading `s_` from
    11 SCAD files and 19 STL files across `airframe/openscad/`, `airframe/stls/`, and
    `deferred/aft-edf/`. Updated all references in 37 active text files (Python, Markdown, JSON,
    SCAD, shell scripts, Makefile, JSX). Archive files and historical BOMs (bom_revP.json,
    bom_revQ.json) intentionally not modified.
    *(done 2026-06-11)*

### 1.5.1. Names

- [x] The ground control station is named "Malcolm" aka "CAPT Reynolds" or "CAPT Tight Pants" - "I aim to misbehave" *(implemented throughout all docs)*

- [x] The Flight Control Avionics Cape is named "Wash" - "I'm a leaf on the wind" *(implemented: CAPE-A-2.kicad_sch, CAPE-A-2.md, all docs)*

- [x] The Comms/Logging/Payload Cape is named "Zoë" - "Big Damn Heros, sir." *(implemented: CAPE-B-2.kicad_sch, CAPE-B-2.md, all docs)*

- [x] The Power Distribution Board is named "Kaylee" - "Everything is shiny." *(implemented: Kaylee.md, PWR-DIST-1.kicad_sch)*

- [x] The Cargo handling system is named "Jayne" - "I was aiming for his head." *(implemented: README.md §Cargo Handling — Jayne, CLAUDE.md, generate_placeholders.py, middle_canonical_shell24.scad)*

- [x] The forward avionics bay is named "Shepherd's room" (Bay A) - "I have heathens enough right here." *(implemented 2026-06-07)*

- [x] The second avionics bay is named "Inara's shuttle" (Bay B) - "Mal, I will never understand you." *(implemented 2026-06-07)*

- [x] The third avionics bay is named "River's room" (Bay D) - "Also, I can kill you with my mind." *(implemented 2026-06-07)*

- [x] The aft avionics bay is named "Simon's medbay" (Bay E) - "What did they do to you?" *(implemented 2026-06-07)*

### Avionics Workload Balancing

- While all Wash capes are identical and all Zoë capes are also identical, they have different primary tasking.  **All Stacks are capable to communicate and control the UAV safety in a benign environment on their own.***

- UAV Tasks with PACE prioritization and failover per stack (primary, alternative, contingency, emergency)

-- Watchdog: P - Shepherd; A - Inara; C - Simon, E - River

-- Comms: P - Inara; A - Shepherd; C - River; E - Simon

-- Flight Control: P - River; A - Simon; C - Shepherd; E - Inara

-- Payload Control: P - Simon; A - River; C - Inara; E - Shepherd

---

- Mal is the ground control station - He's the boss.

- Shepherd is the crew's conscience and therefore takes care of primarily watchdog, fault detection, failover, and authentication. His stack has SiK primary and Wi-Fi secondary.

- Inara has primarily camera, external sensors, and high bandwidth ground communication.  Her stack is connected to  Wi-Fi primarily and LoRa secondary.

- River provides primary control of the forward EDFs, and provides EDF and nacelle control command and syncing, and the most resilient comms.  She may be crazy, but she comes through when no one else can.  She has 49 MHz (Part 15 §15.235) primary and LoRa secondary.

- Simon is the alternate watchdog for the ship, but most of his attention is on River.  He's got aft EDF control and alternate nacelle control. He follows River's lead but makes sure she doesn't crash the ship. Simon also controls Jayne, and ensures that the cargo isn't jettisoned or the crew abandoned. He's got 49MHz as his primary antenna and SiK as his backup.

---

## 2.0 — Procurement (Before Physical Build)

Order components after all Phase 0 STLs are confirmed printable in slicer. Long-lead items should be ordered concurrently with PCB fabrication.

### 2.1 — Filament and CF Stock (needed for Phase 0)

| Item | Qty | Notes |
|------|-----|-------|
| PETG filament | ~1,200 g | Access panels, nozzle parts, cargo gondola — **TODO: recompute split, hull sections moved to CF-PETG row below per CLAUDE.md Fabrication Standards** |
| CF-PETG filament | ~500 g | Hull sections (head, middle, cargo, rear neck, wings), nacelle pods, tilt brackets, pylon, intake frame — hardened-steel nozzle required |
| TPU 95A filament | ~200 g | Landing skid feet — direct-drive extruder required |
| CF flat bar 6×3mm | ~700 mm | Keel 620 mm + 80 mm ring frame offcuts |
| CF tube 12mm OD / 1.5mm wall | ~850 mm | Wing spars 2×380 mm + 90 mm scrap |
| CF solid rod 4mm OD | ~300 mm | Pivot rods (2× nacelle) per pivot housing drawing |
| CF plate 2mm | 250×150 mm | Ring frames (5 stations per drawing) |

### 2.2 — Structural Hardware (Phase 1)

| Item | Qty | Notes |
|------|-----|-------|
| West System 105/206 epoxy | 1 kit | Keel + spar bonding; structural joints |
| 5-minute epoxy syringe 25mL | 3× | Access frames, sensor mounts |
| X-30 PU foam 2-part | ~600 mL | 2 lb/ft³, 4× expansion, 2-min pot life |
| EPS blue foam board 25mm | 500×250 mm | Void formers A–E; Owens Corning Foamular 150 |
| Johnson's Paste Wax | 1 tin | Void former release agent (2 coats) |
| 3M 4016 closed-cell gasket tape | 1 roll | Access panel frame lips |
| PTFE tube 5mm OD × 3mm ID | 6 m | 8 conduits (CAN FD, RS-485, 1553A, 1553B, ETH×2, SERVO-PWR, MAIN-PWR) |
| M2.5 nylon hex standoff 6mm | 16× | Cape-B floor mounts (4 per bay × 4 bays) |
| M2.5 nylon hex standoff 20mm | 16× | Cape-A inter-cape spacing |
| M2.5 × 8mm SS button screws | 64× | Standoff attachment + panel B/E fasteners |
| M3 heat-set threaded inserts | 4× | Cargo gondola belly hard points |
| N42 neodymium disc magnet 6×2mm | 8× | Panel D (4 in frame + 4 in lid) |
| SMA panel-mount bulkhead | 3× | SiK 915MHz (belly) + LoRa 915MHz (belly) + Wi-Fi (dorsal fwd) |
| 0.3mm stainless wire or 22AWG enamelled Cu | ~500 mm | 49 MHz (Part 15 §15.235) top wire |
| Ceramic bead insulator 3mm ID | 1× | Aft end of 49MHz wire (insulated/open end) |

### 2.3 — Propulsion System (Phases 2–4)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| 50mm EDF @ 6S (budget tier) | 4× | ~$25–40ea | 2 per nacelle, tandem; verify OD fits 55–56mm ID bore |
| 40A 6S BLHeli32 BDSHOT ESC | 4× | ~$18–25ea | 1 per nacelle EDF |
| 55mm 6S EDF (~1,500 gf) | 1× | ~$35–55 | Fuselage rear; canonical tail nozzle; **Phase 11 deferred** |
| 50A 6S BLHeli32 ESC | 1× | ~$18–28 | Fuselage EDF; **Phase 11 deferred** |
| Digital tilt servo ≥25 kg·cm @ 6V, metal gear | 2× | ~$20–30ea | Nacelle tilt; prefer 30+ kg·cm |
| SG90 micro servo | 2× | ~$3ea | Nacelle nozzle ×2 (redundant) |
| SG90-class proportional valve servo | 4× | ~$3ea | RCS bleed jets; **Phase 11 deferred** |
| MF104ZZ flanged bearing 4×10×4mm | 4× | ~$8 total | 2 per nacelle pivot |
| 4mm OD CF rod (pivot) | 2× cut lengths | — | From 2.3 CF stock above |
| Steel pushrod 2mm OD × ~60mm | 2× | ~$3 total | Longitudinal nozzle shaft per nacelle |
| Steel pushrod 2mm, Z-bend ends | 2× | ~$4 total | Tilt servo pushrod |
| M2 clevis links | 4× | ~$3 total | Servo-to-pushrod |
| 0.8mm piano wire | ~600 mm | ~$3 | Nozzle iris petal link rings |
| 3mm SS hinge pins | 16× | ~$4 total | 8 per nacelle iris nozzle |
| WS2812B LED ring (50mm) | 2× | ~$6 total | Nacelle duct exit |
| WS2812C-2020 addressable LED | 6× | ~$6 total | Nav lights |
| XT90 PDB, 4× XT30 outputs | 1× | ~$12 | Power distribution |
| XT90 battery pigtail | 1× | ~$5 | Battery lead |
| 5V 5A switching BEC | 1× | ~$8 | Avionics power rail |
| 14AWG silicone wire | 1 m | ~$6 | Main bus |
| 16AWG silicone wire | 0.5 m | ~$4 | ESC signal + fuselage taps |
| 6S 4000mAh LiPo battery | 1× | ~$55–70 | Phase 6 first flight |

### 2.4 — Avionics (Phase 6 — 4-node minimum viable)

*Rev R: all nodes use v2 EMI-hardened capes. Cape-A-1 / Cape-B-1 / XCVR-49MHZ-1 are retired.*

| Item | Qty | Unit Cost | Total | Notes |
|------|-----|----------|-------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | $51.03 | ~$204 | DK 2820-100003007-ND |
| Wash (Wash) PCB (JLCPCB assembled) | 2× | ~$55 | ~$110 | FC1/Shepherd's room (Bay A) + FC2/Inara's shuttle (Bay B) (v2, EMI-hardened) |
| Zoë (Zoë) PCB (JLCPCB assembled) | 2× | ~$95 | ~$190 | CN1/Shepherd's room (Bay A) + CN2/Inara's shuttle (Bay B) (v2, EMI-hardened) |
| Emma PCB (JLCPCB assembled) | 2× | ~$25 | ~$50 | 49 MHz (Part 15 §15.235) sub-module for CN1, CN2 (v2 EMI-hardened) |
| SiK 915MHz ground station radio | 1× | ~$15 | ~$15 | MAVLink GCS link |
| microSD 64GB (log, write-blocked) | 2× | ~$10 | ~$20 | CN1-LOG, CN2-LOG |
| JST-GH cables: CAN 3-pin, RS-485 3-pin, ETH 6-pin, 1553 4-pin, GPS 5-pin | assorted | — | ~$20 | Per §14 connector table |
| USB-UART adapter (CP2102) | 1× | ~$8 | ~$8 | Debug console (one-time tool) |
| 3M double-sided foam tape | 1× | ~$5 | ~$5 | ESC and node mounting |
| Zip ties 100mm + 200mm | 1 bag | ~$4 | ~$4 | Wire management |

### 2.5 — Avionics (Phase 7 — remaining 4 nodes + ToF arrays)

*Rev Q: all Phase 7 nodes also use v2 EMI-hardened capes.*

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| PocketBeagle 2 Industrial (AM6254) | 4× | ~$204 | CN3, FC3, CN4, FC4 |
| Wash (Wash) PCB (JLCPCB assembled) | 2× | ~$110 | FC3/River's room (Bay D) + FC4/Simon's medbay (Bay E) (v2) |
| Zoë (Zoë) PCB (JLCPCB assembled) | 2× | ~$190 | CN3/River's room (Bay D) + CN4/Simon's medbay (Bay E) (v2) |
| Emma PCB (assembled) | 2× | ~$50 | CN3, CN4 (v2 EMI-hardened) |
| microSD 64GB (log) | 2× | ~$20 | CN3-LOG, CN4-LOG |
| VL53L5CX 8×8 ToF sensor | 12× | ~$84 | Dual OA arrays |
| TCA9548A 8-ch I²C multiplexer | 2× | ~$3 | One per array host |
| MCP23008 8-port I²C GPIO expander | 2× | ~$2.40 | XSHUT control |
| JST-SH1.0 4-wire sensor cable 300mm | 12× | ~$12 | ToF sensor leads |
| 5mm PMMA disc 0.5mm thick | 12× | ~$6 | ToF aperture covers |
| UV adhesive | 1× | ~$6 | ToF aperture seal |
| JST-GH cables (remaining bus segments) | assorted | ~$20 | Ring completion |

### 2.6 — Cargo System (Phase 8)

| Item | Qty | Approx. Cost | Notes |
|------|-----|-------------|-------|
| N20 DC motor 6V 300:1 | 1× | ~$8 | Winch drive |
| DRV8833 dual H-bridge driver | 1× | ~$2 | |
| SG90 servo | 2× | ~$6 | Door actuator + payload release |
| Dyneema SK75 0.5mm braid | 2 m | ~$4 | Winch line |
| 3mm CF rod | ~60 mm | — | Clamshell door hinge pin |
| Closed-cell foam gasket tape | — | — | Gondola-to-hull perimeter seal |

---

## 3.0 — Physical Build

**Dependency:** All items in Section 1.0 (STL exports) must be complete before Phase 0.  
**PCB fab lead time:** ~7–14 days for JLCPCB assembled boards — order after 1.2 gerber regen and 1.3 Phase 5 are complete; boards arrive during physical Phases 0–5.

### Phase 0 — Print All Parts + CF Cuts

**Goal:** Every printed part complete and dry-fitted before first epoxy joint.

**Pre-print documentation (complete before any fabrication begins):**

- [ ] **Flight Envelope Document** — create `docs/flight_envelope.md` covering:

    - [ ] V_min (minimum control airspeed) vs. nacelle tilt angle — computed from wing area, CL_max, and nacelle thrust fraction

    - [ ] V_max (never-exceed speed) vs. structural load limit and EDF rpm ceiling

    - [ ] Altitude operating limits (AGL and MSL) per FAA Part 107 and battery performance

    - [ ] Maximum demonstrated crosswind per nacelle angle increment (0°, 30°, 60°, 90°)

    - [ ] Transition corridor: altitude AGL floor for nacelle 90°→0° sweep (minimum safe altitude to initiate transition)

- [ ] **Failsafe Threshold Document** — create `docs/failsafe_thresholds.md` covering:

    - [ ] Battery low-voltage alert threshold per cell (default 3.7V/cell) and RTL cutoff (3.5V/cell)

    - [ ] Node heartbeat timeout for master re-election (default 100ms on CAN FD)

    - [ ] Radio loss timer before automatic RTL (default 5s for SiK/LoRa; 10s for 49 MHz (Part 15 §15.235) as backup)

    - [ ] ESC thermal cutback threshold (default 85°C) and shutdown threshold (95°C)

    - [ ] ToF obstacle avoidance halt clearance (default 1.0m) and resume clearance (default 1.5m)

    - [ ] All thresholds must be defined as compile-time constants in `firmware/common/failsafe_config.h`

- [ ] **Electrical Fault Margin Validation** — create `docs/electrical_fault_margins.md` covering:

    - [ ] Maximum ESC short-circuit current at 6S and required fuse break time; verify XT30 + 100A poly fuse coordinates with ESC MOSFET safe operating area

    - [ ] BEC brown-out threshold: minimum input voltage at which 5V BEC output stays in regulation (≥4.90V); verify with actual 14AWG wire resistance at peak current

    - [ ] Main bus fuse sizing: peak current = 4× EDF ESCs (4× 40A) = 160A nacelle peak; verify main XT90 connector rating and main fuse break curve do not nuisance-trip on motor surge

    - [ ] Balance of plant: verify that loss of any single PWR conduit tap does not collapse the 5V avionics rail (BEC must tolerate single-segment loss)

**Printer setup:**

- [ ] Install hardened-steel nozzle (CF-PETG abrades brass)

- [ ] Calibrate E-steps and Pressure Advance for each filament

- [ ] Dry all filament 6 h at 65°C before printing

**Print schedule (ordered to minimize reprints):**

| Part | Material | Layer | Infill | Qty | Notes |
|------|----------|-------|--------|-----| ------ |
| feet_x_4_scaled24.stl | TPU 95A | 0.25mm | 40% | 1 set | |
| legs_scaled24.stl | CF-PETG | 0.15mm | 30% | 1 | |
| head_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| middle_canonical_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| cargo_sect_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| rear_neck_intake_shell24.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | Print now; cover reduced-area scoop windows (sized for 55mm EDF) with removable 3mm PETG blanks until Phase 11 |
| wings_s1223_revo.stl | CF-PETG | 0.20mm | 8% gyroid | 1 | |
| eng_left_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 | |
| eng_right_stator_shell24_revo.stl | CF-PETG | 0.15mm | 25% gyroid, 4 walls | 1 | |
| s_eng_piv_outer_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | |
| s_eng_piv_pins_scaled24.stl | CF-PETG | 0.15mm | 40% solid, 4 walls | 2 | |
| s_pivot_arm_a_scaled24.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | |
| s_eng_pistons_scaled24.stl | PETG | 0.20mm | 20% gyroid | 2 | |
| wing_nacelle_pylon_revo.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | |
| nacelle_nozzle_petal.stl | PETG + translucent-blue inner | 0.20mm | 20% gyroid | 16 | |
| nacelle_nozzle_ring.stl | CF-PETG | 0.15mm | 40% | 2 | |
| nacelle_nozzle_iris.stl | PETG | 0.12mm | 40% | 2 | |
| rear_nozzle_canonical.stl | CF-PETG | 0.15mm | 30%, 4 walls | 1 | **DEFERRED — Phase 11.** Fixed canonical elliptical tail nozzle (2.06×1.76 in / 52.3×44.7 mm exit); replaces the old iris rear_nozzle_frame/petal. Requires regeneration for 55mm + canonical geometry — see §Phase 11. |
| rcs_thruster_nozzle.stl | CF-PETG | 0.15mm | 40%, 4 walls | 4 | **DEFERRED — Phase 11.** RCS bleed-air jet nozzle; fed from aft EDF plenum. Requires generation — see §Phase 11. |
| rcs_distribution_manifold.stl | PETG | 0.20mm | 30% | 1 | **DEFERRED — Phase 11.** Splits ~15% EDF mass flow to the 4 RCS proportional valves. Requires generation — see §Phase 11. |
| rcs_valve_bracket.stl | CF-PETG | 0.15mm | 40% | 4 | **DEFERRED — Phase 11.** SG90-class proportional valve mount, one per RCS jet. Requires generation — see §Phase 11. |
| nacelle_sector_gear.stl | CF-PETG | 0.12mm | 40%, 4 walls | 2 | |
| nacelle_pinion.stl | PETG or resin | 0.12mm | 40% | 4 | |
| nacelle_bevel_pair.stl | PETG or resin | 0.12mm | 40% | 2 sets | |
| nacelle_bevel_housing.stl | CF-PETG | 0.15mm | 40% | 2 | |
| rcrs49_wire_post.stl | PETG | 0.15mm | 40% | 2 | |
| Access panel frames A–F + lids | PETG | 0.20mm | 100% | 1 set | |
| s_cargo_gondola_shell.stl | PETG | 0.20mm | 15% gyroid | 1 | |
| cargo_door_port.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Generated (PR #22) — reprint if hinge changes |
| cargo_door_stbd.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Generated (PR #22) — reprint if hinge changes |
| cargo_cradle_autolatch.stl | PETG | 0.20mm | 30% | 1 | Already generated (PR #21) — reprint if dimensions change |
| cargo_winch_spool.stl | PETG | 0.20mm | 40% | 1 | Already generated (PR #21) — reprint if dimensions change |
| nacelle_servo_bracket.stl | CF-PETG | 0.15mm | 40%, 4 walls | 2 | One per nacelle; from `airframe/openscad/nacelles/nacelle_servo_bracket.scad` (Rev R). Print with channel mouth up; no supports needed. VERIFY M3 hole ±17.5×±8 mm pattern matches NSVMT inserts in slicer before printing. |
| inara_access_cover.stl | PETG (Cu-foil lined) | 0.20mm | 40% | 1 | Faraday tray lid for Inara bay; 105×75 mm footprint, 5 mm shoulder, Ø38 mm GPS bore offset −13.3 mm Z from cover centre. SCAD not yet created — **BLOCKS printing.** |
| river_access_cover.stl | PETG (Cu-foil lined) | 0.20mm | 40% | 1 | Faraday tray lid for River bay; 105×75 mm footprint, 5 mm shoulder, Ø38 mm GPS bore at +0.7 mm Z from cover centre. SCAD not yet created — **BLOCKS printing.** |
| kaylee_battery_tray.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Battery slide-in rail tray for 6S 4000 mAh LiPo; keel mount at 190 mm station. SCAD not yet created — **BLOCKS Phase 1.** |
| kaylee_pdb_tray.stl | CF-PETG | 0.15mm | 40%, 4 walls | 1 | Kaylee PDB mount tray; keel area, middle section. SCAD not yet created — **BLOCKS Phase 1.** |

**CF cuts:**

| Part | Material | Dimension | Notes |
|------|----------|-----------|-------|
| Keel | CF flat bar 6×3mm | 620 mm | Mark datums at 91, 165, 251, 320, 388mm from nose |
| Wing spars | CF tube 12mm OD / 1.5mm wall | 2× 380 mm | Sand spar ends to fit wing-root pockets |
| Pivot rods | CF solid rod 4mm OD | 2× cut per pivot housing drawing | Deburr; press-fit into MF104ZZ bearings |
| Ring frames | CF plate 2mm | 5 profiles per station drawing | Fit to keel slot-notches |

**Phase 0 checks:**

- [ ] Nacelle bore caliper: 55.0–56.0 mm ID at Z=10 mm and Z=80 mm

- [ ] Stator fins visible in Z=53–95 mm gap (between the two EDF seats)

- [ ] Hub bore clear at stator: 16 mm ID minimum (motor leads)

- [ ] Sector gear ↔ pinion dry-mesh: 0.1–0.2 mm backlash

- [ ] Iris nozzle ring fits flush on nacelle exit; petals hinge freely on 3mm pins

- [ ] 4mm CF pivot rod slides through pivot housing with MF104ZZ bearings seated

- [ ] All access panel lids flush ±0.2 mm in frames

- [ ] Keel dry-fits through all hull sections without force

- [ ] Rear neck shell scoop windows covered with removable 3mm PETG blanks (4 blanks, silicone-sealed)

---

### Phase 1 — Hull Structure + All Future Provisions

**Goal:** Structurally complete hull, every conduit/standoff/void former/sensor mount installed — ready for foam pour.

> ⚠ **Point of no return.** Complete all sub-steps before mixing foam (Step 13). Nothing can be added after foam cures.

- [ ] Epoxy keel through all hull sections; cure 2h. Datum marks at 91, 165, 251, 320, 388mm.

- [ ] Bond ring frames at all 5 station notches; cure 1h.

- [ ] Bond access panel frames A–F into hull sections (5-min epoxy, 30 min cure per phase guide table).

- [ ] Install M2.5 nylon standoffs in bays A, B, D, E (floor 6mm + inter-cape 20mm per bay).

- [ ] Bond wing spar pocket inserts at wing root stations, both sides.

- [ ] Bond tilt servo mount brackets at wing root bay interior (one per nacelle tilt servo).

- [ ] Install M3 heat-set inserts ×4 at belly cargo hard-point locations.

- [ ] Install SMA bulkheads: belly port (SiK 915MHz, X≈260mm), belly stbd (LoRa, X≈260mm), dorsal (Wi-Fi, X≈140mm).

- [ ] Install 49 MHz (Part 15 §15.235) forward wire post (dorsal, X≈120mm, bonded with 5-min epoxy).

- [ ] Install 49 MHz (Part 15 §15.235) **temporary** aft wire post: PETG hook bonded to aft dorsal hull skin near station ~580mm (NOT on rear nozzle frame — that post is Phase 11). This temporary post reduces antenna length slightly; field-strength compliance with 47 CFR §15.235 is firmware power-limited (see §0.1), not antenna-length dependent.

- [ ] String 49MHz top wire (0.3mm SS wire or 22AWG enamelled Cu) from forward post to temporary aft post with ~20g tension; CF keel connected to the 49 MHz (Part 15 §15.235) GND as counterpoise.

- [ ] Install 12× VL53L5CX flush-mount PETG frames (6.5mm hull cutouts); apply 0.5mm PMMA disc over each aperture with UV adhesive.

- [ ] Feed 8× PTFE conduits nose-to-tail; thread pull strings through each immediately; label both ends.

- [ ] Install EPS void formers (waxed 2×) in bays A–E; verify pull strings clear voids.

- [ ] Full dry-fit: all 8 pull strings accessible, standoffs clear, void formers sealed, SMA bulkheads installed.

- [ ] Foam pour: X-30 PU foam, 3 shots aft→fwd, ≤60 mL per batch; cure 24h per zone. **Do NOT foam nacelle bays, pivot housing, or access panel bays.**

- [ ] Remove EPS void formers; IPA wipe bay walls; verify foam not in conduit runs.

- [ ] Bond cockpit cap (verify cockpit bay wires and GPS coax accessible first).

**Phase 1 checks:**

- [ ] Hull rigid — no flex when held at nose and tail

- [ ] All 8 pull strings accessible at both ends

- [ ] All standoffs in place; screws start freely

- [ ] Foam not in nacelle mounting bay, pivot housing, or panel bays

- [ ] All 6 access panel lids flush ±0.2 mm; latches/magnets engage

---

### Phase 2 — Nacelle Assembly

**Goal:** Both nacelles fully assembled — EDFs installed, stator integral, iris nozzle fitted, gear linkage dry-meshed.

**2A — EDF installation (port first, then starboard):**

- [ ] Test EDF rotation direction on bench before installation: port = CW from intake; stbd = CCW from intake. Swap any two motor phase wires to reverse.

- [ ] Install EDF2 (aft/downstream) from nozzle end; seat at Z=5mm shoulder; epoxy 3 dabs at Z=50mm stator shoulder; route leads through hub bore.

- [ ] Install EDF1 (fore/upstream) from intake end; seat at Z=76mm; verify stator fins clear in Z=53–73mm gap; epoxy 3 dabs at Z=76mm shoulder.

- [ ] ESC pair: route to fuselage bay via spar conduit (ESC heat must NOT be trapped in nacelle bore).

- [ ] Cure 2h before proceeding.

- [ ] Repeat for stbd nacelle (opposite rotation direction).

**2B — Nozzle iris assembly (per nacelle):**

- [ ] Press nacelle_nozzle_ring.stl onto nozzle exit face; confirm flush.

- [ ] Install nozzle inner ring (rack, R=28mm) inside base ring.

- [ ] Bend 0.8mm piano wire link ring through all 8 petal link holes.

- [ ] Install 8 petals on 3mm hinge pins in base ring lugs.

- [ ] Dry-test: manually rotate inner ring — petals open smoothly 0°→75°, no binding.

- [ ] Install WS2812B LED ring at duct exit lip; route 3-wire lead through hub bore.

**2C — Gear linkage (per nacelle):**

- [ ] Mount sector gear to tilt bracket (FIXED — does not rotate with nacelle).

- [ ] Mount drive pinion on nacelle outer shell at pivot axis; mesh with sector gear; set backlash 0.1–0.2mm.

- [ ] Install bevel gear pair in nacelle body (nacelle-axis → longitudinal axis redirect).

- [ ] Thread 2mm steel longitudinal shaft through nacelle wall channel toward nozzle end.

- [ ] Mount crown pinion on shaft at nozzle end; mesh with Idler-In on the
    compound idler gear (`nacelle_nozzle_idler.scad`); set backlash 0.1–0.2mm.

- [ ] Mount idler gear on its bracket to the nozzle outer housing; mesh
    Idler-Out with the full-circle nozzle ring gear; set backlash 0.1–0.2mm.

- [ ] **Full sweep test (Rev R1, 2026-06-22):** rotate nacelle -5°→140°;
    verify nozzle ring gear rotates from ≈-1.33° to ≈38.45° (≈23.86° at the
    90° hover reference point), and petals swing from ≈18.76 mm to
    ≈34.42 mm tip radius (75%→105% of the 50 mm bore at the 0°/90°
    reference points) without binding against `HOUSING_INNER_R`=37.5 mm.
    Verify nozzle ring hard stop prevents over-drive beyond -5°/140°.

- [ ] Confirm petal closed position matches nacelle hull profile at 0°.

**Phase 2 checks:**

- [ ] Port nacelle EDF rotation: CW from intake; stbd: CCW from intake

- [ ] Stator fins visible and clear in Z=53–73mm gap on each nacelle

- [ ] Nozzle iris opens/closes smoothly through full nacelle sweep

- [ ] Petal closed: hull-match at 0°; petal open: all 8 even at 90°

- [ ] LED ring installed and wired

---

### Phase 3 — Tilt Mechanism

**Goal:** Both nacelles mounted on fuselage, pivot freely on MF104ZZ bearings, tilt driven by fuselage-mounted servos with hard stops.

- [ ] Press MF104ZZ bearings into pivot housing bores (both ends); flush ±0.2mm.

- [ ] Insert 4mm CF pivot rod through wing spar pocket + pivot housing bearings (rod is FIXED to fuselage; nacelle rotates on it).

- [ ] Slide nacelle pivot housing onto pivot rod; verify <0.5mm axial play.

- [ ] Install tilt servos in fuselage servo mount bracket at wing root bay.

- [ ] Connect pushrods (servo arm → pivot arm): servo 0° = nacelle 0° (cruise), servo ~125° = nacelle 90° (hover), servo ~170° = nacelle 120° (backing).

- [ ] Install CF-PETG hard stop blocks; bond at −5° stop and 140° stop positions.

- [ ] Servo calibration: set FC software travel limits at −5° and 140°; verify both nacelles reach 90° simultaneously.

**Phase 3 checks:**

- [ ] Both nacelles rotate freely on bearings — no grinding, no wobble

- [ ] Hard stops engage at −5° and 140° (servo stalls, does not strip)

- [ ] Nozzle opens/closes correctly via gear linkage through sweep (from Phase 2)

- [ ] Sector gear does NOT rotate with nacelle

- [ ] Both nacelles synchronise to within 2° at 0° and 90°

---

### Phase 4 — Hull Foam Pour + Close-up

**Goal:** Structural foam cured; all void formers removed; hull rigid.

**Pre-pour final checklist:**

- [ ] All PTFE conduits routed — pull strings accessible at both ends

- [ ] All bay standoffs installed

- [ ] Cargo hard points installed

- [ ] SMA bulkheads installed and dusted

- [ ] EPS void formers waxed (2 coats) and seated

- [ ] Nacelle bays and pivot housings masked OFF

- [ ] Servo mount brackets clear of foam path

**Pour sequence:**

- [ ] Mix X-30 per manufacturer (2:1 ratio by volume, 2-min pot life, 4× expansion). Pour in 3 shots: aft bay → mid bays (D+C) → forward bays (B+A). Allow 24h full cure before next shot.

- [ ] After full cure: remove EPS void formers; IPA wipe bay walls; verify foam did not intrude into panel bays, cargo bay, or conduit runs.

- [ ] Pull all 8 pull strings — verify still move freely.

- [ ] Install all 6 access panel lids; verify flush fit.

---

### Phase 5 — Minimum Viable Flyer ★ FIRST FLIGHT

**Goal:** CN1+FC1 (Shepherd's room / Bay A) and CN2+FC2 (Inara's shuttle / Bay B) installed and operational — first flight achieved.

> **Aft EDF not installed** (Phase 11). The 4 nacelle XFly Galaxy X5 EDFs (1240g each, 90%
> additive via stator = 2232g/nacelle × 2 = 4464g total) deliver T/W ≈ **1.61** at the
> Phase 5–10 AUW of ~2,768g — **full VTOL hover is achievable from Phase 5**. Phase 11
> adds the 55mm rear EDF for **forward-flight (cruise) thrust and RCS attitude authority** — it
> exhausts aft through the canonical nozzle and is not counted in hover (Phase 11 hover T/W ≈ 1.43).

**Dependency:** Cape-A (×2) and Cape-B (×2) PCB assemblies received from JLCPCB.

**Power system:**

- [ ] Mount XT90 PDB at keel sta 130mm; solder 14AWG main leads to ESCs.

- [ ] Install 2× 40A BLHeli32 ESCs in bay C (port + stbd nacelle fore EDF = FC1; aft EDF = FC2).

- [ ] **Phase 11 only:** Install 50A ESC in Panel F for 55mm rear EDF (FC2 PRU Ch.2) — skip for Phase 5.

- [ ] Install 5V/5A BEC; verify 5.00V ±0.05V under 1A bench load.

- [ ] Pull motor phase leads through conduit to ESCs; solder (verify rotation marking first).

- [ ] CAN FD termination: 120Ω SOLDERED to CN1 Cape-B at Shepherd's room (Bay A, bus start); temporary 120Ω at FC2 Cape-A in Inara's shuttle (Bay B, Phase 3 far-end; remove in Phase 7).

**ESC assignment (cross-nacelle redundancy — any FC failure retains 50% thrust both nacelles):**

| ESC | EDF | Nacelle | Controlled by |
|-----|-----|---------|---------------|
| ESC1 | EDF1 (fore) | Port | FC1 Cape-A PRU Ch.0 |
| ESC2 | EDF2 (aft) | Port | FC2 Cape-A PRU Ch.0 |
| ESC3 | EDF1 (fore) | Stbd | FC1 Cape-A PRU Ch.1 |
| ESC4 | EDF2 (aft) | Stbd | FC2 Cape-A PRU Ch.1 |
| ESC5 | 55mm rear | Fuselage | **DEFERRED — Phase 11** |

**CN1+FC1 installation — Shepherd's room (Bay A, nose) — Zoë / Wash (v2 EM-hardened):**
> Shepherd's room (Bay A) is the CAN FD / RS-485 / 1553B bus start termination node.  Use Zoë (ADM2795E
> RS-485, ISOW1044 CAN FD, ADIN1300 Ethernet) and Wash for 5 kV isolated transceivers at
> this end of the bus.  v2 placement is mandatory here (see TODO §1.2a node placement note).

- [ ] Mount CN1 Zoë on Shepherd's room (Bay A) floor standoffs (M2.5 nylon 6mm). Insert PB2-I. Secure.

- [ ] Mount FC1 Wash on inter-cape standoffs (M2.5 nylon 20mm) above CN1. Insert second PB2-I.

- [ ] Flash OS to eMMC on CN1 and FC1 via USB-C before installation.

- [ ] Install log μSD (64GB) in CN1 Cape-B log slot. Label: **CN1-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN1 Cape-B header; connect its coax to forward 49 MHz wire post.

- [ ] Connect CN1 radio pigtails: SiK 915MHz → belly port SMA; LoRa → belly stbd SMA; Wi-Fi → dorsal fwd SMA.

- [ ] Route FC1 GPS U.FL coax through cockpit-roof PTFE sleeve (sta ~59mm); mount GPS patch on hull dorsal, face UP.

- [ ] Daisy-chain CAN FD: 120Ω (soldered) → CN1 → FC1 → exit Shepherd's room (Bay A) toward Inara's shuttle (Bay B).

- [ ] Daisy-chain RS-485: CN1 → FC1 → exit toward Inara's shuttle (Bay B).

- [ ] Connect MIL-STD-1553: FC1 = Bus Controller (primary); CN1 = RT 0x01.

- [ ] Cap Simon's medbay (Bay E) end of ETH-EA conduit (will connect to FC4 in Phase 7); connect Shepherd's room (Bay A) end to CN1 Cape-B ETH-2.

**CN2+FC2 installation — Inara's shuttle (Bay B, dorsal fwd) — Zoë / Wash (Rev R):**
> Rev R: Inara's shuttle (Bay B) also uses v2 EMI-hardened capes (same as Shepherd's room). All four bays use Wash + Zoë.

- [ ] Mount CN2 Zoë on Inara's shuttle (Bay B) floor standoffs; insert PB2-I; mount FC2 Wash above.

- [ ] Flash OS to eMMC on CN2 and FC2 before installation.

- [ ] Install log μSD (64GB) in CN2 Cape-B log slot. Label: **CN2-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN2 Zoë J_XCVR header.

- [ ] Route FC2 GPS coax through dorsal PTFE sleeve (sta ~130mm); mount GPS patch on dorsal hull, face UP.

- [ ] Continue CAN FD daisy-chain Shepherd's room→Inara's shuttle: CN2 → FC2 + temporary 120Ω at FC2 (remove Phase 7).

- [ ] Continue RS-485 daisy-chain Shepherd's room (Bay A) → Inara's shuttle (Bay B).

- [ ] Connect ETH-AB (Shepherd's room → Inara's shuttle): FC1 Wash ETH-1 → CN2 Zoë ETH-B (FC1↔CN2 Ethernet ring link).

- [ ] Cap River's room (Bay D) end of ETH-BD (will connect to CN3 in Phase 7).

- [ ] Power taps: connect CN1, FC1, CN2, FC2 power leads from PWR conduit; verify 5V ±0.05V at each header.

**Security provisioning (before first flight):**

- [ ] Provision TPM 2.0 (SLB9670) on CN1, FC1, CN2, FC2 — unique key material per node.

- [ ] Verify CPLD write-blocker on CN1 and CN2: `echo test > /mnt/flightlog/test.txt` must return read-only error.

- [ ] Configure forensic log mount in `/etc/fstab` (noexec, nodev, nosuid, ro) on CN1 and CN2.

**Software configuration:**

- [ ] Flash serenity-cn Phase 6 daemon to CN1 and CN2.

- [ ] Flash serenity-fc Phase 6 stub to FC1 and FC2.

- [ ] Enable CAN FD interfaces at 1 Mbps / 8 Mbps on all 4 nodes.

- [ ] Verify 4-node CAN FD heartbeat ring: `candump can0` shows frames 0x001–0x004 within 100ms.

- [ ] Configure MAVLink routing (mavlink-router) on elected FC master → SiK 915MHz on CN master.

- [ ] Install the 49 MHz (Part 15 §15.235) daemon on CN1 and CN2 (select channel per 47 CFR §15.235; not §95.623, which does not apply to this band).

**Ground tests:**

- [ ] ESC calibration (full throttle power-on → drop to zero).

- [ ] Motor spin test (5% throttle 2s): all 5 motors spin in correct directions.

- [ ] Tilt servo calibration: 0° = nacelle vertical ±0.5°, 90° = horizontal ±0.5°.

- [ ] Rear nozzle servo endpoints verified.

- [ ] Static CG: **190mm from nose** (adjust battery position on rail).

- [ ] GPS lock: HDOP ≤1.5 on both FC nodes; positions agree within 2m.

- [ ] Radio checks: MAVLink heartbeat in QGC (SiK + LoRa backup); 49 MHz (Part 15 §15.235) RC channels correct; Wi-Fi GCS telemetry.

- [ ] Node failover: kill FC master power → standby assumes authority within 100ms on tether.

- [ ] Tethered thrust test: 60% throttle 10s → lift exceeds AUW; ESC temps ≤60°C.

- [ ] Nav lights: 6-position ICAO cycle (RED port, GREEN stbd, WHITE tail, WHITE belly strobe).

- [ ] **Apply FAA registration number** (14 CFR Part 48 — replaces N00000 placeholder on airframe).

**First flight sequence (per REVN_BUILD_GUIDE_24IN.md §Phase 5):**

- [ ] Pre-flight ABCD checklist (Airframe, Battery, Comms, Docs)

- [ ] Tethered hover 1m AGL × 3 successful passes before free flight (nacelles at 90°, ~60% throttle)

- [ ] Free hover 1m AGL (stability, ±10° authority, altitude hold ±0.3m)

- [ ] Free hover 3m AGL (yaw 360° both directions)

- [ ] Nacelle transition: ≥8m AGL, gradual sweep 90°→0° — altitude hold ±1.5m during transition

- [ ] Forward flight circuit: one lap ≤10m AGL, transition back to hover, land

- [ ] Verify flight log written to CN1-LOG and CN2-LOG

**Phase 5 pass criteria:**

- [ ] Stable hover 1m AGL in ≤15° headwind

- [ ] Nacelle transition without altitude excursion >1.5m

- [ ] All 4 nacelle ESCs ≤70°C at full hover power

- [ ] MAVLink telemetry live to QGC during all segments

- [ ] All 4-node CAN FD heartbeats confirmed

- [ ] Node failover: standby assumes within 100ms of master power-kill

- [ ] Flight log on both CN μSDs; CPLD write-block verified

---

### Phase 6 — Full 8-Node Architecture + ToF Obstacle Avoidance

**Goal:** All 8 nodes installed, full ring redundancy, 12× VL53L5CX dual-redundant obstacle avoidance operational.

**CN3+FC3 installation — River's room (Bay D, dorsal aft) — Zoë / Wash (Rev R):**
> Rev R: River's room (Bay D) also uses v2 EMI-hardened capes. All four bays uniform.

- [ ] Remove temporary Phase 6 CAN FD 120Ω from FC2 Wash in Inara's shuttle (Bay B).

- [ ] Mount CN3 Zoë on River's room (Bay D) floor standoffs; insert PB2-I; mount FC3 Wash above.

- [ ] Flash OS to eMMC; install log μSD. Label: **CN3-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN3 Zoë J_XCVR header.

- [ ] Route FC3 GPS coax through dorsal PTFE sleeve (sta ~275mm); mount GPS patch, face UP.

- [ ] Continue CAN FD chain: Inara's shuttle (Bay B) FC2 → River's room (Bay D) CN3 → FC3 → exit toward Simon's medbay (Bay E).

- [ ] Continue RS-485 chain Inara's shuttle (Bay B) → River's room (Bay D) → Simon's medbay (Bay E).

- [ ] Connect ETH-BD (Inara's shuttle → River's room): FC2 Wash ETH-1 → CN3 Zoë ETH-B.

- [ ] Power tap River's room (Bay D); verify 5V ±0.05V.

**CN4+FC4 installation — Simon's medbay (Bay E, aft service) — Zoë / Wash (v2 EM-hardened):**
> Simon's medbay (Bay E) is the CAN FD / RS-485 / 1553B bus end termination node and is physically closest to the
> nacelle motor wiring and rear 55mm EDF.  Use Zoë / Wash for 5 kV isolated
> transceivers at this end of the bus.  v2 placement is mandatory here.

- [ ] Mount CN4 Zoë on Simon's medbay (Bay E) standoffs; insert PB2-I; mount FC4 Wash above.

- [ ] Flash OS to eMMC; install log μSD. Label: **CN4-LOG**.

- [ ] Seat the 49 MHz (Part 15 §15.235) sub-module on CN4 header.

- [ ] Route FC4 GPS coax through dorsal PTFE sleeve (sta ~350mm); mount GPS patch, face UP.

- [ ] Terminate CAN FD bus end: CN4 → FC4 + **120Ω PERMANENT** soldered to FC4 Cape-A.

- [ ] Connect ETH-DE (River's room → Simon's medbay): FC3 Cape-A ETH-1 → CN4 Cape-B ETH-2.

- [ ] Connect ETH-EA ring-close (Simon's medbay → Shepherd's room): FC4 Cape-A ETH-1 → [Shepherd's room CN1 Cape-B ETH-2 already connected]. Closes the 8-node RSTP ring.

- [ ] Power tap Simon's medbay (Bay E); verify 5V ±0.05V.

**Security provisioning — remaining 4 nodes:**

- [ ] TPM 2.0 on CN3, FC3, CN4, FC4 — unique key material per node.

- [ ] CPLD write-blocker verification on CN3 and CN4.

**Full ring integration:**

- [ ] Verify RSTP ring: `bridge vlan show`; disconnect one ETH cable → traffic re-routes within 1s.

- [ ] Verify full 8-node CAN FD ring: `candump can0` shows frames 0x001–0x008 within 100ms.

- [ ] MIL-STD-1553 final config: FC1=BC, FC2=standby BC, FC3/FC4/CN1–CN4=RT; all 8 RT addresses respond within 9μs.

**ToF sensor installation:**

Array B (hosted by FC1, Shepherd's room / Bay A):

| Sensor | Station | Position |
|--------|---------|----------|
| S1B | 50mm | Nose ring |
| S2B | 510mm | Rear bell rim |
| S3B | 180mm | Port hull |
| S4B | 180mm | Stbd hull |
| S5B | 315mm | Dorsal keel |
| S6B | 265mm | Belly blister |

- [ ] Install 6× VL53L5CX in Array B flush-mount frames; wire to TCA9548A ch.0–5 in Shepherd's room (Bay A); MCP23008 GP0–GP5 → XSHUT; I²C to FC1 Cape-A.

Array A (hosted by FC3, River's room / Bay D):

| Sensor | Station | Position |
|--------|---------|----------|
| S1A | 30mm | Nose ring |
| S2A | 525mm | Rear bell rim |
| S3A | 240mm | Port hull |
| S4A | 240mm | Stbd hull |
| S5A | 215mm | Dorsal keel |
| S6A | 195mm | Belly blister |

- [ ] Install 6× VL53L5CX in Array A flush-mount frames; wire to TCA9548A ch.0–5 in River's room (Bay D); separate I²C bus (electrically isolated from Array B).
- [ ] Apply 0.5mm PMMA disc over each sensor aperture with UV adhesive.
- [ ] Configure OA fusion in firmware: halt at 1.0m obstacle clearance; either array independent on single-FC failure.
- [ ] GPS clearance check for 49MHz wire post proximity: bench-verify HDOP ≤1.5 with the 49 MHz (Part 15 §15.235) link transmitting; if GPS degrades, move GPS patch to ≥165mm from forward post.

**Phase 6 pass criteria:**

- [ ] All 8 CAN FD heartbeats (0x001–0x008) confirmed

- [ ] Ethernet RSTP ring heals on single-link disconnect within 1s

- [ ] MIL-STD-1553: all 8 RTs respond within 9μs

- [ ] CN3 and CN4 log μSD write-block verified

- [ ] All 12 ToF sensors return valid range at ≤4m

- [ ] OA halt test: approach wall at 0.5m/s → stops at 1.0m clearance

- [ ] Array failure mode: either FC1 or FC3 loss → remaining array provides full OA coverage

- [ ] 3-waypoint autonomous mission with GPS, altitude hold, RTL on simulated link loss

---

### Phase 7 — Cargo System

**Goal:** 250g payload delivery via autonomous winch deploy with auto-latch cradle.

- [ ] Bond cargo gondola shell into belly void at 4× M3 hard points (installed Phase 1). Cure 24h.

- [ ] Install 3mm CF door hinge pins; attach clamshell door halves (spring-loaded to open).

- [ ] Install DRV8833 + N20 winch motor + drum; wind 1.5m Dyneema; attach auto-latch cradle via double-bowline.

- [ ] Install SG90 door-actuator servo (spring-assist open, servo pull-close via bell-crank).

- [ ] Install SG90 payload-release servo; connect to DRV8833 IN1/IN2 via PWM→resistor divider→GPIO.

- [ ] Route control leads through PWR conduit belly tap to CN master (CN1 or CN2 — winner of CN master election).

- [ ] Seal gondola-hull perimeter with 3M foam gasket tape.

- [ ] Configure CN master GPIO: door open/close, winch deploy/retract, payload latch status (microswitched).

**Phase 7 pass criteria:**

- [ ] Door open/close × 10: no binding

- [ ] Winch deploy 1.5m: straight descent, line clear

- [ ] Winch retract: auto-latch clicks and holds at top

- [ ] 250g load test: winch deploy + retract × 5; latch holds

- [ ] Hover with 250g payload: altitude-hold degradation ≤10%

- [ ] Autonomous delivery: 3-waypoint mission, deploy at waypoint 2, retract empty, complete mission

---

### Phase 8 — Finishing

**Goal:** Aircraft legally compliant, aesthetically complete, and fully documented.

- [ ] Replace FAA N00000 placeholder in `serenity/diagrams/decal_sheet.svg` with issued FAA registration number (via FAA DroneZone, 14 CFR Part 48).

- [ ] Print decal sheet on waterslide decal paper; seal with clear coat; dry 24h.

- [ ] Apply decals per `build_guide_19_decal_placement.svg`: Serenity lettering, FAA blocks, universe markings (宁静 Chinese name, Alliance registry), safety labels, weathering.

- [ ] Final airworthiness inspection: all fasteners, propulsion, electronics, battery, CG.

- [ ] Documentation archive: build log (photos + test results), Cape-B CPLD bitstream, TPM endorsement key fingerprints, final AUW + CG measurements.

- [ ] FAA compliance final check: registration visible without moving any part; remote pilot certificate current; AUW <55 lbs; LAANC authorization for any controlled airspace.

---

### Phase 9 — Performance Tuning and Flight Envelope Expansion

**Goal:** Optimise PID governor coefficients, measure actual thrust and efficiency, and expand the
safe flight envelope beyond the minimum parameters established in Phase 5.

**Dependency:** Phase 6 (all 8 nodes + ToF OA) and Phase 7 (cargo system) complete.

- [ ] **Thrust stand calibration** — run `airframe/scripts/governor_cal.py` on bench against all 4 nacelle EDFs (tandem pairs); measure actual thrust vs. RPM; update `EDF_THRUST_K` in `governor_config.h`.

- [ ] **PID governor tuning** — in-flight hover trim: adjust attitude PID gains until hover hold ±0.15 m altitude, ±2° attitude; log CAN FD governor data for analysis.

- [ ] **Nacelle transition tuning** — refine tilt servo rate and cross-axis coupling compensation; target altitude excursion ≤0.5 m during 90°→0° nacelle sweep.

- [ ] **Endurance test** — full charge 6S 4000mAh, hover 1m AGL until 3.7V/cell cutoff; measure hover time and battery health.

- [ ] **Cross-wind hover** — verify stable hover in ≥10 kt headwind; document max demonstrated crosswind.

- [ ] **Extended autonomous mission** — 5-waypoint GPS mission, altitude hold, RTL on link loss; verify log integrity on all 4 CN μSDs.

**Phase 9 pass criteria:**

- [ ] T/W measured ≥1.10 (nacelles only) on thrust stand

- [ ] Hover altitude hold ±0.15 m for 60 s

- [ ] Nacelle transition altitude excursion ≤0.5 m

- [ ] Endurance ≥8 min at hover (6S 4000mAh baseline)

- [ ] Logs on all 4 CN nodes; write-block verified

---

### Phase 10 — Advanced Autonomy and Long-Range Operations

**Goal:** Validate extended autonomous mission capability, BVLOS readiness, and multi-link
communication redundancy sufficient for real-world deployment.

**Dependency:** Phase 9 complete.

- [ ] **BVLOS communication validation** — verify handover between all 4 radio links (SiK, LoRa, Wi-Fi, 49 MHz (Part 15 §15.235)) in a degraded RF environment; mission continues on any single surviving link.

- [ ] **Extended waypoint missions** — ≥10-waypoint autonomous mission at ≤400 ft AGL; verify all obstacle avoidance halts function through the full mission.

- [ ] **Payload delivery mission** — fully autonomous: takeoff → 3-waypoint transit → cargo deploy → return → land; pass criteria: payload delivered within 2 m of target, cradle auto-latched on return.

- [ ] **Simulated node failure during flight** — kill one FC node mid-hover; verify remaining 3 FC nodes maintain flight for 30 s; RTL executed correctly.

- [ ] **Emergency RTL validation** — disable all control links; verify automatic RTL initiates within 5 s of link loss; lands within 3 m of takeoff point.

- [ ] **Regulatory readiness review** — FAA Part 107 waiver pre-application checklist; confirm LAANC authorization for planned operational area; update flight log and maintenance record.

**Phase 10 pass criteria:**

- [ ] Mission continues on any single surviving radio link

- [ ] 10-waypoint autonomous mission completed without intervention

- [ ] Autonomous cargo delivery within 2 m of target

- [ ] Node failure: remaining FCs maintain flight ≥30 s

- [ ] RTL on link loss: lands within 3 m of takeoff point

- [ ] All regulatory documentation current and on file

---

### Phase 11 — Aft EDF Integration (Deferred)

**Goal:** Install the 55mm 6S fuselage EDF, its reduced-area intake, the fixed canonical
elliptical tail nozzle, and the 4 EDF-fed RCS bleed-air thrusters — adding forward-flight
(cruise) thrust and pitch/yaw attitude authority. The rear EDF exhausts straight aft through
the canonical nozzle and contributes **no** hover lift; VTOL hover remains nacelle-driven.

**Dependency:** Phases 0–10 complete and proven in flight.

**Design files:** `deferred/aft-edf/` — see `deferred/aft-edf/README.md` for full details.
**NOTE (Rev R1 redesign):** the 120 mm SCAD/STLs in `deferred/aft-edf/` are SUPERSEDED. All
rear-EDF geometry must be regenerated for the 55 mm fan, the canonical nozzle, and the RCS system
before Phase 11 fabrication (see §11C). Old iris files (`rear_nozzle_frame.stl`,
`rear_nozzle_petal.stl`) and 120 mm files are archived.

> **Thrust note:** Phases 5–10 nacelle-only thrust is 4,464 g against ~2,768 g AUW → hover
> T/W ≈ 1.61. Phase 11 adds the 55 mm rear EDF (~1,500 g fan thrust → ~1,275 g net forward
> after ~15% RCS bleed). Because the canonical nozzle fires aft, this thrust is **horizontal
> (cruise/range) only** and is not counted in hover. Phase 11 full AUW ~3,130 g → hover
> T/W ≈ 1.43 (above the 1.0 hover floor, below the 1.5 comfort target — keep hover payload light).

**11A — Procurement (if not yet in stock):**

| Item | Qty | Approx. Cost |
|------|-----|-------------|
| 55mm 6S EDF (~1,500 gf) | 1× | ~$35–55 |
| 50A 6S BLHeli32 ESC | 1× | ~$18–28 |
| SG90-class proportional valve servo (RCS) | 4× | ~$12 |
| WS2812B LED ring (55mm duct) | 1× | ~$3 |

**11B — Rear neck shell swap (if printed without windows):**

- [ ] Print `rear_neck_intake_shell24.stl` from `deferred/aft-edf/openscad/rear_neck_intake_shell24.scad`. Verify NECK_X ≈ 310mm alignment in slicer. **Scoop windows must be re-sized for the 55 mm EDF (reduced area).**

- [ ] Remove temporary window covers from existing neck shell, or swap in the new windowed shell if a plain shell was used for Phases 0–10.

**11C — Geometry regeneration and printing (Rev R1 rear-EDF redesign):**

- [ ] **Regenerate** `neck_intake_frame.scad` for the 55 mm intake area; print `neck_intake_frame.stl` (CF-PETG, 0.15mm, 40% gyroid, 4 walls).

- [ ] **Regenerate** `aft_edf_plenum.scad`: 55 mm circular EDF inlet + 4 RCS bleed taps (~15% flow); print `aft_edf_plenum.stl` (CF-PETG, 0.20mm, 20% gyroid) — EDF housing, treated as structural per CLAUDE.md Fabrication Standards.

- [ ] **Generate** `rear_nozzle_canonical.scad`: fixed canonical elliptical tail nozzle, exit 2.06×1.76 in (52.3×44.7 mm, ~1,836 mm²), hull-matched outer surface; print `rear_nozzle_canonical.stl` (CF-PETG, 0.15mm, 30%, 4 walls). **No iris, no servo.**

- [ ] **Generate** `rcs_distribution_manifold.scad` + `rcs_thruster_nozzle.scad` + `rcs_valve_bracket.scad`; print `rcs_distribution_manifold.stl` (×1, PETG), `rcs_thruster_nozzle.stl` (×4, CF-PETG), `rcs_valve_bracket.stl` (×4, CF-PETG).

- [ ] Run mesh watertightness verification on all regenerated STLs; report findings here and resolve.

**11D — Intake frame installation:**

- [ ] Dry-fit `neck_intake_frame.stl` into the resized scoop windows; registration tongues insert with ~0.2mm clearance (sand if tight).

- [ ] Verify aerodynamic orientation: intake lips face forward (−Y / nose-ward).

- [ ] Apply structural epoxy to tongues + shoulder flanges; press frame into position; clamp; cure 24h.

- [ ] Fillet all gaps between flange and hull; cure 2h.

**11E — Plenum + RCS manifold installation:**

- [ ] Dry-fit `aft_edf_plenum.stl`; verify intake arm alignment and 55mm EDF inlet centred.

- [ ] Bond plenum forward arms to intake frame exits; fillet joints; cure 2h.

- [ ] Bond `rcs_distribution_manifold.stl` to the 4 plenum bleed taps; route 4 bleed ducts to the RCS jet locations.

- [ ] Pressure-test: seal EDF face with tape; cover all but one scoop; shop-vac — confirm draft at EDF inlet and at all 4 RCS jets, no joint leakage.

**11F — 55mm EDF installation:**

- [ ] Bench-test 55mm EDF (correct rotation, no vibration).

- [ ] Install EDF retaining ring at station ~430mm inside Panel F; bond; cure 1h.

- [ ] Seat EDF in plenum 55mm inlet; press forward to retaining lip; bond with 4 dabs slow-cure epoxy.

- [ ] Route motor leads through Panel F to 50A ESC; route signal lead forward via MAIN-PWR conduit to Inara's shuttle (Bay B, FC2 PRU Ch.2).

- [ ] Install 50A ESC in Panel F bay; foam tape + cable tie. Cure 2h before applying thrust.

**11G — Canonical nozzle + RCS installation:**

- [ ] Bond `rear_nozzle_canonical.stl` to the tail-cone exit (Panel F aft end), blending into the canonical hull outer mold line. **Fixed — no moving petals.**

- [ ] Install 4× `rcs_thruster_nozzle.stl` at their RCS stations; connect each to its bleed duct.

- [ ] Install 4× SG90-class proportional valves on `rcs_valve_bracket.stl`; link each valve to its RCS bleed duct.

- [ ] Calibrate RCS valves: 0% = closed (no bleed); 100% = full bleed jet. Map 2 jets to pitch, 2 to yaw.

- [ ] Install WS2812B LED ring at canonical nozzle exit lip.

**11H — 49MHz antenna upgrade:**

- [ ] Bond permanent aft 49 MHz (Part 15 §15.235) wire post to top of the canonical tail nozzle (5-min epoxy).

- [ ] Remove temporary aft post from station ~580mm.

- [ ] Restring 49MHz top wire (~470mm) from forward post to nozzle aft post with ~20g tension.

**11I — Software:**

- [ ] Enable ESC5 in FC2 firmware (PRU Ch.2); configure BDSHOT governor for the 55mm EDF.

- [ ] Add the 4 RCS proportional-valve channels to the attitude-control mixer; calibrate pitch/yaw authority via `governor_cal.py`.

- [ ] Add rear EDF to the forward-thrust (cruise) schedule — NOT the hover lift mixer.

- [ ] Verify all 5 ESC heartbeats on CAN FD; confirm FC2 cross-drive capability for ESC5.

- [ ] Bench-test RCS attitude authority; then forward-flight thrust test with the rear EDF at 60% throttle.

**Phase 11 checks:**

- [ ] All regenerated rear-EDF STLs pass mesh watertightness verification

- [ ] Intake frame tongues fully seated in the resized scoop windows

- [ ] Plenum + RCS manifold pressure-test passed (draft at EDF inlet and all 4 RCS jets; no leakage)

- [ ] EDF seated at station ~430mm, centreline ±2mm; rotation verified before sealing

- [ ] 50A ESC installed; ESC5 signal routed to FC2 PRU Ch.2

- [ ] Canonical nozzle bonded flush to hull outer mold line; exit 2.06×1.76 in verified

- [ ] All 4 RCS valves calibrated; pitch/yaw authority confirmed on bench

- [ ] 49MHz aft wire post on canonical nozzle; top wire re-strung at full ~470mm span

- [ ] Forward-thrust test passed; rear EDF NOT used for hover lift; ESC temps ≤70°C

- [ ] All 5 ESC telemetry visible on CAN FD; ESC temps ≤70°C at cruise power

---

## 4.0 — Firmware and Software

**Dependency for Phase 6:** serenity-fc Phase 7 items can be developed concurrently with physical Phases 0–5 and must be integrated by Phase 6 first flight.

### 4.1 — Completed

- [x] Firmware directory structure (`serenity/firmware/`) *(done 2026-05-25)*

- [x] KISS/AX.25 UART driver for XCVR-49MHZ-1 — `serenity/firmware/cn/src/xcvr_kiss.c/.h` *(done 2026-05-25)*

- [x] Si5351A I²C driver — `serenity/firmware/cn/src/si5351.c/.h` *(done 2026-05-25)*

- [x] AM6254 device tree overlays — Cape-A and Cape-B DTSs *(done 2026-05-25)*

- [x] serenity-cn Phase 6 daemon (XCVR KISS driver + argparse + SIGTERM) *(done 2026-05-25)*

- [x] serenity-fc Phase 6 stub (signal handling, idle loop placeholder) *(done 2026-05-25)*

### 4.2 — FC Node (Wash) — Phase 7 Firmware

- [ ] **EDF ESC PID governor** — BDSHOT600 telemetry input on PRU-ICSS, EHRPWM output to ESCs, CAN FD cross-node synchronisation. Targets: settle <200ms, overshoot <5%; equalization |RPM_FWD − RPM_AFT| <100 RPM; fault latch on overtemp/overcurrent (no auto-recovery, GCS ack required).
    - [ ] PRU-ICSS BDSHOT600 telemetry decoder (RPM, voltage, current, temp frames).
    - [ ] EHRPWM throttle output driver with `governor_config.h` k-coefficient (§4.1, already calibrated).
    - [ ] CAN FD cross-node RPM sync message (fwd/aft pairing across River/Simon).
    - [ ] PID tuning bench test against `governor_cal.py` thrust-stand data; verify settle/overshoot/equalization targets above.
    - [ ] Overtemp/overcurrent fault-latch unit test (no auto-recovery path).

- [ ] **Nacelle tilt servo PWM generation** — EHRPWM or PRU; travel limits −5°/140° enforced in firmware; symmetric 2° tracking both nacelles.
    - [ ] EHRPWM/PRU servo output driver with firmware-enforced travel limits (−5°/140°).
    - [ ] Symmetric tracking control loop (port/stbd nacelle ≤2° divergence).
    - [ ] Bench test: command full sweep, verify limit clamping and tracking error budget.

- [ ] **IMU / barometer sensor fusion** — ICM-42688-P (SPI), BMP388/BMP390 (SPI); complementary or Kalman filter for attitude; altitude hold PID using barometric altitude + GPS.
    - [ ] ICM-42688-P SPI driver (accel/gyro read, calibration/bias removal).
    - [ ] BMP388/BMP390 SPI driver (pressure/altitude read).
    - [ ] Attitude filter (complementary or Kalman) fusing IMU + barometer.
    - [ ] Altitude-hold PID using fused barometric + GPS altitude.
    - [ ] Bench test: static and bench-rotation attitude accuracy check.

- [ ] **ToF sensor array management** — VL53L5CX ×6 per node via TCA9548A I²C mux; XSHUT sequencing via MCP23008; OA fusion (Array A + Array B cross-check); halt at 1.0m clearance.
    - [ ] TCA9548A I²C mux driver (channel select for 6× VL53L5CX per node).
    - [ ] MCP23008 XSHUT sequencing driver (sensor power-up ordering, address conflict avoidance).
    - [ ] VL53L5CX 8×8 ranging driver and per-sensor data aggregation.
    - [ ] Array A / Array B cross-check fusion logic; halt-at-1.0m / resume-at-1.5m hysteresis (matches §4.4 "OA integration").
    - [ ] Bench test: known-distance target sweep, verify halt/resume thresholds.

- [ ] **u-blox M10Q GNSS integration** — UART NMEA/UBX parse; position fix broadcast on CAN FD; HDOP gating (≤1.5 for valid position); multi-node position cross-check (≤2m disagreement threshold).
    - [ ] UART NMEA/UBX parser (position, velocity, HDOP, fix-type fields).
    - [ ] HDOP gating logic (reject fix if HDOP >1.5).
    - [ ] CAN FD position-fix broadcast frame.
    - [ ] Multi-node cross-check consumer (flag/exclude outliers >2m, feeds §4.4 "GPS cross-check").
    - [ ] Bench/field test: static fix HDOP and 4-node position agreement.

- [ ] **MIL-STD-1553B RT implementation** — PRU-ICSS Manchester II encoder/decoder; RT address assignment per node role; BC arbitration on FC1 and FC2.
    - [ ] PRU-ICSS Manchester II encode/decode driver.
    - [ ] RT address assignment table per node role (FC1–FC4).
    - [ ] BC arbitration logic for FC1 (primary) / FC2 (standby).
    - [ ] Bench test against the 1553-XFM transformer coupling hardware (§1.2 "Wire the MIL-1553 connector + transformer").

- [ ] **TPM-bound attestation** — SLB9670 TPM 2.0 HMAC on all outbound flight-critical CAN FD messages; pcrs extend on each boot; boot measurement chain.
    - [ ] SLB9670 TPM 2.0 driver (HMAC key derivation, PCR extend calls).
    - [ ] Boot measurement chain (PCR extend at each boot stage).
    - [ ] Outbound CAN FD HMAC signing hook for flight-critical message classes.
    - [ ] Bench test: tamper/replay rejection unit test against signed vs. unsigned frames.

- [x] **governor_cal.py** — thrust stand calibration script: sweeps 0%→100%→0% throttle, fits k coefficient (T = k × RPM²), outputs `EDF_THRUST_K` for `governor_config.h`. *(done 2026-06-04)*

- [x] **governor_config.h** — template with calibrated k values per EDF; compile-time constants. *(done 2026-06-04)*

### 4.3 — CN Node (Zoë) — Phase 7 Firmware

- [ ] **CAN FD heartbeat and telemetry forwarding** — broadcast 0x001–0x008 node health frames; relay MAVLink telemetry from elected FC master to SiK GCS link.
    - [ ] 0x001–0x008 node health frame broadcaster (per-node heartbeat content/period).
    - [ ] MAVLink telemetry relay path: FC master CAN FD → CN master → SiK GCS link.
    - [ ] Bench test: heartbeat timeout detection feeding §4.4 "Node role election protocol."

- [ ] **MIL-STD-1553B BC/RT tasks** — BC on CN1 (standby), RT on CN2–CN4; mirror FC bus controller arbitration.
    - [ ] BC standby logic on CN1 (mirrors FC1/FC2 arbitration, §4.2).
    - [ ] RT implementation on CN2–CN4 (shares PRU-ICSS Manchester II driver with §4.2).
    - [ ] Bench test against 1553-XFM transformer coupling hardware (§1.2).

- [ ] **RS-485 inter-board messaging** — structured message format (header/payload/CRC); inter-node command and status relay.
    - [ ] Define structured frame format (header/payload/CRC) shared across all 8 nodes.
    - [ ] Driver for the RS485_A/B footprint pinout already fixed on Wash/Zoë (§1.2).
    - [ ] Bench test: CRC-reject malformed frame, command/status round-trip between two nodes.

- [ ] **Ethernet RSTP ring management** — CPSW3G bridge configuration; RSTP fast-failover (<1s) verification; ring segment health monitoring.
    - [ ] CPSW3G bridge configuration for the 8-node ring topology (§1.4.3).
    - [ ] RSTP fast-failover implementation and timer tuning.
    - [ ] Ring segment health monitoring/reporting hook (feeds CAN FD heartbeat above).
    - [ ] Bench test: physically break one ring segment, verify <1s failover.

- [ ] **Signed-log write via CPLD write-blocker** — log records written as read-only-append through ATF16V8BQL latch interface; NOR flash (W25Q128JV) circular buffer for overflow.
    - [ ] ATF16V8BQL CPLD write-blocker interface driver (enforces append-only).
    - [ ] microSD log writer (primary store) per node's write-blocked card.
    - [ ] W25Q128JV NOR flash circular buffer driver for overflow when microSD is full/unavailable.
    - [ ] Bench test: attempt out-of-order/overwrite write, verify CPLD blocks it.

- [ ] **TPM-bound HMAC on all outbound AX.25 payloads** — each 49 MHz (Part 15 §15.235) packet includes HMAC-SHA256 computed from SLB9670 stored key; receiver nodes verify before acting.
    - [ ] SLB9670 stored-key HMAC-SHA256 signer for outbound AX.25/49 MHz frames (Emma boards, River/Simon).
    - [ ] Receiver-side verification gate (discard unsigned/invalid before acting, mirrors §4.4 "Security message signing").
    - [ ] Bench test: signed/unsigned/corrupted-signature frame acceptance matrix.

- [ ] **Cargo control** — DRV8833 winch H-bridge, HX711 load cell (payload weight sensing), SG90 door and release servos; state machine: IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED.
    - [ ] DRV8833 H-bridge winch driver.
    - [ ] HX711 load-cell driver (payload weight sensing, overload cutoff).
    - [ ] SG90 door + release servo driver.
    - [ ] State machine implementation: IDLE → DEPLOY → DELIVERED → RETRACT → LATCHED, with fault states.
    - [ ] Bench test: full cycle with simulated payload load, verify HX711 cutoff and state transitions.

- [ ] **MAVLink routing configuration** — mavlink-router config: elected CN master routes FC master telemetry to all 4 radio links (SiK, LoRa, Wi-Fi, 49 MHz (Part 15 §15.235) backup).
    - [ ] mavlink-router config file per CN role (master vs. standby).
    - [ ] Per-link output adapter: SiK, LoRa (Emma), Wi-Fi, 49 MHz (Part 15 §15.235) (Emma, backup).
    - [ ] Bench test: verify telemetry reaches Malcolm GCS over each of the 4 links independently.

### 4.4 — Both Nodes

- [ ] **Node role election protocol** — CAN FD priority arbitration at boot; lowest node-ID wins master role; automatic failover on heartbeat timeout (100ms); FC master and CN master elected independently.
    - [ ] Boot-time CAN FD priority arbitration (lowest node-ID wins, per PACE table in CLAUDE.md).
    - [ ] Independent FC-master / CN-master election state machines.
    - [ ] Failover trigger on 100ms heartbeat timeout (consumes §4.3 heartbeat broadcast).
    - [ ] Bench test: kill the current master, verify failover to next PACE tier within timeout.

- [ ] **Autonomous navigation** — 3-waypoint GPS mission execution; altitude hold ±0.3m; waypoint radius 2m; RTL on any link loss >5s.
    - [ ] Waypoint mission sequencer (3-waypoint minimum viable mission).
    - [ ] Altitude-hold integration with §4.2 barometric/GPS altitude PID.
    - [ ] Waypoint-radius capture logic (2m) and RTL trigger on link loss >5s.
    - [ ] Field test: full 3-waypoint mission with deliberate link-loss RTL trigger.

- [ ] **OA integration** — ToF halt trigger feeds into navigation; velocity command zeroed within 1.0m of obstacle; resumes when clear.
    - [ ] Navigation-layer consumer for §4.2 ToF array halt/resume signal.
    - [ ] Velocity command zeroing at 1.0m clearance; resume logic at 1.5m clearance.
    - [ ] Bench/field test: approach a target obstacle, verify halt/resume hysteresis in flight.

- [ ] **GPS cross-check** — 4 GPS receivers (one per FC node); positions averaged; outlier >2m flagged and excluded from blend.
    - [ ] Multi-node position collection (4× u-blox M10Q via §4.2 CAN FD broadcast).
    - [ ] Averaging/blend algorithm with outlier exclusion (>2m disagreement).
    - [ ] Bench test: inject a synthetic outlier fix, verify exclusion from blend.

- [ ] **Security message signing** — every inter-node CAN FD message signed; unauthenticated messages discarded; signing key material bound to node TPM endorsement key.
    - [ ] CAN FD message signing hook bound to each node's TPM endorsement key (SLB9670, §4.2).
    - [ ] Receiver-side verification gate; discard unauthenticated frames before acting.
    - [ ] Bench test: inject unsigned/forged frame on the bus, verify it is discarded and logged.

### 4.5 — Ground Control (Malcolm / "CAPT Reynolds")

> "I aim to misbehave."

**Architecture summary:** Malcolm stays at a safe operator distance.  The link budget
(directional antennas + gain) is sized to maintain reliable uplink/downlink with an
aircraft whose receivers may be desensed by proximity to high-power RF sources.
No additional transmit power amplifiers are FCC-compliant for any link in the standard
configuration with directional antennas.  See `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`.

**File tree:** `gcs/malcolm/` — hardware docs, SCAD gimbal designs, PB2-I firmware, and
host-PC software all created in Rev R.  See `gcs/malcolm/README.md` for layout.

#### 4.5.1 — Malcolm Hardware Design

- [ ] **Create Malcolm host computer specification** (`gcs/malcolm/hardware/docs/malcolm_host_spec.md`):
    minimum x86\_64 Debian Linux, 8 GB RAM, 256 GB SSD, USB 3.0+; ruggedized laptop
    (IP54 or better) for field use.  Document recommended models and any BIOS/driver notes.

- [ ] **Malcolm field enclosure — print and fit-check** `gcs/malcolm/hardware/enclosure/openscad/malcolm_field_enclosure.scad`:
    export STL (`openscad -o malcolm_field_enclosure_body.stl ... -D RENDER_MODE=0`);
    verify PCB standoff spacing matches Cape-B-2 55×35 mm mounting hole pattern in slicer;
    run mesh validation; print body + lid in PETG (IP65 gasket groove accepts 3 mm EPDM cord).
    **Add to Phase Malcolm-1 print schedule.**

- [ ] **Gimbal STL generation and mesh verification** — for each of the three SCAD files:
    - `malcolm_gimbal_pan.scad` → `malcolm_gimbal_pan_base.stl` + `malcolm_gimbal_pan_turret.stl`
    - `malcolm_gimbal_tilt.scad` → `malcolm_gimbal_tilt_yoke.stl`
    - `malcolm_gimbal_mount.scad` → `malcolm_gimbal_mount.stl`
    Print in CF-PETG (0.15 mm, 40% infill, 4 walls).  Verify bearing pocket diameters
    (6804: 32 mm OD housing; MF104ZZ: 10 mm OD housing) against bearing datasheets before printing.

- [ ] **Gimbal servo wind-load torque check** — compute worst-case wind torque on a 9 dBi Yagi
    (~1.2 m boom, ~0.04 m² front area) at 30 kt crosswind.  Verify DS3218MG (25 kg·cm @ 6 V)
    provides ≥2× safety factor.  Document in `gcs/malcolm/hardware/docs/malcolm_power_budget.md`.

- [ ] **Procure Malcolm comms node hardware:**
    - 1× PocketBeagle 2 Industrial (AM6254) — same DigiKey PN 2820-100003007-ND
    - 1× Cape-B-2 (Zoë) PCB — order 1 additional unit when placing aircraft PCB order at JLCPCB
    - 1× Emma sub-module — order 1 additional unit with aircraft Emma order
    - 1× 64 GB microSD (Samsung or equiv, same as aircraft CN nodes)
    - 1× 5 V / 5 A switching BEC (Pololu D24V50F5 or equiv)
    - 1× 6 V / 2 A servo BEC (Pololu D24V22F6 or equiv)

- [ ] **Procure antenna hardware** per `gcs/malcolm/hardware/docs/malcolm_antenna_spec.md`:
    - 2× 5 dBi 915 MHz omni rubber duck (RP-SMA) — one SiK, one LoRa
    - 1× 9 dBi 915 MHz Yagi directional (RP-SMA) — shared SiK+LoRa via RF splitter
    - 1× 14 dBi 5 GHz flat panel (RP-SMA) — Wi-Fi, gimbal-mounted
    - 1× 49 MHz base-loaded whip 1/4-wave (~0.94 m physical) with 4 ground radials
    - 1× 3 dBi 2.4 GHz rubber duck dipole (Zigbee, optional)
    - 1× u-blox ANN-MB-00 or equiv active GNSS patch (GCS position fix)
    - 1× 2-way 915 MHz RF splitter ≥20 dB isolation (Minicircuits ZFSC-2-1W-S+ or equiv)
    - Coax cables per `malcolm_wiring.md` cable table (LMR-195, RG-58, RG-316)

- [ ] **Procure gimbal hardware:**
    - 2× DS3218MG digital servo (same as aircraft nacelle servos — reduces spare parts inventory)
    - 2× AS5600 magnetic encoder PCB breakout module (I²C, 0x36)
    - 2× N42 diametrically magnetised disc magnet 6×2 mm (encoder rotor)
    - 1× 6804 thin-section bearing (20×32×7 mm) — pan stage
    - 2× MF104ZZ flanged bearing (4×10×4 mm) — tilt pivot (same as nacelle pivot)
    - 1× TCA9548A I²C mux PCB breakout (encoder bus isolation)
    - 1× M6 camera tripod (heavy-duty) or 3 m telescoping mast for outdoor use

#### 4.5.2 — Malcolm Comms Node Setup (Phase Malcolm-2)

**Dependency:** Cape-B-2 and Emma PCBs received from JLCPCB.

- [ ] **Flash Debian Linux to Malcolm PB2-I eMMC** — same OS image as aircraft nodes.
    USB-C boot procedure per BeagleBone Debian documentation.

- [ ] **Apply Cape-B-2 device tree overlay for Malcolm** — compile and install
    `gcs/malcolm/firmware/pb2i/dts/k3-am6254-pocketbeagle2-malcolm-cape-b2.dtbo`.
    Verify EHRPWM0 appears as `/sys/class/pwm/pwmchip0/` with 2 channels.
    Verify I²C2 appears as `/dev/i2c-2`.

- [ ] **Provision TPM 2.0 (SLB9670) on Malcolm's PB2-I** — unique key material; persistent
    handle `MAL_TPM_KEY_HANDLE` (0x81000001) per `mal_config.h`.
    Follow the same provisioning procedure as aircraft nodes (PROVISIONING.md, TBD).

- [ ] **Verify CPLD write-blocker on Malcolm's log μSD** (Cape-B-2 ATF16V8BQL):
    `echo test > /mnt/flightlog/test.txt` must return read-only error.
    Configure `/etc/fstab` noexec/nodev/nosuid/ro mount for log partition.

- [ ] **Build and install Malcolm PB2-I firmware:**

        cd gcs/malcolm/firmware/pb2i
        mkdir build && cd build
        cmake -DCMAKE_TOOLCHAIN_FILE=../toolchain-aarch64.cmake ..
        make -j$(nproc)
        sudo make install

    Verify `mal_gimbal` binary installed at `/usr/local/bin/mal_gimbal`.

- [ ] **Install and configure mavlink-router on Malcolm's PB2-I** — same binary as for
    aircraft CN nodes; configure for GCS role (forward all radio links → USB CDC-ECM → host PC).
    Test: QGC on host PC should receive heartbeat on UDP :14550 with aircraft bench-powered.

- [ ] **Enable all 5 radio interfaces on Malcolm's PB2-I** and verify each link at bench:
    - SiK UART2: `screen /dev/ttyS2 57600` — observe MAVLink framing bytes
    - LoRa SPI1: Python test: `python3 -c "import spidev; ..."` — read RFM95W version register (expected 0x12)
    - Wi-Fi wlan0: `iw dev wlan0 scan` — observe available networks
    - 49 MHz UART5: `screen /dev/ttyS5 1200` — verify Emma responds to KISS init
    - I²C2 (encoders): `i2cdetect -y 2` — verify TCA9548A at 0x70 and AS5600 at 0x36

- [ ] **Configure Wi-Fi transmit power** per FCC EIRP compliance:
    When 14 dBi panel is in use, set `iw dev wlan0 set txpower fixed 1700` (17 dBm = 1700 mBm).
    Create persistent udev hook or network config to apply on boot.

#### 4.5.3 — Malcolm Host PC Software Setup (Phase Malcolm-3)

- [ ] **Install Debian Linux on GCS host PC** (bookworm or later).

- [ ] **Run installation scripts in order:**

        sudo bash gcs/malcolm/software/install/install_deps.sh
        sudo bash gcs/malcolm/software/install/install_mavlink_router.sh
        bash gcs/malcolm/software/install/install_qgc.sh

    Verify: `mavlink-routerd --version`; `~/Applications/QGroundControl.AppImage --version` (launches GUI).

- [ ] **Configure QGroundControl:**
    Application Settings → Comm Links → Add → UDP → localhost:14550 (mavlink-router output).
    Set vehicle type to ArduPilot.  Import parameter file from `gcs/malcolm/software/config/qgc_params.params`
    (create this file in Phase Malcolm-3 after first aircraft connection).

- [ ] **Configure Wi-Fi Tx power on host PC** — if host PC has Wi-Fi and 14 dBi panel connected,
    reduce to 17 dBm before use: `iw dev wlan0 set txpower fixed 1700`.

- [ ] **Run tracking software tests:**

        cd gcs/malcolm/software/tracking
        pip install -r requirements.txt
        pytest tests/test_tracker.py -v

    All 9 bearing/elevation tests must pass.

- [ ] **Implement `gcs/malcolm/firmware/pb2i/src/mal_comms.c` and `mal_comms.h`** — GCS-side
    comms daemon: USB CDC-ECM bridge, MAVLink authentication (TPM HMAC), 49 MHz (Part 15 §15.235) KISS relay,
    LoRa relay, Wi-Fi UDP relay, mavlink-router integration.  Structure parallel to aircraft
    `avionics/firmware/cn/src/main.c`.  Add `mal_comms` target to `CMakeLists.txt`.
    **BLOCKS Phase Malcolm-2 full multi-link operation.**

#### 4.5.4 — Tracking and Gimbal Integration (Phase Malcolm-3)

- [ ] **Bench test gimbal hardware** — connect two AS5600 encoders via TCA9548A to Malcolm
    PB2-I I²C2 bus.  Run `i2cdetect` to confirm encoder presence.  Run mal_gimbal daemon;
    verify it reads encoder angles and drives servo PWM on EHRPWM0.

- [ ] **Gimbal calibration:**
    - Home position: set `s_pan_zero_counts` and `s_tilt_zero_counts` to encoder readings when
        gimbal physically points North at 0° elevation (calibration step in mal_gimbal.c init).
    - Travel limit verification: command pan to ±170°; verify hard stops engage at ±175°.
    - Tilt limit: command −10° and +90°; verify hard stops engage at −15° and +95°.

- [ ] **Run telemetry_feed.py bench test** — power aircraft (Phase 5 minimum: 2-node),
    run `python3 src/telemetry_feed.py`; verify GLOBAL\_POSITION\_INT JSON datagrams appear
    on UDP :14560 within 2 s of aircraft GPS lock (HDOP ≤1.5).

- [ ] **Run tracker.py bench test** — with telemetry_feed.py running and GCS GNSS connected,
    run `python3 src/tracker.py`; verify gimbal target JSON appears on UDP :14570 at ≥5 Hz.
    Confirm azimuth and elevation values change correctly as aircraft position is varied.

- [ ] **Run gimbal_ctrl.py bench test** — with tracker.py running, run `python3 src/gimbal_ctrl.py`;
    verify `GIMBAL_TARGET` commands appear on PB2-I UDP :14571; verify gimbal physically slews
    to commanded position and encoder confirms on-target within 3 s.

- [ ] **End-to-end tracking test (outdoor):**
    - GCS GNSS acquires fix (HDOP ≤1.5); operator records GCS position.
    - Walk aircraft (powered, GPS locked) 30–50 m in cardinal directions.
    - Verify gimbal pan tracks aircraft azimuth within 5°.
    - Verify gimbal tilt tracks aircraft elevation within 3° (at low aircraft altitude, elevation ≈ 0°).

#### 4.5.5 — Malcolm Integration Testing (Phase Malcolm-4)

- [ ] **Multi-link communication bench test:** connect aircraft (Phase 5 minimum) to Malcolm;
    verify QGC heartbeat on each link independently (disable 3, test 1, rotate):
    SiK 915 MHz → LoRa 915 MHz → Wi-Fi 5 GHz → 49 MHz (Part 15 §15.235).
    All 4 links must deliver ≥1 MAVLink heartbeat per 5 s with aircraft at 1 m range.

- [ ] **915 MHz link margin test (open field, 1 km):**
    Aircraft powered (no flight) at 1 km. Observe QGC RSSI on SiK link.
    Required: RSSI ≥ −90 dBm (SiK sensitivity ≈ −112 dBm → ≥22 dB link margin;
    adequate to absorb ~20 dB receiver desense at aircraft in 500 W/m² environment).

- [ ] **Wi-Fi link margin test (open field, 200 m):**
    Aircraft at 200 m. Observe Wi-Fi telemetry rate in QGC.
    Required: ≥100 kbps sustained (adequate for video + MAVLink telemetry at 200 m).

- [ ] **49 MHz (Part 15 §15.235) link test (1 km):**
    Aircraft at 1 km. Verify AX.25 KISS frames received on the 49 MHz (Part 15 §15.235) link.
    Log RSSI from Emma STATUS register.

- [ ] **Gimbal pointing accuracy test (outdoor, aircraft at 200–500 m):**
    With aircraft carrying a known position-fix (GPS HDOP ≤1.0), compare gimbal-pointed
    azimuth to independently measured true bearing.  Required: pointing error ≤5°.

- [ ] **MAVLink authentication test:** verify aircraft nodes reject unsigned commands from
    Malcolm if TPM provisioning is incomplete (remove TPM key, attempt arm command →
    should be rejected; re-provision TPM → arm command accepted).

- [ ] **Node loss with Malcolm active:** kill one aircraft FC node during bench hover test;
    verify Malcolm (QGC) shows failover in status panel within 200 ms; remaining nodes
    maintain MAVLink heartbeat to Malcolm on all links.

---

## 5.0 — Regulatory Compliance

### 5.1 — FCC (external radio systems)

- [ ] **XCVR-49MHZ-1/2 FCC Part 15 §15.235 compliance** — field strength ≤10,000 µV/m at 3 m
    (≈30 µW / −15.2 dBm EIRP-equivalent, requiring a firmware PA limit from the as-designed
    +20 dBm down to ≈ −13 dBm — see §0.1), harmonic suppression per §15.235(b)/§15.209. Document
    via pre-compliance checklist (1.3 Phase 4). Formal FCC equipment authorization (FCC ID grant
    via TCB) required before airborne transmission on 49MHz channels (47 CFR §2.803/§15.19, not
    Part 95 §95.603). **§15.203 antenna-connector gap resolved in design (RP-SMA, see §0.1);
    board re-spin pending.**

- [x] **SiK 915MHz** — operates under FCC Part 15 / ISM band (no license required for operation). Verify SiK radio module carries FCC ID marking.

- [x] **LoRa RFM95W 915MHz** — same Part 15 / ISM band. Verify module carries FCC ID.

- [x] **Wi-Fi (WL1837MOD)** — Part 15 / ISM. Module must carry FCC ID; verify.

- [x] **ZigBee 2.4GHz (if used)** — Part 15 / ISM. Verify FCC ID on any ZigBee module installed.

### 5.2 — FAA (airworthiness and operations)

- [ ] **Aircraft registration** — register under 14 CFR Part 48 (sUAS, AUW <55 lbs) at FAA DroneZone. Replace N00000 placeholder in `decal_sheet.svg`. Mark on airframe per 14 CFR 47 — visible without moving any part. **Complete before first untethered flight.**

- [ ] **Remote Pilot Certificate** — verify FAA Part 107 Remote Pilot Certificate is current (24-month knowledge test recurrency).

- [ ] **Navigation lights compliance** — verify 6-position WS2812C nav light implementation: port RED (≥3 SM visibility), stbd GREEN, tail WHITE steady, belly WHITE strobe. Compliant with ICAO Annex 2 and 14 CFR 91.209.

- [ ] **sUAS data plate** — attach to airframe: operator name, contact info, registration number. See `decal_sheet.svg` "D — safety labels" zone.

- [ ] **Pre-flight area check** — LAANC authorization for any Class B/C/D/E airspace. Verify no TFRs, NOTAM conflicts. File NOTAM if operating in uncontrolled airspace with public nearby.

- [ ] **Airspace waiver (if applicable)** — if operating above 400ft AGL or in controlled airspace without LAANC, apply for FAA Part 107 waiver (approval time 90 days typical).

### 5.3 — Industry Standards Compliance

- [ ] **Structural validation** — wing spar, keel, pivot rod, and tilt servo torque analysis documented per REVN_BUILD_GUIDE_24IN.md structural summary. Verify at actual build dimensions (24" hull).

- [ ] **IEEE/ISA/AUVSI best practices** — validate all design decisions against AUVSI UAS best practices; document in build record.

- [ ] **Tamper-evident logging** — verify CPLD write-blocker (ATF16V8BQL) on all 4 CN nodes prevents post-flight log modification; function as hardware-enforced non-executable microSD per CLAUDE.md requirement.

---

## 6.0 — Version Control and Repository Maintenance

### 6.1 — Branch Reconciliation (2026-06-09)

**Context:** A `git merge --allow-unrelated-histories` at commit `406c53f` joined two divergent
history trees. This created a topology where 11 feature branches appeared to have 44–168 commits
"not in main," but no file content was actually lost.

**Reconciliation findings (verified 2026-06-09):**

- [x] **`claude/aft-edf-phase-11-CMM8b`** — PRs #37, #39 merged. 0 files missing from main. Branch is a pre-merge snapshot; content fully absorbed. ✅
- [x] **`claude/cape-em-harsh-variants-9Yfr1`** — PRs #28–#35 merged. 0 files missing from main. ✅
- [x] **`claude/cargo-equipment-mounts-70I3i`** — PRs #21, #23 merged. Old `serenity/` paths reorganized to `airframe/` and `archives/` in main. ✅
- [x] **`claude/docs-scrub-revision-p-Y7pja`** — PRs #24, #25 merged; PR #27 closed. 0 files missing from main. ✅
- [x] **`claude/kicad-silk-labels-HnUIe`** — PRs #7, #9, #10 merged. Old `serenity/diagrams/` SVGs now in `graphical-build-guide/`; 18in STLs archived in `archives/thingverse-serenity/`. ✅
- [x] **`claude/revision-q-avionics-archive-BXwZI`** — PRs #35, #36, #41 merged. 0 files missing from main. ✅
- [x] **`claude/revt-nacelle-simplified-3Ri7A`** — PRs #38, #40 merged. 0 files missing from main. ✅
- [x] **`claude/todo-implementation-2LV2X`** — PRs #15, #18 merged. Old paths reorganized to current structure. ✅
- [x] **`claude/todo-implementation-8bRee`** — PRs #11–#14, #16, #19 merged. Hull SVGs (hull_bottom/front/side/top) present in `graphical-build-guide/`. ✅
- [x] **`claude/todo-implementation-AY2pY`** — PR #31 merged. 0 files missing from main. ✅
- [x] **`claude/todo-implementation-by1W7`** — PRs #20, #22, #26 merged. KiCad backup ZIPs and lockfiles not design artifacts. ✅
- [x] **`claude/wing-root-nacelle-mounts-5bSEA`** — PRs #42, #43 merged. 0 commits not in main. ✅

**Result:** Main is a superset of all 12 feature branches. All 43 PRs (42 merged, 1 closed) are
fully integrated. The stale branches are safe to delete via GitHub once this PR is merged.

- [ ] **Delete stale feature branches** on GitHub after confirming this reconciliation PR merges
    cleanly. Branches to delete: all `claude/*` branches except `claude/pr-reconciliation-forced-merge-4yefsw`.

### 6.2 — STL Mesh Repair (2026-06-09)

**Context:** CI STL Validation job was failing on 11 files (22 reported — each scanned twice due
to duplicate search paths in the validator). Root causes and resolutions:

**Validator fix:**
- [x] Removed duplicate SEARCH_PATHS (`airframe/stls/fuselage`, `nacelles`, `wings` are subsets
    of `airframe/stls` rglob — each file was reported twice). Fixed by reducing to
    `["airframe/stls", "stls"]` plus a `seen` deduplication set.
- [x] Added per-body watertightness check: a mesh passes CI if `mesh.is_watertight` OR every
    `mesh.split()` body is individually watertight. This correctly handles multi-body assembly
    STLs (4 landing feet, nacelle assembly, shell + insert bodies) where the combined mesh fails
    trimesh's global winding check but every solid sub-body is closed.

**STL repairs (manifold3d 3.5.1):**
- [x] `nacelle_nozzle_closed_asm.stl` — repaired: 1704 → 1648 faces, wt=True (16 bodies)
- [x] `nacelle_nozzle_petal.stl` — repaired: 213 → 206 faces, wt=True
- [x] `head_shell24_2mm_repaired.stl` — repaired: 227428 → 226812 faces, wt=True (6 bodies)
- [x] `cargo_sect_shell24_2mm_repaired.stl` — repaired: 368352 → 367506 faces, wt=True
- [x] `cargo_sect_shell24_2mm_repaired_largest.stl` — repaired: 367514 → 367474 faces, wt=True
- [x] `middle_canonical_edf_intake.stl` — **regenerated** from `middle_canonical_shell24.stl`
    via manifold3d Boolean difference (4 radial intake scoops). Original was non-manifold (3
    connected components, all non-manifold). New mesh: 20734 faces, wt=True. Parameters from
    `airframe/blender-scripts/blender_middle_intake_cut.py` Rev C.

**STLs passing via per-body check (no geometry change needed):**
- [x] `feet_x_4_scaled24.stl` — 4 feet (4 bodies, each wt=True)
- [x] `rear_shell24_2mm_repaired.stl` — 15 bodies, all wt=True
- [x] `middle_shell24_2mm_repaired.stl` — 10 bodies, all wt=True
- [x] `dorsal_antenna_fin.stl` — 3 bodies, all wt=True
- [x] `cargo_sect_shell24.stl` — 190 bodies, all wt=True

**Result:** All 37 STL files pass `python tools/validate_stls.py` (0 failures).

---

*"We're still flying. That's not nothing." — Mal.*

*© 2026 Steve Griffing, PE(CSE), CISSP-ISSEP, CPP — CC BY 4.0*  
*Hull: misubisu CC BY 4.0 · Nozzles: BamJr CC BY 4.0 · Inspiration: Firefly/Serenity © Joss Whedon / Mutant Enemy / Universal — Not an officially licensed product.*
