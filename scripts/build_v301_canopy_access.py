import bpy, bmesh, math, os
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v298_CORRECTED_WING_NORMALS.blend'))
white=next(m for m in bpy.data.materials if 'white' in m.name.lower())
black=next(m for m in bpy.data.materials if 'canopy' in m.name.lower())
metal=next(m for m in bpy.data.materials if 'metal' in m.name.lower() or 'motor' in m.name.lower())
def loft(name,st,mat,n=20):
 verts=[];faces=[]
 for x,w,zbot,ztop in st:
  for i in range(n):
   a=2*math.pi*i/n
   c=math.cos(a);s=math.sin(a)
   y=w*c
   z=(ztop+zbot)*0.5+(ztop-zbot)*0.5*(s if s>=0 else s*.92)
   verts.append((x,y,z))
 for j in range(len(st)-1):
  for i in range(n):
   a=j*n+i;b=j*n+(i+1)%n
   faces.append((a,b,b+n,a+n))
 faces.extend([tuple(reversed(range(n))),tuple((len(st)-1)*n+i for i in range(n))])
 mesh=bpy.data.meshes.new(name)
 mesh.from_pydata(verts,[],faces);mesh.update()
 ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
 mesh.materials.append(mat)
 return ob
def remove(target,cutter):
 mod=target.modifiers.new('v301 removable canopy access relief','BOOLEAN')
 mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
 bpy.context.view_layer.objects.active=target
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
def cyl(name,pos,r,depth,mat,vertices=32):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=pos)
 o=bpy.context.object;o.name=name;o.data.materials.append(mat)
 return o
# Actual master: removable long smoked central canopy, electronics access underneath.
# Cutting away the interior shell while preserving exterior water- and aerodynamic silhouette.
hull=bpy.data.objects['01 Master Central fuselage']
canopy=bpy.data.objects['02 Black canopy']
hull_before=sum(p.area for p in hull.data.polygons)
cut=loft('TEMP cockpit opening tapered to canopy outline',[
 (-142,1,23,90),(-137,10,22,92),(-124,15,21,92),(-112,16.5,21,92),
 (-90,17,21,92),(-67,17,21,92),(-48,16,21,92),(-32,11,23,92),(-25,1,24,92)
 ],white,24)
remove(hull,cut)
# Canopy becomes a separate hollow cover, keeping a physical roof. Opening from below only.
cut2=loft('TEMP under-canopy lightweight relief',[
 (-144,1,34,62),(-137,9,30,63),(-119,12,28,64),
 (-94,15,28,65),(-73,15,28,64),(-50,14,28,61),
 (-30,10,31,57),(-26,1,38,56)
 ],white,24)
remove(canopy,cut2)
# Flange / ledge on the central deck below canopy; only slim plates, not enclosing whole battery
def plate(name,center,size,mat):
 bpy.ops.mesh.primitive_cube_add(size=1,location=center)
 o=bpy.context.object;o.name=name;o.dimensions=size
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 o.data.materials.append(mat)
 bev=o.modifiers.new('Radius on service feature','BEVEL');bev.width=0.8;bev.segments=3
 bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bev.name)
 return o
for s in [-1,1]:
 # Small closure ledges along both longitudinal cockpit edges (master shows deck seam)
 plate('v301 Cockpit flange '+('L' if s<0 else 'R'),(-79,s*20,53.5),(86,3,2),white)
 for x in [-113,-48]:
  # real bosses inside fuselage, no assumed screw clearance
  cyl('v301 Screw boss '+str(x)+' '+str(s),(x,s*21,41),3.8,17,white)
  # Cosmetic top screw head as Master-visible interface, not screw-thread promise
  cyl('v301 Fastener head '+str(x)+' '+str(s),(x,s*21,50.2),1.8,0.7,metal,20)
# Motor mount base was only two struts: add slim triangular lower brace connecting arch to deck.
def brace(side):
 s=side
 vs=[(92,s*24,38),(104,s*24,38),(124,s*22,79),(118,s*22,85),
     (92,s*27,38),(104,s*27,38),(124,s*25,79),(118,s*25,85)]
 fs=[(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]
 me=bpy.data.meshes.new('Motor brace mesh');me.from_pydata(vs,[],fs);me.update()
 o=bpy.data.objects.new('v301 Motor arch inner web '+('L' if s<0 else 'R'),me)
 bpy.context.collection.objects.link(o);me.materials.append(white)
 for f in me.polygons:f.use_smooth=True
brace(-1);brace(1)
# Reserve volume guide (NOT a physical RC device) hidden in viewport/render
guide=plate('REFERENCE ONLY 3S battery envelope 90x30x20',(-79,0,36),(90,30,20),black)
guide.hide_render=True;guide.hide_set(True)
# Mesh audit
names=['01 Master Central fuselage','02 Black canopy']
for name in names:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data)
 bad=sum(1 for edge in bm.edges if not edge.is_manifold)
 vol=bm.calc_volume(signed=True)
 print('v301_AUDIT',name,'verts',len(bm.verts),'faces',len(bm.faces),'nonmanifold',bad,'signed_volume_mm3',round(vol,3));bm.free()
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v301_COCKPIT_ACCESS.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
# export only visible physical components; omit envelope guide
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type=='MESH' and o!=guide:o.select_set(True)
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v301_COCKPIT_ACCESS.stl'),export_selected_objects=True)
print('v301_SAVED',out,'objects',len([o for o in bpy.data.objects if o.type=='MESH']))
