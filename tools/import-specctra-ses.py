#!/usr/bin/env python3
"""Companion to export-specctra-dsn.py: import a freerouting-produced
Specctra .ses session (routed tracks/vias) back into a .kicad_pcb, in place.
Footprint positions are untouched -- only routing (tracks/vias) is applied.

Usage: python3 import-specctra-ses.py <board.kicad_pcb> <routed.ses>
"""
import sys
import pcbnew


def import_ses(pcb_path, ses_path):
    board = pcbnew.LoadBoard(pcb_path)
    success = pcbnew.ImportSpecctraSES(board, ses_path)
    if not success:
        sys.exit("Import failed")
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(pcb_path, board)
    print(f"Imported {ses_path} into {pcb_path} (zones re-filled)")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: import-specctra-ses.py <board.kicad_pcb> <routed.ses>")
    import_ses(sys.argv[1], sys.argv[2])
