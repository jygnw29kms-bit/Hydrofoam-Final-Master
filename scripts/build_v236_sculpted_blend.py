import bpy, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v234_MASTER_IDENTITY.blend'))
# remove flat wing slabs and their old accent strips
for n in ['WingL','WingR','AccentL','AccentR','RearAccentL','RearAccentR']:
 o=bpy.data.objects.get(n)
 if o:bpy.data.objects.remove(o,do_unlink=True)
WHITE=bpy.data.materials.get('BodyWhite'); ORANGE=bpy.data.materials.get('AccentOrange')
# sculpted half-wing surface with thickness and spanwise crown
stations=[(-182,30,102,20),(-150,34,116,21),(-110,40,124,22),(-55,48,128,23),(10,54,130,23),(70,58,122,22),(115,60,108,21),(150,68,145,20),(185,82,198,19),(220,108,224,18)]
def wing(name,sg):
 rails=7; top=[]; bot=[]
 for x,yi,yo,z0 in stations:
  for j in range(rails):
   t=j/(rails-1); y=sg*(yi+(yo-yi)*t); crown=5.5*math.sin(math.pi*t); z=z0+crown
   top.append((x,y,z)); bot.append((x,y,z-6.0))
 nst=len(stations); verts=top+bot; faces=[]
 def idx(i,j,lower=False):return (nst*rails if lower else 0)+i*rails+j
 for i in range(nst-1):
  for j in range(rails-1):faces.append((idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1)));faces.append((idx(i,j,1),idx(i,j+1,1),idx(i+1,j+1,1),idx(i+1,j,1)))
 for i in range(nst-1):
  faces.append((idx(i,0),idx(i,0,1),idx(i+1,0,1),idx(i+1,0)))
  faces.append((idx(i,rails-1),idx(i+1,rails-1),idx(i+1,rails-1,1),idx(i,rails-1,1)))
 for j in range(rails-1):
  faces.append((idx(0,j),idx(0,j+1),idx(0,j+1,1),idx(0,j,1)))
  faces.append((idx(nst-1,j),idx(nst-1,j,1),idx(nst-1,j+1,1),idx(nst-1,j+1)))
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(WHITE)
 bev=o.modifiers.new('Soft','BEVEL');bev.width=2.2;bev.segments=3
 sub=o.modifiers.new('Flow','SUBSURF');sub.levels=1;sub.render_levels=1
 for p in me.polygons:p.use_smooth=True
 return o
wing('WingL',-1);wing('WingR',1)
# orange accent ribbons as thin beveled curves along forward shoulder and rear tips
def ribbon(name,pts,sg,width=.9):
 cu=bpy.data.curves.new(name+'Curve','CURVE');cu.dimensions='3D';cu.bevel_depth=width;cu.bevel_resolution=3;sp=cu.splines.new('BEZIER');sp.bezier_points.add(len(pts)-1)
 for bp,(x,y,z) in zip(sp.bezier_points,pts):bp.co=(x,sg*y,z);bp.handle_left_type='AUTO';bp.handle_right_type='AUTO'
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(ORANGE)
for sg,s in [(-1,'L'),(1,'R')]:
 ribbon('ShoulderAccent'+s,[(-177,34,25),(-145,72,27),(-105,100,28),(-55,112,28)],sg,1.2)
 ribbon('TailAccent'+s,[(180,150,23),(202,194,22),(220,220,21)],sg,1.5)
# canopy slightly lower/narrower
can=bpy.data.objects.get('Canopy')
if can:can.scale.y*=.94;can.scale.z*=.92;can.location.z-=2
# save/export
blend=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v236_SCULPTED_BLEND.blend');bpy.ops.wm.save_as_mainfile(filepath=blend);bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.stl_export(filepath=os.path.join(ROOT,'cad','Hydrofoam_Final_Master_v236_SCULPTED_BLEND.stl'),export_selected_objects=False)
print('V236_DONE')
