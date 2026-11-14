"""v390 hinge coupon: separated leaf roots and genuine pin-axis clearance.
Standalone FreeCAD engineering sample, NOT installed in the Hydrofoam airframe.
Outputs FCStd, individual STL, and an angle-resolved collision report.
"""
import json, math, os
import FreeCAD as App
import Part, MeshPart
V=App.Vector
OUT=os.environ.get("HYDROFOAM_V390_OUT",os.path.join(os.getcwd(),"build","v390"))
os.makedirs(OUT,exist_ok=True)
doc=App.newDocument("Hydrofoam_v390_hinge")
axis=V(0,1,0)
pin_radius=1.2
bore_radius=1.5
barrel_radius=3.6
# Leaves begin beyond the barrel OD, avoiding the zero-angle root collision in v389.
# Both leaves are separate printable bodies, each with alternating knuckles.
fixed=Part.makeBox(24,30,2.4,V(-28,0,-1.2))
moving=Part.makeBox(24,30,2.4,V(4,0,-1.2))
def knuckle(y0,y1):
    return Part.makeCylinder(barrel_radius,y1-y0,V(0,y0,0),axis).cut(
        Part.makeCylinder(bore_radius,y1-y0+0.2,V(0,y0-0.1,0),axis))
# Radial web connects each leaf to its knuckles. Gaps along Y prevent overlap.
for a,b in [(0,9.5),(20.5,30)]:
    fixed=fixed.fuse(knuckle(a,b))
    fixed=fixed.fuse(Part.makeBox(4.5,b-a,2.4,V(-4.5,a,-1.2)))
moving=moving.fuse(knuckle(10,20))
moving=moving.fuse(Part.makeBox(4.5,10,2.4,V(0,10,-1.2)))
# Bore the entire connected body, including webs.
bore=Part.makeCylinder(bore_radius,32,V(0,-1,0),axis)
fixed=fixed.cut(bore).removeSplitter()
moving=moving.cut(bore).removeSplitter()
pin=Part.makeCylinder(pin_radius,32,V(0,-1,0),axis)
# Rudder horn protrudes from the moving surface; rod hole runs parallel to Y.
horn=Part.makeBox(3,7,13,V(19,11.5,1.2))
horn=horn.cut(Part.makeCylinder(1.1,9,V(20.5,10.5,10),axis))
moving=moving.fuse(horn).removeSplitter()
parts={"fixed":fixed,"moving_horn":moving,"pin":pin}
for name,shape in parts.items():
    obj=doc.addObject("PartDesign::Feature",name);obj.Shape=shape
doc.recompute()
doc.saveAs(os.path.join(OUT,"v390_hinge.FCStd"))
for name in ("fixed","moving_horn"):
    MeshPart.meshFromShape(Shape=parts[name],LinearDeflection=0.1,
        AngularDeflection=0.2,Relative=False).write(os.path.join(OUT,name+".stl"))
angles=[]
for deg in range(-35,36,5):
    rotated=moving.copy();rotated.rotate(V(0,0,0),axis,deg)
    angles.append({"deg":deg,"fixed_overlap_mm3":round(rotated.common(fixed).Volume,5),
                   "pin_overlap_mm3":round(rotated.common(pin).Volume,5)})
valid=all(p.isValid() and len(p.Solids)==1 for p in parts.values())
clear=all(a["fixed_overlap_mm3"]<0.01 and a["pin_overlap_mm3"]<0.01 for a in angles)
report={"version":"v390","status":"COUPON_ONLY_NOT_INTEGRATED",
        "geometry_valid":valid,"sweep_clear":clear,"angles":angles,
        "pin_diametral_clearance_mm":2*(bore_radius-pin_radius),
        "not_verified":["FreeCAD execution until run","servo mounting in airframe",
        "pushrod kinematics","load capacity","print tolerances",
        "photographic fidelity","land/water/air operation"]}
with open(os.path.join(OUT,"v390_qa.json"),"w",encoding="utf8") as f:
    json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
if not(valid and clear):
    raise SystemExit("HINGE_COUPON_QA_FAILED")
