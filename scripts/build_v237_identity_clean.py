import bpy, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v236_SCULPTED_BLEND.blend'))
# remove floating curve accents
for n in ['ShoulderAccentL','ShoulderAccentR','TailAccentL','TailAccentR','SponsonNoseAccentL','SponsonNoseAccentR']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
ORANGE=bpy.data.materials.get('AccentOrange')
def prism(name,pts,z0,z1,matl,bev=1.0):
 vs=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts];n=len(pts);fs=[tuple(range(n-1,-1,-1)),tuple(range(n,2*n))]
 for i in range(n):fs.append((i,(i+1)%n,(i+1)%n+n,i+n))
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(matl);b=o.modifiers.new('Soft','BEVEL');b.width=bev;b.segments=3
# proper long sponson nose stripes
for sg,s in [(-1,'L'),(1,'R')]:
 yc=sg*124; pts=[(-215,yc-7),(-170,yc-9),(-155,yc-5),(-198,yc+5)]
 prism('SponsonNoseAccent'+s,pts,18,20,ORANGE,1.2)
# compact fins around own base pivot
for n in ['FinL','FinR','FinTipL','FinTipR']:
 o=bpy.data.objects.get(n)
 if o:
  for v in o.data.vertices:
   v.co.x=160+(v.co.x-160)*0.82
   v.co.z=20+(v.co.z-20)*0.82
# motor arch lower and inward lean
for n,ang in [('Cube',math.radians(-10)),('Cube.001',math.radians(10))]:
 o=bpy.data.objects.get(n)
 if o:
  o.rotation_euler.x=ang; o.location.z-=5; o.dimensions.z*=0.88
bar=bpy.data.objects.get('Cube.002')
if bar:bar.location.z-=8;bar.dimensions.y*=0.86
for n in ['Cylinder','Sphere','Cube.003','Cube.004']:
 o=bpy.data.objects.get(n)
 if o:o.location.z-=8
# slightly shorten rear wing reach
for n in ['WingL','WingR']:
 o=bpy.data.objects.get(n)
 if o:
  for v in o.data.vertices:
   if v.co.x>150:v.co.x=150+(v.co.x-150)*0.88
blend=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v237_IDENTITY_CLEAN.blend');bpy.ops.wm.save_as_mainfile(filepath=blend);bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.stl_export(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v237_IDENTITY_CLEAN.stl'),export_selected_objects=False)
print('V237_DONE')
