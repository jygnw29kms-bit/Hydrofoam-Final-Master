import bpy,bmesh,os,json,math
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v328_RUDDER_HINGES_WIP.blend'))
left=bpy.data.objects['30 Tail fin Left'];right=bpy.data.objects['30 Tail fin Right'];mirror=Matrix.Diagonal((1,-1,1,1))
# Reconstruct the defective port cut from the topologically clean starboard cut.
# Use world-space mirrored vertices, then transform into left-local space.
mesh=right.data.copy();inv=left.matrix_world.inverted();src=right.matrix_world
for v in mesh.vertices:v.co=inv@(mirror@(src@v.co))
for poly in mesh.polygons:
 poly.flip()
old=left.data;left.data=mesh
# Keep source mesh intact and leave old mesh for Blender cleanup.
def manifold(o):
 bm=bmesh.new();bm.from_mesh(o.data);n=sum(not e.is_manifold for e in bm.edges);bm.free();return n
def bvh(o,m):return BVHTree.FromPolygons([m@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons],epsilon=.0001)
report=[]
for side,y in [('Left',-182.5),('Right',182.5)]:
 fin=bpy.data.objects['30 Tail fin '+side];rud=bpy.data.objects['V324_'+side+'_MOVABLE_RUDDER_WIP'];fb=bvh(fin,fin.matrix_world);pivot=Vector((201,y,0));sweep=[]
 for angle in [-30,-25,-20,-15,-10,-5,0,5,10,15,20,25,30]:
  rot=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(angle),4,'Z')@Matrix.Translation(-pivot)
  overlap=len(fb.overlap(bvh(rud,rot@rud.matrix_world)))
  sweep.append({'degrees':angle,'triangle_intersections':overlap})
 report.append({'side':side,'fin_nonmanifold_edges':manifold(fin),'sweep':sweep,'clear_at_25':all(x['triangle_intersections']==0 for x in sweep if abs(x['degrees'])<=25)})
qa={'version':'v330','operation':'rebuild left fixed-fin cut by world-mirroring clean right fin mesh; preserve twin rudder prototypes and hinges','results':report,'accepted':False,'limitations':['mirrored cut still has nonzero collision at +/-30 deg','triangle BVH not full solid penetration or minimum-clearance analysis','hinge sleeves are still detached from parent surfaces','verify final master silhouette and print-fit']}
open(os.path.join(R,'docs','V330_MIRRORED_FIN_REBUILD_QA.json'),'w').write(json.dumps(qa,indent=2))
os.makedirs(os.path.join(R,'renders','v330'),exist_ok=True);bpy.context.scene.render.filepath=os.path.join(R,'renders','v330','symmetric_twin_fin_cut_iso.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v330_SYMMETRIC_FIN_CUT_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V330_RESULTS',json.dumps([{'side':r['side'],'bad':r['fin_nonmanifold_edges'],'clear25':r['clear_at_25'],'hits':[x['triangle_intersections'] for x in r['sweep']]} for r in report]))
