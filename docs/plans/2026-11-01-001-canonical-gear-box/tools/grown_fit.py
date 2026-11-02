import sys, trimesh
sys.path.insert(0,'tools')
import gear_box_concept_fit as f, landing_gear_bay_function as lgbf
S=sys.argv[1]
H=f.to_man(trimesh.load('airframe/stls/fuselage/head_cargo_shell24_2mm_merged.stl'))
for label,c in lgbf.parse_corners(lgbf.SCAD).items():
    if 'stbd' in label: continue
    st=label.split('-')[0]; tf=lgbf.corner_tf(c)
    for var in ("baseline","grown"):
        d=(f'BAY_STATION="{st}"', f'THIGH_VARIANT="{var}"')
        leg=lgbf.render(lgbf.SCAD,st,"leg (thigh+shin+foot)",lgbf.FEATURES["leg (thigh+shin+foot)"][0],d)
        sw=lgbf.swept_leg(leg,tf)
        print(f"{label:9s} {var:8s} swept leg 0..{lgbf.SWEEP_DEG:g} deg x fused hull {(sw^H).volume():9.1f} mm3")
