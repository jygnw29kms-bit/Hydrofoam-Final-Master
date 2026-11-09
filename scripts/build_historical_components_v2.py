import bpy,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Historical_Hydrofoam_DIMENSIONAL_BLOCKOUT_WIP.blend'))
s=bpy.context.scene
collections={}
for key in ('SCHWIMMER','DECK','RUDER','ANTRIEB'):
 c=bpy.data.collections.new('HISTORICAL_'+key);s.collection.children.link(c);collections[key]=c
for o in list(s.objects):
 if o.type!='MESH':continue
 n=o.name.lower()
 k='SCHWIMMER' if ('float' in n or 'keel' in n or 'side fin' in n) else 'RUDER' if ('elevon' in n) else 'ANTRIEB' if ('motor' in n or 'prop' in n or 'pylon' in n) else 'DECK'
 for c in list(o.users_collection):c.objects.unlink(o)
 collections[k].objects.link(o)
# Independent hinge axis and two visual control horns for the elevons
black=bpy.data.materials.get('Carbon reinforcement')
for side in (-1,1):
 bpy.ops.mesh.primitive_cylinder_add(vertices=20,radius=1.6,depth=155,location=(side*120,142,21),rotation=(0,math.pi/2,0))
 o=bpy.context.object;o.name=f'RUDER hinge axle {side}';o.data.materials.append(black)
 for c in list(o.users_collection):c.objects.unlink(o)
 collections['RUDER'].objects.link(o)
 bpy.ops.mesh.primitive_cube_add(size=1,location=(side*110,164,31));o=bpy.context.object;o.name=f'RUDER control horn placeholder {side}';o.dimensions=(3,4,20);bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(black)
 for c in list(o.users_collection):c.objects.unlink(o)
 collections['RUDER'].objects.link(o)
# save separate component collections into a working assembly
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Historical_Hydrofoam_COMPONENT_ASSEMBLY_v2_WIP.blend'))
out=os.path.join(R,'renders','historical_components_v2');os.makedirs(out,exist_ok=True)
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.display.shading.background_color=(.19,.22,.26);s.render.resolution_x=1400;s.render.resolution_y=950;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
cam=s.camera
if cam is None:
 bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam
cam.data.type='ORTHO'
def render(name,loc,scale,only=None):
 for k,c in collections.items():
  c.hide_render=bool(only and k!=only)
 cam.location=loc;cam.rotation_euler=(Vector((0,0,22))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=os.path.join(out,name+'.png');bpy.ops.render.render(write_still=True);print('RENDERED',name)
render('01_schwimmer',(540,-670,430),750,'SCHWIMMER')
render('02_deck',(500,-650,490),750,'DECK')
render('03_ruder',(480,-570,440),730,'RUDER')
render('04_assembled',(650,-800,600),820)
print('COMPONENTS',[(k,len(c.objects)) for k,c in collections.items()])
