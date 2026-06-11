# ARCHIVE_INDEX.md — Serenity UAV

<!-- Auto-maintained: updated whenever files move into archive. -->
<!-- Active file tree described in PROJECT_INDEX.md. -->
<!-- Last updated: Rev R (2026-06-10) -->

---

## avionics/kicad/archive/

Superseded KiCad PCB designs. Design notes in `ARCHIVE-REVQ.md` inside this directory.

```text
ARCHIVE-REVQ.md                     — Archival log with revision history and reason codes

Archived 2026-06-10 (renamed to Wash / Zoë within Rev Q):
  CAPE-A-2.kicad_{pcb,sch,pro,prl}  — EMI-hardened FC cape (superseded by Wash.*)
  CAPE-A-2.md                        — CAPE-A-2 design notes

  CAPE-B-2.kicad_{pcb,sch,pro,prl}  — EMI-hardened CN cape (superseded by Zoë.*)
  CAPE-B-2.md                        — CAPE-B-2 design notes

Archived 2026-06-05 (Rev Q baseline — superseded by -2 EMI-hardened variants):
  CAPE-A-1.kicad_{pcb,sch,pro,prl}  — Standard FC cape (pre-EMI-hardening)
  CAPE-B-1.kicad_{pcb,sch,pro,prl}  — Standard CN cape (pre-EMI-hardening)
  CAPE-B-1a.kicad_{pcb,prl,pro}     — CAPE-B-1 predecessor
  XCVR-49MHZ-1.kicad_{pcb,sch,pro,prl} — Standard 49 MHz XCVR
  XCVR-49MHZ-1.md                   — XCVR-49MHZ-1 design notes
  PWR-DIST-1.kicad_sch               — Early power distribution schematic (pre-Kaylee)
  PWR-DIST-1.md                      — PWR-DIST-1 design notes

Pre-Rev Q (superseded by Cape-A/B architecture at Rev K):
  CAPE-A-1-no-comment.kicad_{pcb,sch} — Intermediate CAPE-A-1 without comments
  CM3-CARRIER-1.kicad_{pcb,sch}      — Raspberry Pi CM3 carrier
  CM4-CARRIER-1.kicad_{pcb,sch}      — Raspberry Pi CM4 carrier v1
  CM4-CARRIER-2.kicad_{pcb,sch}      — Raspberry Pi CM4 carrier v2
  COMMS-HAT-1.kicad_{pcb,sch}        — CM4 comms HAT
  COMMS-HAT-SWITCH.kicad_{pcb,sch}   — CM4 comms HAT with antenna switch
  SENSORHAT-1.kicad_{pcb,sch}        — CM4 sensor HAT
  TRIHAT-1.kicad_{pcb,sch}           — Pico2 triple HAT
```

---

## airframe/archive/

Superseded Blender scripts and STL files. Active scripts are in `airframe/blender-scripts/`.

```text
blender-scripts/
  blender_nacelle_integrated_v1.py   — Nacelle integrated v1 (bore-center bug)
  blender_nacelle_integrated_v2.py   — Nacelle integrated v2 (fixed; superseded by
                                        check_nacelle_alignment.py workflow)
  blender_shells_v3_2mm.py           — Shell hollowing v3 2 mm variant (pre-Rev Q)
  blender_shells_v3_50mm.py          — Shell hollowing v3 50 mm variant (pre-Rev Q)
  generate_hollow_shells.py          — Early hollowing script (pre-Rev N)
  generate_shells_v2.py              — Shell generation v2 (pre-Rev N)

stls/fuselage/                       — Pre-Rev Q fuselage STLs (18" scale and
                                        earlier 24" iterations)
stls/nacelles/                       — Pre-Rev Q nacelle STLs (pre-tandem-EDF design)
```

---

## archives/ (repo root)

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
```
