import bpy,os,math
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.blend'))
def smooth(t):
 t=max(0.,min(1.,t));return t*t*(3-2*t)
def lerp(x,xx,yy):
 if x<=xx[0]:return yy[0]
 if x>=xx[-1]:return yy[-1]
 for i in range(len(xx)-1):
  if xx[i]<=x<=xx[i+1]:
   t=smooth((x-xx[i])/(xx[i+1]-xx[i]))
   return yy[i]*(1-t)+yy[i+1]*t
 return 0.
# target-minus-observed lower-envelope errors measured using 450 mm reference x mapping
X=[-225,-202.6,-180.1,-157.7,-135.2,-112.8,-90.3,-67.9,-45.4,-23,0,23,45.4,67.9,90.3,112.8,135.2,157.7,180.1,202.6,225]
ERR=[0,-5.4,-22.5,-13,-6.7,-5,-3.7,-2,0,0,-0.6,-4.2,10.2,-0.1,0,-0.1,-0.3,-1.1,5.6,10.3,0]
# measured current bottom height relative to reference z base
CUR=[32.2,25.7,22.5,13,6.7,5,3.7,2,0,0,0.6,4.2,17.5,32.8,33.9,34,31.9,29.9,26,25.3,97.7]
z0=-11.31895733
move=['CenterHull','SponsonL','SponsonR','WingDeckL','WingDeckR','TailL','TailR','RearOrangeL','RearOrangeR','SkidL','SkidR']
for name in move:
 ob=bpy.data.objects.get(name)
 if not ob or ob.type!='MESH':continue
 inv=ob.matrix_world.inverted()
 for v in ob.data.vertices:
  w=ob.matrix_world@v.co
  xc=(w.x+228)/456*450-225
  zfloor=z0+lerp(xc,X,CUR)
  # do not change top-side or ornamental details; weight the bottom 32 mm
  amount=lerp(xc,X,ERR)*(1-smooth((w.z-zfloor)/32))
  if abs(amount)>0.00001:
   v.co=inv@type(w)((w.x,w.y,w.z+amount))
  # small planform correction to the wide-forward shoulders
  if name.startswith('Sponson'):
   widthdelta=lerp(xc,[-225,-180,-157.7,-135.2,-112.8,-90.3,-67.9,-45],[0,0,-4.2,-8,-10.5,-8.1,-4.5,0])
   v.co.y+=math.copysign(abs(widthdelta)*(-1),v.co.y) if abs(v.co.y)>100 else 0
 ob.data.update()
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v287_PROFILE_FIT.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v287_PROFILE_FIT.stl'),export_selected_objects=False)
print('V287_DONE')
