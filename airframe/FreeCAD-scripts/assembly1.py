# create_assembly_from_stl.py
import os
import FreeCAD
import FreeCADGui
from FreeCAD import Vector, Rotation
import Mesh
import Part
import ImportGui

# Assembly4
import Assembly4

DOC = FreeCAD.newDocument("AircraftAssembly")
FreeCAD.setActiveDocument(DOC.Name)
FreeCADGui.ActiveDocument = FreeCADGui.getDocument(DOC.Name)

# ---------- User config ----------
# Replace with absolute paths to your STL (or STEP) files
FILES = {
    "head": "/absolute/path/fuselage.stl",
    "cargo": "airframe/stls/fuselage/cargo/s_cargo_sect_shell24_2mm_repaired.stl",
    "wing": "airframe/stls/wings/s_wing_port_s1223_revo.stl",        # single wing STL (intended to be mirrored)
    "nacelle": "/absolute/path/nacelle.stl",  # single nacelle STL (intended to be mirrored)
    "middle": "airframe/stls/middle.stl",
    "rear": "/absolute/path/tail.stl",
}

# Mirror plane X position (centerline)
MIRROR_X = 0.0

# Default placements (tweak as needed)
placements = {
    "fuselage": FreeCAD.Placement(Vector(0,0,0), Rotation(0,0,0,1)),
    "wing": FreeCAD.Placement(Vector(100,0,0), Rotation(0,0,0,1)),      # starboard wing
    "nacelle": FreeCAD.Placement(Vector(200,0,0), Rotation(0,0,0,1)),   # starboard nacelle
    "tail": FreeCAD.Placement(Vector(-200,0,0), Rotation(0,0,0,1)),
}

# ---------- Helpers ----------
def import_stl_as_mesh(path, label):
    ImportGui.insert(path, DOC.Name)
    obj = DOC.Objects[-1]
    obj.Label = label
    return obj

def mesh_to_solid(mesh_obj, label=None, tolerance=0.1):
    # create a shape from mesh, then convert to solid
    mesh = mesh_obj.Mesh
    shp = mesh.makeShapeFromMesh(tolerance, True)
    part_obj = DOC.addObject("Part::Feature", (label or mesh_obj.Label) + "_Part")
    part_obj.Shape = shp
    # try to make solid if possible
    try:
        solid = Part.makeSolid(shp)
        part_obj.Shape = solid
    except Exception:
        pass
    # hide original mesh
    mesh_obj.ViewObject.Visibility = False
    return part_obj

def mirror_shape(s, plane_point=Vector(0,0,0), plane_normal=Vector(1,0,0)):
    # returns a new Shape mirrored across plane defined by point and normal
    mirror = s.mirror(plane_point, plane_normal)
    return mirror

def make_assembly_root(name="AircraftRoot"):
    root = DOC.addObject("App::Part", name)
    root.Label = name
    return root


# ---------- Import & convert ----------
parts = {}
for key, path in FILES.items():
    if not os.path.isfile(path):
        raise FileNotFoundError("File not found: %s" % path)
    mesh_o = import_stl_as_mesh(path, key + "_Mesh")
    part_o = mesh_to_solid(mesh_o, label=key)
    parts[key] = part_o
    part_o.Placement = placements.get(key, FreeCAD.Placement())

# ---------- Create mirrored copies (true mirrored geometry) ----------
# Wing: create starboard (original) and port (mirrored)
wing_s = parts["wing"]
wing_s.Label = "Wing_Starboard"
# Mirror geometry across plane X = MIRROR_X (normal along X)
wing_port_shape = mirror_shape(wing_s.Shape, Vector(MIRROR_X,0,0), Vector(1,0,0))
wing_port = DOC.addObject("Part::Feature", "Wing_Port")
wing_port.Shape = wing_port_shape
# Position starboard and port placements (optional fine tuning)
wing_s.Placement = placements["wing"]
# For mirrored part, we may need to flip rotation to match orientation; here keep placement mirrored
wing_port.Placement = mirror_placement = FreeCAD.Placement(
    Vector(2*MIRROR_X - placements["wing"].Base.x, placements["wing"].Base.y, placements["wing"].Base.z),
    Rotation(Vector(0,0,1),180) * placements["wing"].Rotation
)
wing_port.ViewObject.ShapeColor = wing_s.ViewObject.ShapeColor

# Nacelle: same approach
nac_s = parts["nacelle"]
nac_s.Label = "Nacelle_Starboard"
nac_s.Placement = placements["nacelle"]
nac_port_shape = mirror_shape(nac_s.Shape, Vector(MIRROR_X,0,0), Vector(1,0,0))
nac_port = DOC.addObject("Part::Feature", "Nacelle_Port")
nac_port.Shape = nac_port_shape
nac_port.Placement = FreeCAD.Placement(
    Vector(2*MIRROR_X - placements["nacelle"].Base.x, placements["nacelle"].Base.y, placements["nacelle"].Base.z),
    Rotation(Vector(0,0,1),180) * placements["nacelle"].Rotation
)
nac_port.ViewObject.ShapeColor = nac_s.ViewObject.ShapeColor

# ---------- Assembly4: create root and add parts ----------
root = make_assembly_root("AircraftRoot")
# Add fuselage and tail
root.addObject(parts["fuselage"])
root.addObject(parts["tail"])
# Add wings and nacelles
root.addObject(wing_s)
root.addObject(wing_port)
root.addObject(nac_s)
root.addObject(nac_port)

DOC.recompute()
FreeCADGui.ActiveDocument.ActiveView.fitAll()

print("Assembly created in document:", DOC.Name)
