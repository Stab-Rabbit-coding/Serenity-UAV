import sys, numpy as np
sys.path.insert(0,'tools')
import lg_a1b_census as c
g,mci,cbc,lgbf=c.g,c.mci,c.cbc,c.lgbf
P=cbc.build()
cc=lgbf.parse_corners(lgbf.SCAD)["fore-port"]; tf=np.asarray(lgbf.corner_tf(cc)); inv=np.linalg.inv(tf)
for nm,expr in (("bb","a1b_backbone();"),("mr","a1b_members(0);"),("mf","a1b_members(FLEX_DEG);")):
    w=lgbf.posed(lgbf.render(lgbf.SCAD,"fore",nm,expr,("A1B_STRUT_AZ=90",)),tf)
    for k in ("TACCO CN2 port","chin shelf"):
        x=w^P[k]["m"]
        if x.volume()<0.5: continue
        v=np.asarray(x.to_mesh().vert_properties)[:,:3]
        loc=(np.c_[v,np.ones(len(v))]@inv.T)[:,:3]
        print(nm,k,round(x.volume()),"leg-local x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f"%(loc[:,0].min(),loc[:,0].max(),loc[:,1].min(),loc[:,1].max(),loc[:,2].min(),loc[:,2].max()))
