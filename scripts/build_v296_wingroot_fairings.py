import bpy,math,os,bmesh
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v295_SMOOTH_HULLS.blend'))
# Add physically modeled wing-root fairings to eliminate abrupt flat wing-to-hull steps.
white=next(m for m in bpy.data.materials if 'white' in m.name.lower())
def fairing(name,sign,points):
 # loft a tapered organic 3D shoulder along wing span. Each ring is in x-z plane.
 N=24;v=[];f=[]
 for y,x,z,rx,rz in points:
  for i in range(N):
   a=math.tau*i/N
   v.append((x+rx*math.cos(a),sign*y,z+rz*math.sin(a)))
 for k in range(len(points)-1):
  for i in range(N):
   a=k*N+i;b=k*N+(i+1)%N
   f.append((a,b,b+N,a+N))
 f.extend([tuple(reversed(range(N))),tuple((len(points)-1)*N+i for i in range(N))])
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 ob.data.materials.append(white)
 for p in me.polygons:p.use_smooth=True
 return ob
for s,label in [(-1,'L'),(1,'R')]:
 fairing('v296 Sculpted central wing shoulder '+label,s,[
 (29,-77,42,48,11),(38,-71,39,54,10),(51,-63,36,58,8),
 (66,-51,35,55,6),(83,-30,34,46,4),(98,-8,33,29,2.5),
 (108,9,32,5,0.8)])
 fairing('v296 Wing to float transition '+label,s,[
 (96,8,35,9,1.5),(104,17,34,24,3.5),(112,26,34,40,5.0),
 (121,33,34,48,5.0),(134,40,33,44,3.7),(146,52,32,28,2.5),
 (154,66,31,5,1.0)])
# Clean overlapping triangles? Do not boolean: keep editable parts and flag intersections.
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.stl'),export_selected_objects=False)
report=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=sum(1 for e in bm.edges if len(e.link_faces)!=2)
 report.append((o.name,bad,len(bm.faces)));bm.free()
print('V296_AUDIT',len(report),'objects',sum(n for _,n,_ in report),'open_edges')
for name,bad,faces in report:
 if bad:print('OPEN',name,bad,faces)
