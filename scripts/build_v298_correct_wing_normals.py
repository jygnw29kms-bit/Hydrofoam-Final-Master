import bpy,bmesh,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend'))
fixed=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 prior=bm.calc_volume(signed=True)
 if o.name.startswith('20 Swept blended wing'):
  bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
  volume=bm.calc_volume(signed=True)
  fixed.append((o.name,prior,volume))
  bm.to_mesh(o.data);o.data.update()
 bm.free()
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v298_CORRECTED_WING_NORMALS.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v298_CORRECTED_WING_NORMALS.stl'),export_selected_objects=False)
print('V298_DONE',fixed)
