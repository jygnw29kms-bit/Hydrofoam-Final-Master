from pathlib import Path
import json,trimesh
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
src=R/'print'/'v304_p2s_hollow_modules'
out=R/'print'/'v305_clean_p2s_shell_modules'
out.mkdir(exist_ok=True,parents=True)
report={}
for file in sorted(src.glob('*.stl')):
 original=trimesh.load_mesh(str(file),force='mesh')
 components=original.split(only_watertight=True)
 if not components: raise RuntimeError('NO_WATERTIGHT_COMPONENTS '+file.name)
 main=max(components,key=lambda c: len(c.faces))
 path=out/file.name
 main.export(str(path))
 reloaded=trimesh.load_mesh(str(path),force='mesh')
 err=abs(float(main.volume)-float(original.volume))/(abs(float(original.volume))+1e-9)
 status={'source_faces':int(len(original.faces)), 'kept_faces':int(len(main.faces)),
 'components_seen':int(len(components)), 'original_watertight':bool(original.is_watertight),
 'reloaded_watertight':bool(reloaded.is_watertight),
 'reloaded_consistent':bool(reloaded.is_winding_consistent),
 'volume_loss_percent':float(err*100),
 'dimension_mm':list(map(float,reloaded.extents))}
 print(file.name,status)
 if not(status['reloaded_watertight'] and status['reloaded_consistent'] and err<.001 and all(d<=256 for d in reloaded.extents)):
  raise AssertionError('FAILED '+file.name)
 report[file.name]=status
(R/'docs'/'V305_P2S_STL_AUDIT.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print('V305_ALL_SIX_MODULES_CLOSED')
