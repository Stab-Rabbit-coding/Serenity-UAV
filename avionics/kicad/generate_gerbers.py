#!/usr/bin/env python3
"""
generate_gerbers.py
Regenerate production Gerber and drill files for Cape-A-1, Cape-B-1, and
XCVR-49MHZ-1 from their .kicad_pcb source files using the KiCad pcbnew API.

Run headlessly (no display required):
    python3 generate_gerbers.py

Outputs to serenity/kicad/gerbers/<BOARD>/

Author:  Steve Griffing, PE(CSE), CISSP-ISSEP, CPP
License: CC BY 4.0 — creativecommons.org/licenses/by/4.0
Date:    2026-05-31
"""

import os
import sys
import pcbnew

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

BOARDS = [
    {
        "pcb":  os.path.join(SCRIPT_DIR, "CAPE-A-1.kicad_pcb"),
        "name": "CAPE-A-1",
        "out":  os.path.join(SCRIPT_DIR, "gerbers", "CAPE-A-1"),
    },
    {
        "pcb":  os.path.join(SCRIPT_DIR, "CAPE-B-1.kicad_pcb"),
        "name": "CAPE-B-1",
        "out":  os.path.join(SCRIPT_DIR, "gerbers", "CAPE-B-1"),
    },
    {
        "pcb":  os.path.join(SCRIPT_DIR, "XCVR-49MHZ-1.kicad_pcb"),
        "name": "XCVR-49MHZ-1",
        "out":  os.path.join(SCRIPT_DIR, "gerbers", "XCVR-49MHZ-1"),
    },
]

# Layers to export (4-layer board — F.Cu, In1.Cu GND, In2.Cu +3V3/PWR, B.Cu)
GERBER_LAYERS = [
    pcbnew.F_Cu,
    pcbnew.In1_Cu,
    pcbnew.In2_Cu,
    pcbnew.B_Cu,
    pcbnew.F_Mask,
    pcbnew.B_Mask,
    pcbnew.F_Paste,
    pcbnew.B_Paste,
    pcbnew.F_SilkS,
    pcbnew.B_SilkS,
    pcbnew.Edge_Cuts,
]


def export_gerbers(board_path, out_dir, board_name):
    """Export Gerber files from a .kicad_pcb file."""
    print(f"\n=== {board_name}: loading {board_path}")
    if not os.path.exists(board_path):
        print(f"  ERROR: PCB file not found: {board_path}")
        return False

    board = pcbnew.LoadBoard(board_path)
    if board is None:
        print(f"  ERROR: Failed to load board {board_path}")
        return False

    os.makedirs(out_dir, exist_ok=True)

    ctl = pcbnew.PLOT_CONTROLLER(board)
    opt = ctl.GetPlotOptions()

    # Match JLCPCB standard gerber settings
    opt.SetOutputDirectory(out_dir)
    opt.SetPlotFrameRef(False)
    opt.SetSketchPadLineWidth(pcbnew.FromMM(0.1))
    opt.SetAutoScale(False)
    opt.SetScale(1)
    opt.SetMirror(False)
    opt.SetUseGerberAttributes(True)        # X2 format
    opt.SetUseGerberProtelExtensions(True)
    opt.SetGerberPrecision(6)
    opt.SetSubtractMaskFromSilk(True)
    opt.SetPlotReference(True)
    opt.SetPlotValue(True)

    # Plot each copper/mask/silk/paste/outline layer
    for layer_id in GERBER_LAYERS:
        if not board.IsLayerEnabled(layer_id):
            continue
        ctl.SetLayer(layer_id)
        ctl.OpenPlotfile(
            pcbnew.LayerName(layer_id),
            pcbnew.PLOT_FORMAT_GERBER,
            pcbnew.LayerName(layer_id),
        )
        ctl.PlotLayer()
        ctl.ClosePlot()
        lname = pcbnew.LayerName(layer_id)
        print(f"  Gerber: {lname}")

    # Write Gerber job file
    ctl.SetLayer(pcbnew.F_Cu)
    ctl.OpenPlotfile(
        "job",
        pcbnew.PLOT_FORMAT_GERBER,
        "job",
    )
    ctl.ClosePlot()

    print(f"  Gerbers written to {out_dir}/")

    # Export drill files
    drill = pcbnew.EXCELLON_WRITER(board)
    drill.SetOptions(
        False,              # aMirror
        True,               # aMinimalHeader
        pcbnew.VECTOR2I(0, 0),  # aOffset
        True,               # aMergePTHandNPTH
    )
    drill.SetFormat(True)   # True = metric
    drill.CreateDrillandMapFilesSet(out_dir, True, True)
    print(f"  Drill files written to {out_dir}/")

    return True


def main():
    """Generate gerbers for all boards listed in BOARDS."""
    ok = 0
    fail = 0
    for cfg in BOARDS:
        if not os.path.exists(cfg["pcb"]):
            print(f"SKIP {cfg['name']}: PCB file not found")
            continue
        success = export_gerbers(cfg["pcb"], cfg["out"], cfg["name"])
        if success:
            ok += 1
        else:
            fail += 1

    print(f"\nDone. {ok} succeeded, {fail} failed.")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
