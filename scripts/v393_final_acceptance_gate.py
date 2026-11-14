"""v393: Fail-closed acceptance gate for the complete Hydrofoam assembly.

This does not generate evidence. It validates an independently populated evidence
manifest and SHA256 hashes of its referenced files. A standalone hinge coupon
cannot satisfy the assembled-control-surface requirement.

Usage: python scripts/v393_final_acceptance_gate.py --root . --manifest qa/final_acceptance_manifest.json
"""
import argparse
import hashlib
import json
from pathlib import Path

MASTER_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
VIEWS = ("top", "side", "perspective")
SURFACES = ("left_aileron", "right_aileron", "elevator", "rudder")
LAND = ("hard_ground", "short_grass", "load_bearing_sand")
WATER = ("planing", "foil_lift", "waterproofing", "hydrodynamics")
AIR = ("takeoff", "stable_flight", "controlled_landing", "aerodynamic_stability")
CROSS = ("mass_cg", "thrust", "ground_steering", "foil_ground_clearance",
         "skid_wear", "control_authority")

def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def validate(root, manifest):
    failures = []
    master = root / "reference/FINAL_MASTER_ORIGINAL.jpeg"
    if not master.is_file() or sha256(master) != MASTER_SHA:
        failures.append("Original Final-Master missing or SHA256 mismatch")
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return {"accepted": False, "failures": [f"Manifest unreadable: {exc}"]}
    def evidence(obj, name):
        if not isinstance(obj, dict) or obj.get("result") != "pass":
            failures.append(f"{name}: missing explicit pass")
            return
        path = obj.get("path")
        digest = obj.get("sha256")
        if not isinstance(path, str) or not isinstance(digest, str):
            failures.append(f"{name}: missing evidence path/hash")
            return
        target = (root / path).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            failures.append(f"{name}: unsafe or missing evidence file")
        elif sha256(target) != digest.lower():
            failures.append(f"{name}: evidence SHA256 mismatch")
    for view in VIEWS:
        evidence(data.get("photogrammetry", {}).get(view), f"photogrammetry.{view}")
    for surface in SURFACES:
        block = data.get("controls", {}).get(surface, {})
        for part in ("hinge", "servo_mount", "horn", "linkage", "sweep_collision",
                     "printability", "assembly_clearance"):
            evidence(block.get(part), f"controls.{surface}.{part}")
    for category, items in (("land", LAND), ("water", WATER), ("air", AIR),
                            ("cross_domain", CROSS)):
        for item in items:
            evidence(data.get("trials", {}).get(category, {}).get(item),
                     f"trials.{category}.{item}")
    return {"accepted": not failures, "failures": failures,
            "notice": "Manifest evidence gate only; verify provenance and physical tests independently."}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--root", type=Path, default=Path("."))
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    root = args.root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    result = validate(root, manifest)
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.write_text(output + "\n", encoding="utf-8")
    print(output)
    raise SystemExit(0 if result["accepted"] else 1)

if __name__ == "__main__":
    main()
