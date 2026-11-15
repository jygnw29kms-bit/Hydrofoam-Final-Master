"""v413: dependency-free planar servo linkage feasibility solver (millimetres).
Not an airframe clearance, load, or physical flight certification.
Input JSON: {"surfaces":{"left_aileron":{...}, ...}}.
Each surface requires servo_pivot_yz_mm, horn_pivot_yz_mm,
servo_arm_mm, horn_arm_mm, rod_length_mm, travel_deg, servo_limits_deg.
Angles are measured in the local YZ plane, in degrees.
"""
import argparse
import json
import math
from pathlib import Path

REQUIRED = {"left_aileron", "right_aileron", "elevator_left", "elevator_right", "rudder"}

def point(p, r, deg):
    t = math.radians(deg)
    return (p[0] + r * math.cos(t), p[1] + r * math.sin(t))

def servo_candidates(pivot, length, target, rod):
    dx, dy = target[0]-pivot[0], target[1]-pivot[1]
    d = math.hypot(dx, dy)
    if d < 1e-9 or d > length+rod+1e-8 or d < abs(length-rod)-1e-8:
        return []
    cos_a = max(-1., min(1., (length*length+d*d-rod*rod)/(2*length*d)))
    a = math.acos(cos_a)
    base = math.atan2(dy, dx)
    return [math.degrees(base+a), math.degrees(base-a)]

def wrap(deg):
    return (deg+180)%360-180

def evaluate(name, p):
    sp = tuple(map(float,p["servo_pivot_yz_mm"]))
    hp = tuple(map(float,p["horn_pivot_yz_mm"]))
    sa, ha, rod = (float(p[k]) for k in ("servo_arm_mm","horn_arm_mm","rod_length_mm"))
    travel = float(p["travel_deg"])
    lo, hi = map(float,p["servo_limits_deg"])
    steps = int(p.get("samples",81))
    if not (len(sp)==len(hp)==2 and all(math.isfinite(v) for v in (*sp,*hp,sa,ha,rod,travel,lo,hi)) and
            min(sa,ha,rod)>0 and 0<travel<=60 and lo<hi and steps>=21 and steps<=2001):
        raise ValueError(name+": invalid linkage configuration")
    samples=[]
    previous=None
    errors=[]
    for i in range(steps):
        rudder=-travel+2*travel*i/(steps-1)
        target=point(hp,ha,rudder)
        candidates=[c+360*k for c in servo_candidates(sp,sa,target,rod) for k in range(-2,3)]
        valid=[c for c in candidates if lo-1e-7<=c<=hi+1e-7]
        if not valid:
            errors.append({"rudder_deg":rudder,"error":"unreachable_or_servo_limit"})
            continue
        selected=min(valid,key=lambda c:abs(c-(previous if previous is not None else (lo+hi)/2)))
        if previous is not None and abs(selected-previous)>15:
            errors.append({"rudder_deg":rudder,"error":"servo_branch_jump"})
        endpoint=point(sp,sa,selected)
        residual=abs(math.dist(endpoint,target)-rod)
        if residual>1e-5:
            errors.append({"rudder_deg":rudder,"error":"rod_length_residual","mm":residual})
        samples.append({"rudder_deg":round(rudder,5),"servo_deg":round(selected,5),
                        "rod_residual_mm":residual})
        previous=selected
    return {"status":"KINEMATIC_PASS_ONLY" if not errors and len(samples)==steps else "FAIL",
            "samples":samples,"errors":errors,
            "not_verified":["3D_collision","servo_mount","horn_attachment","printability",
                            "loads","airframe_integration","master_image_match"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("config",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    cfg=json.loads(args.config.read_text(encoding="utf-8"))
    if set(cfg.get("surfaces",{}))!=REQUIRED:
        raise ValueError("Exactly five named surfaces are mandatory")
    results={name:evaluate(name,p) for name,p in cfg["surfaces"].items()}
    report={"classification":"WIP_PLANAR_KINEMATICS_ONLY","results":results,
            "accepted":False,"reason":"No physical, 3D, or image-master verification"}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({k:v["status"] for k,v in results.items()},indent=2))
    if any(v["status"]=="FAIL" for v in results.values()):
        raise SystemExit(2)

if __name__=="__main__":
    main()
