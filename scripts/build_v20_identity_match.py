import FreeCAD as App
import Part, Mesh, os, math, json
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad'); PARTS=os.path.join(ROOT,'print','v20_parts'); DOCS=os.path.join(ROOT,'docs')
os.makedirs(CAD,exist_ok=True); os.makedirs(PARTS,exist_ok=True)
doc=App.newDocument('Hydrofoam_Final_Master_v20')
def add(name,label,shape,mat='PLA',visual=True):
 o=doc.addObject('PartDesign::Feature',name); o.Label=label; o.Shape=shape; o.addProperty('App::PropertyString','Material','Manufacturing').Material=mat; o.addProperty('App::PropertyBool','Visual','Manufacturing').Visual=visual; return o
def hull_wire(x,y,z,w,h):
 # smooth upper deck + sloped chines + flatter planing bottom
 pts=[App.Vector(x,y,z+h*.5),App.Vector(x,y-w*.34,z+h*.34),App.Vector(x,y-w*.50,z+h*.05),App.Vector(x,y-w*.46,z-h*.30),App.Vector(x,y-w*.28,z-h*.50),App.Vector(x,y+w*.28,z-h*.50),App.Vector(x,y+w*.46,z-h*.30),App.Vector(x,y+w*.50,z+h*.05),App.Vector(x,y+w*.34,z+h*.34),App.Vector(x,y,z+h*.5)]
 return Part.makePolygon(pts)
def ell_wire(x,y,z,w,h,n=48):
 pts=[App.Vector(x,y+w*.5*math.cos(2*math.pi*i/n),z+h*.5*math.sin(2*math.pi*i/n)) for i in range(n)]; pts.append(pts[0]); return Part.makePolygon(pts)
def loft(sec,wire=hull_wire): return Part.makeLoft([wire(*s) for s in sec],True,False)
def shell(sec,t=.8,wire=hull_wire):
 out=loft(sec,wire); inn=[(x,y,z,max(1,w-2*t),max(1,h-2*t)) for x,y,z,w,h in sec]
 try:return out.cut(loft(inn,wire))
 except:return out
def prism(points,z,t):
 vs=[App.Vector(x,y,z) for x,y in points]; return Part.Face(Part.makePolygon(vs+[vs[0]])).extrude(App.Vector(0,0,t))
def fillet(s,r):
 try:return s.makeFillet(r,s.Edges)
 except:return s
def split_x(shape,x,name,mat='PLA'):
 b=shape.BoundBox; p=12; a=shape.common(Part.makeBox(x-b.XMin+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(b.XMin-p,b.YMin-p,b.ZMin-p))); c=shape.common(Part.makeBox(b.XMax-x+p,b.YLength+2*p,b.ZLength+2*p,App.Vector(x,b.YMin-p,b.ZMin-p))); add(name+'_Front',name+' front',a,mat); add(name+'_Rear',name+' rear',c,mat)
# Side sponsons: more forward, shorter aft taper; flat planing bottom.
for side,sgn in [('L',-1),('R',1)]:
 y=sgn*137; sec=[(24,y,27,8,8),(42,y,29,26,17),(68,y,31,45,27),(108,y,32,57,35),(158,y,32,62,38),(215,y,31,63,38),(270,y,30,59,35),(318,y,29,50,30),(352,y,28,38,23),(378,y,28,16,12)]
 split_x(shell(sec,.8),205,'Sponson_'+side); add('Skid_'+side,'PETG skid '+side,fillet(Part.makeBox(236,12,1.5,App.Vector(78,y-6,8)),.7),'PETG')
# central body: flatter underside, low upper turtledeck.
body=[(0,0,31,5,5),(20,0,33,22,12),(45,0,36,44,20),(76,0,40,68,29),(112,0,45,90,38),(152,0,49,104,44),(194,0,50,110,45),(236,0,48,104,41),(275,0,44,90,34),(309,0,40,70,27),(337,0,37,48,20),(358,0,35,22,11)]
split_x(shell(body,.8),195,'CenterBody')
can=[(52,0,50,10,6),(76,0,58,31,14),(106,0,66,53,23),(140,0,72,67,30),(174,0,71,64,28),(205,0,64,44,20),(228,0,55,16,8)]
add('Canopy','Canopy / service hatch',shell(can,.75,ell_wire))
# Raised blended shoulder decks. Outer edge overlaps sponson inner chine; z follows upper-body line.
for side,sgn in [('L',-1),('R',1)]:
 pts=[(40,sgn*18),(66,sgn*43),(98,sgn*66),(135,sgn*84),(177,sgn*97),(220,sgn*106),(260,sgn*111),(295,sgn*112),(321,sgn*108),(308,sgn*92),(274,sgn*80),(235,sgn*72),(194,sgn*67),(150,sgn*60),(110,sgn*51),(75,sgn*37),(40,sgn*18)]
 wing=fillet(prism(pts,42,2.0),1.0); split_x(wing,185,'ShoulderWing_'+side)
# Rear deck surfaces at same upper datum, sweeping outward exactly behind sponsons.
for side,sgn in [('L',-1),('R',1)]:
 fixed=[(274,sgn*72),(307,sgn*94),(342,sgn*123),(379,sgn*154),(417,sgn*181),(448,sgn*188),(449,sgn*157),(418,sgn*139),(380,sgn*119),(339,sgn*98),(300,sgn*80)]
 add('RearFixed_'+side,'Rear fixed surface '+side,fillet(prism(fixed,41,2.0),.8))
 outer=[(326,sgn*151),(360,sgn*188),(401,sgn*220),(444,sgn*230),(450,sgn*207),(419,sgn*185),(381,sgn*164),(342,sgn*150)]
 add('OuterControl_'+side,'Outer control '+side,fillet(prism(outer,43,2.0),.8))
 pitch=[(326,sgn*35),(363,sgn*41),(404,sgn*53),(446,sgn*65),(449,sgn*50),(406,sgn*37),(364,sgn*29)]
 add('Pitch_'+side,'Pitch surface '+side,fillet(prism(pitch,42,2.0),.7))
# Final-Master motor arch: two slim triangular side plates with an open center and exposed motor.
def arch_plate(y,sgn):
    pts=[App.Vector(292,y,45),App.Vector(301,y,45),App.Vector(323,y,80),App.Vector(322,y,88),App.Vector(315,y,88),App.Vector(299,y,58),App.Vector(292,y,55),App.Vector(292,y,45)]
    return Part.Face(Part.makePolygon(pts)).extrude(App.Vector(0,sgn*3.0,0))
add('MotorLeg_L','Motor arch plate L',arch_plate(-22,1),'PETG')
add('MotorLeg_R','Motor arch plate R',arch_plate(22,-1),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(4.5,44,App.Vector(319,-22,84),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(16,4.0,App.Vector(321,-2,84),App.Vector(1,0,0)),'PETG')
# visual motor/prop geometry: non-print reference, rendered for shape comparison
motor=Part.makeCylinder(14,32,App.Vector(324,0,84),App.Vector(1,0,0)); add('MotorVisual','Motor visual reference',motor,'REFERENCE',True)
hub=Part.makeCylinder(5,16,App.Vector(356,0,84),App.Vector(1,0,0)); add('PropHubVisual','Prop hub visual',hub,'REFERENCE',True)
blade1=Part.makeBox(3,5,66,App.Vector(369,-2.5,51)); blade2=Part.makeBox(3,66,5,App.Vector(369,-33,81.5)); add('PropVisual','Prop visual',blade1.fuse(blade2),'REFERENCE',True)

# Final-Master twin fins: swept, tapered and less slab-like; rudders follow the trailing contour.
for side,sgn in [('L',-1),('R',1)]:
    y=sgn*177
    fpts=[App.Vector(330,y,43),App.Vector(386,y,43),App.Vector(416,y,60),App.Vector(414,y,103),App.Vector(403,y,135),App.Vector(390,y,132),App.Vector(365,y,116),App.Vector(346,y,84),App.Vector(330,y,43)]
    fw=Part.makePolygon(fpts); add('Fin_'+side,'Fin '+side,Part.Face(fw).extrude(App.Vector(0,sgn*1.6,0)))
    rpts=[App.Vector(386,y,51),App.Vector(419,y,58),App.Vector(418,y,99),App.Vector(403,y,135),App.Vector(390,y,132),App.Vector(386,y,51)]
    rw=Part.makePolygon(rpts); add('Rudder_'+side,'Rudder '+side,Part.Face(rw).extrude(App.Vector(0,sgn*1.6,0)))

# Orange/black visual accent shells from the master; very thin and printable/paintable.
for side,sgn in [('L',-1),('R',1)]:
    y=sgn*137
    nose=loft([(24,y,27,8.5,8.5),(42,y,29,26.5,17.5),(58,y,30.5,39,24)],hull_wire)
    add('NoseAccent_'+side,'Orange nose accent '+side,nose,'PLA')
# hidden RC support hardware
add('BatteryEnvelope','3S2200 envelope',Part.makeBox(110,38,28,App.Vector(125,-19,38)),'REFERENCE',False); rails=Part.makeBox(155,3,3,App.Vector(105,-23,37)).fuse(Part.makeBox(155,3,3,App.Vector(105,20,37))); add('BatteryRails','Battery rails',rails,'PETG',False)
for i,(x,y,z) in enumerate([(245,-48,42),(245,36,42),(324,-10,43),(332,10,49)],1): add(f'Servo{i}Envelope',f'Servo {i}',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE',False)
doc.recompute(); fc=os.path.join(CAD,'Hydrofoam_Final_Master_v20_IDENTITY_MATCH.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]; vis=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Visual',False) and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v20_IDENTITY_MATCH.step')); Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v20_IDENTITY_MATCH_assembly.stl')); Mesh.export(vis,os.path.join(CAD,'Hydrofoam_Final_Master_v20_IDENTITY_MATCH_visual.stl'))
audit=[]
for o in phys:
 Mesh.export([o],os.path.join(PARTS,o.Name+'.stl')); b=o.Shape.BoundBox; audit.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':b.XLength,'dy':b.YLength,'dz':b.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':b.XLength<=256 and b.YLength<=256 and b.ZLength<=256})
json.dump(audit,open(os.path.join(DOCS,'V20_PART_AUDIT.json'),'w'),indent=2); print('V20_SAVED',len(phys),'fit',sum(x['fits_P2S'] for x in audit),'visual',len(vis))