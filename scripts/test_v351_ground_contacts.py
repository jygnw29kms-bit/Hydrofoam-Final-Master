"""v351: independently test v347 ground contact geometry with adversarial cases.

Run: python scripts/test_v351_ground_contacts.py
No acceptance of real-world land operation is implied. This test prevents
regressions in the screening algorithm, including false stable contact claims.
"""
import importlib.util
import json
import math
from pathlib import Path

src = Path(__file__).with_name("engineering_v347_active_ground_contacts.py")
spec = importlib.util.spec_from_file_location("hydrofoam_v347", src)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def case(name, contacts, cg, tolerance, expected):
    data = {
        "surface": "hard",
        "contacts_mm": contacts,
        "cg_mm": cg,
        "pitch_deg": [0],
        "roll_deg": [0],
        "contact_height_tolerance_mm": tolerance,
        "minimum_margin_mm": 1,
    }
    result = module.run(data)
    observed = result["screen_pass"]
    return {"name": name, "expected": expected, "observed": observed,
            "pass": observed is expected,
            "active_contacts": result["samples"][0]["active_contact_count"],
            "margin_mm": result["samples"][0]["cg_margin_mm"]}

cases = [
    case("four coplanar corners, centered CG",
         [[-50,-50,0],[50,-50,0],[50,50,0],[-50,50,0]],
         [0,0,30], 0.01, True),
    case("two lowest corners must not support polygon",
         [[-50,-50,0],[50,-50,0],[50,50,8],[-50,50,8]],
         [0,0,30], 0.01, False),
    case("CG outside support polygon",
         [[-50,-50,0],[50,-50,0],[50,50,0],[-50,50,0]],
         [100,0,30], 0.01, False),
    case("collinear contacts",
         [[-50,0,0],[0,0,0],[50,0,0]],
         [0,0,30], 0.01, False),
    case("one low foil tip dominates contact",
         [[-50,-50,0],[50,-50,0],[50,50,0],[-50,50,0],[0,0,-10]],
         [0,0,30], 0.01, False),
]
report = {"version":"v351","test_count":len(cases),
          "all_pass":all(c["pass"] for c in cases),
          "cases":cases,
          "limitations":["Synthetic regression tests only; no measured contact locations.",
                         "No evidence of traction, water sealing, foil lift or flight."]}
print(json.dumps(report,indent=2))
if not report["all_pass"]:
    raise SystemExit(1)
