import bpy,os,math
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v284_SIDE_CLOSE2.blend'))
# Master side view: planing underbody ends near X=30; aft lower shell rises to tailplane.
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3.-2.*t)
for name in ['CenterHull','SponsonL','SponsonR','WingDeckL','WingDeckR','TailL','TailR']:
 ob=bpy.data.objects.get(name)
 if not ob or ob.type!='MESH':continue
 for v in ob.data.vertices:
  x=v.co.x; z=v.co.z
  aft=smooth((x-17.)/35.)
  # lift only underside, preserving upper master silhouette
  low=smooth((33.-z)/24.)
  if name.startswith('Sponson'):
   # release chine rises aft, smoothly into rear attachment
   rise=30.*aft*low
  elif name=='CenterHull':rise=29.*aft*low
  else:rise=23.*aft*low
  v.co.z+=rise
 ob.data.update()
# Keep runners short, removable and below planing region
for name in ['SkidL','SkidR']:
 ob=bpy.data.objects.get(name)
 if ob and ob.type=='MESH':
  for v in ob.data.vertices:
   if v.co.x>18.:v.co.x=18.+(v.co.x-18.)*.15
  ob.data.update()
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v285_PLANING_RELEASE.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v285_PLANING_RELEASE.stl'),export_selected_objects=False)
print('V285_DONE')

