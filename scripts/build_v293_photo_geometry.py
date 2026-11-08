import bpy,math,os
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
def mat(name,color,met=.06,rough=.32):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
 p=m.node_tree.nodes.get('Principled BSDF')
 p.inputs['Base Color'].default_value=(*color,1)
 p.inputs['Metallic'].default_value=met;p.inputs['Roughness'].default_value=rough
 return m
white=mat('Pearl white PLA',(.82,.85,.88))
orange=mat('Signal orange PLA',(1,.19,.008))
canopy=mat('Smoked panoramic canopy',(.025,.035,.052),.27,.12)
skid=mat('Black PETG runners',(.018,.022,.028),.12,.42)
metal=mat('Anodized motor metal',(.14,.16,.18),.7,.24)
def mesh(name,vertices,faces,material,smooth=True):
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update()
 o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
 o.data.materials.append(material)
 for p in me.polygons:p.use_smooth=smooth
 return o
def closed_loft(name,rings,material,segments=28):
 v=[];faces=[]
 for x,cy,w,zt,zb in rings:
  for j in range(segments):
   a=2*math.pi*j/segments;ss=math.sin(a)
   v.append((x,cy+w*math.cos(a),(zt+zb)/2+(zt-zb)/2*(ss if ss>0 else ss*.85)))
 for k in range(len(rings)-1):
  for j in range(segments):
   a=k*segments+j;b=k*segments+(j+1)%segments
   faces.append((a,b,b+segments,a+segments))
 faces.append(tuple(range(segments-1,-1,-1)))
 faces.append(tuple((len(rings)-1)*segments+j for j in range(segments)))
 return mesh(name,v,faces,material)
def panel(name,outline,z,thick,material):
 n=len(outline)
 vv=[(x,y,z(x,y)) for x,y in outline]+[(x,y,z(x,y)-thick) for x,y in outline]
 cx=sum(x for x,y in outline)/n;cy=sum(y for x,y in outline)/n
 vv.extend([(cx,cy,z(cx,cy)),(cx,cy,z(cx,cy)-thick)])
 f=[]
 for i in range(n):
  j=(i+1)%n
  f.extend([(2*n,i,j),(2*n+1,n+j,n+i),(i,j,n+j,n+i)])
 return mesh(name,vv,f,material,False)
def beam(name,p1,p2,r,material):
 a=Vector(p1);b=Vector(p2);dif=b-a
 bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=r,depth=dif.length,location=(a+b)/2)
 o=bpy.context.object;o.name=name;o.rotation_euler=dif.to_track_quat('Z','Y').to_euler();o.data.materials.append(material)
 return o
# Master image: CENTER NOSE FIRST. Bow extends 60-70 mm beyond float tips.
central=[
 (-225,0,1,24,23),(-218,0,9,28,20),(-204,0,20,33,17),(-186,0,30,39,13),
 (-155,0,39,47,7),(-125,0,43,54,6),(-90,0,44,58,7),(-55,0,43,57,10),
 (-20,0,40,53,15),(22,0,37,48,21),(67,0,36,43,25),
 (113,0,35,40,28),(164,0,31,34,28),(203,0,13,30,27)]
closed_loft('01 Master Central fuselage',central,white)
# Long dark cockpit with tight pointed forward end, widening midbody then tapering back
closed_loft('02 Black canopy',[
 (-162,0,1,56,53),(-153,0,11,62,52),(-134,0,20,68,54),(-108,0,23,72,57),
 (-78,0,23,73,60),(-47,0,20,70,59),(-26,0,14,65,58),(-11,0,1,59,57)
 ],canopy)
# PonTons are set back 65 mm relative to center tip; water planing keel is flatter aft.
for s,side in [(-1,'Left'),(1,'Right')]:
 stations=[
 (-164,119*s,1,25,22),(-159,119*s,9,29,16),(-149,119*s,18,31,9),
 (-130,119*s,26,33,1),(-105,119*s,29,35,-5),(-72,119*s,30,37,-8),
 (-26,119*s,30,37,-9),(16,119*s,30,36,-8),(58,119*s,28,34,-3),
 (92,119*s,26,32,7),(125,119*s,22,30,17),(153,119*s,13,28,23),
 (170,119*s,3,27,25)]
 closed_loft('10 Planing float '+side,stations,white)
 # narrow orange top-edge bow stripe (not an orange nose cone)
 stripe=[
 (-164,119*s,1,26,25),(-157,119*s,6,31,28),(-143,119*s,7,34,31),
 (-125,119*s,6,35,33),(-107,119*s,4,36,34),(-90,119*s,1,37,36)]
 closed_loft('11 Orange float leading stripe '+side,stripe,orange,16)
 # full length removable skid tapered toward each end
 closed_loft('12 Black PETG skid '+side,[
 (-95,119*s,6,-9,-12),(-84,119*s,11,-12,-15),(-45,119*s,12,-13,-17),
 (0,119*s,11,-12,-16),(35,119*s,10,-9,-12),(52,119*s,5,-4,-5)],skid,12)
 # wings follow sweep from central shell inwards to the outer float rear shoulder
 surf=[
 (-165,30*s),(-143,48*s),(-116,71*s),(-89,88*s),(-55,102*s),
 (-5,128*s),(51,150*s),(96,184*s),(137,231*s),
 (157,236*s),(170,226*s),(166,180*s),(145,158*s),
 (105,133*s),(72,94*s),(25,53*s),(-62,37*s)]
 panel('20 Swept blended wing '+side,surf,lambda x,y:35-3*abs(y)/240+2*math.sin((x+225)/450*math.pi),3,white)
 # livery sweeps out from canopy shoulders, tapering toward outer pontoon
 stripe_poly=[(-156,36*s),(-143,40*s),(-114,61*s),(-65,93*s),(-24,122*s),
 (5,142*s),(34,150*s),(3,139*s),(-35,109*s),(-80,78*s),(-137,34*s)]
 panel('21 Orange wing curve '+side,stripe_poly,lambda x,y:37.6-3*abs(y)/240,0.45,orange)
 # Winglet trailing outer section, orange wingtips
 outer=[(104,141*s),(147,174*s),(176,222*s),(157,237*s),(119,209*s),(87,156*s)]
 panel('22 Outer rear wing '+side,outer,lambda x,y:31.2,3.1,white)
 panel('23 Orange wingtip '+side,[(151,211*s),(170,230*s),(160,237*s),(145,224*s)],
       lambda x,y:33.1,0.6,orange)
 # independent control surfaces at rear extending from center to outer fin
 elev=[(130,43*s),(175,54*s),(207,112*s),(204,176*s),(174,162*s),(147,119*s)]
 panel('24 Elevon '+side,elev,lambda x,y:30,2.4,white)
 panel('25 Orange elevon trim '+side,[(194,82*s),(210,105*s),(209,174*s),(202,163*s)],
       lambda x,y:31,0.7,orange)
 # tall curved rear fins fitted near side extremities; projecting up 95mm
 fin=[(145,181*s,31),(165,181*s,45),(185,181*s,75),
      (204,181*s,110),(213,181*s,112),(220,181*s,48),(219,181*s,30)]
 def finpanel(name,vertices,material):
  n=len(vertices);v=vertices+[(x,y+s*3,z) for x,y,z in vertices];f=[]
  for i in range(1,n-1):f.extend([(0,i,i+1),(n,n+i+1,n+i)])
  for i in range(n):f.append((i,(i+1)%n,(i+1)%n+n,i+n))
  return mesh(name,v,f,material,False)
 finpanel('30 Tail fin '+side,fin,white)
 finpanel('31 Tail fin orange top '+side,[(197,181*s,86),(204,181*s,110),
                                      (213,181*s,112),(213,181*s,95)],orange)
 # dark fin upper inset
 finpanel('32 Tail fin dark inset '+side,[(166,181*s,55),(193,181*s,84),
                                        (209,181*s,105),(198,181*s,94)],canopy)
 # embedded hatch and dorsal vent on each float
 panel('33 Float service panel '+side,[(-65,105*s),(-37,105*s),
        (-37,109*s),(-65,109*s)],lambda x,y:38,0.3,metal)
# Distinct motor bridge behind canopy, motor axis along longitudinal X
for s in [-1,1]:
 beam('40 Arch motor foot',(102,29*s,37),(120,24*s,83),4.6,white)
 beam('41 Arch inclined arm',(120,24*s,83),(141,14*s,100),4.7,white)
beam('42 Arch top brace',(141,-14,100),(141,14,100),4,white)
beam('43 Brushless motor',(145,0,102),(176,0,102),13,metal)
beam('44 Orange bell',(165,0,102),(169,0,102),15.2,orange)
beam('45 Prop spindle',(177,0,102),(183,0,102),3.1,metal)
for s in [-1,1]:
 beam('46 Pusher prop blade',(184,0,102),(184,2*s,102+50*s),4,canopy)
# hardware details, screw-like heads on central hatch
for x,y in [(23,30),(23,-30),(59,30),(59,-30)]:
 bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=2.4,location=(x,y,47))
 bpy.context.object.name='50 Access panel screw';bpy.context.object.data.materials.append(metal)
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.stl'),export_selected_objects=False)
print('V293_REAL_PHOTO_GEOMETRY',len([o for o in bpy.data.objects if o.type=='MESH']))
