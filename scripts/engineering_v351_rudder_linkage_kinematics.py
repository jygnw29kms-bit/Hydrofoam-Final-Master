"""v351 rudder pushrod linkage kinematics, geometry-only screening.

Input JSON contains measured pivot locations and servo/rudder horn radii.
Units: mm, degrees. XY plane is the local linkage plane. The servo arm
rotates about servo_pivot_mm; the rudder horn rotates about hinge_pivot_mm.
A fixed-length pushrod joins their tips. Solve rudder angle by intersecting
the horn-tip circle with the rod-length circle at each servo sample.

Does NOT check 3D collision, joint angular limits, mounting stiffness,
water sealing, printed clearances or physical servo performance.
"""
import json
import math
import sys
from pathlib import Path

def point(v):
    if not isinstance(v, list) or len(v) != 2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("finite [x,y] required")
    return tuple(map(float,v))

def scalar(d,key,positive=False):
    v=d[key]
    if type(v) not in (int,float) or not math.isfinite(v) or (positive and v<=0):
        raise ValueError(key+" invalid")
    return float(v)

def arm(p,r,angle):
    a=math.radians(angle)
    return (p[0]+r*math.cos(a),p[1]+r*math.sin(a))

def dist(a,b):
    return math.hypot(a[0]-b[0],a[1]-b[1])

def wrap(a):
    return (a+180)%360-180

def solve(h,tip,rod,r):
    # Circle intersection: rudder horn tip at radius r from h,
    # and rod end at radius rod from servo arm tip.
    dx,dy=tip[0]-h[0],tip[1]-h[1]
    d=math.hypot(dx,dy)
    if d<1e-9 or d>r+rod+1e-8 or d<abs(r-rod)-1e-8:
        return []
    along=(r*r-rod*rod+d*d)/(2*d)
    offset=math.sqrt(max(0.0,r*r-along*along))
    mx,my=h[0]+along*dx/d,h[1]+along*dy/d
    return [(mx-offset*dy/d,my+offset*dx/d),(mx+offset*dy/d,my-offset*dx/d)]

def run(d):
    required=("servo_pivot_mm","hinge_pivot_mm","servo_horn_radius_mm",
              "rudder_horn_radius_mm","rod_length_mm","servo_angles_deg",
              "neutral_rudder_angle_deg","rudder_angle_limit_deg",
              "max_step_deg","minimum_transmission_sine")
    missing=[k for k in required if k not in d]
    if missing:return {"version":"v351","screen_pass":False,"accepted":False,"missing_inputs":missing}
    s=point(d["servo_pivot_mm"]);h=point(d["hinge_pivot_mm"])
    sr=scalar(d,"servo_horn_radius_mm",True)
    hr=scalar(d,"rudder_horn_radius_mm",True)
    rod=scalar(d,"rod_length_mm",True)
    neutral=scalar(d,"neutral_rudder_angle_deg")
    limit=scalar(d,"rudder_angle_limit_deg",True)
    max_step=scalar(d,"max_step_deg",True)
    transmission=scalar(d,"minimum_transmission_sine",True)
    if not 0<transmission<=1:raise ValueError("transmission sine must be in (0,1]")
    angles=d["servo_angles_deg"]
    if not isinstance(angles,list) or len(angles)<3 or any(type(a) not in (int,float) or not math.isfinite(a) for a in angles):
        raise ValueError("servo_angles_deg needs at least three finite samples")
    if angles!=sorted(angles) or len(set(angles))!=len(angles):
        raise ValueError("servo angles must be strictly increasing")
    rows=[];previous=neutral;all_pass=True
    for servo_angle in angles:
        tip=arm(s,sr,servo_angle)
        choices=solve(h,tip,rod,hr)
        candidates=[]
        for p in choices:
            a=math.degrees(math.atan2(p[1]-h[1],p[0]-h[0]))
            rod_vector=(tip[0]-p[0],tip[1]-p[1])
            horn_vector=(p[0]-h[0],p[1]-h[1])
            sine=abs(horn_vector[0]*rod_vector[1]-horn_vector[1]*rod_vector[0])/(hr*rod)
            candidates.append((abs(wrap(a-previous)),a,sine,p))
        candidates.sort(key=lambda x:x[0])
        if not candidates:
            rows.append({"servo_angle_deg":servo_angle,"reachable":False,"screen_pass":False})
            all_pass=False
            continue
        step,a,sine,p=candidates[0]
        deviation=wrap(a-neutral)
        passed=step<=max_step and abs(deviation)<=limit and sine>=transmission
        rows.append({"servo_angle_deg":servo_angle,"rudder_angle_deg":round(a,4),
                     "rudder_deflection_deg":round(deviation,4),
                     "step_deg":round(step,4),"transmission_sine":round(sine,5),
                     "reachable":True,"screen_pass":passed})
        previous=a;all_pass=all_pass and passed
    return {"version":"v351","accepted":False,"screen_pass":all_pass,
            "samples":rows,"limitations":["Planar rigid linkage only; 3D collision not checked.",
            "Branch continuity is sampled, not a proof between samples.",
            "Servo travel, real hardware tolerances, hinges and mounts remain unverified.",
            "Screen pass never constitutes final-master acceptance."]}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v351_rudder_linkage_kinematics.py input.json")
    p=Path(sys.argv[1])
    result=run(json.loads(p.read_text(encoding="utf-8")))
    dest=p.with_name(p.stem+"_v351_rudder_kinematics.json")
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(dest,"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
