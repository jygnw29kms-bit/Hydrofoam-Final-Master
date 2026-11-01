import FreeCAD as App
import Part, Mesh, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); REND=os.path.join(ROOT,'renders','v08')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v08')
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

# Two truly integrated shoulder-wing halves. Inner edge overlaps fuselage; outer edge overlaps sponsons.
for side,sgn in [('L',-1),('R',1)]:
    pts=[
      (40,sgn*10),(72,sgn*24),(108,sgn*38),(148,sgn*50),(188,sgn*60),(228,sgn*72),
      (268,sgn*90),(304,sgn*112),(336,sgn*142),(360,sgn*176),(374,sgn*210),
      (356,sgn*226),(326,sgn*220),(294,sgn*202),(260,sgn*178),(226,sgn*154),
      (194,sgn*142),(164,sgn*136),(136,sgn*134),(110,sgn*126),(84,sgn*108),
      (62,sgn*82),(46,sgn*52)]
    add(f'Wing_{side}',f'Integrated shoulder wing {side}',fillet(prism(pts,34,7.5),3.0))

# Separate rear control panels, no full-width rectangular deck: this matches the Master top view.
for side,sgn in [('L',-1),('R',1)]:
    tailpts=[(335,sgn*58),(385,sgn*86),(442,sgn*82),(448,sgn*48),(392,sgn*44)]
    add(f'TailPanel_{side}',f'Rear tail panel {side}',fillet(prism(tailpts,31,4.5),1.2))
    ailpts=[(300,sgn*152),(338,sgn*210),(392,sgn*222),(418,sgn*196),(366,sgn*160)]
    add(f'Aileron_{side}',f'Outer control surface {side}',fillet(prism(ailpts,36,4),1.0))

for side,y in [('L',-22),('R',22)]:
    sec=[(292,y,39,8,8),(307,y,53,11,16),(319,y,72,12,22),(327,y,86,10,14)]
    add(f'MotorLeg_{side}',f'Motor arch leg {side}',loft(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(6,44,App.Vector(327,-22,86),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,6,App.Vector(327,0,86),App.Vector(1,0,0)),'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(357,0,86),App.Vector(1,0,0)),'REFERENCE')

for side,y in [('L',-188),('R',188)]:
    w=Part.makePolygon([App.Vector(326,y,36),App.Vector(370,y,36),App.Vector(414,y,98),App.Vector(400,y,134),App.Vector(362,y,116),App.Vector(326,y,36)])
    add(f'Fin_{side}',f'Outer fin {side}',Part.Face(w).extrude(App.Vector(0,3.2,0)))
    rw=Part.makePolygon([App.Vector(382,y,50),App.Vector(422,y,44),App.Vector(423,y,94),App.Vector(400,y,134),App.Vector(382,y,50)])
    add(f'Rudder_{side}',f'Rudder {side}',Part.Face(rw).extrude(App.Vector(0,3.2,0)))

# Two inboard pitch/elevator panels as shown in the Final Master top view.
for side,sgn in [('L',-1),('R',1)]:
    ep=[(342,sgn*42),(388,sgn*48),(444,sgn*56),(446,sgn*122),(390,sgn*116),(344,sgn*92)]
    add(f'PitchSurface_{side}',f'Pitch control surface {side}',fillet(prism(ep,36,4),1.0))
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(132,-19,39)),'REFERENCE')
rails=Part.makeBox(155,4,4,App.Vector(112,-24,37)).fuse(Part.makeBox(155,4,4,App.Vector(112,20,37)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
for i,(x,y,z) in enumerate([(250,-55,42),(250,43,42),(330,-10,42),(334,10,48)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')
for name,x,y,l,axis in [('AilL',334,-176,70,'y'),('AilR',334,176,70,'y'),('Pitch',370,-120,240,'y'),('RudL',392,-186,78,'z'),('RudR',392,190,78,'z')]:
    sh=Part.makeCylinder(0.75,l,App.Vector(x,y,42 if axis=='y' else 52),App.Vector(0,1,0) if axis=='y' else App.Vector(0,0,1))
    add('Hinge_'+name,'1.5mm hinge axis '+name,sh,'PETG')

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v08_MASTER_INTEGRATED.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v08_MASTER_INTEGRATED.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v08_MASTER_INTEGRATED_assembly.stl'))
print('V08_SAVED',len(phys))
