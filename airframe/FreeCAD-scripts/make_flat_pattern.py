import FreeCAD, Draft, Part
from FreeCAD import Base
doc = FreeCAD.newDocument("FlatPattern")

# params (mm)
L=80.0; W=60.0; H=45.0; thk=0.5; lid_overlap=5.0
bend_allowance = 0.0  # leave to CAM; set if you want compensated dims

# Panels sizes (simple box with 4 side panels + base + lid)
base_L = L - 2*thk
base_W = W - 2*thk
side1_L = L - 2*thk
side1_H = H - thk - lid_overlap
side2_L = W - 2*thk
side2_H = H - thk - lid_overlap

# Layout origin
x0 = 10; y0 = 10
gap = 3.0

# Base rectangle
base = Draft.makeRectangle(base_L, base_W, placement=Base.Placement(Base.Vector(x0,y0,0),Base.Rotation(0,0,0,1)))
doc.recompute()

# Side A (top of base)
sa = Draft.makeRectangle(side1_L, side1_H, placement=Base.Placement(Base.Vector(x0, y0+base_W+gap, 0),Base.Rotation(0,0,0,1)))
# Side B (right of base)
sb = Draft.makeRectangle(side2_L, side2_H, placement=Base.Placement(Base.Vector(x0+base_L+gap, y0, 0),Base.Rotation(0,0,0,1)))
# Side C (bottom of base)
sc = Draft.makeRectangle(side1_L, side1_H, placement=Base.Placement(Base.Vector(x0, y0 - side1_H - gap, 0),Base.Rotation(0,0,0,1)))
# Side D (left of base)
sd = Draft.makeRectangle(side2_L, side2_H, placement=Base.Placement(Base.Vector(x0 - side2_L - gap, y0, 0),Base.Rotation(0,0,0,1)))
# Lid (separate piece)
lid_w = L; lid_h = W
lid = Draft.makeRectangle(lid_w, lid_h, placement=Base.Placement(Base.Vector(x0 + base_L + side2_L + 3*gap, y0, 0),Base.Rotation(0,0,0,1)))

doc.recompute()

# Add mounting hole markers (for CAM) - circles
def add_hole(cx,cy,dia):
    c = Draft.makeCircle(dia/2.0, placement=Base.Placement(Base.Vector(cx,cy,0),Base.Rotation(0,0,0,1)))
    c.ViewObject.DisplayMode = "Wire"
    return c

# Standoff holes positions relative to base origin (same positions as 3D macro)
standoffs = [(18,18),(62,18),(18,42),(62,42)]
for (sx,sy) in standoffs:
    add_hole(x0 + sx - thk, y0 + sy - thk, 2.8)

# SMA hole markers on lid layout (approx mapping to right face cluster in 3D)
sma_ys = [7.5,16.5,25.5,34.5]
sma_x = x0 + base_L + side2_L + 3*gap +  (L - thk/2) - (x0 + base_L + side2_L + 3*gap)
for y in sma_ys:
    add_hole(x0 + base_L + side2_L + 3*gap + (L - 10), y0 + y, 6.2)

# M12 marker
add_hole(x0 + 12, y0 + 22.5, 21.0)

# circular bulkheads markers
cb_ys = [10,20,30,40]
for y in cb_ys:
    add_hole(x0 + base_L + side2_L + 3*gap + (L - 20), y0 + y, 14.0)

doc.recompute()

# Export all draft objects to DXF
import ImportGui
objs = [o for o in doc.Objects if o.TypeId.startswith("Draft::")]
dxf_path = FreeCAD.getHomePath() + "shield_box_flat_pattern.dxf"
ImportGui.export(objs, dxf_path)
print("DXF exported to:", dxf_path)
