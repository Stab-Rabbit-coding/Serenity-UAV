# -------------------------------------------------
# KiCad 9 – perimeter stitching via generator
# -------------------------------------------------
import pcbnew
import math

# ---- user‑adjustable parameters ---------------------------------
spacing_mm      = 2.5               # distance between consecutive vias
via_diameter_mm = 0.6               # via drill + pad size (adjust to your design)
net_name        = "GND"             # net to which the stitching vias belong
# ------------------------------------------------------------------

board = pcbnew.GetBoard()
edge = board.GetBoardEdges()          # returns a list of EDGE_SEGMENTS (the board outline)

# Helper: convert millimeters to internal KiCad units (nanometers)
def mm_to_nm(value):
    return int(value * pcbnew.IU_PER_MM)

# ------------------------------------------------------------------
# 1. Build a list of points that follow the whole board perimeter
#    (including corners).  The points are in board‑local coordinates.
perimeter = []
for edge_seg in edge:
    # each EDGE_SEGMENT is a line; add its start point
    start = edge_seg.GetStart()
    perimeter.append(pcbnew.VECTOR2I(start))

# close the loop by adding the first point again
if perimeter:
    perimeter.append(perimeter[0])

# ------------------------------------------------------------------
# 2. Walk along the perimeter and place a via every *spacing_mm*
# ------------------------------------------------------------------
def place_via_at(pos):
    via = pcbnew.VIA(board)
    via.SetPosition(pos)

    # set drill and pad size (KiCad stores them in nanometers)
    via.SetDrill(mm_to_nm(via_diameter_mm * 0.4))          # typical drill ≈ 40 % of pad
    via.SetWidth(mm_to_nm(via_diameter_mm))

    # assign the net (create it if it does not exist)
    net = board.FindNet(net_name)
    if not net:
        net = pcbnew.NETINFO_ITEM(board, net_name)
        board.Add(net)
    via.SetNet(net)

    board.Add(via)

# walk the polyline
if len(perimeter) < 2:
    raise RuntimeError("Board outline not found.")

dist_acc = 0.0                 # accumulated distance along current edge
last_pt  = perimeter[0]

for pt in perimeter[1:]:
    # vector for this edge
    dx = pt.x - last_pt.x
    dy = pt.y - last_pt.y
    edge_len_nm = math.hypot(dx, dy)
    edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM

    while dist_acc + edge_len_mm >= spacing_mm:
        # distance from last_pt to the next via position
        remain_mm = spacing_mm - dist_acc
        t = remain_mm / edge_len_mm            # interpolation factor (0‑1)

        # interpolate position in nanometers
        new_x = int(last_pt.x + t * dx)
        new_y = int(last_pt.y + t * dy)
        place_via_at(pcbnew.VECTOR2I(new_x, new_y))

        # move forward along the edge
        last_pt = pcbnew.VECTOR2I(new_x, new_y)
        dx = pt.x - last_pt.x
        dy = pt.y - last_pt.y
        edge_len_nm = math.hypot(dx, dy)
        edge_len_mm = edge_len_nm / pcbnew.IU_PER_MM
        dist_acc = 0.0

    # no more vias on this segment – keep the leftover distance
    dist_acc += edge_len_mm
    last_pt = pt

# -------------------------------------------------
# Refresh view (optional)
pcbnew.Refresh()
# -------------------------------------------------
