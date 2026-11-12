"""Hydrofoam v354: planar servo-to-rudder linkage kinematics, conservative screening.

Input JSON requires *measured* installed geometry in mm. A servo crank pin
rotates about servo_axis_xy; the rudder horn pin rotates about hinge_axis_xy.
A rigid pushrod of length rod_length_mm connects both pins. For each servo
angle, solve both rudder branches and select the continuous solution.
This is a geometry screening tool, not a collision, strength or flight approval.
No default fabricated geometry is supplied.
"""
import json, math, sys
from pathlib import Path

def pt(v):
    if not isinstance(v,list) or len(v)!=2 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("expected finite XY pair")
    return tuple(map(float,v))
def finite(v,name,positive=False):
    if type(v) not in (int,float) or not math.isfinite(v) or (positive and v<=0):
        raise ValueError("invalid "+name)
    return float(v)
def pin(c,r,deg,zero):
    a=math.radians(deg+zero)
    return (c[0]+r*math.cos(a),c[1]+r*math.sin(a))
def wrap(a):
    return (a+180)%360-180
def run(d):
    keys=("servo_axis_xy_mm","hinge_axis_xy_mm","servo_arm_mm","rudder_horn_mm",
          "rod_length_mm","servo_zero_deg","rudder_zero_deg","servo_angles_deg",
          "rudder_limit_deg","rod_length_tolerance_mm")
    missing=[k for k in keys if k not in d]
    if missing:return {"version":"v354","screen_pass":False,"accepted":False,"missing_inputs":missing}
    s=pt(d["servo_axis_xy_mm"]);h=pt(d["hinge_axis_xy_mm"])
    a=finite(d["servo_arm_mm"],"servo_arm_mm",True)
    b=finite(d["rudder_horn_mm"],"rudder_horn_mm",True)
    rod=finite(d["rod_length_mm"],"rod_length_mm",True)
    sz=finite(d["servo_zero_deg"],"servo_zero_deg")
    rz=finite(d["rudder_zero_deg"],"rudder_zero_deg")
    tol=finite(d["rod_length_tolerance_mm"],"rod_length_tolerance_mm")
    if tol<0:raise ValueError("negative tolerance")
    limit=finite(d["rudder_limit_deg"],"rudder_limit_deg",True)
    angles=d["servo_angles_deg"]
    if not isinstance(angles,list) or len(angles)<2:raise ValueError("need 2+ servo samples")
    previous=None;rows=[]
    for val in angles:
        angle=finite(val,"servo angle")
        p=pin(s,a,angle,sz)
        vx=p[0]-h[0];vy=p[1]-h[1];dist=math.hypot(vx,vy)
        reachable=dist>1e-9 and abs(dist-b)<=rod+tol and rod<=dist+b+tol and dist<=rod+b+tol
        if not reachable:
            rows.append({"servo_deg":angle,"reachable":False,"rudder_deg":None,"screen_pass":False})
            continue
        # Solve |h + b*u(theta) - p| = rod, with u unit vector.
        cosv=(dist*dist+b*b-rod*rod)/(2*dist*b)
        if cosv < -1-tol/max(b,1) or cosv > 1+tol/max(b,1):
            rows.append({"servo_deg":angle,"reachable":False,"rudder_deg":None,"screen_pass":False})
            continue
        delta=math.degrees(math.acos(max(-1,min(1,cosv))))
        bearing=math.degrees(math.atan2(vy,vx))
        candidates=[wrap(bearing+delta-rz),wrap(bearing-delta-rz)]
        target=0 if previous is None else previous
        chosen=min(candidates,key=lambda q:abs(wrap(q-target)))
        actual=pin(h,b,chosen,rz)
        error=abs(math.dist(actual,p)-rod)
        passed=abs(chosen)<=limit+1e-7 and error<=tol+1e-6
        rows.append({"servo_deg":angle,"reachable":True,"rudder_deg":round(chosen,5),
                     "rod_error_mm":round(error,8),"screen_pass":passed})
        previous=chosen
    return {"version":"v354","accepted":False,"screen_pass":all(x["screen_pass"] for x in rows),
            "samples":rows,"limitations":["Planar ideal rigid linkage only; no 3D collision envelope",
            "Servo spline backlash, hinge friction, print tolerances and horn strength untested",
            "No proof of integrated rudder, waterproofing, or three-mode performance"]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v354_linkage_kinematics.py measured.json")
    p=Path(sys.argv[1]);r=run(json.loads(p.read_text(encoding="utf-8")))
    dest=p.with_name(p.stem+"_v354_linkage.json")
    dest.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
    print(dest,"screen_pass:",r["screen_pass"])
