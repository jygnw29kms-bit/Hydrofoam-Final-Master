"""Hydrofoam v417: conservative three-mode mass and clearance screening.

Engineering precheck only. Values must come from measured CAD and hardware,
not visual estimates. No aerodynamic, hydrodynamic or flight certification.
Coordinates in mm, z up, common datum. Masses in grams. All deployment
states (land/water/air) are mandatory and independently evaluated.
"""
import argparse
import json
import math
from pathlib import Path

MODES = ("land", "water", "air")
SURFACES = ("hard_ground", "short_grass", "firm_sand")

def finite_positive(value, label, allow_zero=False):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label}: finite numeric value required")
    v = float(value)
    if not math.isfinite(v) or (v < 0 if allow_zero else v <= 0):
        raise ValueError(f"{label}: invalid value")
    return v

def screen(data):
    parts = data["parts"]
    if not isinstance(parts, list) or not parts:
        raise ValueError("parts must be nonempty")
    names = set()
    total_mass = 0.0
    moments = [0.0, 0.0, 0.0]
    for p in parts:
        name = p["name"]
        if not isinstance(name, str) or not name.strip() or name in names:
            raise ValueError("duplicate/invalid part name")
        names.add(name)
        mass = finite_positive(p["mass_g"], name + ".mass_g")
        xyz = p["cg_xyz_mm"]
        if not isinstance(xyz, list) or len(xyz) != 3:
            raise ValueError(name + ": cg_xyz_mm must contain three values")
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in xyz):
            raise ValueError(name + ": nonfinite CG")
        total_mass += mass
        for i in range(3):
            moments[i] += mass * xyz[i]
    cg = [v / total_mass for v in moments]
    max_mass = finite_positive(data["max_takeoff_mass_g"], "max_takeoff_mass_g")
    modes = data["modes"]
    if set(modes) != set(MODES):
        raise ValueError("exactly land, water and air states required")
    results = {}
    for mode in MODES:
        state = modes[mode]
        min_z = finite_positive(state["lowest_foil_z_mm"], mode + ".lowest_foil_z_mm", True)
        contact_z = finite_positive(state["ground_contact_z_mm"], mode + ".ground_contact_z_mm", True)
        if mode == "land":
            obstacles = state["surface_obstacle_allowance_mm"]
            if set(obstacles) != set(SURFACES):
                raise ValueError("all three land surfaces required")
            clearances = {}
            for surface in SURFACES:
                allowance = finite_positive(obstacles[surface], surface, True)
                clearances[surface] = round(min_z - contact_z - allowance, 3)
            clearance_pass = all(v > 0 for v in clearances.values())
            results[mode] = {"foil_clearance_by_surface_mm": clearances,
                             "geometric_screen_pass": clearance_pass}
        else:
            # Foil positions on water and in air are recorded, not used as
            # substitutes for flotation, foil lift or propeller safety tests.
            results[mode] = {"foil_relative_to_contact_mm": round(min_z - contact_z, 3),
                             "geometric_screen_pass": None}
    return {"classification": "WIP_MEASURED_INPUT_SCREEN",
            "total_mass_g": round(total_mass, 3),
            "cg_xyz_mm": [round(x, 3) for x in cg],
            "mass_budget_margin_g": round(max_mass - total_mass, 3),
            "mass_budget_screen_pass": total_mass <= max_mass,
            "modes": results,
            "final_release_authorized": False,
            "limitations": ["No structural load test", "No ground steering or skid wear test",
                            "No water sealing, planing or foil lift test",
                            "No aerodynamic stability, thrust or flight test",
                            "No measured input provenance verified"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("measurements", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = screen(json.loads(args.measurements.read_text(encoding="utf-8")))
    payload = json.dumps(report, indent=2, allow_nan=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    raise SystemExit(0 if report["mass_budget_screen_pass"] and
                     report["modes"]["land"]["geometric_screen_pass"] else 2)

if __name__ == "__main__":
    main()
