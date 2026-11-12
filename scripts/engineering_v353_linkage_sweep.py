"""v353: fail-closed control linkage sweep geometry audit (standard-library only).

Input JSON contains controls with hinge endpoints, moving horn pivot point at
zero deflection, servo pivot, servo arm radius, pushrod length and commanded
deflections. Coordinates are millimetres in one common body frame. The servo
is modelled as a planar arm rotating around the supplied servo axis. A sampled
rod-to-servo-arm solution is sought; collision checks are conservative capsules
against explicitly supplied fixed-part spheres. This is a design-screen only,
not proof of printable integrated mechanics or a real servo's torque.
"""
import json, math, sys
from pathlib import Path

def v(a):
    if not isinstance(a,list) or len(a)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in a):
        raise ValueError("expected finite [x,y,z]")
    return tuple(float(x) for x in a)
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def add(a,b):return tuple(x+y for x,y in zip(a,b))
def mul(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def norm(a):return math.sqrt(dot(a,a))
def cross(a,b):return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def unit(a):
    n=norm(a)
    if n<1e-8:raise ValueError("zero-length axis")
    return mul(a,1/n)
def rotate(p,origin,axis,angle):
    a=unit(axis);q=sub(p,origin);t=math.radians(angle)
    return add(origin,add(add(mul(q,math.cos(t)),mul(cross(a,q),math.sin(t))),mul(a,dot(a,q)*(1-math.cos(t)))))
def distance_segment_point(a,b,p):
    ab=sub(b,a); d=dot(ab,ab)
    t=max(0,min(1,dot(sub(p,a),ab)/d)) if d>1e-12 else 0
    return norm(sub(p,add(a,mul(ab,t))))
def run(data):
    if not isinstance(data.get("controls"),list) or not data["controls"]:
        return {"version":"v353","accepted":False,"screen_pass":False,"missing_inputs":["controls"]}
    results=[]
    for control in data["controls"]:
        name=str(control["name"])
        h0=v(control["hinge_start_mm"]);h1=v(control["hinge_end_mm"])
        axis=unit(sub(h1,h0));horn=v(control["horn_joint_zero_mm"])
        center=v(control["servo_axis_origin_mm"]);saxis=unit(v(control["servo_axis_direction"]))
        arm_zero=v(control["servo_arm_joint_zero_mm"])
        radius=norm(sub(arm_zero,center))
        if radius<0.1:raise ValueError(name+": servo arm radius too small")
        rod=float(control["rod_length_mm"]);rod_radius=float(control["rod_radius_mm"])
        tolerance=float(control["rod_length_tolerance_mm"])
        angles=control["rudder_angles_deg"];servo_range=control["servo_range_deg"]
        if rod<=0 or rod_radius<0 or tolerance<0 or not angles or len(servo_range)!=2 or servo_range[0]>=servo_range[1]:
            raise ValueError(name+": invalid mechanical limits")
        obstacles=[(v(o["center_mm"]),float(o["radius_mm"])) for o in control.get("fixed_obstacle_spheres",[])]
        samples=[]
        for angle in angles:
            hp=rotate(horn,h0,axis,float(angle))
            candidates=[]
            lo,hi=map(float,servo_range)
            for k in range(721):
                sa=lo+(hi-lo)*k/720
                sp=rotate(arm_zero,center,saxis,sa)
                error=abs(norm(sub(hp,sp))-rod)
                if error<=tolerance:
                    clearance=min((distance_segment_point(hp,sp,c)-r-rod_radius for c,r in obstacles),default=None)
                    if clearance is None or clearance>=0:
                        candidates.append((error,sa,clearance))
            best=min(candidates) if candidates else None
            samples.append({"rudder_deg":angle,"feasible":best is not None,
                            "servo_deg":None if best is None else round(best[1],3),
                            "rod_length_error_mm":None if best is None else round(best[0],4),
                            "minimum_modeled_clearance_mm":None if best is None or best[2] is None else round(best[2],4)})
        results.append({"name":name,"screen_pass":all(s["feasible"] for s in samples),
                        "samples":samples})
    return {"version":"v353","accepted":False,"screen_pass":all(r["screen_pass"] for r in results),
            "controls":results,"limitations":["Only rod-to-spherical-obstacle clearance is checked.",
            "No hinge knuckle, horn, hull, surface or servo case mesh collision checked.",
            "Discrete angular sampling can miss collisions between steps.",
            "Not proof of actual integration, physical articulation, print tolerance or servo torque."]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v353_linkage_sweep.py input.json")
    path=Path(sys.argv[1]);result=run(json.loads(path.read_text(encoding="utf-8")))
    dest=path.with_name(path.stem+"_v353_linkage_sweep.json")
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(dest,"screen_pass",result["screen_pass"],"accepted",result["accepted"])
