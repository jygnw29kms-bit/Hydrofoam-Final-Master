import FreeCAD as App
import Part, Mesh, os, math
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad')
os.makedirs(CAD,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v09')

def add(name,label,shape,mat='PLA'):
 o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape; o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat; return o

def ellipse_wire(x,y,z,wy,hz,n=40):
 pts=[App.Vector(x,y+(wy/2)*math.cos(2*math.pi*i/n),z+(hz/2)*math.sin(2*math.pi*i/n)) for i in range(n)]; pts.append(pts[0]); return Part.makePolygon(pts)
def loft_ell(sec): return Part.makeLoft([ellipse_wire(*s) for s in sec],True,False)
def prism(points,z,t):
 pts=[App.Vector(x,y,z) for x,y in points]; return Part.Face(Part.makePolygon(pts+[pts[0]])).extrude(App.Vector(0,0,t))
def fillet(s,r):
 try:return s.makeFillet(r,s.Edges)
 except:return s

def wing_wire(x,yi,yo,z,t):
 # rounded-ish closed yz section, root thicker than tip
 pts=[App.Vector(x,yi,z-t*.35),App.Vector(x,yi+8,z+t*.50),App.Vector(x,yo-8,z+t*.22),App.Vector(x,yo,z),App.Vector(x,yo-8,z-t*.22),App.Vector(x,yi+8,z-t*.50),App.Vector(x,yi,z-t*.35)]
 return Part.makePolygon(pts)
def wing_loft(stations): return Part.makeLoft([wing_wire(*s) for s in stations],True,False)

# Final Master sponsons: long pointed boat bodies, separated from center fuselage
for side,sgn in [('L',-1),('R',1)]:
 y=sgn*145
 sec=[(12,y,24,5,5),(28,y,26,20,15),(52,y,28,36,24),(88,y,29,48,32),(140,y,29,54,37),(205,y,28,56,38),(270,y,27,54,36),(320,y,26,48,31),(356,y,26,34,23),(378,y,26,12,10)]
 add('Sponson_'+side,'Final Master Sponson '+side,loft_ell(sec))
 add('Skid_'+side,'PETG skid '+side,fillet(Part.makeBox(255,16,3,App.Vector(70,y-8,6)),1.2),'PETG')

# Central fuselage with long low nose and low tail
body=[(28,0,30,6,6),(44,0,33,24,14),(68,0,37,46,24),(96,0,43,68,32),(128,0,49,84,40),(164,0,53,94,45),(205,0,52,92,43),(245,0,48,82,36),(282,0,43,64,28),(315,0,38,44,20),(344,0,34,22,12)]
add('CenterFuselage','Final Master center fuselage',loft_ell(body))
can=[(62,0,49,12,7),(82,0,56,28,13),(110,0,65,44,20),(142,0,70,52,24),(173,0,68,48,22),(202,0,60,30,14),(220,0,53,14,7)]
add('Canopy','Canopy / hatch',loft_ell(can))

# Blended shoulder wings: 3D lofts grown from fuselage to outer shoulder
for side,sgn in [('L',-1),('R',1)]:
 st=[(62,sgn*18,sgn*62,34,8.5),(105,sgn*28,sgn*92,34,9.0),(155,sgn*35,sgn*118,33,9.0),(205,sgn*40,sgn*138,32,8.5),(252,sgn*38,sgn*165,31,7.5),(292,sgn*32,sgn*195,31,6.5),(325,sgn*26,sgn*218,32,5.5),(350,sgn*22,sgn*226,33,4.5)]
 add('Wing_'+side,'Blended shoulder wing '+side,wing_loft(st))

# Rear outer flying surfaces as separate swept panels, not one rectangular slab
for side,sgn in [('L',-1),('R',1)]:
 panel=[(302,sgn*132),(338,sgn*180),(382,sgn*212),(430,sgn*205),(445,sgn*176),(398,sgn*158),(350,sgn*142)]
 add('OuterSurface_'+side,'Outer rear control surface '+side,fillet(prism(panel,35,4.2),1.1))
 inner=[(330,sgn*36),(372,sgn*50),(434,sgn*70),(444,sgn*58),(394,sgn*42),(350,sgn*30)]
 add('PitchSurface_'+side,'Inboard pitch surface '+side,fillet(prism(inner,34,4.2),1.1))

# Open compact motor arch and pusher
for side,y in [('L',-23),('R',23)]:
 sec=[(286,y,38,8,7),(300,y,50,10,14),(310,y,66,12,20),(319,y,80,10,13)]
 add('MotorLeg_'+side,'Motor arch leg '+side,loft_ell(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(6,46,App.Vector(319,-23,80),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,6,App.Vector(319,0,80),App.Vector(1,0,0)),'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(350,0,80),App.Vector(1,0,0)),'REFERENCE')

# Tall swept twin fins, positioned outboard as in Final Master
for side,sgn in [('L',-1),('R',1)]:
 y=sgn*188
 w=Part.makePolygon([App.Vector(325,y,37),App.Vector(368,y,37),App.Vector(414,y,101),App.Vector(402,y,139),App.Vector(364,y,119),App.Vector(325,y,37)])
 add('Fin_'+side,'Outer fin '+side,Part.Face(w).extrude(App.Vector(0,sgn*3.2,0)))
 rw=Part.makePolygon([App.Vector(381,y,50),App.Vector(421,y,45),App.Vector(422,y,96),App.Vector(402,y,139),App.Vector(381,y,50)])
 add('Rudder_'+side,'Rudder '+side,Part.Face(rw).extrude(App.Vector(0,sgn*3.2,0)))

# Packaging references remain inside master exterior
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(126,-19,38)),'REFERENCE')
rails=Part.makeBox(155,4,4,App.Vector(108,-24,36)).fuse(Part.makeBox(155,4,4,App.Vector(108,20,36))); add('BatteryRails','Battery rails',rails,'PETG')
for i,(x,y,z) in enumerate([(245,-52,41),(245,40,41),(319,-9,41),(326,9,46)],1): add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')

doc.recompute(); fc=os.path.join(CAD,'Hydrofoam_Final_Master_v09_MASTER_SURFACE.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v09_MASTER_SURFACE.step')); Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v09_MASTER_SURFACE_assembly.stl'))
print('V09_SAVED',len(phys))
