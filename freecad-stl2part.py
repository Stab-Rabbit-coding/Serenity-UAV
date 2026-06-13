import sys
import FreeCAD as App
import Mesh
import Part


def convert_stl_to_shape(stl_path, step_path):
    doc = App.newDocument("Headless")

    # Load and build geometry
    mesh_obj = Mesh.Mesh(stl_path)
    shape = Part.Shape()
    shape.makeShapeFromMesh(mesh_obj.Topology, 0.1)  # 0.1 is standard tolerance

    feature = doc.addObject("Part::Feature", "ShapeObject")
    feature.Shape = shape
    solid = Part.makeSolid(feature.Shape)

    # Export to standard CAD exchange format
    Part.export([solid], step_path)
    print(f"Successfully converted {stl_path} to {step_path}")

if __name__ == "__main__":
    
    # Pull paths directly from the command line arguments
    convert_stl_to_shape(sys.argv[1], sys.argv[2])
