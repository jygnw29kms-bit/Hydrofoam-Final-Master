import FreeCAD as App
import Part, Mesh, os, math, json
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v17_parts'); os.makedirs(CAD,exist_ok=True); os.makedirs(PARTS,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v17_FINAL_WEIGHT')

def add(name,label,shape,mat='PLA'):
    o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat
    return o

def ew(x,y,z,w,h,n=48):
    pts=[App.Vector(x,y+(w/2)*math.cos(2*math.pi*i/n),z+(h/2)*math.sin(2*math.pi*i/n)) for i in range(n)]
    pts.append(pts[0]); return Part.makePolygon(pts)

def loft(sec): return Part.makeLoft([ew(*s) for s in sec],True,False)
def prism(poly,z,t):
    pts=[App.Vector(x,y,z) for x,y in poly]; w=Part.makePolygon(pts+[pts[0]])
    return Part.Face(w).extrude(App.Vector(0,0,t))
def fillet(sh,r):
    try:return sh.makeFillet(r,sh.Edges)
    except:return sh
def split_x(sh,x0,x1): return sh.common(Part.makeBox(x1-x0,700,300,App.Vector(x0,-350,-80)))
def shell_loft(outer,wall=1.0):
    inn=[(x,y,z,max(1,w-2*wall),max(1,h-2*wall)) for x,y,z,w,h in outer]
    return loft(outer).cut(loft(inn))

for side,y in [('L',-135),('R',135)]:
    sec=[(8,y,26,4,4),(24,y,28,18,13),(48,y,30,34,23),(82,y,31,48,31),(125,y,31,56,36),(180,y,30,60,38),(235,y,29,60,37),(285,y,28,56,34),(325,y,27,47,29),(355,y,27,32,21),(375,y,27,10,8)]
    sh=shell_loft(sec,0.8)
    add('Sponson_'+side+'_Front','Sponson '+side+' front shell',split_x(sh,0,205))
    add('Sponson_'+side+'_Rear','Sponson '+side+' rear shell',split_x(sh,205,390))
    add('Skid_'+side,'Replaceable PETG skid '+side,fillet(Part.makeBox(245,12,1.5,App.Vector(70,y-6,7)),0.8),'PETG')

body_sec=[(22,0,31,5,5),(38,0,34,21,13),(60,0,38,42,22),(88,0,43,64,31),(120,0,49,82,40),(155,0,54,96,47),(195,0,54,100,48),(235,0,51,92,43),(272,0,47,76,35),(305,0,42,58,27),(332,0,38,40,19),(350,0,35,20,11)]
body=shell_loft(body_sec,0.8)
add('CenterBody_Front','Center fuselage front shell',split_x(body,0,205)); add('CenterBody_Rear','Center fuselage rear shell',split_x(body,205,370))
can_sec=[(58,0,49,10,6),(78,0,56,26,12),(104,0,64,42,19),(132,0,71,53,25),(160,0,73,55,27),(188,0,69,45,22),(212,0,60,26,13),(225,0,54,10,6)]
add('Canopy','Canopy / service hatch',shell_loft(can_sec,0.8))

for side,sgn in [('L',-1),('R',1)]:
    poly=[(55,sgn*18),(78,sgn*34),(110,sgn*52),(148,sgn*67),(188,sgn*78),(230,sgn*89),(270,sgn*98),(305,sgn*105),(325,sgn*107),(306,sgn*91),(270,sgn*82),(225,sgn*72),(180,sgn*62),(138,sgn*50),(102,sgn*37),(72,sgn*25)]
    shw=fillet(prism(poly,34,2.0),2.0)
    add('ShoulderWing_'+side+'_Front','Blended shoulder wing '+side+' front',split_x(shw,0,190))
    add('ShoulderWing_'+side+'_Rear','Blended shoulder wing '+side+' rear',split_x(shw,190,340))
    fixed=[(270,sgn*103),(303,sgn*124),(340,sgn*150),(375,sgn*178),(410,sgn*202),(440,sgn*211),(445,sgn*194),(415,sgn*176),(378,sgn*152),(338,sgn*128),(302,sgn*110)]
    add('RearFixed_'+side,'Rear fixed panel '+side,fillet(prism(fixed,35,2.0),1.0))
    ctrl=[(330,sgn*155),(365,sgn*180),(405,sgn*208),(446,sgn*222),(449,sgn*199),(414,sgn*184),(375,sgn*164),(344,sgn*148)]
    add('OuterControl_'+side,'Outer control surface '+side,fillet(prism(ctrl,39.5,2.0),0.9))
    pitch=[(326,sgn*32),(360,sgn*38),(397,sgn*50),(438,sgn*67),(448,sgn*60),(410,sgn*44),(370,sgn*32)]
    add('Pitch_'+side,'Pitch surface '+side,fillet(prism(pitch,38.5,2.0),0.9))

for side,y in [('L',-23),('R',23)]:
    sec=[(286,y,39,8,7),(298,y,51,10,14),(309,y,66,12,20),(320,y,82,10,13)]
    add('MotorLeg_'+side,'Motor arch leg '+side,loft(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(4.5,46,App.Vector(320,-23,82),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,6,App.Vector(320,0,82),App.Vector(1,0,0)),'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(351,0,82),App.Vector(1,0,0)),'REFERENCE')

for side,sgn in [('L',-1),('R',1)]:
    y=sgn*191
    fw=Part.makePolygon([App.Vector(326,y,39),App.Vector(370,y,39),App.Vector(415,y,99),App.Vector(404,y,137),App.Vector(365,y,118),App.Vector(326,y,39)])
    add('Fin_'+side,'Fin '+side,Part.Face(fw).extrude(App.Vector(0,sgn*1.6,0)))
    rw=Part.makePolygon([App.Vector(382,y,52),App.Vector(422,y,47),App.Vector(424,y,95),App.Vector(404,y,137),App.Vector(382,y,52)])
    add('Rudder_'+side,'Rudder '+side,Part.Face(rw).extrude(App.Vector(0,sgn*1.6,0)))

add('BatteryEnvelope','3S 2200 envelope',Part.makeBox(110,38,28,App.Vector(128,-19,39)),'REFERENCE')
rails=Part.makeBox(155,3,3,App.Vector(108,-23,37)).fuse(Part.makeBox(155,3,3,App.Vector(108,20,37)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
for i,(x,y,z) in enumerate([(245,-52,42),(245,40,42),(326,-10,43),(333,10,49)],1): add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')
for name,x,y,l,axis in [('AilL',350,-168,64,'y'),('AilR',350,168,64,'y'),('PitchL',375,-62,45,'y'),('PitchR',375,20,45,'y'),('RudL',393,-189,74,'z'),('RudR',393,193,74,'z')]:
    sh=Part.makeCylinder(0.75,l,App.Vector(x,y,44 if axis=='y' else 54),App.Vector(0,1,0) if axis=='y' else App.Vector(0,0,1)); add('Hinge_'+name,'1.5 mm hinge axis '+name,sh,'PETG')

doc.recompute(); fc=os.path.join(CAD,'Hydrofoam_Final_Master_v17_FINAL_WEIGHT.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v17_FINAL_WEIGHT.step')); Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v17_FINAL_WEIGHT_assembly.stl'))
audit=[]
for o in phys:
    Mesh.export([o],os.path.join(PARTS,o.Name+'.stl')); bb=o.Shape.BoundBox
    audit.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':bb.XLength,'dy':bb.YLength,'dz':bb.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':bb.XLength<=256 and bb.YLength<=256 and bb.ZLength<=256})
with open(os.path.join(ROOT,'docs','V17_PART_AUDIT.json'),'w') as f: json.dump(audit,f,indent=2)
print('V17_SAVED',len(phys),'parts',sum(a['fits_P2S'] for a in audit),'fit')


