import trimesh,os,json,numpy as np
from pathlib import Path
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
out={}
for prefix,folder in [('01_Master_Central_fuselage','v297_hull_modules'),('10_Planing_float_Left','v297_hull_modules'),('10_Planing_float_Right','v297_hull_modules'),('20_Swept_blended_wing_Left','v298_wing_modules'),('20_Swept_blended_wing_Right','v298_wing_modules')]:
 a=trimesh.load_mesh(R/'print'/folder/(prefix+'_front.stl'))
 b=trimesh.load_mesh(R/'print'/folder/(prefix+'_rear.stl'))
 plane=-15 if prefix.startswith('01') else -10
 sections=[]
 for m in (a,b):
  # Trimesh cross-section: actual perimeter and 2D filled area
  tris=m.triangles
  mask=np.all(np.abs(tris[:,:,0]-plane)<.01,axis=1)
  flat=tris[mask]
  area=float(np.sum(np.linalg.norm(np.cross(flat[:,1]-flat[:,0],flat[:,2]-flat[:,0]),axis=1)*.5))
  sections.append({'coplanar_triangles':int(mask.sum()),'area_mm2':area,'bounds_mm':flat[:,:,1:].reshape(-1,2).min(axis=0).tolist()+flat[:,:,1:].reshape(-1,2).max(axis=0).tolist() if len(flat) else []})
 out[prefix]={'plane_x_mm':plane,'front':sections[0],'rear':sections[1],
 'area_difference_mm2':abs(sections[0]['area_mm2']-sections[1]['area_mm2'])}
 print(prefix,out[prefix])
(R/'docs'/'V299_JOINT_SECTIONS.json').write_text(json.dumps(out,indent=2))
