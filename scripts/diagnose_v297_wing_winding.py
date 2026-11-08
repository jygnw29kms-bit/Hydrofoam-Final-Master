import bpy,bmesh,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend'))
for name in ['20 Swept blended wing Left','20 Swept blended wing Right']:
 ob=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(ob.data)
 print('BEFORE',name,'V',bm.calc_volume(signed=True),'open',sum(1 for e in bm.edges if not e.is_manifold),'faces',len(bm.faces))
 v0=bm.calc_volume(signed=True)
 bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 print('AFTER_RECALC',name,'V',bm.calc_volume(signed=True),'open',sum(1 for e in bm.edges if not e.is_manifold))
 for f in list(bm.faces)[:8]:print('FACE',len(f.verts),f.normal[:])
 bm.free()
