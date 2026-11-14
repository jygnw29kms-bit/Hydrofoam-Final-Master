"""v396: Independent geometric audit of the v395 servo-fit coupon.
Run inside FreeCAD Python. Never implies aircraft integration or flight approval.
"""
import os, json, math
import FreeCAD as App
import Part
from FreeCAD import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "qa_runs", "v395_servo_coupon", "v395_servo_fit_coupon.FCStd")
OUT = os.path.join(ROOT, "qa_runs", "v396_servo_coupon_audit")
os.makedirs(OUT, exist_ok=True)
report = {"version":396, "source":SRC, "status":"FAIL", "checks":{}, "limits":[
    "Coupon only; no installed servo, linkage, hinge or full-model fit",
    "No measured servo envelope or print tolerances",
    "No three-dimensional control-surface travel validation",
    "Land, water and air operating modes remain unverified"]}
if not os.path.isfile(SRC):
    report["checks"]["source_exists"] = False
else:
    doc = App.openDocument(SRC)
    try:
        parts = {o.Name:o.Shape for o in doc.Objects if hasattr(o,"Shape") and not o.Shape.isNull()}
        for name in ("ServoMount_Coupon","ControlHorn_Coupon"):
            shape=parts.get(name)
            report["checks"][name] = {
                "present":shape is not None,
                "valid":bool(shape and shape.isValid()),
                "one_solid":bool(shape and len(shape.Solids)==1),
                "positive_volume":bool(shape and shape.Volume>0),
                "bbox_mm":([shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength] if shape else None)}
        a=parts.get("ServoMount_Coupon")
        b=parts.get("ControlHorn_Coupon")
        if a and b:
            report["checks"]["parts_nonoverlap"] = a.common(b).Volume < 1e-7
        report["status"]="PASS_COUPON_ONLY" if all(
            v.get("present") and v.get("valid") and v.get("one_solid") and v.get("positive_volume")
            for k,v in report["checks"].items() if isinstance(v,dict)
        ) and report["checks"].get("parts_nonoverlap") is True else "FAIL"
    finally:
        App.closeDocument(doc.Name)
with open(os.path.join(OUT,"v396_audit.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
if report["status"]!="PASS_COUPON_ONLY":
    raise RuntimeError("v396 coupon audit failed")
