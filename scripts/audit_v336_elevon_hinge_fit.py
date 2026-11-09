"""V336 CAD dimensional audit: verify axial gaps, bearing bore, pin and object origins."""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v335_ELEVON_HINGE_HARDWARE_WIP.blend'))
data=[]
for side,sgn in [('Left',-1),('Right',1)]:
 a=Vector((175,sgn*54,28.8)); b=Vector((174,sgn*162,28.8))
 axis=(b-a).normalized()
 items=[]
 for i,owner in enumerate(('FIXED','MOVING','FIXED')):
  name=f'V335_{side}_{owner}_ELEVON_KNUCKLE_{i}'
  o=bpy.data.objects.get(name)
  assert o, name
  center=o.matrix_world.translation
  # Dimension from transformed mesh geometry, not just nominal input.
  proj=[(o.matrix_world@v.co-center).dot(axis) for v in o.data.vertices]
  axial_min=center.dot(axis)+min(proj)
  axial_max=center.dot(axis)+max(proj)
  items.append({'name':name,'axial_min_mm':round(axial_min,3),'axial_max_mm':round(axial_max,3),'center_mm':[round(x,3) for x in center]})
 items.sort(key=lambda x:x['axial_min_mm'])
 gaps=[round(items[i+1]['axial_min_mm']-items[i]['axial_max_mm'],3) for i in range(2)]
 pin=bpy.data.objects.get(f'V335_{side}_ELEVON_PIN_2p4mm')
 assert pin
 nominal_bore=2.9
 nominal_pin=2.4
 data.append({'side':side,'knuckles':items,'axial_gaps_mm':gaps,'axial_noninterference':all(g>=0 for g in gaps),'nominal_radial_clearance_mm':(nominal_bore-nominal_pin)/2,'pin_length_mm':round(pin.dimensions.length,3),'pin_present':True})
report={'version':'v336','scope':'real Blender v335 hinge hardware fit check','results':data,'acceptance':{'axial_noninterference':all(x['axial_noninterference'] for x in data),'both_pins_exist':all(x['pin_present'] for x in data),'structural_parent_union':False,'servo_linkage_sweep':False,'real_print_fit':False},'limitations':['Axial gap uses CAD geometry only, not manufacturing tolerance','Pin fit is nominal; STL and printed dimensions not yet measured','Hinge knuckles are not attached to parent surfaces','No collision sweep of complete moving elevon, horns or linkage'],'accepted':False}
out=root/'docs/V336_ELEVON_HINGE_FIT_AUDIT.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,indent=2))
