"""Twin elevon pushrod and clevis mockup, dimensional QA only; not mechanically accepted."""
import bpy,bmesh,json,math
from mathutils import Vector
from pathlib import Path
root=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v338_SERVO_HORN_PROTOTYPES_WIP.blend'))
col=bpy.data.collections.new('V339_ELEVON_PUSHROD_PROTOTYPES')
bpy.context.scene.collection.children.link(col)
report=[]
def rod(name,start,end,radius):
 a,b=Vector(start),Vector(end);delta=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=radius,depth=delta.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler()
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
 bm=bmesh.new();bm.from_mesh(o.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
 return o,round(delta.length,3),bad
for side,sign in [('Left',-1),('Right',1)]:
 y=sign*94
 # The tray and horn geometry is provisional, so rod endpoints are CAD-only reference positions.
 servo=(143,y+sign*6,22)
 horn=(183,y+sign*6,28.8)
 o,length,bad=rod(f'V339_{side}_ELEVON_PUSHROD_REFERENCE_WIP',servo,horn,1.0)
 report.append({'side':side,'object':o.name,'center_to_center_mm':length,'rod_diameter_mm':2.0,'nonmanifold_edges':bad,'endpoint_status':'unverified provisional coordinates'})
outdir=root/'stl/v339';outdir.mkdir(parents=True,exist_ok=True)
for o in col.objects:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 bpy.ops.wm.stl_export(filepath=str(outdir/(o.name+'.stl')),export_selected_objects=True)
result={'version':'v339','purpose':'symmetric CAD reference rods for later verified mechanical linkages','parts':report,'accepted':False,'blockers':['servo output arm and horn pivot not located on real selected hardware','rod ends not joined to bearings or clevises','motion and collision sweep not verified','servo trays and hinges not united to original wing/elevon','no master photo match or land-water-air proof']}
(root/'docs/V339_ELEVON_PUSHROD_REFERENCE_QA.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend'))
print('V339',json.dumps(result))
