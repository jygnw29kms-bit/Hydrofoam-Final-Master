"""v399: independent FreeCAD geometry audit of v398 pivot coupon.
Run with FreeCAD Python (not ordinary CPython). Never grants vehicle approval.
"""
import os, json, hashlib, math
import FreeCAD as App
import Part
from FreeCAD import Vector

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC=os.path.join(ROOT,"qa_runs","v398_foil_pivot","v398_foil_pivot.FCStd")
OUT=os.path.join(ROOT,"qa_runs","v399_pivot_audit")
os.makedirs(OUT,exist_ok=True)
report={"status":"FAIL_NOT_EVALUATED","source":os.path.relpath(SRC,ROOT),
        "scope":"isolated pivot coupon only; not integrated into master",
        "checks":{},"sweep":[],"limitations":[
          "No master-float installation or external appearance verification",
          "No hinge locking pin, retaining clip, actuator, or water sealing",
          "No foil lift or Land/Water/Air functional validation",
          "No measured print tolerance, servo geometry or load testing"]}
try:
    if not os.path.isfile(SRC):
        raise FileNotFoundError(SRC)
    report["source_sha256"]=hashlib.sha256(open(SRC,"rb").read()).hexdigest()
    doc=App.openDocument(SRC)
    names=("CheekLeft","CheekRight","FoilMast","PivotPin")
    parts={n:doc.getObject(n).Shape for n in names}
    for n,s in parts.items():
        report["checks"][n+"_solid"]={"pass":bool(s.isValid() and len(s.Solids)==1 and s.Volume>0),
           "volume_mm3":round(s.Volume,3)}
    moving=parts["FoilMast"]
    cheeks=[parts["CheekLeft"],parts["CheekRight"]]
    pin=parts["PivotPin"]
    pivot=Vector(0,0,40)
    axis=Vector(0,1,0)
    # Pin-to-bore contact is intentional. Check only actual penetration of moving
    # body into fixed cheeks, and distinguish moving-pin bearing contact.
    for deg in range(0,91):
        s=moving.copy()
        s.rotate(pivot,axis,deg)
        overlap=sum(s.common(c).Volume for c in cheeks)
        report["sweep"].append({"angle_deg":deg,
            "cheek_overlap_mm3":round(overlap,6),
            "lowest_z_mm":round(s.BoundBox.ZMin,4)})
    max_overlap=max(p["cheek_overlap_mm3"] for p in report["sweep"])
    report["checks"]["cheek_sweep_0_to_90"]={"pass":max_overlap<0.001,
        "max_overlap_mm3":max_overlap}
    report["checks"]["stowed_z_clearance_vs_coupon_datum"]={
        "pass":report["sweep"][-1]["lowest_z_mm"]>=12,
        "lowest_z_mm":report["sweep"][-1]["lowest_z_mm"],
        "datum_note":"coupon Z=0 is NOT a measured ground plane"}
    report["checks"]["fixed_cheeks_no_overlap"]={"pass":cheeks[0].common(cheeks[1]).Volume<0.001}
    # Critical geometry: this test only verifies a printable prototype, never
    # substitutes for real foil clearance relative to the actual skids.
    report["status"]="COUPON_PASS_ONLY" if all(v["pass"] for v in report["checks"].values()) else "COUPON_FAIL"
    App.closeDocument(doc.Name)
except Exception as exc:
    report["status"]="FAIL_EXCEPTION"
    report["error"]=str(exc)
finally:
    dest=os.path.join(OUT,"v399_audit.json")
    with open(dest,"w",encoding="utf-8") as f:
        json.dump(report,f,indent=2)
    print(json.dumps({"status":report["status"],"report":dest,"checks":report["checks"]}))
    if report["status"]!="COUPON_PASS_ONLY":
        raise SystemExit(1)
