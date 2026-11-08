import os,glob,json,trimesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
p=os.path.join(R,'print','v303_shell_prototypes')
report=[]
for fn in sorted(glob.glob(os.path.join(p,'*.stl'))):
 m=trimesh.load_mesh(fn,force='mesh')
 v=float(m.volume)
 x={'file':os.path.basename(fn),'watertight':bool(m.is_watertight),
 'winding_consistent':bool(m.is_winding_consistent),'components':len(m.split(only_watertight=False)),
 'volume_mm3':round(v,3),'solid_PLA_equivalent_g':round(abs(v)/1000*1.24,2),
 'extents_mm':[round(float(a),2) for a in m.extents],
 'axis_within_p2s':bool(all(float(a)<=256 for a in m.extents))}
 print(x);report.append(x)
h=[a for a in report if 'float_shell' in a['file'] or 'central_hull' in a['file']]
print('SUM_HULLS_MM3',sum(x['volume_mm3'] for x in h),
 'SUM_SOLID_PLA_EQUIVALENT_G',sum(x['solid_PLA_equivalent_g'] for x in h))
assert len(report)==4 and all(x['watertight'] and x['winding_consistent'] for x in report)
with open(os.path.join(R,'docs','V303_SHELL_AUDIT.json'),'w',encoding='utf-8') as f:json.dump(report,f,indent=2)
print('V303_AUDIT_PASS')
