import FreeCAD as App
import Part, Mesh, os, math

ROOT = r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD = os.path.join(ROOT,'cad')
REND = os.path.join(ROOT,'renders')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v01')

# --- master parameters (mm) ---
L=450.0
W=300.0
SPONSON_W=58.0
SPONSON_H=48.0
SPONSON_Y=105.0
DECK_Z=34.0
DECK_T=10.0

# helper: rounded loft from rectangular/elliptic-ish sections
def rounded_rect_wire(x,y,z,l,w,h,r=8):
    # ellipse-like closed bezier approximation using rounded rectangle from box fillet
    sh=Part.makeBox(l,w,h,App.Vector(x,y,z))
    try:
        edges=[e for e in sh.Edges if abs((e.Vertexes[-1].Point-e.Vertexes[0].Point).z)>h*0.8]
        return sh.makeFillet(min(r,w/2-0.5,h/2-0.5), edges)
    except:
        return sh

def add_obj(name,label,shape,color=(0.85,0.85,0.88)):
    o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyString','Material','Manufacturing').Material='PLA'
    try:
        if o.ViewObject:
            o.ViewObject.ShapeColor=color
    except Exception:
        pass
    return o

# sponsons: 2-piece modules each, tapered noses with planing underside
for side, y0 in [('L',-SPONSON_Y-SPONSON_W/2),('R',SPONSON_Y-SPONSON_W/2)]:
    # front module 0..225
    body1=rounded_rect_wire(20,y0,8,205,SPONSON_W,SPONSON_H,10)
    nose=Part.makeCone(8,SPONSON_W/2,35,App.Vector(0,y0+SPONSON_W/2,32),App.Vector(1,0,0))
    sh1=body1.fuse(nose)
    add_obj(f'Sponson_{side}_Front',f'Sponson {side} Front',sh1)
    # rear module
    sh2=rounded_rect_wire(225,y0,8,205,SPONSON_W,SPONSON_H,8)
    add_obj(f'Sponson_{side}_Rear',f'Sponson {side} Rear',sh2)
    # PETG skid runner
    skid=Part.makeBox(365,12,4,App.Vector(40,y0+SPONSON_W/2-6,4))
    so=add_obj(f'Skid_{side}',f'PETG Skid {side}',skid,(0.25,0.25,0.28)); so.Material='PETG'

# center lifting deck, split into left/right/center modules
center=Part.makeBox(310,82,DECK_T,App.Vector(75,-41,DECK_Z))
# soften leading edge with cylinders blended visually
lead=Part.makeCylinder(5,310,App.Vector(75,-41,DECK_Z+5),App.Vector(1,0,0))
center=center.fuse(lead)
add_obj('CenterDeck','Center lifting deck',center)

# outer wing/deck panels
for side, ys in [('L',-SPONSON_Y+SPONSON_W/2),('R',41)]:
    y_start = -SPONSON_Y+SPONSON_W/2 if side=='L' else 41
    width = (SPONSON_Y-SPONSON_W/2)-41
    if side=='L':
        sh=Part.makeBox(285,width,8,App.Vector(95,y_start,DECK_Z+1))
    else:
        sh=Part.makeBox(285,width,8,App.Vector(95,41,DECK_Z+1))
    add_obj(f'WingDeck_{side}',f'Wing deck {side}',sh)

# central aerodynamic pod / battery bay envelope
pod=rounded_rect_wire(110,-34,44,190,68,36,14)
add_obj('CenterPod','Center electronics pod',pod,(0.93,0.93,0.95))
# removable hatch
hatch=rounded_rect_wire(140,-30,77,125,60,5,2)
add_obj('Hatch','Removable top hatch',hatch,(0.9,0.5,0.16))

# battery envelope 3S 2200 and sliding rail representation
batt=Part.makeBox(110,38,28,App.Vector(145,-19,49))
bo=add_obj('Battery_Envelope','3S 2200 battery envelope',batt,(0.25,0.7,0.25)); bo.Material='REFERENCE'
railL=Part.makeBox(150,4,4,App.Vector(125,-24,47)); railR=Part.makeBox(150,4,4,App.Vector(125,20,47))
ro=add_obj('Battery_Rails','Battery slide rails',railL.fuse(railR),(0.2,0.2,0.2)); ro.Material='PETG'

# motor bridge / pusher mount
p1=Part.makeBox(18,18,62,App.Vector(330,-42,44)); p2=Part.makeBox(18,18,62,App.Vector(330,24,44))
bridge=Part.makeBox(18,84,14,App.Vector(330,-42,102))
mb=p1.fuse(p2).fuse(bridge)
mo=add_obj('MotorBridge','PETG motor bridge',mb,(0.28,0.28,0.30)); mo.Material='PETG'
fire=Part.makeBox(6,44,44,App.Vector(348,-22,88))
fo=add_obj('Firewall','PETG motor firewall',fire,(0.25,0.25,0.27)); fo.Material='PETG'
# motor and prop envelopes (reference)
motor=Part.makeCylinder(14,28,App.Vector(354,0,110),App.Vector(1,0,0))
ref=add_obj('Motor_Envelope','2212 motor envelope',motor,(0.35,0.35,0.35)); ref.Material='REFERENCE'
prop=Part.makeCylinder(76,2,App.Vector(383,0,110),App.Vector(1,0,0))
pr=add_obj('Prop_Envelope','6 inch prop envelope',prop,(0.75,0.85,0.95)); pr.Material='REFERENCE'
try:
    if pr.ViewObject:
        pr.ViewObject.Transparency=75
except Exception:
    pass

# twin fins and separate rudders
for side,yc in [('L',-88),('R',88)]:
    fin=Part.makePolygon([App.Vector(330,yc,48),App.Vector(390,yc,48),App.Vector(372,yc,130),App.Vector(342,yc,122),App.Vector(330,yc,48)])
    finface=Part.Face(fin).extrude(App.Vector(0,4,0))
    add_obj(f'Fin_{side}',f'Fin {side}',finface)
    rud=Part.makePolygon([App.Vector(390,yc,50),App.Vector(422,yc,50),App.Vector(402,yc,120),App.Vector(372,yc,130),App.Vector(390,yc,50)])
    rudface=Part.Face(rud).extrude(App.Vector(0,4,0))
    add_obj(f'Rudder_{side}',f'Rudder {side}',rudface,(0.95,0.55,0.15))

# pitch surface / elevator and ailerons as separate parts
pitch=Part.makeBox(68,150,6,App.Vector(366,-75,48))
add_obj('Pitch_Surface','Pitch control surface',pitch,(0.95,0.55,0.15))
for side,yy in [('L',-92),('R',47)]:
    ail=Part.makeBox(115,45,6,App.Vector(240,yy,43))
    add_obj(f'Aileron_{side}',f'Aileron {side}',ail,(0.95,0.55,0.15))

# servo envelopes 4x 10g class
servo_positions=[(245,-70,48),(245,52,48),(320,-15,52),(350,8,58)]
for i,(x,y,z) in enumerate(servo_positions,1):
    s=Part.makeBox(24,12,25,App.Vector(x,y,z))
    so=add_obj(f'Servo_{i}_Envelope',f'Servo {i} envelope',s,(0.25,0.45,0.85)); so.Material='REFERENCE'

# groups
grp=doc.addObject('App::DocumentObjectGroup','FlightStructure');
for n in ['Sponson_L_Front','Sponson_L_Rear','Sponson_R_Front','Sponson_R_Rear','CenterDeck','WingDeck_L','WingDeck_R','CenterPod','Hatch','Fin_L','Fin_R','Rudder_L','Rudder_R','Pitch_Surface','Aileron_L','Aileron_R']:
    grp.addObject(doc.getObject(n))

grp2=doc.addObject('App::DocumentObjectGroup','PETG_Functionals')
for n in ['Skid_L','Skid_R','Battery_Rails','MotorBridge','Firewall']:
    grp2.addObject(doc.getObject(n))

grp3=doc.addObject('App::DocumentObjectGroup','Reference_Envelopes')
for n in ['Battery_Envelope','Motor_Envelope','Prop_Envelope','Servo_1_Envelope','Servo_2_Envelope','Servo_3_Envelope','Servo_4_Envelope']:
    grp3.addObject(doc.getObject(n))

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v01.FCStd'); doc.saveAs(fc)
# STEP export of physical parts only
phys=[o for o in doc.Objects if hasattr(o,'Shape') and not getattr(o,'Material','')=='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v01.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v01_assembly.stl'))
print('SAVED',fc,'objects',len(phys))
