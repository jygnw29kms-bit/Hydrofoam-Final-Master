"""v348: Ground-contact and foil/propeller clearance sweep (planning only).

Coordinates are measured in millimetres in one body frame, +Z upward.
Rigid-body pitch/roll are applied about the measured centre of gravity.
At each attitude, the lowest *skid* sets the ground plane. The routine
never permits a foil or propeller to serve as a ground contact.
For sand/grass, a measured or conservatively specified sinkage is subtracted.
No result is a driving or flight approval. Physical validation is mandatory.
"""
import json
import math
import sys
from pathlib import Path

SURFACES = {"hard", "short_grass", "firm_sand"}
REQUIRED = ("surface", "cg_mm", "skid_contacts_mm", "protected_points_mm",
            "pitch_deg", "roll_deg", "sinkage_mm", "required_clearance_mm")


def finite(value, name):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(name + " must be a finite number")
    return float(value)


def vec3(value, name):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(name + " must be a three-element array")
    return tuple(finite(v, name) for v in value)


def rotate_about_cg(point, cg, pitch_deg, roll_deg):
    x, y, z = (point[i] - cg[i] for i in range(3))
    pitch, roll = math.radians(pitch_deg), math.radians(roll_deg)
    x, z = x * math.cos(pitch) + z * math.sin(pitch), -x * math.sin(pitch) + z * math.cos(pitch)
    y, z = y * math.cos(roll) - z * math.sin(roll), y * math.sin(roll) + z * math.cos(roll)
    return x, y, z


def run(data):
    missing = [k for k in REQUIRED if k not in data]
    if missing:
        return {"version": "v348", "accepted": False, "screen_pass": False,
                "missing_inputs": missing}
    if data["surface"] not in SURFACES:
        raise ValueError("surface must be hard, short_grass or firm_sand")
    cg = vec3(data["cg_mm"], "cg_mm")
    skids = data["skid_contacts_mm"]
    if not isinstance(skids, list) or len(skids) < 3:
        raise ValueError("at least three measured skid contact points required")
    skids = [vec3(p, "skid contact") for p in skids]
    protected = data["protected_points_mm"]
    if not isinstance(protected, dict) or not protected:
        raise ValueError("protected_points_mm must map part names to point arrays")
    parts = {}
    for name, points in protected.items():
        if not isinstance(name, str) or not name or not isinstance(points, list) or not points:
            raise ValueError("each protected part requires a name and measured points")
        parts[name] = [vec3(p, name) for p in points]
    for mandatory in ("left_foil", "right_foil", "propeller"):
        if mandatory not in parts:
            raise ValueError("missing protected component: " + mandatory)
    pitch = data["pitch_deg"]
    roll = data["roll_deg"]
    if not isinstance(pitch, list) or not pitch or not isinstance(roll, list) or not roll:
        raise ValueError("pitch_deg and roll_deg must be nonempty arrays")
    for angle in pitch + roll:
        if abs(finite(angle, "angle")) > 45:
            raise ValueError("angle magnitude exceeds 45 degrees")
    sinkage = finite(data["sinkage_mm"], "sinkage_mm")
    minimum = finite(data["required_clearance_mm"], "required_clearance_mm")
    if sinkage < 0 or minimum < 0:
        raise ValueError("sinkage and required clearance cannot be negative")
    samples = []
    for p in pitch:
        for r in roll:
            ground = min(rotate_about_cg(s, cg, p, r)[2] for s in skids)
            clearance = {
                name: round(min(rotate_about_cg(q, cg, p, r)[2] - ground - sinkage
                                for q in points), 4)
                for name, points in parts.items()
            }
            samples.append({"pitch_deg": p, "roll_deg": r,
                            "clearance_mm": clearance,
                            "screen_pass": all(v >= minimum for v in clearance.values())})
    worst = {name: min(row["clearance_mm"][name] for row in samples) for name in parts}
    return {"version": "v348", "accepted": False,
            "screen_pass": all(row["screen_pass"] for row in samples),
            "surface": data["surface"], "worst_clearance_mm": worst,
            "samples": samples,
            "limitations": [
                "Protected-point lists must include the actual lowest point of every foil and the swept propeller disk.",
                "No tire/skid deformation, grass deflection, steering load, vibration or impact is modelled.",
                "Sinkage is an input, not a prediction. Measure it separately for each surface.",
                "A passed screen is not proof of land, water or flight capability."
            ]}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python scripts/engineering_v348_foil_prop_clearance.py input.json")
    source = Path(sys.argv[1])
    result = run(json.loads(source.read_text(encoding="utf-8")))
    destination = source.with_name(source.stem + "_v348_clearance.json")
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(destination, "screen_pass:", result["screen_pass"], "accepted:", result["accepted"])
