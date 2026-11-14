"""Hydrofoam v388: parametrischer Servo-/Ruderhorn-/Gestänge-Prüfstand.
FreeCAD-Python; getrennte Prüfbaugruppe, NICHT in Master integriert.
Alle Maße in mm. Keine konstruktive Freigabe ohne tatsächlichen Lauf.
"""
import os, json, math
import FreeCAD as App
import Part, MeshPart

OUT=os.environ.get("HYDROFOAM_V388_OUT",os.path.join(os.getcwd(),"build","v388"))
os.makedirs(OUT,exist_ok=True)
doc=App.newDocument("Hydrofoam_v388_servo_linkage_coupon")
V=App.Vector
# Servo als austauschbarer geometrischer Platzhalter: Abmessungen vor Montage messen.
servo_length,servo_width,servo_height=23.0,12.5,24.0
clearance=0.5
wall=3.0
base=3.0
outer_l=servo_length+2*(wall+clearance)
outer_w=servo_width+2*(wall+clearance)
tray=Part.makeBox(outer_l,outer_w,base+12,V(0,0,0))
cavity=Part.makeBox(servo_length+2*clearance,servo_width+2*clearance,13,
                    V(wall,wall,base))
tray=tray.cut(cavity)
# Two mounting ears outside servo envelope; fasteners isolated from servo body.
for x in (5.0,outer_l-5.0):
    ear=Part.makeBox(10,8,base,V(x-5,-8,0))
    tray=tray.fuse(ear)
    tray=tray.cut(Part.makeCylinder(1.7,base+2,V(x,-4,-1)))
tray=tray.removeSplitter()
# Separate rudder test leaf and hinge knuckles with bore; pin axis along Y.
hinge_x=outer_l+24
hinge_y=outer_w/2
hinge_z=base+10
leaf=Part.makeBox(36,outer_w,3,V(hinge_x,0,hinge_z-1.5))
# Knuckle cylinders; bores must remain clear for a removable metal pin.
for ya,yb in ((0,7),(outer_w-7,outer_w)):
    sleeve=Part.makeCylinder(4.0,yb-ya,V(hinge_x,ya,hinge_z),V(0,1,0))
    leaf=leaf.fuse(sleeve)
leaf=leaf.cut(Part.makeCylinder(1.35,outer_w+2,V(hinge_x,-1,hinge_z),V(0,1,0)))
leaf=leaf.removeSplitter()
# Horn: attached to rudder coupon. Rod connection bore is perpendicular to leaf.
horn=Part.makeBox(3,8,15,V(hinge_x+17,hinge_y-4,hinge_z+1.5))
horn=horn.cut(Part.makeCylinder(1.1,5,V(hinge_x+16,hinge_y,hinge_z+12),V(1,0,0)))
leaf=leaf.fuse(horn).removeSplitter()
# Servo shaft and lever: illustrative geometry, not manufacturer-certified.
shaft_center=V(outer_l/2,outer_w/2,base+12)
servo=Part.makeBox(servo_length,servo_width,servo_height,
                   V(wall+clearance,wall+clearance,base))
lever=Part.makeCylinder(2.5,3,shaft_center).fuse(
      Part.makeBox(17,4,3,V(shaft_center.x,shaft_center.y-2,shaft_center.z)))
# Geometry exports are physically meaningful solids, not final assembly.
shapes={"servo_tray":tray,"rudder_hinge_horn":leaf,"servo_envelope":servo,
        "servo_lever_envelope":lever}
for name,shape in shapes.items():
    ob=doc.addObject("PartDesign::Feature",name)
    ob.Shape=shape
doc.recompute()
doc.saveAs(os.path.join(OUT,"v388_servo_linkage_coupon.FCStd"))
for name in ("servo_tray","rudder_hinge_horn"):
    mesh=MeshPart.meshFromShape(Shape=shapes[name],LinearDeflection=0.12,
                               AngularDeflection=0.25,Relative=False)
    mesh.write(os.path.join(OUT,"v388_"+name+".stl"))
qa={"version":"v388","status":"STANDALONE_COUPON_UNVALIDATED",
    "assumptions":{"servo_length_mm":servo_length,"servo_width_mm":servo_width,
                   "servo_height_mm":servo_height,"clearance_mm":clearance},
    "geometry":{name:{"valid":shape.isValid(),"solids":len(shape.Solids),
                       "volume_mm3":shape.Volume} for name,shape in shapes.items()},
    "known_intersections_mm3":{
       "tray_servo":tray.common(servo).Volume,
       "tray_rudder":tray.common(leaf).Volume,
       "rudder_servo":leaf.common(servo).Volume},
    "unverified":["servo flange and horn manufacturer geometry",
       "moving hinge partner and metal pin fit","rod and clevis integration",
       "swept 3D collision over deflection","loads and print tolerances",
       "integration into master control surfaces","physical print and actuation"]}
with open(os.path.join(OUT,"v388_servo_linkage_qa.json"),"w",encoding="utf-8") as f:
    json.dump(qa,f,indent=2)
print(json.dumps(qa,indent=2))
