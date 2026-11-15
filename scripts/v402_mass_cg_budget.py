"""v402: three-mode mass, CG and static stability budget. Engineering preflight, NOT flight approval.

Usage: python scripts/v402_mass_cg_budget.py parts.json
Input: {"components":[{"name":"battery","mass_g":180,"x_mm":0,"y_mm":0,"z_mm":30}, ...],
"limits":{"max_mass_g":1500,"cg_x_min_mm":-15,"cg_x_max_mm":25,
"cg_y_abs_max_mm":8,"min_static_thrust_ratio":0.7},
"measurements":{"static_thrust_g":1100},
"modes":{"land":{"excluded":[]},"water":{"excluded":[]},"air":{"excluded":[]}}}
All values must be measured or explicitly identified as estimates in the source data.
Coordinate frame and positive axes must be declared in input metadata.
"""
import json
import math
import pathlib
import sys

MODES = ("land", "water", "air")
AXES = ("x_mm", "y_mm", "z_mm")

def finite_positive(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value > 0

def analyze(data):
    errors = []
    meta = data.get("metadata", {})
    if not all(meta.get(k) for k in ("coordinate_frame", "axis_convention", "measurement_source")):
        errors.append("metadata requires coordinate_frame, axis_convention, measurement_source")
    parts = data.get("components", [])
    if not isinstance(parts, list) or not parts:
        errors.append("nonempty components array required")
        parts = []
    names = set()
    for p in parts:
        if not isinstance(p, dict):
            errors.append("component must be object")
            continue
        name = p.get("name")
        if not isinstance(name, str) or not name or name in names:
            errors.append("missing or duplicate component name")
        names.add(name)
        if not finite_positive(p.get("mass_g")):
            errors.append(str(name) + ": invalid mass_g")
        if any(not isinstance(p.get(axis), (int, float)) or not math.isfinite(p.get(axis)) for axis in AXES):
            errors.append(str(name) + ": invalid coordinates")
        if p.get("basis") not in ("measured", "estimated"):
            errors.append(str(name) + ": basis must be measured or estimated")
    limits = data.get("limits", {})
    for key in ("max_mass_g", "cg_x_min_mm", "cg_x_max_mm", "cg_y_abs_max_mm", "min_static_thrust_ratio"):
        if not isinstance(limits.get(key), (int, float)) or not math.isfinite(limits[key]):
            errors.append("missing/invalid limit " + key)
    if errors:
        return {"status": "BLOCKED", "errors": errors, "modes": {}}
    if limits["cg_x_min_mm"] > limits["cg_x_max_mm"] or limits["max_mass_g"] <= 0 or limits["cg_y_abs_max_mm"] < 0 or limits["min_static_thrust_ratio"] <= 0:
        return {"status": "BLOCKED", "errors": ["inconsistent limits"], "modes": {}}
    result = {}
    for mode in MODES:
        config = data.get("modes", {}).get(mode)
        if not isinstance(config, dict) or not isinstance(config.get("excluded"), list):
            errors.append(mode + ": explicit excluded list required")
            continue
        excluded = config["excluded"]
        if len(excluded) != len(set(excluded)) or any(n not in names for n in excluded):
            errors.append(mode + ": unknown/duplicate excluded component")
            continue
        active = [p for p in parts if p["name"] not in excluded]
        total = sum(p["mass_g"] for p in active)
        if total <= 0:
            errors.append(mode + ": zero mass")
            continue
        cg = {axis: sum(p["mass_g"] * p[axis] for p in active) / total for axis in AXES}
        checks = {"mass_limit": total <= limits["max_mass_g"],
                  "cg_longitudinal": limits["cg_x_min_mm"] <= cg["x_mm"] <= limits["cg_x_max_mm"],
                  "cg_lateral": abs(cg["y_mm"]) <= limits["cg_y_abs_max_mm"]}
        thrust = data.get("measurements", {}).get("static_thrust_g")
        if mode == "air":
            checks["thrust_ratio"] = finite_positive(thrust) and thrust / total >= limits["min_static_thrust_ratio"]
        result[mode] = {"mass_g": round(total, 3),
                        "cg_mm": {k: round(v, 3) for k, v in cg.items()},
                        "estimated_parts": [p["name"] for p in active if p["basis"] == "estimated"],
                        "thrust_to_weight": round(thrust / total, 4) if mode == "air" and finite_positive(thrust) else None,
                        "checks": checks, "status": "PASS_BUDGET" if all(checks.values()) else "BLOCKED"}
    status = "PASS_BUDGET_ONLY" if not errors and len(result) == 3 and all(v["status"] == "PASS_BUDGET" for v in result.values()) else "BLOCKED"
    return {"status": status, "errors": errors, "modes": result,
            "disclaimer": "Mass/CG arithmetic only. No aerodynamic, hydrodynamic, terrain or structural approval."}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/v402_mass_cg_budget.py parts.json")
    path = pathlib.Path(sys.argv[1])
    report = analyze(json.loads(path.read_text(encoding="utf-8")))
    out = path.with_suffix(".mass_cg_report.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"status": report["status"], "report": str(out)}))
    if report["status"] != "PASS_BUDGET_ONLY":
        sys.exit(1)

if __name__ == "__main__":
    main()
