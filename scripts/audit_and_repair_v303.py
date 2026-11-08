import os,json,trimesh
from pathlib import Path
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
p=R/'print'/'v303_shell_prototypes'
fn=p/'removable_smoked_canopy.stl'
m=trimesh.load_mesh(str(fn),force='mesh')
mask=m.nondegenerate_faces(height=1e-5)
removed=len(m.faces)-int(mask.sum())
m.update_faces(mask);m.remove_unreferenced_vertices()
assert removed==2 and m.is_watertight and m.is_winding_consistent
m.export(str(fn))
report=[]
for f in sorted(p.glob('*.stl')):
 mesh=trimesh.load_mesh(str(f),force='mesh')
 row={'file':f.name,'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),'components':len(mesh.split(only_watertight=False)),'volume_mm3':round(float(mesh.volume),2),'estimated_PLA_mass_g':round(float(mesh.volume)*0.00124,2),'extents_mm':[round(float(v),2) for v in mesh.extents],'single_part_fits_P2S':bool(all(v<=256 for v in mesh.extents))}
 print(row);report.append(row)
assert all(x['watertight'] and x['winding_consistent'] for x in report)
(R/'docs'/'V303_SHELL_AUDIT.json').write_text(json.dumps({'status':'PASS_MESH_ONLY','canopy_degenerate_faces_removed':removed,'parts':report},indent=2),encoding='utf-8')
print('V303_STL_MESH_AUDIT_PASS; NOTE FULL LENGTH HULLS NOT YET P2S SEGMENTED')
