import FreeCAD as App
import Part, Mesh, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); REND=os.path.join(ROOT,'renders','v02')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v03')
L=450.0; W=300.0; DECK_Z=38.0

def add(name,label,shape,mat='PLA'):
    o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat
    return o

def ellipse_wire(x,y,z,wy,hz,n=28):
    pts=[]
    for i in range(n):
        a=2.0*math.pi*i/n
        pts.append(App.Vector(x, y+(wy/2.0)*math.cos(a), z+(hz/2.0)*math.sin(a)))
    pts.append(pts[0])
    return Part.makePolygon(pts)

def loft_sections(sections):
    return Part.makeLoft([ellipse_wire(*s) for s in sections],True,False)

def poly_prism(points,z0,t):
    pts=[App.Vector(x,y,z0) for x,y in points]
    wire=Part.makePolygon(pts+[pts[0]])
    return Part.Face(wire).extrude(App.Vector(0,0,t))

def safe_fillet(sh,r):
    try: return sh.makeFillet(r,sh.Edges)
    except: return sh

# Streamlined twin sponsons: fine nose, full planing midbody, tapered stern
for side, yc in [('L',-112),('R',112)]:
    secs=[
      (4,yc,25,10,12), (30,yc,28,28,24), (82,yc,31,44,34),
      (170,yc,32,52,38), (270,yc,32,54,36), (356,yc,31,48,32),
      (420,yc,30,34,24), (446,yc,29,14,14)]
    sh=loft_sections(secs)
    add(f'Sponson_{side}',f'Streamlined Sponson {side}',sh)
    # flat PETG runner aligned to planing region
    skid=Part.makeBox(330,18,3,App.Vector(62,yc-9,9))
    add(f'Skid_{side}',f'PETG Skid {side}',safe_fillet(skid,1.4),'PETG')

# Blended lifting center deck, broad delta/organic planform
center_pts=[(28,-48),(70,-76),(150,-96),(270,-94),(360,-72),(420,-38),(438,0),(420,38),(360,72),(270,94),(150,96),(70,76),(28,48)]
deck=poly_prism(center_pts,30,8)
deck=safe_fillet(deck,4.5)
add('CenterDeck','Blended lifting center deck',deck)

# side blend panels to sponsons, preserving open visual channels
for side,sgn in [('L',-1),('R',1)]:
    pts=[(78,sgn*66),(112,sgn*86),(245,sgn*95),(355,sgn*76),(388,sgn*58),(348,sgn*48),(215,sgn*61),(110,sgn*54)]
    panel=poly_prism(pts,36,7)
    add(f'Blend_{side}',f'Blended wing panel {side}',safe_fillet(panel,3.0))

# Central low pod shaped as longitudinal loft
podsecs=[(78,0,42,20,16),(120,0,47,42,28),(182,0,51,58,34),(242,0,50,54,32),(298,0,46,40,26),(326,0,42,20,16)]
pod=loft_sections(podsecs)
add('CenterPod','Final Master center pod',pod)
# hatch follows pod upper surface visually
hatch=loft_sections([(145,0,64,42,6),(205,0,68,52,7),(258,0,64,40,6)])
add('Hatch','Flush maintenance hatch',hatch)

# Battery tray + envelope (reference geometry physically excluded later)
rails=Part.makeBox(150,4,4,App.Vector(126,-24,49)).fuse(Part.makeBox(150,4,4,App.Vector(126,20,49)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
batt=Part.makeBox(110,38,28,App.Vector(145,-19,51)); bo=add('BatteryEnvelope','3S2200 envelope',batt,'REFERENCE')

# Swept aerodynamic motor arch: two tapered pylons + rounded bridge
for side,yc in [('L',-34),('R',34)]:
    psecs=[(316,yc,44,12,10),(334,yc,61,16,20),(347,yc,82,18,28),(354,yc,98,16,18)]
    add(f'MotorPylon_{side}',f'Motor Pylon {side}',loft_sections(psecs),'PETG')
bridge=Part.makeCylinder(10,68,App.Vector(354,-34,98),App.Vector(0,1,0))
add('MotorBridge','Aerodynamic motor bridge',bridge,'PETG')
fire=Part.makeCylinder(22,6,App.Vector(354,0,98),App.Vector(1,0,0))
add('Firewall','Motor firewall',fire,'PETG')
# reference prop disk
prop=Part.makeCylinder(76,1.5,App.Vector(387,0,98),App.Vector(1,0,0)); add('PropEnvelope','6x4 prop envelope',prop,'REFERENCE')

# Twin fins, swept and integrated
for side,y in [('L',-82),('R',82)]:
    finpts=[(318,y),(374,y),(402,y),(388,y),(354,y)]
    # x-z profile via face in XZ then extrude Y
    w=Part.makePolygon([App.Vector(320,y,43),App.Vector(374,y,43),App.Vector(402,y,98),App.Vector(386,y,122),App.Vector(352,y,105),App.Vector(320,y,43)])
    f=Part.Face(w).extrude(App.Vector(0,4,0)); add(f'Fin_{side}',f'Fin {side}',f)
    rw=Part.makePolygon([App.Vector(386,y,62),App.Vector(418,y,58),App.Vector(416,y,98),App.Vector(386,y,122),App.Vector(386,y,62)])
    add(f'Rudder_{side}',f'Rudder {side}',Part.Face(rw).extrude(App.Vector(0,4,0)))

# Pitch surface: swept central tailplane with detached elevator
stabpts=[(326,-70),(365,-92),(430,-72),(430,72),(365,92),(326,70)]
stab=poly_prism(stabpts,45,6); add('Tailplane','Integrated tailplane',safe_fillet(stab,2.0))
elevpts=[(385,-72),(430,-72),(442,-58),(442,58),(430,72),(385,72)]
elev=poly_prism(elevpts,46,5); add('PitchSurface','Pitch control surface',safe_fillet(elev,1.5))

# Ailerons shaped with deck trailing contour
for side,sgn in [('L',-1),('R',1)]:
    pts=[(248,sgn*67),(350,sgn*63),(393,sgn*48),(362,sgn*78),(275,sgn*92)]
    add(f'Aileron_{side}',f'Aileron {side}',safe_fillet(poly_prism(pts,45,5),1.5))

# Hinge pin visual/structural placeholders (1.5 mm axis)
for name,x,y,l,axis in [
 ('Hinge_Ail_L',286,-76,75,'y'),('Hinge_Ail_R',286,76,75,'y'),('Hinge_Pitch',389,-62,124,'y'),
 ('Hinge_Rud_L',386,-80,62,'z'),('Hinge_Rud_R',386,84,62,'z')]:
    if axis=='y': sh=Part.makeCylinder(0.75,l,App.Vector(x,y,49),App.Vector(0,1,0))
    else: sh=Part.makeCylinder(0.75,l,App.Vector(x,y,68),App.Vector(0,0,1))
    add(name,name,sh,'PETG')

# Servo envelopes (reference) positioned on short pushrod paths
for i,(x,y,z) in enumerate([(270,-55,50),(270,43,50),(340,-11,53),(349,10,59)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v03_MASTER_FORM.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v03_MASTER_FORM.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v03_MASTER_FORM_assembly.stl'))
print('V02_SAVED',len(phys))

