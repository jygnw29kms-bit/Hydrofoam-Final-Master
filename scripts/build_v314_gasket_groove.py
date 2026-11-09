import bpy,os,json
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v313_CONTINUOUS_GASKET_WIP.blend'))
s=bpy.context.scene;c=bpy.data.collections.get('V312_WATERTIGHT_ELECTRONICS_POD_PROTOTYPE')
lid=bpy.data.objects.get('REMOVABLE_LID_150x85x3_EXPLODED');assert lid and lid.type=='MESH'
# Four overlapping cutters produce a connected rectangular groove in the lid underside.
# This is intentionally a prototype, no sealing claim.
def cutter(name,xyz,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);return o
# lid z=29, lower face 27.5; 1.0 mm groove depth from bottom, 2.8 mm groove width
for n,x,y,dx,dy in [('front',0,-377,140,2.8),('back',0,-303,140,2.8),('left',-69,-340,2.8,76.8),('right',69,-340,2.8,76.8)]:
 tool=cutter('TEMP_GROOVE_'+n,(x,y,27.6),(dx,dy,2.0))
 bpy.context.view_layer.objects.active=lid;mod=lid.modifiers.new('V314_GROOVE_'+n,'BOOLEAN');mod.operation='DIFFERENCE';mod.object=tool
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
# Position a detail camera above the exploded lid to make actual groove visible
bpy.ops.object.camera_add(location=(230,-540,230));cam=bpy.context.object
from mathutils import Vector
cam.rotation_euler=(Vector((0,-340,25))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=265;cam.data.clip_end=10000;s.camera=cam
# Hide model in detail image; only lid, enclosure and gasket remain visible
for ob in s.objects:
 if ob.type=='MESH' and ob not in list(c.objects):ob.hide_render=True
s.render.resolution_x=1400;s.render.resolution_y=1000;s.render.resolution_percentage=100
report={'version':'v314','status':'groove cut in lid underside using four Boolean operations','nominal_groove_width_mm':2.8,'nominal_groove_depth_mm':1.0,'gasket_nominal_diameter_mm':2.4,'note':'lid is exploded; seal compression cannot be inferred from illustration','blockers':['verify exact groove dimensions in real mesh','verify gasket path aligns to groove','verify continuous corner geometry and flange contact','fastener through-hole seals','cable glands','pressure immersion test','hull fit']}
open(os.path.join(R,'docs','V314_LID_GROOVE_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v314'),exist_ok=True)
s.render.filepath=os.path.join(R,'renders','v314','lid_groove_detail.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v314_LID_GROOVE_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V314_LID_GROOVE_CREATED')
