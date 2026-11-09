import bpy,os,json,math
from mathutils import Vector,Matrix
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v331_HINGE_MOUNT_BRIDGES_WIP.blend'))
coll=bpy.data.collections.new('V333_MASTER_ELEVON_ARTICULATION_WIP');bpy.context.scene.collection.children.link(coll)
qa=[]
for side,sgn in [('Left',-1),('Right',1)]:
 surf=bpy.data.objects['24 Elevon '+side];trim=bpy.data.objects['25 Orange elevon trim '+side]
 # Axis along actual master mesh stations near the inboard trailing-edge sweep.
 a=Vector((175,sgn*54,28.8));b=Vector((174,sgn*162,28.8));direction=(b-a).normalized();center=(a+b)/2
 rig=bpy.data.objects.new('V333_'+side+'_ELEVON_PIVOT',None);coll.objects.link(rig);rig.empty_display_type='ARROWS';rig.empty_display_size=8;rig.location=center
 # Local Z is the swept hinge axis, so local-Z rotation actuates the existing surfaces.
 rig.rotation_mode='QUATERNION';rig.rotation_quaternion=Vector((0,0,1)).rotation_difference(direction)
 for obj in (surf,trim):
  world=obj.matrix_world.copy();obj.parent=rig;obj.matrix_parent_inverse=rig.matrix_world.inverted();obj.matrix_world=world
 for frame,angle in [(1,0),(20,math.radians(15)),(40,math.radians(-15)),(60,0)]:
  rig.rotation_mode='QUATERNION';base=Vector((0,0,1)).rotation_difference(direction);from mathutils import Quaternion
  rig.rotation_quaternion=base@Quaternion((0,0,1),angle);rig.keyframe_insert(data_path='rotation_quaternion',frame=frame)
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=0.9,depth=(b-a).length,location=center);pin=bpy.context.object;pin.name='V333_'+side+'_SWEPT_HINGE_AXIS_REFERENCE';pin.rotation_mode='QUATERNION';pin.rotation_quaternion=Vector((0,0,1)).rotation_difference(direction)
 for c in list(pin.users_collection):c.objects.unlink(pin)
 coll.objects.link(pin);pin.hide_render=True
 qa.append({'side':side,'existing_surface':surf.name,'existing_trim':trim.name,'hinge_reference_a':list(a),'hinge_reference_b':list(b),'animation_frames':{'1':0,'20':15,'40':-15,'60':0},'limitation':'reference hinge inferred from mesh stations; not cut or structurally joined; ±15 degrees is demonstration only'})
bpy.context.scene.frame_set(1)
report={'version':'v333','source':'actual Final Master CAD elevon mesh and orange trim, unchanged contours','results':qa,'status':'articulated non-destructive rig and keyframes; not flight-ready','open':['hinge physical cut and knuckles','servo mounts and horns','moving geometry interference and linkage sweep','pixel-aligned comparison to exact master top view']}
open(os.path.join(R,'docs','V333_MASTER_ELEVON_ARTICULATION_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v333'),exist_ok=True)
bpy.context.scene.render.filepath=os.path.join(R,'renders','v333','master_elevon_articulation_iso.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V333_ELEVON_RIGS',json.dumps(qa))
