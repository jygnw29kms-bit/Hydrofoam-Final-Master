import bpy, os
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v237_IDENTITY_CLEAN.blend'))
WHITE=bpy.data.materials.get('BodyWhite')
# remove rounded pods
for n in ['SponsonL','SponsonR']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
secs=[(-215,5,8,4),(-198,28,20,6),(-160,48,30,9),(-105,58,38,11),(-40,62,40,12),(20,58,38,12),(72,46,30,10),(105,28,20,8),(122,7,8,6)]
def chine(name,yc):
 verts=[];faces=[]; n=10
 for x,w,h,z in secs:
  pts=[(.22*w,.50*h),(.42*w,.32*h),(.50*w,0),(.46*w,-.28*h),(.25*w,-.48*h),(-.25*w,-.48*h),(-.46*w,-.28*h),(-.50*w,0),(-.42*w,.32*h),(-.22*w,.50*h)]
  for yy,zz in pts:verts.append((x,yc+yy,z+zz))
 for j in range(len(secs)-1):
  for i in range(n):a=j*n+i;b=j*n+(i+1)%n;c=(j+1)*n+(i+1)%n;d=(j+1)*n+i;faces.append((a,b,c,d))
 faces.append(tuple(range(n-1,-1,-1)));faces.append(tuple((len(secs)-1)*n+i for i in range(n)))
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(WHITE)
 bev=o.modifiers.new('EdgeRadius','BEVEL');bev.width=2.0;bev.segments=3
 return o
chine('SponsonL',-124);chine('SponsonR',124)
# skids align directly under new pods
for n,y in [('SkidL',-124),('SkidR',124)]:
 o=bpy.data.objects.get(n)
 if o:o.location.y=0
# save/export
blend=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v238_PLANING_SPONSONS.blend');bpy.ops.wm.save_as_mainfile(filepath=blend);bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.stl_export(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v238_PLANING_SPONSONS.stl'),export_selected_objects=False)
print('V238_DONE')
