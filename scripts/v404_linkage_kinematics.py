"""v404: planar servo-horn/pushrod kinematics audit (engineering precheck).
Coordinates in millimetres, angles in degrees. Does not replace 3D CAD collision
checking, structural tests, measured servo torque or hardware verification.
Usage: python scripts/v404_linkage_kinematics.py input.json output.json
Each surface: name, hinge_xy_mm, horn_radius_mm, horn_zero_deg,
servo_xy_mm, servo_arm_radius_mm, servo_zero_deg, servo_limits_deg [min,max],
surface_angles_deg [min,...,max], rod_length_mm, tolerance_mm.
Hinge horn rotates with surface angle; servo-arm tip follows a circle.
Find all possible servo angles satisfying fixed rod length and choose a
continuous branch from the first sample. No arbitrary servo angle accepted.
"""
import json, math, sys, pathlib

def pt(center, radius, angle):
    a=math.radians(angle)
    return (center[0]+radius*math.cos(a),center[1]+radius*math.sin(a))

def dist(a,b):
    return math.hypot(a[0]-b[0],a[1]-b[1])

def solve(s):
    required=("name","hinge_xy_mm","horn_radius_mm","horn_zero_deg",
              "servo_xy_mm","servo_arm_radius_mm","servo_zero_deg",
              "servo_limits_deg","surface_angles_deg","rod_length_mm","tolerance_mm")
    for k in required:
        if k not in s: raise ValueError("Missing "+k)
    if min(s["horn_radius_mm"],s["servo_arm_radius_mm"],s["rod_length_mm"],s["tolerance_mm"])<=0:
        raise ValueError("Nonpositive geometry")
    angles=s["surface_angles_deg"]
    if len(angles)<3 or 0 not in angles or angles!=sorted(set(angles)):
        raise ValueError("Require ordered unique sweep containing zero")
    lo,hi=s["servo_limits_deg"]
    if lo>=hi: raise ValueError("Invalid servo limits")
    center=s["servo_xy_mm"]; radius=s["servo_arm_radius_mm"]
    rows=[]; prev=None; failures=[]
    for a in angles:
        horn=pt(s["hinge_xy_mm"],s["horn_radius_mm"],s["horn_zero_deg"]+a)
        dx=horn[0]-center[0]; dy=horn[1]-center[1]
        d=math.hypot(dx,dy)
        rod=s["rod_length_mm"]
        if d<1e-9 or abs(d-radius)>rod+s["tolerance_mm"] or rod> d+radius+s["tolerance_mm"]:
            failures.append({"surface_deg":a,"reason":"unreachable linkage"});continue
        cosine=(d*d+radius*radius-rod*rod)/(2*d*radius)
        if abs(cosine)>1+1e-8:
            failures.append({"surface_deg":a,"reason":"no circle intersection"});continue
        offset=math.degrees(math.acos(max(-1,min(1,cosine))))
        direction=math.degrees(math.atan2(dy,dx))
        candidates=[]
        for sign in (-1,1):
            absolute=direction+sign*offset
            for winding in range(-2,3):
                servo=absolute+360*winding-s["servo_zero_deg"]
                if lo<=servo<=hi and all(abs(servo-x)>1e-6 for x in candidates):
                    candidates.append(servo)
        if not candidates:
            failures.append({"surface_deg":a,"reason":"servo limit exceeded"});continue
        chosen=min(candidates,key=lambda x:abs(x-prev) if prev is not None else abs(x))
        if prev is not None and abs(chosen-prev)>90:
            failures.append({"surface_deg":a,"reason":"discontinuous servo branch"})
        tip=pt(center,radius,s["servo_zero_deg"]+chosen)
        error=abs(dist(tip,horn)-rod)
        if error>s["tolerance_mm"]:
            failures.append({"surface_deg":a,"reason":"rod length error","error_mm":error})
        rows.append({"surface_deg":a,"servo_deg":round(chosen,6),"rod_error_mm":round(error,9)})
        prev=chosen
    return {"name":s["name"],"pass":not failures and len(rows)==len(angles),
            "samples":rows,"failures":failures,
            "servo_travel_deg":round(max((r["servo_deg"] for r in rows),default=0)-min((r["servo_deg"] for r in rows),default=0),6)}

def main():
    if len(sys.argv)!=3: raise SystemExit("Usage: input.json output.json")
    source=pathlib.Path(sys.argv[1]); output=pathlib.Path(sys.argv[2])
    data=json.loads(source.read_text(encoding="utf-8"))
    surfaces=data.get("surfaces")
    if not isinstance(surfaces,list) or not surfaces: raise ValueError("No surfaces")
    names=[s["name"] for s in surfaces]
    if len(names)!=len(set(names)): raise ValueError("Duplicate names")
    required=set(data.get("required_surfaces",[]))
    if not required or required!=set(names):
        raise ValueError("Required surface inventory missing or incomplete")
    results=[solve(s) for s in surfaces]
    report={"schema":"hydrofoam.v404.linkage.precheck","pass":all(r["pass"] for r in results),
            "limitations":["2D planar mechanism only","No 3D collision or structural verification",
                           "No servo torque, backlash, printed fit or actual installed CAD validation"],
            "results":results}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2),encoding="utf-8")
    if not report["pass"]: raise SystemExit(2)
if __name__=="__main__": main()
