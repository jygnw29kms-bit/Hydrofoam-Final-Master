"""Build real printable twin elevon servo tray and control-horn prototype meshes."""
import bpy,bmesh,json,math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v337_FIVE_KNUCKLE_ELEVONS_WIP.blend'))
col=bpy.data.collections.new('V338_ELEVON_SERVO_AND_HORN_PROTOTYPES')
bpy.context.scene.collection.children.link(col)
results=[]
def move_to_col(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
def cube(name,loc,scale):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
 o=bpy.context.object;o.name=name
 o.dimensions=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 move_to_col(o)
 return o
def cylinder(name,loc,radius,depth):
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=depth,location=loc)
 o=bpy.context.object;o.name=name;move_to_col(o);return o
def subtract(o,cut):
 bpy.context.view_layer.objects.active=o
 m=o.modifiers.new('precision_cut','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=cut
 bpy.ops.object.modifier_apply(modifier=m.name)
 bpy.data.objects.remove(cut,do_unlink=True)
def manifold(o):
 bm=bmesh.new();bm.from_mesh(o.data);n=sum(not e.is_manifold for e in bm.edges);bm.free();return n
for side,sign in [('Left',-1),('Right',1)]:
 # Reference station is within the elevon root region, NOT a verified servo bay.
 y=sign*94
 tray=cube('V338_'+side+'_SERVO_TRAY_WIP',(143,y,19),(29,17,4))
 # Servo body aperture: 23 x 12 mm. Clearance and material are provisional.
 cut=cube('TEMP_APERTURE',(143,y,19),(23,12,8))
 subtract(tray,cut)
 # Horn: printable flat triangular-like lever from pivot to linkage hole.
 horn=cube('V338_'+side+'_ELEVON_HORN_WIP',(183,y,28.8),(4,20,3))
 pivot=cylinder('TEMP_PIVOT',(183,y-sign*6,28.8),1.3,8)
 subtract(horn,pivot)
 link=cylinder('TEMP_LINK',(183,y+sign*6,28.8),1.1,8)
 subtract(horn,link)
 for o in (tray,horn):
  results.append({'side':side,'part':o.name,'nonmanifold_edges':manifold(o),'vertices':len(o.data.vertices)})
outdir=root/'stl/v338';outdir.mkdir(parents=True,exist_ok=True)
for o in col.objects:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.wm.stl_export(filepath=str(outdir/(o.name+'.stl')),export_selected_objects=True,apply_modifiers=True)
report={'version':'v338','stage':'printable elevon servo-tray and control-horn geometry prototypes','parts':results,'servo_aperture_mm':[23,12],'horn_holes_mm':[2.6,2.2],'accepted':False,'blocking':['servo geometry and screw mounts not matched to selected hardware','parts not yet structurally united to existing wing/elevon meshes','no pushrod, load, articulation, or clearance validation','visual master image comparison not accepted','land water air modes untested']}
(root/'docs/V338_ELEVON_SERVO_HORN_PROTOTYPES_QA.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v338_SERVO_HORN_PROTOTYPES_WIP.blend'))
print('V338_REPORT',json.dumps(report))
