import trimesh,glob,os,json
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
rows=[]
for f in sorted(glob.glob(os.path.join(R,'print','v307_land_skid_prototypes','*.stl'))):
 m=trimesh.load_mesh(f,force='mesh')
 row={'name':os.path.basename(f),'watertight':bool(m.is_watertight),'winding':bool(m.is_winding_consistent),'components':len(m.split(only_watertight=False)),'volume_mm3':round(float(m.volume),2),'bounds_mm':m.bounds.round(2).tolist(),'extents_mm':m.extents.round(2).tolist()}
 rows.append(row);print(row)
out=os.path.join(R,'docs','V307_LAND_SKID_QA.json')
with open(out,'w') as g:json.dump(rows,g,indent=2)
assert len(rows)==4 and all(x['watertight'] and x['winding'] and max(x['extents_mm'])<256 for x in rows)
print('V307_QA_PASS')
