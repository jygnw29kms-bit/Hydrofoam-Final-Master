"""Hydrofoam v348: planar linkage feasibility solver, not a flight or mechanical approval.

Measured hinge axis, servo axis, servo arm length, horn radius and neutral
pushrod length are required. Coordinates in mm, angles in degrees. Both axes
must be parallel and all points lie in one measured linkage plane. The servo
crank is solved for each control deflection using circle-circle intersections.
No fabricated CAD dimensions, no implicit pass for missing values.
Usage: python scripts/engineering_v348_linkage_sweep.py measurements.json report.json
"""
import json, math, sys
from pathlib import Path

def xy(p):
    if not isinstance(p, list) or len(p)!=2 or any(type(v) not in (float,int) or not math.isfinite(v) for v in p):
        raise ValueError("expected finite [x,y] in mm")
    return [float(v) for v in p]

def rotate(v, angle):
    t=math.radians(angle)
    return [v[0]*math.cos(t)-v[1]*math.sin(t),v[0]*math.sin(t)+v[1]*math.cos(t)]

def add(a,b): return [a[0]+b[0],a[1]+b[1]]
def sub(a,b): return [a[0]-b[0],a[1]-b[1]]
def norm(a): return math.hypot(*a)
def wrap(deg): return (deg+180)%360-180

def servo_solutions(axis, arm_radius, horn, rod_length):
    delta=sub(horn,axis); d=norm(delta)
    if d<1e-9 or d>arm_radius+rod_length+1e-8 or d<abs(arm_radius-rod_length)-1e-8:
        return []
    along=(arm_radius**2-rod_length**2+d*d)/(2*d)
    h2=arm_radius**2-along**2
    if h2 < -1e-7:return []
    h=math.sqrt(max(0,h2)); ux,uy=delta[0]/d,delta[1]/d
    return [math.degrees(math.atan2(along*uy+s*h*ux,along*ux-s*h*uy)) for s in (-1,1)]

def analyze(d):
    mandatory=["surface_id","hinge_axis_mm","servo_axis_mm","horn_offset_neutral_mm",
               "servo_arm_radius_mm","rod_length_mm","neutral_servo_angle_deg",
               "control_deflections_deg","servo_limits_deg","minimum_transmission_angle_deg"]
    missing=[k for k in mandatory if k not in d]
    if missing:return {"accepted":False,"missing_inputs":missing}
    hinge=xy(d["hinge_axis_mm"]); servo=xy(d["servo_axis_mm"]); horn=xy(d["horn_offset_neutral_mm"])
    radius=float(d["servo_arm_radius_mm"]); rod=float(d["rod_length_mm"])
    neutral=float(d["neutral_servo_angle_deg"])
    limits=d["servo_limits_deg"]; deflections=d["control_deflections_deg"]
    min_trans=float(d["minimum_transmission_angle_deg"])
    if radius<=0 or rod<=0 or len(limits)!=2 or not limits[0]<limits[1] or not deflections:
        raise ValueError("invalid radii, servo limits or sweep")
    if any(not math.isfinite(float(x)) for x in [radius,rod,neutral,min_trans,*limits,*deflections]):
        raise ValueError("non-finite measurements")
    if not 0<=min_trans<=90:raise ValueError("invalid transmission threshold")
    rows=[]; failures=[]
    for deg in deflections:
        horn_point=add(hinge,rotate(horn,float(deg)))
        sols=servo_solutions(servo,radius,horn_point,rod)
        # Track the measured neutral branch rather than jumping to another assembly mode.
        candidates=sorted(sols,key=lambda a:abs(wrap(a-neutral)))
        angle=candidates[0] if candidates else None
        if angle is None:
            failures.append(f"{deg}: linkage unreachable")
            rows.append({"deflection_deg":deg,"reachable":False})
            continue
        crank=add(servo,rotate([radius,0],angle))
        rodvec=sub(horn_point,crank); crankvec=sub(crank,servo)
        cosine=max(-1,min(1,(rodvec[0]*crankvec[0]+rodvec[1]*crankvec[1])/(rod*radius)))
        transmission=math.degrees(math.acos(abs(cosine)))
        within=limits[0]<=wrap(angle-neutral)<=limits[1]
        if not within:failures.append(f"{deg}: servo limit exceeded")
        if transmission<min_trans:failures.append(f"{deg}: near toggle / poor transmission")
        rows.append({"deflection_deg":deg,"servo_angle_deg":angle,
                     "servo_offset_deg":wrap(angle-neutral),"transmission_angle_deg":transmission,
                     "servo_within_limits":within,"reachable":True})
    return {"accepted":False,"geometric_screen_pass":not failures,
            "surface_id":d["surface_id"],"results":rows,"failures":failures,
            "limitations":["2D parallel-axis model only","no mesh collision verification",
                           "no servo torque/load verification","no printable hinge verification",
                           "no physical actuation test"]}

def main():
    if len(sys.argv)!=3:raise SystemExit("usage: script measurements.json report.json")
    result=analyze(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"geometric_screen_pass":result.get("geometric_screen_pass",False),
                      "accepted":False,"report":sys.argv[2]}))

if __name__=="__main__":main()
