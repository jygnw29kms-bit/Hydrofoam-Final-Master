import FreeCAD as App
import Part, Mesh, os, math, json
from PIL import Image
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v28_parts'); DOCS=os.path.join(ROOT,'docs'); CMP=os.path.join(ROOT,'comparison','v20')
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
# side orthographic target -> exact upper/lower silhouette curves
side=Image.open(os.path.join(CMP,'master_side_crop.png')).convert('RGB')
smask=target_mask(side); sbb=smask.getbbox(); smask=smask.crop(sbb); SW,SH=smask.size; spix=smask.load(); SS=450.0/max(1,SW-1)
side_top=[]; side_bottom=[]
for i in range(31):
 sx=round(i*(SW-1)/30); ys=[yy for yy in range(SH) if spix[sx,yy]>127]
 if ys:
  topy=min(ys); boty=max(ys); side_top.append(8+(SH-1-topy)*SS); side_bottom.append(8+(SH-1-boty)*SS)
 else:
  side_top.append(None); side_bottom.append(None)
def fill_side(v,default):
 known=[i for i,x in enumerate(v) if x is not None]; out=[]
 for i,x in enumerate(v):
  if x is not None: out.append(x); continue
  lo=max([k for k in known if k<i],default=None); hi=min([k for k in known if k>i],default=None)
  if lo is None and hi is None: out.append(default)
  elif lo is None: out.append(v[hi])
  elif hi is None: out.append(v[lo])
  else:
   t=(i-lo)/(hi-lo); out.append(v[lo]*(1-t)+v[hi]*t)
 return out
side_top=fill_side(side_top,70); side_bottom=fill_side(side_bottom,8)

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
 xpix=round(i*(W-1)/30); rr=runs_at(xpix); rec={'x':i*15.0,'body_w':None,'sp_y':None,'sp_w':None,'env':None}
 # classify small/central and outer runs. merged full-width runs intentionally ignored.
 if rr:
  infos=[((a+b)/2.0,b-a+1,a,b) for a,b in rr]
  rec['env']=max(max(abs(z[2]-mid),abs(z[3]-mid)) for z in infos)*SY
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
body_w=fill('body_w',90); spy=fill('sp_y',137); spw=fill('sp_w',58); env=fill('env',235)
sp_known=[i for i,r in enumerate(raw) if r['sp_y'] is not None]; body_known=[i for i,r in enumerate(raw) if r['body_w'] is not None]
sp_start=max(15,(min(sp_known)*15-15) if sp_known else 30); sp_end=min(420,(max(sp_known)*15+15) if sp_known else 390)
body_start=max(0,(min(body_known)*15-10) if body_known else 0); body_end=min(450,(max(body_known)*15+10) if body_known else 360)
# smooth curves with 3-sample moving average
def smooth(v):
 return [sum(v[max(0,i-1):min(len(v),i+2)])/len(v[max(0,i-1):min(len(v),i+2)]) for i in range(len(v))]
body_w=smooth(body_w); spy=smooth(spy); spw=smooth(spw)
# clamp to sane physical master ranges and preserve image-driven variation
body_w=[max(8,min(115,v)) for v in body_w]; spy=[max(115,min(155,v)) for v in spy]; spw=[max(12,min(68,v)) for v in spw]
# station-by-station correction from best measured candidate
sc=json.load(open(os.path.join(DOCS,'V25_STATION_CORRECTIONS.json')))
body_w=[body_w[i]*sc['body'][i] for i in range(31)]
spy=[spy[i]*sc['spy'][i] for i in range(31)]
spw=[spw[i]*sc['spw'][i] for i in range(31)]
env=[env[i]*sc['env'][i] for i in range(31)]
VSC=sc['vert']
# another local convergence pass against current best overlay
sc28=json.load(open(os.path.join(DOCS,'V28_STATION_CORRECTIONS.json')))
body_w=[body_w[i]*sc28['body'][i] for i in range(31)]
spy=[spy[i]*sc28['spy'][i] for i in range(31)]
spw=[spw[i]*sc28['spw'][i] for i in range(31)]
env=[env[i]*sc28['env'][i] for i in range(31)]
VSC=[VSC[i]*sc28['vert'][i] for i in range(31)]
json.dump({'raw':raw,'body_w':body_w,'sponson_y':spy,'sponson_w':spw,'mask_size':[W,H],'scale':[SX,SY]},open(os.path.join(DOCS,'V28_IMAGE_MEASUREMENTS.json'),'w'),indent=2)

doc=App.newDocument('Hydrofoam_Final_Master_v28')
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
 end=min(max(0.05,(x-body_start)/38.0),max(0.05,(body_end-x)/58.0),1.0); w=max(4,w*max(.12,end))
 # master side profile: subtract canopy bubble from body top in canopy zone
 target_top=side_top[i]; target_bottom=side_bottom[i]
 canopy_bump=18.0*math.exp(-((x-140.0)/75.0)**2)
 body_top=target_top-canopy_bump
 body_bottom=target_bottom+10.0
 h=max(6.0,(body_top-body_bottom))*VSC[i]
 z=(body_top+body_bottom)/2.0
 bodysec.append((x,0,z,w,h))
splitx(shell(bodysec,.8),195,'CenterBody')
# sponsons are derived from measured outer runs; valid mainly over their physical x range
for side,sgn in [('L',-1),('R',1)]:
 sec=[]
 for i,x in enumerate(xs):
  if x<sp_start or x>sp_end: continue
  taper=min((x-sp_start)/35.0,(sp_end-x)/40.0,1.0); w=max(5,spw[i]*max(.16,taper)); h=max(7,38*max(.28,taper)**.55)*VSC[i]; bottom=side_bottom[i]+1.0; z=bottom+h/2.0; sec.append((x,sgn*spy[i],z,w,h))
 splitx(shell(sec,.8),215,'Sponson_'+side); add('Skid_'+side,'Skid '+side,fillet(Part.makeBox(230,12,1.5,App.Vector(90,sgn*spy[15]-6,8)),.7),'PETG')
# canopy from image master identity
can=[(58,0,51,8,5),(78,0,58,29,13),(106,0,67,52,23),(138,0,73,67,31),(171,0,72,65,29),(203,0,65,46,21),(228,0,56,16,8)];add('Canopy','Canopy',shell(can,.75,ew))
# shoulder bridge follows measured inner sponson edge and body edge station by station.
for side,sgn in [('L',-1),('R',1)]:
 outer=[];inner=[]
 for i in range(3,22,2):
  x=xs[i]; outer.append((x,sgn*(spy[i]-spw[i]*.42))); inner.append((x,sgn*(body_w[i]*.42)))
 pts=inner+list(reversed(outer)); wing=fillet(prism(pts,42,2.0),.9); splitx(wing,185,'ShoulderWing_'+side)
# Rear surfaces: outer edge is read from the Final Master silhouette envelope.
for side,sgn in [('L',-1),('R',1)]:
    ids=list(range(18,31,2))
    outeredge=[(xs[i],sgn*max(125,min(241,env[i]))) for i in ids]
    inneredge=[]
    for i in reversed(ids):
        # root line stays around central tail/sponson inner region
        root=max(body_w[i]*0.40,42)
        inneredge.append((xs[i],sgn*root))
    tailpoly=inneredge+outeredge
    tail=fillet(prism(tailpoly,41,2.0),0.8)
    # split aft 45% as control surface, fixed forward portion stays structurally separate
    cutx=365
    b=tail.BoundBox; pad=8
    fixed=tail.common(Part.makeBox(cutx-b.XMin+pad,b.YLength+2*pad,b.ZLength+2*pad,App.Vector(b.XMin-pad,b.YMin-pad,b.ZMin-pad)))
    ctrl=tail.common(Part.makeBox(b.XMax-cutx+pad,b.YLength+2*pad,b.ZLength+2*pad,App.Vector(cutx,b.YMin-pad,b.ZMin-pad)))
    add('RearFixed_'+side,'Rear fixed '+side,fixed)
    add('OuterControl_'+side,'Outer control '+side,ctrl)
    # inner pitch strip follows central trailing edge
    pitch=[(330,sgn*34),(366,sgn*40),(405,sgn*52),(446,sgn*64),(449,sgn*49),(406,sgn*36),(365,sgn*28)]
    add('Pitch_'+side,'Pitch '+side,fillet(prism(pitch,42,2.0),0.7))
# exact identity motor arch shape
for side,sgn in [('L',1),('R',-1)]:
 y=-22 if side=='L' else 22; pts=[App.Vector(292,y,45),App.Vector(301,y,45),App.Vector(323,y,80),App.Vector(322,y,88),App.Vector(315,y,88),App.Vector(299,y,58),App.Vector(292,y,55),App.Vector(292,y,45)];add('MotorLeg_'+side,'Motor arch '+side,Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0,sgn*3,0)),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(4.5,44,App.Vector(319,-22,84),App.Vector(0,1,0)),'PETG');add('Firewall','Firewall',Part.makeCylinder(16,4,App.Vector(321,-2,84),App.Vector(1,0,0)),'PETG')
# fins
for side,sgn in [('L',-1),('R',1)]:
 i_fin=25; y=sgn*max(150,min(205,env[i_fin]*0.78)); fp=[App.Vector(330,y,43),App.Vector(386,y,43),App.Vector(416,y,60),App.Vector(414,y,103),App.Vector(403,y,max(112,side_top[27])),App.Vector(390,y,132),App.Vector(365,y,116),App.Vector(346,y,84),App.Vector(330,y,43)];add('Fin_'+side,'Fin '+side,Part.Face(Part.makePolygon(fp)).extrude(App.Vector(0,sgn*1.6,0)))
 rp=[App.Vector(386,y,51),App.Vector(419,y,58),App.Vector(418,y,99),App.Vector(403,y,max(112,side_top[27])),App.Vector(390,y,132),App.Vector(386,y,51)];add('Rudder_'+side,'Rudder '+side,Part.Face(Part.makePolygon(rp)).extrude(App.Vector(0,sgn*1.6,0)))
# packaging hidden
add('BatteryEnvelope','3S2200',Part.makeBox(110,38,28,App.Vector(125,-19,38)),'REFERENCE',False)
doc.recompute();fc=os.path.join(CAD,'Hydrofoam_Final_Master_v28_CONVERGENCE.FCStd');doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()];vis=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Visual',False) and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v28_CONVERGENCE.step'));Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v28_CONVERGENCE_assembly.stl'));Mesh.export(vis,os.path.join(CAD,'Hydrofoam_Final_Master_v28_CONVERGENCE_visual.stl'))
a=[]
for o in phys:
 Mesh.export([o],os.path.join(PARTS,o.Name+'.stl'));b=o.Shape.BoundBox;a.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':b.XLength,'dy':b.YLength,'dz':b.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':b.XLength<=256 and b.YLength<=256 and b.ZLength<=256})
json.dump(a,open(os.path.join(DOCS,'V28_PART_AUDIT.json'),'w'),indent=2);print('V28_SAVED',len(phys),'FIT',sum(x['fits_P2S'] for x in a),'MASK',W,H)