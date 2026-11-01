import bpy, os
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; blend=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v91_IDENTITY.blend'); out=os.path.join(ROOT,'renders','v91','master_hero.png'); os.makedirs(os.path.dirname(out),exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=blend)
scene=bpy.context.scene;scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=1600;scene.render.resolution_y=1000;scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
sh=scene.display.shading;sh.light='STUDIO';sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.show_object_outline=True;sh.background_type='VIEWPORT';sh.background_color=(0.98,0.98,0.98)
for o in list(bpy.data.objects):
 if o.type in {'LIGHT','CAMERA'} or o.name=='Plane': bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.object.camera_add(location=(-460,-220,360));cam=bpy.context.object;scene.camera=cam;target=Vector((225,0,33));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=58
scene.render.filepath=out;bpy.ops.render.render(write_still=True);print('V90_HERO')



