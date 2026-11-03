import bpy, os
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
blend=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v238_PLANING_SPONSONS.blend')
out=os.path.join(ROOT,'renders','v238'); os.makedirs(out,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=blend)
objs=[o for o in bpy.context.scene.objects if o.type=='MESH']
coords=[]
for o in objs:
 for c in o.bound_box: coords.append(o.matrix_world @ Vector(c))
mn=Vector((min(c.x for c in coords),min(c.y for c in coords),min(c.z for c in coords)))
mx=Vector((max(c.x for c in coords),max(c.y for c in coords),max(c.z for c in coords)))
ctr=(mn+mx)/2
for o in objs: o.location-=ctr
bpy.ops.object.camera_add(); cam=bpy.context.object; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'; scene.render.resolution_x=1600; scene.render.resolution_y=1000; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'
sh=scene.display.shading; sh.light='STUDIO'; sh.color_type='MATERIAL'; sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.show_object_outline=True; sh.background_type='VIEWPORT'; sh.background_color=(0.97,0.97,0.97)
def aim(loc):
 cam.location=Vector(loc); cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
def save(name): scene.render.filepath=os.path.join(out,name); bpy.ops.render.render(write_still=True)
cam.data.type='PERSP'; cam.data.lens=62; aim((650,-650,420)); save('assembled_iso.png')
cam.data.type='ORTHO'; cam.data.ortho_scale=560; aim((0,0,900)); save('assembled_top.png')
cam.data.ortho_scale=520; aim((0,-900,0)); save('assembled_side.png')
cam.data.ortho_scale=520; aim((-900,0,0)); save('assembled_front.png')
print('RENDERED_V238')


