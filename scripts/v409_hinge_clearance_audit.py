"""v409: FreeCAD hinge swept-clearance and topology QA (WIP coupon).
Run with FreeCAD Python. No aircraft certification or measured fit implied.
Unlike v408, pin/bore overlap is recorded separately from leaf/leaf interference.
"""
import importlib.util
import json
from pathlib import Path

ANGLES = range(-45, 46, 1)
MIN_CLEARANCE_MM = 0.20
MAX_LEAF_INTERSECTION_MM3 = 0.01

def run():
    import FreeCAD as App
    from FreeCAD import Vector
    root = Path(__file__).resolve().parents[1]
    path = root / "scripts" / "v407_hinge_interface_coupon.py"
    spec = importlib.util.spec_from_file_location("v407_hinge", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.build()
    doc = App.ActiveDocument
    fixed = doc.getObject("FixedLeaf").Shape
    moving = doc.getObject("MovingLeaf").Shape
    pin = doc.getObject("PinReferenceOnly").Shape
    axis = Vector(1, 0, 0)
    center = Vector(0, 0, mod.KNUCKLE_OUTER_D / 2)
    rows = []
    for angle in ANGLES:
        rotated = moving.copy()
        rotated.rotate(center, axis, angle)
        overlap = fixed.common(rotated).Volume
        # A shared hinge axis permits intentional pin/bore contact; measure it,
        # but never mistake it for leaf-to-leaf interference.
        pin_overlap = pin.common(rotated).Volume
        clearance = fixed.distToShape(rotated)[0]
        rows.append({
            "angle_deg": angle,
            "leaf_overlap_mm3": round(overlap, 6),
            "leaf_distance_mm": round(clearance, 6),
            "pin_overlap_mm3_diagnostic": round(pin_overlap, 6),
            "leaf_collision": overlap > MAX_LEAF_INTERSECTION_MM3,
            "clearance_below_target": clearance < MIN_CLEARANCE_MM,
        })
    valid = all(s.isValid() and not s.isNull() and len(s.Solids) == 1
                for s in (fixed, moving, pin))
    # Distance between whole leaves is zero at any contact, so a positive
    # target is conservative. It may reject workable joints; never waive it
    # without inspecting local faces and physical printer tolerance.
    passed = valid and all(not r["leaf_collision"] and
                           not r["clearance_below_target"] for r in rows)
    report = {
        "version": "v409", "scope": "hinge coupon only",
        "status": "PASS_COUPON_ONLY" if passed else "FAIL_OR_REVIEW",
        "geometry_valid": valid, "min_target_clearance_mm": MIN_CLEARANCE_MM,
        "max_overlap_mm3": MAX_LEAF_INTERSECTION_MM3,
        "rows": rows, "passed": passed,
        "limitations": [
            "No control surface integration or servo/linkage load testing",
            "Whole-solid distance can be conservative near hinge knuckles",
            "CAD clearance is not printed dimensional accuracy",
            "No land, water or flight validation",
        ],
    }
    out = root / "qa_runs" / "v409_hinge_clearance"
    out.mkdir(parents=True, exist_ok=True)
    (out / "report.json").write_text(json.dumps(report, indent=2),
                                     encoding="utf-8")
    if not passed:
        raise RuntimeError("v409 clearance or topology failed; inspect report.json")
    return report

if __name__ == "__main__":
    run()
