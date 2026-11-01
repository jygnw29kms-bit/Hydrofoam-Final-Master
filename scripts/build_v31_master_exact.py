import FreeCAD as App
import Part, Mesh, os, math, json
from PIL import Image
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
REF=os.path.join(ROOT,'reference'); CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v31_parts'); DOCS=os.path.join(ROOT,'docs')
os.makedirs(CAD,exist_ok=True); os.makedirs(PARTS,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v31')

def add(n,l,s,mat='PLA',vis=True):
 o=doc.addObject('PartDesign::Feature',n); o.Label=l; o.Shape=s
 o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat
 o.addProperty('App::PropertyBool','Visual','Manufacturing').Visual=vis
 return o

def split_x(shape,x,name,mat='PLA',vis=True):
 b=shape.BoundBox; p=8
 a=shape.common(Part.makeBox(x-b.XMin+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(b.XMin-p,b.YMin-p,b.ZMin-p)))
 c=shape.common(Part.makeBox(b.XMax-x+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(x,b.YMin-p,b.ZMin-p)))
 add(name+'_Front',name+' front',a,mat,vis); add(name+'_Rear',name+' rear',c,mat,vis)

def ellwire(x,y,z,w,h,n=36):
 pts=[App.Vector(x,y+w*.5*math.cos(2*math.pi*i/n),z+h*.5*math.sin(2*math.pi*i/n)) for i in range(n)]; pts.append(pts[0]); return Part.makePolygon(pts)
def flatwire(x,y,z,w,h,n=32):
 pts=[]
 for i in range(n):
  a=2*math.pi*i/n; cy=math.cos(a); sz=math.sin(a); zz=z+h*.5*sz
  if sz<-.25: zz=max(zz,z-h*.36)
  pts.append(App.Vector(x,y+w*.5*cy,zz))
 pts.append(pts[0]); return Part.makePolygon(pts)
def loft(sec,wire=ellwire): return Part.makeLoft([wire(*s) for s in sec],True,False)
def shell(sec,t=.8,wire=ellwire):
 out=loft(sec,wire); inn=[(x,y,z,max(2,w-2*t),max(2,h-2*t)) for x,y,z,w,h in sec]
 try:return out.cut(loft(inn,wire))
 except:return out

# Exact Final Master top silhouette. In mask, image Y is model longitudinal X.
im=Image.open(os.path.join(REF,'final_master_top_mask_v3.png')).convert('L')
b=im.getbbox(); pix=im.load(); x0,y0,x1,y1=b
L=450.0; W=482.0; sx=W/max(1,x1-x0-1); sl=L/max(1,y1-y0-1)
left=[]; right=[]
step=4
for yy in range(y0,y1,step):
 xs=[xx for xx in range(x0,x1) if pix[xx,yy]>127]
 if not xs: continue
 X=(yy-y0)*sl; left.append((X,(min(xs)-(x0+x1-1)/2)*sx)); right.append((X,(max(xs)-(x0+x1-1)/2)*sx))
poly=left+right[::-1]
vs=[App.Vector(x,y,34) for x,y in poly]; vs.append(vs[0]); face=Part.Face(Part.makePolygon(vs)); plan=face.extrude(App.Vector(0,0,2.0))
split_x(plan,225,'MasterPlanform','PLA',True)

# Exact side-mask driven longitudinal body height, clipped so fins remain separate objects.
sid=Image.open(os.path.join(REF,'final_master_side_mask_v3.png')).convert('L'); sb=sid.getbbox(); sp=sid.load(); ax0,ay0,ax1,ay1=sb
ss=L/max(1,ax1-ax0-1)
def side_bounds(X):
 xx=int(round(ax0+X/ss)); xx=max(ax0,min(ax1-1,xx)); ys=[yy for yy in range(ay0,ay1) if sp[xx,yy]>127]
 if not ys:return (10,45)
 ztop=(ay1-1-min(ys))*ss; zbot=(ay1-1-max(ys))*ss
 return zbot,ztop

# Central fuselage: exact side height where useful, width kept as master centerbody proportions.
sec=[]
for X in [0,15,35,60,90,125,165,205,245,285,320,350]:
 zb,zt=side_bounds(X); zt=min(zt,78); zb=max(8,min(zb,30)); h=max(6,zt-zb); z=(zt+zb)/2
 # smooth width schedule derived from master center pod
 w= max(5, 108*math.sin(math.pi*min(max(X,0),360)/360.0)**0.72) if X<360 else 8
 sec.append((X,0,z,w,h))
body=shell(sec,.8,ellwire); split_x(body,190,'CenterBody','PLA',True)

# Twin planing sponsons, master proportions.
for side,sgn in [('L',-1),('R',1)]:
 y=sgn*137
 s=[]
 for X,w,h in [(18,8,8),(38,26,18),(68,46,28),(105,58,36),(155,62,40),(220,62,40),(280,58,36),(330,46,28),(370,28,18),(392,8,8)]:
  zb,zt=side_bounds(min(X,440)); z=23+0.15*(zt-45); s.append((X,y,z,w,h))
 sh=shell(s,.8,flatwire); split_x(sh,205,'Sponson_'+side,'PLA',True)
 skid=Part.makeBox(238,11,1.5,App.Vector(78,y-5.5,7)); add('Skid_'+side,'PETG skid '+side,skid,'PETG',True)

# Canopy, master long teardrop.
can=[(62,0,49,8,5),(82,0,58,30,15),(112,0,68,54,26),(146,0,74,66,32),(178,0,72,62,30),(207,0,64,43,21),(229,0,55,12,7)]
add('Canopy','Canopy/service hatch',shell(can,.8,ellwire),'PLA',True)

# Motor arch and firewall.
for side,y in [('L',-22),('R',22)]:
 a=[(292,y,40,8,7),(303,y,52,10,15),(312,y,67,11,21),(320,y,81,9,12)]
 add('MotorLeg_'+side,'Motor arch '+side,loft(a,ellwire),'PETG',True)
add('MotorBridge','Motor bridge',Part.makeCylinder(5,44,App.Vector(320,-22,81),App.Vector(0,1,0)),'PETG',True)
add('Firewall','Motor firewall',Part.makeCylinder(16,5,App.Vector(320,0,81),App.Vector(1,0,0)),'PETG',True)

# Twin swept fins and integrated rudders, scaled to master side image.
for side,sgn in [('L',-1),('R',1)]:
 y=sgn*176
 p=[App.Vector(330,y,36),App.Vector(365,y,39),App.Vector(399,y,92),App.Vector(410,y,126),App.Vector(382,y,119),App.Vector(330,y,36)]
 fin=Part.Face(Part.makePolygon(p)).extrude(App.Vector(0,sgn*1.6,0)); add('Fin_'+side,'Fin '+side,fin,'PLA',True)
 r=[App.Vector(382,y,49),App.Vector(420,y,47),App.Vector(420,y,91),App.Vector(410,y,126),App.Vector(382,y,49)]
 rud=Part.Face(Part.makePolygon(r)).extrude(App.Vector(0,sgn*1.6,0)); add('Rudder_'+side,'Rudder '+side,rud,'PLA',True)

# Internal RC packaging, hidden in renders.
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(125,-19,35)),'REFERENCE',False)
add('BatteryRails','Battery rails',Part.makeBox(155,3,3,App.Vector(105,-23,34)).fuse(Part.makeBox(155,3,3,App.Vector(105,20,34))),'PETG',False)
for i,(x,y,z) in enumerate([(245,-48,38),(245,36,38),(324,-10,40),(332,10,46)],1): add(f'Servo{i}Envelope',f'Servo {i}',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE',False)

doc.recompute(); phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]; vis=[o for o in phys if getattr(o,'Visual',False)]
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v31_MASTER_EXACT.FCStd'); doc.saveAs(fc)
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v31_MASTER_EXACT.step')); Mesh.export(vis,os.path.join(CAD,'Hydrofoam_Final_Master_v31_MASTER_EXACT_visual.stl'))
a=[]
for o in phys:
 Mesh.export([o],os.path.join(PARTS,o.Name+'.stl')); bb=o.Shape.BoundBox; a.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':bb.XLength,'dy':bb.YLength,'dz':bb.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':bb.XLength<=256 and bb.YLength<=256 and bb.ZLength<=256})
json.dump(a,open(os.path.join(DOCS,'V31_PART_AUDIT.json'),'w'),indent=2)
print('V31_SAVED',len(phys),'FIT',sum(x['fits_P2S'] for x in a),'VIS',len(vis))

