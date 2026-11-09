"""Hydrofoam v341: reproducible three-view CAD evidence capture (WIP only).

Run on Jens-PC:
blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend -t 4 --python scripts/audit_v341_three_view.py
This script never writes the original .blend or master JPEG.
"""
import bpy, hashlib, json
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
reference=root/'reference/FINAL_MASTER_ORIGINAL.jpeg'
expected='a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd'
digest=hashlib.sha256(reference.read_bytes()).hexdigest()
if digest!=expected:
    raise RuntimeError('MASTER SHA256 MISMATCH: no rendering or acceptance permitted')
objects=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render]
assert objects,'No visible mesh objects'
points=[o.matrix_world @ Vector(c) for o in objects for c in o.bound_box]
lo=Vector(tuple(min(p[i] for p in points) for i in range(3)))
hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
center=(lo+hi)*0.5
span=max(hi[i]-lo[i] for i in range(3))
scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.display.shading.light='STUDIO'
scene.display.shading.color_type='OBJECT'
scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD'
scene.display.shading.background_color=(0.08,0.10,0.13)
for o in objects:
    o.color=(0.95,0.42,0.09,1) if 'trim' in o.name.lower() or 'orange' in o.name.lower() else (0.87,0.91,0.95,1)
cam_data=bpy.data.cameras.new('V341_AUDIT_CAMERA')
cam=bpy.data.objects.new('V341_AUDIT_CAMERA',cam_data)
scene.collection.objects.link(cam)
cam_data.type='ORTHO'
scene.camera=cam
scene.render.resolution_x=1600
scene.render.resolution_y=1000
scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
output=root/'renders/v341'
output.mkdir(parents=True,exist_ok=True)
views={'top':(0,0,1),'side':(0,-1,0.01),'perspective':(1.35,-1.5,1.15)}
rendered={}
for name,offset in views.items():
    direction=Vector(offset).normalized()
    cam.location=center+direction*span*2.2
    cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler()
    cam_data.ortho_scale=span*(1.75 if name=='perspective' else 1.45)
    target=output/(name+'_cad_wip.png')
    scene.render.filepath=str(target)
    bpy.ops.render.render(write_still=True)
    rendered[name]={'path':str(target.relative_to(root)).replace('\\','/'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()}
report={'version':'v341','accepted':False,'reference_sha256':digest,'source_blend':bpy.data.filepath,
        'mesh_count':len(objects),'bounds_mm':{'min':list(lo),'max':list(hi)},
        'views':rendered,'comparison':{'top':'NOT VERIFIED','side':'NOT VERIFIED','perspective':'NOT VERIFIED'},
        'limitations':['No image registration, landmark correspondence, or pixel-difference measurements','Orthographic CAD views alone do not prove photograph fidelity','No hinge/servo mechanical integration or collision acceptance','No land, water, or flight acceptance']}
(root/'docs/V341_THREE_VIEW_EVIDENCE_WIP.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('V341_EVIDENCE',json.dumps(report))
