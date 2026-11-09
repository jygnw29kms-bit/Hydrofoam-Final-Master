import bpy,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
white=bpy.data.materials.new('Depron 3mm white');white.diffuse_color=(.88,.9,.86,1)
black=bpy.data.materials.new('Carbon reinforcement');black.diffuse_color=(.055,.07,.08,1)
orange=bpy.data.materials.new('Temporary reference orange');orange.diffuse_color=(.95,.31,.035,1)
def plate(name,points,z,thick,mat):
 n=len(points);verts=[(x,y,z-thick/2) for x,y in points]+[(x,y,z+thick/2) for x,y in points]
 faces=[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
 mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update();obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);obj.data.materials.append(mat);return obj
def cube(name,loc,scale,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(mat);return o
# Reconstruction blockout, proportions inferred from 600x400 reported dimensions, NOT a traced plan
plate('01 main wing / flat foam deck', [(-170,-160),(170,-160),(200,-15),(165,125),(-165,125),(-200,-15)], 18,3,white)
plate('02 center spine', [(-32,-295),(32,-295),(52,-170),(44,180),(18,300),(-18,300),(-44,180),(-52,-170)],24,3,white)
for side in (-1,1):
 x=side*145
 plate(f'03 side float {side} flat deck',[(x-30,-295),(x+30,-295),(x+34,110),(x+15,275),(x-15,275),(x-34,110)],7,3,white)
 cube(f'04 float keel {side}',(x,-25,-12),(6,480,34),white)
 cube(f'05 vertical side fin {side}',(x,190,54),(3,100,85),white)
 plate(f'06 aft elevon {side}',[(side*45,140),(side*195,140),(side*185,220),(side*45,220)],20,3,orange)
 cube(f'07 front spar {side}',(side*92,-75,21),(175,3,3),black)
cube('08 aft carbon spar',(0,140,22),(380,3,3),black)
cube('09 motor pylon',(0,195,85),(9,9,125),black)
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=18,depth=16,location=(0,195,151),rotation=(math.pi/2,0,0));bpy.context.object.name='10 pusher motor placeholder';bpy.context.object.data.materials.append(black)
for a in (0,math.pi/2):
 blade=cube('11 pusher prop visual', (0,212,151),(8,3,160),black);blade.rotation_euler[1]=a
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.background_type='WORLD';s.display.shading.background_color=(.19,.22,.26);s.render.resolution_x=1400;s.render.resolution_y=950;s.render.resolution_percentage=100
bpy.ops.object.camera_add(location=(680,-820,620));cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
out=os.path.join(R,'renders','historical_blockout');os.makedirs(out,exist_ok=True)
def render(name,loc,scale):
 cam.location=loc;cam.rotation_euler=(Vector((0,0,24))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale;s.render.filepath=os.path.join(out,name+'.png');bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Historical_Hydrofoam_DIMENSIONAL_BLOCKOUT_WIP.blend'))
render('assembled_iso',(650,-800,600),820)
render('assembled_top',(0,0,900),750)
render('assembled_side',(900,0,140),730)
print('HISTORICAL_DIMENSIONAL_BLOCKOUT_RENDERED')
