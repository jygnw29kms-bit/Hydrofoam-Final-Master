import bpy,os,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v320_CONTROL_HORN_BORES_WIP.blend'))
from collections import Counter
names=['LEFT_AILERON_HORN_PLACEHOLDER','RIGHT_AILERON_HORN_PLACEHOLDER','RUDDER_HORN_12P5MM_PROTOTYPE'];results=[]
for name in names:
 o=bpy.data.objects[name];mesh=o.data;counts=Counter()
 for e in mesh.edges:counts[e.index]=len(e.link_faces) if hasattr(e,'link_faces') else 0
 import bmesh
 bm=bmesh.new();bm.from_mesh(mesh);boundary=sum(e.is_boundary for e in bm.edges);nonmanifold=sum(not e.is_manifold for e in bm.edges);loose=sum(e.is_wire for e in bm.edges)
 dims=tuple(round(x,3) for x in o.dimensions)
 results.append({'name':name,'vertices':len(mesh.vertices),'faces':len(mesh.polygons),'dimensions_model_units':dims,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'loose_edges':loose,'watertight_mesh':nonmanifold==0});bm.free()
print(json.dumps(results,indent=2))
report={'version':'v321','section':'01 control horns','results':results,'note':'mesh manifold check only; not dimensional bore or structural fit proof','section_accepted':False,'remaining':['validate bore diameter from actual mesh','place pivots on actual hinge axes','servo clearance and full movement sweep','physical load and watertightness tests']}
open(os.path.join(R,'docs','V321_CONTROL_HORN_MESH_QA.json'),'w').write(json.dumps(report,indent=2))
