import bpy, math, os
from mathutils import Vector
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad'); os.makedirs(CAD,exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
def mat(n,c): m=bpy.data.materials.new(n); m.diffuse_color=(*c,1); return m
WHITE=mat('Body',(0.92,0.92,0.92)); DARK=mat('Canopy',(0.025,0.035,0.045)); ORANGE=mat('Accent',(1,.24,.025)); BLACK=mat('Black',(.015,.015,.015))
def sweep(name,st,ma,rings=48,flat=.18):
 v=[]; f=[]
 for x,yc,bot,top,w in st:
  h=top-bot
  for j in range(rings):
   a=2*math.pi*j/rings; yy=yc+w*.5*math.cos(a); q=(math.sin(a)+1)/2
   if q<flat:q=flat*(q/flat)**1.8
   v.append((x,yy,bot+h*q))
 n=len(st)
 for i in range(n-1):
  for j in range(rings):f.append((i*rings+j,i*rings+(j+1)%rings,(i+1)*rings+(j+1)%rings,(i+1)*rings+j))
 f += [tuple(range(rings-1,-1,-1)),tuple((n-1)*rings+j for j in range(rings))]
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(ma)
 for p in me.polygons:p.use_smooth=True
 bev=o.modifiers.new('Soft','BEVEL');bev.width=.7;bev.segments=2
 return o
def plate(name,pts,z0,z1,ma):
 v=[(x,y,z0) for x,y in pts]+[(x,y,z1) for x,y in pts];n=len(pts);f=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n))
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(v,[],f);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(ma)
 bev=o.modifiers.new('Soft','BEVEL');bev.width=1.2;bev.segments=3
 return o
# Exact outer planform traced from final-master top view
outline=[(66.27,-138.42),(81.24,-145.9),(100.48,-146.97),(112.23,-154.45),(164.61,-168.35),(269.36,-185.45),(278.98,-183.31),(338.84,-241.03),(364.49,-238.9),(378.38,-233.55),(378.38,-186.52),(380.52,-184.38),(448.93,-182.24),(448.93,-177.97),(425.42,-166.21),(413.66,-167.28),(391.21,-164.07),(385.87,-160.87),(388.0,-158.73),(402.97,-157.66),(401.9,-142.7),(407.24,-81.77),(378.38,-70.01),(369.83,-75.36),(349.52,-62.53),(347.39,-58.25),(352.73,-56.12),(354.87,-44.36),(354.87,-4.81),(359.14,-1.6),(407.24,0.53),(359.14,1.6),(352.73,6.95),(353.8,36.88),(351.66,57.19),(363.42,64.67),(384.8,74.29),(389.07,73.22),(408.31,82.84),(401.9,157.66),(433.97,170.49),(448.93,179.04),(450.0,182.24),(427.55,183.31),(426.48,181.18),(408.31,181.18),(380.52,184.38),(378.38,233.55),(364.49,238.9),(338.84,241.03),(286.46,190.8),(268.29,176.9),(261.88,177.97),(153.92,155.52),(127.2,153.38),(118.65,149.11),(83.37,146.97),(69.48,141.63),(66.27,138.42),(66.27,126.66),(69.48,123.46),(88.72,118.11),(123.99,113.84),(127.2,111.7),(123.99,97.8),(113.3,90.32),(99.41,68.94),(80.17,52.91),(75.89,46.5),(8.55,15.5),(0.0,4.81),(1.07,-8.02),(7.48,-14.43),(76.96,-46.5),(103.68,-74.29),(123.99,-107.42),(121.85,-113.84),(91.92,-117.04),(68.41,-123.46),(66.27,-125.59)]
plate('MasterPlanform',outline,29.0,32.2,WHITE)
# center hull
center=[(0,0,23,27,4),(18,0,18,31,22),(42,0,13,36,42),(78,0,10,41,65),(118,0,9,45,86),(160,0,10,47,102),(205,0,12,45,100),(245,0,15,41,88),(282,0,18,38,70),(315,0,22,36,52),(342,0,26,34,30),(360,0,29,32,10)]
sweep('CenterHull',center,WHITE,52,.18)
can=[(58,0,43,45,5),(78,0,44,51,18),(105,0,45,61,36),(138,0,46,69,55),(173,0,46,68,54),(205,0,45,58,38),(228,0,44,49,10)]
sweep('Canopy',can,DARK,48,.04)
# pontoons per master top view
for sgn,l in [(-1,'L'),(1,'R')]:
 y=sgn*140
 st=[(68,y,20,23,5),(82,y,17,27,18),(105,y,13,32,36),(140,y,10,37,54),(185,y,9,40,62),(235,y,10,39,64),(280,y,13,36,58),(315,y,18,31,40),(330,y,23,27,10)]
 sweep('Sponson'+l,st,WHITE,44,.20)
 sweep('NoseAccent'+l,[(68,y,21,24,5),(83,y,24,29,18),(102,y,28,33,31)],ORANGE,28,.06)
 # narrow orange flow stripe on upper shoulder
 stripe=[(88,sgn*48),(112,sgn*64),(148,sgn*82),(190,sgn*95),(232,sgn*98),(270,sgn*92),(294,sgn*82),(284,sgn*75),(244,sgn*84),(198,sgn*85),(152,sgn*75),(110,sgn*58)]
 plate('Stripe'+l,stripe,33.0,33.7,ORANGE)
 # skid
 bpy.ops.mesh.primitive_cube_add(location=(205,y,6),scale=(82,5,2));bpy.context.object.data.materials.append(BLACK)
# fins exactly near outer tail stations
for sgn,l in [(-1,'L'),(1,'R')]:
 y=sgn*184
 pts=[(340,y,33),(377,y,33),(424,y,76),(418,y,98),(402,y,94),(370,y,67),(340,y,33)]
 verts=[];th=2.4
 for dy in (-th/2,th/2):verts += [(x,y+sgn*dy,z) for x,yy,z in pts]
 n=len(pts);faces=[tuple(range(n)),tuple(range(2*n-1,n-1,-1))]
 for i in range(n-1):faces.append((i,i+1,i+1+n,i+n))
 me=bpy.data.meshes.new('Fin'+l+'Mesh');me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new('Fin'+l,me);bpy.context.collection.objects.link(o);o.data.materials.append(WHITE)
 # orange tip patch
 plate('FinAccent'+l,[(399,sgn*182),(424,sgn*182),(418,sgn*185),(405,sgn*185)],91.0,97.0,ORANGE)
# motor U arch
for y in (-20,20):
 a=Vector((310,y,38));b=Vector((337,y,73));d=b-a;mid=(a+b)/2;bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=3.2,depth=d.length,location=mid);o=bpy.context.object;o.rotation_euler=d.to_track_quat('Z','Y').to_euler();o.data.materials.append(WHITE)
bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=3.2,depth=40,location=(337,0,73),rotation=(math.pi/2,0,0));bpy.context.object.data.materials.append(WHITE)
bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=10.5,depth=30,location=(352,0,73),rotation=(0,math.pi/2,0));bpy.context.object.data.materials.append(DARK)
bpy.ops.mesh.primitive_torus_add(major_radius=11.2,minor_radius=1.4,major_segments=40,minor_segments=10,location=(361,0,73),rotation=(0,math.pi/2,0));bpy.context.object.data.materials.append(ORANGE)
# prop in YZ plane
for ang in (0,math.pi/2):
 bpy.ops.mesh.primitive_cube_add(location=(365,0,73),scale=(1.2,2.0,30));o=bpy.context.object;o.rotation_euler[0]=ang;o.data.materials.append(BLACK)
# save/export
blend=os.path.join(CAD,'Hydrofoam_Final_Master_v70_EXACT_PLANFORM.blend');bpy.ops.wm.save_as_mainfile(filepath=blend);bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.stl_export(filepath=os.path.join(CAD,'Hydrofoam_Final_Master_v70_EXACT_PLANFORM.stl'),export_selected_objects=False);print('V70_SAVED')
