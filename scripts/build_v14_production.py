
# Open motor arch and pusher mount.
for side,y in [('L',-23),('R',23)]:
    sec=[(286,y,39,8,7),(298,y,51,10,14),(309,y,66,12,20),(320,y,82,10,13)]
    add('MotorLeg_'+side,'Motor arch leg '+side,loft(sec),'PETG')
add('MotorBridge','Motor bridge',Part.makeCylinder(6,46,App.Vector(320,-23,82),App.Vector(0,1,0)),'PETG')
add('Firewall','Motor firewall',Part.makeCylinder(17,6,App.Vector(320,0,82),App.Vector(1,0,0)),'PETG')
add('PropEnvelope','6x4 prop envelope',Part.makeCylinder(76,1,App.Vector(351,0,82),App.Vector(1,0,0)),'REFERENCE')

# Outboard twin fins and separate rudders.
for side,sgn in [('L',-1),('R',1)]:
    y=sgn*191
    fw=Part.makePolygon([App.Vector(326,y,39),App.Vector(370,y,39),App.Vector(415,y,99),App.Vector(404,y,137),App.Vector(365,y,118),App.Vector(326,y,39)])
    add('Fin_'+side,'Fin '+side,Part.Face(fw).extrude(App.Vector(0,sgn*3.2,0)))
    rw=Part.makePolygon([App.Vector(382,y,52),App.Vector(422,y,47),App.Vector(424,y,95),App.Vector(404,y,137),App.Vector(382,y,52)])
    add('Rudder_'+side,'Rudder '+side,Part.Face(rw).extrude(App.Vector(0,sgn*3.2,0)))

# Real packaging references.
add('BatteryEnvelope','3S 2200 envelope',Part.makeBox(110,38,28,App.Vector(128,-19,39)),'REFERENCE')
rails=Part.makeBox(155,4,4,App.Vector(108,-24,37)).fuse(Part.makeBox(155,4,4,App.Vector(108,20,37)))
add('BatteryRails','Adjustable battery rails',rails,'PETG')
for i,(x,y,z) in enumerate([(245,-52,42),(245,40,42),(326,-10,43),(333,10,49)],1):
    add(f'Servo{i}Envelope',f'Servo {i} envelope',Part.makeBox(24,12,25,App.Vector(x,y,z)),'REFERENCE')

# Hinge axes.
for name,x,y,l,axis in [('AilL',350,-168,64,'y'),('AilR',350,168,64,'y'),('PitchL',375,-62,45,'y'),('PitchR',375,20,45,'y'),('RudL',393,-189,74,'z'),('RudR',393,193,74,'z')]:
    sh=Part.makeCylinder(0.75,l,App.Vector(x,y,44 if axis=='y' else 54),App.Vector(0,1,0) if axis=='y' else App.Vector(0,0,1))
    add('Hinge_'+name,'1.5 mm hinge axis '+name,sh,'PETG')

doc.recompute()
fc=os.path.join(CAD,'Hydrofoam_Final_Master_v14_PRODUCTION.FCStd'); doc.saveAs(fc)
phys=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Material','')!='REFERENCE' and not o.Shape.isNull()]
Part.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v14_PRODUCTION.step'))
Mesh.export(phys,os.path.join(CAD,'Hydrofoam_Final_Master_v14_PRODUCTION_assembly.stl'))
# Export each physical component and audit P2S envelope + volume.
audit=[]
for o in phys:
    fn=os.path.join(PARTS,o.Name+'.stl'); Mesh.export([o],fn)
    bb=o.Shape.BoundBox
    audit.append({'name':o.Name,'material':getattr(o,'Material',''),'dx':bb.XLength,'dy':bb.YLength,'dz':bb.ZLength,'volume_mm3':o.Shape.Volume,'fits_P2S':bb.XLength<=256 and bb.YLength<=256 and bb.ZLength<=256})
with open(os.path.join(ROOT,'docs','V14_PART_AUDIT.json'),'w') as f: json.dump(audit,f,indent=2)
print('V14_SAVED',len(phys),'parts',sum(1 for a in audit if a['fits_P2S']),'fit')
