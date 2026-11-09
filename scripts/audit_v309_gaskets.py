import glob,json,os,trimesh
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=[]
for p in sorted(glob.glob(os.path.join(R,'print','v309_mounting_gasket_prototypes','*.stl'))):
 m=trimesh.load_mesh(p,force='mesh')
 rows.append(dict(file=os.path.basename(p),watertight=bool(m.is_watertight),winding=bool(m.is_winding_consistent),components=len(m.split()),volume_mm3=round(float(m.volume),3),extents_mm=m.extents.round(3).tolist()))
with open(os.path.join(R,'docs','V309_GASKET_QA.json'),'w') as f:json.dump(rows,f,indent=2)
assert len(rows)==8 and all(r['watertight'] and r['winding'] and r['components']==1 and max(r['extents_mm'])<256 for r in rows)
print('V309_QA_PASS',len(rows),'total volume mm3',round(sum(r['volume_mm3'] for r in rows),2))
