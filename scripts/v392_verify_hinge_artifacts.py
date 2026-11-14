"""v392: independent, read-only audit of v391 FreeCAD hinge coupon artifacts.

Run: python scripts/v392_verify_hinge_artifacts.py --run-dir qa_runs/v391_20261114
No FreeCAD dependency; does not certify integrated aircraft mechanics.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

EXPECTED_MASTER = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
ANGLES = list(range(-35, 36))
FILES = ("v391_hinge_coupon.FCStd", "fixed.stl", "moving_horn.stl", "v391_qa.json")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def verify(root, run_dir):
    issues = []
    reference = root / "reference" / "FINAL_MASTER_ORIGINAL.jpeg"
    actual_hash = sha256(reference) if reference.is_file() else None
    if actual_hash != EXPECTED_MASTER:
        issues.append("Immutable master image missing or SHA256 mismatch")
    artifacts = {}
    for filename in FILES:
        path = run_dir / filename
        if not path.is_file() or path.stat().st_size == 0:
            issues.append("Missing/empty artifact: " + filename)
        else:
            artifacts[filename] = {"bytes": path.stat().st_size, "sha256": sha256(path)}
    qa_path = run_dir / "v391_qa.json"
    qa = None
    if qa_path.is_file():
        try:
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            issues.append("Invalid QA JSON: " + str(exc))
    if qa is not None:
        if qa.get("version") != "v391" or qa.get("scope") != "standalone_hinge_coupon":
            issues.append("Incorrect version or scope")
        solids = qa.get("valid_solids")
        if not isinstance(solids, dict) or set(solids) != {"fixed", "moving_horn", "pin"} or not all(v is True for v in solids.values()):
            issues.append("Solid validity not demonstrated")
        samples = qa.get("sweep")
        if not isinstance(samples, list) or len(samples) != len(ANGLES):
            issues.append("Incomplete angular sweep")
        else:
            for angle, sample in zip(ANGLES, samples):
                if not isinstance(sample, dict) or sample.get("angle_deg") != angle:
                    issues.append("Angle sequence mismatch")
                    break
                for key in ("fixed_intersection_mm3", "pin_intersection_mm3"):
                    value = sample.get(key)
                    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0 or value >= 0.001:
                        issues.append("Collision threshold violated or missing: " + str(angle) + " " + key)
        if qa.get("sweep_pass") is not True:
            issues.append("Sweep flag is not true")
        if qa.get("axial_knuckle_gap_mm") != 0.5 or qa.get("diametral_pin_clearance_mm") is None:
            issues.append("Clearance data absent or inconsistent")
        if not qa.get("limitations"):
            issues.append("Limitations missing")
    return {
        "audit": "v392",
        "scope": "independent artifact consistency check, NOT mechanical or flight acceptance",
        "reference_sha256": actual_hash,
        "expected_reference_sha256": EXPECTED_MASTER,
        "artifacts": artifacts,
        "checked_angles_deg": ANGLES,
        "pass": not issues,
        "issues": issues,
        "unverified": ["Physical print and dimensional tolerances", "Full airframe integration",
                       "Servo linkage and load tests", "Master image visual correspondence",
                       "Land, water, and air operational acceptance"],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, help="Optional JSON output; never overwrites existing file")
    args = parser.parse_args()
    root = args.root.resolve()
    run_dir = args.run_dir if args.run_dir.is_absolute() else root / args.run_dir
    result = verify(root, run_dir)
    encoded = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    print(encoded, end="")
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
    raise SystemExit(0 if result["pass"] else 1)

if __name__ == "__main__":
    main()
