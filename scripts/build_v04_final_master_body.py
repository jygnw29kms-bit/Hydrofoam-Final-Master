import FreeCAD as App
import Part, Mesh, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); REND=os.path.join(ROOT,'renders','v04')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v04')

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

def loft(sec): return Part.makeLoft([ellipse_wire(*s) for s in sec],True,False)

def prism(points,z,t):
    pts=[App.Vector(x,y,z) for x,y in points]
    w=Part.makePolygon(pts+[pts[0]])
    return Part.Face(w).extrude(App.Vector(0,0,t))

def fillet(s,r):
    try: return s.makeFillet(r,s.Edges)
    except: return s

# FINAL MASTER REFERENCE: twin slim boat-like sponsons, low central fuselage, blended shoulder wings,
# twin swept fins, short open pusher arch. 450 mm class, overall width ~300 mm.

# Sponsons: pointed orange-nose style, long waterline, fuller lower body, clean stern taper
for side,yc in [('L',-111),('R',111)]:
    sec=[
        (4,yc,27,5,5),(18,yc,29,20,16),(45,yc,31,34,25),(90,yc,32,44,32),
        (160,yc,31,50,36),(245,yc,30,52,36),(320,yc,30,49,33),(382,yc,30,41,27),
        (428,yc,31,28,20),(448,yc,31,8,8)]
    add(f'Sponson_{side}',f'Final Master Sponson {side}',loft(sec))
    skid=fillet(Part.makeBox(315,14,3,App.Vector(66,yc-7,8)),1.2)
    add(f'Skid_{side}',f'PETG skid {side}',skid,'PETG')

# Main center body: narrow nose, cockpit volume mid-forward, tail taper
center_sec=[
    (40,0,35,18,12),(68,0,39,42,24),(100,0,45,64,34),(145,0,52,86,45),
    (200,0,55,92,48),(255,0,53,82,42),(310,0,47,58,31),(352,0,42,36,22),(382,0,38,20,14)]
add('CenterFuselage','Final Master central fuselage',loft(center_sec))

# Canopy, kept separate for future hatch integration
canopy_sec=[(92,0,60,26,12),(125,0,69,48,22),(165,0,75,58,28),(205,0,73,50,24),(232,0,65,28,13)]
add('Canopy','Canopy / service hatch',loft(canopy_sec),'PLA')

# Blended shoulder wings exactly in Master spirit: swept, organic, low thickness
wing_pts=[(72,-44),(108,-72),(168,-92),(240,-96),(300,-86),(352,-64),(395,-42),(420,-28),
          (420,28),(395,42),(352,64),(300,86),(240,96),(168,92),(108,72),(72,44)]
add('ShoulderDeck','Blended shoulder deck',fillet(prism(wing_pts,34,8),3.5))

# Thin rear deck / tailplane bridge
rear_pts=[(292,-74),(345,-92),(418,-76),(446,-54),(446,54),(418,76),(345,92),(292,74)]
add('RearDeck','Low rear lifting deck',fillet(prism(rear_pts,34,6),2.0))

# Ailerons integrated into trailing shoulder edges
for side,sgn in [('L',-1),('R',1)]:
    pts=[(262,sgn*72),(340,sgn*66),(398,sgn*48),(420,sgn*32),(386,sgn*42),(330,sgn*58)]
    add(f'Aileron_{side}',f'Aileron {side}',fillet(prism(pts,43,4.5),1.2))

# Short open motor arch, central pusher
for side,y in [('L',-24),('R',24)]:
    sec=[(307,y,43,10,10),(326,y,61,14,20),(338,y,82,15,28),(344,y,96,12,16)]
    add(f'MotorLeg_{side}',f'Motor arch leg {side}',loft(sec),'PETG')
bridge=Part.makeCylinder(7,48,App.Vector(344,-24,96),App.Vector(0,1,0))
add('MotorBridge','Pusher motor bridge',bridge,'PETG')
fire=Part.makeCylinder(18,6,App.Vector(344,0,96),App.Vector(1,0,0))
add('Firewall','Motor firewall',fire,'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(376,0,96),App.Vector(1,0,0)),'REFERENCE')

# Twin vertical fins: tall, swept and narrow like the Master
for side,y in [('L',-74),('R',74)]:
    w=Part.makePolygon([App.Vector(340,y,38),App.Vector(392,y,38),App.Vector(418,y,112),App.Vector(401,y,151),App.Vector(364,y,128),App.Vector(340,y,38)])
    add(f'Fin_{side}',f'Fin {side}',Part.Face(w).extrude(App.Vector(0,4,0)))
    rw=Part.makePolygon([App.Vector(392,y,54),App.Vector(425,y,47),App.Vector(427,y,104),App.Vector(401,y,151),App.Vector(392,y,54)])
    add(f'Rudder_{side}',f'Rudder {side}',Part.Face(rw).extrude(App.Vector(0,4,0)))

# Central elevator integrated in thin tail surface
stab=fillet(prism([(325,-58),(376,-70),(445,-56),(445,56),(376,70),(325,58)],39,4.5),1.2)
add('Tailplane','Central tailplane',stab)
elev=fillet(prism([(386,-56),(445,-56),(449,-42),(449,42),(445,56),(386,56)],40,4),1.0)
add('PitchSurface','Pitch control surface',elev)

# Battery tray and service hardware inside the fixed Master exterior
rails=Part.makeBox(150,4,4,App.Vector(120,-24,43)).fuse(Part.makeBox(150,4,4,App.Vector(120,20,43)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
add('BatteryEnvelope','3S 2200 envelope',Part.makeBox(110,38,28,App.Vector(145,-19,45)),'REFERENCE')
for i,(x,y,z) in enumerate([(260,-45,46),(260,33,46),(334,-10,46),(344,10,52)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')

# Hinge axes as real construction references
for name,x,y,l,axis in [('AilL',285,-70,72,'y'),('AilR',285,70,72,'y'),('Pitch',390,-50,100,'y'),('RudL',397,-72,74,'z'),('RudR',397,76,74,'z')]:
    sh=Part.makeCylinder(0.75,l,App.Vector(x,y,46 if axis=='y' else 56),App.Vector(0,1,0) if axis=='y' else App.Vector(0,0,1))
    add('Hinge_'+name,'1.5mm hinge axis '+name,sh,'PETG')

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v04_FINAL_MASTER_BODY.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v04_FINAL_MASTER_BODY.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v04_FINAL_MASTER_BODY_assembly.stl'))
print('V04_SAVED',len(phys))