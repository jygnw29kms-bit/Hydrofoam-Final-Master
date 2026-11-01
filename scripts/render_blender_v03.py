import bpy, os
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
stl=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v03_MASTER_FORM_assembly.stl')
out=os.path.join(ROOT,'renders','v03'); os.makedirs(out,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
try: bpy.ops.wm.stl_import(filepath=stl)
except: bpy.ops.import_mesh.stl(filepath=stl)
obj=bpy.context.selected_objects[0]
corners=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
mn=Vector((min(c.x for c in corners),min(c.y for c in corners),min(c.z for c in corners)))
mx=Vector((max(c.x for c in corners),max(c.y for c in corners),max(c.z for c in corners)))
obj.location-=(mn+mx)/2
mat=bpy.data.materials.new('Body'); mat.diffuse_color=(1.0,0.42,0.08,1.0); obj.data.materials.append(mat)
bpy.ops.mesh.primitive_plane_add(size=1400, location=(0,0,-80)); plane=bpy.context.object
pm=bpy.data.materials.new('Floor'); pm.diffuse_color=(0.985,0.985,0.985,1.0); plane.data.materials.append(pm)
bpy.ops.object.camera_add(); cam=bpy.context.object; bpy.context.scene.camera=cam
for loc,energy,size in [((300,-350,420),2800,300),((-260,220,280),1800,260),((0,0,500),1200,350)]:
    bpy.ops.object.light_add(type='AREA', location=loc); l=bpy.context.object; l.data.energy=energy; l.data.size=size
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=1800; scene.render.resolution_y=1100; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'; scene.world.color=(1.0,1.0,1.0)
scene.view_settings.look='AgX - Medium High Contrast'; scene.view_settings.exposure=1.0

def render(name,loc,lens):
    cam.location=Vector(loc); cam.data.lens=lens
    cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=os.path.join(out,name); bpy.ops.render.render(write_still=True)
render('assembled_iso.png',(560,-520,340),60)
render('assembled_top.png',(0,0,760),58)
render('assembled_side.png',(0,-760,120),60)
render('assembled_front.png',(-760,0,120),60)
print('RENDERED_V02',out)



