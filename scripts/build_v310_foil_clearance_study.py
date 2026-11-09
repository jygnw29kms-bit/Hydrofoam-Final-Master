import bpy,os,math,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v309_GASKET_WIP.blend'))
scene=bpy.context.scene
coll=bpy.data.collections.new('V310_FOIL_LAND_CLEARANCE_STUDY_WIP');scene.collection.children.link(coll)
def mat(name,rgb):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m
orange=mat('v310 foil prototype amber',(.9,.39,.05));blue=mat('v310 strut cyan',(.02,.6,.75));ground=mat('v310 reference ground',(.22,.26,.28))
def cube(name,xyz,size,material):
 bpy.ops.mesh.primitive_cube_add(size=1,location=xyz);o=bpy.context.object;o.name=name;o.dimensions=size;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);o.data.materials.append(material);return o
# This is an isolated mechanical packaging study, not a fitted or verified flight-ready foil.
# Place reference below the assembly using evaluated object bounds, excluding cameras/lights.
zs=[]
for o in scene.objects:
 if o.type=='MESH' and o.name not in [x.name for x in coll.objects]:
  zs.extend([(o.matrix_world @ Vector(c)).z for c in o.bound_box])
base=min(zs) if zs else 0
# mm-style Blender coordinates: preliminary dimensions must be reconciled with existing model units.
# Keep all new geometry separated from production collections.
for sign in (-1,1):
 x=sign*140
 cube(('PORT' if sign<0 else 'STARBOARD')+'_FOIL_STRUT_WIP',(x,0,base-18),(8,8,36),blue)
 cube(('PORT' if sign<0 else 'STARBOARD')+'_FOIL_WIP',(x,0,base-37),(130,35,5),orange)
 cube(('PORT' if sign<0 else 'STARBOARD')+'_SKID_GROUND_PAD_REFERENCE',(x,0,base-3),(155,20,6),ground)
# An explicit land-mode interference warning marker: foils sit below skid reference and MUST retract/remove.
cube('GROUND_CONTACT_PLANE_REFERENCE',(0,0,base-7),(600,350,1),ground)
report={'version':'v310','status':'WIP conceptual mechanical packaging, not verified','reference_base_z':base,'foil_below_skid_mm_assuming_mm_units':34,'land_mode':'FAIL: deployed foils intersect ground reference; retraction/removal mandatory','geometry':'two detachable foil/strut mockups, ground plane and skid references','next':'measure v309 assembly scale and attachment hardpoints; engineer actual retractable mechanism'}
os.makedirs(os.path.join(R,'docs'),exist_ok=True)
open(os.path.join(R,'docs','V310_FOIL_CLEARANCE_STUDY.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v310'),exist_ok=True)
# frame entire scene from top-oblique with clipping robustly set
bpy.ops.object.camera_add(location=(650,-800,850));cam=bpy.context.object;cam.rotation_euler=(Vector((0,0,base))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1100;cam.data.clip_end=10000;scene.camera=cam
scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL';scene.display.shading.show_cavity=True;scene.render.resolution_x=1500;scene.render.resolution_y=1000;scene.render.resolution_percentage=100
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v310_FOIL_CLEARANCE_STUDY_WIP.blend'))
scene.render.filepath=os.path.join(R,'renders','v310','foil_clearance_study_iso.png');bpy.ops.render.render(write_still=True)
print('V310_SAVED',base)
