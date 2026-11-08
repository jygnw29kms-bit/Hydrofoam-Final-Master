import bpy,os,re
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.blend'))
out=os.path.join(R,'print','v293_individual_meshes')
os.makedirs(out,exist_ok=True)
objs=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
for i,o in enumerate(objs):
 bpy.ops.object.select_all(action='DESELECT')
 o.select_set(True);bpy.context.view_layer.objects.active=o
 safe=re.sub(r'[^a-zA-Z0-9_-]+','_',o.name)
 bpy.ops.wm.stl_export(filepath=os.path.join(out,f'{i+1:02d}_{safe}.stl'),export_selected_objects=True)
 print('EXPORTED_PART',i+1,o.name)
print('EXPORT_PARTS_DONE',len(objs))
