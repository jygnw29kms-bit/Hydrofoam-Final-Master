import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v310_FOIL_CLEARANCE_STUDY_WIP.blend'))
s=bpy.context.scene
old=bpy.data.collections.get('V310_FOIL_LAND_CLEARANCE_STUDY_WIP')
if old:
 for o in list(old.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(old)
c=bpy.data.collections.new('V311_DETACHABLE_FOIL_CASSETTE_PROTOTYPE');s.collection.children.link(c)
def material(name,rgb):
 m=bpy.data.materials.new(name);m.diffuse_color=(*rgb,1);return m
cyan=material('V311 detachable mounting hardware',(.08,.66,.8));orange=material('V311 removable foil',(.95,.42,.05));black=material('V311 wear insert',(.08,.09,.1))
def block(name,pos,dimensions,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=pos);o=bpy.context.object;o.name=name;o.dimensions=dimensions;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for col in list(o.users_collection):col.objects.unlink(o)
 c.objects.link(o);o.data.materials.append(mat);return o
# Prototype is spatially separate from hull: mounting geometry not falsely claimed as fitted.
# Each foil cassette has a vertical removable mast, top plate, 2 mechanical pin placeholders, foil, and skid insert.
for side,sign in [('PORT',-1),('STARBOARD',1)]:
 x=sign*180;y=-220;z=-65
 block(side+'_FOIL_BLADE_WIP',(x,y,z),(125,42,5),orange)
 block(side+'_REMOVABLE_MAST_WIP',(x,y,z+24),(10,12,44),cyan)
 block(side+'_MOUNTING_TOP_PLATE_WIP',(x,y,z+47),(55,35,5),cyan)
 block(side+'_SKID_WEAR_INSERT_WIP',(x,y,z+53),(55,14,4),black)
 for dy in [-10,10]:
  bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=3,depth=8,location=(x,y+dy,z+51))
  o=bpy.context.object;o.name=side+'_PIN_PLACEHOLDER_'+str(dy)
  for col in list(o.users_collection):col.objects.unlink(o)
  c.objects.link(o);o.data.materials.append(cyan)
# Existing main assembly stays unchanged. Prototypes are intentionally detached in staging area.
report={'version':'v311','status':'prototype only; NOT dimensioned or flight approved','assembly':'two removable foil cassette subassemblies','per_side':['foil blade','mast','mounting plate','wear insert','two pin placeholders'],'manufacturing_blockers':['actual hull hardpoint geometry','scale calibration','structural pin shear sizing','water seal','foil hydrodynamic sizing','ground clearance verification','P2S printable split and tolerances'],'land_mode':'foil cassettes removed; no deployed foil permitted','note':'detached visualization only; no functional lock mechanism validated'}
open(os.path.join(R,'docs','V311_REMOVABLE_FOIL_CASSETTE_QA.json'),'w').write(json.dumps(report,indent=2))
# Camera shows model and detached parts together
cam=s.camera;cam.data.clip_end=10000;cam.data.ortho_scale=1150
s.render.filepath=os.path.join(R,'renders','v311','removable_foil_cassettes_iso.png');os.makedirs(os.path.dirname(s.render.filepath),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v311_REMOVABLE_FOIL_CASSETTES_WIP.blend'))
bpy.ops.render.render(write_still=True)
print('V311_DONE',len(c.objects))
