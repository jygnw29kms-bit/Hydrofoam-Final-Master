"""Hydrofoam v351: rudder linkage kinematics and interference screening.

Standalone Python 3, no Blender required.
Input JSON: {"hinge_mm":[x,y], "servo_mm":[x,y],
"horn_radius_mm":r, "servo_arm_radius_mm":r, "neutral_horn_angle_deg":a,
"neutral_servo_angle_deg":a, "rudder_angles_deg":[...],
"linkage_radius_mm":r, "obstacles":[{"name":"...","center_mm":[x,y],"radius_mm":r}],
"servo_min_deg":-60,"servo_max_deg":60,"minimum_clearance_mm":1.0}
Coordinates represent a measured 2D control-plane projection, not full 3D.
Output: *_v351_kinematics.json. This is a design screen, NOT acceptance.
"""
import json, math, sys
from pathlib import Path

def scalar(v,name,lo=None):
    if type(v) not in (float,int) or not math.isfinite(v) or (lo is not None and v<lo):
        raise ValueError(name+" must be a finite number"+(" >= "+str(lo) if lo is not None else ""))
    return float(v)

def xy(v,name):
    if not isinstance(v,list) or len(v)!=2:raise ValueError(name+" must be [x,y]")
    return (scalar(v[0],name),scalar(v[1],name))

def endpoint(p,r,angle):
    t=math.radians(angle)
    return (p[0]+r*math.cos(t),p[1]+r*math.sin(t))

def dist(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])

def segment_distance(p,a,b):
    dx=b[0]-a[0];dy=b[1]-a[1];q=dx*dx+dy*dy
    if q<1e-12:return dist(p,a)
    t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/q))
    return dist(p,(a[0]+t*dx,a[1]+t*dy))

def solve(d):
    required=["hinge_mm","servo_mm","horn_radius_mm","servo_arm_radius_mm",
              "neutral_horn_angle_deg","neutral_servo_angle_deg",
              "rudder_angles_deg","linkage_radius_mm","obstacles",
              "servo_min_deg","servo_max_deg","minimum_clearance_mm"]
    missing=[x for x in required if x not in d]
    if missing:return {"version":"v351","screen_pass":False,"accepted":False,"missing_inputs":missing}
    hinge=xy(d["hinge_mm"],"hinge_mm");servo=xy(d["servo_mm"],"servo_mm")
    rh=scalar(d["horn_radius_mm"],"horn_radius_mm",0.1)
    rs=scalar(d["servo_arm_radius_mm"],"servo_arm_radius_mm",0.1)
    ah=scalar(d["neutral_horn_angle_deg"],"neutral_horn_angle_deg")
    a0=scalar(d["neutral_servo_angle_deg"],"neutral_servo_angle_deg")
    lr=scalar(d["linkage_radius_mm"],"linkage_radius_mm",0)
    clearance=scalar(d["minimum_clearance_mm"],"minimum_clearance_mm",0)
    smin=scalar(d["servo_min_deg"],"servo_min_deg")
    smax=scalar(d["servo_max_deg"],"servo_max_deg")
    if smin>=smax:raise ValueError("servo_min_deg must be below servo_max_deg")
    angles=d["rudder_angles_deg"]
    if not isinstance(angles,list) or not angles:raise ValueError("rudder_angles_deg required")
    if not isinstance(d["obstacles"],list):raise ValueError("obstacles must be a list")
    obstacles=[]
    for o in d["obstacles"]:
        obstacles.append((str(o["name"]),xy(o["center_mm"],"obstacle center"),
                          scalar(o["radius_mm"],"obstacle radius",0)))
    neutral_horn=endpoint(hinge,rh,ah)
    neutral_servo=endpoint(servo,rs,a0)
    length=dist(neutral_horn,neutral_servo)
    if length<1e-6:raise ValueError("neutral linkage length zero")
    rows=[]
    # Continuous servo-angle search: grid samples and bisection of length residual.
    # Find ALL roots to expose branch ambiguity and potential toggle positions.
    def residual(angle,horn):
        return dist(endpoint(servo,rs,angle),horn)-length
    for rudder_angle in angles:
        rudder_angle=scalar(rudder_angle,"rudder angle")
        horn=endpoint(hinge,rh,ah+rudder_angle)
        roots=[]
        steps=max(360,int((smax-smin)*4))
        prev=smin;fp=residual(prev,horn)
        for i in range(1,steps+1):
            curr=smin+(smax-smin)*i/steps;fc=residual(curr,horn)
            if abs(fp)<1e-8:roots.append(prev)
            if fp*fc<0:
                lo,hi=prev,curr;flo=fp
                for _ in range(45):
                    mid=(lo+hi)/2;fm=residual(mid,horn)
                    if flo*fm<=0:hi=mid
                    else:lo=mid;flo=fm
                roots.append((lo+hi)/2)
            prev,fp=curr,fc
        if abs(fp)<1e-8:roots.append(smax)
        roots=sorted(set(round(v,6) for v in roots))
        options=[]
        for angle in roots:
            arm=endpoint(servo,rs,angle)
            obclear={name:round(segment_distance(center,horn,arm)-radius-lr,4)
                     for name,center,radius in obstacles}
            options.append({"servo_angle_deg":angle,"obstacle_clearance_mm":obclear,
                            "obstacle_screen_pass":all(v>=clearance for v in obclear.values())})
        rows.append({"rudder_angle_deg":rudder_angle,"servo_solutions":options,
                     "screen_pass":bool(options) and any(x["obstacle_screen_pass"] for x in options),
                     "ambiguous_branches":len(options)>1})
    return {"version":"v351","accepted":False,"screen_pass":all(x["screen_pass"] for x in rows),
            "neutral_linkage_length_mm":round(length,4),"samples":rows,
            "limitations":["2D circular-obstacle approximation; full 3D collision checks remain mandatory",
                           "No motor torque, load, horn flexure, binding or printable fit verification",
                           "Multiple inverse-kinematic branches require continuous actuator path validation",
                           "No real measurements means no physical or operational approval"]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v351_rudder_kinematics.py input.json")
    p=Path(sys.argv[1]);result=solve(json.loads(p.read_text(encoding="utf-8")))
    target=p.with_name(p.stem+"_v351_kinematics.json")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(target,"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
