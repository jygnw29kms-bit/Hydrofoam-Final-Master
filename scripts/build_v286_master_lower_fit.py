import bpy,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v285_PLANING_RELEASE.blend'))
# measured transverse lower-envelope correction, aft planing release
xs=[-90.3,-45.4,0,23,45.4,67.9,90.3,112.8,135.2,157.7,180.1,202.6,225]
measured=[3.8,0,5.8,10.9,22.0,34.2,35.8,37.4,37.6,37.9,26.0,25.3,97.7]
target=[0,0,0,0,27.7,32.7,33.9,33.9,31.6,28.8,31.6,35.6,97.7]
def smooth(t):
 t=max(0,min(1,t));return t*t*(3-2*t)
def interp(x,ls):
 if x<=xs[0]:return ls[0]
 if x>=xs[-1]:return ls[-1]
 for i in range(len(xs)-1):
  if xs[i]<=x<=xs[i+1]:
   t=smooth((x-xs[i])/(xs[i+1]-xs[i]))
   return ls[i]*(1-t)+ls[i+1]*t
 return 0
z0=min((ob.matrix_world@v.co).z for ob in bpy.data.objects if ob.type=='MESH' for v in ob.data.vertices)
for name in ['CenterHull','SponsonL','SponsonR','WingDeckL','WingDeckR','TailL','TailR']:
 ob=bpy.data.objects.get(name)
 if not ob or ob.type!='MESH':continue
 for v in ob.data.vertices:
  x=v.co.x; z=v.co.z
  if x<xs[0] or x>xs[-1]:continue
  floor=z0+interp(x,measured)
  # full correction near lower envelope, fade to zero 27 mm above
  weight=1-smooth((z-floor)/27)
  correction=interp(x,[b-a for a,b in zip(measured,target)])
  v.co.z+=correction*weight
 ob.data.update()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.stl'),export_selected_objects=False)
print('V286_DONE',z0)
