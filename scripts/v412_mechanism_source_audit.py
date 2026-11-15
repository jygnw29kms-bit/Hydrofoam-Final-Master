"""v412: fail-closed audit of v411 FreeCAD mechanism generator.
Run: python scripts/v412_mechanism_source_audit.py
This is source-level QA, not a mechanical or flight certification.
"""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "v411_control_mechanism_assembly_freecad.py"
OUT = ROOT / "cad" / "v412_source_audit.json"

def audit(text):
    ast.parse(text)
    checks = {
        "local_geometry_translated_before_sweep":
            "shape.translate(origin)" in text and
            "leaf=orient(moving,V(0,0,0),V(1,0,0),deg)" in text,
        "servo_angle_solver_missing":
            "real servo-angle solver is still required" in text,
        "fixed_leaf_sleeve_occupancy_unchecked":
            "fixed=fixed.fuse(sleeve.cut(bore))" in text and
            "moving=moving.fuse(sleeve.cut(bore))" in text,
        "linkage_not_constructed_as_solid":
            'parts={"fixed":fixed,"moving":moving,"pin":pin,"servo_tray":tray}' in text,
        "airframe_integration_missing":
            "verified_in_airframe\":False" in text,
    }
    return {
        "classification": "SOURCE_AUDIT_ONLY",
        "source": str(SOURCE.relative_to(ROOT)),
        "findings": [
            {"id": k, "present": v, "severity": "BLOCKER",
             "description": {
                 "local_geometry_translated_before_sweep": "The source translates the same shape objects to world coordinates for export, then rotates them around the local origin; sweep interference and linkage geometry therefore mix coordinate frames.",
                 "servo_angle_solver_missing": "The servo output remains fixed at neutral during the rudder sweep, so fixed-length rod closure and achievable servo angles are not established.",
                 "fixed_leaf_sleeve_occupancy_unchecked": "Both leaves have full-width base plates adjacent to sleeves; adjacent-body overlap must be checked at zero and full travel, not assumed absent.",
                 "linkage_not_constructed_as_solid": "No printable rod, clevis or articulated linkage solid is included in the exported parts list.",
                 "airframe_integration_missing": "The generator itself explicitly marks airframe integration unverified."
             }[k]} for k, v in checks.items()
        ],
        "pass": False,
        "reason": "No release until the geometry frame, rod closure, hinge clearances, physical parts and integration are tested in actual FreeCAD assemblies."
    }

def main():
    report = audit(SOURCE.read_text(encoding="utf-8"))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"pass": report["pass"], "blockers_detected": sum(f["present"] for f in report["findings"])}))
    if not all(f["present"] for f in report["findings"]):
        raise SystemExit("Source changed; review audit rules and findings before relying on them.")

if __name__ == "__main__":
    main()
