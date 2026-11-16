"""Hydrofoam v420: fail-closed evidence gate for skid coupon integration.

This gate only checks traceable measurements and test records; it does not
certify ground performance, structural safety or image fidelity.
Usage: python scripts/v420_skid_evidence_gate.py evidence.json --output qa/v420.json
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

SURFACES = ("hard_ground", "short_grass", "firm_sand")
REQUIRED = ("left_skid", "right_skid")
MASTER_SHA256 = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"

def finite(v):
    return isinstance(v, (float, int)) and not isinstance(v, bool) and math.isfinite(v)

def audit(data, root):
    failures = []
    original = root / "reference" / "FINAL_MASTER_ORIGINAL.jpeg"
    if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != MASTER_SHA256:
        failures.append("original_reference_hash_not_verified")
    skids = data.get("skids", {})
    if not isinstance(skids, dict) or set(skids) != set(REQUIRED):
        failures.append("both_skids_required")
        skids = {}
    for side in REQUIRED:
        skid = skids.get(side, {})
        for field in ("mass_g", "wear_thickness_mm", "fastener_edge_margin_mm"):
            val = skid.get(field)
            if not finite(val) or val <= 0:
                failures.append(side + "_invalid_" + field)
        for field in ("cad_file", "stl_file", "measurement_record"):
            path = skid.get(field)
            if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts or not (root / path).is_file():
                failures.append(side + "_missing_" + field)
    tests = data.get("surface_tests", {})
    if not isinstance(tests, dict) or set(tests) != set(SURFACES):
        failures.append("all_three_land_surfaces_required")
        tests = {}
    for surface in SURFACES:
        test = tests.get(surface, {})
        for key in ("start_distance_m", "turn_radius_m", "wear_depth_mm", "minimum_foil_clearance_mm"):
            value = test.get(key)
            if not finite(value) or value < 0 or (key == "minimum_foil_clearance_mm" and value <= 0):
                failures.append(surface + "_invalid_" + key)
        for key in ("video", "measurement_record"):
            path = test.get(key)
            if not isinstance(path, str) or not path or Path(path).is_absolute() or ".." in Path(path).parts or not (root / path).is_file():
                failures.append(surface + "_missing_" + key)
    return {"classification": "WIP_EVIDENCE_INVENTORY", "evidence_complete": not failures,
            "failures": sorted(set(failures)), "final_release_authorized": False,
            "limitations": ["File existence does not prove measurement authenticity",
                            "No CAD collision, watertightness or structural load verification",
                            "Water and air modes require independent acceptance"]}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("evidence", type=Path)
    p.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    result = audit(json.loads(args.evidence.read_text(encoding="utf-8")), args.root.resolve())
    payload = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    raise SystemExit(0 if result["evidence_complete"] else 2)

if __name__ == "__main__":
    main()
