"""Hydrofoam: fail-closed acceptance manifest for the TWO mandatory CAD gates.

Run: python scripts/v369_final_master_evidence_gate.py evidence.json report.json
This checks provenance/completeness, NOT geometric correctness. All evidence paths
must exist beneath the project root; no automatic final status is ever granted.
"""
import hashlib
import json
import sys
from pathlib import Path

MASTER_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
VIEWS = ("top", "side", "perspective")
PARTS = ("left_aileron", "right_aileron", "elevator", "rudder")
REQUIRED_HARDWARE = ("hinge", "servo_mount", "control_horn", "linkage")

def within(root, rel):
    if not isinstance(rel, str) or not rel.strip():
        raise ValueError("Missing evidence path")
    path = (root / rel).resolve()
    if not path.is_relative_to(root):
        raise ValueError("Evidence path escapes project root")
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("Evidence file absent or empty: " + rel)
    return path

def run(manifest_path, report_path):
    manifest_path = Path(manifest_path).resolve()
    root = manifest_path.parent
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    master = root / "reference/FINAL_MASTER_ORIGINAL.jpeg"
    if not master.is_file() or hashlib.sha256(master.read_bytes()).hexdigest() != MASTER_SHA:
        errors.append("Original master missing or SHA256 mismatch")
    comparisons = data.get("comparisons", {})
    for view in VIEWS:
        entry = comparisons.get(view, {})
        for key in ("original_crop", "cad_render", "registered_overlay", "comparison_report"):
            try:
                within(root, entry.get(key))
            except ValueError as exc:
                errors.append(f"{view}.{key}: {exc}")
        if entry.get("reviewed_against_original") is not True:
            errors.append(f"{view}: visual correspondence not signed off")
    controls = data.get("controls", {})
    for part in PARTS:
        entry = controls.get(part, {})
        for hardware in REQUIRED_HARDWARE:
            try:
                within(root, entry.get(hardware))
            except ValueError as exc:
                errors.append(f"{part}.{hardware}: {exc}")
        for key in ("cad_assembly", "collision_sweep_report", "print_fit_report", "servo_load_report"):
            try:
                within(root, entry.get(key))
            except ValueError as exc:
                errors.append(f"{part}.{key}: {exc}")
        if entry.get("sweep_collision_free") is not True:
            errors.append(f"{part}: collision-free travel not verified")
        if entry.get("printed_fit_verified") is not True:
            errors.append(f"{part}: printed mechanical fit not verified")
    report = {
        "gate": "v369_evidence_completeness",
        "master_sha256_expected": MASTER_SHA,
        "status": "EVIDENCE_COMPLETE_REQUIRES_INDEPENDENT_REVIEW" if not errors else "NOT_APPROVED",
        "errors": errors,
        "note": "Never infer photorealism, strength, or actual safe flight from file existence or booleans.",
    }
    Path(report_path).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if not errors else 1

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("usage: python v369_final_master_evidence_gate.py evidence.json report.json")
    try:
        sys.exit(run(sys.argv[1], sys.argv[2]))
    except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
        print(f"Evidence gate failed closed: {exc}", file=sys.stderr)
        sys.exit(2)
