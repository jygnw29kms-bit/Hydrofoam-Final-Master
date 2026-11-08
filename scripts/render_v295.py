import bpy,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v295_SMOOTH_HULLS.blend'))
out=os.path.join(R,'renders','v295');os.makedirs(out,exist_ok=True)
world=bpy.context.scene.world
world.use_nodes=True
bg=world.node_tree.nodes.get('Background')
bg.inputs['Color'].default_value=(0.6,0.65,0.72,1)
bg.inputs['Strength'].default_value=1.0
for o in bpy.data.objects:
 if o.type=='LIGHT' or o.type=='CAMERA':bpy.data.objects.remove(o,do_unlink=True)
def area(name,loc,power,size):
 bpy.ops.object.light_add(type='AREA',location=loc)
 l=bpy.context.object;l.name=name;l.data.energy=power;l.data.shape='DISK';l.data.size=size
 direction=Vector((0,0,35))-l.location;l.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
area('Softbox front',(-220,-280,320),18000,360)
area('Softbox rear',(220,140,300),14000,360)
bpy.ops.object.camera_add(location=(-520,-680,390))
cam=bpy.context.object
bpy.context.scene.camera=cam
def setcam(loc, target=(0,0,38),ortho=True,scale=720):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.type='ORTHO' if ortho else 'PERSP'
 if ortho:cam.data.ortho_scale=scale
s=bpy.context.scene
s.render.engine='BLENDER_EEVEE_NEXT'
s.render.resolution_x=1400;s.render.resolution_y=930;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
s.render.film_transparent=False
s.render.engine='BLENDER_EEVEE_NEXT'
s.view_settings.view_transform='AgX'
def render(name,loc,scale):
 setcam(loc,scale=scale)
 s.render.filepath=os.path.join(out,name+'.png')
 bpy.ops.render.render(write_still=True)
 print('SAVED_RENDER',name)
render('assembled_iso',(-550,-650,360),720)
render('assembled_top',(0,0,750),630)
render('assembled_side',(0,-650,70),560)
render('assembled_front',(-650,0,80),560)
print('RENDER_V295_DONE')

