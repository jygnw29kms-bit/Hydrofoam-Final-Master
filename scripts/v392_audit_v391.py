"""v392: Independent, read-only audit of the v391 FreeCAD hinge specimen.
Run: python scripts/v392_audit_v391.py --root . --qa qa_runs/v391_20261114/v391_qa.json
Does not certify assembled mechanisms or physical land/water/air performance.
"""
import argparse
import hashlib
import json
from pathlib import Path

MASTER_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def audit(root, qa_path):
    checks, artifacts = {}, {}
    original = root / "reference" / "FINAL_MASTER_ORIGINAL.jpeg"
    checks["master_sha256"] = original.is_file() and digest(original) == MASTER_SHA
    checks["qa_exists"] = qa_path.is_file()
    if not checks["qa_exists"]:
        return {"passed": False, "checks": checks, "artifacts": artifacts,
                "limitations": ["v391 report unavailable; no inference of success"]}
    report = json.loads(qa_path.read_text(encoding="utf-8"))
    sweep = report.get("sweep", [])
    expected = list(range(-35, 36))
    checks["scope"] = report.get("scope") == "standalone_hinge_coupon"
    checks["angles_complete"] = [x.get("angle_deg") for x in sweep] == expected
    checks["solids_valid"] = all(report.get("valid_solids", {}).get(k) is True
                                  for k in ("fixed", "moving_horn", "pin"))
    checks["collision_volumes"] = checks["angles_complete"] and all(
        isinstance(x.get(k), (int, float)) and 0 <= x[k] < 0.001
        for x in sweep for k in ("fixed_intersection_mm3", "pin_intersection_mm3"))
    checks["reported_sweep_pass"] = report.get("sweep_pass") is True
    checks["knuckle_gap"] = report.get("axial_knuckle_gap_mm") == 0.5
    checks["pin_clearance"] = abs(report.get("diametral_pin_clearance_mm", -1) - 0.7) < 1e-6
    for filename in ("v391_hinge_coupon.FCStd", "fixed.stl", "moving_horn.stl"):
        path = qa_path.parent / filename
        artifacts[filename] = {"exists": path.is_file(),
                               "size_bytes": path.stat().st_size if path.is_file() else 0,
                               "sha256": digest(path) if path.is_file() else None}
    checks["artifacts_present"] = all(x["exists"] and x["size_bytes"] > 0
                                      for x in artifacts.values())
    return {"passed": all(checks.values()), "checks": checks, "artifacts": artifacts,
            "limitations": ["Report consistency only; does not independently rerun FreeCAD BRep intersections",
                            "Not integrated with airframe, servos, horns or pushrods",
                            "No measured physical hinge motion, print tolerance, structural test or flight clearance",
                            "No visual master comparison or land/water/air test evidence"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--qa", type=Path, required=True)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    root = a.root.resolve()
    qa = a.qa if a.qa.is_absolute() else root / a.qa
    result = audit(root, qa)
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    raise SystemExit(0 if result["passed"] else 1)

if __name__ == "__main__":
    main()
