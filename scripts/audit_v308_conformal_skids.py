import os,json,glob,trimesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
rows=[]
for f in sorted(glob.glob(os.path.join(R,'print','v308_conformal_skids','*.stl'))):
 m=trimesh.load_mesh(f,force='mesh')
 row={'file':os.path.basename(f),'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),
 'bounds_mm':m.bounds.round(3).tolist(),'max_axis_mm':round(float(max(m.extents)),3),
 'volume_mm3':round(float(m.volume),3),'components':len(m.split(only_watertight=False))}
 rows.append(row);print('QA',row)
with open(os.path.join(R,'docs','V308_CONFORMAL_SKID_AUDIT.json'),'w') as o:json.dump(rows,o,indent=2)
print('V308_QA_ALL',len(rows),sum(x['watertight'] for x in rows),sum(x['winding'] for x in rows))
