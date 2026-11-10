"""v347: conservative support contact and ground-clearance screening.

Uses measured body-frame skid points, foil low points and propeller low points.
For each prescribed pitch/roll attitude, finds the lowest transformed support
points and treats only those within measured contact compliance as load-bearing.
This is a geometric envelope, not a structural or driving certification.
Coordinates are millimetres, Z up. Rotation is about measured CG.
"""
import json
import math
import sys
from pathlib import Path

def vec3(value, name):
    if not isinstance(value, list) or len(value) != 3 or any(
        type(v) not in (int, float) or not math.isfinite(v) for v in value
    ):
        raise ValueError(name + " must be three finite coordinates")
    return tuple(float(v) for v in value)

def number(value, name, nonnegative=True):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError(name + " must be finite")
    if nonnegative and value < 0:
        raise ValueError(name + " must be nonnegative")
    return float(value)

def transform(p, cg, pitch_deg, roll_deg):
    x, y, z = (p[i] - cg[i] for i in range(3))
    a, b = math.radians(pitch_deg), math.radians(roll_deg)
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
    return x, y, z

def convex_hull(points):
    points = sorted(set(points))
    if len(points) < 3:
        return []
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]

def cg_margin(hull):
    if len(hull) < 3:
        return None
    return min(
        ((b[0]-a[0])*(-a[1])-(b[1]-a[1])*(-a[0])) /
        math.hypot(b[0]-a[0], b[1]-a[1])
        for a, b in zip(hull, hull[1:] + hull[:1])
    )

def evaluate(data):
    required = ("cg_mm", "skid_contact_points_mm", "foil_low_points_mm",
                "propeller_low_points_mm", "pitch_deg", "roll_deg",
                "contact_compliance_mm", "surface_intrusion_mm",
                "minimum_foil_clearance_mm", "minimum_prop_clearance_mm",
                "minimum_cg_margin_mm")
    missing = [k for k in required if k not in data]
    if missing:
        return {"version": "v347", "accepted": False, "missing_inputs": missing}
    cg = vec3(data["cg_mm"], "cg_mm")
    arrays = {}
    for name in ("skid_contact_points_mm", "foil_low_points_mm", "propeller_low_points_mm"):
        raw = data[name]
        if not isinstance(raw, list) or not raw:
            raise ValueError(name + " requires measured points")
        arrays[name] = [vec3(p, name) for p in raw]
    if len(arrays["skid_contact_points_mm"]) < 3:
        raise ValueError("at least three skid reference points required")
    values = {name: number(data[name], name) for name in (
        "contact_compliance_mm", "surface_intrusion_mm",
        "minimum_foil_clearance_mm", "minimum_prop_clearance_mm",
        "minimum_cg_margin_mm")}
    angles = {}
    for name in ("pitch_deg", "roll_deg"):
        seq = data[name]
        if not isinstance(seq, list) or not seq:
            raise ValueError(name + " must be nonempty angle list")
        angles[name] = [number(v, name, False) for v in seq]
        if any(abs(v) > 45 for v in angles[name]):
            raise ValueError(name + " exceeds 45 degrees")
    rows = []
    for pitch in angles["pitch_deg"]:
        for roll in angles["roll_deg"]:
            skids = [transform(p, cg, pitch, roll) for p in arrays["skid_contact_points_mm"]]
            floor_z = min(p[2] for p in skids)
            active = [p for p in skids if p[2] <= floor_z + values["contact_compliance_mm"] + 1e-8]
            margin = cg_margin(convex_hull([(p[0], p[1]) for p in active]))
            clearance = {}
            for kind, key in (("foil", "foil_low_points_mm"), ("propeller", "propeller_low_points_mm")):
                points = [transform(p, cg, pitch, roll) for p in arrays[key]]
                clearance[kind] = min(p[2] - floor_z for p in points) - values["surface_intrusion_mm"]
            screen_pass = (margin is not None and margin >= values["minimum_cg_margin_mm"]
                           and clearance["foil"] >= values["minimum_foil_clearance_mm"]
                           and clearance["propeller"] >= values["minimum_prop_clearance_mm"])
            rows.append({"pitch_deg": pitch, "roll_deg": roll,
                         "active_support_points": len(active),
                         "cg_margin_mm": None if margin is None else round(margin, 3),
                         "foil_clearance_mm": round(clearance["foil"], 3),
                         "propeller_clearance_mm": round(clearance["propeller"], 3),
                         "geometry_screen_pass": screen_pass})
    return {"version": "v347", "accepted": False,
            "geometry_screening_pass": all(r["geometry_screen_pass"] for r in rows),
            "samples": rows,
            "limitations": [
                "Support points selected by height tolerance, not a solved elastic contact/force model.",
                "No dynamic steering, skid wear, sand sinkage distribution or traction acceptance.",
                "No hydrodynamic, aerodynamic, watertightness or flight acceptance.",
                "Real measured geometry and operating loads are mandatory."]}

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python engineering_v347_active_contacts.py measured.json")
    source = Path(sys.argv[1])
    result = evaluate(json.loads(source.read_text(encoding="utf-8")))
    output = source.with_name(source.stem + "_v347_contact_screen.json")
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(output, result.get("geometry_screening_pass"), "accepted:", result["accepted"])
