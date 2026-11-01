import bpy, os, math, json
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
best=open(os.path.join(ROOT,'comparison','best_version.txt')).read().strip()
mapn={'v20':'v20_IDENTITY_MATCH','v21':'v21_IMAGE_DRIVEN','v22':'v22_IMAGE_FIT','v23':'v23_PROFILE_CORRECTED','v24':'v24_SECOND_PASS','v25':'v25_STATION_FIT','v26':'v26_STATION_FIT2','v27':'v27_SIDE_IMAGE_FIT','v28':'v28_CONVERGENCE','v29':'v29_BLENDED_SURFACE'}
tag=mapn.get(best,'v29_BLENDED_SURFACE')
stl=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_'+tag+'_visual.stl')
out=os.path.join(ROOT,'comparison','hero_grid');os.makedirs(out,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.wm.stl_import(filepath=stl);obj=bpy.context.selected_objects[0]
# center geometry
corn=[obj.matrix_world@Vector(c) for c in obj.bound_box];mn=Vector((min(c.x for c in corn),min(c.y for c in corn),min(c.z for c in corn)));mx=Vector((max(c.x for c in corn),max(c.y for c in corn),max(c.z for c in corn)));obj.location-=(mn+mx)/2
bpy.ops.object.camera_add();cam=bpy.context.object;bpy.context.scene.camera=cam
sc=bpy.context.scene;sc.render.engine='BLENDER_WORKBENCH';sc.render.resolution_x=700;sc.render.resolution_y=430;sc.render.resolution_percentage=100;sc.render.image_settings.file_format='PNG'
sh=sc.display.shading;sh.light='STUDIO';sh.color_type='SINGLE';sh.single_color=(1.0,.28,.03);sh.show_shadows=False;sh.show_cavity=False;sh.show_object_outline=False;sh.background_type='VIEWPORT';sh.background_color=(1,1,1)
configs=[]
idx=0
for ysign in (-1,1):
 for az in (32,40,48,56):
  for elev in (16,22,28):
   idx+=1; r=720; # nose is -X, camera at negative X
   a=math.radians(az); e=math.radians(elev)
   x=-r*math.cos(a)*math.cos(e); y=ysign*r*math.sin(a)*math.cos(e); z=r*math.sin(e)
   cam.location=(x,y,z);cam.data.lens=62;cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();fn=f'g{idx:02d}_s{ysign}_a{az}_e{elev}.png';sc.render.filepath=os.path.join(out,fn);bpy.ops.render.render(write_still=True);configs.append({'file':fn,'ysign':ysign,'az':az,'elev':elev,'lens':62})
json.dump({'best':best,'configs':configs},open(os.path.join(out,'grid.json'),'w'),indent=2)
print('GRID_DONE',best,len(configs))