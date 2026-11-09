"""Replace sparse 3-knuckle elevon hinge prototypes with 5 alternating knuckles."""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v335_ELEVON_HINGE_HARDWARE_WIP.blend'))
for obj in list(bpy.data.objects):
 if obj.name.startswith('V335_') and ('KNUCKLE' in obj.name or 'PIN' in obj.name):
  bpy.data.objects.remove(obj,do_unlink=True)
col=bpy.data.collections.new('V337_FIVE_KNUCKLE_ELEVON_HARDWARE_WIP')
bpy.context.scene.collection.children.link(col)
report=[]
for side,sign in [('Left',-1),('Right',1)]:
 a=Vector((175,sign*54,28.8));b=Vector((174,sign*162,28.8))
 axis=(b-a).normalized();positions=(0.16,0.33,0.50,0.67,0.84)
 sleeve_list=[]
 for i,t in enumerate(positions):
  owner='FIXED' if i%2==0 else 'MOVING'
  center=a+(b-a)*t
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=2.9,depth=14,location=center)
  sleeve=bpy.context.object;sleeve.name=f'V337_{side}_{owner}_ELEVON_KNUCKLE_{i}'
  sleeve.rotation_mode='QUATERNION';sleeve.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis)
  for collection in list(sleeve.users_collection):collection.objects.unlink(sleeve)
  col.objects.link(sleeve)
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1.45,depth=18,location=center)
  bore=bpy.context.object;bore.rotation_mode='QUATERNION';bore.rotation_quaternion=sleeve.rotation_quaternion
  bpy.context.view_layer.objects.active=sleeve
  mod=sleeve.modifiers.new('Bore_2p9','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=bore
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(bore,do_unlink=True)
  bm=bmesh.new();bm.from_mesh(sleeve.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
  sleeve_list.append({'name':sleeve.name,'owner':owner,'station':t,'nonmanifold_edges':bad})
 bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1.2,depth=(b-a).length+4,location=(a+b)/2)
 pin=bpy.context.object;pin.name=f'V337_{side}_ELEVON_PIN_2p4mm'
 pin.rotation_mode='QUATERNION';pin.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis)
 for collection in list(pin.users_collection):collection.objects.unlink(pin)
 col.objects.link(pin)
 gap=round((positions[1]-positions[0])*(b-a).length-14,3)
 report.append({'side':side,'knuckles':sleeve_list,'min_axial_gap_mm':gap,'nominal_radial_clearance_mm':0.25,'pin_diameter_mm':2.4})
outdir=root/'stl/v337';outdir.mkdir(parents=True,exist_ok=True)
for o in col.objects:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.wm.stl_export(filepath=str(outdir/(o.name+'.stl')),export_selected_objects=True,apply_modifiers=True)
out={'version':'v337','status':'five alternating physical bearing prototypes','sides':report,'accepted':False,'limitations':['not Boolean-unioned to wing/elevon','servo mounts/horns/linkages not integrated','print-fit and full articulation collision not validated','master image match not validated']}
(root/'docs/V337_FIVE_KNUCKLE_ELEVON_QA.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v337_FIVE_KNUCKLE_ELEVONS_WIP.blend'))
print('V337',json.dumps({'knuckles':sum(len(x['knuckles']) for x in report),'gaps':[x['min_axial_gap_mm'] for x in report],'bad_edges':sum(y['nonmanifold_edges'] for x in report for y in x['knuckles'])}))
