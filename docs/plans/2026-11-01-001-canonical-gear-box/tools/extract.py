# mypy: ignore-errors  (exploratory plan-folder analysis script)
import sys, math, numpy as np, trimesh

sys.path.insert(0, "tools")
import gear_box_concept_fit as f, landing_gear_bay_function as lgbf
from manifold3d import Manifold

H = f.to_man(trimesh.load("airframe/stls/fuselage/head_cargo_shell24_2mm_merged.stl"))
C = lgbf.parse_corners(lgbf.SCAD)
for label in ("fore-port", "aft-port"):
    c = C[label]
    st = label.split("-")[0]
    tf = lgbf.corner_tf(c)
    d = (f'BAY_STATION="{st}"',)
    parts = [
        f.to_man(trimesh.load(f"airframe/stls/fuselage/landing-gear/lg_r6_3_0in_bay_{label}.stl"))
    ]
    for nm, ex in (("a1b backbone", "a1b_backbone();"), ("a1b members rest", "a1b_members(0);")):
        parts.append(lgbf.posed(lgbf.render(lgbf.SCAD, st, nm, ex, d), tf))
    cart = Manifold.batch_boolean(parts, 0)
    base = (cart ^ H).volume()
    az = math.radians(c[3])
    th = math.radians(48.2)
    dirs = {
        "out along thigh/pillar": (
            math.cos(az) * math.cos(th),
            math.sin(az) * math.cos(th),
            -math.sin(th),
        ),
        "inboard (cargo hold)": (-1, 0, 0),
        "straight down": (0, 0, -1),
        "outboard (hatch)": (1, 0, 0),
    }
    print(label, "cartridge", round(cart.volume()), "mm3; seated contact with hull", round(base))
    for n, v in dirs.items():
        sweep = Manifold.batch_boolean(
            [cart.translate(tuple(k * np.array(v))) for k in range(0, 121, 4)], 0
        )
        print(f"   {n:24s} swept clash {round((sweep^H).volume()-base):8d} mm3")
