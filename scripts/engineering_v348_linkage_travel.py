"""v348: Measured servo-horn linkage travel solver for Hydrofoam controls.

Input JSON uses millimetres and degrees. All pivots must be extracted from the
actual assembled CAD; a pass is a kinematic SCREEN, not mechanical acceptance.
A rigid pushrod links a rotating servo horn to a rotating surface horn. For
each requested surface angle the solver finds the servo angle that maintains
the measured rod length, reports endpoint error, and checks the declared servo
range. Geometry must additionally be checked for collisions and load capacity.
"""
import json
import math
import sys
from pathlib import Path


def finite(value, label):
    if type(value) not in (float, int) or not math.isfinite(value):
        raise ValueError(label + " must be finite")
    return float(value)


def vector(value, label):
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(label + " must be a 3-vector")
    return tuple(finite(x, label) for x in value)


def subtract(a, b):
    return tuple(x-y for x,y in zip(a,b))


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def norm(a):
    return math.sqrt(dot(a,a))


def unit(a, label):
    length=norm(a)
    if length < 1e-8:
        raise ValueError(label + " cannot have zero length")
    return tuple(x/length for x in a)


def rotate(point, pivot, axis, degrees):
    v=subtract(point,pivot)
    u=unit(axis,"axis")
    t=math.radians(degrees)
    c,s=math.cos(t),math.sin(t)
    cross=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
    return tuple(pivot[i]+v[i]*c+cross[i]*s+u[i]*dot(u,v)*(1-c) for i in range(3))


def distance(a,b):
    return norm(subtract(a,b))


def solve(data):
    required=("surface_pivot_mm","surface_axis","surface_horn_pin_mm",
              "servo_pivot_mm","servo_axis","servo_horn_pin_mm",
              "pushrod_pin_distance_mm","surface_angles_deg",
              "servo_limits_deg","max_length_error_mm")
    missing=[x for x in required if x not in data]
    if missing:
        return {"version":"v348","accepted":False,"screen_pass":False,"missing_inputs":missing}
    sp=vector(data["surface_pivot_mm"],"surface_pivot_mm")
    sa=unit(vector(data["surface_axis"],"surface_axis"),"surface_axis")
    sh=vector(data["surface_horn_pin_mm"],"surface_horn_pin_mm")
    vp=vector(data["servo_pivot_mm"],"servo_pivot_mm")
    va=unit(vector(data["servo_axis"],"servo_axis"),"servo_axis")
    vh=vector(data["servo_horn_pin_mm"],"servo_horn_pin_mm")
    rod=finite(data["pushrod_pin_distance_mm"],"pushrod_pin_distance_mm")
    errmax=finite(data["max_length_error_mm"],"max_length_error_mm")
    if rod<=0 or errmax<0:
        raise ValueError("rod length must be positive and tolerance nonnegative")
    limits=data["servo_limits_deg"]
    if not isinstance(limits,list) or len(limits)!=2:
        raise ValueError("servo_limits_deg must be [min,max]")
    lo,hi=(finite(v,"servo limit") for v in limits)
    if lo>=hi or lo < -180 or hi > 180:
        raise ValueError("invalid servo travel limits")
    angles=data["surface_angles_deg"]
    if not isinstance(angles,list) or len(angles)<2:
        raise ValueError("at least two surface angles required")
    angles=[finite(a,"surface angle") for a in angles]
    if any(abs(a)>90 for a in angles):
        raise ValueError("surface angle outside +/-90 degrees")
    if norm(subtract(sh,sp))<1e-6 or norm(subtract(vh,vp))<1e-6:
        raise ValueError("horn pin must be offset from its pivot")
    rows=[]
    for angle in angles:
        target=rotate(sh,sp,sa,angle)
        # Bracket candidates by sampling, then minimize absolute rod-length error.
        samples=720
        def error(deg):
            return distance(target,rotate(vh,vp,va,deg))-rod
        grid=[lo+(hi-lo)*i/samples for i in range(samples+1)]
        candidates=[]
        for i in range(samples):
            a,b=grid[i],grid[i+1]
            fa,fb=error(a),error(b)
            if fa==0:
                candidates.append(a)
            if fa*fb<0:
                for _ in range(48):
                    mid=(a+b)/2
                    if error(a)*error(mid)<=0:
                        b=mid
                    else:
                        a=mid
                candidates.append((a+b)/2)
        candidates.extend([lo,hi])
        best=min(candidates,key=lambda t:abs(error(t)))
        deviation=abs(error(best))
        rows.append({"surface_deg":angle,"servo_deg":round(best,5),
                     "pushrod_length_error_mm":round(deviation,6),
                     "screen_pass":deviation<=errmax})
    return {"version":"v348","accepted":False,
            "screen_pass":all(row["screen_pass"] for row in rows),
            "samples":rows,
            "limitations":["Only exact rigid-pin distance and servo angle range are screened.",
                           "No collision, rod buckling, joint articulation, servo torque or structural integrity proof.",
                           "Pin/pivot coordinates must be extracted from assembled CAD, not conceptual sketches.",
                           "Both travel directions and all installed control surfaces require separate runs."]}


if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("usage: python scripts/engineering_v348_linkage_travel.py input.json")
    source=Path(sys.argv[1])
    result=solve(json.loads(source.read_text(encoding="utf-8")))
    output=source.with_name(source.stem+"_v348_linkage_screen.json")
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(output,"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
