from pathlib import Path
src=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v19_surface_match.py').read_text(encoding='utf-8-sig')
s=src.replace("v19_parts","v20_parts").replace("v19_SURFACE_MATCH","v20_IDENTITY_MATCH").replace("V19_PART_AUDIT","V20_PART_AUDIT").replace("V19_SAVED","V20_SAVED").replace("Hydrofoam_Final_Master_v19","Hydrofoam_Final_Master_v20")
start=s.index('# Motor arch shortened')
end=s.index('# hidden RC support hardware')
new=r'''# Final-Master motor arch: two slim triangular side plates with an open center and exposed motor.
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
'''
s=s[:start]+new+s[end:]
# visual set must include non-print motor reference
s=s.replace("vis=[o for o in phys if getattr(o,'Visual',False)]","vis=[o for o in doc.Objects if hasattr(o,'Shape') and getattr(o,'Visual',False) and not o.Shape.isNull()]")
Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\scripts\build_v20_identity_match.py').write_text(s,encoding='utf-8')
print('PATCHED_V20')