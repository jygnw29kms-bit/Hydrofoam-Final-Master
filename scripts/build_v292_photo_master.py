import bpy, math, os
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def material(name,hexcol,metal=0,rough=.38):
 c=tuple(int(hexcol[i:i+2],16)/255 for i in (0,2,4))
 m=bpy.data.materials.new(name);m.diffuse_color=(*c,1)
 m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*c,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough
 return m
white=material('Master / pearlescent white','D9DDE2',.12,.32)
orange=material('Master / signal orange','FF650D',.07,.28)
black=material('Master / smoke canopy','151D26',.3,.15)
dark=material('Master / black skid','11161B',.1,.48)
steel=material('Master / titanium hardware','59616A',.7,.3)
def mesh(name,verts,faces,mat):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);ob.data.materials.append(mat)
 for face in me.polygons:face.use_smooth=True
 return ob
def loft(name,stations,mat,N=24):
 vs=[];fs=[]
 for x,y,w,mid,h in stations:
  for i in range(N):
   a=math.tau*i/N
   # slightly flattened lower hull, arch-style upper deck
   cs=math.cos(a);ss=math.sin(a)
   yy=y+w*cs
   zz=mid+h*(ss if ss>0 else .72*ss)
   vs.append((x,yy,zz))
 for k in range(len(stations)-1):
  for i in range(N):
   a=k*N+i;b=k*N+(i+1)%N
   fs.append((a,b,b+N,a+N))
 fs.append(tuple(reversed(range(N))))
 fs.append(tuple((len(stations)-1)*N+i for i in range(N)))
 return mesh(name,vs,fs,mat)
def surf(name,outline,zfn,thick,mat):
 n=len(outline);vs=[(x,y,zfn(x,y)) for x,y in outline]
 vs+= [(x,y,zfn(x,y)-thick) for x,y in outline]
 # triangulated convex-ish wings via fan around interior center
 cx=sum(x for x,y in outline)/n;cy=sum(y for x,y in outline)/n
 vs.extend([(cx,cy,zfn(cx,cy)),(cx,cy,zfn(cx,cy)-thick)])
 fs=[]
 for i in range(n):
  j=(i+1)%n
  fs.extend([(2*n,i,j),(2*n+1,n+j,n+i),(i,n+i,n+j,j)])
 return mesh(name,vs,fs,mat)
# twin water pontoons: image shows strong parallel outer hulls, pointed orange noses
xs=[-220,-213,-196,-173,-145,-105,-65,-15,32,77,112,146,167]
widths=[1,8,19,29,37,42,43,41,38,34,30,22,2]
tops=[17,23,29,33,36,36,35,34,32,29,26,22,19]
bottoms=[16,11,3,-4,-8,-9,-8,-6,-2,4,9,13,17]
for sign,name in [(-1,'L'),(1,'R')]:
 stations=[]
 for i,x in enumerate(xs):
  zbot=bottoms[i];zt=tops[i]
  stations.append((x,sign*121,widths[i],(zt+zbot)/2,(zt-zbot)/1.72))
 loft('Hull / outer float '+name,stations,white)
 loft('Orange forward float cap '+name,[(x,sign*121,w*.98,m+h*.67,h*.27) for (x,_,w,m,h) in stations[:5]],orange)
 # uninterrupted black detachable runners below hulls
 loft('PETG hydro skid '+name,[(x,sign*121,w,zz,hh) for x,w,zz,hh in
 [(-142,15,-10,3),(-110,17,-12,3),(-55,17,-12,3),(0,15,-10,3),(48,11,-5,3)]],dark,N=12)
 # actual swept wings: front low diagonal to central canopy, rear swept control surface
 wing=[(-100,sign*45),(-64,sign*104),(-20,sign*169),(38,sign*185),(108,sign*176),
       (154,sign*207),(188,sign*212),(172,sign*119),(92,sign*81),(25,sign*56)]
 surf('Swept main wing '+name,wing,lambda x,y:27+2*math.sin((x+110)/300*math.pi),3.6,white)
 surf('Wing orange leading stripe '+name,[(-80,sign*77),(-51,sign*117),(-18,sign*155),(28,sign*174),(61,sign*177),
 (43,sign*156),(-16,sign*137),(-65,sign*82)],lambda x,y:30,0.8,orange)
 # vertical tail fins, tilted sharp leading edge and tall orange tip
 fin=[(132,sign*185,28),(160,sign*184,34),(205,sign*181,100),(214,sign*181,105),(221,sign*181,53),(221,sign*181,29)]
 def panel3(name,vertices,mat):
  v=vertices+[(x,y+sign*3,z) for x,y,z in vertices]
  n=len(vertices);fs=[]
  for i in range(1,n-1):fs.extend([(0,i,i+1),(n,n+i+1,n+i)])
  for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
  return mesh(name,v,fs,mat)
 panel3('Twin tall fin '+name,fin,white)
 panel3('Fin orange tip '+name,[(204,sign*185,78),(214,sign*185,105),(221,sign*185,102),(221,sign*185,82)],orange)
 # rear control flaps and orange wingtip
 surf('Rear elevon '+name,[(139,sign*106),(193,sign*118),(212,sign*193),(186,sign*210)],lambda x,y:29,2.2,white)
 surf('Elevon orange trailing '+name,[(188,sign*141),(210,sign*151),(217,sign*203),(198,sign*198)],lambda x,y:30,1,orange)
# central hull and angular low nose, elevated cockpit
loft('Center spear fuselage',[
 (-186,0,2,23,2),(-167,0,15,25,12),(-146,0,32,28,21),(-115,0,46,31,26),
 (-65,0,52,34,27),(-10,0,48,34,24),(46,0,44,30,21),(108,0,39,28,17),
 (170,0,23,24,11),(205,0,5,22,3)],white)
loft('Dark panoramic canopy',[
 (-118,0,2,57,2),(-107,0,17,65,11),(-76,0,29,71,15),(-41,0,32,73,18),
 (-9,0,26,73,15),(18,0,12,69,9),(30,0,1,64,1)],black)
# arched pusher motor mount between fins; structural arch, not flat beam
def beam(name,a,b,r,mat):
 a,b=Vector(a),Vector(b)
 delta=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=r,depth=delta.length,location=(a+b)*.5)
 o=bpy.context.object;o.name=name;o.rotation_euler=delta.to_track_quat('Z','Y').to_euler();o.data.materials.append(mat);return o
for sg in (-1,1):
 beam('Pusher arch strut',(92,sg*32,35),(113,sg*29,88),6,white)
 beam('Pusher arch roof',(113,sg*29,88),(136,sg*13,99),5,white)
beam('Pusher cross brace',(132,-20,97),(132,20,97),5,white)
beam('Black brushless motor',(145,0,99),(170,0,99),15,dark)
beam('Orange motor trim',(162,0,99),(166,0,99),16,orange)
beam('Propeller spindle',(171,0,99),(180,0,99),4,steel)
for sign in [-1,1]:
 beam('Black two blade prop',(180,0,99),(180,sign*4,99+sign*46),5,dark)
# save real mesh, not generated concept art
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v292_PHOTO_REBUILD.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v292_PHOTO_REBUILD.stl'),export_selected_objects=False)
print('PHOTO_MASTER_V292_READY',len([o for o in bpy.data.objects if o.type=='MESH']))
