"""Hydrofoam v357: conservative 3D pushrod-to-obstacle clearance screening.

Input JSON contains measured samples and obstacles in mm. Every sample has
rod_start_mm, rod_end_mm and servo_deg. Obstacles are spheres defined by
center_mm and radius_mm. The rod is modelled as a capsule with measured
rod_radius_mm; clearance is the minimum capsule-to-sphere separation.
This intentionally cannot certify hinge motion or arbitrary CAD mesh clearance.
No dimensions are inferred from the Final Master image.
"""
import json
import math
import sys
from pathlib import Path

def point(v):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("finite [x,y,z] in mm required")
    return tuple(map(float,v))

def nonnegative(v,name):
    if type(v) not in (int,float) or not math.isfinite(v) or v<0:
        raise ValueError(name+" must be finite and nonnegative")
    return float(v)

def segment_distance(a,b,p):
    direction=[b[i]-a[i] for i in range(3)]
    length2=sum(x*x for x in direction)
    if length2<=1e-12:raise ValueError("zero-length pushrod")
    t=max(0,min(1,sum((p[i]-a[i])*direction[i] for i in range(3))/length2))
    return math.sqrt(sum((a[i]+t*direction[i]-p[i])**2 for i in range(3)))

def run(data):
    required=("samples","obstacles","rod_radius_mm","required_clearance_mm")
    missing=[k for k in required if k not in data]
    if missing:return {"version":"v357","accepted":False,"screen_pass":False,"missing_inputs":missing}
    rod=nonnegative(data["rod_radius_mm"],"rod_radius_mm")
    clearance=nonnegative(data["required_clearance_mm"],"required_clearance_mm")
    samples=data["samples"];obstacles=data["obstacles"]
    if not isinstance(samples,list) or len(samples)<2:raise ValueError("two or more measured samples required")
    if not isinstance(obstacles,list) or not obstacles:raise ValueError("measured obstacles required")
    obs=[]
    for o in obstacles:
        if not isinstance(o,dict) or not isinstance(o.get("name"),str) or not o["name"]:raise ValueError("named obstacle required")
        obs.append((o["name"],point(o["center_mm"]),nonnegative(o["radius_mm"],"radius_mm")))
    rows=[]
    for s in samples:
        if not isinstance(s,dict):raise ValueError("invalid sample")
        angle=s.get("servo_deg")
        if type(angle) not in (int,float) or not math.isfinite(angle):raise ValueError("finite servo angle required")
        a=point(s["rod_start_mm"]);b=point(s["rod_end_mm"])
        measurements=[]
        for name,center,radius in obs:
            gap=segment_distance(a,b,center)-rod-radius
            measurements.append({"obstacle":name,"gap_mm":round(gap,5),"screen_pass":gap>=clearance})
        rows.append({"servo_deg":angle,"obstacles":measurements,"screen_pass":all(x["screen_pass"] for x in measurements)})
    return {"version":"v357","accepted":False,"screen_pass":all(x["screen_pass"] for x in rows),"samples":rows,
        "limitations":["Sphere approximations require conservative measured obstacle bounds.",
                       "Discrete servo samples cannot prove clearance between samples.",
                       "Does not check rudder body, servo horn, hinge, water sealing or load.",
                       "Not a CAD collision, physical actuation, land, water or flight acceptance."]}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v357_rod_clearance.py measurements.json")
    source=Path(sys.argv[1]);result=run(json.loads(source.read_text(encoding="utf-8")))
    output=source.with_name(source.stem+"_v357_rod_clearance.json")
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(output,"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
