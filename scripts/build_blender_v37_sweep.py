import bpy, json, os, math
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
data=json.load(open(os.path.join(ROOT,'reference','master_profiles_v3.json')))['profiles']
L=450.0; W=482.0; Z0=5.0; ZS=118.0; M=25
verts=[]; faces=[]
# upper/lower grid driven by exact top outline + side height envelope
for i,p in enumerate(data):
 x=p['t']*L; yl=p['left']*W; yr=p['right']*W
 zb=Z0+p['zbot']*ZS; zt=Z0+p['ztop']*ZS; bodytop=min(zt,76.0)
 for j in range(M):
  u=j/(M-1); y=yl+(yr-yl)*u
  yn=0 if abs(yr-yl)<1 else 2*(u-.5)
  # center fuselage + twin sponson crowns, with valleys between
  g0=math.exp(-(yn/0.34)**2)
  g1=math.exp(-((yn-0.58)/0.20)**2)
  g2=math.exp(-((yn+0.58)/0.20)**2)
  crown=max(g0,g1,g2)
  edge=(1-abs(yn))**0.35
  shape=max(0.10, min(1.0,0.18*edge+0.82*crown))
  zu=zb+(bodytop-zb)*shape
  zl=zb-5.0*(1-edge)
  verts.append((x,y,zu)); verts.append((x,y,zl))
for i in range(len(data)-1):
 for j in range(M-1):
  a=2*(i*M+j); b=a+2; c=2*((i+1)*M+j)+2; d=2*((i+1)*M+j)
  faces.append((a,b,c,d)); faces.append((a+1,d+1,c+1,b+1))
# side walls and ends
for i in range(len(data)-1):
 for j in [0,M-1]:
  a=2*(i*M+j); b=2*((i+1)*M+j); faces.append((a,b,b+1,a+1))
for i in [0,len(data)-1]:
 row=[2*(i*M+j) for j in range(M)]; faces.append(tuple(row)); faces.append(tuple(r+1 for r in row[::-1]))
mesh=bpy.data.meshes.new('MasterSurface'); mesh.from_pydata(verts,[],faces); mesh.update()
obj=bpy.data.objects.new('Hydrofoam_Master_Surface',mesh); bpy.context.collection.objects.link(obj)
# smooth visual surface
for p in mesh.polygons:p.use_smooth=True
bev=obj.modifiers.new('EdgeSoft','BEVEL'); bev.width=0.8; bev.segments=2
# fins as swept plates

def fin(name,y,sgn):
 pts=[(328,y,38),(365,y,40),(405,y,112),(413,y,128),(383,y,120),(328,y,38)]
 v=[Vector(p) for p in pts]+[Vector((x,y+sgn*2.2,z)) for x,_,z in pts]
 n=len(pts); f=[]
 f.append(tuple(range(n))); f.append(tuple(range(n,2*n)))
 for k in range(n-1):f.append((k,k+1,n+k+1,n+k))
 me=bpy.data.meshes.new(name); me.from_pydata(v,[],f); me.update(); o=bpy.data.objects.new(name,me); bpy.context.collection.objects.link(o); return o
fin('Fin_L',-176,-1); fin('Fin_R',176,1)
# motor arch using cylinders between points

def cyl_between(name,a,b,r):
 a=Vector(a); b=Vector(b); d=b-a; mid=(a+b)/2
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=r,depth=d.length,location=mid)
 o=bpy.context.object; o.name=name; o.rotation_mode='QUATERNION'; o.rotation_quaternion=d.to_track_quat('Z','Y'); return o
for y in (-22,22): cyl_between('MotorLeg',(292,y,42),(320,y,82),5)
cyl_between('MotorBridge',(320,-22,82),(320,22,82),5)
# prop disk placeholder, thin
bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=16,depth=5,location=(322,0,82),rotation=(0,math.pi/2,0)); bpy.context.object.name='Firewall'
# canopy: scaled ellipsoid
bpy.ops.mesh.primitive_uv_sphere_add(segments=48,ring_count=24,location=(145,0,70)); can=bpy.context.object; can.name='Canopy'; can.scale=(82,31,23)
# export master visual STL
bpy.ops.object.select_all(action='SELECT')
out=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v37_MASTER_SURFACE.stl'); bpy.ops.wm.stl_export(filepath=out,export_selected_objects=True)
# save blend
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v37_MASTER_SURFACE.blend'))
print('V37_MASTER_SURFACE_SAVED',out)

