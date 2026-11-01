import bpy, math, os
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad')
bpy.ops.wm.open_mainfile(filepath=os.path.join(CAD,'Hydrofoam_Final_Master_v90_VOXEL_BLEND.blend'))
WHITE=bpy.data.materials.get('Body');ORANGE=bpy.data.materials.get('Accent');BLACK=bpy.data.materials.get('Black')
def sweep(name,st,ma,rings=40,flat=.20):
 v=[];f=[]
 for x,yc,bot,top,w in st:
  h=top-bot
  for j in range(rings):
   a=2*math.pi*j/rings;yy=yc+w*.5*math.cos(a);q=(math.sin(a)+1)/2
   if q<flat:q=flat*(q/flat)**1.8
   v.append((x,yy,bot+h*q))
 n=len(st)
 for i in range(n-1):
  for j in range(rings):f.append((i*rings+j,i*rings+(j+1)%rings,(i+1)*rings+(j+1)%rings,(i+1)*rings+j))
 f += [tuple(range(rings-1,-1,-1)),tuple((n-1)*rings+j for j in range(rings))]
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(ma)
 for p in me.polygons:p.use_smooth=True
 return o
def plate(name,pts,z0,z1,ma):
 v=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts];n=len(pts);f=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n))
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(ma);return o
# restore more distinct pontoon crowns like master, still blended at shoulders
for sgn,l in [(-1,'L'),(1,'R')]:
 y=sgn*140
 crest=[(78,y,31,32,8),(100,y,31,35,26),(135,y,31,38,44),(180,y,31,40,52),(225,y,31,39,54),(270,y,31,37,48),(305,y,31,34,32),(326,y,31,32,8)]
 sweep('PontoonCrest'+l,crest,WHITE,40,.18)
 # master rear orange control panel
 panel=[(340,sgn*125),(360,sgn*180),(392,sgn*190),(422,sgn*174),(433,sgn*160),(418,sgn*151),(390,sgn*164),(360,sgn*158)]
 plate('RearOrange'+l,panel,34.2,35.0,ORANGE)
 # fin top orange patch near tip
 panel2=[(402,sgn*182),(424,sgn*182),(418,sgn*185),(408,sgn*185)]
 plate('FinOrange'+l,panel2,91,97,ORANGE)
# save
blend=os.path.join(CAD,'Hydrofoam_Final_Master_v91_IDENTITY.blend');bpy.ops.wm.save_as_mainfile(filepath=blend);bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.stl_export(filepath=os.path.join(CAD,'Hydrofoam_Final_Master_v91_IDENTITY.stl'),export_selected_objects=False);print('V91_SAVED')
