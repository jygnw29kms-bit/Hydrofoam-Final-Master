import FreeCAD as App
import Part, Mesh, os, math, json
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v18_parts'); DOCS=os.path.join(ROOT,'docs')
os.makedirs(CAD,exist_ok=True); os.makedirs(PARTS,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v18')

def add(name,label,shape,mat='PLA',visual=True):
    o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat
    o.addProperty('App::PropertyBool','Visual','Manufacturing').Visual=visual
    return o

def ew(x,y,z,wy,hz,n=48):
    pts=[]
    for i in range(n):
        a=2*math.pi*i/n
        pts.append(App.Vector(x,y+wy*0.5*math.cos(a),z+hz*0.5*math.sin(a)))
    pts.append(pts[0]); return Part.makePolygon(pts)

def loft(sec): return Part.makeLoft([ew(*s) for s in sec],True,False)
def shell(sec,t=0.8):
    outer=loft(sec)
    inner=[]
    for x,y,z,w,h in sec:
        inner.append((x,y,z,max(1,w-2*t),max(1,h-2*t)))
    try: return outer.cut(loft(inner))
    except: return outer

def prism(points,z,t):
    vs=[App.Vector(x,y,z) for x,y in points]; w=Part.makePolygon(vs+[vs[0]])
    return Part.Face(w).extrude(App.Vector(0,0,t))
def fillet(s,r):
    try:return s.makeFillet(r,s.Edges)
    except:return s

def split_x(shape,x,name,mat='PLA'):
    b=shape.BoundBox; pad=10
    left=shape.common(Part.makeBox(x-b.XMin+pad,b.YLength+2*pad,b.ZLength+2*pad,App.Vector(b.XMin-pad,b.YMin-pad,b.ZMin-pad)))
    right=shape.common(Part.makeBox(b.XMax-x+pad,b.YLength+2*pad,b.ZLength+2*pad,App.Vector(x,b.YMin-pad,b.ZMin-pad)))
    add(name+'_Front',name+' front',left,mat); add(name+'_Rear',name+' rear',right,mat)

# FINAL MASTER proportions: central body forward, twin sponsons close to body, wide rear tail surfaces.
# Sponsons: centers ±137 mm, smooth pointed bows, low planing hulls.
for side,sgn in [('L',-1),('R',1)]:
    y=sgn*137
    sec=[(18,y,24,8,8),(34,y,27,24,17),(60,y,30,44,27),(100,y,31,56,34),(155,y,31,62,38),(220,y,30,62,38),(280,y,29,58,34),(330,y,28,48,29),(366,y,27,32,20),(388,y,27,8,8)]
    sh=shell(sec,0.8); split_x(sh,205,'Sponson_'+side)
    skid=fillet(Part.makeBox(238,12,1.5,App.Vector(78,y-6,7)),0.7); add('Skid_'+side,'PETG skid '+side,skid,'PETG')

# Central fuselage: long pointed nose, maximum fullness under canopy, taper to motor/tail zone.
body=[(0,0,30,5,5),(18,0,32,20,11),(42,0,35,42,19),(72,0,39,66,28),(110,0,45,88,38),(150,0,50,102,46),(195,0,51,108,47),(240,0,48,100,41),(278,0,43,84,32),(310,0,39,62,24),(340,0,36,40,17),(360,0,34,18,10)]
bs=shell(body,0.8); split_x(bs,195,'CenterBody')
# Dark canopy/hatch shape, hollow shell.
can=[(55,0,49,10,6),(78,0,57,30,14),(108,0,66,52,24),(142,0,72,66,31),(177,0,71,62,29),(208,0,64,42,20),(230,0,55,14,8)]
add('Canopy','Canopy / service hatch',shell(can,0.8))

# Shoulder surfaces: exact design logic from master, broad blended bridges from body flanks to inner sponson flanks.
# No gaps; outer edge overlaps sponson inner edge (~106 mm).
for side,sgn in [('L',-1),('R',1)]:
    pts=[(42,sgn*18),(64,sgn*42),(92,sgn*63),(126,sgn*79),(166,sgn*91),(210,sgn*100),(254,sgn*104),(292,sgn*104),(320,sgn*99),
         (305,sgn*82),(270,sgn*71),(230,sgn*63),(188,sgn*58),(146,sgn*53),(108,sgn*45),(74,sgn*34),(42,sgn*18)]
    wing=fillet(prism(pts,33,2.0),1.0)
    # split to P2S friendly front/rear modules around x=185
    split_x(wing,185,'ShoulderWing_'+side)

# Rear fixed surfaces and movable outer panels: broad swept, low and continuous with master tail silhouette.
for side,sgn in [('L',-1),('R',1)]:
    fixed=[(275,sgn*70),(310,sgn*92),(346,sgn*122),(382,sgn*154),(420,sgn*181),(448,sgn*185),(447,sgn*149),(412,sgn*132),(372,sgn*112),(330,sgn*91),(292,sgn*76)]
    add('RearFixed_'+side,'Rear fixed surface '+side,fillet(prism(fixed,34,2.0),0.8))
    outer=[(330,sgn*150),(365,sgn*188),(405,sgn*221),(447,sgn*228),(450,sgn*203),(416,sgn*181),(376,sgn*162),(340,sgn*148)]
    add('OuterControl_'+side,'Outer control surface '+side,fillet(prism(outer,36,2.0),0.8))
    pitch=[(330,sgn*34),(366,sgn*40),(405,sgn*52),(446,sgn*65),(448,sgn*49),(405,sgn*36),(365,sgn*28)]
    add('Pitch_'+side,'Pitch surface '+side,fillet(prism(pitch,35,2.0),0.7))

# Compact open motor arch exactly aft of central body.
for side,y in [('L',-23),('R',23)]:
    sec=[(286,y,39,8,7),(299,y,51,10,14),(310,y,66,12,20),(320,y,82,10,13)]
    add('MotorLeg_'+side,'Motor arch leg '+side,loft(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(5.5,46,App.Vector(320,-23,82),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,5,App.Vector(320,0,82),App.Vector(1,0,0)),'PETG')

# Twin fins are carried by rear surfaces, farther inboard than previous v17.
for side,sgn in [('L',-1),('R',1)]:
    y=sgn*178
    fw=Part.makePolygon([App.Vector(327,y,38),App.Vector(371,y,38),App.Vector(414,y,100),App.Vector(402,y,136),App.Vector(365,y,116),App.Vector(327,y,38)])
    add('Fin_'+side,'Fin '+side,Part.Face(fw).extrude(App.Vector(0,sgn*1.6,0)))
    rw=Part.makePolygon([App.Vector(382,y,52),App.Vector(422,y,47),App.Vector(424,y,94),App.Vector(402,y,136),App.Vector(382,y,52)])
    add('Rudder_'+side,'Rudder '+side,Part.Face(rw).extrude(App.Vector(0,sgn*1.6,0)))

# RC packaging / hardware, not rendered in exterior images.
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(125,-19,38)),'REFERENCE',False)
rails=Part.makeBox(155,3,3,App.Vector(105,-23,37)).fuse(Part.makeBox(155,3,3,App.Vector(105,20,37)))
add('BatteryRails','Battery rails',rails,'PETG',False)
for i,(x,y,z) in enumerate([(245,-48,41),(245,36,41),(324,-10,42),(332,10,48)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE',False)
for name,x,y,l,axis in [('AilL',365,-180,55,'y'),('AilR',365,180,55,'y'),('PitchL',370,-58,40,'y'),('PitchR',370,18,40,'y'),('RudL',393,-177,72,'z'),('RudR',393,179,72,'z')]:
    sh=Part.makeCylinder(0.75,l,App.Vector(x,y,44 if axis=='y' else 53),App.Vector(0,1,0) if axis=='y' else App.Vector(0,0,1))
    add('Hinge_'+name,'1.5mm hinge axis '+name,sh,'PETG',False)

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v18_MASTER_CONVERGENCE.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
vis=[o for o in phys if getattr(o,'Visual',False)]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v18_MASTER_CONVERGENCE.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v18_MASTER_CONVERGENCE_assembly.stl'))
Mesh.export(vis,os.path.join(CAD,'Hydrofoam_Final_Master_v18_MASTER_CONVERGENCE_visual.stl'))
audit=[]
for o in phys:
    Mesh.export([o],os.path.join(PARTS,o.Name+'.stl'))
    b=o.Shape.BoundBox; audit.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':b.XLength,'dy':b.YLength,'dz':b.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':b.XLength<=256 and b.YLength<=256 and b.ZLength<=256})
json.dump(audit,open(os.path.join(DOCS,'V18_PART_AUDIT.json'),'w'),indent=2)
print('V18_SAVED',len(phys),'fit',sum(x['fits_P2S'] for x in audit),'visual',len(vis))