import sys, numpy as np, trimesh

sys.path.insert(0, "tools")
import lg_a1b_packaging as pk
from manifold3d import Manifold, OpType

g, mci, cbc, lgbf = pk.g, pk.mci, pk.cbc, pk.lgbf
S = sys.argv[1]
src = cbc.as_trimesh(trimesh.load(mci.BLENDER_SRC, process=False), mci.BLENDER_SRC)
src.merge_vertices()
env = mci.to_man(mci.extract_envelope(mci.bake(src)))
hull = mci.to_man(mci.bake(src))
P = cbc.build()
keep = Manifold.batch_boolean([P[k]["m"] for k in g.KEEPOUTS], OpType.Add)
box = mci.to_man(trimesh.load(S + "/fit/gear_box_port_fit.stl"))
ok_region = env + box
c = lgbf.parse_corners(lgbf.SCAD)["fore-port"]
tf = np.asarray(lgbf.corner_tf(c))[:3, :4]
for az in []:
    rows = pk.members(pk.REACH, az)
    tot = [0, 0, 0]
    for m in rows.values():
        w = m.transform(tf)
        tot[0] += (w ^ keep).volume()
        tot[1] += ((w ^ hull) - box).volume()
        tot[2] += (w - ok_region).volume()
    print(
        f"fore az {az:4d}: keep-outs {tot[0]:8.1f}  hull wall outside box {tot[1]:8.1f}  proud of OML {tot[2]:8.1f} mm3"
    )

# payload hold: members may not cross into the hoist path either
pay = P["payload keep-out"]["m"]
print("reach sweep (fore-port), PASS = keep-outs+payload <1, wall-outside-box <1, proud <1 mm3")
HIP = np.array(c[:3], float)
for MASK in (18.0,):
    mask = Manifold.sphere(MASK, 48).translate(tuple(HIP))
    print("hip mask r", MASK)
    for az in range(35, 150, 15):
        best = None
        why = None
        for reach in (25, 30, 35, 40, 45, 50, 55):
            rows = pk.members(reach, az)
            t = [0, 0, 0]
            for m in rows.values():
                w = m.transform(tf)
                wm = w - mask
                t[0] += ((w ^ keep) + (w ^ pay)).volume()
                t[1] += ((wm ^ hull) - box).volume()
                t[2] += (wm - ok_region).volume()
            if max(t) < 1:
                best = reach
            elif why is None:
                why = [round(x) for x in t]
        print(f"  az {az:4d}: max clear reach {best}  first fail [keep+pay, wall, proud] {why}")
