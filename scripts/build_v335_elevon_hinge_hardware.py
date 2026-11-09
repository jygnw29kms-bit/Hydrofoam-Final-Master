import bpy,os,json,math,bmesh
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend'))
col=bpy.data.collections.new('V335_ELEVON_HINGE_HARDWARE_PROTOTYPE');bpy.context.scene.collection.children.link(col)
report=[]
def move(o,name):
 o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
 return o
for side,sign in [('Left',-1),('Right',1)]:
 a=Vector((175,sign*54,28.8));b=Vector((174,sign*162,28.8))
 axis=(b-a).normalized();length=(b-a).length
 # Two separate axial bearing sleeves on the fixed side, one on moving side.
 for i,(t,owner) in enumerate([(0.18,'FIXED'),(0.50,'MOVING'),(0.82,'FIXED')]):
  center=a+(b-a)*t
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=2.9,depth=14,location=center)
  sleeve=move(bpy.context.object,f'V335_{side}_{owner}_ELEVON_KNUCKLE_{i}')
  sleeve.rotation_mode='QUATERNION';sleeve.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis)
  bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.45,depth=17,location=center)
  bore=bpy.context.object;bore.rotation_mode='QUATERNION';bore.rotation_quaternion=sleeve.rotation_quaternion
  bpy.context.view_layer.objects.active=sleeve
  mod=sleeve.modifiers.new('Pin_bore_2p9mm','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=bore
  bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(bore,do_unlink=True)
  bm=bmesh.new();bm.from_mesh(sleeve.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
  report.append({'side':side,'owner':owner,'knuckle':i,'nonmanifold_edges':nonmanifold,'bore_diameter_mm':2.9,'outer_diameter_mm':5.8,'length_mm':14})
 # Print pin as independent physical solid, no render-only axis.
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.2,depth=length+4,location=(a+b)/2)
 pin=move(bpy.context.object,f'V335_{side}_ELEVON_PIN_2p4mm')
 pin.rotation_mode='QUATERNION';pin.rotation_quaternion=Vector((0,0,1)).rotation_difference(axis)
os.makedirs(os.path.join(R,'stl','v335'),exist_ok=True)
exports=[]
for o in list(col.objects):
 if o.type!='MESH':continue
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 target=os.path.join(R,'stl','v335',o.name+'.stl')
 bpy.ops.wm.stl_export(filepath=target,export_selected_objects=True,apply_modifiers=True)
 exports.append(os.path.relpath(target,R))
out={'version':'v335','prototype_only':True,'knuckles':report,'stl_exports':exports,'limitations':['bearing sleeves and pins not yet structurally joined to original elevon and fixed wing','hinge axis inferred from CAD, not verified against image','clearance 0.25mm radial nominal; printing tolerance unverified','servo mounts, horns, linkages, collision sweep, loads, flight tests remain open'],'accepted':False}
open(os.path.join(R,'docs','V335_ELEVON_HINGE_HARDWARE_QA.json'),'w').write(json.dumps(out,indent=2))
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v335_ELEVON_HINGE_HARDWARE_WIP.blend'))
print('V335_EXPORTS',len(exports),'NONMANIFOLD',sum(x['nonmanifold_edges'] for x in report))
