import bpy,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v287_PROFILE_FIT.blend'))
# Restore unwanted width change from v287 using original v286 mesh coordinates y
ref=bpy.data.libraries.load(os.path.join(R,'cad','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.blend'),link=False)
with ref as (src,dest):
 dest.objects=[n for n in ['SponsonL','SponsonR'] if n in src.objects]
for orig in dest.objects:
 cur=bpy.data.objects.get(orig.name.replace('.001',''))
 if cur and len(cur.data.vertices)==len(orig.data.vertices):
  for a,b in zip(cur.data.vertices,orig.data.vertices):
   a.co.y=b.co.y
  cur.data.update()
  print('RESTORED_WIDTH',cur.name)
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v288_BOTTOM_FIT_CLEAN.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v288_BOTTOM_FIT_CLEAN.stl'),export_selected_objects=False)
print('V288_DONE')
