import sys, trimesh
sys.path.insert(0,'tools')
import lg_a1b_census as c
g,mci,cbc,lgbf=c.g,c.mci,c.cbc,c.lgbf
P=cbc.build(); h=mci.to_man(trimesh.load(sys.argv[1]))
for k in g.KEEPOUTS+("payload keep-out",):
    v=(h^P[k]["m"]).volume()
    if v>0.1: print("housing x",k,round(v,1))
print("housing vol",round(h.volume()))
src=cbc.as_trimesh(trimesh.load(mci.BLENDER_SRC,process=False),mci.BLENDER_SRC); src.merge_vertices()
env=mci.to_man(mci.extract_envelope(mci.bake(src)))
for k in ("TACCO CN2 port","chin shelf"):
    print("overlap outside hull envelope", k, round(((h^P[k]["m"])-env).volume(),2))
print("housing outside hull (new skin region) vol", round((h-env).volume()))
