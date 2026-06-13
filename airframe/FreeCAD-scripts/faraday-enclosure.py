import FreeCAD, Part, Mesh, MeshPart, Draft
from FreeCAD import Base
doc = FreeCAD.newDocument("ShieldBox")

L=80.0; W=60.0; H=45.0; thk=0.5; lid_overlap=5.0
innerL=L-2*thk; innerW=W-2*thk; innerH=H-thk

# base box (sheet metal box, approximate with solid walls)
outer = Part.makeBox(L,W,H)
inner = Part.makeBox(innerL,innerW,innerH)
inner.translate(Base.Vector(thk,thk,thk))
shell = outer.cut(inner)

# lid (simple removable lid with overlap)
lid_thk = thk
lid = Part.makeBox(L, W, lid_thk)
lid.translate(Base.Vector(0,0,H-lid_thk+lid_overlap))  # overlap region
# finger-stock groove (inner perimeter cutout)
groove_depth=1.5; groove_width=2.0
groove = Part.makeBox(innerL+2*groove_width, innerW+2*groove_width, groove_depth)
groove.translate(Base.Vector(-groove_width, -groove_width, H-lid_thk+lid_overlap))
lid = lid.cut(groove)

# SMA bulkhead holes (right face), positions per spec
import math
sma_hole = Part.makeCylinder(3.1, thk+2) # diameter 6.2
sma_x = L - thk/2
sma_ys = [7.5,16.5,25.5,34.5]
holes = []
for y in sma_ys:
    h = sma_hole.copy()
    h.translate(Base.Vector(sma_x, y, H/2 - 1))
    holes.append(h)

# M12 DC hole (front left)
m12 = Part.makeCylinder(10.5, thk+4) # adjust per nut spec
m12.translate(Base.Vector(12,22.5,H/2 - 2))

# circular bulkheads cluster (right cluster)
cb_hole = Part.makeCylinder(7.0, thk+2)
cb_ys = [10,20,30,40]
cb_x = L - 12
cbs = []
for y in cb_ys:
    c = cb_hole.copy()
    c.translate(Base.Vector(cb_x, y, H/2 - 1))
    cbs.append(c)

# vent cutouts on narrow sides (left & right)
vent_w=40; vent_h=6; vent_depth=thk+2
vent = Part.makeBox(vent_w, vent_h, vent_depth)
vent.translate(Base.Vector((L-vent_w)/2, -1, H-8-vent_h/2))
vent_r = vent.copy(); vent_r.translate(Base.Vector(0,W+1,0))

# apply holes to shell
for h in holes: shell = shell.cut(h)
shell = shell.cut(m12)
for c in cbs: shell = shell.cut(c)
shell = shell.cut(vent); shell = shell.cut(vent_r)

# add features: mounting standoff holes (M2.8)
standoff = Part.makeCylinder(1.4, H)
standoff_positions = [(18,18),(62,18),(18,42),(62,42)]
for (x,y) in standoff_positions:
    s = standoff.copy()
    s.translate(Base.Vector(x,y,0))
    shell = shell.cut(s)

# create objects in document
shell_obj = doc.addObject("Part::Feature","EnclosureShell")
shell_obj.Shape = shell
lid_obj = doc.addObject("Part::Feature","Lid")
lid_obj.Shape = lid

doc.recompute()

# export STEP
step_path = FreeCAD.getHomePath() + "shield_box_80x60x45.step"
Part.export([shell_obj, lid_obj], step_path)
print("STEP exported to:", step_path)
