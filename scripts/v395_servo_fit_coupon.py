"""v395: FreeCAD servo-fit coupon. WIP; not integrated or flight approved.
Run in FreeCAD Python, not ordinary Python. Dimensions are test assumptions.
"""
import FreeCAD as App
import Part, Mesh
from FreeCAD import Vector
import os, json
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = os.path.join(root, "qa_runs", "v395_servo_coupon")
os.makedirs(out, exist_ok=True)
doc = App.newDocument("Hydrofoam_v395_ServoFit")
servo_w, servo_d, clearance, wall, floor, height = 23.0, 12.5, 0.45, 2.4, 3.0, 17.0
w, d = servo_w + 2*(clearance+wall), servo_d + 2*(clearance+wall)
mount = Part.makeBox(w,d,height).cut(Part.makeBox(servo_w+2*clearance,servo_d+2*clearance,height-floor+1,Vector(wall,wall,floor)))
for x in (2.5,w-8.5):
    tab=Part.makeBox(6,9,3,Vector(x,d,0))
    tab=tab.cut(Part.makeCylinder(1.15,3,Vector(x+3,d+4.5,0)))
    mount=mount.fuse(tab)
mount=mount.removeSplitter()
horn=Part.makeBox(22,7,3,Vector(w+8,0,0))
for x in (w+14,w+24):
    horn=horn.cut(Part.makeCylinder(0.9,3,Vector(x,3.5,0)))
horn=horn.removeSplitter()
checks={}
for name,shape in (("ServoMount_Coupon",mount),("ControlHorn_Coupon",horn)):
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Shape=shape
    checks[name]={"valid":shape.isValid(),"solids":len(shape.Solids),"volume_mm3":shape.Volume}
    Mesh.export([obj],os.path.join(out,name+".stl"))
doc.recompute()
doc.saveAs(os.path.join(out,"v395_servo_fit_coupon.FCStd"))
report={"status":"WIP_UNVERIFIED_FIT","units":"mm","candidate_servo_envelope":[servo_w,servo_d],"clearance":clearance,"checks":checks,"limits":["Real servo dimensions not measured","Not integrated in aircraft","No full-travel collision test","No flight approval"]}
with open(os.path.join(out,"v395_qa.json"),"w",encoding="utf8") as f: json.dump(report,f,indent=2)
if not all(c["valid"] and c["solids"]==1 for c in checks.values()): raise RuntimeError("Invalid coupon")
print(json.dumps(report))
