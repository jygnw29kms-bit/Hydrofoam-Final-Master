import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v320_CONTROL_HORN_BORES_WIP.blend'))
col=bpy.data.collections.new('V323_TWIN_FIN_RUDDER_PACKAGING_WIP');bpy.context.scene.collection.children.link(col)
for name in ['RUDDER_HINGE_REFERENCE','RUDDER_HORN_12P5MM_PROTOTYPE','RUDDER_PUSHROD_WIP','RUDDER_SERVO_PLACEHOLDER']:
 o=bpy.data.objects.get(name)
 if o:o.hide_render=True;o.hide_set(True)
def bounds(o):
 pts=[o.matrix_world@Vector(v) for v in o.bound_box];return [[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
def cube(name,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);return o
def rod(name,start,end,r=1.1):
 a=Vector(start);b=Vector(end);mid=(a+b)/2;v=b-a;bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=v.length,location=mid);o=bpy.context.object;o.name=name;o.rotation_euler=v.to_track_quat('Z','Y').to_euler()
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o);return o
results=[]
for side in ['Left','Right']:
 fin=bpy.data.objects['30 Tail fin '+side];bb=bounds(fin);yc=sum(bb[1])/2;z0=bb[2][0];xback=bb[0][1]
 # Distinct per-fin packaging, unlike previous nonfunctional central rudder linkage.
 servo=cube('V323_'+side+'_RUDDER_SERVO_WIP',(xback-46,yc,z0+24),(24,12,23))
 horn=cube('V323_'+side+'_RUDDER_HORN_WIP',(xback-8,yc,z0+30),(4,11,14.5))
 rod('V323_'+side+'_RUDDER_ROD_REFERENCE',(xback-34,yc,z0+24),(xback-8,yc,z0+30))
 rod('V323_'+side+'_RUDDER_HINGE_AXIS_REFERENCE',(xback,yc,z0+8),(xback,yc,z0+65),0.9)
 results.append({'side':side,'fin_world_bounds':[[round(v,2) for v in axis] for axis in bb],'servo_position':[round(v,2) for v in servo.location],'horn_position':[round(v,2) for v in horn.location],'hinge_x_assumed':round(xback,2)})
report={'version':'v323','change':'replace inaccurate central rudder control mockup with two separate twin-fin rudder linkage packaging layouts','fin_reference':results,'status':'WIP only','limitations':['fin trailing-edge x assumed from bounds; actual hinge and movable rudder geometry not yet defined','rudder surfaces not cut from fins','rods are visual alignment references not moving kinematic assemblies','servo torque, collisions, mass and sealing not verified'],'build_section_01_accepted':False}
open(os.path.join(R,'docs','V323_TWIN_RUDDER_LAYOUT_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v323'),exist_ok=True)
for o in bpy.data.objects:
 if o.type in {'MESH','CURVE'} and not o.name.startswith('RUDDER_'):o.hide_render=False
bpy.context.scene.render.filepath=os.path.join(R,'renders','v323','twin_fin_rudder_layout_iso.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v323_TWIN_RUDDER_LAYOUT_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V323_FIN_LAYOUT',json.dumps(results))
