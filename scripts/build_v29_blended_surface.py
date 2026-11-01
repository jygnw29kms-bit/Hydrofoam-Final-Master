import FreeCAD as App
import Part, Mesh, os, math, json
from PIL import Image
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v29_parts'); DOCS=os.path.join(ROOT,'docs'); CMP=os.path.join(ROOT,'comparison','v20')
os.makedirs(CAD,exist_ok=True); os.makedirs(PARTS,exist_ok=True)
# Read final-master top silhouette exactly as previous image-driven builds.
top=Image.open(os.path.join(CMP,'master_top_crop.png')).convert('RGB')
def mask(im):
 m=Image.new('L',im.size,0); p=im.load(); q=m.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,b=p[x,y]; mx=max(r,g,b); mn=min(r,g,b)
   if (r+g+b)/3<238 or mx-mn>18:q[x,y]=255
 return m
M=mask(top); b=M.getbbox(); M=M.crop(b); W,H=M.size; px=M.load(); mid=H/2; SY=482/max(1,H-1)
def runs(ix):
 ys=[y for y in range(H) if px[min(W-1,max(0,ix)),y]>127]
 if not ys:return []
 out=[]; s=l=ys[0]
 for y in ys[1:]:
  if y>l+1:
   if l-s>2:out.append((s,l))
   s=y
  l=y
 if l-s>2:out.append((s,l))
 return out
raw=[]
for i in range(31):
 ix=round(i*(W-1)/30); rr=runs(ix); infos=[((a+c)/2,c-a+1,a,c) for a,c in rr]
 rec={'x':i*15.0,'bw':None,'sy':None,'sw':None,'env':None}
 if infos:
  cen=min(infos,key=lambda z:abs(z[0]-mid)); rec['env']=max(max(abs(z[2]-mid),abs(z[3]-mid)) for z in infos)*SY
  if cen[1]<H*.5:rec['bw']=cen[1]*SY
  ou=[z for z in infos if abs(z[0]-mid)>H*.12 and z[1]<H*.3]
  if ou: rec['sy']=sum(abs(z[0]-mid)*SY for z in ou)/len(ou);rec['sw']=sum(z[1]*SY for z in ou)/len(ou)
 raw.append(rec)
def fill(k,d):
 v=[r[k] for r in raw]; kn=[i for i,x in enumerate(v) if x is not None]; out=[]
 for i,x in enumerate(v):
  if x is not None:out.append(x);continue
  lo=max([j for j in kn if j<i],default=None);hi=min([j for j in kn if j>i],default=None)
  if lo is None and hi is None:out.append(d)
  elif lo is None:out.append(v[hi])
  elif hi is None:out.append(v[lo])
  else:
   t=(i-lo)/(hi-lo);out.append(v[lo]*(1-t)+v[hi]*t)
 return out
def sm(v):return [sum(v[max(0,i-1):min(len(v),i+2)])/len(v[max(0,i-1):min(len(v),i+2)]) for i in range(len(v))]
bw=sm(fill('bw',90)); sy=sm(fill('sy',137)); sw=sm(fill('sw',58)); env=sm(fill('env',230))
# Use latest station correction if available.
cf=os.path.join(DOCS,'V28_STATION_CORRECTIONS.json')
if os.path.exists(cf):
 c=json.load(open(cf)); bw=[bw[i]*c['body'][i] for i in range(31)];sy=[sy[i]*c['spy'][i] for i in range(31)];sw=[sw[i]*c['spw'][i] for i in range(31)];env=[env[i]*c['env'][i] for i in range(31)]
# Side profile target.
side=Image.open(os.path.join(CMP,'master_side_crop.png')).convert('RGB'); SM=mask(side); sb=SM.getbbox();SM=SM.crop(sb);SW,SH=SM.size;sp=SM.load();SS=450/max(1,SW-1)
stop=[];sbot=[]
for i in range(31):
 ix=round(i*(SW-1)/30);ys=[y for y in range(SH) if sp[ix,y]>127]
 stop.append(8+(SH-1-min(ys))*SS if ys else None);sbot.append(8+(SH-1-max(ys))*SS if ys else None)
def fs(v,d):
 kn=[i for i,x in enumerate(v) if x is not None];o=[]
 for i,x in enumerate(v):
  if x is not None:o.append(x);continue
  lo=max([j for j in kn if j<i],default=None);hi=min([j for j in kn if j>i],default=None)
  if lo is None:o.append(v[hi] if hi is not None else d)
  elif hi is None:o.append(v[lo])
  else:
   t=(i-lo)/(hi-lo);o.append(v[lo]*(1-t)+v[hi]*t)
 return o
stop=fs(stop,75);sbot=fs(sbot,8)
doc=App.newDocument('Hydrofoam_Final_Master_v29')
def add(n,l,s,mat='PLA',vis=True):
 o=doc.addObject('PartDesign::Feature',n);o.Label=l;o.Shape=s;o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat;o.addProperty('App::PropertyBool','Visual','Manufacturing').Visual=vis;return o
def polywire(x,y,z,w,h):
 pts=[App.Vector(x,y,z+h*.5),App.Vector(x,y-w*.35,z+h*.34),App.Vector(x,y-w*.5,z+h*.04),App.Vector(x,y-w*.46,z-h*.30),App.Vector(x,y-w*.27,z-h*.5),App.Vector(x,y+w*.27,z-h*.5),App.Vector(x,y+w*.46,z-h*.30),App.Vector(x,y+w*.5,z+h*.04),App.Vector(x,y+w*.35,z+h*.34),App.Vector(x,y,z+h*.5)];return Part.makePolygon(pts)
def ellwire(x,y,z,w,h,n=48):
 p=[App.Vector(x,y+w*.5*math.cos(2*math.pi*j/n),z+h*.5*math.sin(2*math.pi*j/n)) for j in range(n)];p.append(p[0]);return Part.makePolygon(p)
def loft(sec,wire=polywire,solid=True):return Part.makeLoft([wire(*s) for s in sec],solid,False)
def shell(sec,t=.8,wire=polywire):
 out=loft(sec,wire);inn=[(x,y,z,max(1,w-2*t),max(1,h-2*t)) for x,y,z,w,h in sec]
 try:return out.cut(loft(inn,wire))
 except:return out
def split(sh,x,n,mat='PLA'):
 b=sh.BoundBox;p=10;a=sh.common(Part.makeBox(x-b.XMin+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(b.XMin-p,b.YMin-p,b.ZMin-p)));c=sh.common(Part.makeBox(b.XMax-x+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(x,b.YMin-p,b.ZMin-p)));add(n+'_Front',n+' front',a,mat);add(n+'_Rear',n+' rear',c,mat)
def prism(P,z,t):
 vs=[App.Vector(x,y,z) for x,y in P];return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(App.Vector(0,0,t))
def fillet(s,r):
 try:return s.makeFillet(r,s.Edges)
 except:return s
# Body sections driven by top width + side profile.
body=[]
for i in range(31):
 x=i*15.; end=min(max(.08,x/42),max(.08,(450-x)/70),1); w=max(5,min(116,bw[i])*end); bump=17*math.exp(-((x-140)/72)**2); topz=stop[i]-bump; bot=sbot[i]+10; h=max(7,topz-bot); body.append((x,0,(topz+bot)/2,w,h))
split(shell(body,.8),195,'CenterBody')
# sponsons image driven.
for sideN,sgn in [('L',-1),('R',1)]:
 sec=[]
 for i in range(2,28):
  x=i*15.; tap=min((x-25)/42,(415-x)/50,1); w=max(6,min(68,sw[i])*max(.14,tap)); h=max(8,37*max(.25,tap)**.58); z=sbot[i]+2+h/2; sec.append((x,sgn*max(118,min(153,sy[i])),z,w,h))
 split(shell(sec,.8),215,'Sponson_'+sideN);add('Skid_'+sideN,'Skid '+sideN,Part.makeBox(230,12,1.5,App.Vector(90,sgn*sy[15]-6,8)),'PETG')
# Canopy master curve.
can=[(56,0,stop[4]-8,10,6),(78,0,stop[5]-7,31,14),(108,0,stop[7]-5,52,24),(140,0,stop[9]-3,67,31),(173,0,stop[12]-4,64,29),(205,0,stop[14]-6,45,20),(228,0,stop[16]-8,15,8)];add('Canopy','Canopy',shell(can,.75,ellwire))
# GENUINE BLENDED SHOULDERS: loft between longitudinal wing sections, with rounded thickness and crown.
def wing_section(x,sgn,inner,outer,z,t):
 # section lies in YZ plane, rounded crown and tapered outer edge
 pts=[App.Vector(x,sgn*inner,z),App.Vector(x,sgn*(inner+(outer-inner)*.22),z+t*.75),App.Vector(x,sgn*(inner+(outer-inner)*.55),z+t),App.Vector(x,sgn*(inner+(outer-inner)*.82),z+t*.55),App.Vector(x,sgn*outer,z),App.Vector(x,sgn*(inner+(outer-inner)*.82),z-t*.28),App.Vector(x,sgn*(inner+(outer-inner)*.40),z-t*.32),App.Vector(x,sgn*inner,z)];return Part.makePolygon(pts)
for sideN,sgn in [('L',-1),('R',1)]:
 secs=[]
 for i in [3,5,7,9,11,13,15,17,19,21]:
  x=i*15.; inner=max(12,bw[i]*.40);outer=max(inner+10,sy[i]-sw[i]*.40);z=stop[i]-15;t=5.0-1.5*(i/21);secs.append(wing_section(x,sgn,inner,outer,z,t))
 wing=Part.makeLoft(secs,True,False);split(wing,185,'ShoulderWing_'+sideN)
# Rear surfaces from target envelope, thin with softened edges.
for sideN,sgn in [('L',-1),('R',1)]:
 ids=list(range(18,31,2)); outer=[(i*15.,sgn*max(120,min(241,env[i]))) for i in ids]; inner=[(i*15.,sgn*max(35,bw[i]*.38)) for i in reversed(ids)]; tail=fillet(prism(inner+outer,stop[22]-18,2.0),.8); cut=365;b=tail.BoundBox;p=8;fixed=tail.common(Part.makeBox(cut-b.XMin+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(b.XMin-p,b.YMin-p,b.ZMin-p)));ctrl=tail.common(Part.makeBox(b.XMax-cut+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(cut,b.YMin-p,b.ZMin-p)));add('RearFixed_'+sideN,'Rear fixed '+sideN,fixed);add('OuterControl_'+sideN,'Outer control '+sideN,ctrl)
 pitch=[(330,sgn*34),(366,sgn*40),(405,sgn*52),(446,sgn*64),(449,sgn*49),(406,sgn*36),(365,sgn*28)];add('Pitch_'+sideN,'Pitch '+sideN,fillet(prism(pitch,stop[24]-18,2.0),.7))
# Master-like open motor arch.
for sideN,sgn in [('L',1),('R',-1)]:
 y=-22 if sideN=='L' else 22;P=[App.Vector(292,y,47),App.Vector(301,y,47),App.Vector(323,y,80),App.Vector(322,y,88),App.Vector(315,y,88),App.Vector(299,y,59),App.Vector(292,y,56),App.Vector(292,y,47)];add('MotorLeg_'+sideN,'Motor arch '+sideN,Part.Face(Part.makePolygon(P)).extrude(App.Vector(0,sgn*3,0)),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(4.5,44,App.Vector(319,-22,84),App.Vector(0,1,0)),'PETG');add('Firewall','Firewall',Part.makeCylinder(16,4,App.Vector(321,-2,84),App.Vector(1,0,0)),'PETG')
# Fins/rudders.
for sideN,sgn in [('L',-1),('R',1)]:
 y=sgn*177;ap=max(116,stop[27]);fp=[App.Vector(330,y,43),App.Vector(386,y,43),App.Vector(416,y,60),App.Vector(414,y,103),App.Vector(403,y,ap),App.Vector(390,y,ap-3),App.Vector(365,y,116),App.Vector(346,y,84),App.Vector(330,y,43)];add('Fin_'+sideN,'Fin '+sideN,Part.Face(Part.makePolygon(fp)).extrude(App.Vector(0,sgn*1.6,0)))
 rp=[App.Vector(386,y,51),App.Vector(419,y,58),App.Vector(418,y,99),App.Vector(403,y,ap),App.Vector(390,y,ap-3),App.Vector(386,y,51)];add('Rudder_'+sideN,'Rudder '+sideN,Part.Face(Part.makePolygon(rp)).extrude(App.Vector(0,sgn*1.6,0)))
# hidden battery envelope
add('BatteryEnvelope','3S2200',Part.makeBox(110,38,28,App.Vector(125,-19,38)),'REFERENCE',False)
doc.recompute();fc=os.path.join(CAD,'Hydrofoam_Final_Master_v29_BLENDED_SURFACE.FCStd');doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()];vis=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Visual',False) and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v29_BLENDED_SURFACE.step'));Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v29_BLENDED_SURFACE_assembly.stl'));Mesh.export(vis,os.path.join(CAD,'Hydrofoam_Final_Master_v29_BLENDED_SURFACE_visual.stl'))
a=[]
for o in phys:
 Mesh.export([o],os.path.join(PARTS,o.Name+'.stl'));bb=o.Shape.BoundBox;a.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':bb.XLength,'dy':bb.YLength,'dz':bb.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':bb.XLength<=256 and bb.YLength<=256 and bb.ZLength<=256})
json.dump(a,open(os.path.join(DOCS,'V29_PART_AUDIT.json'),'w'),indent=2);print('V29_SAVED',len(phys),'FIT',sum(x['fits_P2S'] for x in a))