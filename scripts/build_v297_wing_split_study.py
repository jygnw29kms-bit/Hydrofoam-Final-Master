import bpy,bmesh,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend'))
outdir=os.path.join(R,'print','v297_wing_modules')
os.makedirs(outdir,exist_ok=True)
# 256 x 256 mm P2S build plate bound; these are geometry modules, not assembled couplings.
names=[('20 Swept blended wing Left',-10),('20 Swept blended wing Right',-10)]
def cut(o,x,side):
 bm=bmesh.new();bm.from_mesh(o.data)
 # vertices are local, reference has no placement on primary parts
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
   dist=.00001,plane_co=(x,0,0),plane_no=(1,0,0),
   clear_inner=(side=='rear'),clear_outer=(side=='front'))
 boundary=[e for e in bm.edges if e.is_boundary]
 # Only fill cut-plane edges, not any other boundaries (original geometry closed)
 cutedges=[e for e in boundary if all(abs(v.co.x-x)<.01 for v in e.verts)]
 if cutedges:
  bmesh.ops.holes_fill(bm,edges=cutedges,sides=0)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 mesh=bpy.data.meshes.new(o.name+'_'+side+'_module_mesh');bm.to_mesh(mesh);mesh.update();bm.free()
 ob=bpy.data.objects.new(o.name+' '+side+' module',mesh);bpy.context.collection.objects.link(ob)
 for m in o.data.materials:mesh.materials.append(m)
 return ob
kept=[]
for name,x in names:
 base=bpy.data.objects.get(name)
 if base is None:raise ValueError('MISSING '+name)
 for part in ['front','rear']:
  obj=cut(base,x,part)
  kept.append(obj)
  bpy.ops.object.select_all(action='DESELECT')
  obj.select_set(True);bpy.context.view_layer.objects.active=obj
  safe=name.replace(' ','_')
  path=os.path.join(outdir,safe+'_'+part+'.stl')
  bpy.ops.wm.stl_export(filepath=path,export_selected_objects=True)
  pts=[obj.matrix_world@v.co for v in obj.data.vertices]
  dims=[max(p[i] for p in pts)-min(p[i] for p in pts) for i in range(3)]
  print('MODULE',obj.name,'dims',*[round(z,2) for z in dims],'fits_axis_bounds',all(z<=256 for z in dims))
for o in list(bpy.data.objects):
 if o not in kept:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_v297_WING_SPLIT_STUDY.blend'))
print('SPLIT_STUDY_DONE',len(kept))
