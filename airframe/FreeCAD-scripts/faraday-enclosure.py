import os
import FreeCAD as App
import Part

# Initialize script-specific document safely
DOC_NAME = "ShieldBox"
doc = App.activeDocument()
if doc and doc.Name == DOC_NAME:
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)

# --- Parametric Dimensions ---
L, W, H = 80.0, 60.0, 45.0
thk = 0.5
lid_overlap = 5.0

innerL = L - (2 * thk)
innerW = W - (2 * thk)
innerH = H - thk

# --- Base Enclosure Shell ---
outer_box = Part.makeBox(L, W, H)
inner_box = Part.makeBox(innerL, innerW, innerH)
inner_box.translate(App.Vector(thk, thk, thk))
shell = outer_box.cut(inner_box)

# --- Lid and Finger-Stock Groove ---
lid_thk = thk
lid = Part.makeBox(L, W, lid_thk)
lid.translate(App.Vector(0, 0, H - lid_thk + lid_overlap))

groove_depth = 1.5
groove_width = 2.0
groove = Part.makeBox(innerL + (2 * groove_width), innerW + (2 * groove_width), groove_depth)
groove.translate(App.Vector(-groove_width, -groove_width, H - lid_thk + lid_overlap))
lid = lid.cut(groove)

# --- Cutout Tools Collection ---
cutout_tools = []

# Rotations for horizontal wall penetration
rotate_x_to_y = App.Rotation(App.Vector(1, 0, 0), 90)
rotate_z_to_x = App.Rotation(App.Vector(0, 1, 0), 90)

# SMA Bulkhead Holes (Punching through X-axis wall)
sma_radius = 3.1
sma_len = thk + 4.0
sma_y_positions = [7.5, 16.5, 25.5, 34.5]

for y in sma_y_positions:
    sma_cyl = Part.makeCylinder(sma_radius, sma_len)
    # Rotate cylinder to point along the X-axis
    sma_cyl.rotate(App.Vector(0, 0, 0), rotate_z_to_x)
    sma_cyl.translate(App.Vector(L - 2.0, y, (H / 2.0) - 1.0))
    cutout_tools.append(sma_cyl)

# M12 DC Hole (Punching through Y-axis wall)
m12_cyl = Part.makeCylinder(10.5, thk + 6.0)
m12_cyl.rotate(App.Vector(0, 0, 0), rotate_x_to_y)
m12_cyl.translate(App.Vector(12.0, -2.0, (H / 2.0) - 2.0))
cutout_tools.append(m12_cyl)

# Circular Bulkheads Cluster (Punching through Z-axis base floor)
cb_radius = 7.0
cb_len = thk + 4.0
cb_y_positions = [10.0, 20.0, 30.0, 40.0]
cb_fixed_x = L - 12.0

for y in cb_y_positions:
    cb_cyl = Part.makeCylinder(cb_radius, cb_len)
    cb_cyl.translate(App.Vector(cb_fixed_x, y, -2.0))
    cutout_tools.append(cb_cyl)

# Vent Cutouts (Narrow Sides - Left and Right Walls)
vent_w, vent_h, vent_d = 40.0, 6.0, thk + 4.0

vent_l = Part.makeBox(vent_w, vent_d, vent_h)
vent_l.translate(App.Vector((L - vent_w) / 2.0, -2.0, H - 8.0 - (vent_h / 2.0)))
cutout_tools.append(vent_l)

vent_r = Part.makeBox(vent_w, vent_d, vent_h)
vent_r.translate(App.Vector((L - vent_w) / 2.0, W - thk - 2.0, H - 8.0 - (vent_h / 2.0)))
cutout_tools.append(vent_r)

# Mounting Standoff Holes (M2.8 vertical through-holes)
standoff_radius = 1.4
standoff_positions = [(18.0, 18.0), (62.0, 18.0), (18.0, 42.0), (62.0, 42.0)]

for x, y in standoff_positions:
    standoff_cyl = Part.makeCylinder(standoff_radius, H + 4.0)
    standoff_cyl.translate(App.Vector(x, y, -2.0))
    cutout_tools.append(standoff_cyl)

# --- Consolidated Geometry Processing ---
# Combine all cutters into one compound for top-tier execution performance
cut_compound = Part.makeCompound(cutout_tools)
final_shell = shell.cut(cut_compound)

# --- Commit Shapes into FreeCAD Tree ---
shell_obj = doc.addObject("Part::Feature", "EnclosureShell")
shell_obj.Shape = final_shell

lid_obj = doc.addObject("Part::Feature", "Lid")
lid_obj.Shape = lid

doc.recompute()

# --- Secure File Path Export Handling ---
if doc.FileName:
    # Use the active path of the project if the file is already saved
    export_dir = os.path.dirname(doc.FileName)
else:
    # Fallback to User Home directory to preserve system permissions safely
    export_dir = os.path.expanduser("~")

step_path = os.path.normpath(os.path.join(export_dir, "shield_box_80x60x45.step"))

try:
    Part.export([shell_obj, lid_obj], step_path)
    print(f"Success: STEP file safely exported to: {step_path}")
except Exception as e:
    print(f"Error during STEP export operations: {str(e)}")
