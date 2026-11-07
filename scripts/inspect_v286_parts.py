import bpy,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v286_MASTER_LOWER_FIT.blend'))
print('PARTS',[(o.name,o.type,len(o.data.vertices) if o.type=='MESH' else 0) for o in bpy.data.objects])
for x in [-180,-135,-90,0,23,45,67,113,157,180,202]:
 points=[]
 for ob in bpy.data.objects:
  if ob.type!='MESH':continue
  vnear=[(ob.matrix_world@v.co).z for v in ob.data.vertices if abs((ob.matrix_world@v.co).x-x)<5]
  if vnear:points.append((round(min(vnear),1),ob.name))
 print('STATION',x, sorted(points)[:7])
