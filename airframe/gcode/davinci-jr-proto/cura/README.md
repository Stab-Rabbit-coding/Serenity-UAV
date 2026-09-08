# Rev T Cura Slice Output — da Vinci Jr. microSD

**Author:** Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
**License:** CC BY 4.0 — creativecommons.org/licenses/by/4.0
**Date:** 2026-09-07

Companion to `docs/PROTO_PRINT_DAVINCI_JR.md` §5 batches and to the sibling
PrusaSlicer pipeline in `../davinci_jr_pla.ini` / `../slice_all_batches.sh`.
This directory holds the **Cura**-produced equivalent, generated headlessly
with `cura-engine` (apt package, `/usr/bin/CuraEngine`, v5.0.0) rather than
the Cura GUI, using `slice_all_batches_cura.py` in this directory.

## Why Cura output lives separately from the PrusaSlicer batches

Both toolchains target the same physical machine — XYZprinting da Vinci Jr.
1.0 w, 150×150×150 mm, 0.4 mm nozzle, running **Repetier firmware** (a
community replacement for the stock XYZ firmware; this is what lets the
printer read plain `.gcode` off a microSD card at all — see `../davinci_jr_pla.ini`
header comment). The start/end G-code in `slice_all_batches_cura.py` is
copied verbatim from `../davinci_jr_pla.ini` so a print behaves identically
regardless of which slicer produced the file.

## How to use the microSD card

1. Format a microSD card **FAT32**.
2. Copy the contents of `sdcard/` onto the card, preserving the `batch_X/`
   subfolders (or flatten it — Repetier firmware browses folders fine, but
   flattening is a reasonable fallback if your printer's LCD menu is
   older/simpler and struggles with subfolders).
3. On the printer, browse to the file and print directly from SD — no
   XYZware / WiFi / `.3w` conversion needed on Repetier firmware.
4. **Apply glue stick to the bed before every plate** — this printer has no
   heated bed (`machine_heated_bed=False`, `material_bed_temperature=0` in
   every sliced file); adhesion is 100% mechanical/glue-stick.
5. Each `.gcode` file is a single part. There is no multi-plate batching in
   this Cura pipeline (unlike the old XYZware "batch" concept) — load and
   print files one at a time, or manually queue several on a print run.

## What's in `sdcard/`

**All 49 parts** from `docs/PROTO_PRINT_DAVINCI_JR.md` §5, organized into
`batch_A/` … `batch_N/` matching that guide's batch lettering — 294 MB
total. See the guide for print orientation, verification checklist, and
per-batch settings — this directory only holds the sliced output.

**One caveat — see the mesh-integrity note in
`docs/PROTO_PRINT_DAVINCI_JR.md` §10:**

- `cargo_vera_faraday.stl` (Batch D) **is** in `sdcard/`, but the source STL
  has its lid body floating ~9 mm above the base with no support underneath —
  reposition the lid in slicer before printing, or expect a failed bridge
  print. See §10.2.

`rear_shell24_2mm_repaired.stl` (Batch N) needed a mesh repair before it
would slice (it's the largest of the six overlapping-faces-affected meshes
by face count and didn't finish within 400s as exported) — see §10.5 and
`mesh_repair.py` in this directory. The driver applies that repair
automatically; nothing further to do for this file.

## Regenerating

```bash
cd airframe/gcode/davinci-jr-proto/cura
python3 slice_all_batches_cura.py              # all 49 parts (rear shell ~5.5 min via mesh_repair.py)
python3 slice_all_batches_cura.py --skip-heavy # skip the 6 slow hull-shell/nacelle-pod parts
python3 slice_all_batches_cura.py --only wing  # just one part by substring
```

Output is gitignored (`../.gitignore` covers `*.gcode` recursively) — this
README and the driver script are the only committed files in this directory.
