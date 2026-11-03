# mypy: ignore-errors  (exploratory plan-folder analysis script)
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
mask = Manifold.sphere(18.0, 48).translate(tuple(HIP))
names = list(g.KEEPOUTS) + ["payload keep-out"]
for caz in (-22.4, -35, -45, -55, -65, -75):
    cc = list(c)
    cc[3] = caz
    tfc = np.asarray(lgbf.corner_tf(cc))[:3, :4]
    best = None
    for az in range(50, 200, 10):
        w = Manifold.batch_boolean(
            [m.transform(tfc) for m in pk.members(55, az).values()], OpType.Add
        )
        wm = w - mask
        k = sum((w ^ P[n]["m"]).volume() for n in names)
        pr = (wm - ok_region).volume()
        wl = ((wm ^ hull) - box).volume()
        score = k + pr + wl
        if best is None or score < best[0]:
            best = (score, az, round(k), round(pr), round(wl))
    print(
        f"corner az {caz:6.1f}: best strut az {best[1]}  keep {best[2]}  proud {best[3]}  wall {best[4]}  (sum {best[0]:.0f} mm3)"
    )
