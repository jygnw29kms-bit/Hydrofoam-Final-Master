"""Hydrofoam v413: deterministic planar servo-linkage feasibility gate.

Input is a reviewed JSON with five surfaces. This is a 2-D kinematic
screening tool, NOT a 3-D collision, print, or flight certification.
All positions in mm in each hinge-local YZ plane, angles in degrees.
The hinge is at (0,0). The servo pivot is fixed. A rigid pushrod joins
servo-arm and control-horn endpoints. Positive angles are CCW in YZ.
"""
import argparse
import json
import math
from pathlib import Path

REQUIRED = {"left_aileron", "right_aileron", "elevator_left", "elevator_right", "rudder"}

def point(p, key):
    v = p[key]
    if not isinstance(v, list) or len(v) != 2 or not all(isinstance(x, (int,float)) and math.isfinite(x) for x in v):
        raise ValueError(f"{key}: expected finite [y,z]")
    return tuple(map(float,v))

def rotate(p, deg):
    a = math.radians(deg)
    return (p[0]*math.cos(a)-p[1]*math.sin(a),p[0]*math.sin(a)+p[1]*math.cos(a))

def dist(a,b):
    return math.hypot(a[0]-b[0],a[1]-b[1])

def servo_solutions(pivot, arm, target, rod):
    """Circle-circle intersection, return servo angles."""
    d = dist(pivot,target)
    if d < 1e-9 or d > arm+rod+1e-8 or d < abs(arm-rod)-1e-8:
        return []
    c = max(-1.,min(1.,(arm*arm+d*d-rod*rod)/(2*arm*d)))
    base = math.atan2(target[1]-pivot[1],target[0]-pivot[0])
    delta = math.acos(c)
    return [math.degrees(base+delta), math.degrees(base-delta)]

def angle_difference(a,b):
    return (a-b+180)%360-180

def solve_surface(p):
    pivot = point(p,"servo_pivot_yz_mm")
    horn = point(p,"horn_tip_neutral_yz_mm")
    arm = float(p["servo_arm_mm"])
    rod = float(p["rod_length_mm"])
    travel = float(p["rudder_travel_deg"])
    servo_min,servo_max = map(float,p["servo_limits_deg"])
    samples = int(p.get("samples",81))
    if not all(math.isfinite(x) for x in [arm,rod,travel,servo_min,servo_max]):
        raise ValueError("Nonfinite dimensions")
    if arm <= 0 or rod <= 0 or not 0 < travel <= 60 or servo_min >= servo_max or samples < 21 or samples > 2001:
        raise ValueError("Invalid servo geometry/travel")
    if dist(horn,(0,0)) < 1:
        raise ValueError("Horn too close to hinge axis")
    rows=[]
    last=None
    for i in range(samples):
        rudder=-travel+2*travel*i/(samples-1)
        target=rotate(horn,rudder)
        candidates=servo_solutions(pivot,arm,target,rod)
        candidates=[x for x in candidates if servo_min-1e-8 <= x <= servo_max+1e-8]
        if last is not None:
            candidates.sort(key=lambda x:abs(angle_difference(x,last)))
        else:
            neutral=float(p.get("preferred_servo_angle_deg",0))
            candidates.sort(key=lambda x:abs(angle_difference(x,neutral)))
        chosen=candidates[0] if candidates else None
        if chosen is not None:
            last=chosen
        rows.append({"rudder_deg":round(rudder,5),"servo_deg":None if chosen is None else round(chosen,5),"solutions_within_limits":len(candidates)})
    missing=sum(r["servo_deg"] is None for r in rows)
    max_step=max((abs(angle_difference(b["servo_deg"],a["servo_deg"])) for a,b in zip(rows,rows[1:]) if a["servo_deg"] is not None and b["servo_deg"] is not None),default=0)
    passed=missing==0 and max_step<=float(p.get("max_servo_step_deg",12))
    return {"status":"KINEMATIC_SCREEN_PASS" if passed else "KINEMATIC_SCREEN_FAIL", "unreachable_samples":missing,"max_step_deg":round(max_step,5),"samples":rows,
            "limitations":["No 3-D linkage collision analysis", "No servo torque/load analysis", "No printable hinge or horn validation", "No airframe installation validation"]}

def audit(config):
    if set(config.get("surfaces",{})) != REQUIRED:
        raise ValueError("Exactly five named control surfaces required")
    results={}
    for name,p in config["surfaces"].items():
        try: results[name]=solve_surface(p)
        except (KeyError,TypeError,ValueError,OverflowError) as e: results[name]={"status":"INVALID_INPUT","error":str(e)}
    return {"version":"v413","classification":"WIP_KINEMATIC_SCREEN","all_screens_pass":all(r["status"]=="KINEMATIC_SCREEN_PASS" for r in results.values()),
            "final_master_image_verified":False,"integrated_mechanism_verified":False,"land_water_air_verified":False,"surfaces":results}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("config",type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    report=audit(json.loads(args.config.read_text(encoding="utf-8")))
    payload=json.dumps(report,indent=2,allow_nan=False)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload+"\n",encoding="utf-8")
    else: print(payload)
    raise SystemExit(0 if report["all_screens_pass"] else 2)
if __name__=="__main__": main()
