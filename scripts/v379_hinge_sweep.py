# Hydrofoam v379: non-destructive hinge articulation sweep for v378 test bench.
# Run in FreeCAD Python: FreeCADCmd scripts/v379_hinge_sweep.py
# This test does NOT certify the aircraft or its control linkages.
import os, json, math
import FreeCAD as App
from FreeCAD import Vector
BASE=os.environ.get("HYDROFOAM_V378_OUT",os.path.join(os.getcwd(),"build","v378"))
OUT=os.environ.get("HYDROFOAM_V379_OUT",os.path.join(os.getcwd(),"build","v379"))
os.makedirs(OUT,exist_ok=True)
source=os.path.join(BASE,"Hydrofoam_v378_Linkage_Test.FCStd")
if not os.path.isfile(source):
    raise RuntimeError("Missing v378 FCStd: execute v378 first, no fabricated QA")
doc=App.openDocument(source)
fixed=doc.getObject("FixedLeaf")
moving=doc.getObject("MovingLeaf")
pin=doc.getObject("RemovablePin")
if any(x is None or x.Shape.isNull() for x in (fixed,moving,pin)):
    raise RuntimeError("Missing or null hinge components")
axis_point=Vector(0,0,3.8)
axis=Vector(1,0,0)
base=moving.Shape.copy()
results=[]
for degrees in range(-35,36,5):
    rotated=base.copy()
    rotated.rotate(axis_point,axis,degrees)
    overlap=rotated.common(fixed.Shape)
    # Pin is intentionally in bore: any pin overlap is separately measured.
    pin_overlap=rotated.common(pin.Shape)
    results.append({"angle_deg":degrees,
                    "fixed_intersection_mm3":round(overlap.Volume,6),
                    "pin_intersection_mm3":round(pin_overlap.Volume,6),
                    "moving_valid":rotated.isValid()})
doc.close()
# No arbitrary tolerance silently promoted to pass.
report={"version":"v379","source":source,"kind":"static_CAD_boolean_sweep",
        "angles":results,
        "collision_free_with_fixed":all(r["fixed_intersection_mm3"]<1e-6 for r in results),
        "collision_free_with_pin":all(r["pin_intersection_mm3"]<1e-6 for r in results),
        "limits":{"master_integration":"NOT_TESTED","servo_actuation":"NOT_TESTED",
                  "linkage_kinematics":"NOT_TESTED","manufacturing_fit":"NOT_TESTED",
                  "load_and_fatigue":"NOT_TESTED","physical_validation":"NOT_TESTED"},
        "release":"NOT_APPROVED"}
with open(os.path.join(OUT,"hinge_sweep_qa.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
