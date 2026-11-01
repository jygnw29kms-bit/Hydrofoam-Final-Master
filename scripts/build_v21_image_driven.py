import FreeCAD as App
import Part, Mesh, os, math, json
from PIL import Image
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v21_parts'); DOCS=os.path.join(ROOT,'docs'); CMP=os.path.join(ROOT,'comparison','v20')
os.makedirs(CAD,exist_ok=True); os.makedirs(PARTS,exist_ok=True)
top=Image.open(os.path.join(CMP,'master_top_crop.png')).convert('RGB')
# Rebuild the same target mask locally.
def target_mask(im):
 m=Image.new('L',im.size,0); a=im.load(); b=m.load()
 for y in range(im.height):
  for x in range(im.width):
   r,g,bl=a[x,y]; mx=max(r,g,bl); mn=min(r,g,bl)
   if (r+g+bl)/3 < 238 or mx-mn>18: b[x,y]=255
 return m
mask=target_mask(top); bb=mask.getbbox()
if not bb: raise RuntimeError('empty top target mask')
mask=mask.crop(bb); W,H=mask.size; pix=mask.load(); mid=H/2.0
SX=450.0/max(1,W-1); SY=482.0/max(1,H-1)

def runs_at(px):
 ys=[y for y in range(H) if pix[min(max(px,0),W-1),y]>127]
 if not ys:return []
 runs=[]; s=ys[0]; p=ys[0]
 for y in ys[1:]:
  if y>p+1:
   if p-s>=2:runs.append((s,p))
   s=y
  p=y
 if p-s>=2:runs.append((s,p))
 return runs
raw=[]
for i in range(31):
 xpix=round(i*(W-1)/30); rr=runs_at(xpix); rec={'x':i*15.0,'body_w':None,'sp_y':None,'sp_w':None}
 # classify small/central and outer runs. merged full-width runs intentionally ignored.
 if rr:
  infos=[((a+b)/2.0,b-a+1,a,b) for a,b in rr]
  cen=sorted(infos,key=lambda z:abs(z[0]-mid))[0]
  if cen[1] < H*.48: rec['body_w']=cen[1]*SY
  ou=[z for z in infos if abs(z[0]-mid)>H*.13 and z[1]<H*.28]
  if ou:
   rec['sp_y']=sum(abs(z[0]-mid)*SY for z in ou)/len(ou); rec['sp_w']=sum(z[1]*SY for z in ou)/len(ou)
 raw.append(rec)

def fill(key,default):
 vals=[r[key] for r in raw]
 known=[i for i,v in enumerate(vals) if v is not None]
 if not known:return [default]*len(vals)
 out=[]
 for i,v in enumerate(vals):
  if v is not None:out.append(v);continue
  lo=max([k for k in known if k<i],default=None); hi=min([k for k in known if k>i],default=None)
  if lo is None:out.append(vals[hi])
  elif hi is None:out.append(vals[lo])
  else:
   t=(i-lo)/(hi-lo); out.append(vals[lo]*(1-t)+vals[hi]*t)
 return out
body_w=fill('body_w',90); spy=fill('sp_y',137); spw=fill('sp_w',58)
# smooth curves with 3-sample moving average
def smooth(v):
 return [sum(v[max(0,i-1):min(len(v),i+2)])/len(v[max(0,i-1):min(len(v),i+2)]) for i in range(len(v))]
body_w=smooth(body_w); spy=smooth(spy); spw=smooth(spw)
# clamp to sane physical master ranges and preserve image-driven variation
body_w=[max(8,min(115,v)) for v in body_w]; spy=[max(115,min(155,v)) for v in spy]; spw=[max(12,min(68,v)) for v in spw]
json.dump({'raw':raw,'body_w':body_w,'sponson_y':spy,'sponson_w':spw,'mask_size':[W,H],'scale':[SX,SY]},open(os.path.join(DOCS,'V21_IMAGE_MEASUREMENTS.json'),'w'),indent=2)

doc=App.newDocument('Hydrofoam_Final_Master_v21')
def add(name,label,shape,mat='PLA',visual=True):
 o=doc.addObject('PartDesign::Feature',name);o.Label=label;o.Shape=shape;o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat;o.addProperty('App::PropertyBool','Visual','Manufacturing').Visual=visual;return o
def hw(x,y,z,w,h):
 pts=[App.Vector(x,y,z+h*.5),App.Vector(x,y-w*.34,z+h*.34),App.Vector(x,y-w*.50,z+h*.05),App.Vector(x,y-w*.46,z-h*.30),App.Vector(x,y-w*.28,z-h*.50),App.Vector(x,y+w*.28,z-h*.50),App.Vector(x,y+w*.46,z-h*.30),App.Vector(x,y+w*.50,z+h*.05),App.Vector(x,y+w*.34,z+h*.34),App.Vector(x,y,z+h*.5)];return Part.makePolygon(pts)
def ew(x,y,z,w,h,n=48):
 pts=[App.Vector(x,y+w*.5*math.cos(2*math.pi*i/n),z+h*.5*math.sin(2*math.pi*i/n)) for i in range(n)];pts.append(pts[0]);return Part.makePolygon(pts)
def loft(sec,wire=hw):return Part.makeLoft([wire(*s) for s in sec],True,False)
def shell(sec,t=.8,wire=hw):
 o=loft(sec,wire);inn=[(x,y,z,max(1,w-2*t),max(1,h-2*t)) for x,y,z,w,h in sec]
 try:return o.cut(loft(inn,wire))
 except:return o
def prism(p,z,t):
 v=[App.Vector(x,y,z) for x,y in p];return Part.Face(Part.makePolygon(v+[v[0]])).extrude(App.Vector(0,0,t))
def fillet(s,r):
 try:return s.makeFillet(r,s.Edges)
 except:return s
def splitx(sh,x,n,mat='PLA'):
 b=sh.BoundBox;p=10;a=sh.common(Part.makeBox(x-b.XMin+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(b.XMin-p,b.YMin-p,b.ZMin-p)));c=sh.common(Part.makeBox(b.XMax-x+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(x,b.YMin-p,b.ZMin-p)));add(n+'_Front',n+' front',a,mat);add(n+'_Rear',n+' rear',c,mat)
# Image-driven longitudinal stations.
xs=[i*15.0 for i in range(31)]
# body nose/tail taper and height curve based on master side proportions
bodysec=[]
for i,x in enumerate(xs):
 w=body_w[i]
 # force true pointed ends, keep image-driven middle
 end=min(x/42.0,(450-x)/75.0,1.0); w=max(4,w*max(.12,end))
 h=8 + 39*math.sin(math.pi*min(max(x/365.0,0),1))**0.78
 z=31+h*.18
 bodysec.append((x,0,z,w,h))
splitx(shell(bodysec,.8),195,'CenterBody')
# sponsons are derived from measured outer runs; valid mainly over their physical x range
for side,sgn in [('L',-1),('R',1)]:
 sec=[]
 for i,x in enumerate(xs):
  if x<35 or x>390: continue
  taper=min((x-35)/40.0,(390-x)/45.0,1.0); w=max(5,spw[i]*max(.16,taper)); h=max(7,38*max(.28,taper)**.55); sec.append((x,sgn*spy[i],29,w,h))
 splitx(shell(sec,.8),215,'Sponson_'+side); add('Skid_'+side,'Skid '+side,fillet(Part.makeBox(230,12,1.5,App.Vector(90,sgn*spy[15]-6,8)),.7),'PETG')
# canopy from image master identity
can=[(58,0,51,8,5),(78,0,58,29,13),(106,0,67,52,23),(138,0,73,67,31),(171,0,72,65,29),(203,0,65,46,21),(228,0,56,16,8)];add('Canopy','Canopy',shell(can,.75,ew))
# shoulder bridge follows measured inner sponson edge and body edge station by station.
for side,sgn in [('L',-1),('R',1)]:
 outer=[];inner=[]
 for i in range(3,22,2):
  x=xs[i]; outer.append((x,sgn*(spy[i]-spw[i]*.42))); inner.append((x,sgn*(body_w[i]*.42)))
 pts=inner+list(reversed(outer)); wing=fillet(prism(pts,42,2.0),.9); splitx(wing,185,'ShoulderWing_'+side)
# master rear surfaces: fixed + movable sweep to full 482 mm envelope
for side,sgn in [('L',-1),('R',1)]:
 fixed=[(275,sgn*72),(310,sgn*95),(345,sgn*125),(381,sgn*157),(418,sgn*183),(448,sgn*188),(449,sgn*157),(416,sgn*138),(378,sgn*117),(337,sgn*96),(300,sgn*80)];add('RearFixed_'+side,'Rear fixed '+side,fillet(prism(fixed,41,2),.8))
 outer=[(326,sgn*151),(360,sgn*190),(401,sgn*222),(445,sgn*236),(450,sgn*207),(418,sgn*184),(380,sgn*163),(342,sgn*150)];add('OuterControl_'+side,'Outer control '+side,fillet(prism(outer,43,2),.8))
 pitch=[(326,sgn*35),(364,sgn*41),(405,sgn*53),(446,sgn*65),(449,sgn*50),(406,sgn*37),(364,sgn*29)];add('Pitch_'+side,'Pitch '+side,fillet(prism(pitch,42,2),.7))
# exact identity motor arch shape
for side,sgn in [('L',1),('R',-1)]:
 y=-22 if side=='L' else 22; pts=[App.Vector(292,y,45),App.Vector(301,y,45),App.Vector(323,y,80),App.Vector(322,y,88),App.Vector(315,y,88),App.Vector(299,y,58),App.Vector(292,y,55),App.Vector(292,y,45)];add('MotorLeg_'+side,'Motor arch '+side,Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0,sgn*3,0)),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(4.5,44,App.Vector(319,-22,84),App.Vector(0,1,0)),'PETG');add('Firewall','Firewall',Part.makeCylinder(16,4,App.Vector(321,-2,84),App.Vector(1,0,0)),'PETG')
# fins
for side,sgn in [('L',-1),('R',1)]:
 y=sgn*177; fp=[App.Vector(330,y,43),App.Vector(386,y,43),App.Vector(416,y,60),App.Vector(414,y,103),App.Vector(403,y,135),App.Vector(390,y,132),App.Vector(365,y,116),App.Vector(346,y,84),App.Vector(330,y,43)];add('Fin_'+side,'Fin '+side,Part.Face(Part.makePolygon(fp)).extrude(App.Vector(0,sgn*1.6,0)))
 rp=[App.Vector(386,y,51),App.Vector(419,y,58),App.Vector(418,y,99),App.Vector(403,y,135),App.Vector(390,y,132),App.Vector(386,y,51)];add('Rudder_'+side,'Rudder '+side,Part.Face(Part.makePolygon(rp)).extrude(App.Vector(0,sgn*1.6,0)))
# packaging hidden
add('BatteryEnvelope','3S2200',Part.makeBox(110,38,28,App.Vector(125,-19,38)),'REFERENCE',False)
doc.recompute();fc=os.path.join(CAD,'Hydrofoam_Final_Master_v21_IMAGE_DRIVEN.FCStd');doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()];vis=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Visual',False) and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v21_IMAGE_DRIVEN.step'));Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v21_IMAGE_DRIVEN_assembly.stl'));Mesh.export(vis,os.path.join(CAD,'Hydrofoam_Final_Master_v21_IMAGE_DRIVEN_visual.stl'))
a=[]
for o in phys:
 Mesh.export([o],os.path.join(PARTS,o.Name+'.stl'));b=o.Shape.BoundBox;a.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':b.XLength,'dy':b.YLength,'dz':b.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':b.XLength<=256 and b.YLength<=256 and b.ZLength<=256})
json.dump(a,open(os.path.join(DOCS,'V21_PART_AUDIT.json'),'w'),indent=2);print('V21_SAVED',len(phys),'FIT',sum(x['fits_P2S'] for x in a),'MASK',W,H)