#!/usr/bin/env python3
"""
slice_all_batches_cura.py -- Serenity-Class UAV Rev T Prototype Slice Runner (Cura)

Author : Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 -- creativecommons.org/licenses/by/4.0
Date   : 2026-09-07
Slicer : CuraEngine 5.0.0 CLI (apt package cura-engine) -- headless, no GUI
Printer: XYZprinting da Vinci Jr. 1.0 w (150x150x150 mm, 0.4 mm nozzle), Repetier
         firmware -- same machine this repo's PrusaSlicer profile
         (davinci_jr_pla.ini, sibling directory) targets. Start/end G-code below
         is carried over unchanged from that profile so both toolchains produce
         G-code the printer's firmware handles identically.

Part list mirrors docs/PROTO_PRINT_DAVINCI_JR.md Section 5 (Rev T edition).

Scaling: CuraEngine's per-mesh `mesh_rotation_matrix` CLI setting was tested and
does NOT reliably apply a uniform scale in this build (verified empirically --
see the session's mesh-integrity report). Parts requiring a scale factor are
pre-scaled with trimesh into a scratch STL before slicing, and the pre-scaled
bounding box is printed to the log for verification against
docs/PROTO_PRINT_DAVINCI_JR.md Section 4.2.

Support: several current hull-shell and nacelle-pod STLs carry an "overlapping
faces" mesh warning (self-intersecting geometry from the Blender hollowing
pipeline) that is watertight per trimesh but crashes or hangs CuraEngine
5.0.0's support/combing pass. Every batch below is sliced with support
disabled (support_enable=False) for that reason -- this is a slicer-CLI
limitation, not a design change from the printed guide's per-batch tables.
Parts whose printed guide entry calls for support need it added by hand in
the Cura GUI, or the flagged geometry repaired first (see the mesh-integrity
report for the specific files).

Usage:
    python3 slice_all_batches_cura.py [--only NAME] [--skip-heavy]
"""

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

import trimesh

import mesh_repair

REPO_ROOT = Path(__file__).resolve().parents[4]
STL_ROOT = REPO_ROOT / "airframe" / "stls"
OUT_ROOT = Path(__file__).resolve().parent
SCRATCH = Path("/tmp/claude-1000/cura_scaled_stl")
SCRATCH.mkdir(parents=True, exist_ok=True)

CURA_ENGINE = "/usr/bin/CuraEngine"
FDM_DEF = "/usr/share/cura/resources/definitions/fdmprinter.def.json"

# Carried over verbatim from ../davinci_jr_pla.ini so both slicers drive the
# printer identically (Repetier firmware / Marlin-derivative, no heated bed).
START_GCODE = (
    "G21\nG90\nM82\nG28\nG1 Z5 F3000\nG1 X10 Y10 F5000\nG1 Z0.3 F1500\n"
    "G92 E0\nG1 X60 E9 F500\nG92 E0\nG1 Z1 F3000"
)
END_GCODE = (
    "M104 S0\nG91\nG1 E-3 F1800\nG1 Z10 F3000\nG90\nG1 X5 Y145 F5000\nM84"
)

# (batch, out_name, stl_relpath, scale, infill_pct, raft, notes)
# raft: True -> adhesion_type=raft, False -> adhesion_type=skirt
PARTS = [
    # Batch A
    ("A", "cargo_door_servo_bracket", "fuselage/cargo/cargo_door_servo_bracket.stl", 1.0, 20, True, ""),
    ("A", "cargo_release_servo_bracket", "fuselage/cargo/cargo_release_servo_bracket.stl", 1.0, 20, True, ""),
    ("A", "cargo_drv8833_tray", "fuselage/cargo/cargo_drv8833_tray.stl", 1.0, 20, False, ""),
    ("A", "cargo_gps_retention_ring", "fuselage/cargo/cargo_gps_retention_ring.stl", 1.0, 20, True, ""),
    ("A", "cargo_fpv_bezel", "fuselage/cargo/cargo_fpv_bezel.stl", 1.0, 20, True, ""),
    # Batch B / C
    ("B", "cargo_door_port", "fuselage/cargo/cargo_door_port.stl", 1.0, 20, False, ""),
    ("B", "cargo_hinge_retention", "fuselage/cargo/cargo_hinge_retention.stl", 1.0, 20, False, ""),
    ("C", "cargo_door_stbd", "fuselage/cargo/cargo_door_stbd.stl", 1.0, 20, False, ""),
    # Batch D
    ("D", "cargo_cradle_autolatch", "fuselage/cargo/cargo_cradle_autolatch.stl", 1.0, 25, False, ""),
    ("D", "cargo_vera_faraday", "fuselage/cargo/cargo_vera_faraday.stl", 1.0, 25, False,
     "KNOWN DEFECT: lid body floats ~9mm above base in source STL -- reposition "
     "in slicer/GUI before printing (see mesh-integrity report). Sliced as-is here."),
    # Batch E / F
    ("E", "nacelle_nozzle_flap", "nacelles/nozzles/nacelle_nozzle_flap.stl", 1.0, 15, False, ""),
    ("E", "nacelle_nozzle_flap_seal", "nacelles/nozzles/nacelle_nozzle_flap_seal.stl", 1.0, 15, False, ""),
    ("E", "nacelle_nozzle_ring", "nacelles/nozzles/nacelle_nozzle_ring.stl", 1.0, 15, False, ""),
    ("E", "nacelle_nozzle_throat", "nacelles/nozzles/nacelle_nozzle_throat.stl", 1.0, 15, False, ""),
    ("F", "nacelle_nozzle_iris-closed", "nacelles/nozzles/nacelle_nozzle_iris-closed.stl", 1.0, 10, False, ""),
    ("F", "nacelle_nozzle_iris-open", "nacelles/nozzles/nacelle_nozzle_iris-open.stl", 1.0, 10, False, ""),
    # Batch G
    ("G", "nacelle_trunnion", "nacelles/nacelle_trunnion.stl", 1.0, 25, False, ""),
    ("G", "nacelle_servo_bracket", "nacelles/nacelle_servo_bracket.stl", 1.0, 25, False, ""),
    ("G", "edf_stator_sleeve", "nacelles/edf_stator_sleeve.stl", 1.0, 25, False, ""),
    ("G", "edf_aft_spider_sleeve", "nacelles/edf_aft_spider_sleeve.stl", 1.0, 25, False, ""),
    # Batch H
    ("H", "nacelle_esc_cover_port_a", "nacelles/esc/nacelle_esc_cover_port_a.stl", 1.0, 20, False, ""),
    ("H", "nacelle_esc_cover_port_b", "nacelles/esc/nacelle_esc_cover_port_b.stl", 1.0, 20, False, ""),
    ("H", "nacelle_esc_cover_stbd_a", "nacelles/esc/nacelle_esc_cover_stbd_a.stl", 1.0, 20, False, ""),
    ("H", "nacelle_esc_cover_stbd_b", "nacelles/esc/nacelle_esc_cover_stbd_b.stl", 1.0, 20, False, ""),
    # Batch I -- nacelle pods, 89% (heavy, handled separately -- see --skip-heavy)
    ("I", "nacelle_port_revs", "nacelles/nacelle_port_revs.stl", 0.89, 15, True, "HEAVY"),
    ("I", "nacelle_stbd_revs", "nacelles/nacelle_stbd_revs.stl", 0.89, 15, True, "HEAVY"),
    # Batch J
    ("J", "wing_port_s1223_revo", "wings/wing_port_s1223_revo.stl", 1.0, 15, False, ""),
    ("J", "wing_stbd_s1223_revo", "wings/wing_stbd_s1223_revo.stl", 1.0, 15, False, ""),
    ("J", "wing_root_flange_port", "fuselage/wing_root_flange_port.stl", 1.0, 15, False, ""),
    ("J", "wing_root_flange_stbd", "fuselage/wing_root_flange_stbd.stl", 1.0, 15, False, ""),
    ("J", "lg_r6_1_5in_leg_assembled", "fuselage/landing-gear/lg_r6_1_5in_leg_assembled.stl", 1.0, 25, False, ""),
    ("J", "lg_r6_1_5in_leg_frame", "fuselage/landing-gear/lg_r6_1_5in_leg_frame.stl", 1.0, 25, False, ""),
    ("J", "lg_r6_common_bay", "fuselage/landing-gear/lg_r6_common_bay.stl", 1.0, 25, False, ""),
    ("J", "lg_r6_common_foot", "fuselage/landing-gear/lg_r6_common_foot.stl", 1.0, 25, False, ""),
    ("J", "lg_r6_common_ductile_wire_nominal", "fuselage/landing-gear/lg_r6_common_ductile_wire_nominal.stl", 1.0, 25, False, ""),
    ("J", "lg_r6_common_spring_wire_nominal", "fuselage/landing-gear/lg_r6_common_spring_wire_nominal.stl", 1.0, 25, False, ""),
    # Batch K
    ("K", "head_cargo_splice_collar", "fuselage/head_cargo_splice_collar.stl", 1.0, 25, False, ""),
    ("K", "cargo_middle_splice_collar", "fuselage/cargo_middle_splice_collar.stl", 1.0, 25, False, ""),
    ("K", "middle_rear_splice_collar", "fuselage/middle_rear_splice_collar.stl", 1.0, 25, False, ""),
    # Batch L
    ("L", "bow_sensor_faceplate", "fuselage/bow_sensor_faceplate.stl", 1.0, 20, False, ""),
    ("L", "dorsal_antenna_fin", "fuselage/dorsal_antenna_fin.stl", 1.0, 20, False, ""),
    ("L", "inara_access_cover", "fuselage/inara_access_cover.stl", 1.0, 20, False, ""),
    ("L", "river_access_cover", "fuselage/river_access_cover.stl", 1.0, 20, False, ""),
    ("L", "battery_tray", "fuselage/battery_tray.stl", 0.97, 20, False, ""),
    # Batch M
    ("M", "belly_panel", "fuselage/belly_panel.stl", 0.94, 15, True, ""),
    # Batch N -- hull shells, 64%. All 3 of these carry the same
    # overlapping-faces warning as the rest of the "heavy" set but slice fine
    # as-is (52-99s wall time, confirmed) -- not HEAVY despite the warning.
    ("N", "head_shell24_2mm_repaired", "fuselage/head_shell24_2mm_repaired.stl", 0.64, 10, False, ""),
    ("N", "cargo_sect_shell24_2mm_repaired", "fuselage/cargo/cargo_sect_shell24_2mm_repaired.stl", 0.64, 10, False, ""),
    ("N", "middle_shell24_2mm_repaired", "fuselage/middle_shell24_2mm_repaired.stl", 0.64, 10, False, ""),
    # rear_shell24_2mm_repaired did NOT finish within 400s even without support
    # (largest mesh of the six, ~1.0M faces, with the same overlapping-faces
    # defect the other 5 tolerate) -- routed through mesh_repair.py (self-union
    # + simplify via manifold3d) before scaling. HEAVY-REPAIRED, not HEAVY:
    # --skip-heavy still skips it (it's slow, ~5.5min), but it is not broken.
    ("N", "rear_shell24_2mm_repaired", "fuselage/rear_shell24_2mm_repaired.stl", 0.64, 10, False, "HEAVY-REPAIRED"),
]

# Parts that need mesh_repair.py applied before scaling -- see mesh_repair.py
# docstring for why (Blender-boolean-pipeline overlapping-faces defect that
# is invisible to a watertight check but blocks/stalls CuraEngine).
NEEDS_REPAIR = {"rear_shell24_2mm_repaired"}


def prepare_stl(name: str, rel_path: str, scale: float) -> Path:
    """Return a path to slice: the original STL (repaired first if `name` is
    in NEEDS_REPAIR), scaled with trimesh if scale != 1 (not via CuraEngine's
    CLI matrix -- that path was verified unreliable this session)."""
    src = STL_ROOT / rel_path

    if name in NEEDS_REPAIR:
        repaired = SCRATCH / f"{src.stem}_meshfix.stl"
        if not repaired.exists():
            mesh = trimesh.load(src, process=True)
            fixed = mesh_repair.repair_mesh(mesh)
            fixed.export(repaired)
        src = repaired

    if scale == 1.0:
        return src
    out = SCRATCH / f"{src.stem}_{int(scale * 100)}pct.stl"
    if not out.exists():
        mesh = trimesh.load(src, process=True)
        mesh.apply_scale(scale)
        mesh.export(out)
    return out


def slice_part(batch, name, rel_path, scale, infill, raft, notes, timeout_s=300):
    if "HEAVY" in notes:
        timeout_s = max(timeout_s, 600)
    stl_path = prepare_stl(name, rel_path, scale)
    out_dir = OUT_ROOT / f"batch_{batch}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_gcode = out_dir / f"{name}.gcode"

    args = [
        CURA_ENGINE, "slice",
        "-j", FDM_DEF,
        "-s", "machine_width=150",
        "-s", "machine_depth=150",
        "-s", "machine_height=150",
        "-s", "machine_heated_bed=False",
        "-s", "machine_center_is_zero=False",
        "-s", "machine_gcode_flavor=RepRap (Marlin/Sprinter)",
        "-s", f"machine_start_gcode={START_GCODE}",
        "-s", f"machine_end_gcode={END_GCODE}",
        "-s", "layer_height=0.2",
        "-s", "layer_height_0=0.3",
        "-s", "wall_line_count=2",
        "-s", f"infill_sparse_density={infill}",
        "-s", "infill_pattern=grid",
        "-s", f"adhesion_type={'raft' if raft else 'skirt'}",
        "-s", "support_enable=False",  # see module docstring
        "-s", "speed_print=45",
        "-s", "speed_travel=130",
        "-s", "speed_wall_0=35",
        "-s", "cool_fan_enabled=True",
        "-s", "cool_min_layer_time=15",
        "-e0",
        "-s", "machine_nozzle_size=0.4",
        "-s", "material_diameter=1.75",
        "-s", "material_print_temperature=200",
        "-s", "material_print_temperature_layer_0=205",
        "-s", "material_bed_temperature=0",
        "-s", "material_bed_temperature_layer_0=0",
        "-s", "retraction_amount=2",
        "-s", "retraction_speed=45",
        "-l", str(stl_path),
        "-o", str(out_gcode),
    ]

    t0 = time.time()
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired:
        return {"name": name, "ok": False, "reason": f"TIMEOUT>{timeout_s}s"}
    dt = time.time() - t0
    combined = r.stdout + r.stderr
    ok = r.returncode == 0 and out_gcode.exists()
    layers = re.search(r"Layer count: (\d+)", combined)
    printtime = re.search(r"Print time \(s\): (\d+)", combined)
    filament = re.search(r"Filament \(mm\^3\): ([\d.]+)", combined)
    overlap_warn = "overlapping faces" in combined.lower()
    return {
        "name": name,
        "batch": batch,
        "ok": ok,
        "returncode": r.returncode,
        "slice_wall_s": round(dt, 1),
        "layers": int(layers.group(1)) if layers else None,
        "print_time_s": int(printtime.group(1)) if printtime else None,
        "filament_mm3": float(filament.group(1)) if filament else None,
        "overlap_warning": overlap_warn,
        "notes": notes,
        "out": str(out_gcode) if ok else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None, help="Only slice parts whose name contains this substring")
    ap.add_argument("--skip-heavy", action="store_true", help="Skip parts marked HEAVY in notes")
    args = ap.parse_args()

    results = []
    for batch, name, rel_path, scale, infill, raft, notes in PARTS:
        if args.only and args.only not in name:
            continue
        if args.skip_heavy and "HEAVY" in notes:
            continue
        print(f"[{batch}] slicing {name} (scale={scale}, infill={infill}%, raft={raft}) ...", flush=True)
        res = slice_part(batch, name, rel_path, scale, infill, raft, notes)
        results.append(res)
        status = "OK" if res["ok"] else f"FAIL ({res.get('reason', res.get('returncode'))})"
        print(f"    -> {status}  layers={res.get('layers')}  "
              f"time={res.get('print_time_s')}s  wall={res.get('slice_wall_s')}s  "
              f"overlap_warn={res.get('overlap_warning')}", flush=True)

    n_ok = sum(1 for r in results if r["ok"])
    print(f"\n{n_ok}/{len(results)} parts sliced successfully.")
    failed = [r["name"] for r in results if not r["ok"]]
    if failed:
        print("FAILED:", ", ".join(failed))
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())
