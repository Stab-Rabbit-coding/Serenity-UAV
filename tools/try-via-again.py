#!/usr/bin/env python3
# -------------------------------------------------
# KiCad 9 (kicad-cli) – perimeter stitching via generator
# -------------------------------------------------
import sys
import math
import pcbnew

# -------------------- USER SETTINGS --------------------
SPACING_MM = 2.5               # distance between consecutive stitching vias
VIA_DIAMETER_MM = 0.6               # overall via pad diameter
VIA_DRILL_MM = 0.3               # drill size (adjust to fab house)
NET_NAME = "GND"             # net to which the vias belong
# -----------------------------------------------------

if len(sys.argv) < 2:
    print("Usage: kicad-cli pcbnew run-script stitch_vias.py <board_file>")
    sys.exit(1)

board_path = sys.argv[1]

# -----------------------------------------------------------------
# 1️⃣ Load the board
# -----------------------------------------------------------------
board = pcbnew.LoadBoard(board_path)

# -----------------------------------------------------------------
# 2️⃣ Get the board outline (Edge‑Cuts)
# -----------------------------------------------------------------
# In KiCad 9 the board outline is returned as a list of VECTOR2I points.
outline_pts = board.GetBoardOutline()          # type: list[pcbnew.VECTOR2I]

if not outline_pts or len(outline_pts) < 2:
    raise RuntimeError("Board outline not found – make sure you have an Edge‑Cuts layer.")

# Ensure the polygon is closed (first point == last point)
if outline_pts[0] != outline_pts[-1]:
    outline_pts.append(outline_pts[0])


# -----------------------------------------------------------------
# 3️⃣ Helper: mm → internal KiCad units (nanometers)
# -----------------------------------------------------------------
def mm_to_nm(v: float) -> int:
    return int(v * pcbnew.IU_PER_MM)


# -----------------------------------------------------------------
# 4️⃣ Get (or create) the net for the stitching vias
# -----------------------------------------------------------------
net = board.FindNet(NET_NAME)
if net is None:
    net = pcbnew.NETINFO_ITEM(board, NET_NAME)
    board.Add(net)


# -----------------------------------------------------------------
# 5️⃣ Function that actually places a via at a VECTOR2I position
# -----------------------------------------------------------------
def place_via(pos: pcbnew.VECTOR2I):
    via = pcbnew.VIA(board)
    via.SetPosition(pos)

    via.SetWidth(mm_to_nm(VIA_DIAMETER_MM))   # pad diameter
    via.SetDrill(mm_to_nm(VIA_DRILL_MM))     # drill size
    via.SetNet(net)

    board.Add(via)


# -----------------------------------------------------------------
# 6️⃣ Walk the outline and drop a via every SPACING_MM
# -----------------------------------------------------------------
acc_dist_mm = 0.0                     # distance already travelled on the current edge
prev_pt = outline_pts[0]

for pt in outline_pts[1:]:
    # Edge vector in nanometers
    dx_nm = pt.x - prev_pt.x
    dy_nm = pt.y - prev_pt.y
    edge_len_nm = math.hypot(dx_nm, dy_nm)
    edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM

    # Place as many vias as fit on this segment
    while acc_dist_mm + edge_len_mm >= SPACING_MM:
        # Remaining distance to the next via
        remain_mm = SPACING_MM - acc_dist_mm
        t = remain_mm / edge_len_mm                     # interpolation factor 0‑1

        # Interpolated position (still nanometers)
        new_x = int(prev_pt.x + t * dx_nm)
        new_y = int(prev_pt.y + t * dy_nm)
        place_via(pcbnew.VECTOR2I(new_x, new_y))

        # Advance the “previous point” to the newly placed via
        prev_pt = pcbnew.VECTOR2I(new_x, new_y)

        # Re‑compute the remainder of the current edge
        dx_nm = pt.x - prev_pt.x
        dy_nm = pt.y - prev_pt.y
        edge_len_nm = math.hypot(dx_nm, dy_nm)
        edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM
        acc_dist_mm = 0.0                               # we just placed a via

    # No more vias on this segment – keep the leftover distance
    acc_dist_mm += edge_len_mm
    prev_pt = pt

# -----------------------------------------------------------------
# 7️⃣ Save the modified board (overwrites the original file)
# -----------------------------------------------------------------
pcbnew.SaveBoard(board_path, board)

print(f"Stitching vias placed every {SPACING_MM} mm on '{board_path}'.")
