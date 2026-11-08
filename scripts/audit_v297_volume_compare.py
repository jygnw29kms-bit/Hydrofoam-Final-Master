import json,glob,os,trimesh
from pathlib import Path
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
original=json.loads((R/'docs'/'V297_SOURCE_VOLUMES.json').read_text())
report={}
for key,src in original.items():
 folder='v297_wing_modules' if key.startswith('20') else 'v297_hull_modules'
 volumes=[trimesh.load_mesh(str(R/'print'/folder/(key+'_'+side+'.stl')),force='mesh').volume for side in ('front','rear')]
 total=sum(volumes);rel=abs(total-src)/src
 report[key]={'source_mm3':src,'split_sum_mm3':total,'relative_volume_error':rel,'passes_1pct':bool(rel<.01)}
 print(key,'volume delta',round(total-src,2),'relative',round(rel*100,2),'%','PASS' if rel<.01 else 'FAIL')
(R/'docs'/'V297_VOLUME_CONSERVATION.json').write_text(json.dumps(report,indent=2))
assert all(report[k]['passes_1pct'] for k in report if not k.startswith('20'))
print('HULLS_PASS_WINGS_FLAGGED')

