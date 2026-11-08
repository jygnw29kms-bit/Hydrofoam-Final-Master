import json,trimesh,glob,os,numpy as np
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
entries=[]
for f in sorted(glob.glob(os.path.join(R,'print','v306_faceted_float_modules','*.stl'))):
 mesh=trimesh.load_mesh(f,force='mesh')
 entries.append(dict(name=os.path.basename(f),watertight=bool(mesh.is_watertight),
 winding=bool(mesh.is_winding_consistent),volume_mm3=float(mesh.volume),
 bounds=mesh.bounds.tolist(),extents_mm=mesh.extents.tolist(),
 euler=int(mesh.euler_number),components=len(mesh.split(only_watertight=False))))
 for e in entries[-1:]:print(e)
with open(os.path.join(R,'docs','V306_FACETED_FLOAT_AUDIT.json'),'w') as g:
 json.dump(entries,g,indent=2)
print('V306_QA',len(entries),'watertight',sum(x['watertight'] for x in entries),'winding',sum(x['winding'] for x in entries))
