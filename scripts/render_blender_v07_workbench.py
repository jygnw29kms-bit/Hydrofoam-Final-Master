import bpy, os
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
stl=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v07_MASTER_BLENDED_assembly.stl')
out=os.path.join(ROOT,'renders','v07'); os.makedirs(out,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
try: bpy.ops.wm.stl_import(filepath=stl)
except: bpy.ops.import_mesh.stl(filepath=stl)
obj=bpy.context.selected_objects[0]
corners=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
mn=Vector((min(c.x for c in corners),min(c.y for c in corners),min(c.z for c in corners)))
mx=Vector((max(c.x for c in corners),max(c.y for c in corners),max(c.z for c in corners)))
obj.location-=(mn+mx)/2
bpy.ops.object.camera_add(); cam=bpy.context.object; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=1800; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
sh=scene.display.shading; sh.light='STUDIO'; sh.color_type='SINGLE'; sh.single_color=(0.88,0.32,0.06)
sh.show_shadows=True; sh.show_cavity=True; sh.cavity_type='BOTH'; sh.curvature_ridge_factor=2.0; sh.curvature_valley_factor=1.5
sh.show_object_outline=True; sh.background_type='VIEWPORT'; sh.background_color=(0.96,0.96,0.96)
def render_persp(name,loc,lens):
    cam.data.type='PERSP'; cam.location=Vector(loc); cam.data.lens=lens
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(out,name); bpy.ops.render.render(write_still=True)
def render_ortho(name,loc,scale):
    cam.data.type='ORTHO'; cam.data.ortho_scale=scale; cam.location=Vector(loc)
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(out,name); bpy.ops.render.render(write_still=True)
render_persp('assembled_iso.png',(620,-620,360),62)
render_ortho('assembled_top.png',(0,0,820),560)
render_ortho('assembled_side.png',(0,-820,105),520)
render_ortho('assembled_front.png',(-820,0,105),520)
print('RENDERED_V06',out)
