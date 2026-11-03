# mypy: ignore-errors  (exploratory plan-folder analysis script)
import sys, numpy as np, trimesh

sys.path.insert(0, "tools")
import lg_a1b_census as c
from manifold3d import Manifold

g, mci, cbc, lgbf = c.g, c.mci, c.cbc, c.lgbf
S = sys.argv[1]
src = cbc.as_trimesh(trimesh.load(mci.BLENDER_SRC, process=False), mci.BLENDER_SRC)
src.merge_vertices()
env = mci.to_man(mci.extract_envelope(mci.bake(src)))
hull = mci.to_man(mci.bake(src))
box = mci.to_man(trimesh.load(S + "/fit/gear_box_port_fit.stl"))
envm = mci.to_man(trimesh.load(S + "/fit/envelope_port.stl"))
ok = env + envm
cc = lgbf.parse_corners(lgbf.SCAD)["fore-port"]
mask = Manifold.sphere(18.0, 48).translate(tuple(cc[:3]))
for saz in (80,):
    parts = [
        lgbf.posed(
            lgbf.render(lgbf.SCAD, "fore", nm, expr, (f"A1B_STRUT_AZ={saz}",)), lgbf.corner_tf(cc)
        )
        for nm, expr in (
            ("bb", "a1b_backbone();"),
            ("mr", "a1b_members(0);"),
            ("mf", "a1b_members(FLEX_DEG);"),
        )
    ]
    w = Manifold.batch_boolean(parts, 0) - mask
    pr = w - ok
    print(
        f"strut {saz}: proud of OML {pr.volume():.0f} mm3  wall outside box {((w^hull)-envm).volume():.0f} mm3",
        [
            [round(v) for v in b.bounding_box()]
            for b in sorted(pr.decompose(), key=lambda b: -b.volume())[:2]
        ],
    )
