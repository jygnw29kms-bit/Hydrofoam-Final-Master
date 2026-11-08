from pathlib import Path
import json,trimesh
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master');outdir=R/'print'/'v304_p2s_hollow_modules'
source=R/'print'/'v303_shell_prototypes'
report={}
for label,source_file in [('center','central_hull_shell.stl'),('float_left','left_float_shell.stl'),('float_right','right_float_shell.stl')]:
 ref=trimesh.load_mesh(str(source/source_file),force='mesh')
 parts=[]
 for side in ('front','rear'):
  p=outdir/(label+'_'+side+'.stl')
  m=trimesh.load_mesh(str(p),force='mesh')
  parts.append(m)
  print(label,side,'watertight',m.is_watertight,'winding',m.is_winding_consistent,'volume',m.volume,'dims',m.extents)
 vol=sum(float(m.volume) for m in parts)
 err=abs(vol-ref.volume)/abs(ref.volume)
 report[label]={'source_volume_mm3':float(ref.volume),'split_volume_mm3':vol,
 'relative_difference_pct':err*100,'watertight_parts':[bool(m.is_watertight) for m in parts],
 'p2s_256_axis_fit_parts':[bool(all(float(x)<256 for x in m.extents)) for m in parts],
 'passes_volume_1pct':bool(err<.01)}
 print('COMPARISON',label,'delta_pct',round(err*100,2),'volume_pass',err<.01)
(R/'docs'/'V304_SPLIT_QA.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('V304_RELEASE_READY',all(p['passes_volume_1pct'] and all(p['watertight_parts']) and all(p['p2s_256_axis_fit_parts']) for p in report.values()))
