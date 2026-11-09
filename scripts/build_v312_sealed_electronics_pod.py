import bpy,os,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v311_REMOVABLE_FOIL_CASSETTES_WIP.blend'))
s=bpy.context.scene;c=bpy.data.collections.new('V312_WATERTIGHT_ELECTRONICS_POD_PROTOTYPE');s.collection.children.link(c)
def mat(n,color):
 m=bpy.data.materials.new(n);m.diffuse_color=(*color,1);return m
white=mat('V312 PETG enclosure',(.88,.89,.85));black=mat('V312 flexible seal material NOT validated',(.03,.08,.1));cyan=mat('V312 stainless fastener placeholders',(.1,.65,.8))
def box(n,pos,dim,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=n;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for x in list(o.users_collection):x.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(ma);return o
def cut(o,tool):
 bpy.context.view_layer.objects.active=o;mod=o.modifiers.new('cut cavity','BOOLEAN');mod.operation='DIFFERENCE';mod.object=tool
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
# Prototype is staged BESIDE model, not yet fitted to central fuselage.
x,y,z=0,-340,0
shell=box('POD_BASE_150x85x40_WALL3',(x,y,z),(150,85,40),white)
cut(shell,box('CAVITY_TOOL',(x,y,z+4),(144,79,38),white))
# lid lifted to show seal geometry; four overlapping strips are NOT a validated continuous compression seal
box('REMOVABLE_LID_150x85x3_EXPLODED',(x,y,z+29),(150,85,3),white)
for label,dx,dy,w,h in [('front',0,-37,138,3),('back',0,37,138,3),('left',-69,0,3,74),('right',69,0,3,74)]:
 box('SEAL_STRIP_'+label+'_WIP',(x+dx,y+dy,z+23),(w,h,2),black)
for dx in [-61,61]:
 for dy in [-30,30]:
  box('M3_BOSS_PLACEHOLDER_%d_%d'%(dx,dy),(x+dx,y+dy,z+18),(10,10,8),white)
  bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=2.7,depth=8,location=(x+dx,y+dy,z+32));o=bpy.context.object;o.name='M3_FASTENER_PLACEHOLDER_%d_%d'%(dx,dy)
  for col in list(o.users_collection):col.objects.unlink(o)
  c.objects.link(o);o.data.materials.append(cyan)
report={'version':'v312','status':'CAD waterproofing concept; not leak-tested','design':'150x85x40 mm enclosure with 3 mm nominal walls, removable lid, four seal-strip placeholders and four fastener bosses','known_failures':['seal corners are not continuous or tested','no verified gasket compression or material','fastener holes not machined','cable glands and vent not designed','no fit check with center hull','no IP rating','no pressure immersion test'],'requirements_before_watertight_claim':['continuous perimeter groove and closed-loop gasket','measured compression and flange stiffness','threaded insert seals','cable gland penetration seals','submersion and pressure test with electronics absent']}
open(os.path.join(R,'docs','V312_WATERPROOF_POD_QA.json'),'w').write(json.dumps(report,indent=2))
cam=s.camera;cam.data.clip_end=10000;cam.data.ortho_scale=1200
os.makedirs(os.path.join(R,'renders','v312'),exist_ok=True);s.render.filepath=os.path.join(R,'renders','v312','electronics_pod_exploded_iso.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v312_ELECTRONICS_POD_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V312_POD_CREATED',len(c.objects))
