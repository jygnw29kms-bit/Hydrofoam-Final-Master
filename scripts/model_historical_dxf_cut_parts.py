import bpy,json,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';d=json.load(open(os.path.join(R,'docs','HISTORICAL_DXF_EXTRACTED_CONTOURS_WIP.json')))
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
mat=bpy.data.materials.new('Original DXF outlines - Depron');mat.diffuse_color=(.9,.91,.83,1)
parts=[]
for i,p in enumerate(d['polygons']):
 if p['area_mm2']>100000:continue # drawing sheet outline, not a part
 coords=p['outline_mm'];pts=coords[:-1] if coords[0]==coords[-1] else coords
 if len(pts)<3:continue
 # All outlines originate directly from DXF; no guessed geometry
 curve=bpy.data.curves.new('DXF_CUT_%03d'%i,'CURVE');curve.dimensions='2D';curve.fill_mode='BOTH';curve.extrude=1.5;curve.resolution_u=2
 spline=curve.splines.new('POLY');spline.points.add(len(pts)-1)
 for j,(x,y) in enumerate(pts):spline.points[j].co=(x,y,0,1)
 spline.use_cyclic_u=True
 ob=bpy.data.objects.new('DXF_cut_%03d_area_%dmm2'%(i,p['area_mm2']),curve);bpy.context.collection.objects.link(ob);curve.materials.append(mat);parts.append(ob)
# note nested contours may include holes; no production cut validation yet
bpy.ops.object.camera_add(location=(0,0,2800));cam=bpy.context.object;cam.rotation_euler=(0,0,0);cam.rotation_euler=(Vector((0,0,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=2000;cam.data.clip_end=10000
scene=bpy.context.scene;scene.camera=cam;scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.display.shading.background_type='WORLD';scene.display.shading.background_color=(.17,.19,.22);scene.render.resolution_x=1400;scene.render.resolution_y=1600;scene.render.resolution_percentage=100
os.makedirs(os.path.join(R,'renders','historical_dxf'),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Historical_Hydrofoam_DXF_ORIGINAL_CONTOURS_WIP.blend'))
scene.render.filepath=os.path.join(R,'renders','historical_dxf','dxf_cut_parts_layout.png');bpy.ops.render.render(write_still=True)
print('REAL_DXF_CONTOURS',len(parts))

