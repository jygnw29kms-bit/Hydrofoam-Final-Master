"""v414: conservative 3-D pushrod swept-clearance screening.

Coordinates are millimetres in a common, measured airframe frame. This is
a broad-phase geometry audit, not a FreeCAD solid-intersection or flight test.
Each obstacle is an axis-aligned bounding box; false positives are possible.
Do not use a PASS to authorize manufacturing or Final-Master release.
"""
import argparse
import json
import math
from pathlib import Path

def vec(value):
    if not isinstance(value, list) or len(value) != 3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in value):
        raise ValueError("Expected finite 3-vector")
    return tuple(float(x) for x in value)

def rotate_axis(point, origin, axis, degrees):
    """Rodrigues rotation about an arbitrary unit hinge axis."""
    p=vec(point); o=vec(origin); a=vec(axis)
    norm=math.sqrt(sum(x*x for x in a))
    if norm < 1e-9: raise ValueError("Zero hinge axis")
    a=tuple(x/norm for x in a)
    v=tuple(p[i]-o[i] for i in range(3))
    t=math.radians(degrees); c=math.cos(t); s=math.sin(t)
    cross=(a[1]*v[2]-a[2]*v[1],a[2]*v[0]-a[0]*v[2],a[0]*v[1]-a[1]*v[0])
    dot=sum(a[i]*v[i] for i in range(3))
    return tuple(o[i]+v[i]*c+cross[i]*s+a[i]*dot*(1-c) for i in range(3))

def segment_box_distance(p,q,lo,hi):
    """Exact minimum distance of a line segment to a closed AABB."""
    p=vec(list(p));q=vec(list(q));lo=vec(list(lo));hi=vec(list(hi))
    if any(lo[i]>hi[i] for i in range(3)): raise ValueError("Inverted AABB")
    d=[q[i]-p[i] for i in range(3)]
    cuts=[0.,1.]
    for i in range(3):
        if abs(d[i])>1e-12:
            for boundary in (lo[i],hi[i]):
                t=(boundary-p[i])/d[i]
                if 0<t<1: cuts.append(t)
    cuts=sorted(set(cuts))
    def sq(t):
        return sum((max(lo[i]-(p[i]+t*d[i]),0.,(p[i]+t*d[i])-hi[i]))**2 for i in range(3))
    best=float("inf")
    for a,b in zip(cuts,cuts[1:]):
        mid=(a+b)/2
        active=[i for i in range(3) if p[i]+mid*d[i]<lo[i] or p[i]+mid*d[i]>hi[i]]
        if active:
            targets={i:(lo[i] if p[i]+mid*d[i]<lo[i] else hi[i]) for i in active}
            den=sum(d[i]*d[i] for i in active)
            t=sum(d[i]*(targets[i]-p[i]) for i in active)/den if den>1e-15 else a
            t=max(a,min(b,t))
            best=min(best,sq(t))
        best=min(best,sq(a),sq(b))
    return math.sqrt(best)

def audit(config):
    if config.get("coordinate_frame")!="measured_airframe_mm":
        raise ValueError("Unverified coordinate frame")
    results={}
    surfaces=config.get("surfaces",{})
    expected={"left_aileron","right_aileron","elevator_left","elevator_right","rudder"}
    if set(surfaces)!=expected: raise ValueError("Five control surfaces required")
    for name,s in surfaces.items():
        origin=vec(s["hinge_origin_mm"]); axis=vec(s["hinge_axis"])
        horn=vec(s["horn_tip_neutral_mm"]); servo=vec(s["servo_arm_tip_mm"])
        rod_radius=float(s["rod_radius_mm"]); margin=float(s["required_clearance_mm"])
        travel=float(s["travel_deg"]); steps=int(s.get("steps",91))
        if not all(math.isfinite(v) for v in (rod_radius,margin,travel)) or rod_radius<=0 or margin<0 or not 0<travel<=60 or not 21<=steps<=721:
            raise ValueError("Invalid rod radius, clearance, travel or sample count")
        obstacles=s.get("obstacles",[])
        if not obstacles: raise ValueError(name+": missing measured obstacles")
        boxes=[(vec(x["min_mm"]),vec(x["max_mm"]),str(x["id"])) for x in obstacles]
        min_clear=float("inf"); failures=[]
        for j in range(steps):
            angle=-travel+2*travel*j/(steps-1)
            end=rotate_axis(horn,origin,axis,angle)
            for lo,hi,ident in boxes:
                clearance=segment_box_distance(servo,end,lo,hi)-rod_radius
                min_clear=min(min_clear,clearance)
                if clearance+1e-8<margin:
                    failures.append({"angle_deg":round(angle,4),"obstacle":ident,"clearance_mm":round(clearance,5)})
        results[name]={"status":"BROAD_PHASE_PASS" if not failures else "BROAD_PHASE_FAIL",
                       "minimum_clearance_mm":round(min_clear,5),
                       "collision_samples":len(failures),"first_failures":failures[:12]}
    return {"classification":"WIP_3D_BROAD_PHASE_ONLY","all_screens_pass":all(v["status"]=="BROAD_PHASE_PASS" for v in results.values()),
            "final_master_image_verified":False,"integrated_mechanism_verified":False,
            "land_water_air_verified":False,"limitations":["AABB obstacle approximation","Fixed servo-arm endpoint; no servo linkage solution","No CAD solids, bearings, loads or physical test","Sampled angular sweep; intermediate angles unproven"],"surfaces":results}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("config",type=Path);ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    report=audit(json.loads(args.config.read_text(encoding="utf-8")))
    result=json.dumps(report,indent=2,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(result,encoding="utf-8")
    else: print(result,end="")
    raise SystemExit(0 if report["all_screens_pass"] else 2)
if __name__=="__main__": main()
