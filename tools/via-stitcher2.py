# -------------------------------------------------
# KiCad 9 – perimeter stitching via generator (IPC API)
# -------------------------------------------------
import pcbnew
import math

# -------------------- USER SETTINGS --------------------
spacing_mm = 2.5               # spacing between vias
via_diameter_mm = 0.6               # overall via pad diameter
via_drill_mm = 0.3               # drill size (adjust to your fab house)
net_name = "GND"             # net name for the stitching vias
# -----------------------------------------------------


# Helper to convert mm → internal KiCad units (nanometers)
def mm_to_nm(v: float) -> int:
    return int(v * pcbnew.IU_PER_MM)


# -----------------------------------------------------------------
# 1️⃣ Get the current board and its outline (Edge‑Cuts)
# -----------------------------------------------------------------
board = pcbnew.GetBoard()                 # active board in PCBNew
outline = board.GetBoardOutline()          # returns a list of VECTOR2I points

if not outline or len(outline) < 2:
    raise RuntimeError("Board outline not found – make sure you have an Edge‑Cuts layer.")

# Ensure the polygon is closed (last point equals first)
if outline[0] != outline[-1]:
    outline.append(outline[0])

# -----------------------------------------------------------------
# 2️⃣ Create (or fetch) the net that will own the stitching vias
# -----------------------------------------------------------------
net = board.FindNet(net_name)
if net is None:
    net = pcbnew.NETINFO_ITEM(board, net_name)
    board.Add(net)


# -----------------------------------------------------------------
# 3️⃣ Function that actually places a via at a VECTOR2I position
# -----------------------------------------------------------------
def place_via(pos: pcbnew.VECTOR2I):
    via = pcbnew.VIA(board)
    via.SetPosition(pos)

    via.SetWidth(mm_to_nm(via_diameter_mm))          # pad diameter
    via.SetDrill(mm_to_nm(via_drill_mm))            # drill size
    via.SetNet(net)

    board.Add(via)


# -----------------------------------------------------------------
# 4️⃣ Walk the outline and drop a via every *spacing_mm*
# -----------------------------------------------------------------
acc_dist_mm = 0.0               # distance accumulated on the current edge
prev_pt = outline[0]

for pt in outline[1:]:
    # Vector of the current edge (nanometers)
    dx_nm = pt.x - prev_pt.x
    dy_nm = pt.y - prev_pt.y
    edge_len_nm = math.hypot(dx_nm, dy_nm)
    edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM

    while acc_dist_mm + edge_len_mm >= spacing_mm:
        # How far from *prev_pt* we need to step to hit the next via
        remain_mm = spacing_mm - acc_dist_mm
        t = remain_mm / edge_len_mm                     # interpolation factor 0‑1

        # Interpolated position (still in nanometers)
        new_x = int(prev_pt.x + t * dx_nm)
        new_y = int(prev_pt.y + t * dy_nm)
        place_via(pcbnew.VECTOR2I(new_x, new_y))

        # Move the “previous point” forward to the new via location
        prev_pt = pcbnew.VECTOR2I(new_x, new_y)

        # Re‑compute the remaining vector of the current edge
        dx_nm = pt.x - prev_pt.x
        dy_nm = pt.y - prev_pt.y
        edge_len_nm = math.hypot(dx_nm, dy_nm)
        edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM
        acc_dist_mm = 0.0                               # we just placed a via

    # No more vias on this segment – keep the leftover distance
    acc_dist_mm += edge_len_mm
    prev_pt = pt

# -------------------------------------------------
# Refresh the view so you can see the new vias
pcbnew.Refresh()
# -------------------------------------------------
