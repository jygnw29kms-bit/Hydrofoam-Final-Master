"""v347: Conservative three-contact ground-plane support screen.

This is a CAD/measurement planning tool, NOT a land-operation acceptance.
Unlike v346, it does not treat every installed skid point as load bearing.
For each attitude, points are transformed about the measured CG; only points
within a measured contact tolerance of the lowest ground-contact elevation
are eligible. The eligible points must form a nondegenerate support polygon.
A single low foil tip or a pair of skid corners therefore FAILS the screen.
The user must independently verify contact compliance, suspension and sinkage.
"""
import json
import math
import sys
from pathlib import Path

SURFACES = {"hard", "short_grass", "firm_sand"}


def vec3(value):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("expected [x,y,z] point")
    if any(type(v) not in (float, int) or not math.isfinite(v) for v in value):
        raise ValueError("point coordinates must be finite numbers")
    return tuple(float(v) for v in value)


def number(value, label, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(label + " must be a finite number >= " + str(minimum))
    return float(value)


def convex_hull(points):
    points = sorted(set(points))
    if len(points) < 3:
        return []
    def cross(o, a, b):
        return (a[0]-o[0])*(b[1]-o[1])-(a[1]-o[1])*(b[0]-o[0])
    lower, upper = [], []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 1e-9:
            lower.pop()
        lower.append(p)
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 1e-9:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]


def rotate(point, pitch, roll):
    x, y, z = point
    a, b = math.radians(pitch), math.radians(roll)
    x, z = x*math.cos(a)+z*math.sin(a), -x*math.sin(a)+z*math.cos(a)
    y, z = y*math.cos(b)-z*math.sin(b), y*math.sin(b)+z*math.cos(b)
    return (x, y, z)


def margin(poly):
    if len(poly) < 3:
        return None
    values = []
    for (x1,y1),(x2,y2) in zip(poly, poly[1:]+poly[:1]):
        length = math.hypot(x2-x1,y2-y1)
        values.append(((x2-x1)*(-y1)-(y2-y1)*(-x1))/length)
    return min(values)


def run(data):
    required = ["surface", "contacts_mm", "cg_mm", "pitch_deg", "roll_deg",
                "contact_height_tolerance_mm", "minimum_margin_mm"]
    missing = [key for key in required if key not in data]
    if missing:
        return {"version":"v347", "accepted":False, "screen_pass":False,
                "missing_inputs":missing}
    if data["surface"] not in SURFACES:
        raise ValueError("unsupported surface")
    cg = vec3(data["cg_mm"])
    contacts = data["contacts_mm"]
    if not isinstance(contacts,list) or len(contacts)<3:
        raise ValueError("at least three measured skid contacts required")
    contacts = [vec3(p) for p in contacts]
    tolerance = number(data["contact_height_tolerance_mm"], "contact_height_tolerance_mm")
    threshold = number(data["minimum_margin_mm"], "minimum_margin_mm")
    for key in ("pitch_deg", "roll_deg"):
        if not isinstance(data[key],list) or not data[key]:
            raise ValueError(key + " must contain angle samples")
        for angle in data[key]:
            if type(angle) not in (float,int) or not math.isfinite(angle) or abs(angle)>45:
                raise ValueError("angles must be finite and within +/-45 degrees")
    rows=[]
    for pitch in data["pitch_deg"]:
        for roll in data["roll_deg"]:
            positions=[rotate(tuple(p[i]-cg[i] for i in range(3)),pitch,roll)
                       for p in contacts]
            lowest=min(p[2] for p in positions)
            active=[p for p in positions if p[2] <= lowest+tolerance+1e-9]
            polygon=convex_hull([(p[0],p[1]) for p in active])
            m=margin(polygon)
            rows.append({"pitch_deg":pitch,"roll_deg":roll,
                         "active_contact_count":len(active),
                         "active_polygon_vertices":len(polygon),
                         "cg_margin_mm":None if m is None else round(m,4),
                         "screen_pass":m is not None and m>=threshold})
    return {"version":"v347", "surface":data["surface"],"accepted":False,
            "screen_pass":all(row["screen_pass"] for row in rows),
            "samples":rows,
            "limitations":["Assumes rigid ground plane and a measured contact-height tolerance.",
                           "No solution for load redistribution, compliance, differential sinkage or steering.",
                           "A passed screen is not a drive, hydrofoil or flight clearance."]}


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python scripts/engineering_v347_active_ground_contacts.py input.json")
    source=Path(sys.argv[1])
    result=run(json.loads(source.read_text(encoding="utf-8")))
    target=source.with_name(source.stem+"_v347_active_contacts.json")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(target, "screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
