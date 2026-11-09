"""v312: fail-closed gate for real v310 mounting survey outputs.

Run on Jens-PC after executing survey_v310_mounting_rays.py.
This gate checks coverage and numerical plausibility, NOT strength or sealing.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "docs" / "V310_MOUNTING_RAY_SURVEY.json"
OUTPUT = ROOT / "docs" / "V312_MOUNTING_GATE_QA.json"

def validate(rows):
    issues = []
    expected = {(s, h, i) for s in ("left", "right")
                for h in ("front", "rear") for i in (1, 2)}
    found = [(r.get("side"), r.get("half"), r.get("hole")) for r in rows]
    if len(rows) != 8 or set(found) != expected or len(set(found)) != len(found):
        issues.append("Missing, duplicated or unexpected M3 hole locations")
    for r in rows:
        key = "/".join(map(str, (r.get("side"), r.get("half"), r.get("hole"))))
        probes = r.get("annulus_probes", [])
        if len(probes) != 4:
            issues.append(f"{key}: expected four annular probes")
        if r.get("valid_annulus_probe_count") != 4:
            issues.append(f"{key}: incomplete annular coverage")
        if not r.get("bore_axis_skid_crossings_expected_zero"):
            issues.append(f"{key}: bore axis unexpectedly intersects skid")
        if not r.get("ray_crossings_even"):
            issues.append(f"{key}: odd hull surface crossings")
        gaps = [p.get("gap_mm") for p in probes]
        if any(not isinstance(g, (int, float)) or not math.isfinite(g) for g in gaps):
            issues.append(f"{key}: missing or non-finite gap")
            continue
        if abs(min(gaps) - r.get("vertical_gap_mm", float("inf"))) > 1e-5:
            issues.append(f"{key}: reported gap differs from probe minimum")
        if min(gaps) < 0:
            issues.append(f"{key}: apparent geometric overlap")
        if max(gaps) - min(gaps) > 1.0:
            issues.append(f"{key}: >1 mm local variation, inspect mounting interface")
    return issues

def main():
    if not INPUT.exists():
        raise SystemExit("BLOCKED: real v310 survey JSON missing; run on Jens-PC first")
    rows = json.loads(INPUT.read_text(encoding="utf-8"))
    issues = validate(rows)
    report = {
        "stage": "v312 mounting interface data gate",
        "survey_file": str(INPUT.relative_to(ROOT)),
        "checked_holes": len(rows),
        "data_gate_pass": not issues,
        "mechanical_approval": False,
        "sealing_approval": False,
        "foil_ground_clearance_approval": False,
        "issues": issues,
    }
    OUTPUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if issues:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
