import bpy,bmesh,math,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v301_COCKPIT_ACCESS.blend'))
white=next(m for m in bpy.data.materials if 'white' in m.name.lower())
def cutter_loft(name,rings,cy,n=40):
 v=[];f=[]
 for x,w,zt,zb in rings:
  for j in range(n):
   a=math.tau*j/n;s=math.sin(a)
   v.append((x,cy+w*math.cos(a),(zt+zb)/2+(zt-zb)/2*(s if s>=0 else s*.85)))
 for k in range(len(rings)-1):
  for j in range(n):
   a=k*n+j;b=k*n+(j+1)%n;f.append((a,b,b+n,a+n))
 f.append(tuple(reversed(range(n))))
 f.append(tuple((len(rings)-1)*n+j for j in range(n)))
 me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);return o
def volume(o):
 bm=bmesh.new();bm.from_mesh(o.data)
 vol=abs(bm.calc_volume(signed=True));bad=sum(1 for e in bm.edges if not e.is_manifold)
 bm.free()
 return vol,bad
def core_cut(name,rings,cy):
 obj=bpy.data.objects[name]
 before,err=volume(obj)
 core=cutter_loft('TEMP v303 sealed air void '+name,rings,cy)
 mod=obj.modifiers.new('v303 inner shell cavity','BOOLEAN')
 mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=core
 bpy.context.view_layer.objects.active=obj
 bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(core,do_unlink=True)
 after,bad=volume(obj)
 print('V303_SHELL',name,'before_mm3',round(before,3),'after_mm3',round(after,3),
 'savings_percent',round(100*(before-after)/before,2),'watertight_edges',bad==0)
 return before,after,bad
# lofted internal void follows the real external master silhouette without modifying it.
center=[(-213,0.7,26,22),(-204,17.5,31.5,18.5),(-186,28.4,37.5,14.5),
 (-155,37.3,45.5,8.5),(-125,41.3,52.5,7.5),(-90,42.3,56.5,8.5),
 (-55,41.3,55.5,11.5),(-20,38.3,51.5,16.5),
 (22,35.3,46.5,22.5),(67,34.3,41.5,26.5),
 (113,30.3,37.0,30.5),(134,22.0,33.4,31.0)]
# Most of the center cockpit opens into the interior after the v301 access pocket.
rows=[]
rows.append(('center',*core_cut('01 Master Central fuselage',center,0)))
outer=[(-159,9,29,16),(-149,18,31,9),(-130,26,33,1),(-105,29,35,-5),
 (-72,30,37,-8),(-26,30,37,-9),(16,30,36,-8),(58,28,34,-3),
 (92,26,32,7),(125,22,30,17),(153,13,28,23)]
inner=[(x,max(0.4,w-1.65),zt-1.35,zb+1.35) for x,w,zt,zb in outer]
for sign,key in [(-1,'10 Planing float Left'),(1,'10 Planing float Right')]:
 rows.append((key,*core_cut(key,inner,119*sign)))
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v303_LIGHTWEIGHT_HULLS.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
 if o.type=='MESH' and not o.name.startswith('REFERENCE ONLY'):o.select_set(True)
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v303_LIGHTWEIGHT_HULLS.stl'),export_selected_objects=True)
print('V303_COMPLETED',rows)
