# ARCHIVE_INDEX.md — Serenity UAV

<!-- Auto-maintained: updated whenever files move into archive. -->
<!-- Active file tree described in PROJECT_INDEX.md. -->
<!-- Last updated: 2026-07-13 — corrected avionics/kicad/archive/ and avionics/gerbers/archive/
     paths to their new archives/avionics-archives/ consolidated location; documented
     archives/ root loose-file snapshots and the (empty) airframe-archives/ staging dir -->

---

## airframe/archive/FreeCAD-scripts/

Deprecated FreeCAD prototype assembly scripts.  All predate the Rev R1 hull-frame
bake; their placement/transform values would double-transform the baked hull-frame
STLs and MUST NOT be applied.  The canonical assembly script is
`airframe/FreeCAD-scripts/serenity_assembly.py`.

```text
Archived 2026-06-29 (Rev R — superseded by serenity_assembly.py):
  assembly1.py                      — Earliest prototype (pre-R1 transforms)
  Serenity-Assemble.py              — Subsystem stub (Assembly4Lib placeholders)
  Serenity-Subsystem-Assembly.py    — Subsystem stub (Assembly4Lib placeholders)
  serenity_subsystem_assembler.py   — Subsystem assembler class (stub)
  serenity_fuselage_asm4.py         — Fuselage Assembly4 sub-assembly script
                                       (was airframe/freecad/assembly/)
```

---

## archives/avionics-archives/kicad-archives/ (moved from avionics/kicad/archive/)

Superseded KiCad PCB designs. **Path corrected 2026-07-13:** this content used to live at
`avionics/kicad/archive/` (that path no longer exists on disk); it has been consolidated
under `archives/avionics-archives/kicad-archives/`. Design notes in `archive/ARCHIVE-REVQ.md`
inside this directory.

```text
archive/ARCHIVE-REVQ.md             — Archival log with revision history and reason codes

Archived 2026-06-10 (renamed to Wash / Zoë within Rev Q):
  archive/CAPE-A-2.kicad_{pcb,sch,pro,prl} — EMI-hardened FC cape (superseded by Wash.*)
  archive/CAPE-A-2.md                — CAPE-A-2 design notes

  archive/CAPE-B-2.kicad_{pcb,sch,pro,prl} — EMI-hardened CN cape (superseded by Zoë.*)
  archive/CAPE-B-2.md                — CAPE-B-2 design notes

Archived 2026-06-05 (Rev Q baseline — superseded by -2 EMI-hardened variants):
  archive/CAPE-A-1.kicad_{pcb,sch,pro,prl}  — Standard FC cape (pre-EMI-hardening)
  archive/CAPE-B-1.kicad_{pcb,sch,pro,prl}  — Standard CN cape (pre-EMI-hardening)
  archive/CAPE-B-1a.kicad_{pcb,prl,pro}     — CAPE-B-1 predecessor
  archive/XCVR-49MHZ-1.kicad_{pcb,sch,pro,prl} — Standard 49 MHz XCVR
  archive/XCVR-49MHZ-1.md            — XCVR-49MHZ-1 design notes
  archive/PWR-DIST-1.kicad_sch        — Early power distribution schematic (pre-Kaylee)
  archive/PWR-DIST-1.md               — PWR-DIST-1 design notes
  archive/gen_cape_a2.py, gen_cape_a2_pcb.py, gen_cape_b2.py, gen_cape_b2_pcb.py — generator
                                       scripts archived alongside their boards

Pre-Rev Q (superseded by Cape-A/B architecture at Rev K):
  archive/CAPE-A-1-no-comment.kicad_{pcb,sch} — Intermediate CAPE-A-1 without comments
  archive/CM3-CARRIER-1.kicad_{pcb,sch}      — Raspberry Pi CM3 carrier
  archive/CM4-CARRIER-1.kicad_{pcb,sch}      — Raspberry Pi CM4 carrier v1
  archive/CM4-CARRIER-2.kicad_{pcb,sch}      — Raspberry Pi CM4 carrier v2
  archive/COMMS-HAT-1.kicad_{pcb,sch}        — CM4 comms HAT
  archive/COMMS-HAT-SWITCH.kicad_{pcb,sch}   — CM4 comms HAT with antenna switch
  archive/SENSORHAT-1.kicad_{pcb,sch}        — CM4 sensor HAT
  archive/TRIHAT-1.kicad_{pcb,sch}           — Pico2 triple HAT

CAPE-A-1-backups/, CAPE-B-1-backups/ — KiCad autosave zip backups for the archived Cape-A-1/
                                       Cape-B-1 boards (16 + 5 zips respectively)
```

---

## airframe/archive/

Superseded Blender scripts and STL files. Active scripts are in `airframe/blender-scripts/`.
Design notes in `ARCHIVE-REVQ.md` inside this directory (distinct from the KiCad archive's
own `ARCHIVE-REVQ.md`).

```text
ARCHIVE-REVQ.md                      — Airframe design archival log, Rev Q (2026-06-05):
                                        revision history and reason codes for archived
                                        airframe geometry/scripts
edf_bore_sleeve.scad                 — DEPRECATED nacelle EDF bore sleeve (superseded by
                                        edf_stator_sleeve.scad + edf_aft_spider_sleeve.scad)

blender-scripts/
  blender_nacelle_integrated_v1.py   — Nacelle integrated v1 (bore-center bug)
  blender_nacelle_integrated_v2.py   — Nacelle integrated v2 (fixed; superseded by
                                        check_nacelle_alignment.py workflow)
  blender_shells_v3_2mm.py           — Shell hollowing v3 2 mm variant (pre-Rev Q)
  blender_shells_v3_50mm.py          — Shell hollowing v3 50 mm variant (pre-Rev Q)
  generate_hollow_shells.py          — Early hollowing script (pre-Rev N)
  generate_shells_v2.py              — Shell generation v2 (pre-Rev N)

stls/fuselage/                       — Pre-Rev Q fuselage STLs (18" scale and earlier 24"
                                        iterations): hull_engine_bell.stl,
                                        s_cargo_door_scaled24.stl,
                                        s_cargo_door_strutts_scaled24.stl,
                                        s_cargo_sect_shell24.stl, s_cargo_sect_shell24_2mm.stl,
                                        s_cargo_sect_shell24_repaired.stl,
                                        s_cargo_sect_shell24_revs.stl,
                                        s_feet_x_4_scaled24_repaired.stl,
                                        s_head_shell24_2mm.stl, s_head_shell24_2mm_repaired.stl,
                                        s_head_shell24_repaired.stl,
                                        s_middle_intake_shell24.stl, s_middle_shell24.stl,
                                        s_middle_shell24_2mm.stl,
                                        s_middle_shell24_2mm_repaired.stl, s_rear_shell24.stl,
                                        s_rear_shell24_2mm.stl,
                                        s_rear_shell24_2mm_repaired.stl,
                                        s_rear_shell24_repaired.stl
stls/fuselage/landing-gear/          — Archived 2026-07-12 (TODO.md §1.1.4.6):
                                        landing_legs_hull_r1.stl — pre-R1.4 single-leg
                                        render, orphaned by the Rev R1.4 corner V-brace
                                        redesign (itself since superseded by the Rev R5
                                        vertical-post + wire-brace design,
                                        wire_brace_leg.scad); had no surviving SCAD
                                        source. Reference removed from
                                        serenity_render_views.py.
stls/nacelles/                       — Pre-Rev Q nacelle STLs (pre-tandem-EDF design):
                                        edf_bore_sleeve.stl, nacelle_port_revt.stl,
                                        nacelle_stbd_revt.stl, sector_gear_22mm_fixed.obj,
                                        sector_gear_22mm_fixed.stl, stator_50mm.stl
                                      Archived 2026-06-22 (legacy part, no longer needed):
                                        nacelle_tip_cap_port.stl, nacelle_tip_cap_stbd.stl
                                        — no SCAD source ever existed; placement code removed
                                        from serenity_assembly.py (was a best-guess VERIFY
                                        placeholder; see TODO.md §1.1.3 history)
  nozzles/                            — nacelle_nozzle_closed_asm_repaired.stl,
                                        nacelle_nozzle_petal_repaired.stl,
                                        rear_nozzle_petal_repaired.stl,
                                        nacelle_nozzle_petal.stl (Rev R1 flat blender petal,
                                        superseded 2026-07-04 by the Rev R2 tangential-hinge
                                        conical flap nacelle_nozzle_flap.stl; TODO §1.1.3.1)
                                      Archived 2026-07-18 (Rev T, Option B pushrod drive —
                                        docs/NOZZLE_DRIVE_TRADE.md; the entire tilt-to-nozzle
                                        GEAR train is deleted, replaced by the spar-crank
                                        pushrod nacelle_nozzle_pushrod.scad):
                                        stls/nacelles/   nacelle_pinion_a.stl,
                                          nacelle_drive_pinion.stl, nacelle_sector_gear.stl
                                        stls/nacelles/nozzles/  nacelle_bevel_housing.stl,
                                          nacelle_bevel_pair.stl

openscad/nacelles/                   — Archived 2026-07-18 (Rev T, Option B pushrod drive):
                                        nacelle_sector_gear.scad, nacelle_pinion.scad
                                        (Pinion A + Nozzle Drive Pinion variants),
                                        nacelle_bevel_pair.scad, nacelle_bevel_housing.scad,
                                        and the earlier nacelle_nozzle_idler.scad — the
                                        tilt-to-nozzle gear train, superseded by the pushrod/
                                        cam-only-ring drive (nacelle_nozzle_pushrod.scad +
                                        Rev T unison_ring() in nacelle_nozzle_iris.scad).
```

---

## avionics/firmware/dts/cape-a/archive/ and cape-b/archive/

Superseded device-tree sources, pre-Rev-R1 -a2/-b2 cape naming. Active device trees are
`avionics/firmware/dts/cape-a/k3-am6254-pocketbeagle2-serenity-cape-a2.dts` and
`avionics/firmware/dts/cape-b/k3-am6254-pocketbeagle2-serenity-cape-b2.dts`.

```text
cape-a/archive/
  k3-am6254-pocketbeagle2-serenity-cape-a.dts   — Pre-R1 Wash device tree (superseded by -cape-a2.dts)

cape-b/archive/
  k3-am6254-pocketbeagle2-serenity-cape-b.dts   — Pre-R1 Zoë device tree (superseded by -cape-b2.dts)
```

---

## archives/avionics-archives/gerber-archive/ (moved from avionics/gerbers/archive/)

Pre-Rev Q gerber snapshots for boards superseded by the Cape-A-2/Cape-B-2/XCVR-49MHZ-2 (-2
EMI-hardened) designs. **Path corrected 2026-07-13:** `avionics/gerbers/` no longer exists on
disk at all; this content is consolidated under `archives/avionics-archives/gerber-archive/`.
There is no longer a duplicate ARCHIVED-named gerber set at `avionics/kicad/gerbers/` either —
that directory is now empty (see PROJECT_INDEX.md avionics/kicad/ section).

```text
CAPE-A-1/    — 17 gerber/drill files: B_Cu, B_Mask, B_Paste, B_Silkscreen, Edge_Cuts, F_Cu,
               F_Mask, F_Paste, F_Silkscreen, In1_Cu, In2_Cu, NPTH-drl_map, NPTH.drl,
               PTH-drl_map, PTH.drl, job.gbrjob, .net (plus a nested CAPE-A-1/ subfolder
               duplicating the *_Cu/_Mask/_Paste/_Silkscreen/Edge_Cuts/job/.drl set)
CAPE-B-1/    — 17 gerber/drill files: same set as CAPE-A-1/ (same nested-subfolder duplication)
XCVR-49MHZ-1/ — 14 gerber/drill files: B_Cu, B_Mask, B_Paste, B_Silkscreen, Edge_Cuts, F_Cu,
               F_Mask, F_Paste, F_Silkscreen, In1_Cu, In2_Cu, drl_map.pdf, job.gtl, .drl
```

---

## archives/ (repository root)

Whole-project snapshots and superseded subsystems.

```text
18in-scale-scad/                     — OpenSCAD sources at 18" scale (SCALE_18=2.1974×)
                                       Superseded by 24" scale at Rev N.
  s_cargo_door_scaled18.scad/.stl
  s_cargo_door_strutts_scaled18.scad/.stl
  s_cargo_sect_shell18.scad/.stl
  s_eng_left_shell18.scad/.stl       — (and remaining 18" sections/parts)

20260422-Serenity-RevF/              — Full project snapshot at Rev F (2026-04-22)
  serenity-drone/                    — Rev F source tree snapshot
20260422-Serenity-RevF.zip           — Zip archive of same

20260429/                            — Snapshot at 2026-04-29
  serenity-drone/                    — Intermediate source tree
20260429_files.zip                   — Zip archive of a 2026-04-29 snapshot

stale-20260601/                      — Stale files culled on 2026-06-01
  airframe-stls/                     — STL snapshots prior to Rev Q mesh repairs
  files-revF/                        — Rev F file fragments

stl/                                 — Miscellaneous one-off STL exports (pre-Rev N)

thingverse-serenity/                 — Thingiverse Thing:4677565 reference model
  files/                             — Source STLs (18" scale hull sections)
  images/                            — Reference images

serenity/                            — Early web/UI experiment (Node.js prototype)
  src/, public/, node_modules/       — Superseded by current Python/FreeCAD pipeline

chat/                                — Session transcript exports (reference only)

docs-superseded/                     — Documentation superseded by current docs/

avionics-archives/                   — NEW (2026-07-13): consolidates avionics KiCad/gerber
                                       archives previously scattered under avionics/kicad/archive/
                                       and avionics/gerbers/archive/ (both paths now gone from
                                       disk) — see the two sections above this one.
  gerber-archive/                    — (see "archives/avionics-archives/gerber-archive/" above)
  kicad-archives/                    — (see "archives/avionics-archives/kicad-archives/" above)

airframe-archives/                   — NEW (2026-07-13), currently EMPTY: an equivalent
                                       consolidation staging directory for airframe/archive/
                                       content has been created but the move has not happened
                                       yet — airframe/archive/ itself is still the live location
                                       (see "airframe/archive/" section below).

Loose files directly at archives/ root (not yet organized into a subfolder — historical
revision snapshots, superseded before this index existed):
  serenity-rev-b.jsx, serenity-rev-c.jsx, serenity-rev-d.jsx, serenity-rev-e.jsx,
  serenity-rev-f.jsx, serenity-rev-f-.jsx, serenity-rev-o.jsx, serenity-rev-p.jsx,
  serenity-rev-q.jsx, serenity-connectivity-revH.jsx, serenity-esc-telem-revH1.jsx,
  serenity-drone.jsx, nacelle-nozzle-gear.jsx, tiltrotor-drone.jsx — historical interactive-spec
  .jsx snapshots (see current-specification/ for the active serenity-rev-r.jsx)
  bom_revH1.json, bom_revP.csv, bom_revQ.csv, bom_revR.csv — historical BOM snapshots
  build_guide_00_cover.svg, build_guide_20_node_placement.svg — early build-guide card drafts
  generate_foam_svgs.py                — early foam-void SVG generator (pre-current pipeline)
  nacelles.jst                        — 1-byte stub file
  sensorhat_mounting_tray.stl          — SENSORHAT-1 (archived cape) mounting tray
  files.zip, more-files.zip, serenity-drone-rev-g.zip, serenity-drone-COMPLETE-revH1.zip,
  "Serenity Firefly with landing gear and swivel engines - 7330462.zip",
  "Serenity0Firefly0with0landing0gear0and0swivel0engines0-07330462.zip",
  "serenity firefly transport ship - 2601098.zip" — whole-tree zip snapshots at various dates
```
