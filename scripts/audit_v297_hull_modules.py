import os,glob,trimesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
parts=sorted(glob.glob(os.path.join(R,'print','v297_hull_modules','*.stl')))
assert len(parts)==6
for p in parts:
 m=trimesh.load_mesh(p,force='mesh')
 assert m.is_watertight and m.is_winding_consistent
 dims=m.extents
 assert all(v<256 for v in dims)
 side='front' if '_front.' in p else 'rear'
 if side=='front':assert m.bounds[1,0]<=-10+1e-2
 else:assert m.bounds[0,0]>=-15-1e-2
 print(os.path.basename(p),'dimensions',*[round(x,1) for x in dims], 'V',round(m.volume,1))
for file in ['01_Master_Central_fuselage','10_Planing_float_Left','10_Planing_float_Right']:
 front=trimesh.load_mesh(os.path.join(R,'print','v297_hull_modules',file+'_front.stl'))
 rear=trimesh.load_mesh(os.path.join(R,'print','v297_hull_modules',file+'_rear.stl'))
 print('SPLIT_SUM',file,round(front.volume+rear.volume,1))
print('ALL_SIX_PASS_CLOSED_AND_AXIS_FIT')
