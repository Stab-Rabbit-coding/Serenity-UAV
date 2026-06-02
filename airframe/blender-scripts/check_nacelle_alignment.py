import bpy, bmesh, math, os
from mathutils import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = [
    os.path.join('files-hollowed-18in', 's_eng_left_stator_shell24_50mm.stl'),
    os.path.join('files-hollowed-18in', 's_eng_right_stator_shell24_50mm.stl'),
]

# Use a Z slice around the middle of the thrust tube.
SAMPLING_Z_LO = 40.0
SAMPLING_Z_HI = 120.0


def circle_fit(points):
    # algebraic circle fit using least-squares
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    n = len(points)
    A00 = sum(x*x for x in xs)
    A01 = sum(x*y for x,y in zip(xs,ys))
    A02 = sum(xs)
    A11 = sum(y*y for y in ys)
    A12 = sum(ys)
    A22 = n
    b0 = -sum((x*x+y*y)*x for x,y in zip(xs,ys))
    b1 = -sum((x*x+y*y)*y for x,y in zip(xs,ys))
    b2 = -sum((x*x+y*y) for x,y in zip(xs,ys))
    A = [[float(A00), float(A01), float(A02)],
         [float(A01), float(A11), float(A12)],
         [float(A02), float(A12), float(A22)]]
    b = [float(b0), float(b1), float(b2)]
    # solve 3x3 linear system
    for i in range(3):
        pivot = i
        for j in range(i+1, 3):
            if abs(A[j][i]) > abs(A[pivot][i]):
                pivot = j
        if pivot != i:
            A[i], A[pivot] = A[pivot], A[i]
            b[i], b[pivot] = b[pivot], b[i]
        if abs(A[i][i]) < 1e-12:
            return None
        fac = A[i][i]
        for j in range(i, 3):
            A[i][j] /= fac
        b[i] /= fac
        for j in range(i+1, 3):
            f = A[j][i]
            for k in range(i, 3):
                A[j][k] -= f * A[i][k]
            b[j] -= f * b[i]
    x = [0.0, 0.0, 0.0]
    for i in range(2, -1, -1):
        s = b[i]
        for j in range(i+1, 3):
            s -= A[i][j] * x[j]
        x[i] = s / A[i][i]
    D, E, F = x
    cx = -D / 2.0
    cy = -E / 2.0
    r = math.sqrt(cx*cx + cy*cy - F)
    return cx, cy, r


def sample_vertices(obj, z_lo, z_hi):
    verts = []
    for v in obj.data.vertices:
        if z_lo <= v.co.z <= z_hi:
            verts.append((v.co.x, v.co.y, v.co.z))
    return verts


def main():
    for name in FILES:
        path = os.path.join(BASE, name)
        print('\n===', name, '===')
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.wm.stl_import(filepath=path)
        objs = [o for o in bpy.context.selected_objects if o.type == 'MESH']
        if not objs:
            print('Failed to import', name)
            continue
        obj = objs[0]
        verts = sample_vertices(obj, SAMPLING_Z_LO, SAMPLING_Z_HI)
        if not verts:
            print('No vertices in Z slice', SAMPLING_Z_LO, SAMPLING_Z_HI)
            continue
        xs = [x for x,y,z in verts]
        ys = [y for x,y,z in verts]
        x_centroid = sum(xs) / len(xs)
        y_centroid = sum(ys) / len(ys)
        bbox = [Vector(v) for v in obj.bound_box]
        bx = sum(v.x for v in bbox) / len(bbox)
        by = sum(v.y for v in bbox) / len(bbox)
        print(f'Shell bbox center XY = ({bx:.4f}, {by:.4f})')
        print(f'Shell vertex centroid XY = ({x_centroid:.4f}, {y_centroid:.4f})')
        inliers = []
        for x,y,z in verts:
            r = math.hypot(x - x_centroid, y - y_centroid)
            if 22.0 <= r <= 28.0:
                inliers.append((x, y))
        fit = circle_fit(inliers) if inliers else None
        if fit:
            cx, cy, r = fit
            print(f'Inner bore fit center = ({cx:.4f}, {cy:.4f}), r={r:.4f}, pts={len(inliers)}')
            print(f'Offset shell bbox -> bore = ({cx-bx:.4f}, {cy-by:.4f})')
        else:
            print('Inner bore fit failed or not enough points (n=', len(inliers), ')')
        bpy.ops.object.delete()


if __name__ == '__main__':
    main()
