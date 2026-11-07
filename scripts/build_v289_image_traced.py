import bpy,os,json,math
from mathutils import Vector
from mathutils.geometry import tessellate_polygon
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v288_BOTTOM_FIT_CLEAN.blend'))
# Retain detailed components, discard old guessed wing/deck/pontoon geometry.
for name in ['CenterHull','WingDeckL','WingDeckR','SponsonL','SponsonR','SkidL','SkidR']:
 o=bpy.data.objects.get(name)
 if o:bpy.data.objects.remove(o,do_unlink=True)
tr=json.load(open(os.path.join(R,'reference','top_v4_traced_outline.json')))
pts=[(max(-225,min(225,x)),y) for x,y in tr['contour']]
# Remove duplicates after x clamping.
points=[]
for p in pts:
 if not points or abs(p[0]-points[-1][0])+abs(p[1]-points[-1][1])>0.03:points.append(p)
if points[0]==points[-1]:points.pop()
white=bpy.data.materials.get('BodyWhite')
orange=bpy.data.materials.get('AccentOrange')
def make(name,verts,faces,material):
 me=bpy.data.meshes.new(name+'Mesh');me.from_pydata(verts,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
 if material:ob.data.materials.append(material)
 return ob
# Main deck follows *actual image outline*: mathematically identical top-view projection,
# with only 6 mm hull thickness. It is not the previous v288 deck.
n=len(points)
def deck_z(x,y):
 return 19.5 + 5.5*math.exp(-(y/92)**2) + 1.4*math.sin((x+225)/450*math.pi)
top=[(x,y,deck_z(x,y)) for x,y in points]
bot=[(x,y,deck_z(x,y)-6) for x,y in points]
faces=[]
for tri in tessellate_polygon([[Vector(v) for v in top]]):
 ids=list(tri)
 faces.append(tuple(ids))
 faces.append(tuple(n+i for i in reversed(ids)))
for i in range(n):
 j=(i+1)%n
 faces.append((i,j,j+n,i+n))
main=make('IMAGE_MASTER_OutlineDeck',top+bot,faces,white)
for p in main.data.polygons:p.use_smooth=False
# Triple longitudinal bodies with pointed forefoot and gently lifting rear release.
def loft(name,stations,center_fn,half_fn,top_fn,bot_fn,mat):
 verts=[];rings=16
 for x in stations:
  yc=center_fn(x);w=half_fn(x);zt=top_fn(x);zb=bot_fn(x);zc=(zt+zb)*.5;hz=(zt-zb)*.5
  for j in range(rings):
   a=2*math.pi*j/rings
   y=yc+w*math.cos(a)
   z=zc+hz*math.sin(a)
   verts.append((x,y,z))
 faces=[]
 for k in range(len(stations)-1):
  for j in range(rings):
   a=k*rings+j;b=k*rings+(j+1)%rings;c=b+rings;dd=a+rings
   faces.append((a,b,c,dd))
 faces.append(tuple(reversed(range(rings))))
 faces.append(tuple((len(stations)-1)*rings+j for j in range(rings)))
 obj=make(name,verts,faces,mat)
 for p in obj.data.polygons:p.use_smooth=True
 return obj
def itp(x,stations,values):
 if x<=stations[0]:return values[0]
 if x>=stations[-1]:return values[-1]
 for i in range(len(stations)-1):
  if stations[i]<=x<=stations[i+1]:
   t=(x-stations[i])/(stations[i+1]-stations[i])
   t=t*t*(3-2*t)
   return values[i]*(1-t)+values[i+1]*t
xs=[-225,-215,-200,-175,-145,-112,-85,-45,0,45,90,140,185,215]
w=[1,12,24,33,40,49,53,56,55,52,46,37,28,18]
zt=[24,29,36,42,45,50,55,61,65,58,45,37,31,27]
zb=[20,12,0,-8,-10,-9,-8,-6,-3,2,11,17,20,21]
loft('IMAGE_MASTER_CenterPod',xs,lambda x:0,lambda x:itp(x,xs,w),lambda x:itp(x,xs,zt),lambda x:itp(x,xs,zb),white)
for sg,name in [(-1,'L'),(1,'R')]:
 xs2=[-165,-158,-145,-125,-95,-60,-20,25,75,120,165,200,220]
 cw=[136,145,153,157,160,163,166,168,174,182,185,177,170]
 wi=[2,13,21,26,28,30,30,29,29,27,25,20,4]
 tops=[25,29,35,36,37,37,36,35,35,33,31,29,26]
 bots=[22,13,1,-7,-8,-8,-8,-6,-2,5,12,18,22]
 loft('IMAGE_MASTER_Sponson'+name,xs2,lambda x:sg*itp(x,xs2,cw),lambda x:itp(x,xs2,wi),lambda x:itp(x,xs2,tops),lambda x:itp(x,xs2,bots),white)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v289_IMAGE_TRACED.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v289_IMAGE_TRACED.stl'),export_selected_objects=False)
print('IMAGE_TRACED_V289',n,'contour_points',len(faces),'deck_faces')
