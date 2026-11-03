import sys, numpy as np, trimesh

sys.path.insert(0, "tools")
import lg_a1b_census as c
from manifold3d import Manifold

g, mci, cbc, lgbf = c.g, c.mci, c.cbc, c.lgbf
P = cbc.build()
names = g.KEEPOUTS + ("payload keep-out",)
S = sys.argv[1]
box = mci.to_man(trimesh.load(S + "/fit/gear_box_port_fit.stl"))
cc0 = lgbf.parse_corners(lgbf.SCAD)["fore-port"]
for caz in (-60, -65, -70, -75):
    for saz in (80, 85, 90, 95, 100):
        cc = list(cc0)
        cc[3] = caz
        parts = []
        for nm, expr in (
            ("bb", "a1b_backbone();"),
            ("mr", "a1b_members(0);"),
            ("mf", "a1b_members(FLEX_DEG);"),
        ):
            path = lgbf.render(lgbf.SCAD, "fore", nm, expr, (f"A1B_STRUT_AZ={saz}",))
            parts.append(lgbf.posed(path, lgbf.corner_tf(cc)))
        w = Manifold.batch_boolean(parts, 0)
        hits = {k: round((w ^ P[k]["m"]).volume()) for k in names if (w ^ P[k]["m"]).volume() > 0.5}
        top = w.bounding_box()[5]
        print(f"corner {caz} strut {saz}: keep {sum(hits.values())} {hits} top Z {top:.0f}")
