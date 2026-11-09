import bpy,os,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v328_RUDDER_HINGES_WIP.blend'))
def bvh(o,mat):
 v=[mat@x.co for x in o.data.vertices];polys=[tuple(p.vertices) for p in o.data.polygons];return BVHTree.FromPolygons(v,polys,all_triangles=False,epsilon=0.0001)
report=[]
for side,y in [('Left',-182.5),('Right',182.5)]:
 fin=bpy.data.objects['30 Tail fin '+side];rud=bpy.data.objects['V324_'+side+'_MOVABLE_RUDDER_WIP'];pivot=Vector((201,y,0));fb=bvh(fin,fin.matrix_world);steps=[]
 for deg in [-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30]:
  angle=math.radians(deg);rot=Matrix.Translation(pivot)@Matrix.Rotation(angle,4,'Z')@Matrix.Translation(-pivot);rb=bvh(rud,rot@rud.matrix_world);hits=fb.overlap(rb)
  steps.append({'angle_deg':deg,'triangle_overlap_pairs':len(hits)})
 report.append({'side':side,'pivot':[201,y],'sweep':steps,'all_clear':all(s['triangle_overlap_pairs']==0 for s in steps)})
qa={'version':'v329','purpose':'triangle BVH intersection test of rectangular rudder prototype versus cut fixed fin at 5-degree steps from -30 to +30 degrees','results':report,'caution':'zero surface triangle intersections does not rule out containment, hinge sleeve collisions, dynamic linkage collisions or inadequate mechanical clearance','accepted':False}
open(os.path.join(R,'docs','V329_RUDDER_SWEEP_BVH_QA.json'),'w').write(json.dumps(qa,indent=2));print('V329_SWEEP',json.dumps(report))
