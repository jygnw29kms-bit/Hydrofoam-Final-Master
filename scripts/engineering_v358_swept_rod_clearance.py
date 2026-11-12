"""v358: conservative continuous pushrod clearance certificate between measured poses.

Given consecutive endpoint poses, every intermediate endpoint must lie inside
a measured or independently validated linear-interpolation envelope plus
max_deviation_mm. For a segment-to-sphere gap the Lipschitz bound is the
maximum displacement of either endpoint. If the observed endpoint gaps are
both greater than required clearance plus half the endpoint displacement
bound plus max_deviation_mm, the entire interpolation interval is clear.
This does NOT prove that actual linkage motion follows the interpolation.
"""
import json
import math
import sys
from pathlib import Path

def p3(v):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("expected finite 3D point")
    return tuple(float(x) for x in v)

def nonneg(v):
    if type(v) not in (int,float) or not math.isfinite(v) or v<0:
        raise ValueError("expected finite nonnegative number")
    return float(v)

def distance(a,b):
    return math.dist(a,b)

def gap(a,b,c,r):
    d=tuple(b[i]-a[i] for i in range(3))
    dd=sum(x*x for x in d)
    if dd<=1e-12:raise ValueError("zero-length pushrod")
    t=max(0,min(1,sum((c[i]-a[i])*d[i] for i in range(3))/dd))
    return distance(tuple(a[i]+t*d[i] for i in range(3)),c)-r

def run(data):
    keys=("samples","obstacles","rod_radius_mm","required_clearance_mm","max_deviation_mm")
    missing=[k for k in keys if k not in data]
    if missing:return {"version":"v358","accepted":False,"screen_pass":False,"missing_inputs":missing}
    rod=nonneg(data["rod_radius_mm"]);required=nonneg(data["required_clearance_mm"])
    deviation=nonneg(data["max_deviation_mm"])
    if not data.get("interpolation_envelope_verified",False) is True:
        return {"version":"v358","accepted":False,"screen_pass":False,
                "reason":"independently verified interpolation deviation envelope required"}
    samples=data["samples"];obstacles=data["obstacles"]
    if not isinstance(samples,list) or len(samples)<2 or not isinstance(obstacles,list) or not obstacles:
        raise ValueError("at least two samples and one obstacle required")
    poses=[]
    for s in samples:
        angle=s.get("servo_deg")
        if type(angle) not in (int,float) or not math.isfinite(angle):
            raise ValueError("finite servo angle required")
        poses.append((float(angle),p3(s["rod_start_mm"]),p3(s["rod_end_mm"])))
    if len({x[0] for x in poses})!=len(poses) or any(poses[i+1][0]<=poses[i][0] for i in range(len(poses)-1)):
        raise ValueError("servo angles must be strictly increasing")
    obs=[]
    for o in obstacles:
        if not isinstance(o.get("name"),str) or not o["name"]:raise ValueError("named obstacle required")
        obs.append((o["name"],p3(o["center_mm"]),nonneg(o["radius_mm"])))
    rows=[]
    for (angle0,a0,b0),(angle1,a1,b1) in zip(poses,poses[1:]):
        displacement=max(distance(a0,a1),distance(b0,b1))
        # Nearest sampled endpoint of an interpolated pose is at most half
        # the total endpoint displacement, plus verified deviation.
        penalty=displacement/2+deviation
        for name,center,radius in obs:
            g0=gap(a0,b0,center,radius+rod)
            g1=gap(a1,b1,center,radius+rod)
            bound=min(g0,g1)-penalty
            rows.append({"servo_interval_deg":[angle0,angle1],"obstacle":name,
                         "conservative_lower_bound_mm":round(bound,5),
                         "screen_pass":bound>=required})
    return {"version":"v358","accepted":False,"screen_pass":all(r["screen_pass"] for r in rows),
            "intervals":rows,"limitations":["Requires independently verified actual-path deviation from endpoint interpolation.",
            "Sphere obstacles must conservatively enclose real CAD parts.",
            "Does not validate servo torque, hinge loads, water sealing, physical movement or flight safety."]}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python engineering_v358_swept_rod_clearance.py measurements.json")
    src=Path(sys.argv[1]);result=run(json.loads(src.read_text(encoding="utf-8")))
    out=src.with_name(src.stem+"_v358_swept_clearance.json")
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(out,result["screen_pass"],result["accepted"])
