"""v401: independent, fail-closed acceptance evidence gate.

Run: python scripts/v401_acceptance_gate.py evidence.json
Evidence file must be authored from measured CAD and physical test results.
This script never substitutes an assumed dimension or simulated test for evidence.
"""
import json
import hashlib
import pathlib
import sys

REFERENCE_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
VIEWS = ("top", "side", "perspective")
SURFACES = ("left_aileron", "right_aileron", "left_elevator", "right_elevator", "rudder")
LAND = ("hard_ground", "short_grass", "load_bearing_sand")
WATER = ("static_float", "planing", "foil_lift", "waterproofing")
AIR = ("mass_cg", "static_thrust", "aero_stability", "control_authority", "flight")
FIELDS = ("artifact", "sha256", "method", "result", "reviewer")

def check_record(label, record, errors, root):
    if not isinstance(record, dict):
        errors.append(label + ": evidence record absent")
        return
    for field in FIELDS:
        if not record.get(field):
            errors.append(label + ": missing " + field)
    if record.get("result") != "PASS":
        errors.append(label + ": no PASS result")
    name = record.get("artifact")
    if not isinstance(name, str):
        return
    path = (root / name).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        errors.append(label + ": missing local evidence artifact")
        return
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != record.get("sha256"):
        errors.append(label + ": artifact checksum mismatch")

def audit(data, root):
    errors = []
    ref = root / "reference" / "FINAL_MASTER_ORIGINAL.jpeg"
    if not ref.is_file() or hashlib.sha256(ref.read_bytes()).hexdigest() != REFERENCE_SHA:
        errors.append("immutable Final-Master image missing or SHA256 mismatch")
    photo = data.get("photogrammetry", {})
    for view in VIEWS:
        check_record("photo/" + view, photo.get(view), errors, root)
    for surface in SURFACES:
        entry = data.get("controls", {}).get(surface, {})
        for part in ("hinges", "servo_mount", "horn", "linkage", "motion_clearance",
                     "measured_stroke", "print_fit"):
            check_record("controls/" + surface + "/" + part,
                         entry.get(part), errors, root)
    for terrain in LAND:
        for test in ("self_start", "steering", "foil_ground_clearance", "skid_wear"):
            check_record("land/" + terrain + "/" + test,
                         data.get("land", {}).get(terrain, {}).get(test), errors, root)
    for test in WATER:
        check_record("water/" + test, data.get("water", {}).get(test), errors, root)
    for test in AIR:
        check_record("air/" + test, data.get("air", {}).get(test), errors, root)
    for part in ("freecad_assembly", "blender_assembly", "stl_mesh_quality",
                 "p2s_printability", "mass_budget", "propeller_clearance"):
        check_record("integration/" + part, data.get("integration", {}).get(part), errors, root)
    return {"status": "PASS" if not errors else "BLOCKED",
            "errors": errors, "checks_required": 3 + 5*7 + 3*4 + 4 + 5 + 6,
            "note": "Record integrity gate only; PASS still requires independent engineering signoff."}

def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: v401_acceptance_gate.py REPO_ROOT EVIDENCE_JSON")
    root = pathlib.Path(sys.argv[1]).resolve()
    evidence = pathlib.Path(sys.argv[2]).resolve()
    data = json.loads(evidence.read_text(encoding="utf-8"))
    report = audit(data, root)
    out = evidence.with_suffix(".gate.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out),
                      "failed_checks": len(report["errors"])}))
    if report["status"] != "PASS":
        sys.exit(1)

if __name__ == "__main__":
    main()
