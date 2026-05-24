import bpy, os, math
from mathutils import Vector

BASE = os.path.dirname(os.path.abspath(__file__))
FILES = [
    os.path.join('files-hollowed-18in', 's_eng_left_shell24_50mm.stl'),
    os.path.join('files-hollowed-18in', 's_eng_right_shell24_50mm.stl'),
]

Z_LO = 40.0
Z_HI = 120.0


def circle_fit(points):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    n = len(xs)
    if n < 3:
        return None
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
    x = [0.0,0.0,0.0]
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


def sample_and_fit(obj, z_lo, z_hi):
    pts = [(v.co.x, v.co.y, v.co.z) for v in obj.data.vertices if z_lo <= v.co.z <= z_hi]
    if not pts:
        return None
    cx = sum(x for x,y,z in pts) / len(pts)
    cy = sum(y for x,y,z in pts) / len(pts)
    ring = []
    for x,y,z in pts:
        r = math.hypot(x-cx, y-cy)
        if 22.0 <= r <= 30.0:
            ring.append((x,y))
    fit = circle_fit(ring)
    return {
        'centroid': (cx, cy),
        'fit': fit,
        'ring_pts': len(ring),
    }


def main():
    for f in FILES:
        path = os.path.join(BASE, f)
        print('\n===', f, '===')
        bpy.ops.wm.read_homefile(use_empty=True)
        bpy.ops.wm.stl_import(filepath=path)
        obj = bpy.context.selected_objects[0]
        res = sample_and_fit(obj, Z_LO, Z_HI)
        if not res:
            print('No verts in slice')
            continue
        bbox = [Vector(v) for v in obj.bound_box]
        bx = sum(v.x for v in bbox) / len(bbox)
        by = sum(v.y for v in bbox) / len(bbox)
        print('shell bbox center XY =', bx, by)
        print('shell centroid XY =', res['centroid'])
        if res['fit']:
            print('fit center XY =', res['fit'][:2], 'r=', res['fit'][2], 'pts=', res['ring_pts'])
        else:
            print('fit failed, ring points=', res['ring_pts'])
        bpy.ops.object.delete()

if __name__ == '__main__':
    main()
