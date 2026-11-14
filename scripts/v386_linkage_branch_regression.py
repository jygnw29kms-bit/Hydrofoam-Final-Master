"""Hydrofoam v386: deterministic linkage reachability regression, bench only.

Tests v385's inverse kinematics for both assembly branches, detects branch
flips and servo sweep discontinuities. No claim of 3D collision clearance.
Run: python scripts/v386_linkage_branch_regression.py
"""
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v385", HERE / "v385_linkage_kinematics.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def wrap_difference(a, b):
    return (a - b + 180.0) % 360.0 - 180.0


def audit():
    baseline = module.solve()
    geometry = baseline["geometry_mm"]
    shaft = tuple(geometry["servo_shaft"])
    radius = geometry["servo_arm_radius"]
    horn_radius = geometry["horn_radius"]
    rod_length = geometry["rod_center_distance"]
    previous_angle = None
    issues = []
    rows = []
    for sample in baseline["samples"]:
        angle = sample["rudder_deg"]
        theta = math.radians(angle)
        horn = (horn_radius * math.cos(theta), horn_radius * math.sin(theta))
        solutions = module.circle_intersections(shaft, radius, horn, rod_length)
        if not solutions:
            issues.append(f"rudder {angle}: linkage unreachable")
            rows.append({"rudder_deg": angle, "reachable": False})
            continue
        # The v385 reference branch chooses the servo-arm endpoint nearest
        # (shaft_x - radius, shaft_y), independently at every sample.
        reference = (shaft[0] - radius, shaft[1])
        chosen = min(solutions, key=lambda p: math.dist(p, reference))
        servo_angle = math.degrees(math.atan2(chosen[1]-shaft[1], chosen[0]-shaft[0]))
        if previous_angle is not None:
            jump = abs(wrap_difference(servo_angle, previous_angle))
            if jump > 25:
                issues.append(f"rudder {angle}: servo discontinuity {jump:.3f} deg")
        previous_angle = servo_angle
        # Endpoint distance residuals are necessary, not sufficient,
        # geometric checks; rounded input from v385 limits precision.
        residual = max(abs(math.dist(chosen, shaft)-radius),
                       abs(math.dist(chosen, horn)-rod_length))
        if residual > 0.001:
            issues.append(f"rudder {angle}: endpoint residual {residual:.5f} mm")
        rows.append({"rudder_deg": angle, "reachable": True,
                     "servo_deg": round(servo_angle, 4),
                     "endpoint_residual_mm": round(residual, 6),
                     "solution_count": len(solutions)})
    return {"version": "v386", "scope": "PLANAR_BENCH_ONLY",
            "approved": False, "baseline": "v385_linkage_kinematics.py",
            "sample_count": len(rows), "issues": issues,
            "planar_regression_pass": not issues,
            "samples": rows,
            "not_verified": ["airframe integration", "3D collisions",
                             "hinge clearances", "servo torque", "print fit",
                             "master-image fidelity", "land/water/air operation"]}


if __name__ == "__main__":
    result = audit()
    output = HERE.parent / "build" / "v386" / "linkage_branch_audit.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"planar_regression_pass": result["planar_regression_pass"],
                      "issues": result["issues"], "output": str(output)}, indent=2))
    raise SystemExit(0 if result["planar_regression_pass"] else 1)
