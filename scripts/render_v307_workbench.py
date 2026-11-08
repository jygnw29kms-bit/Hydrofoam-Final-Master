import bpy,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v307_LAND_SKID_PROTOTYPES.blend'))
s=bpy.context.scene
out=os.path.join(R,'renders','v307');os.makedirs(out,exist_ok=True)
s.render.engine='BLENDER_WORKBENCH'
s.display.shading.light='STUDIO'
s.display.shading.color_type='MATERIAL'
s.display.shading.show_shadows=True
s.display.shading.show_cavity=True
s.display.shading.cavity_type='BOTH'
s.display.shading.curvature_ridge_factor=1.3
s.display.shading.curvature_valley_factor=1.2
s.display.shading.background_type='WORLD'
s.display.shading.background_color=(0.18,0.2,0.24)
s.render.resolution_x=1350;s.render.resolution_y=900;s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'
bpy.ops.object.camera_add(location=(-470,-640,340))
cam=bpy.context.object;s.camera=cam
cam.data.type='ORTHO'
def render(name,loc,scale,target=(0,0,36)):
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
 cam.data.ortho_scale=scale
 s.render.filepath=os.path.join(out,name+'.png')
 bpy.ops.render.render(write_still=True)
 print('V306_RENDER_SAVED',name)
render('assembled_iso',(-535,-650,355),695)
render('assembled_top',(0,0,840),590)
render('assembled_side',(0,-650,65),545)
render('assembled_front',(-650,0,80),535)
canopy=bpy.data.objects['02 Black canopy']
canopy.location.z+=33
render('exploded_cockpit',(-350,-430,250),510,target=(-65,0,58))
print('V306_ALL_RENDERED')
