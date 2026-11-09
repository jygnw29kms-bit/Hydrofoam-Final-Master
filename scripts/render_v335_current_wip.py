"""Render actual v335 Blender assembly; never replace original reference."""
import bpy
from mathutils import Vector
from pathlib import Path
root = Path(__file__).resolve().parents[1]
scene = bpy.context.scene
meshes = [o for o in scene.objects if o.type == 'MESH' and not o.hide_render]
assert meshes, "No visible CAD meshes"
pts = [o.matrix_world @ Vector(corner) for o in meshes for corner in o.bound_box]
lo = Vector(tuple(min(p[i] for p in pts) for i in range(3)))
hi = Vector(tuple(max(p[i] for p in pts) for i in range(3)))
center = (lo + hi) / 2
span = max((hi-lo).x, (hi-lo).y, (hi-lo).z)
camera_data = bpy.data.cameras.new("V335_QA_CAMERA")
camera = bpy.data.objects.new("V335_QA_CAMERA", camera_data)
scene.collection.objects.link(camera)
camera.location = center + Vector((span * 1.5, -span * 1.6, span * 1.25))
direction = center - camera.location
camera.rotation_euler = direction.to_track_quat('-Z','Y').to_euler()
camera_data.type = 'ORTHO'
camera_data.ortho_scale = span * 1.8
scene.camera = camera
scene.render.engine = 'BLENDER_EEVEE_NEXT'
scene.render.resolution_x = 1440
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.world.color = (0.7,0.7,0.7)
scene.render.image_settings.file_format = 'PNG'
out = root / "renders/v335/current_cad_assembly_wip.png"
out.parent.mkdir(parents=True, exist_ok=True)
scene.render.filepath = str(out)
bpy.ops.render.render(write_still=True)
print("V335_RENDER", out, out.stat().st_size, "mesh_count",len(meshes))
