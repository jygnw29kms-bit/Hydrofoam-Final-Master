import bpy,math,os
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v305_P2S_ASSEMBLY.blend'))
# Frame coordinates and station envelope from original v293 for each master float.
stations=[
 (-164,0.4,25,22),(-159,9,29,16),(-149,18,31,9),(-130,26,33,1),
 (-105,29,35,-5),(-72,30,37,-8),(-26,30,37,-9),
 (16,30,36,-8),(58,28,34,-3),(92,26,32,7),
 (125,22,30,17),(153,13,28,23),(170,3,27,25)]
# Explicit angular chine cross section (from square-shouldered flat deck to
# steep dry sidewall and sharply broken lower chine). The outline stays
# star-shaped and does not introduce any extra leading hulls or appendages.
profile=[(0.,1.),(.66,1.),(.86,.78),(1.,.38),(1.,-.21),
 (.77,-.60),(.37,-.93),(0.,-1.),(-.37,-.93),
 (-.77,-.60),(-1.,-.21),(-1.,.38),(-.86,.78),(-.66,1.)]
anchors=sorted([(math.atan2(z,y),math.hypot(y,z)) for y,z in profile])
def envelope(x):
 x=max(stations[0][0],min(stations[-1][0],x))
 for i in range(len(stations)-1):
  xa,wa,ta,ba=stations[i];xb,wb,tb,bb=stations[i+1]
  if x<=xb:
   f=(x-xa)/(xb-xa)
   return (wa+(wb-wa)*f,ta+(tb-ta)*f,ba+(bb-ba)*f)
 return stations[-1][1:]
def poly_radius(angle):
 # theta wraps from [-pi,pi]; radius interpolation yields polygonal corners
 angle=(angle+math.pi)%(2*math.pi)-math.pi
 vals=anchors
 for i in range(len(vals)):
  a0,r0=vals[i]
  a1,r1=vals[(i+1)%len(vals)]
  if i==len(vals)-1:a1+=2*math.pi
  v=angle
  if i==len(vals)-1 and v<a0:v+=2*math.pi
  if a0<=v<=a1:
   f=(v-a0)/(a1-a0)
   return r0+(r1-r0)*f
 return 1.0
# radial squaring with control factor prevents the cavity walls from collapsing.
def mapped(p):
 x,y,z=p
 s=-1 if y<0 else 1
 cy=s*119.
 w,zt,zb=envelope(x)
 mid=(zt+zb)*.5
 amp=(zt-zb)*.5
 if w<.2 or amp<.2:return Vector((x,y,z))
 dy=(y-cy)/w
 dz=(z-mid)/(amp if z>=mid else amp*.85)
 rr=math.hypot(dy,dz)
 if rr<1e-7:return Vector((x,y,z))
 theta=math.atan2(dz,dy)
 # polygon radius in direction theta; inner cavities share identical map
 radius=poly_radius(theta)
 u=rr*math.cos(theta)*radius*.95
 v=rr*math.sin(theta)*radius*.97
 # 92% hard-chine transform; keep the existing inner surface offset
 t=.92
 newy=cy+w*(dy*(1-t)+u*t)
 newz=mid+amp*((dz*(1-t)+v*t) if z>=mid else .85*(dz*(1-t)+v*t))
 return Vector((x,newy,newz))
names=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 name=o.name.lower()
 if ('v305 hollow float_' in name or
     'orange float leading stripe' in name or
     'black petg skid' in name):
  before=[v.co.copy() for v in o.data.vertices]
  displacements=[]
  for v in o.data.vertices:
   new=mapped(v.co)
   displacements.append((new-v.co).length)
   v.co=new
  o.data.update()
  # keep both side profiles matched with same curve shape
  names.append((o.name,round(max(displacements),3),round(sum(displacements)/len(displacements),3)))
  print('CHINED',o.name,'max_mm',names[-1][1],'avg_mm',names[-1][2])
# Fillet-free faceted prototype uses original existing segmentation and
# material assignments; no changes to mid hull, wings, fins or motor geometry.
output=os.path.join(R,'cad','Hydrofoam_Final_Master_v306_FACETED_MASTER_FLOATS.blend')
bpy.ops.wm.save_as_mainfile(filepath=output)
folder=os.path.join(R,'print','v306_faceted_float_modules')
os.makedirs(folder,exist_ok=True)
for o in bpy.data.objects:
 if o.type!='MESH' or not o.name.startswith('v305 HOLLOW float_'):continue
 bpy.ops.object.select_all(action='DESELECT')
 o.select_set(True);bpy.context.view_layer.objects.active=o
 fname=o.name.replace('v305 HOLLOW ','').replace(' ','_')
 bpy.ops.wm.stl_export(filepath=os.path.join(folder,fname+'.stl'),export_selected_objects=True)
print('V306_COMPLETED',len(names),'adjusted objects')
