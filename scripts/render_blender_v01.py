import bpy, os, math
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
stl=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v01_assembly.stl')
out=os.path.join(ROOT,'renders')
os.makedirs(out,exist_ok=True)
# clean
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
# import STL
try:
    bpy.ops.wm.stl_import(filepath=stl)
except Exception:
    bpy.ops.import_mesh.stl(filepath=stl)
obj=bpy.context.selected_objects[0]
# center model
corners=[obj.matrix_world @ Vector(c) for c in obj.bound_box]
mn=Vector((min(c.x for c in corners),min(c.y for c in corners),min(c.z for c in corners)))
mx=Vector((max(c.x for c in corners),max(c.y for c in corners),max(c.z for c in corners)))
center=(mn+mx)/2
obj.location-=center
# material
mat=bpy.data.materials.new('Body'); mat.diffuse_color=(0.22,0.62,1.0,1.0); obj.data.materials.append(mat)
# floor
bpy.ops.mesh.primitive_plane_add(size=1200, location=(0,0,-65))
plane=bpy.context.object
pm=bpy.data.materials.new('Floor'); pm.diffuse_color=(0.93,0.94,0.96,1); plane.data.materials.append(pm)
# camera
bpy.ops.object.camera_add(); cam=bpy.context.object; bpy.context.scene.camera=cam
# light
bpy.ops.object.light_add(type='AREA', location=(250,-300,350)); key=bpy.context.object; key.data.energy=3200; key.data.shape='DISK'; key.data.size=260
bpy.ops.object.light_add(type='AREA', location=(-250,180,220)); fill=bpy.context.object; fill.data.energy=1800; fill.data.size=220
# world
bpy.context.scene.world.color=(1.0,1.0,1.0)
scene=bpy.context.scene
scene.render.engine='BLENDER_EEVEE_NEXT'
scene.render.resolution_x=1800; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG'
scene.render.film_transparent=False
scene.view_settings.look='AgX - Medium High Contrast'
scene.view_settings.exposure=2.0
scene.view_settings.gamma=1.0

def point_cam(loc, lens=52):
    cam.location=Vector(loc)
    cam.data.lens=lens
    direction=Vector((0,0,0))-cam.location
    cam.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()

def render(name,loc,lens=52):
    point_cam(loc,lens)
    scene.render.filepath=os.path.join(out,name)
    bpy.ops.render.render(write_still=True)

render('assembled_iso.png',(500,-470,330),62)
render('assembled_top.png',(0,0,720),55)
render('assembled_side.png',(0,-720,100),58)
render('assembled_front.png',(-720,0,100),58)
print('RENDERED', out)




