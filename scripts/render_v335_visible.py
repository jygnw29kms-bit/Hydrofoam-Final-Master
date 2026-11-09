"""Bright diagnostic render from the unchanged v335 Blender CAD assembly."""
import bpy
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[1]
scene=bpy.context.scene
objects=[o for o in scene.objects if o.type=='MESH' and not o.hide_render and not o.hide_get()]
assert objects
# Exclude hidden construction helpers and extreme outlier bounds.
major=[o for o in objects if not any(w in o.name.lower() for w in ('camera','light','reference','background'))]
pts=[o.matrix_world @ Vector(c) for o in major for c in o.bound_box]
lo=Vector(tuple(min(p[i] for p in pts) for i in range(3)))
hi=Vector(tuple(max(p[i] for p in pts) for i in range(3)))
center=(lo+hi)*0.5
span=max((hi-lo).x,(hi-lo).y,(hi-lo).z)
# Workbench renders true object surfaces with studio illumination, no missing lights.
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.studio_light='paint.sl'
scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True
scene.display.shading.show_cavity=True
scene.display.shading.cavity_type='BOTH'
scene.display.shading.curvature_ridge_factor=1.5
scene.display.shading.curvature_valley_factor=1.1
scene.display.shading.background_type='WORLD'
scene.display.shading.background_color=(0.08,0.10,0.13)
# Force a readable white/orange diagnostic palette without altering the saved CAD.
for o in objects:
    n=o.name.lower()
    orange=any(t in n for t in ('orange','trim','stripe'))
    o.color=(0.98,0.35,0.05,1) if orange else (0.88,0.92,0.96,1)
scene.display.shading.color_type='OBJECT'
cam_data=bpy.data.cameras.new('VISIBLE_QA_CAMERA')
cam=bpy.data.objects.new('VISIBLE_QA_CAMERA',cam_data)
scene.collection.objects.link(cam)
cam.location=center+Vector((span*1.4,-span*1.5,span*1.15))
cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
cam_data.type='ORTHO'
cam_data.ortho_scale=span*1.65
scene.camera=cam
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
out=root/'renders/v335/current_cad_assembly_visible.png'
scene.render.filepath=str(out)
bpy.ops.render.render(write_still=True)
print('VISIBLE_RENDER',out,out.stat().st_size,'mesh_count',len(objects),'bounds',tuple(lo),tuple(hi))
