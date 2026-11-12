#!/usr/bin/env python3
"""v353: fail-closed evidence manifest gate for Hydrofoam's three-mode master.

Usage: python scripts/audit_v353_release_evidence.py <evidence.json> [output.json]
The manifest is intentionally external: missing files, missing hash checks and
self-declared passes without actual evidence never produce final acceptance.
This is an audit of evidence completeness, not a substitute for engineering tests.
"""
import hashlib
import json
import sys
from pathlib import Path

MASTER_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
CATEGORIES = {
    "visual": ["top_overlay", "side_overlay", "perspective_overlay", "comparison_metrics"],
    "mechanics": ["elevator_sweep", "aileron_left_sweep", "aileron_right_sweep",
                  "rudder_sweep", "servo_mounts", "horns_and_linkages",
                  "hinge_clearances", "printable_mesh_audit"],
    "land": ["hard_start", "short_grass_start", "firm_sand_start",
             "ground_steering", "foil_ground_clearance", "skid_wear"],
    "water": ["sealed_electronics", "static_buoyancy", "planing",
              "foil_lift", "hydrodynamic_stability"],
    "air": ["weighed_mass", "cg_and_stability", "measured_thrust",
            "control_authority", "safe_flight_test"],
}
def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def audit(manifest, root):
    result={"version":"v353","accepted":False,"master_verified":False,
            "categories":{},"errors":[]}
    master=root/"reference"/"FINAL_MASTER_ORIGINAL.jpeg"
    if not master.is_file():
        result["errors"].append("Master reference missing")
    elif digest(master)!=MASTER_SHA:
        result["errors"].append("Master SHA256 mismatch")
    else:
        result["master_verified"]=True
    evidence=manifest.get("evidence",{})
    if not isinstance(evidence,dict):
        evidence={}
    for category,keys in CATEGORIES.items():
        checks={}
        for key in keys:
            entry=evidence.get(category,{}).get(key) if isinstance(evidence.get(category),dict) else None
            status={"verified":False,"reason":"missing evidence entry"}
            if isinstance(entry,dict):
                relative=entry.get("file")
                expected=entry.get("sha256")
                signed=entry.get("reviewed_by")
                passed=entry.get("test_passed") is True
                if not isinstance(relative,str) or not relative:
                    status["reason"]="missing file path"
                elif Path(relative).is_absolute() or ".." in Path(relative).parts:
                    status["reason"]="unsafe path"
                elif not isinstance(expected,str) or len(expected)!=64:
                    status["reason"]="missing SHA256"
                elif not isinstance(signed,str) or not signed.strip():
                    status["reason"]="missing reviewer"
                elif not passed:
                    status["reason"]="test not passed"
                else:
                    target=(root/relative).resolve()
                    if not target.is_relative_to(root.resolve()) or not target.is_file():
                        status["reason"]="evidence file missing or outside repository"
                    elif digest(target)!=expected.lower():
                        status["reason"]="evidence SHA256 mismatch"
                    else:
                        status={"verified":True,"reason":"evidence file verified; reviewer assertion recorded"}
            checks[key]=status
        result["categories"][category]={"complete":all(v["verified"] for v in checks.values()),"checks":checks}
    result["evidence_complete"]=result["master_verified"] and all(v["complete"] for v in result["categories"].values())
    result["accepted"]=False
    result["limitations"]=["Evidence completeness does not prove engineering safety.",
                           "Final release requires independent engineering and field-test signoff.",
                           "A reviewed_by string is an assertion, not authenticated identity."]
    return result

if __name__=="__main__":
    if len(sys.argv) not in (2,3):
        raise SystemExit("usage: python scripts/audit_v353_release_evidence.py manifest.json [report.json]")
    src=Path(sys.argv[1]).resolve()
    repo=Path(__file__).resolve().parent.parent
    result=audit(json.loads(src.read_text(encoding="utf-8")),repo)
    report=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if len(sys.argv)==3:
        Path(sys.argv[2]).write_text(report,encoding="utf-8")
    else:
        print(report)
    sys.exit(0 if result["evidence_complete"] else 2)
