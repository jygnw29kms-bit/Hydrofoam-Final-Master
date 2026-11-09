import bpy,os,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v307_LAND_SKID_PROTOTYPES.blend'))
for o in list(bpy.data.objects):
 if o.name.startswith('v307 PETG land skid '):bpy.data.objects.remove(o,do_unlink=True)
mat=bpy.data.materials.get('Black PETG skid')
if mat is None:
 mat=bpy.data.materials.new('Black PETG skid')
 mat.diffuse_color=(.025,.028,.035,1)
# A contoured replaceable wear surface follows the actually modeled bottom of both v306 hull halves.
# 0.6 mm nominal local bondline; bores are NOT yet approved insert locations.
folder=os.path.join(R,'print','v308_conformal_skids')
os.makedirs(folder,exist_ok=True)
records=[]
for side in ['left','right']:
 cy=(-119 if side=='left' else 119)
 for half,xa,xb in [('front',-135,-14),('rear',-6,135)]:
  h=bpy.data.objects['v305 HOLLOW float_'+side+'_'+half]
  deps=bpy.context.evaluated_depsgraph_get()
  bvh=BVHTree.FromObject(h,deps)
  def bottom(x,y):
   hit,norm,ix,dist=bvh.ray_cast(Vector((x,y,-150)),Vector((0,0,1)),250)
   if hit is None:raise RuntimeError('NO HULL AT '+str((x,y)))
   return float(hit.z)
  xs=[xa+(xb-xa)*i/40 for i in range(41)]
  ys=[cy+(j-5)*1.5 for j in range(11)]
  n=len(ys);top=[];bot=[]
  for x in xs:
   for y in ys:
    z=bottom(x,y)-.6
    top.append((x,y,z));bot.append((x,y,z-3.2))
  v=top+bot;fs=[];o=n*len(xs)
  for i in range(len(xs)-1):
   for j in range(n-1):
    a=i*n+j;b=a+1;c=(i+1)*n+j;dd=c+1
    fs.append((a,c,dd,b))
    fs.append((o+b,o+dd,o+c,o+a))
  # side perimeters
  for i in range(len(xs)-1):
   for j in (0,n-1):
    a=i*n+j;b=(i+1)*n+j
    fs.append((a,o+a,o+b,b) if j==0 else (a,b,o+b,o+a))
  for j in range(n-1):
   a=j;b=j+1
   fs.append((a,b,o+b,o+a))
   a=(len(xs)-1)*n+j;b=a+1
   fs.append((a,o+a,o+b,b))
  me=bpy.data.meshes.new('v308 conformal skid mesh');me.from_pydata(v,[],fs);me.update()
  obj=bpy.data.objects.new('v308 CONFORMAL PETG skid '+side+' '+half,me)
  bpy.context.collection.objects.link(obj);obj.data.materials.append(mat)
  # Recalculate outward normals on full geometry before Boolean
  import bmesh
  bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free();me.update()
  # Positions inherited from v307; holes are experimental until actual inserts are engineered.
  for xx in (xa+15,xb-15):
   bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=1.65,depth=100,location=(xx,cy,-5))
   cutter=bpy.context.object
   mod=obj.modifiers.new('M3 clearance TEST','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
   bpy.context.view_layer.objects.active=obj
   bpy.ops.object.modifier_apply(modifier=mod.name)
   bpy.data.objects.remove(cutter,do_unlink=True)
  bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
  path=os.path.join(folder,'conformal_skid_'+side+'_'+half+'.stl')
  bpy.ops.wm.stl_export(filepath=path,export_selected_objects=True)
  records.append((obj.name,len(obj.data.vertices),min(p[2] for p in v),max(p[2] for p in v)))
  print('V308_SKID',*records[-1])
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v308_CONFORMAL_LAND_SKIDS.blend'))
print('V308_DONE',len(records))
