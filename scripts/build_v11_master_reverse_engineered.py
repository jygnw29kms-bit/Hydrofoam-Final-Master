import FreeCAD as App
import Part, Mesh, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
CAD=os.path.join(ROOT,'cad'); REND=os.path.join(ROOT,'renders','v11')
os.makedirs(CAD,exist_ok=True); os.makedirs(REND,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v11')

def add(name,label,shape,mat='PLA'):
    o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape
    o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat
    return o

def ellipse_wire(x,y,z,wy,hz,n=40):
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

def fillet(sh,r):
    try:return sh.makeFillet(r,sh.Edges)
    except:return sh

# Reverse-engineered from exact Final Master top/side views; 450 mm overall length.
# Measured master ratios: width ~1.05*L, sponson centers ~270 mm, sponson width ~60 mm.

# Twin forward sponsons, long teardrop/boat shape
for side,y in [('L',-136),('R',136)]:
    sec=[(42,y,24,5,5),(52,y,26,18,13),(72,y,28,34,22),(105,y,29,50,30),
         (150,y,29,58,36),(205,y,28,60,38),(260,y,27,58,36),(305,y,26,52,31),
         (338,y,25,38,23),(358,y,24,18,12),(366,y,24,6,6)]
    add('Sponson_'+side,'Master sponson '+side,loft(sec))
    add('Skid_'+side,'PETG skid '+side,fillet(Part.makeBox(245,18,3,App.Vector(82,y-9,6)),1.4),'PETG')

# Center fuselage, pointed nose and low boat-like underside
body=[(0,0,27,5,5),(18,0,30,20,12),(42,0,34,42,22),(72,0,40,66,31),
      (108,0,47,92,40),(150,0,52,112,46),(195,0,52,122,46),(235,0,49,116,41),
      (270,0,45,100,34),(300,0,40,80,27),(325,0,36,58,21),(345,0,33,36,15),(360,0,31,18,9)]
add('CenterFuselage','Master center fuselage',loft(body))

# Low elongated canopy/service hatch
can=[(60,0,45,14,7),(80,0,53,30,14),(105,0,61,48,21),(135,0,67,60,26),
     (165,0,68,62,27),(190,0,63,50,21),(212,0,55,30,14),(225,0,49,14,7)]
add('Canopy','Master canopy',loft(can))

# Shoulder/deck panels traced from master top view. They bridge center body to sponsons and sweep aft.
for side,sgn in [('L',-1),('R',1)]:
    pts=[(55,sgn*30),(86,sgn*50),(122,sgn*69),(162,sgn*83),(205,sgn*96),(248,sgn*105),
         (285,sgn*116),(315,sgn*132),(340,sgn*151),(360,sgn*176),(372,sgn*198),
         (354,sgn*205),(330,sgn*191),(302,sgn*171),(270,sgn*150),(235,sgn*134),
         (198,sgn*121),(158,sgn*107),(120,sgn*89),(86,sgn*65)]
    add('Shoulder_'+side,'Master shoulder deck '+side,fillet(prism(pts,31,6.5),2.5))

# Outer rear flying surfaces and orange-tip wing silhouette
for side,sgn in [('L',-1),('R',1)]:
    pts=[(285,sgn*120),(315,sgn*145),(350,sgn*176),(385,sgn*210),(420,sgn*225),(445,sgn*218),
         (448,sgn*194),(425,sgn*180),(390,sgn*164),(350,sgn*145),(315,sgn*130)]
    add('OuterSurface_'+side,'Outer rear surface '+side,fillet(prism(pts,34,4.2),1.1))
    # Separate inboard pitch surface
    inner=[(330,sgn*34),(370,sgn*42),(410,sgn*55),(445,sgn*70),(447,sgn*54),(405,sgn*38),(360,sgn*28)]
    add('PitchSurface_'+side,'Pitch surface '+side,fillet(prism(inner,34,4),1.0))

# Compact open pusher motor arch, as visible in side/master ISO view
for side,y in [('L',-24),('R',24)]:
    sec=[(288,y,37,8,7),(300,y,47,10,14),(311,y,61,12,20),(321,y,75,11,18),(328,y,86,9,11)]
    add('MotorLeg_'+side,'Motor arch leg '+side,loft(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(6,48,App.Vector(328,-24,86),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,6,App.Vector(328,0,86),App.Vector(1,0,0)),'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(359,0,86),App.Vector(1,0,0)),'REFERENCE')

# Tall swept fins at far outboard rear positions
for side,sgn in [('L',-1),('R',1)]:
    y=sgn*205
    wire=Part.makePolygon([App.Vector(334,y,36),App.Vector(370,y,36),App.Vector(410,y,64),App.Vector(430,y,101),
                           App.Vector(420,y,126),App.Vector(388,y,111),App.Vector(360,y,85),App.Vector(334,y,36)])
    add('Fin_'+side,'Master fin '+side,Part.Face(wire).extrude(App.Vector(0,sgn*3.2,0)))
    rw=Part.makePolygon([App.Vector(389,y,52),App.Vector(430,y,48),App.Vector(430,y,98),App.Vector(420,y,126),App.Vector(389,y,52)])
    add('Rudder_'+side,'Rudder '+side,Part.Face(rw).extrude(App.Vector(0,sgn*3.2,0)))

# Packaging references only. Exterior is frozen by MASTER_LOCK.
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(125,-19,38)),'REFERENCE')
rails=Part.makeBox(155,4,4,App.Vector(108,-24,36)).fuse(Part.makeBox(155,4,4,App.Vector(108,20,36)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
for i,(x,y,z) in enumerate([(245,-52,42),(245,40,42),(320,-10,43),(326,10,48)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v11_REVERSE_ENGINEERED.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v11_REVERSE_ENGINEERED.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v11_REVERSE_ENGINEERED_assembly.stl'))
print('V11_SAVED',len(phys))
