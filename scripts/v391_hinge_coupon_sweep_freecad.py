"""v391: FreeCAD hinge-coupon sweep with tolerance-aware interference checks.
Engineering specimen only. NOT integrated into Hydrofoam control surfaces.
Run using FreeCAD's Python environment; no claim of flightworthiness.
"""
import json, math, os
import FreeCAD as App
import Part, MeshPart
V=App.Vector
out=os.environ.get("HYDROFOAM_V391_OUT",os.path.join(os.getcwd(),"build","v391"))
os.makedirs(out,exist_ok=True)
doc=App.newDocument("Hydrofoam_v391_hinge_coupon")
axis=V(0,1,0)
pin_r,bore_r,barrel_r=1.2,1.55,3.6
# Alternating knuckles: 0.5 mm gaps at both interfaces.
fixed_spans=((0,9.5),(20.5,30))
moving_spans=((10,20),)
def tube(lo,hi):
    return Part.makeCylinder(barrel_r,hi-lo,V(0,lo,0),axis).cut(
        Part.makeCylinder(bore_r,hi-lo+0.2,V(0,lo-0.1,0),axis))
def leaf(x0,spans,root_x):
    s=Part.makeBox(23,30,2.4,V(x0,0,-1.2))
    for lo,hi in spans:
        s=s.fuse(tube(lo,hi))
        s=s.fuse(Part.makeBox(4.6,hi-lo,2.4,V(root_x,lo,-1.2)))
    return s.cut(Part.makeCylinder(bore_r,32,V(0,-1,0),axis)).removeSplitter()
fixed=leaf(-28,fixed_spans,-5)
moving=leaf(5,moving_spans,0.4)
# Ruderhorn integral to moving coupon, with through-hole for a clevis pin.
horn=Part.makeBox(3.5,7,13,V(22,11.5,1.2))
horn=horn.cut(Part.makeCylinder(1.1,9,V(23.75,10.5,10),axis))
moving=moving.fuse(horn).removeSplitter()
pin=Part.makeCylinder(pin_r,32,V(0,-1,0),axis)
parts={"fixed":fixed,"moving_horn":moving,"pin":pin}
for name,shape in parts.items():
    ob=doc.addObject("PartDesign::Feature",name)
    ob.Shape=shape
doc.recompute()
doc.saveAs(os.path.join(out,"v391_hinge_coupon.FCStd"))
for name in ("fixed","moving_horn"):
    MeshPart.meshFromShape(Shape=parts[name],LinearDeflection=0.1,
        AngularDeflection=0.2,Relative=False).write(os.path.join(out,name+".stl"))
angles=[]
for angle in range(-35,36,1):
    rotated=moving.copy()
    rotated.rotate(V(0,0,0),axis,angle)
    angles.append({"angle_deg":angle,
        "fixed_intersection_mm3":round(rotated.common(fixed).Volume,6),
        "pin_intersection_mm3":round(rotated.common(pin).Volume,6)})
valid={name:bool(shape.isValid() and len(shape.Solids)==1) for name,shape in parts.items()}
sweep_pass=all(a["fixed_intersection_mm3"]<0.001 and
               a["pin_intersection_mm3"]<0.001 for a in angles)
report={"version":"v391","scope":"standalone_hinge_coupon",
 "valid_solids":valid,"sweep_pass":sweep_pass,
 "axial_knuckle_gap_mm":0.5,"diametral_pin_clearance_mm":2*(bore_r-pin_r),
 "sweep":angles,
 "limitations":["No print or dimensional metrology performed",
 "No servo mount or linkage integrated into actual airframe",
 "No structural load test or full assembly collision clearance",
 "No photogrammetric match to immutable Final Master",
 "No land, water or flight acceptance evidence"]}
with open(os.path.join(out,"v391_qa.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)
print(json.dumps({"valid_solids":valid,"sweep_pass":sweep_pass,
 "samples":len(angles)},indent=2))
if not all(valid.values()) or not sweep_pass:
    raise SystemExit("V391_COUPON_QA_FAILED")
