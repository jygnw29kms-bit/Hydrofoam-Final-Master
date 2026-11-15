"""v403: hydrostatic displacement and flotation preflight for BOTH floats.
No guessed geometry, no dynamic foil-lift or water-tightness approval.
Usage: python scripts/v403_buoyancy_budget.py measured_hydrostatics.json
Input volume is submerged displacement measured at the proposed waterline,
not total hull volume. All numbers must be sourced from CAD or measurements.
"""
import json
import math
import pathlib
import sys

def number(x, positive=False):
    return type(x) in (int, float) and math.isfinite(x) and (x > 0 if positive else x >= 0)

def analyze(data):
    errors = []
    m = data.get("mass", {})
    h = data.get("hydrostatics", {})
    floats = h.get("floats", [])
    for k in ("all_up_mass_g", "density_water_kg_m3", "minimum_buoyancy_reserve_fraction"):
        source = m if k == "all_up_mass_g" else h
        if not number(source.get(k), positive=(k != "minimum_buoyancy_reserve_fraction")):
            errors.append("invalid " + k)
    if not isinstance(floats, list) or len(floats) != 2:
        errors.append("exactly two independent float displacement records required")
        floats = []
    ids = set()
    for f in floats:
        if not isinstance(f, dict):
            errors.append("float record must be an object")
            continue
        name = f.get("id")
        if not isinstance(name, str) or not name or name in ids:
            errors.append("float ids must be unique and nonempty")
        ids.add(name)
        for k in ("submerged_volume_cm3", "maximum_allowed_submerged_volume_cm3", "x_center_buoyancy_mm", "y_center_buoyancy_mm"):
            if k.startswith(("x_", "y_")):
                if type(f.get(k)) not in (int, float) or not math.isfinite(f[k]):
                    errors.append(str(name) + ": invalid " + k)
            elif not number(f.get(k), positive=True):
                errors.append(str(name) + ": invalid " + k)
        if f.get("evidence") not in ("measured", "cad"):
            errors.append(str(name) + ": evidence must be measured or cad")
        if not f.get("source_file"):
            errors.append(str(name) + ": source_file required")
    if errors:
        return {"status": "BLOCKED", "errors": errors}
    if any(f["submerged_volume_cm3"] > f["maximum_allowed_submerged_volume_cm3"] for f in floats):
        errors.append("proposed waterline exceeds maximum permitted submerged volume")
    rho = h["density_water_kg_m3"]
    displacement_g = sum(f["submerged_volume_cm3"] for f in floats) * rho / 1000.0
    mass_g = m["all_up_mass_g"]
    reserve = displacement_g / mass_g - 1
    center = {}
    volume = sum(f["submerged_volume_cm3"] for f in floats)
    for axis in ("x", "y"):
        center[axis + "_mm"] = sum(f["submerged_volume_cm3"] * f[axis + "_center_buoyancy_mm"] for f in floats) / volume
    if displacement_g < mass_g:
        errors.append("insufficient buoyancy at proposed waterline")
    if reserve < h["minimum_buoyancy_reserve_fraction"]:
        errors.append("buoyancy reserve below requirement")
    return {"status": "PASS_STATIC_DISPLACEMENT_ONLY" if not errors else "BLOCKED",
            "errors": errors, "displacement_capacity_g": round(displacement_g, 3),
            "all_up_mass_g": mass_g, "reserve_fraction": round(reserve, 5),
            "combined_center_buoyancy_mm": {k: round(v, 3) for k,v in center.items()},
            "disclaimer": "Static displacement arithmetic only; no pitch/roll stability, free-surface, leakage, planing, foil lift or real-world certification."}

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/v403_buoyancy_budget.py measured_hydrostatics.json")
    p = pathlib.Path(sys.argv[1])
    result = analyze(json.loads(p.read_text(encoding="utf-8")))
    out = p.with_suffix(".buoyancy_report.json")
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "report": str(out)}))
    if result["status"] != "PASS_STATIC_DISPLACEMENT_ONLY":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
