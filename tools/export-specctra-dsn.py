#!/usr/bin/env python3
import sys
import pcbnew


def export_dsn(pcb_path, dsn_path):
    board = pcbnew.LoadBoard(pcb_path)
    # Real API name (verified against this pcbnew build): ExportSpecctraDSN,
    # not ExportSpecctraFile. Counterpart for reading a routed session back
    # in is pcbnew.ImportSpecctraSES(board, ses_path).
    success = pcbnew.ExportSpecctraDSN(board, dsn_path)
    if not success:
        sys.exit('Export failed')
    print(f'Exported {dsn_path}')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Usage: kicad_export_dsn.py <board.kicad_pcb> <out.dsn>')
    export_dsn(sys.argv[1], sys.argv[2])
