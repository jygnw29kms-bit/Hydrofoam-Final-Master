"""Hydrofoam v334: reproducible control-surface acceptance gate. No CAD mutation."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
actual = hashlib.sha256((ROOT / "reference/FINAL_MASTER_ORIGINAL.jpeg").read_bytes()).hexdigest()
fin = json.loads((ROOT / "docs/V330_MIRRORED_FIN_REBUILD_QA.json").read_text(encoding="utf-8"))
hinges = json.loads((ROOT / "docs/V331_HINGE_MOUNT_BRIDGES_QA.json").read_text(encoding="utf-8"))
elevons = json.loads((ROOT / "docs/V333_MASTER_ELEVON_ARTICULATION_QA.json").read_text(encoding="utf-8"))
sides = {x["side"]: x for x in fin["results"]}
checks = {
    "reference_sha256": actual == EXPECTED,
    "twin_fins_manifold": set(sides) == {"Left", "Right"} and all(x["fin_nonmanifold_edges"] == 0 for x in sides.values()),
    "rudder_clear_at_plus_minus_25": all(all(x["triangle_intersections"] == 0 for x in side["sweep"] if abs(x["degrees"]) <= 25) for side in sides.values()),
    "rudder_clear_at_plus_minus_30": all(all(x["triangle_intersections"] == 0 for x in side["sweep"]) for side in sides.values()),
    "hinge_bridges_manifold": len(hinges["results"]) == 10 and all(x["sleeve_with_bridge_nonmanifold"] == 0 for x in hinges["results"]),
    "hinge_bridges_joined_to_parent": bool(hinges.get("accepted")),
    "elevon_physical_hinges_verified": not bool(elevons.get("open")),
    "flight_ready": False,
    "water_ready": False,
    "land_ready": False,
}
report = {
    "version": "v334",
    "type": "evidence-only acceptance gate",
    "reference_sha256_actual": actual,
    "checks": checks,
    "passed": [k for k, v in checks.items() if v],
    "blocked": [k for k, v in checks.items() if not v],
    "notes": [
        "BVH triangle intersections do not prove physical clearance.",
        "No real land, water or flight tests have been supplied.",
        "No servo torque, structural load, mass, thrust or watertightness validation.",
        "Do not label this model Final Master or replace README master imagery."
    ],
    "accepted": all(checks.values()),
}
out = ROOT / "docs/V334_CONTROL_SURFACE_ACCEPTANCE_GATE.json"
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report, indent=2))
