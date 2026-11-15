"""v408: Independent FreeCAD sweep of v407 hinge geometry, WIP verification.
Run using FreeCAD Python with v407 script available in sibling scripts directory.
This is a *coupon* audit, not aircraft-control-surface certification.
"""
import importlib.util
import json
import math
from pathlib import Path

TOL_MM3 = 0.01
ANGLES_DEG = list(range(-45, 46, 3))

def audit():
    import FreeCAD as App
    from FreeCAD import Vector
    root = Path(__file__).resolve().parents[1]
    source = root / "scripts" / "v407_hinge_interface_coupon.py"
    spec = importlib.util.spec_from_file_location("v407_coupon", str(source))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    # v407 build itself refuses to certify a failed static assembly.
    mod.build()
    doc = App.ActiveDocument
    fixed = doc.getObject("FixedLeaf").Shape
    moving = doc.getObject("MovingLeaf").Shape
    pin = doc.getObject("PinReferenceOnly").Shape
    center = Vector(0, 0, mod.KNUCKLE_OUTER_D / 2)
    axis = Vector(1, 0, 0)
    rows = []
    for angle in ANGLES_DEG:
        rotated = moving.copy()
        rotated.rotate(center, axis, angle)
        intersection = fixed.common(rotated).Volume
        pin_intersection = pin.common(rotated).Volume
        rows.append(dict(angle_deg=angle,
                         leaf_overlap_mm3=round(intersection, 6),
                         pin_overlap_mm3=round(pin_intersection, 6),
                         collision=intersection > TOL_MM3 or pin_intersection > TOL_MM3))
    out = root / "qa_runs" / "v408_hinge_sweep"
    out.mkdir(parents=True, exist_ok=True)
    qa = dict(version="v408", status="WIP_ONLY",
              angles_deg=ANGLES_DEG, rows=rows,
              passed=all(not r["collision"] for r in rows),
              limitations=["Coupon only; no aircraft integration",
                           "No linkage, servo load, print or fatigue tests",
                           "FreeCAD boolean tolerance may miss near-contact",
                           "Land/water/air tests not performed"])
    (out / "v408_sweep.json").write_text(json.dumps(qa, indent=2), encoding="utf-8")
    if not qa["passed"]:
        raise RuntimeError("Hinge sweep failed: collision found; inspect v408_sweep.json")
    return qa

if __name__ == "__main__":
    audit()
