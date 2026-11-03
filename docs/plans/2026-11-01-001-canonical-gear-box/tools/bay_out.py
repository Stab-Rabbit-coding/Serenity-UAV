# mypy: ignore-errors  (exploratory plan-folder analysis script)
import sys, numpy as np, trimesh

sys.path.insert(0, "tools")
sys.path.insert(0, "airframe/blender-scripts")
import gear_box_hull_merge as g, gear_box_concept_fit as f
import lg_bay_corner_params as bp, landing_gear_bay_function as lgbf

S = sys.argv[1]
O = g.placed("cargo_sect_shell24_2mm_repaired__outer.stl", "Cargo_Shell")
bo = g.both(f.trim(f.render_box(S + "/fit", 0.0)))
keep = O + bo
wing = f.to_man(trimesh.load(f.WING))
wing = wing + g.mirror_cl(wing)
for c in g.BAYS:
    b = f.to_man(trimesh.load(f"airframe/stls/fuselage/landing-gear/lg_r6_3_0in_bay_{c}.stl"))
    out = b - keep
    pcs = sorted(out.decompose(), key=lambda x: -x.volume())
    print(
        c,
        "bay vol",
        round(b.volume()),
        "outside hull+box",
        round(out.volume()),
        "x wing",
        round((b ^ wing).volume(), 1),
        [[round(v) for v in p.bounding_box()] for p in pcs[:2]],
    )
