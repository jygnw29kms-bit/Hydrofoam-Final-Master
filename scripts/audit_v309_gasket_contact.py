"""Evaluate planar v309 gasket mismatch against real v306 hull triangle geometry."""
import json,sys
from pathlib import Path
import numpy as np,trimesh
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from survey_v310_mounting_rays import vertical_hits
records=[]
for side in ('left','right'):
 cy=-119 if side=='left' else 119
 for half,xa,xb in (('front',-135,-14),('rear',-6,135)):
  hull=trimesh.load_mesh(ROOT/'print'/'v306_faceted_float_modules'/f'float_{side}_{half}.stl',force='mesh')
  for idx,x in enumerate((xa+15,xb-15),1):
   samples=[]
   for radius in (2.2,3.0,4.0,4.8):
    for angle in np.linspace(0,2*np.pi,16,endpoint=False):
     z=vertical_hits(hull,x+radius*np.cos(angle),cy+radius*np.sin(angle))
     if z:samples.append(min(z))
   if not samples:raise RuntimeError(f'No hull surface at {side}/{half}/{idx}')
   records.append({'side':side,'half':half,'hole':idx,'sample_count':len(samples),'hull_z_range_mm':round(max(samples)-min(samples),4),'hull_z_min_mm':round(min(samples),4),'hull_z_max_mm':round(max(samples),4),'planar_gasket_contact_approved':False})
report={'method':'64 vertical surface samples around each nominal gasket annulus; not a 3D collision or sealing test','positions':records,'pass':False,'reason':'No validated compression, inserts, or watertight mechanical interface'}
out=ROOT/'docs'/'V309_GASKET_CONTACT_QA.json';out.write_text(json.dumps(report,indent=2),encoding='utf-8')
print('V309_CONTACT_SAMPLED',len(records),'ranges mm',[r['hull_z_range_mm'] for r in records]);print('SEAL_APPROVAL',report['pass'])
