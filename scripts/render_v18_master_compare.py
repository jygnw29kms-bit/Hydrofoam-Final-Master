import bpy, os, glob, math
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
PARTS=os.path.join(ROOT,'print','v18_parts'); OUT=os.path.join(ROOT,'renders','v18'); os.makedirs(OUT,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(name,rgba,metal=0.0,rough=.35):
 m=bpy.data.materials.new(name); m.diffuse_color=rgba; m.metallic=metal; m.roughness=rough; return m
white=mat('White',(0.82,0.84,0.86,1),0,.42); orange=mat('Orange',(1.0,.18,.015,1),0,.35); dark=mat('Dark',(.018,.022,.028,1),.15,.22); black=mat('Black',(.025,.025,.025,1),0,.5)
objs=[]
for fp in glob.glob(os.path.join(PARTS,'*.stl')):
    name=os.path.splitext(os.path.basename(fp))[0]
    if name.startswith('Hinge_') or name=='BatteryRails': continue
    bpy.ops.wm.stl_import(filepath=fp); o=bpy.context.selected_objects[0]; o.name=name; objs.append(o)
    if name=='Canopy': o.data.materials.append(dark)
    elif name.startswith('Skid_'): o.data.materials.append(black)
    elif name.startswith('OuterControl_') or name.startswith('Pitch_'): o.data.materials.append(orange)
    else: o.data.materials.append(white)
# orange master accents as thin visual overlays, not structural geometry
# nose caps on sponsons + center nose; simple projected wedges
for y in (-137,137):
    bpy.ops.mesh.primitive_cube_add(location=(36,y,41),scale=(28,22,1.0)); a=bpy.context.object; a.name='OrangeNose'; a.data.materials.append(orange); a.rotation_euler[1]=math.radians(-5)
# camera and lights
mins=Vector((1e9,1e9,1e9)); maxs=Vector((-1e9,-1e9,-1e9))
for o in objs:
 for c in o.bound_box:
  w=o.matrix_world@Vector(c); mins.x=min(mins.x,w.x); mins.y=min(mins.y,w.y); mins.z=min(mins.z,w.z); maxs.x=max(maxs.x,w.x); maxs.y=max(maxs.y,w.y); maxs.z=max(maxs.z,w.z)
ctr=(mins+maxs)/2
for o in bpy.context.scene.objects:
 if o.type=='MESH': o.location-=ctr
bpy.ops.object.camera_add(); cam=bpy.context.object; bpy.context.scene.camera=cam; cam.location=(540,-520,265); cam.data.lens=58; cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler()
for loc,energy,size in [((250,-300,450),1700,220),((-250,150,300),1000,180),((0,250,420),900,200)]:
 bpy.ops.object.light_add(type='AREA', location=loc); l=bpy.context.object; l.data.energy=energy; l.data.shape='DISK'; l.data.size=size
scene=bpy.context.scene; scene.render.engine='BLENDER_EEVEE_NEXT'; scene.render.resolution_x=1800; scene.render.resolution_y=1050; scene.render.resolution_percentage=100; scene.render.image_settings.file_format='PNG'; scene.world.color=(.78,.80,.82); scene.view_settings.look='AgX - Medium High Contrast'
# neutral floor
bpy.ops.mesh.primitive_plane_add(size=1500,location=(0,0,-75)); pl=bpy.context.object; pl.data.materials.append(mat('Floor',(.48,.5,.52,1),0,.8))
scene.render.filepath=os.path.join(OUT,'master_compare_hero.png'); bpy.ops.render.render(write_still=True)
print('MASTER_COMPARE_RENDERED')