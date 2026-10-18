#!/usr/bin/env python3
# stitch_vias.py – place stitching vias every 2.5 mm around the board edge
# -------------------------------------------------
import sys
import math
import pcbnew

# ---------- USER SETTINGS ----------
SPACING_MM = 2.5               # distance between consecutive vias
VIA_PAD_MM = 0.6               # total via pad diameter
VIA_DRILL_MM = 0.3               # drill size
NET_NAME = "GND"             # net to which the vias belong
# -----------------------------------

if len(sys.argv) != 2:
    print("Usage: stitch_vias.py <board_file.kicad_pcb>")
    sys.exit(1)

board_path = sys.argv[1]

# Load the board (the IPC API will start a head‑less server automatically)
board = pcbnew.LoadBoard(board_path)
if board is None:
    raise RuntimeError("Failed to load board")

# -----------------------------------------------------------------
# 1️⃣  Get the closed Edge‑Cuts outline (list of VECTOR2I points)
# -----------------------------------------------------------------
outline = board.GetBoardOutline()
if not outline:
    raise RuntimeError("No Edge‑Cuts outline found")

# Ensure the polyline is closed
if outline[0] != outline[-1]:
    outline.append(outline[0])


# -----------------------------------------------------------------
# 2️⃣  Helper: mm → KiCad internal units (nanometres)
# -----------------------------------------------------------------
def mm_to_nm(v: float) -> int:
    return int(v * pcbnew.IU_PER_MM)


# -----------------------------------------------------------------
# 3️⃣  Get (or create) the net that will own the stitching vias
# -----------------------------------------------------------------
net = board.FindNet(NET_NAME)
if net is None:
    net = pcbnew.NETINFO_ITEM(board, NET_NAME)
    board.Add(net)


# -----------------------------------------------------------------
# 4️⃣  Function that actually creates a via at a given position
# -----------------------------------------------------------------
def place_via(pos: pcbnew.VECTOR2I):
    via = pcbnew.VIA(board)
    via.SetPosition(pos)
    via.SetWidth(mm_to_nm(VIA_PAD_MM))      # pad diameter
    via.SetDrill(mm_to_nm(VIA_DRILL_MM))    # drill size
    via.SetNet(net)
    board.Add(via)


# -----------------------------------------------------------------
# 5️⃣  Walk the outline and drop a via every SPACING_MM
# -----------------------------------------------------------------
acc_mm = 0.0                     # distance already travelled on current edge
prev = outline[0]

for pt in outline[1:]:
    # Edge vector (nanometres)
    dx = pt.x - prev.x
    dy = pt.y - prev.y
    edge_len_nm = math.hypot(dx, dy)
    edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM

    while acc_mm + edge_len_mm >= SPACING_MM:
        # Distance from prev to the next via
        remain_mm = SPACING_MM - acc_mm
        t = remain_mm / edge_len_mm                     # interpolation factor (0‑1)

        # Interpolated point (still nanometres)
        new_x = int(prev.x + t * dx)
        new_y = int(prev.y + t * dy)
        place_via(pcbnew.VECTOR2I(new_x, new_y))

        # Advance prev to the new via location
        prev = pcbnew.VECTOR2I(new_x, new_y)

        # Re‑compute the remaining part of the current edge
        dx = pt.x - prev.x
        dy = pt.y - prev.y
        edge_len_nm = math.hypot(dx, dy)
        edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM
        acc_mm = 0.0

    # No more vias on this segment – keep leftover distance
    acc_mm += edge_len_mm
    prev = pt

# -----------------------------------------------------------------
# 6️⃣  Save the modified board (overwrites original file)
# -----------------------------------------------------------------
pcbnew.SaveBoard(board_path, board)
print(f"Stitching vias placed every {SPACING_MM} mm in '{board_path}'.")
