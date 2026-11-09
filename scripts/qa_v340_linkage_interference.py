"""Non-destructive BVH interference audit of v339 linkage prototypes against CAD mesh."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parents[1]
scene_path=root/'cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend'
bpy.ops.wm.open_mainfile(filepath=str(scene_path))
sha=hashlib.sha256((root/'reference/FINAL_MASTER_ORIGINAL.jpeg').read_bytes()).hexdigest()
assert sha=='a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd'
deps=bpy.context.evaluated_depsgraph_get()
parts=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('V339_') and 'PUSHROD' in o.name]
assert len(parts)==2, 'Expected symmetric twin linkage references'
targets=[o for o in bpy.data.objects if o.type=='MESH' and o not in parts and not o.hide_render and not o.name.startswith('TEMP_')]
def tree(obj):
 try:return BVHTree.FromObject(obj,deps,epsilon=0.00001)
 except Exception:return None
results=[]
for p in parts:
 bp=tree(p)
 hits=[]
 if bp:
  for t in targets:
   bt=tree(t)
   if bt:
    overlap=bp.overlap(bt)
    if overlap:hits.append({'object':t.name,'triangle_pairs':len(overlap)})
 results.append({'rod':p.name,'intersecting_meshes':len(hits),'hits':sorted(hits,key=lambda x:-x['triangle_pairs'])[:30]})
report={'version':'v340','source_blend':str(scene_path.relative_to(root)),'reference_sha256':sha,'test':'Blender BVH surface triangle overlap; not a proof of positive physical clearance','linkages':results,'accepted':False,'limitations':['reference pushrods are provisional, not connected with clevises','BVH overlap is a screening method only and can miss contained solids','no angle sweep or servo travel kinematics','no structural attachment of hinges, trays or horns','no image-registered master comparison or land-water-air acceptance']}
(root/'docs/V340_LINKAGE_INTERFERENCE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('V340_AUDIT',json.dumps({'rods':len(parts),'intersections':[r['intersecting_meshes'] for r in results],'accepted':False}))
