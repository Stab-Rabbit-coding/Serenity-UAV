import os
import FreeCAD as App
import Part

# Initialize script-specific document safely
DOC_NAME = "FlatPattern"
doc = App.activeDocument()
if doc and doc.Name == DOC_NAME:
    App.closeDocument(DOC_NAME)
doc = App.newDocument(DOC_NAME)

# Try to safely load Draft, falling back if not initialized
try:
    import Draft
except ImportError:
    import drafttests.uicmd as Draft

# --- Layout Parameters (mm) ---
L, W, H = 80.0, 60.0, 45.0
thk = 0.5
lid_overlap = 5.0
gap = 3.0

# Fixed grid origin for 2D nesting
x0, y0 = 10.0, 10.0

# --- Panel Dimensional Analysis ---
base_L = L - (2.0 * thk)
base_W = W - (2.0 * thk)

side1_L = L - (2.0 * thk)
side1_H = H - thk - lid_overlap

side2_L = W - (2.0 * thk)
side2_H = H - thk - lid_overlap

lid_w, lid_h = L, W

# --- 2D Sheet Metal Layout Generation ---

# Base Plate Panel
base_placement = App.Placement(App.Vector(x0, y0, 0), App.Rotation(0, 0, 0, 1))
base = Draft.makeRectangle(base_L, base_W, placement=base_placement)

# Side Panel A (Nested above the base)
sa_placement = App.Placement(App.Vector(x0, y0 + base_W + gap, 0), App.Rotation(0, 0, 0, 1))
sa = Draft.makeRectangle(side1_L, side1_H, placement=sa_placement)

# Side Panel B (Nested to the right of the base)
sb_placement = App.Placement(App.Vector(x0 + base_L + gap, y0, 0), App.Rotation(0, 0, 0, 1))
sb = Draft.makeRectangle(side2_L, side2_H, placement=sb_placement)

# Side Panel C (Nested below the base)
sc_placement = App.Placement(App.Vector(x0, y0 - side1_H - gap, 0), App.Rotation(0, 0, 0, 1))
sc = Draft.makeRectangle(side1_L, side1_H, placement=sc_placement)

# Side Panel D (Nested to the left of the base)
sd_placement = App.Placement(App.Vector(x0 - side2_L - gap, y0, 0), App.Rotation(0, 0, 0, 1))
sd = Draft.makeRectangle(side2_L, side2_H, placement=sd_placement)

# Separate Lid Shield Panel
lid_x0 = x0 + base_L + side2_L + (3.0 * gap)
lid_placement = App.Placement(App.Vector(lid_x0, y0, 0), App.Rotation(0, 0, 0, 1))
lid = Draft.makeRectangle(lid_w, lid_h, placement=lid_placement)

doc.recompute()

# --- Helper Function: CAM Marker Placement ---
def add_hole_marker(cx, cy, diameter):
    """Safely draws a 2D circle feature compatible with GUI and Headless workflows."""
    circle_placement = App.Placement(App.Vector(cx, cy, 0), App.Rotation(0, 0, 0, 1))
    c = Draft.makeCircle(diameter / 2.0, placement=circle_placement)
    
    # Secure view parameters against CLI/Headless engine crashes
    if hasattr(c, "ViewObject") and c.ViewObject is not None:
        c.ViewObject.DisplayMode = "Wire"
    return c

# --- Feature Cutout Layout Processing ---

# Mounting Standoff Pattern (Calculated relative to Base Plate)
standoffs = [(18.0, 18.0), (62.0, 18.0), (18.0, 42.0), (62.0, 42.0)]
for sx, sy in standoffs:
    add_hole_marker(x0 + sx - thk, y0 + sy - thk, 2.8)

# M12 Power Access Cutout Marker
add_hole_marker(x0 + 12.0, y0 + 22.5, 21.0)

# SMA RF Connector Target Cluster (Calculated on Lid Shield Panel)
sma_ys = [7.5, 16.5, 25.5, 34.5]
sma_target_x = lid_x0 + (L - 10.0)
for y_pos in sma_ys:
    add_hole_marker(sma_target_x, y0 + y_pos, 6.2)

# Circular Utility Bulkheads Pattern
cb_ys = [10.0, 20.0, 30.0, 40.0]
cb_target_x = lid_x0 + (L - 20.0)
for y_pos in cb_ys:
    add_hole_marker(cb_target_x, y0 + y_pos, 14.0)

doc.recompute()

# --- Secure File Path Export Handling ---
if doc.FileName:
    export_dir = os.path.dirname(doc.FileName)
else:
    export_dir = os.path.expanduser("~")

dxf_path = os.path.normpath(os.path.join(export_dir, "shield_box_flat_pattern.dxf"))

# Collect all Draft objects generated for manufacturing export
export_objects = [obj for obj in doc.Objects if obj.TypeId.startswith("Draft::")]

try:
    # Check for graphical user interface vs headless execution mode
    import FreeCADGui
    if FreeCADGui.getMainWindow() is not None:
        import ImportGui
        ImportGui.export(export_objects, dxf_path)
    else:
        # CLI Fallback using low-level internal DXF export libraries
        import importDXF
        importDXF.export(export_objects, dxf_path)
        
    print(f"Success: DXF flat pattern exported to: {dxf_path}")
except Exception as e:
    print(f"Error executing DXF export processing sequence: {str(e)}")
