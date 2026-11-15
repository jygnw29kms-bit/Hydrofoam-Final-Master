"""v416: fail-closed acceptance evidence inventory for Hydrofoam.

Only verifies existence, nonempty files and SHA-256 checksums of declared
evidence. It NEVER asserts engineering acceptance from file presence alone.
Human-reviewed measurements and real CAD/field testing remain mandatory.
"""
import argparse
import hashlib
import json
from pathlib import Path

MASTER_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
REQUIRED = {
    "master_top_overlay", "master_side_overlay", "master_perspective_overlay",
    "blender_native_model", "freecad_integrated_assembly",
    "left_aileron_sweep", "right_aileron_sweep",
    "elevator_left_sweep", "elevator_right_sweep", "rudder_sweep",
    "servo_mounts_horns_linkages", "printability_and_mesh",
    "land_hard_ground", "land_short_grass", "land_firm_sand",
    "ground_steering", "foil_ground_clearance", "skid_wear",
    "water_flotation", "water_seal", "water_planing",
    "water_foil_lift", "hydrodynamic_stability",
    "air_mass_cg", "air_thrust", "air_aero_stability",
    "air_control_authority", "air_flight_test"
}

def check(root, manifest):
    root = root.resolve()
    issues = []
    master = root / "reference/FINAL_MASTER_ORIGINAL.jpeg"
    if not master.is_file() or hashlib.sha256(master.read_bytes()).hexdigest() != MASTER_SHA:
        issues.append("Immutable master missing or SHA-256 mismatch")
    entries = manifest.get("evidence", {})
    if not isinstance(entries, dict):
        raise ValueError("evidence must be a mapping")
    for name in sorted(REQUIRED):
        entry = entries.get(name)
        if not isinstance(entry, dict):
            issues.append(name + ": missing evidence record")
            continue
        rel = entry.get("path")
        sha = entry.get("sha256")
        if not isinstance(rel, str) or not rel or not isinstance(sha, str) or len(sha) != 64:
            issues.append(name + ": invalid path/hash")
            continue
        candidate = (root / rel).resolve()
        if not candidate.is_relative_to(root) or not candidate.is_file():
            issues.append(name + ": missing or outside project")
            continue
        if candidate.stat().st_size == 0 or hashlib.sha256(candidate.read_bytes()).hexdigest() != sha.lower():
            issues.append(name + ": empty or checksum mismatch")
        if entry.get("reviewed") is not True or not entry.get("reviewer") or not entry.get("measurement"):
            issues.append(name + ": independent review/measurement missing")
    return {
        "classification": "EVIDENCE_INVENTORY_ONLY",
        "inventory_complete": not issues,
        "engineering_acceptance": False,
        "final_release_authorized": False,
        "issues": issues,
        "warning": "Matching files and signed review records are not proof of safe operation."
    }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("project_root", type=Path)
    p.add_argument("manifest", type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    result = check(a.project_root, json.loads(a.manifest.read_text(encoding="utf-8")))
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    raise SystemExit(0 if result["inventory_complete"] else 2)

if __name__ == "__main__":
    main()
