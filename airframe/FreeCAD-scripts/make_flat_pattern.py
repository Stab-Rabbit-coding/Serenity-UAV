"""Generate a 2-D flat pattern (DXF) for the avionics shield-box sheet-metal.

Lays out a simple sheet-metal box as flat panels (base + 4 sides + separate
lid) with mounting-hole, SMA, M12 and circular-bulkhead markers for CAM.
Run headless under FreeCAD: ``freecadcmd make_flat_pattern.py``.
"""

import FreeCAD
import Draft
import ImportGui
from FreeCAD import Base

doc = FreeCAD.newDocument("FlatPattern")

# Box parameters (all dimensions in millimetres).
L = 80.0            # box length (X)
W = 60.0            # box width (Y)
H = 45.0            # box height (Z)
thk = 0.5           # sheet thickness
lid_overlap = 5.0   # lid skirt overlap onto the side panels
bend_allowance = 0.0  # leave to CAM; set if you want compensated dims

# Panel sizes (simple box with 4 side panels + base + lid).
base_L = L - 2 * thk
base_W = W - 2 * thk
side1_L = L - 2 * thk
side1_H = H - thk - lid_overlap
side2_L = W - 2 * thk
side2_H = H - thk - lid_overlap

# Layout origin and inter-panel gap on the flat sheet.
x0 = 10
y0 = 10
gap = 3.0

# Base rectangle.
base = Draft.makeRectangle(
    base_L, base_W,
    placement=Base.Placement(Base.Vector(x0, y0, 0), Base.Rotation(0, 0, 0, 1)))
doc.recompute()

# Side A (top of base).
sa = Draft.makeRectangle(
    side1_L, side1_H,
    placement=Base.Placement(
        Base.Vector(x0, y0 + base_W + gap, 0), Base.Rotation(0, 0, 0, 1)))
# Side B (right of base).
sb = Draft.makeRectangle(
    side2_L, side2_H,
    placement=Base.Placement(
        Base.Vector(x0 + base_L + gap, y0, 0), Base.Rotation(0, 0, 0, 1)))
# Side C (bottom of base).
sc = Draft.makeRectangle(
    side1_L, side1_H,
    placement=Base.Placement(
        Base.Vector(x0, y0 - side1_H - gap, 0), Base.Rotation(0, 0, 0, 1)))
# Side D (left of base).
sd = Draft.makeRectangle(
    side2_L, side2_H,
    placement=Base.Placement(
        Base.Vector(x0 - side2_L - gap, y0, 0), Base.Rotation(0, 0, 0, 1)))
# Lid (separate piece).
lid_w = L
lid_h = W
lid = Draft.makeRectangle(
    lid_w, lid_h,
    placement=Base.Placement(
        Base.Vector(x0 + base_L + side2_L + 3 * gap, y0, 0),
        Base.Rotation(0, 0, 0, 1)))

doc.recompute()


# Add mounting-hole markers (for CAM) as wire circles.
def add_hole(cx, cy, dia):
    """Draw a wire circle of diameter ``dia`` centred at ``(cx, cy)``."""
    c = Draft.makeCircle(
        dia / 2.0,
        placement=Base.Placement(
            Base.Vector(cx, cy, 0), Base.Rotation(0, 0, 0, 1)))
    c.ViewObject.DisplayMode = "Wire"
    return c


# Standoff holes positioned relative to the base origin (same as the 3D macro).
standoffs = [(18, 18), (62, 18), (18, 42), (62, 42)]
for (sx, sy) in standoffs:
    add_hole(x0 + sx - thk, y0 + sy - thk, 2.8)

# SMA hole markers on the lid layout (approx. mapping to right-face cluster in 3D).
sma_ys = [7.5, 16.5, 25.5, 34.5]
for y in sma_ys:
    add_hole(x0 + base_L + side2_L + 3 * gap + (L - 10), y0 + y, 6.2)

# M12 bulkhead marker.
add_hole(x0 + 12, y0 + 22.5, 21.0)

# Circular bulkhead markers.
cb_ys = [10, 20, 30, 40]
for y in cb_ys:
    add_hole(x0 + base_L + side2_L + 3 * gap + (L - 20), y0 + y, 14.0)

doc.recompute()

# Export all Draft objects to DXF.
objs = [o for o in doc.Objects if o.TypeId.startswith("Draft::")]
dxf_path = FreeCAD.getHomePath() + "shield_box_flat_pattern.dxf"
ImportGui.export(objs, dxf_path)
print("DXF exported to:", dxf_path)
