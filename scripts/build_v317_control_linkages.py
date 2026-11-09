import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v314_LID_GROOVE_WIP.blend'))
s=bpy.context.scene;c=bpy.data.collections.new('V317_AILERON_RUDDER_LINKAGE_PACKAGING_WIP');s.collection.children.link(c)
def material(n,rgb):
 m=bpy.data.materials.new(n);m.diffuse_color=(*rgb,1);return m
orange=material('v317 horn orange',(.98,.38,.04));metal=material('v317 pushrod steel',(.65,.72,.76));dark=material('v317 servo placeholder',(.1,.12,.14))
def box(n,p,dim,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=p);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for co in list(o.users_collection):co.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(ma);return o
def rod(n,a,b,r=1.1):
 d=Vector(b)-Vector(a);mid=(Vector(a)+Vector(b))/2
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=d.length,location=mid);o=bpy.context.object;o.name=n;o.rotation_euler=d.to_track_quat('Z','Y').to_euler()
 for co in list(o.users_collection):co.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(metal);return o
# Explicit design intent: dual independent aileron servos, one rudder servo.
# Positions are packaging guesses pending actual hinge-axis/throw measurements.
for side,sign in [('LEFT',-1),('RIGHT',1)]:
 y=sign*180
 box(side+'_AILERON_SERVO_PLACEHOLDER',(100,y,36),(24,12,23),dark)
 box(side+'_AILERON_HORN_PLACEHOLDER',(151,y,35),(4,9,18),orange)
 rod(side+'_AILERON_PUSHROD_WIP',(112,y,43),(150,y,43))
 box(side+'_AILERON_HINGE_AXIS_REFERENCE',(157,y,30),(35,2,2),metal)
box('RUDDER_SERVO_PLACEHOLDER',(185,0,55),(24,12,23),dark)
box('RUDDER_HORN_PLACEHOLDER',(227,0,84),(4,11,17),orange)
rod('RUDDER_PUSHROD_WIP',(196,0,61),(227,0,84))
box('RUDDER_HINGE_REFERENCE',(234,0,80),(2,2,60),metal)
# camera showing top/aft surface, preserve base geometry and hide detached pod/foil experiments
for name in ['V311_DETACHABLE_FOIL_CASSETTE_PROTOTYPE','V312_WATERTIGHT_ELECTRONICS_POD_PROTOTYPE']:
 co=bpy.data.collections.get(name)
 if co:co.hide_render=True
for o in s.objects:
 if o.type in ('MESH','CURVE'):o.hide_render=False
bpy.ops.object.camera_add(location=(620,-620,680));cam=bpy.context.object;cam.rotation_euler=(Vector((30,0,35))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=780;cam.data.clip_end=10000;s.camera=cam
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.render.resolution_x=1500;s.render.resolution_y=1000;s.render.resolution_percentage=100
report={'version':'v317','status':'WIP control-linkage packaging, NOT kinematically validated','aileron':'two independent servo placeholders, symmetric horn and pushrod references','rudder':'one servo placeholder, horn and pushrod reference','critical_blockers':['measure true aileron and rudder hinge axes','verify each pushrod clears airframe at full travel','determine linkage mechanical advantage and control throw','size servo torque from aerodynamic hinge moments','select water-protected servo and sealed linkage exits','printable horns with reinforced pivot bores','check CG impact, wiring and receiver mixing','rudder linkage may require redesign to avoid vertical fin interference'],'modes':'LAND+WATER+AIR still unverified'}
open(os.path.join(R,'docs','V317_CONTROL_LINKAGE_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v317'),exist_ok=True);s.render.filepath=os.path.join(R,'renders','v317','ailerons_rudder_linkages_iso.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v317_CONTROL_LINKAGES_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V317_LINKAGE_OBJECTS',len(c.objects))
