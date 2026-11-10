"""v348: actual horn/pushrod travel and servo geometry screening (millimetres).
Independent, conservative geometric calculation; NOT a flight or hardware approval.
Inputs are measured hinge/servo geometry, not inferred from the reference photograph.
Run: python scripts/engineering_v348_control_kinematics.py geometry.json
"""
import json, math, sys
from pathlib import Path

def vec(v):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("3 finite coordinates required")
    return tuple(map(float,v))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(a): return math.sqrt(dot(a,a))
def unit(a):
    n=norm(a)
    if n<1e-9: raise ValueError("zero axis")
    return tuple(x/n for x in a)
def rotate(p,origin,axis,degrees):
    u=unit(axis); v=sub(p,origin); t=math.radians(degrees)
    c=math.cos(t); s=math.sin(t); w=cross(u,v)
    return add(origin,tuple(v[i]*c+w[i]*s+u[i]*dot(u,v)*(1-c) for i in range(3)))
def positive(d,key):
    v=d[key]
    if type(v) not in (int,float) or not math.isfinite(v) or v<=0: raise ValueError(key+" must be positive")
    return float(v)
def run(d):
    required=["controls","rod_length_tolerance_mm","minimum_clearance_mm"]
    missing=[k for k in required if k not in d]
    if missing:return {"version":"v348","accepted":False,"screen_pass":False,"missing_inputs":missing}
    tolerance=positive(d,"rod_length_tolerance_mm")
    clearance=positive(d,"minimum_clearance_mm")
    if not isinstance(d["controls"],list) or not d["controls"]:raise ValueError("controls must be nonempty")
    results=[]
    for c in d["controls"]:
        name=c["name"]
        h0=vec(c["hinge_origin_mm"]); ha=unit(vec(c["hinge_axis"]))
        s0=vec(c["servo_axis_origin_mm"]); sa=unit(vec(c["servo_axis"]))
        horn=vec(c["control_horn_joint_mm"]); servo=vec(c["servo_horn_joint_mm"])
        angles=c["surface_angles_deg"]; servo_angles=c["servo_angles_deg"]
        if len(angles)!=len(servo_angles) or len(angles)<3:raise ValueError(name+": paired angle samples >=3 required")
        if any(type(x) not in (int,float) or not math.isfinite(x) or abs(x)>90 for x in angles+servo_angles):
            raise ValueError(name+": invalid angle")
        if 0 not in angles or 0 not in servo_angles:raise ValueError(name+": zero neutral samples required")
        rod=positive(c,"nominal_rod_length_mm")
        joint_radius=positive(c,"joint_clearance_radius_mm")
        rows=[]
        for a,b in zip(angles,servo_angles):
            p=rotate(horn,h0,ha,a); q=rotate(servo,s0,sa,b)
            length=norm(sub(p,q))
            # Collision screen: moving joint balls cannot overlap; this does not
            # test rod/structure collision or servo torque.
            joint_gap=length-2*joint_radius
            rows.append({"surface_deg":a,"servo_deg":b,"joint_distance_mm":round(length,4),
                         "rod_length_error_mm":round(length-rod,4),
                         "joint_gap_mm":round(joint_gap,4),
                         "screen_pass":abs(length-rod)<=tolerance and joint_gap>=clearance})
        results.append({"name":name,"screen_pass":all(x["screen_pass"] for x in rows),
                        "samples":rows})
    return {"version":"v348","accepted":False,
            "screen_pass":all(x["screen_pass"] for x in results),
            "controls":results,
            "limitations":["Independent joint geometry only; no mechanical CAD integration established.",
                           "No rod-to-airframe, horn-to-hull, hinge-knuckle, or servo body collision tested.",
                           "No torque, stiffness, print-fit, linkage buckling, or flight proof.",
                           "Servo and control-surface angles must be paired by measured linkage motion, not guessed."]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v348_control_kinematics.py geometry.json")
    source=Path(sys.argv[1]); result=run(json.loads(source.read_text(encoding="utf-8")))
    target=source.with_name(source.stem+"_v348_kinematics.json")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(str(target),"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
