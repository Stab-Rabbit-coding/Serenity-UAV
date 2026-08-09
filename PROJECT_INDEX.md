# PROJECT_INDEX.md — Serenity UAV
<!-- Auto-maintained: updated whenever active files are added or removed. -->
<!-- Archive contents described in ARCHIVE_INDEX.md. -->
<!-- Last updated: 2026-08-09 — Automated reconciliation pass -->
                                    chapter/section/paragraph per citation, repo usage index)
REPO_ENFORCEMENT.md               — Repository rules
SECURITY.md                       — Security policy and vulnerability reporting
WBS.md                            — Master WBS index (full record, compact: headings/short
                                    checkbox items only, ≤70 chars each, done+open); full
                                    detail lives in the subordinate WBS.md files per-folder
TODO.md                           — Open-work-only subset of WBS.md (what's left to do)
package.json                       — Node.js dependency manifest (tooling/preview support)
package-lock.json                  — Node.js dependency lockfile
previewConfig.json                 — Live preview configuration
requirements-dev.txt               — Python development dependencies
```

---

## tools/

Repository-level engineering tools and build automation.

```text
TODO.md                           — Build-tools & automation reference index (pointer view;
                                    graphical-build-guide/WBS.md for the owned detail)
AGENTS.md                         — Build tools and automation standards (hull-frame bake tool,
                                    Blender pipeline, SCAD generation, mesh validation)
                                    json.dump() round-trip. docs/bom_*.json mixes expanded and
                                    compact styles; rewriting via json.dump silently re-expands
                                    the compact ones, adding ~35 lines of unrelated diff churn
                                    and re-surfacing pre-existing DevSkim TODO findings. Run
                                    after ANY script that rewrites a BOM. --check for a
                                    pre-commit gate; matches on data equality (not ref/stl,
                                    which can collide) and verifies before writing.
                                    --schematic-parity); HARD/SOFT severity policy, --changed-since
                                    scoping for pre-existing per-board DRC debt
                                    against the baked head shell on the 40° flat (replaces manual slicer checks)
                                    STLs (hull frame: X=+port, Y=+aft, Z=+dorsal);
                                    idempotent via 'SerenityUAV HULL-FRAME R1' STL
                                    header marker; single source of the historical
                                    placement constants (COMPONENTS)
                                    (post/spring/ductile wires, assembled/exploded/deformed)
                                    into airframe/stls/fuselage/landing-gear/; see
                                    docs/LANDING_GEAR_ANALYSIS.md §16
```

---

## airframe/

Structural design, fabrication, 3D modeling, and CAD assembly.

```text
WBS.md                            — Airframe WBS detail (full record): §1.1.0 hull-frame
                                    standard, §1.1.5 non-printable placeholders, §2.1/§2.2/
                                    §2.3/§2.6 procurement BOMs
TODO.md                           — Open-work-only subset of WBS.md
AGENTS.md                         — Airframe design standards (coordinate system, CAD/3D
                                    modeling, hull-frame bake, fabrication specs, STL
                                    validation, structural joints, landing gear)
                                    PMMA windows, cargo interior bosses, Jayne mounting
                                    mounts, nacelle servo bracket
                                    regeneration, Kaylee/Simon middle-section bays
```

### airframe/FreeCAD-scripts/

Assembly pipeline for FreeCAD 0.20+ with Assembly4.

```text
                                    baked hull-frame STLs, identity placements; run with
                                    freecadcmd)
```

Serenity-Subsystem-Assembly.py, serenity_subsystem_assembler.py,
airframe/archive/FreeCAD-scripts/; see ARCHIVE_INDEX.md.)

### airframe/blender-scripts/

Headless Blender Python scripts for shell hollowing and STL generation.

```text
                                    hull-frame STLs, renders 17 PNGs (6 principal + 8 iso +
                                    3 close-up) to graphical-build-guide/pngs/
                                    airframe/AGENTS.md Hull-Frame Coordinate Standard) + operands/ boolean
                                    operand meshes (inner/outer split surfaces, engraved text meshes)
```

### airframe/gcode/davinci-jr-proto/

Prototype print batches (DaVinci Jr., PLA, visual-only parts).

```text
.gitignore                        — VCS ignore rules for generated g-code batch output
                                    docs/PROTO_PRINT_DAVINCI_JR.md)
```

### airframe/freecad/assembly/

Working FreeCAD assembly directory (in-progress / backup state; not yet the published
canonical `SerenityAssembly.FCStd` referenced by airframe/AGENTS.md's Hull-Frame Coordinate Standard).

```text
                                    Hull-Frame Coordinate Standard)
```

(serenity_fuselage_asm4.py archived 2026-06-29 to airframe/archive/FreeCAD-scripts/;
see ARCHIVE_INDEX.md.)

### airframe/openscad/

All parametric source files.  Compiled to STLs via `airframe/FreeCAD-scripts/Makefile`.

#### airframe/openscad/fuselage/

```text
                                    10mm lens, ToF (STBD bump) 8mm, crosshair laser (CL) 6mm exit; bumps shaved +
                                    4× M2 inserts; use'd by head_shell24.scad
                                    carrying all three bow apertures; replaces the two camera bumps / separate bezels
                                    2× ventral hatch covers (battery/Kaylee), 2× ventral hatch frames (Rev R)
                                    rendered/printed; superseded by wire_brace_leg.scad (Rev R5);
                                    see docs/LANDING_GEAR_ANALYSIS.md (Rev R5)
                                    brace (2 spring apex wires, 2 ductile 1/3-down wires); see
                                    docs/LANDING_GEAR_ANALYSIS.md Rev R5
                                    crash fuse; kept for reference only, superseded by
                                    wire_brace_leg.scad's single-bend bowed-wire strut
cargo/
```

#### airframe/openscad/nacelles/

```text
 nacelle_bevel_housing, nacelle_bevel_pair, nacelle_pinion, nacelle_sector_gear
```

#### airframe/openscad/wings/

```text
                                        RENDER_SIDE=+1 port, -1 stbd, 0 both
```

### airframe/diagrams/

Reference diagrams and machine-readable profiles generated from hull analysis.

```text
ring_frames/
[Nick Henning REF-CAD-002 reference renders + permission email MOVED 2026-07-20 to
 docs/references/nick-henning/ — consolidated with all Nick Henning material and the other
 canonical references; see the docs/references/ section below and REFERENCES.md REF-CAD-002]
```

### airframe/stls/

Compiled and repaired STLs ready for slicing.

#### airframe/stls/fuselage/

```text
                                    bow_sensor_faceplate.scad, see fuselage/ section above)
                                    lofted, per-station conforming sleeve (samples actual inner-cavity
                                    cross-section at each Y, insets by bond gap, lofts via pairwise
generate_head_cargo_splice_collar.py, generate_cargo_middle_splice_collar.py,
                                    each extruded ONE constant inner contour straight across the
                                    joint, which passed through solid plastic (collar∩shell ≈
                                    1600-2000 mm³/side); still on disk, not yet archived
landing-gear/
[Rev R1.4 parametric corner V-brace concept (arm_upper_r1/arm_lower_r1/main_strut_r1/
docs/LANDING_GEAR_ANALYSIS.md (Rev R5). Superseded by the Rev R5 wire-brace files below.]
                                    tools/build_landing_gear_views.py + wire_brace_leg.scad)
                                    the field-inspection reference shape
                                    placeholders, correct relative position
                                    concept (Rev R2–R4), retired per
                                    docs/LANDING_GEAR_ANALYSIS.md in favor of Rev R5; not
                                    yet archived
cargo/
```

#### airframe/stls/nacelles/

```text
                                    nacelles/edf_aft_spider_sleeve.scad)
                                    nacelles/edf_stator_sleeve.scad)
                                    required by tools/bake_hull_frame.py,
                                    airframe/FreeCAD-scripts/serenity_assembly.py, and the
                                    FreeCAD-scripts Makefile (do not archive)
                                    same active-pipeline dependency as eng_left_* (do not archive)
                                    Rev S1 nozzle/nav/intake mods baked in); required by
                                    tools/bake_hull_frame.py, serenity_assembly.py, and the
                                    FreeCAD-scripts Makefile (active, do not archive)
                                    same active-pipeline dependency as nacelle_port_revs.stl (do not archive)
nozzles/
                                    Ø71 housing + 8 flaps, closed) of the Rev T pushrod-
                                    driven nozzle; re-rendered 2026-07-18
                                    of nacelle_nozzle_iris.scad); print part, 2026-07-18
                                    no gear teeth; RENDER_PART="ring"); 2026-07-18
                                    (RENDER_PART="flap", print × 8); 2026-07-18 [REF-CAD-001]
```

#### airframe/stls/wings/

```text
```

### airframe/placeholders/

Dimensionally-accurate bounding-geometry STL placeholder files for all non-printable
Rev R BOM components.  Used for FreeCAD assembly exploded views and build guides.
Generated by `generate_placeholders.py` (pure Python, stdlib only).
STL header marker: `SerenityUAV PLACEHOLDER R1`.
FreeCAD catalog: `airframe/FreeCAD-scripts/serenity_placeholders_assembly.py`.

```text
propulsion/
                                    still reflects the pre-Rev-R1 120 mm rear EDF (superseded
                                    spec is 55 mm, see root AGENTS.md); pending regeneration to
                                    EDF_55mm_6S_deferred.stl for Phase 11
                                    reflects the pre-Rev-R1 120 mm EDF's ESC sizing; pending
                                    regeneration to ESC_50A_6S_BLHeli32_deferred.stl for Phase 11
servos/
bearings/
structural/
avionics/
power/
cargo/
gears/
hardware/
lighting/
wiring/
gcs/
foam/
faraday/
```

### airframe/FreeCAD-scripts/ (updated Rev R1 + placeholders)

```text
                                    run with freecadcmd; output Serenity-Placeholders.FCStd)
```

(Deprecated prototypes assembly1.py, Serenity-Assemble.py,
Serenity-Subsystem-Assembly.py, serenity_subsystem_assembler.py, and

### airframe/ (root-level files)

```text
                                    gitignored (*.FCStd) like all FreeCAD documents, so it carries
                                    Distinct from the canonical
                                    airframe/freecad/assembly/SerenityAssembly.FCStd (airframe/AGENTS.md
                                    before treating either as authoritative; flagged, not resolved
                                    here.
```

---

## avionics/

KiCad PCB schematics and layouts, electronics design, firmware, and communications stack.

```text
WBS.md                            — Avionics WBS detail (full record): §1.2 (archived),
                                    §1.2a (Wash/Zoe/Emma EMI-hardened), §1.8 Names, §1.9
                                    workload, §2.4/§2.5 procurement
TODO.md                           — Open-work-only subset of WBS.md
                                    XCVR-49MHZ-1 (superseded)
                                    hardening beyond the PCBs (500 W/m^2)
AGENTS.md                         — Avionics design standards (cape naming, KiCad DRC
                                    workflow, security/cryptography, communications
                                    protocols, external radio regulations, avionics
                                    architecture)
```

### avionics/firmware/

CMake-based firmware for PocketBeagle 2 Industrial (AM6254) nodes.

```text
README.md                         — Firmware build guide
common/
CMakeLists.txt
include/
src/
dts/
README.md
cape-a/
cape-b/
fc/
CMakeLists.txt
src/
tools/
    requirements.txt
    .gitignore                    — VCS ignore rules for calibration tool output
cn/
CMakeLists.txt
src/
```

### avionics/kicad/

KiCad 7/9 PCB design files.  All active designs are Rev R (EMI-hardened -2 variants).

```text
README.md                         — KiCad directory overview, generation workflow, DRC notes
.gitignore                        — VCS ignore rules for KiCad backups/autosave/fp-info-cache

Board designs are organized one folder per board, each following the same internal layout
(established as the Kaylee folder, replicated to Wash/Zoë/Emma/Jayne):

[generated by gen_cape_a2.py + gen_cape_a2_pcb.py]

[generated by gen_cape_b2.py + gen_cape_b2_pcb.py]



STANDALONE, not a PB2-I cape; merges the former separately-documented "Vera" board identity
into the Jayne cargo-handling system, see Jayne.md below):
                                    Wash/Zoe Rev R baseline)
                                    DS_Laser_2P, phyCORE-AM62x_PCM071_2xBTH-060 SoM land,
                                    TQFP-128-1EP_KSZ9477…EP10x10 = generic TQFP-128 + datasheet
                                    10×10 GND EP, Wurth_749010012A_10-100BASE-TX extracted from
                                    the old board)
                                    clean-room symbols (PCM-071 SoM + KSZ9477 + MSPM0G3507 +
                                    ISOW1044 + SLB9670) + discrete carrier rails; ERC 0 errors.
                                    Built by scripts/gen_Jayne_carrier_sch.py
                                    placeholders, SoM on B.Cu; nose-carrier trapezoid outline;
                                    initial shelf-pack placement (no shorts), traces not routed.
                                    Built by scripts/gen_Jayne_carrier_pcb.py
                                    (FootprintLoad-after-Remove segfault; unwrapped PAD objects)
                                    worked around by gen_Jayne_carrier_pcb.py
                                    superseded by gen_Jayne_carrier_sch.py for the schematic
                                    gen_Jayne_carrier_pcb.py
                                    signal name; adds carrier regulators + PWR_FLAGs)
                                    pad nets via text pass, shelf-pack placement)
scripts/gen_Jayne_som_symbol.py, gen_Jayne_som_pcm071.py, gen_Jayne_ic_symbols.py,
scripts/gen_Jayne_ksz_symbol.py, gen_Jayne_ds_footprints.py, gen_Jayne_bth060_footprint.py
                                    docstring for provenance; SoM pinout is PHYTEC-published
                                    fact, not SnapEDA geometry)
scripts/mod_Jayne_corners.py, mod_Jayne_trapezoid.py, mod_Jayne_ds_pcb.py,
                                    trapezoid outline, direct-solder pad nets, SoM placement)
[see avionics/jayne/WBS.md §1.2c and Jayne.md above for full status/open items]

CAN-PERIPH-GW-1 (fleet trust-module CAN-FD/RS-485 peripheral gateway; new 2026-07-26,
stackable via N_STACKS; publishes AK7455 nacelle tilt-encoder data and accepts
UART/TTL/BSHOT/PWM servo commands over CAN-FD+RS-485; see CAN-PERIPH-GW-1.md):
kicads/CAN-PERIPH-GW-1.kicad_sch, kicads/CAN-PERIPH-GW-1.kicad_pcb, kicads/CAN-PERIPH-GW-1.dsn,
                                    nets, 0 shorts; footprint placement is the user's own manual
                                    packing, never regenerated by script after 2026-07-26)
                                    user's manual component packing/board resize)
                                    auto-route attempted and reverted, see script docstring)

Trust-module additions to existing boards (MCU + SLB9670 TPM + ISOW1044BDFMR CAN-FD +
ISOW1412 RS-485, or subset per board's needs), all 2026-07-26, all ERC 0:
                                    docstring for why gen_kaylee.py itself is NOT regenerated
                                    (pre-existing drift from the checked-in working file)
                                    CAN-FD/RS-485 via the P1/P2 PocketBeagle2 link)
                                    session's additions) broken ADM2795EBRWZ pin numbers and
                                    ISOW1044BDFMR footprint, and renames ADM2795E→ISOW1412;
                                    verified zero ERC regression (Wash 48 / Zoë 234, unchanged)

ENC-NACELLE-1 (nacelle encoder breakout):
ENC-NACELLE-1.kicad_sch
ENC-NACELLE-1.md

Shared symbols/footprints (avionics/kicad/symbols/):
Jayne_ISOW1044BDFMR.kicad_sym, Jayne_KSZ9477.kicad_sym, Jayne_MSPM0G3507_RGZ.kicad_sym,
Jayne_SLB9670_TPM.kicad_sym, Jayne_SoM.kicad_sym, Jayne_SoM_PCM071.kicad_sym
                                    half and SoM (see each script's docstring for sourcing)
ISOW1044BDFMR_pinmap.csv, KSZ9477STXI_pinmap.csv, MSPM0G3507SRGZR_pinmap.csv,
                                    above (primary-datasheet-derived, not SnapEDA geometry)
isow1044.pdf, mspm0g3507.pdf, KSZ9477S-Data-Sheet-DS00002392C.pdf, SLB_9670VQ20_Infineon.pdf
                                    parts (owner's call to keep in-repo as authoritative refs)

incompatible with this repo's CC BY 4.0): ISOW1044BDFMR.kicad_sym, KSZ9477STXI.kicad_sym,
*.step, *.kicad_mod, SLB 9670VQ2.0.lbr.

Shared Python generation scripts (avionics/kicad/, not board-specific):
                                   + scripts/mod_emma_pcb.py schematic-first migration)

```

Note: the Rev-Q-and-earlier archived CAPE-A-1/CAPE-B-1/XCVR-49MHZ-1 gerber sets and the
avionics/kicad/archive/ KiCad archive have both been consolidated under
ARCHIVE_INDEX.md. `avionics/gerbers/` no longer exists on disk at all.

---

## docs/

Project documentation, design specifications, analysis reports, and standards references.

```text
WBS.md                            — Docs/standards/regulatory WBS detail (full record) —
                                    §0.x, §1.5-1.7, §5.x, §6.x
TODO.md                           — Open-work-only subset of WBS.md
AGENTS.md                         — Documentation standards (standards vetting policy,
                                    references management, measurements and units,
                                    version control, traceability matrix)
PROJECT_INDEX.md                  — This file: active project directory tree
                                    phyCORE-AM62A SoM + trapezoidal carrier re-scope, locked
                                    2026-07-11; honest scope of what's clean-room vs placeholder
README.md                         — Rev M 18-inch project overview (SUPERSEDED; active README.md at root)
                                    truth for hull/exterior fidelity; see REFERENCES.md Part XIV
                                    and airframe/AGENTS.md "Canonical Accuracy References").
                                    Authority ranking: QMx 2007 pack > Nick Henning > Thingiverse.
                                    AUTHORITATIVE canonical geometry reference; copyrighted
                                    commercial product, NOT redistributed/relicensed as CC BY
                                    email 2026-07-06; derived from show/QMx canon, higher mesh
                                    detail than the QMx line art
                                    final: backside/front/top)
                                    engines", Thingiverse Thing 7330462 (REF-CAD-004, CC BY 4.0) —
                                    ORIGIN of the project's s_*.stl geometry; verify against the
                                    more-authoritative refs above, still usable
                                    s_wings_both, s_eng_left/right, s_legs, s_feet_x_4, s_pivot_arm_a…)
```

---

## current-specification/

Active design specifications, requirements, and version-controlled design baselines.

```text
TODO.md                           — Specification-sync reference index (pointer view into
                                    docs/WBS.md §1.6/§1.7/§6.3)
AGENTS.md                         — Specification standards (revision policy, document
                                    structure, standards citations, traceability matrix,
                                    specification approval workflow)
                                    TODO.md §6.3; a serenity-rev-s.jsx complete non-delta
                                    supersedes bom_revR.csv, archived 2026-07-04)
```

> Note: `serenity-rev-q.jsx` and `bom_revQ.csv` are NOT present in this directory; the Rev Q
> historical references live in `archives/` (`archives/serenity-rev-q.jsx`,
> `archives/bom_revQ.csv`, `archives/docs-superseded/bom_revQ.csv`,
> `archives/docs-superseded/serenity-rev-q.jsx`). See ARCHIVE_INDEX.md.

---

## gcs/

Ground control station and mission planning software. Malcolm ("CAPT Reynolds") is the
ArduPilot-compatible GCS for Serenity UAV.  Architecture: 1× PocketBeagle 2 Industrial +
Cape-B-2 (Zoë) + Emma, USB CDC-ECM tethered to a host Debian Linux PC running QGroundControl.
Five radio links: SiK 915 MHz, LoRa 915 MHz, Wi-Fi 5 GHz, 49 MHz Part 15 §15.235 (AX.25),
Zigbee 2.4 GHz.  Servo-driven two-axis antenna gimbal with AS5600 magnetic encoders.
No external PAs (FCC-compliant with directional antennas).  IP65 field enclosure.

```text
WBS.md                            — Malcolm GCS WBS detail (full record) — §4.5 (ground
                                    control, gimbal, comms)
TODO.md                           — Open-work-only subset of WBS.md
AGENTS.md                         — GCS design standards (operator interface, command
                                    authentication, telemetry display, communications
                                    protocols, security/compliance, hardware requirements)
gcs/malcolm/
README.md                                — Malcolm GCS overview, architecture table, radio link
                                            table, directory layout, build/setup steps, security notes
hardware/
    docs/
                                            gain tables; no-PA conclusion; WiFi Tx power reduction
                                            encoder I²C, RF SMA, power rails, enclosure glands
    enclosure/
        openscad/
                                            110×80×55mm interior; EPDM gasket groove; 40mm fan
                                            cutout; cable gland locations; RENDER_MODE 0/1/2
    gimbal/
        openscad/
                                            sector gear, 120×100×12mm base plate with M6 tripod
                                            holes, 80mm OD turret; RENDER_MODE 0/1/2
                                            100mm wide, tilt range -10° to +90°
                                            with MF104ZZ bore; encoder magnet pocket 6.1mm dia;
                                            U-bolt clamps for 15mm Yagi boom; WiFi panel M4 holes
firmware/
    pb2i/
                                            static lib; strict security flags; MAVLINK_INCLUDE_DIR
        dts/
        k3-am6254-pocketbeagle2-malcolm-cape-b2.dts
                                            I²C2 TCA9548A+AS5600 encoders, UART2 SiK, UART5 49 MHz
        src/
                                            UART paths, LoRa SPI, WiFi tx_power_mbm, gimbal limits,
                                            AS5600 register map, TPM key handle, heartbeat timeout
                                            is_on_target; types mal_gimbal_pos_t, mal_gimbal_err_t
                                            AS5600 angle read (STATUS MD bit check), zero-calibration,
                                            rate-limited control, counts_to_deg, angle_to_duty_ns
                                            is_link_lost; types mal_aircraft_pos_t, mal_telemetry_status_t
                                            + GLOBAL_POSITION_INT; publishes JSON to UDP 127.0.0.1:14560
software/
    config/
                                            ports, PB2-I host, GNSS device, WiFi tx_power_mbm,
                                            49 MHz default channel
                                            qgc UDP 14550, tracking UDP 14552; serial fallback stubs
    install/
                                            udev rule for u-blox GNSS (/dev/gnss_gcs)
    tracking/
        src/
                                            publishes position JSON to UDP :14560
                                            elevation; GNSS reader; publishes gimbal targets to UDP :14570
                                            rate limiting 90°/s; dead-band 0.2°; sends GIMBAL_TARGET
                                            JSON to PB2-I UDP :14571
        tests/
                                            NE quadrant, horizontal/above/overhead/airborne elevations,
                                            azimuth and elevation range assertions
```

---

## deferred/

Design work deferred beyond the current build phase (Phases 5–10). Includes planned upgrades
for future build phases.

```text
WBS.md                            — Deferred-work WBS detail (full record) — Phase 11
                                    (aft EDF + RCS), Phase 12 (range-extender battery)
TODO.md                           — Open-work-only subset of WBS.md
AGENTS.md                         — Deferred work standards (status categories, planned
                                    upgrades, Phase 11+ scope, design decision history,
                                    phase numbering convention)
```

### deferred/aft-edf/

```text
README.md                         — Aft fuselage EDF design scope, rationale, and defer decision
openscad/
                                    regen to 55 mm EDF inlet + 4 RCS bleed taps
                                    edf_55_motor_mount.scad (still required by
                                    not archive until Rev R1 replacement exists)
                                    edf_55_thrust_tube.scad (still required by active build
                                    for 55 mm EDF
stls/
                                    boolean operands (× 8)
```

> 55 mm with a fixed canonical elliptical tail nozzle + 4 RCS bleed-air thrusters (per root AGENTS.md).
> The on-disk SCAD/STL files in this directory **still reflect the pre-Rev-R1 120 mm / iris-nozzle
> have not yet been regenerated as `edf_55_motor_mount.scad`, `edf_55_thrust_tube.scad`,
> `rear_nozzle_canonical.scad`, `rcs_thruster.scad`, etc. `edf_120_motor_mount.scad` and
> `edf_120_thrust_tube.scad` remain **active** (referenced by
> `airframe/blender-scripts/blender_edf_bore_and_petals.py`,
> `airframe/gcode/davinci-jr-proto/slice_all_batches.sh`, and
> `docs/PROTO_PRINT_DAVINCI_JR.md`) and must not be archived until the Rev R1 55 mm/RCS
> replacements are generated. This is a deferred-but-active Phase 11 scope, not stale work.

---

## graphical-build-guide/

Visual build guides, assembly sequences, fabrication checklists, and troubleshooting documentation.
SVG visual build guide cards and hull outline diagrams generated by `gen_hull_outlines.py`
from blender-rendered views.

```text
WBS.md                            — Phased physical-build WBS detail (full record) —
                                    Phases 0-4 + SVG rebuild pipeline (§1.5.6)
TODO.md                           — Open-work-only subset of WBS.md
AGENTS.md                         — Build guide standards (phased approach, guide structure,
                                    illustrations/graphics, troubleshooting, phase
                                    completion sign-off)
                                    diagram camera framing)
overview_svgs/
                                    (head/cargo/middle/rear sections, inner/outer hollow-wall
                                    comparisons, axis-labeled views, cross-sections, engrave
                                    previews) generated while iterating the hollowing pipeline,
                                    plus port_wall.stl (single-wall reference geometry probe)
                                    3 close-up), generated by
                                    airframe/blender-scripts/serenity_render_views.py
```

---

## archives/

Superseded designs retained for reference (not included in active build).
See ARCHIVE_INDEX.md for full contents.

```text
```

---

## airframe/archive/

Per-component archive STLs and blender scripts superseded by active files.
See ARCHIVE_INDEX.md.

```text
```

## --- AUTO-DISCOVERED (2026-07-20) ---
.github/linters/.ecrc — [PENDING AI CLASSIFICATION]
.github/linters/.markdown-lint.yml — [PENDING AI CLASSIFICATION]
.github/workflows/devskim.yml — [PENDING AI CLASSIFICATION]
.github/workflows/super-linter.yml — [PENDING AI CLASSIFICATION]
airframe/AGENTS.md — [PENDING AI CLASSIFICATION]
airframe/FreeCAD-scripts/Makefile — [PENDING AI CLASSIFICATION]
airframe/FreeCAD-scripts/faraday-enclosure.py — [PENDING AI CLASSIFICATION]
airframe/FreeCAD-scripts/freecad-stl2part.py — [PENDING AI CLASSIFICATION]
airframe/FreeCAD-scripts/make_flat_pattern.py — [PENDING AI CLASSIFICATION]
airframe/FreeCAD-scripts/serenity_assembly.py — [PENDING AI CLASSIFICATION]
airframe/FreeCAD-scripts/serenity_placeholders_assembly.py — [PENDING AI CLASSIFICATION]
airframe/TODO.md — [PENDING AI CLASSIFICATION]
airframe/VERIFY_PLACEMENT_CHECKLIST.md — [PENDING AI CLASSIFICATION]
airframe/WBS.md — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/add_structural_features.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_edf_bore_and_petals.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_hollow_shells.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_intake_cut.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_middle_intake_cut.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_nacelle_revo.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_nozzle_gen.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_shells_2mm_solidify.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_shells_v3.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/blender_stator_gen.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/check_nacelle_alignment.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/engrave_plaques.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/engrave_shuttles.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/cargo_sect_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/head_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/middle_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/cargo_inner_opened.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/cargo_sect_shell24_2mm_repaired__inner.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/cargo_sect_shell24_2mm_repaired__outer.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/head_inner_opened.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/head_shell24_2mm_repaired__inner.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/head_shell24_2mm_repaired__outer.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/middle_inner_opened.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/middle_shell24_2mm_repaired__inner.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/middle_shell24_2mm_repaired__outer.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/rear_inner_opened.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/rear_shell24_2mm_repaired__inner.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/rear_shell24_2mm_repaired__outer.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/text_inara.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/text_kaylee.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/text_river.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/text_shepherd.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/operands/text_simon.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/files-hollowed-24in/rear_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/fill_thin_details.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/finalize_cargo_middle.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/finalize_head_rear.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/generate_overview_svgs.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/hollow_manifold.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/inspect_shell_center.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/make_bay_text.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/make_shuttle_text.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/merge_cargo_interior.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/merge_head_interior.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/morph_open_voxel.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/regen_rear_interior.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/repair_shells_for_scad.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/serenity_render_views.py — [PENDING AI CLASSIFICATION]
airframe/blender-scripts/verify_shells.py — [PENDING AI CLASSIFICATION]
airframe/diagrams/ring_frames/ring_cargo_Y30_inner.csv — [PENDING AI CLASSIFICATION]
airframe/diagrams/ring_frames/ring_cargo_Y30_plate_PROVISIONAL.dxf — [PENDING AI CLASSIFICATION]
airframe/diagrams/ring_frames/ring_rear_Y290_inner.csv — [PENDING AI CLASSIFICATION]
airframe/diagrams/ring_frames/ring_rear_Y290_plate.dxf — [PENDING AI CLASSIFICATION]
airframe/freecad/assembly/SerenityAssembly.FCStd.bak2 — [PENDING AI CLASSIFICATION]
airframe/freecad/assembly/leg_2_scaled-oriented.stl — [PENDING AI CLASSIFICATION]
airframe/fuselage-covers/TODO.md — [PENDING AI CLASSIFICATION]
airframe/fuselage-covers/WBS.md — [PENDING AI CLASSIFICATION]
airframe/fuselage-joints/TODO.md — [PENDING AI CLASSIFICATION]
airframe/fuselage-joints/WBS.md — [PENDING AI CLASSIFICATION]
airframe/fuselage-mid/TODO.md — [PENDING AI CLASSIFICATION]
airframe/fuselage-mid/WBS.md — [PENDING AI CLASSIFICATION]
airframe/gcode/davinci-jr-proto/.gitignore — [PENDING AI CLASSIFICATION]
airframe/gcode/davinci-jr-proto/davinci_jr_pla.ini — [PENDING AI CLASSIFICATION]
airframe/gcode/davinci-jr-proto/slice_all_batches.sh — [PENDING AI CLASSIFICATION]
airframe/gcode/davinci-jr-proto/xyz_wrap.py — [PENDING AI CLASSIFICATION]
airframe/landing-gear/TODO.md — [PENDING AI CLASSIFICATION]
airframe/landing-gear/WBS.md — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/access_panels_24in.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/battery_tray.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/belly_panel.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/bow_sensor_faceplate.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/bow_sensor_pod.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/cargo/_export_cargo_port_root_chunk.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/cargo/cargo_sect_shell24.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/cargo/cargo_spar_drive.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/cargo/cargo_vera_faraday.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/head_shell24.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/landing_leg_assy.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/middle_canonical_shell24.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/rcrs49_wire_post.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/rear_shell24.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/wire_brace_leg.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/wire_loop_fuse.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/_export_inboard_cut.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/_export_pivot_slab.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/edf_aft_spider_sleeve.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/edf_stator_sleeve.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/gear_option_compare.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/nacelle_nozzle_iris.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/nacelle_nozzle_pushrod.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/nacelle_pod_50mm_tandem.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/nacelles/nacelle_servo_bracket.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/port_tilt_spar_assembly.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/wings/wings_s1223_revo.scad — [PENDING AI CLASSIFICATION]
airframe/openscad/wings/wings_s1223_revo.scad.backup-2026-07-18 — [PENDING AI CLASSIFICATION]
airframe/placeholders/avionics/Cape_A2_PCB_55x35mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/avionics/Cape_B2_PCB_55x35mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/avionics/Kaylee_PDB_90x65mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/avionics/PocketBeagle2_Industrial_56x35mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/avionics/XCVR_49MHZ2_PCB_55x35mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/avionics/microSD_64GB.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/bearings/B6804_20x32x7mm_GCS.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/bearings/MF104ZZ_4x10x4mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/bearings/MR63ZZ_3x6x2p5mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/cargo/DRV8833_Hbridge_breakout.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/cargo/Dyneema_SK75_0p5mm_coil.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/cargo/HX711_loadcell_ADC_breakout.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/cargo/N20_motor_300RPM_6V.stl — [SUPERSEDED 2026-07-27] Retired with the
                                    N20 winch train; replaced by the STS3215 (placeholder mesh
                                    pending the envelope gate in docs/CARGO_WINCH_SPECIFICATION.md
                                    §3.1). Do not place in new assemblies.
airframe/placeholders/faraday/Far_EMI_vent_40x40x6mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Far_FT_panel_55x35mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Far_bond_strap_100mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Far_cage_AV_70x50x82mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Far_fan_40mm_5V.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Far_ferrite_4mm_ID.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Far_gasket_AV_250x6x1mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Mal_far_fan_40mm_5V.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/faraday/Mal_far_gasket_470x8x1p5mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Foam_fill_cargo_190x200x159mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Foam_fill_head_125x231x136mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Foam_fill_middle_horseshoe_173x69x161mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Foam_fill_rear_136x177x154mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_avionics_bay_62x42x75mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_cargo_bay_120x150x80mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_far_cage_76x56x88mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_far_fan_spur_44x44x50mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_nacelle_pylon_20x80x20mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_power_bus_25x500x25mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_vent_exhaust_20x300x20mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_vent_intake_20x250x20mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/foam/Void_wiring_trunk_30x700x20mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/AS5600_encoder_breakout_15x15mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Antenna_2p4GHz_zigbee_rubber_duck.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Antenna_49MHz_whip_940mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Antenna_5GHz_panel_14dBi.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Antenna_915MHz_Yagi_9dBi.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Antenna_915MHz_omni_5dBi.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Antenna_GNSS_patch_ANN_MB00.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/B6804_20x32x7mm_gimbal_pan.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/GPS_module_M10Q_SparkFun.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Malcolm_enclosure_IP65_145x90x65mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Malcolm_tripod_antenna_mast.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/N42_disc_magnet_6x2mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Pololu_D24V22F6_6V2A_BEC.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/Pololu_D24V50F5_5V5A_BEC.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/RF_splitter_915MHz_2way_ZFSC.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gcs/TCA9548A_I2C_mux_breakout.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gears/Bevel_M1_14T_pair.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gears/Bevel_housing_CF_PETG.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gears/Pinion_M1_12T_R6mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/gears/Sector_gear_M1_R22mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/generate_placeholders.py — [PENDING AI CLASSIFICATION]
airframe/placeholders/hardware/Batt_strap_silicone_16mm_CAM.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/hardware/Insert_M25_brass_L5.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/hardware/Insert_M3_brass_L5.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/hardware/Pin_SS_3x5mm_hinge.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/hardware/Screw_M3x8mm_button_ISO7380.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/lighting/WS2812C_2020_SMD.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/power/Fuse_MAXI_150A.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/power/Fuse_mini_40A.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/power/LiPo_4S_10000mAh_175x64x38mm_GCS.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/power/LiPo_6S_2800mAh_115x35x35mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/power/LiPo_6S_4000mAh_138x44x36mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/power/Shunt_CSS2H_2512K_1mohm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/propulsion/EDF_120mm_6S_deferred.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/propulsion/EDF_50mm_6S.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/propulsion/ESC_40A_6S_BLHeli32.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/propulsion/ESC_80A_6S_BLHeli32_deferred.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/servos/DS3218MG_25kgcm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/servos/SG90_micro.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/structural/CF_bar_6x3mm_620mm_keel.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/structural/CF_plate_2mm_200x300mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/structural/CF_rod_3mm_300mm_stock.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/structural/CF_rod_4mm_300mm_stock.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/structural/CF_tube_12mm_OD_1p5w_350mm_spar.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/structural/PTFE_sleeve_4mm_OD_3mm_ID_52mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/wiring/PTFE_conduit_4mm_OD_3mm_ID_700mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/wiring/Post_49MHz_base_load_coil.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/wiring/Wire_10AWG_silicone_400mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/wiring/Wire_28AWG_STP_bundle_500mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/wiring/Wire_49MHz_antenna_0p3mm_470mm.stl — [PENDING AI CLASSIFICATION]
airframe/placeholders/wiring/Wire_4AWG_silicone_200mm_pair.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/battery_tray.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/belly_panel.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/bow_sensor_faceplate.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_cradle_autolatch.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_door_port.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_door_servo_bracket.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_door_stbd.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_drv8833_tray.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_fpv_bezel.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_gps_retention_ring.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_hinge_retention.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_release_servo_bracket.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_sect_shell24_2mm_bossed.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_sect_shell24_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_vera_faraday.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_winch_motor_mount.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/cargo_winch_spool.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/generate_cargo_doors.py — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/generate_cargo_hinge_retention.py — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/generate_cargo_mounts.py — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo/starboard-view-of-cargo_sect_shell24_2mm_repaired.svg — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/cargo_middle_splice_collar.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/dorsal_antenna_fin.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/generate_conforming_collars.py — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/head_cargo_splice_collar.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/head_shell24.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/head_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/inara_access_cover.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/middle_canonical_edf_intake.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/middle_canonical_shell24.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/middle_rear_splice_collar.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/middle_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/rear_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/fuselage/river_access_cover.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/edf_aft_spider_sleeve.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/edf_stator_sleeve.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/eng_left_shell24_50mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/eng_right_shell24_50mm_repaired.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nacelle_port_revs.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nacelle_servo_bracket.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nacelle_stbd_revs.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nozzles/nacelle_nozzle_flap.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nozzles/nacelle_nozzle_iris.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nozzles/nacelle_nozzle_ring.stl — [PENDING AI CLASSIFICATION]
airframe/stls/nacelles/nozzles/nacelle_nozzle_throat.stl — [PENDING AI CLASSIFICATION]
airframe/stls/wings/wing_port_s1223_revo.stl — [PENDING AI CLASSIFICATION]
airframe/stls/wings/wing_stbd_s1223_revo.stl — [PENDING AI CLASSIFICATION]
airframe/wings-nacelles/TODO.md — [PENDING AI CLASSIFICATION]
airframe/wings-nacelles/WBS.md — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_cargo_door_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_cargo_door_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_cargo_door_strutts_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_cargo_door_strutts_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_cargo_sect_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_cargo_sect_shell18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_left_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_left_shell18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_pistons_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_pistons_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_piv_outer_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_piv_outer_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_piv_pins_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_piv_pins_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_right_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_eng_right_shell18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_feet_x_4_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_feet_x_4_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_head_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_head_shell18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_legs_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_legs_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_middle_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_middle_shell18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_pivot_arm_a_scaled18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_pivot_arm_a_scaled18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_rear_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_rear_shell18.stl — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_wings_both_shell18.scad — [PENDING AI CLASSIFICATION]
archives/18in-scale-scad/s_wings_both_shell18.stl — [PENDING AI CLASSIFICATION]
archives/20260422-Serenity-RevF.zip — [PENDING AI CLASSIFICATION]
archives/20260429_files.zip — [PENDING AI CLASSIFICATION]
archives/Serenity Firefly with landing gear and swivel engines - 7330462.zip — [PENDING AI CLASSIFICATION]
archives/Serenity0Firefly0with0landing0gear0and0swivel0engines0-07330462.zip — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/ARCHIVE-REVQ.md — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/FreeCAD-scripts/Serenity-Assemble.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/FreeCAD-scripts/Serenity-Subsystem-Assembly.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/FreeCAD-scripts/assembly1.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/FreeCAD-scripts/serenity_fuselage_asm4.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/FreeCAD-scripts/serenity_subsystem_assembler.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/blender-scripts/blender_nacelle_integrated_v1.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/blender-scripts/blender_nacelle_integrated_v2.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/blender-scripts/blender_shells_v3_2mm.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/blender-scripts/blender_shells_v3_50mm.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/blender-scripts/generate_hollow_shells.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/blender-scripts/generate_shells_v2.py — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/edf_bore_sleeve.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/nacelles/nacelle_bevel_housing.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/nacelles/nacelle_bevel_pair.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/nacelles/nacelle_nozzle_idler.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/nacelles/nacelle_pinion.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/nacelles/nacelle_sector_gear.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/wings/wing_nacelle_pylon_revo.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/hull_engine_bell.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/landing_legs_hull_r1.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_cargo_door_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_cargo_door_strutts_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_cargo_sect_shell24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_cargo_sect_shell24_2mm.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_cargo_sect_shell24_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_cargo_sect_shell24_revs.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_feet_x_4_scaled24_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_head_shell24_2mm.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_head_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_head_shell24_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_middle_intake_shell24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_middle_shell24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_middle_shell24_2mm.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_middle_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_rear_shell24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_rear_shell24_2mm.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_rear_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/s_rear_shell24_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/edf_bore_sleeve.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_bevel_housing.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_bevel_pair.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_drive_pinion.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_pinion.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_pinion_a.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_port_revt.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_pushrod_crank.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_sector_gear.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_stbd_revt.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_tip_cap_port.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nacelle_tip_cap_stbd.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_bevel_housing.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_bevel_pair.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_nozzle_closed_asm.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_nozzle_closed_asm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_nozzle_idler.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_nozzle_idler_bracket.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_nozzle_petal.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/nacelle_nozzle_petal_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/nozzles/rear_nozzle_petal_repaired.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/sector_gear_22mm_fixed.obj — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/sector_gear_22mm_fixed.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/nacelles/stator_50mm.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/wings/wing_nacelle_pylon_revo.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/nacelle_nozzle_straight.scad — [PENDING AI CLASSIFICATION]
archives/airframe-archives/nacelle_pod_50mm_tandem_simple.scad — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-B_Cu.gbl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-B_Mask.gbs — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-B_Paste.gbp — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-F_Cu.gtl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-F_Mask.gts — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-F_Paste.gtp — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-In2_Cu.g2 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-NPTH-drl_map.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-NPTH.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-PTH-drl_map.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-PTH.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1-job.gbrjob — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1.net — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-B_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-B_Mask.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-B_Paste.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-B_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-Edge_Cuts.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-F_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-F_Mask.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-F_Paste.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-F_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-In1_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-In2_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1-job.gbrjob — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-A-1/CAPE-A-1/CAPE-A-1.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-B_Cu.gbl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-B_Mask.gbs — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-B_Paste.gbp — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-F_Cu.gtl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-F_Mask.gts — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-F_Paste.gtp — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-In2_Cu.g2 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-NPTH-drl_map.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-NPTH.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-PTH-drl_map.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-PTH.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1-job.gbrjob — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1.net — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-B_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-B_Mask.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-B_Paste.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-B_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-Edge_Cuts.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-F_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-F_Mask.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-F_Paste.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-F_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-In1_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-In2_Cu.gbr — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1-job.gbrjob — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/CAPE-B-1/CAPE-B-1/CAPE-B-1.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-B_Cu.gbl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-B_Mask.gbs — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-B_Paste.gbp — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-F_Cu.gtl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-F_Mask.gts — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-F_Paste.gtp — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-In2_Cu.g2 — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-drl_map.pdf — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1-job.gtl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/gerber-archive/XCVR-49MHZ-1/XCVR-49MHZ-1.drl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-A-1-backups/CAPE-A-1-2026-05-12_202152.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-A-1-backups/CAPE-A-1-2026-05-21_163955.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-A-1-backups/CAPE-A-1-2026-05-21_165517.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-A-1-backups/CAPE-A-1-2026-05-21_170545.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-A-1-backups/CAPE-A-1-2026-05-21_171620.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-A-1-backups/CAPE-A-1-2026-05-21_172625.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-19_234555.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-21_120000.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-21_134835.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-21_174009.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-21_221653.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-22_114948.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-22_115954.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-22_120631.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-22_121147.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-22_121710.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-24_170015.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-31_203319.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-31_204417.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-31_205610.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-31_210615.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/CAPE-B-1-backups/CAPE-B-1-2026-05-31_211230.zip — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/ARCHIVE-REVQ.md — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-1-no-comment.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-1-no-comment.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-1.kicad_prl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-1.kicad_pro — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-2.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-2.kicad_prl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-2.kicad_pro — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-2.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-A-2.md — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1.kicad_prl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1.kicad_pro — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1a.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1a.kicad_prl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-1a.kicad_pro — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-2.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-2.kicad_prl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-2.kicad_pro — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-2.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CAPE-B-2.md — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CM3-CARRIER-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CM3-CARRIER-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CM4-CARRIER-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CM4-CARRIER-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CM4-CARRIER-2.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/CM4-CARRIER-2.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/COMMS-HAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/COMMS-HAT-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/COMMS-HAT-SWITCH.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/COMMS-HAT-SWITCH.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/PWR-DIST-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/PWR-DIST-1.md — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/SENSORHAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/SENSORHAT-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/TRIHAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/TRIHAT-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/XCVR-49MHZ-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/XCVR-49MHZ-1.kicad_prl — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/XCVR-49MHZ-1.kicad_pro — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/XCVR-49MHZ-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/XCVR-49MHZ-1.md — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/gen_cape_a2.py — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/gen_cape_a2_pcb.py — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/gen_cape_b2.py — [PENDING AI CLASSIFICATION]
archives/avionics-archives/kicad-archives/archive/gen_cape_b2_pcb.py — [PENDING AI CLASSIFICATION]
archives/bom_revH1.json — [PENDING AI CLASSIFICATION]
archives/bom_revP.csv — [PENDING AI CLASSIFICATION]
archives/bom_revQ.csv — [PENDING AI CLASSIFICATION]
archives/bom_revR.csv — [PENDING AI CLASSIFICATION]
archives/build_guide_00_cover.svg — [PENDING AI CLASSIFICATION]
archives/build_guide_20_node_placement.svg — [PENDING AI CLASSIFICATION]
archives/chat/2026-04-22-11-20-04-serenity-tiltrotor-drone-design.txt — [PENDING AI CLASSIFICATION]
archives/chat/2026-04-28-14-10-02-serenity-tiltrotor-drone-design.txt — [PENDING AI CLASSIFICATION]
archives/chat/2026-05-03-20-24-05-serenity-tiltrotor-drone-design.txt — [PENDING AI CLASSIFICATION]
archives/chat/journal.txt — [PENDING AI CLASSIFICATION]
archives/docs-superseded/POWER_SYSTEM_Q.md — [PENDING AI CLASSIFICATION]
archives/docs-superseded/README.md — [PENDING AI CLASSIFICATION]
archives/docs-superseded/bom_revQ.csv — [PENDING AI CLASSIFICATION]
archives/docs-superseded/serenity-rev-q.jsx — [PENDING AI CLASSIFICATION]
archives/files.zip — [PENDING AI CLASSIFICATION]
archives/generate_foam_svgs.py — [PENDING AI CLASSIFICATION]
archives/more-files.zip — [PENDING AI CLASSIFICATION]
archives/nacelle-nozzle-gear.jsx — [PENDING AI CLASSIFICATION]
archives/nacelles.jst — [PENDING AI CLASSIFICATION]
archives/sensorhat_mounting_tray.stl — [PENDING AI CLASSIFICATION]
archives/serenity firefly transport ship - 2601098.zip — [PENDING AI CLASSIFICATION]
archives/serenity-connectivity-revH.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-drone-COMPLETE-revH1.zip — [PENDING AI CLASSIFICATION]
archives/serenity-drone-rev-g.zip — [PENDING AI CLASSIFICATION]
archives/serenity-drone.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-esc-telem-revH1.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-b.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-c.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-d.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-f-.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-f.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-o.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-p.jsx — [PENDING AI CLASSIFICATION]
archives/serenity-rev-q.jsx — [PENDING AI CLASSIFICATION]
archives/serenity/.gitignore — [PENDING AI CLASSIFICATION]
archives/serenity/MANIFEST.json — [PENDING AI CLASSIFICATION]
archives/serenity/README.md — [PENDING AI CLASSIFICATION]
archives/serenity/package-lock.json — [PENDING AI CLASSIFICATION]
archives/serenity/package.json — [PENDING AI CLASSIFICATION]
archives/serenity/public/favicon.ico — [PENDING AI CLASSIFICATION]
archives/serenity/public/index.html — [PENDING AI CLASSIFICATION]
archives/serenity/public/logo192.png — [PENDING AI CLASSIFICATION]
archives/serenity/public/logo512.png — [PENDING AI CLASSIFICATION]
archives/serenity/public/manifest.json — [PENDING AI CLASSIFICATION]
archives/serenity/public/robots.txt — [PENDING AI CLASSIFICATION]
archives/serenity/src/App.css — [PENDING AI CLASSIFICATION]
archives/serenity/src/App.js — [PENDING AI CLASSIFICATION]
archives/serenity/src/App.test.js — [PENDING AI CLASSIFICATION]
archives/serenity/src/index.css — [PENDING AI CLASSIFICATION]
archives/serenity/src/index.js — [PENDING AI CLASSIFICATION]
archives/serenity/src/logo.svg — [PENDING AI CLASSIFICATION]
archives/serenity/src/reportWebVitals.js — [PENDING AI CLASSIFICATION]
archives/serenity/src/setupTests.js — [PENDING AI CLASSIFICATION]
archives/stale-20260601/README.md — [PENDING AI CLASSIFICATION]
archives/stale-20260601/airframe-stls/fuselage.md — [PENDING AI CLASSIFICATION]
archives/stale-20260601/antenna-layout.jsx — [PENDING AI CLASSIFICATION]
archives/stale-20260601/cm4-carrier-update.jsx — [PENDING AI CLASSIFICATION]
archives/stale-20260601/cockpit_dome_clear.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/comms-hat.jst — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/CM4-CARRIER-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/COMMS-HAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/LICENSE_AND_ATTRIBUTION.md — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/TRIHAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/build_plan.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/cockpit_dome_clear.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/components_overview.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/hull_cockpit_section.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/nacelle_pod_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/overview_bottom.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/overview_front.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/overview_side.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/overview_top.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/sector_gear_22mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF.zip — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/README.md — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/diagrams/build_plan.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/diagrams/components_overview.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/diagrams/overview_bottom.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/diagrams/overview_front.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/diagrams/overview_side.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/diagrams/overview_top.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/docs/LICENSE_AND_ATTRIBUTION.md — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/CM4-CARRIER-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/CM4-CARRIER-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/cm4-carrier-backups/cm4-carrier-2026-04-20_232359.zip — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/cm4-carrier-backups/cm4-carrier-2026-05-11_130328.zip — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/cm4-carrier.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/cm4-carrier.kicad_prl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/cm4-carrier.kicad_pro — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/cm4-carrier.kicad_sch — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/CM4-CARRIER-1/cm4-carrier/fp-info-cache — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/COMMS-HAT-1/COMMS-HAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/COMMS-HAT-1/COMMS-HAT-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/TRIHAT-1/TRIHAT-1.kicad_pcb — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/pcb/TRIHAT-1/TRIHAT-1.kicad_sch — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/bevel_gear_housing.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/cockpit_dome_clear.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/dorsal_antenna_fin.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/hull_aft_neck.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/hull_cockpit_cap.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/hull_cockpit_section.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/hull_engine_bell.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/hull_mid_body_left.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/hull_mid_body_right.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/landing_skid_foot.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nacelle_pod_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nacelle_tip_cap_port.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nacelle_tip_cap_stbd.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nozzle_flap_x8.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nozzle_inner_ring_40mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nozzle_inner_ring_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nozzle_outer_housing_40mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/nozzle_outer_housing_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/payload_bay_door.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/pinion_a_bracket.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/sector_gear_22mm.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/files-revF/serenity-drone-revF/stl/tilt_bracket_cf_petg.stl — [PENDING AI CLASSIFICATION]
archives/stale-20260601/overview_side.svg — [PENDING AI CLASSIFICATION]
archives/stale-20260601/pico2-hat.jsx — [PENDING AI CLASSIFICATION]
archives/stl/bevel_gear_housing.stl — [PENDING AI CLASSIFICATION]
archives/stl/cm4_node_mounting_tray.stl — [PENDING AI CLASSIFICATION]
archives/stl/hull_aft_neck.stl — [PENDING AI CLASSIFICATION]
archives/stl/hull_cockpit_cap.stl — [PENDING AI CLASSIFICATION]
archives/stl/hull_cockpit_section.stl — [PENDING AI CLASSIFICATION]
archives/stl/hull_engine_bell.stl — [PENDING AI CLASSIFICATION]
archives/stl/hull_mid_body_left.stl — [PENDING AI CLASSIFICATION]
archives/stl/hull_mid_body_right.stl — [PENDING AI CLASSIFICATION]
archives/stl/landing_skid_foot.stl — [PENDING AI CLASSIFICATION]
archives/stl/nacelle_pod_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nacelle_pod_80mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nacelle_tip_cap_80mm_port.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_flap_x8.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_inner_ring_40mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_inner_ring_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_inner_ring_80mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_outer_housing_40mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_outer_housing_70mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/nozzle_outer_housing_80mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/payload_bay_door.stl — [PENDING AI CLASSIFICATION]
archives/stl/pinion_a_bracket.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_left_shell24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_left_shell24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_left_stator_shell24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_left_stator_shell24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_left_stator_shell24_50mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_left_stator_shell24_revo.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_pistons_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_piv_outer_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_piv_outer_scaled24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_piv_pins_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_piv_pins_scaled24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_right_shell24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_right_shell24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_right_stator_shell24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_right_stator_shell24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_right_stator_shell24_50mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_eng_right_stator_shell24_revo.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_pivot_arm_a_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_pivot_arm_a_scaled24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_pivot_arm_a_scaled24_50mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wing_port_s1223_revo.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wing_stbd_s1223_revo.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wings_both_shell24.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wings_both_shell24_2mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wings_both_shell24_2mm_repaired.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wings_both_shell24_50mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wings_both_shell24_repaired.stl — [PENDING AI CLASSIFICATION]
archives/stl/s_wings_s1223_revo.stl — [PENDING AI CLASSIFICATION]
archives/stl/sector_gear_22mm.stl — [PENDING AI CLASSIFICATION]
archives/stl/sensorhat_mounting_tray.stl — [PENDING AI CLASSIFICATION]
archives/stl/tilt_bracket_cf_petg.stl — [PENDING AI CLASSIFICATION]
archives/tiltrotor-drone.jsx — [PENDING AI CLASSIFICATION]
avionics/AGENTS.md — [PENDING AI CLASSIFICATION]
avionics/TODO.md — [PENDING AI CLASSIFICATION]
avionics/WBS.md — [PENDING AI CLASSIFICATION]
avionics/datasheets/749010012A.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/987651-1223.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/KSZ9477S-Data-Sheet-DS00002392C.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/L-1038e.A5_phyCORE-AM62x_HW Manual.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/MT6701_Datasheet_Rev.1.9.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/PCA9555.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/SAM-M10Q_DataSheet_UBX-22013293.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/SLB_9670VQ20_Infineon.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/SM04B-SRSS-TB.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/SM1553-Series_HiRel-Data-Bus-Pulse-Transformer_RevD.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/SRF2012A.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/Vishay_45273MDSK.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/X2YDatasheet.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/X2Y_15-2237598.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/adin1300.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/adm2795e.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/ak7455-en-datasheet-myakm.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/bsh-bth.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/bst-bmp388-ds001.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/bth-xxx-xx-x-d-xx-footprint.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/ds-000347-icm-42688-p-v1.6.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/ds26lv31qml.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/ds26lv32at.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/eGH.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/iso6442.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/isow1044.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/mspm0g3507.pdf — [PENDING AI CLASSIFICATION]
avionics/emi-hardening/TODO.md — [PENDING AI CLASSIFICATION]
avionics/emi-hardening/WBS.md — [PENDING AI CLASSIFICATION]
avionics/firmware/CMakeLists.txt — [PENDING AI CLASSIFICATION]
avionics/firmware/README.md — [PENDING AI CLASSIFICATION]
avionics/firmware/TODO.md — [PENDING AI CLASSIFICATION]
avionics/firmware/WBS.md — [PENDING AI CLASSIFICATION]
avionics/firmware/cn/CMakeLists.txt — [PENDING AI CLASSIFICATION]
avionics/firmware/cn/src/main.c — [PENDING AI CLASSIFICATION]
avionics/firmware/cn/src/si5351.c — [PENDING AI CLASSIFICATION]
avionics/firmware/cn/src/si5351.h — [PENDING AI CLASSIFICATION]
avionics/firmware/cn/src/xcvr_kiss.c — [PENDING AI CLASSIFICATION]
avionics/firmware/cn/src/xcvr_kiss.h — [PENDING AI CLASSIFICATION]
avionics/firmware/common/CMakeLists.txt — [PENDING AI CLASSIFICATION]
avionics/firmware/common/include/ax25_types.h — [PENDING AI CLASSIFICATION]
avionics/firmware/common/include/failsafe_config.h — [PENDING AI CLASSIFICATION]
avionics/firmware/common/include/kiss_types.h — [PENDING AI CLASSIFICATION]
avionics/firmware/common/include/sbus_input.h — [PENDING AI CLASSIFICATION]
avionics/firmware/common/src/sbus_input.c — [PENDING AI CLASSIFICATION]
avionics/firmware/dts/Makefile — [PENDING AI CLASSIFICATION]
avionics/firmware/dts/README.md — [PENDING AI CLASSIFICATION]
avionics/firmware/dts/cape-a/archive/k3-am6254-pocketbeagle2-serenity-cape-a.dts — [PENDING AI CLASSIFICATION]
avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts — [PENDING AI CLASSIFICATION]
avionics/firmware/dts/cape-b/archive/k3-am6254-pocketbeagle2-serenity-cape-b.dts — [PENDING AI CLASSIFICATION]
avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/CMakeLists.txt — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/bmon_ina2xx.c — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/bmon_ina2xx.h — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/cell_mon_bq769x0.c — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/cell_mon_bq769x0.h — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/governor_config.h — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/mag_mmc5983ma.c — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/mag_mmc5983ma.h — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/mag_qmc5883l.c — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/mag_qmc5883l.h — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/main.c — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/pwr_fault.c — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/src/pwr_fault.h — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/tools/.gitignore — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/tools/governor_cal.py — [PENDING AI CLASSIFICATION]
avionics/firmware/fc/tools/requirements.txt — [PENDING AI CLASSIFICATION]
avionics/jayne/TODO.md — [PENDING AI CLASSIFICATION]
avionics/jayne/WBS.md — [PENDING AI CLASSIFICATION]
avionics/kicad/.gitignore — [PENDING AI CLASSIFICATION]
avionics/kicad/ENC-NACELLE-1.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/ENC-NACELLE-1.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/Emma.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-B_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-B_Mask.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-B_Paste.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-B_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-Edge_Cuts.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-F_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-F_Mask.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-F_Paste.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-F_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-In1_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-In2_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/XCVR-49MHZ-2.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/kicads/Emma.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/kicads/Emma.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/kicads/Emma.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/kicads/Emma.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/scripts/cleanup_emma_drc.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/scripts/gen_emma_sch.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/scripts/mod_emma_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/scripts/route_emma_rssi.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/JAYNE_SOM_NETMAP.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/DS_Camera_9P.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/DS_Laser_2P.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/DS_ToF_4P.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/TQFP-128-1EP_KSZ9477_14x14mm_P0.4mm_EP10x10.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/Wurth_749010012A_10-100BASE-TX.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/phyCORE-AM62x_PCM071_2xBTH-060.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne.pretty/phyCORE-AM62x_PCM071_placement.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Jayne_som_pinmap.csv — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/VERA_NOSE_TRAPEZOID.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Vera.pretty/DS_Camera_9P.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Vera.pretty/DS_Laser_2P.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Vera.pretty/DS_ToF_4P.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Vera.pretty/phyCORE-AM62x_PCM071_2xBTH-060.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/Vera.pretty/phyCORE-AM62x_PCM071_placement.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/gen_vera_bth060_footprint.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/gen_vera_ds_footprints.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/gen_vera_som_pcm071.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/kicads/Jayne.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/kicads/Jayne.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/kicads/Jayne.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/kicads/Jayne.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/kicads/Jayne.net — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/kicads/fp-lib-table — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/mod_vera_corners.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/mod_vera_ds_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/mod_vera_som_place.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/mod_vera_trapezoid.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_bth060_footprint.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_carrier_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_carrier_sch.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_ds_footprints.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_ic_symbols.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_ksz_symbol.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_som_pcm071.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/gen_Jayne_som_symbol.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/mod_Jayne_corners.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/mod_Jayne_ds_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/mod_Jayne_som_place.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Jayne/scripts/mod_Jayne_trapezoid.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/Kaylee.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Adhesive.gba — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Cu.gbl — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Mask.gbs — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Paste.gbp — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Adhesive.gta — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Cu.gtl — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Mask.gts — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Paste.gtp — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-Margin.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/gerbers/Kaylee.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/kicads/Kaylee.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/kicads/Kaylee.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/kicads/Kaylee.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/kicads/Kaylee.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/gen_kaylee.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/gen_kaylee_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/README.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Serenity-Custom.pretty/TI_WL1837MOD.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Serenity-Custom.pretty/uBlox_SAM-M10Q-00B.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/TODO-1.2b-CHECKLIST.md — [PENDING AI CLASSIFICATION]
avionics/kicad/TODO-1.2b-KICAD-READY.md — [PENDING AI CLASSIFICATION]
avionics/kicad/TODO-1.2b-STATUS-REPORT.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/WASH_FOOTPRINT_VERIFICATION.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/Wash.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-B_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-B_Mask.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-B_Paste.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-B_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-Edge_Cuts.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-F_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-F_Mask.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-F_Paste.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-F_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-In1_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-In2_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/gerbers/Wash.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/kicads/Wash.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/kicads/Wash.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/kicads/Wash.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/kicads/Wash.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/kicads/Wash_rebuild.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/kicads/sym-lib-table — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/scripts/gen_wash_sch.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/Zoë.md — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-B_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-B_Mask.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-B_Paste.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-B_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-Edge_Cuts.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-F_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-F_Mask.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-F_Paste.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-F_Silkscreen.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-In1_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-In2_Cu.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/gerbers/Zoë.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/kicads/Zoë.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/kicads/Zoë.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/kicads/Zoë.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/kicads/Zoë.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/ref_remap_2026-07-18.json — [PENDING AI CLASSIFICATION]
avionics/kicad/add_eth_phy.py — [PENDING AI CLASSIFICATION]
avionics/kicad/add_sensors_sbus.py — [PENDING AI CLASSIFICATION]
avionics/kicad/apply_netlist.py — [PENDING AI CLASSIFICATION]
avionics/kicad/check_impedance.py — [PENDING AI CLASSIFICATION]
avionics/kicad/complete_1_2b.py — [PENDING AI CLASSIFICATION]
avionics/kicad/complete_xcvr_49mhz2.py — [PENDING AI CLASSIFICATION]
avionics/kicad/drc_report.txt — [PENDING AI CLASSIFICATION]
avionics/kicad/fix_xcvr_labels.py — [PENDING AI CLASSIFICATION]
avionics/kicad/fp-lib-table — [PENDING AI CLASSIFICATION]
avionics/kicad/generate_gerbers.py — [PENDING AI CLASSIFICATION]
avionics/kicad/generate_gerbers_rev_s1.py — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-B_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-B_Cu.gbl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-B_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-B_Mask.gbs — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-B_Paste.gbp — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-F_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-F_Cu.gtl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-F_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-F_Mask.gts — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-F_Paste.gtp — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-In2_Cu.g2 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-Margin.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/CAPE-B-2-S1/Zoë.drl/Zoë.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-B_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-B_Cu.gbl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-B_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-B_Mask.gbs — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-B_Paste.gbp — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-F_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-F_Cu.gtl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-F_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-F_Mask.gts — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-F_Paste.gtp — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-In2_Cu.g2 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-Margin.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Emma-S1/Emma.drl/Emma.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Adhesive.gba — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Cu.gbl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Mask.gbs — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Paste.gbp — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Adhesive.gta — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Cu.gtl — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Mask.gts — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Paste.gtp — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-Margin.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/gerbers/Kaylee-S1/Kaylee.drl/Kaylee.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/replace_footprints.py — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/ISOW1044BDFMR_pinmap.csv — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Jayne_ISOW1044BDFMR.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Jayne_KSZ9477.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Jayne_MSPM0G3507_RGZ.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Jayne_SLB9670_TPM.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Jayne_SoM.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Jayne_SoM_PCM071.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/KSZ9477STXI_pinmap.csv — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/MSPM0G3507SRGZR_pinmap.csv — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/SLB9670VQ2_0_pinmap.csv — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/Vera_SoM_PCM071.kicad_sym — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/footprints/PHYCORE-AM62AX-DSC-FOOTPRINT.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/symbols/phyCORE_AM62x_PCM071_pinmap.csv — [PENDING AI CLASSIFICATION]
avionics/rev-s1/TODO.md — [PENDING AI CLASSIFICATION]
avionics/rev-s1/WBS.md — [PENDING AI CLASSIFICATION]
current-specification/AGENTS.md — [PENDING AI CLASSIFICATION]
current-specification/LICENSE_AND_ATTRIBUTION.md — [PENDING AI CLASSIFICATION]
current-specification/TODO.md — [PENDING AI CLASSIFICATION]
current-specification/bom_revS.csv — [PENDING AI CLASSIFICATION]
current-specification/serenity-rev-r.jsx — [PENDING AI CLASSIFICATION]
deferred/AGENTS.md — [PENDING AI CLASSIFICATION]
deferred/TODO.md — [PENDING AI CLASSIFICATION]
deferred/WBS.md — [PENDING AI CLASSIFICATION]
deferred/aft-edf/README.md — [PENDING AI CLASSIFICATION]
deferred/aft-edf/openscad/aft_edf_plenum.scad — [PENDING AI CLASSIFICATION]
deferred/aft-edf/openscad/edf_120_motor_mount.scad — [PENDING AI CLASSIFICATION]
deferred/aft-edf/openscad/edf_120_thrust_tube.scad — [PENDING AI CLASSIFICATION]
deferred/aft-edf/openscad/neck_intake_frame.scad — [PENDING AI CLASSIFICATION]
deferred/aft-edf/openscad/rear_neck_intake_shell24.scad — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/aft_edf_plenum.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/edf_120_motor_mount.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/edf_120_thrust_tube.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/neck_intake_frame.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_closed_asm.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_frame.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_0.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_1.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_2.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_3.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_4.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_5.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_6.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_nozzle_petal_hull_7.stl — [PENDING AI CLASSIFICATION]
deferred/aft-edf/stls/rear_shell24_2mm_edf_bored.stl — [PENDING AI CLASSIFICATION]
docs/AGENTS.md — [PENDING AI CLASSIFICATION]
docs/AVIONICS_PB2_REDESIGN.md — [PENDING AI CLASSIFICATION]
docs/BATTERY_MOUNT.md — [PENDING AI CLASSIFICATION]
docs/CARGO_WINCH_SPECIFICATION.md — [ACTIVE, Rev B 2026-07-27] Cargo winch: STS3215 serial-bus
                                    servo, spool supported at both ends on a fixed axle, normally-
                                    engaged one-way safety ratchet, powerless overload line-shed,
                                    single CAN-PERIPH-GW driving both servo and catch. Supersedes
                                    the N20 winch train. Rev A withdrawn (see §-header note).
docs/ETHERNET_PHY_TRADE.md — [PENDING AI CLASSIFICATION]
docs/FIRST_FLIGHT_READINESS.md — [PENDING AI CLASSIFICATION]
docs/JAYNE_LASER_ANALYSIS.md — [PENDING AI CLASSIFICATION]
docs/JAYNE_MANUFACTURING_READINESS.md — [PENDING AI CLASSIFICATION]
docs/LANDING_GEAR_ANALYSIS.md — [PENDING AI CLASSIFICATION]
docs/MANIFEST.json — [PENDING AI CLASSIFICATION]
docs/NOZZLE_DRIVE_TRADE.md — [PENDING AI CLASSIFICATION]
docs/PHASED_BUILD_GUIDE.md — [PENDING AI CLASSIFICATION]
docs/POWER_DISTRIBUTION.md — [PENDING AI CLASSIFICATION]
docs/PROTO_PRINT_DAVINCI_JR.md — [PENDING AI CLASSIFICATION]
docs/PYLON_INTEGRATION_2026-07-18.md — [PENDING AI CLASSIFICATION]
docs/README.md — [PENDING AI CLASSIFICATION]
docs/TILT_SPAR_ANALYSIS.md — [PENDING AI CLASSIFICATION]
docs/TODO.md — [PENDING AI CLASSIFICATION]
docs/TODO_1_1_0_COMPLETION_SUMMARY.md — [PENDING AI CLASSIFICATION]
docs/VERIFY_PLACEMENT_WORKFLOW.md — [PENDING AI CLASSIFICATION]
docs/WBS.md — [PENDING AI CLASSIFICATION]
docs/bom_revP.json — [PENDING AI CLASSIFICATION]
docs/bom_revQ.json — [PENDING AI CLASSIFICATION]
docs/bom_revR.json — [PENDING AI CLASSIFICATION]
docs/electrical_fault_margins.md — [PENDING AI CLASSIFICATION]
docs/failsafe_thresholds.md — [PENDING AI CLASSIFICATION]
docs/flight_envelope.md — [PENDING AI CLASSIFICATION]
docs/img/nozzle_drive_trade.png — [PENDING AI CLASSIFICATION]
docs/img/wing_rev_r1a_sections.png — [PENDING AI CLASSIFICATION]
docs/references/The_Official_Serenity_Blueprints_Reference_Pack.pdf — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/Re: Contact got a new submission - Nick Henning <nickhenning3d@gmail.com> - 2026-07-06 1421.txt — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-close-back-combine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-close-bridge-combine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-close-gear-combine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-final-backside-combine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-final-front-combine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-final-top-combine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-uvdisplay-engine.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-uvdisplay-gear.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/nick-henning-uvdisplay-wing.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/port-bow-full-henning.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/port-bow-upper-bridge-with-wireframe-henning.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/port-bow-view-with-wireframe-henning.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/port-quarter-with-wireframe-henning.jpg — [PENDING AI CLASSIFICATION]
docs/references/nick-henning/top-view-with-wireframe-henning.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/LICENSE.txt — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/README.txt — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_cargo_door.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_cargo_door_strutts.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_cargo_sect.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_eng_left.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_eng_pistons.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_eng_piv_outer.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_eng_piv_pins.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_eng_right.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_feet_x_4.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_head.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_legs.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_middle.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_pivot_arm_a.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_rear.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/files/s_wings_both.stl — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/front-starboard.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_01.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_02.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_03.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_04.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_05.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_06.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_07.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_08.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_09.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_10.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_11.jpg — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_cargo_door.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_cargo_door_strutts.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_cargo_sect.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_eng_left.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_eng_pistons.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_eng_piv_outer.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_eng_piv_pins.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_eng_right.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_feet_x_4.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_head.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_legs.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_middle.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_pivot_arm_a.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_rear.png — [PENDING AI CLASSIFICATION]
docs/references/thingverse-serenity/images/s_wings_both.png — [PENDING AI CLASSIFICATION]
docs/structural_analysis.md — [PENDING AI CLASSIFICATION]
gcs/AGENTS.md — [PENDING AI CLASSIFICATION]
gcs/TODO.md — [PENDING AI CLASSIFICATION]
gcs/WBS.md — [PENDING AI CLASSIFICATION]
gcs/malcolm/README.md — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/CMakeLists.txt — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/dts/k3-am6254-pocketbeagle2-malcolm-cape-b2.dts — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/src/mal_config.h — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/src/mal_gimbal.c — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/src/mal_gimbal.h — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/src/mal_telemetry.c — [PENDING AI CLASSIFICATION]
gcs/malcolm/firmware/pb2i/src/mal_telemetry.h — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/docs/malcolm_antenna_spec.md — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/docs/malcolm_power_budget.md — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/docs/malcolm_wiring.md — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/enclosure/openscad/malcolm_field_enclosure.scad — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/gimbal/openscad/malcolm_gimbal_mount.scad — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/gimbal/openscad/malcolm_gimbal_pan.scad — [PENDING AI CLASSIFICATION]
gcs/malcolm/hardware/gimbal/openscad/malcolm_gimbal_tilt.scad — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/config/malcolm_config.yaml — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/config/mavlink_router.conf — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/install/install_deps.sh — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/install/install_mavlink_router.sh — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/install/install_qgc.sh — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/tracking/requirements.txt — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/tracking/src/gimbal_ctrl.py — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/tracking/src/telemetry_feed.py — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/tracking/src/tracker.py — [PENDING AI CLASSIFICATION]
gcs/malcolm/software/tracking/tests/test_tracker.py — [PENDING AI CLASSIFICATION]
graphical-build-guide/AGENTS.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/REVN_BUILD_GUIDE_24IN.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/TODO-old.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/TODO.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/WBS.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_00_cover.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_01_print_prep.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_02_print_hull.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_03_print_nacelle.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_04_cut_cf.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_05_cf_skeleton.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_06_nacelle_pivot.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_07_edf_install.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_08_nozzle_gear.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_09_avionics.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_10_power_wiring.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_11_inter_board.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_12_security_hw.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_13_nav_lights.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_14_antennas.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_15_software.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_16_calibration.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_17_ground_test.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_18_first_flight.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_19_decal_placement.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_20_node_placement.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_21_node_install.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_22_void_formers.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_23_foam_fill.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_24_access_panels.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_25_obstacle_sensors.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_guide_26_cargo_bay_winch.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/build_plan.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/components_overview.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/decal_sheet.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/flight-phases/TODO.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/flight-phases/WBS.md — [PENDING AI CLASSIFICATION]
graphical-build-guide/gen_hull_outlines.py — [PENDING AI CLASSIFICATION]
graphical-build-guide/hull_bottom.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/hull_front.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/hull_side.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/hull_top.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_bottom.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_front.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_side.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_bottom.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_bow.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_iso_port_bow.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_iso_port_quarter.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_iso_starboard_bow.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_iso_stbd_quarter.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_port.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_starboard.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_stern.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_svgs/serenity_top.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/overview_top.svg — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/01_port.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/02_stbd.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/03_top.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/04_bottom.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/05_bow.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/06_stern.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/07_iso_port_bow_dorsal.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/08_iso_stbd_bow_dorsal.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/09_iso_port_stern_dorsal.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/10_iso_stbd_stern_dorsal.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/11_iso_port_bow_ventral.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/12_iso_stbd_bow_ventral.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/13_iso_port_stern_ventral.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/14_iso_stbd_stern_ventral.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/15_closeup_nose.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/16_closeup_gear.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/pngs/17_closeup_nacelle.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/probe_stl.py — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/cargo_port.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/cargo_stbd.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/cargoax_front.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/cargoax_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/cargoax_stbd.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/cargoax_top.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/fine2_starb.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/fine_starb.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/fine_top.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/grid_starb.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/hd_s_fwdtop.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/hd_sf_hi.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/hd_sf_lo.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/hd_sf_mid.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_front_Yneg_rg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_xsec.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/head_xsec_zoom.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headax_front.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headax_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headax_stbd.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headax_top.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headfin_s_fwdtop.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headfin_sf_hi.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headfin_sf_lo.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headfin_sf_mid.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/headfin_sf_mid_rg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inara_engrave.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_op4_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_op4_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_op4_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_op4_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_op4_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_orig_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_orig_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_orig_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_orig_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_orig_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_vop_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_vop_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_vop_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_vop_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/inner_vop_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/mk_fwdtop.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/mk_stbd.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/port_wall.stl — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rear_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rear_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rear_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rear_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rear_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_op_s_fwdtop.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_op_sf_hi.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_op_sf_lo.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_op_sf_mid.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_orig_s_fwdtop.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_orig_sf_hi.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_orig_sf_lo.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rinner_orig_sf_mid.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rio_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rio_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rio_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rio_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rio_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rop_front_Yneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rop_iso.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rop_port_Xpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rop_stbd_Xneg.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/shellview/rop_top_Zpos.png — [PENDING AI CLASSIFICATION]
graphical-build-guide/update_overview_paths.py — [PENDING AI CLASSIFICATION]
node_modules/.package-lock.json — [PENDING AI CLASSIFICATION]
node_modules/autopreview/Autopreview.js — [PENDING AI CLASSIFICATION]
node_modules/autopreview/components/components.d.ts — [PENDING AI CLASSIFICATION]
node_modules/autopreview/components/list/index.js — [PENDING AI CLASSIFICATION]
node_modules/autopreview/css/index.css — [PENDING AI CLASSIFICATION]
node_modules/autopreview/index.template.js — [PENDING AI CLASSIFICATION]
node_modules/autopreview/package.json — [PENDING AI CLASSIFICATION]
node_modules/autopreview/react.d.ts — [PENDING AI CLASSIFICATION]
node_modules/autopreview/react.js — [PENDING AI CLASSIFICATION]
node_modules/autopreview/react18.d.ts — [PENDING AI CLASSIFICATION]
node_modules/autopreview/react18.js — [PENDING AI CLASSIFICATION]
node_modules/autopreview/vue2.d.ts — [PENDING AI CLASSIFICATION]
node_modules/autopreview/vue2.js — [PENDING AI CLASSIFICATION]
node_modules/autopreview/vue3.d.ts — [PENDING AI CLASSIFICATION]
node_modules/autopreview/vue3.js — [PENDING AI CLASSIFICATION]
tools/AGENTS.md — [PENDING AI CLASSIFICATION]
tools/TODO.md — [PENDING AI CLASSIFICATION]
tools/add_landing_gear_bosses.py — [PENDING AI CLASSIFICATION]
tools/bake_hull_frame.py — [PENDING AI CLASSIFICATION]
tools/build_head_shell.py — [PENDING AI CLASSIFICATION]
tools/build_landing_gear_views.py — [PENDING AI CLASSIFICATION]
tools/precommit_index.py — [PENDING AI CLASSIFICATION]
tools/precommit_kicad_load.py — [PENDING AI CLASSIFICATION]
tools/precommit_sanitize.py — [PENDING AI CLASSIFICATION]
tools/validate_kicad.py — [PENDING AI CLASSIFICATION]
tools/validate_stls.py — [PENDING AI CLASSIFICATION]
tools/verify_bow_pod.py — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-21) ---
airframe/stls/fuselage/landing-gear/lg_r6_1_5in_hull_legs.stl — Rev R6 default (1.5in/38.1mm clearance) landing gear, 4 corners, hull frame; active in serenity_assembly.py
airframe/stls/fuselage/landing-gear/lg_r6_1_5in_hull_stance.stl — same + ground plane + cargo-belly ghost (review view)
airframe/stls/fuselage/landing-gear/lg_r6_1_5in_leg_assembled.stl — one corner: bay + 1.5in leg + 4 wires, nominal stance
airframe/stls/fuselage/landing-gear/lg_r6_1_5in_leg_deformed.stl — same corner at full 30.9deg flexion, fired ductile wires
airframe/stls/fuselage/landing-gear/lg_r6_1_5in_leg_frame.stl — one-piece 1.5in leg frame (CF-PETG), print orientation
airframe/stls/fuselage/landing-gear/lg_r6_3_0in_hull_legs.stl — Rev R6 extended (3.0in/80mm clearance) landing gear variant, 4 corners, hull frame; kept, not wired into default assembly
airframe/stls/fuselage/landing-gear/lg_r6_3_0in_hull_stance.stl — same + ground plane + cargo-belly ghost (review view)
airframe/stls/fuselage/landing-gear/lg_r6_3_0in_leg_assembled.stl — one corner: bay + 3.0in leg + 4 wires, nominal stance
airframe/stls/fuselage/landing-gear/lg_r6_3_0in_leg_deformed.stl — same corner at full 30.9deg flexion, fired ductile wires
airframe/stls/fuselage/landing-gear/lg_r6_3_0in_leg_frame.stl — one-piece 3.0in leg frame (CF-PETG), print orientation
airframe/stls/fuselage/landing-gear/lg_r6_common_bay.stl — hull-flank bay plate; bit-identical between leg-length variants
airframe/stls/fuselage/landing-gear/lg_r6_common_ductile_wire_deformed.stl — fired ductile bowed wire (~19.2mm bow), field-inspection reference; shared
airframe/stls/fuselage/landing-gear/lg_r6_common_ductile_wire_nominal.stl — nominal ductile bowed wire; shared
airframe/stls/fuselage/landing-gear/lg_r6_common_foot.stl — canonical tri-pad TPU foot; shared
airframe/stls/fuselage/landing-gear/lg_r6_common_spring_wire_deformed.stl — spring wire at elastic-limit bow; shared
airframe/stls/fuselage/landing-gear/lg_r6_common_spring_wire_nominal.stl — nominal spring bowed wire; shared
archives/airframe-archives/archive/stls/fuselage/landing-gear/ductile_wire_deformed.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/ductile_wire_nominal.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/feet_x_4_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/foot_1_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/foot_2_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/foot_3_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/foot_4_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/landing_gear_assembled.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/landing_gear_deformed.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/landing_gear_exploded.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/leg_1_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/leg_2_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/leg_3_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/leg_4_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/legs_scaled24.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/post.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/spring_wire_deformed.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/spring_wire_nominal.stl — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/stls/fuselage/landing-gear/strong-leg.stl — [PENDING AI CLASSIFICATION]
avionics/kicad/ENC-NACELLE-1.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/ENC-NACELLE-1.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/ENC-NACELLE-1.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/ENC-NACELLE-1.net — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/fix_kaylee_pin_snap.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/fix_kaylee_revs1_cleanup.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/fix_kaylee_yinv.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/gen_kaylee_revs1.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/mod_kaylee_pcb_revs1.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Serenity-Custom.pretty/MountingHole_2.2mm_M2_SelfTap_Compact.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Serenity-Custom.pretty/Pigtail_7W_DirectSolder.kicad_mod — [PENDING AI CLASSIFICATION]
avionics/kicad/Wash/scripts/mod_wash_pcb_reconcile.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Zoë/kicads/_autosave-Zoë.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/gen_enc_nacelle_pcb.py — [PENDING AI CLASSIFICATION]
tools/landing_gear_r6_sizing.py — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-22) ---
.githooks/pre-commit — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-22) ---

## --- AUTO-DISCOVERED (2026-07-23) ---
.github/workflows/ci.yml — [PENDING AI CLASSIFICATION]
airframe/openscad/fuselage/canonical_leg_r6_1_5in.scad — Rev R6 canonical articulated hip-pivot leg, 1.5in (38.1mm) belly-clearance variant (default)
airframe/openscad/fuselage/canonical_leg_r6_3_0in.scad — Rev R6 canonical articulated hip-pivot leg, 3.0in (80mm) belly-clearance variant (extended, kept)

## --- AUTO-DISCOVERED (2026-07-26) ---
.github/workflows/stale-branches.yml — [PENDING AI CLASSIFICATION]
archives/airframe-archives/archive/openscad/fuselage/canonical_leg_r6.scad — [PENDING AI CLASSIFICATION]
avionics/datasheets/6391731564544371956530548.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/FOCSineESCCANCommunicationProtocolV30.pdf — [PENDING AI CLASSIFICATION]
avionics/datasheets/isow1412.pdf — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/CAN-PERIPH-GW-1.md — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.dsn — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_pcb — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_prl — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_pro — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.kicad_sch — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.net — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1.ses — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/kicads/CAN-PERIPH-GW-1_v2.ses — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/scripts/gen_can_periph_gw_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/scripts/gen_can_periph_gw_sch.py — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/scripts/route_can_periph_gw_pcb.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/scripts/inject_emma_tpm.py — [PENDING AI CLASSIFICATION]
avionics/kicad/Kaylee/scripts/inject_kaylee_trust_module.py — [PENDING AI CLASSIFICATION]
avionics/kicad/fix_wash_zoe_isolators.py — [PENDING AI CLASSIFICATION]
docs/references/108090023_STS3215-C001_Datasheet.pdf — [PENDING AI CLASSIFICATION]
docs/references/Bus_servo_control_circuit.pdf — [PENDING AI CLASSIFICATION]
docs/references/ST3215 memory register map-EN.xls — [PENDING AI CLASSIFICATION]
docs/references/ST3215-2D.zip — [PENDING AI CLASSIFICATION]
docs/references/ST3215-3D.zip — [PENDING AI CLASSIFICATION]
docs/references/Servo_Driver_with_ESP32_3D.zip — [PENDING AI CLASSIFICATION]
docs/references/scservo.zip.zip — [PENDING AI CLASSIFICATION]
docs/references/vimdrones_can_periph_pico_v1.0.stl — [PENDING AI CLASSIFICATION]
docs/references/vimdrones_esc_s50_v1.0.step — [PENDING AI CLASSIFICATION]
docs/references/vimdrones_esc_s50_v1.0.stl — [PENDING AI CLASSIFICATION]
docs/references/vimdrones_esc_s50_wiring.png — [PENDING AI CLASSIFICATION]
tools/export-specctra-dsn.py — [PENDING AI CLASSIFICATION]
tools/import-specctra-ses.py — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-26) ---
avionics/kicad/4_Run KiCad ERC_DRC validator (changed files only).txt — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Adhesive.gba — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Cu.gbl — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Mask.gbs — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Paste.gbp — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Adhesive.gta — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Cu.gtl — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Mask.gts — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Paste.gtp — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-Margin.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/CAN-PERIPH-GW-1/gerbers/CAN-PERIPH-GW-1.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/fix_starved_thermal_pads.py — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-26) ---
avionics/kicad/Emma/gerbers/Emma-B_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-B_Cu.gbl — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-B_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-B_Mask.gbs — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-B_Paste.gbp — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-B_Silkscreen.gbo — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-Edge_Cuts.gm1 — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-F_Courtyard.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-F_Cu.gtl — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-F_Fab.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-F_Mask.gts — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-F_Paste.gtp — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-F_Silkscreen.gto — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-In1_Cu.g1 — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-In2_Cu.g2 — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-Margin.gbr — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-in1-back.drl — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma-job.gbrjob — [PENDING AI CLASSIFICATION]
avionics/kicad/Emma/gerbers/Emma.drl — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-27) ---
tools/open_mating_faces.py — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-27) ---
avionics/kicad/Jayne/kicads/Jayne.kicad_dru — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-07-27) ---
avionics/kicad/Jayne/kicads/_autosave-Jayne.kicad_pcb — [PENDING AI CLASSIFICATION]

## --- AUTO-DISCOVERED (2026-08-09) ---
current-specification/bom_revS.json — [PENDING AI CLASSIFICATION]
current-specification/serenity-rev-s.jsx — [PENDING AI CLASSIFICATION]
docs/DOCUMENTATION_RECONCILIATION_2026-07-28.md — [PENDING AI CLASSIFICATION]
tools/compact_bom_entries.py — [PENDING AI CLASSIFICATION]
tools/landing_gear_bay_pad_fit.py — [PENDING AI CLASSIFICATION]
tools/__pycache__/landing_gear_bay_pad_fit.cpython-313.pyc — [IGNORED/VCS-EXCLUDED]
