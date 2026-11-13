"""Hydrofoam v370: linkage kinematics from measured CAD pivots (WIP only).

All dimensions are millimetres. Input is a JSON file with:
 hinge_axis_y_mm, horn_radius_mm, servo_axis_xy_mm, servo_arm_radius_mm,
 servo_neutral_deg, servo_min_deg, servo_max_deg, rudder_min_deg,
 rudder_max_deg, step_deg, rod_length_mm, rod_length_tolerance_mm,
 servo_torque_nmm, hinge_moment_nmm, rod_axial_limit_n.
The hinge lies at (0,0) in the XZ section. Servo axis and horn geometry
MUST be measured in the actual assembly; no defaults are invented.
This is planar kinematics only, not a 3D collision or flight acceptance.
"""
import argparse
import json
import math
from pathlib import Path

REQUIRED = ("hinge_axis_y_mm", "horn_radius_mm", "servo_axis_xy_mm",
            "servo_arm_radius_mm", "servo_neutral_deg", "servo_min_deg",
            "servo_max_deg", "rudder_min_deg", "rudder_max_deg",
            "step_deg", "rod_length_mm", "rod_length_tolerance_mm",
            "servo_torque_nmm", "hinge_moment_nmm", "rod_axial_limit_n")

def point(center, radius, angle):
    a = math.radians(angle)
    return (center[0] + radius * math.cos(a),
            center[1] + radius * math.sin(a))

def distance(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])

def evaluate(d):
    missing = [k for k in REQUIRED if k not in d]
    if missing:
        raise ValueError("Missing measured input fields: " + ", ".join(missing))
    s = d["servo_axis_xy_mm"]
    if not isinstance(s, list) or len(s) != 2:
        raise ValueError("servo_axis_xy_mm must contain exactly two numbers")
    for k in REQUIRED:
        if k != "servo_axis_xy_mm" and not isinstance(d[k], (int, float)):
            raise ValueError("Non-numeric input: " + k)
    for k in ("horn_radius_mm", "servo_arm_radius_mm", "step_deg",
              "rod_length_mm", "rod_axial_limit_n", "servo_torque_nmm"):
        if d[k] <= 0:
            raise ValueError(k + " must be positive")
    if d["rod_length_tolerance_mm"] < 0 or d["hinge_moment_nmm"] < 0:
        raise ValueError("Invalid tolerance or load")
    if d["servo_min_deg"] >= d["servo_max_deg"] or d["rudder_min_deg"] >= d["rudder_max_deg"]:
        raise ValueError("Invalid angular limits")
    if d["step_deg"] > 10:
        raise ValueError("Step too coarse for provisional kinematic sweep")
    rows = []
    angle = d["rudder_min_deg"]
    while angle <= d["rudder_max_deg"] + 1e-9:
        horn = point((0, 0), d["horn_radius_mm"], angle)
        solutions = []
        # Sample servo angles at 0.25 degrees; refine later in real CAD.
        n = math.ceil((d["servo_max_deg"] - d["servo_min_deg"]) / 0.25)
        for i in range(n + 1):
            servo_angle = d["servo_min_deg"] + (d["servo_max_deg"] - d["servo_min_deg"]) * i / n
            arm = point(s, d["servo_arm_radius_mm"], servo_angle)
            residual = abs(distance(horn, arm) - d["rod_length_mm"])
            if residual <= d["rod_length_tolerance_mm"]:
                solutions.append((servo_angle, residual, arm))
        if solutions:
            chosen = min(solutions, key=lambda x: (x[1], abs(x[0] - d["servo_neutral_deg"])))
            arm = chosen[2]
            rod_angle = math.atan2(horn[1] - arm[1], horn[0] - arm[0])
            horn_angle = math.radians(angle)
            lever = abs(d["horn_radius_mm"] * math.sin(rod_angle - horn_angle))
            required_rod_force_n = d["hinge_moment_nmm"] / lever if lever > 1e-6 else float("inf")
            servo_arm_angle = math.radians(chosen[0])
            servo_lever = abs(d["servo_arm_radius_mm"] * math.sin(rod_angle - servo_arm_angle))
            required_servo_torque = required_rod_force_n * servo_lever
            valid = (required_rod_force_n <= d["rod_axial_limit_n"]
                     and required_servo_torque <= d["servo_torque_nmm"])
            rows.append(dict(rudder_deg=round(angle, 4), servo_deg=round(chosen[0], 4),
                             rod_residual_mm=round(chosen[1], 5),
                             required_rod_force_n=round(required_rod_force_n, 4),
                             required_servo_torque_nmm=round(required_servo_torque, 4),
                             planar_load_gate=valid))
        else:
            rows.append(dict(rudder_deg=round(angle, 4), planar_load_gate=False,
                             error="No servo angle satisfies measured rod length"))
        angle += d["step_deg"]
    return {"status": "PLANAR_PRECHECK_PASS_NOT_CERTIFICATION" if all(r["planar_load_gate"] for r in rows)
            else "FAIL_PLANAR_LINKAGE", "samples": rows,
            "limitations": ["Measured CAD pivots and loads must be supplied",
                            "Planar approximation; no 3D collisions, bearings, backlash or flex",
                            "No servo horn spline fit, P2S print fit, or dynamic load test",
                            "Does not certify LAND/WATER/AIR or master-photo fidelity"]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("measured_input_json")
    ap.add_argument("report_json")
    args = ap.parse_args()
    inp = Path(args.measured_input_json).resolve()
    out = Path(args.report_json).resolve()
    if inp == out or out.exists():
        raise SystemExit("Refusing input overwrite or existing report")
    result = evaluate(json.loads(inp.read_text(encoding="utf-8")))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(result["status"])

if __name__ == "__main__":
    main()
