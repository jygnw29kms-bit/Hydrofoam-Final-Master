import FreeCAD as App
import Part, Mesh, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); REND=os.path.join(ROOT,'renders','v05')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v05')
L=450.0

def add(name,label,shape,mat='PLA'):
    o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat
    return o

def ellipse_wire(x,y,z,wy,hz,n=36):
    pts=[]
    for i in range(n):
        a=2*math.pi*i/n
        pts.append(App.Vector(x,y+(wy/2)*math.cos(a),z+(hz/2)*math.sin(a)))
    pts.append(pts[0]); return Part.makePolygon(pts)

def loft(sec):
    return Part.makeLoft([ellipse_wire(*s) for s in sec],True,False)

def prism(points,z,t):
    pts=[App.Vector(x,y,z) for x,y in points]
    w=Part.makePolygon(pts+[pts[0]])
    return Part.Face(w).extrude(App.Vector(0,0,t))

def fillet(s,r):
    try: return s.makeFillet(r,s.Edges)
    except: return s

# V05 is based on measured proportions from the actual Final Master top/side views.
# 450 mm length => approx. 465-470 mm overall span. Planform area ~14.5 dm2.
for side,yc in [('L',-132),('R',132)]:
    sec=[(18,yc,25,6,6),(35,yc,27,22,16),(58,yc,29,36,25),(92,yc,30,46,32),(145,yc,30,52,36),(205,yc,29,54,37),(265,yc,28,53,36),(315,yc,27,48,32),(350,yc,27,36,25),(372,yc,27,16,12)]
    add(f'Sponson_{side}',f'Final Master Sponson {side}',loft(sec))
    add(f'Skid_{side}',f'PETG skid {side}',fillet(Part.makeBox(250,16,3,App.Vector(72,yc-8,7)),1.2),'PETG')

center_sec=[(0,0,31,6,6),(22,0,34,22,14),(48,0,38,44,24),(80,0,43,64,32),(118,0,49,82,40),(160,0,54,94,46),(205,0,53,92,44),(248,0,49,80,37),(290,0,44,60,29),(322,0,39,40,21),(350,0,35,20,12)]
add('CenterFuselage','Measured Final Master center fuselage',loft(center_sec))
canopy_sec=[(55,0,52,14,8),(82,0,61,34,16),(116,0,70,48,23),(151,0,74,52,26),(184,0,70,42,20),(208,0,61,22,10)]
add('Canopy','Canopy service hatch',loft(canopy_sec),'PLA')

wing_pts=[(42,-22),(64,-48),(96,-76),(132,-101),(170,-122),(208,-142),(248,-160),(286,-184),(320,-220),(350,-234),(372,-228),(395,-188),(420,-186),(445,-185),(445,185),(420,186),(395,188),(372,228),(350,234),(320,220),(286,184),(248,160),(208,142),(170,122),(132,101),(96,76),(64,48),(42,22)]
add('BlendedWingDeck','Final Master blended wing/deck',fillet(prism(wing_pts,30,7.5),3.0))
for side,sgn in [('L',-1),('R',1)]:
    cutpts=[(62,sgn*70),(95,sgn*88),(140,sgn*102),(185,sgn*106),(220,sgn*96),(180,sgn*76),(118,sgn*62)]
    cutter=prism(cutpts,24,22)
    obj=doc.getObject('BlendedWingDeck'); obj.Shape=obj.Shape.cut(cutter)

rear=fillet(prism([(300,-190),(345,-220),(440,-205),(450,-160),(450,160),(440,205),(345,220),(300,190)],31,5),1.8)
add('RearDeck','Wide rear lifting deck',rear)
for side,sgn in [('L',-1),('R',1)]:
    pts=[(315,sgn*165),(365,sgn*210),(438,sgn*196),(447,sgn*156),(390,sgn*150)]
    add(f'Aileron_{side}',f'Aileron {side}',fillet(prism(pts,37,4),1.0))

for side,y in [('L',-22),('R',22)]:
    sec=[(292,y,39,8,8),(307,y,53,11,16),(319,y,72,12,22),(327,y,86,10,14)]
    add(f'MotorLeg_{side}',f'Motor arch leg {side}',loft(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(6,44,App.Vector(327,-22,86),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,6,App.Vector(327,0,86),App.Vector(1,0,0)),'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(357,0,86),App.Vector(1,0,0)),'REFERENCE')

for side,y in [('L',-188),('R',188)]:
    w=Part.makePolygon([App.Vector(318,y,36),App.Vector(370,y,36),App.Vector(420,y,105),App.Vector(404,y,146),App.Vector(356,y,124),App.Vector(318,y,36)])
    add(f'Fin_{side}',f'Outer fin {side}',Part.Face(w).extrude(App.Vector(0,4,0)))
    rw=Part.makePolygon([App.Vector(384,y,52),App.Vector(430,y,45),App.Vector(431,y,100),App.Vector(404,y,146),App.Vector(384,y,52)])
    add(f'Rudder_{side}',f'Rudder {side}',Part.Face(rw).extrude(App.Vector(0,4,0)))

add('PitchSurface','Pitch control surface',fillet(prism([(330,-130),(392,-150),(448,-132),(448,132),(392,150),(330,130)],36,4),1.0))
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(132,-19,39)),'REFERENCE')
rails=Part.makeBox(155,4,4,App.Vector(112,-24,37)).fuse(Part.makeBox(155,4,4,App.Vector(112,20,37)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
for i,(x,y,z) in enumerate([(250,-55,42),(250,43,42),(330,-10,42),(334,10,48)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')
for name,x,y,l,axis in [('AilL',334,-176,70,'y'),('AilR',334,176,70,'y'),('Pitch',370,-120,240,'y'),('RudL',392,-186,78,'z'),('RudR',392,190,78,'z')]:
    sh=Part.makeCylinder(0.75,l,App.Vector(x,y,42 if axis=='y' else 52),App.Vector(0,1,0) if axis=='y' else App.Vector(0,0,1))
    add('Hinge_'+name,'1.5mm hinge axis '+name,sh,'PETG')

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v05_MEASURED_MASTER.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v05_MEASURED_MASTER.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v05_MEASURED_MASTER_assembly.stl'))
print('V05_SAVED',len(phys))
