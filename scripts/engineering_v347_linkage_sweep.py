"""v347: planar servo-horn/pushrod linkage sweep with strict evidence gating.

Input JSON: pivot_mm, horn_radius_mm, servo_center_mm, servo_arm_radius_mm,
servo_zero_deg, servo_angles_deg, horn_zero_deg, horn_range_deg,
rod_length_mm, rod_length_tolerance_mm, linkage_plane_tolerance_mm.
All positions are in a single measured linkage plane; degrees use mathematical
CCW convention. Solves output angle by minimizing rod-length residual over
horn_range_deg; requires continuity and an unambiguous branch. This is NOT
a 3D collision, strength, or physical clearance certification.
"""
import json, math, sys
from pathlib import Path

def finite(x):
    if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x):
        raise ValueError("finite number required")
    return float(x)

def xy(v):
    if not isinstance(v,list) or len(v)!=2: raise ValueError("2D coordinate required")
    return tuple(map(finite,v))

def arm(center,radius,angle):
    a=math.radians(angle)
    return (center[0]+radius*math.cos(a),center[1]+radius*math.sin(a))

def distance(a,b): return math.hypot(a[0]-b[0],a[1]-b[1])

def candidates(pivot, radius, servo_end, rod, lo, hi):
    # Exact circle-circle intersection; filter to mechanically permitted angle range.
    dx=servo_end[0]-pivot[0];dy=servo_end[1]-pivot[1]
    d=math.hypot(dx,dy)
    if d<1e-9 or d>radius+rod+1e-8 or d<abs(radius-rod)-1e-8:return []
    along=(radius*radius-rod*rod+d*d)/(2*d)
    h2=radius*radius-along*along
    if h2 < -1e-7:return []
    h=math.sqrt(max(0,h2))
    base=(pivot[0]+along*dx/d,pivot[1]+along*dy/d)
    results=[]
    for sign in (-1,1):
        pt=(base[0]-sign*h*dy/d,base[1]+sign*h*dx/d)
        raw=math.degrees(math.atan2(pt[1]-pivot[1],pt[0]-pivot[0]))
        for k in range(math.floor((lo-raw)/360)-1,math.ceil((hi-raw)/360)+2):
            angle=raw+360*k
            if lo-1e-7<=angle<=hi+1e-7 and all(abs(angle-q)>1e-6 for q in results):
                results.append(angle)
    return sorted(results)

def run(d):
    required=["pivot_mm","horn_radius_mm","servo_center_mm","servo_arm_radius_mm",
              "servo_zero_deg","servo_angles_deg","horn_zero_deg","horn_range_deg",
              "rod_length_mm","rod_length_tolerance_mm","linkage_plane_tolerance_mm"]
    missing=[k for k in required if k not in d]
    if missing:return {"accepted":False,"missing_inputs":missing}
    pivot=xy(d["pivot_mm"]);center=xy(d["servo_center_mm"])
    hr=finite(d["horn_radius_mm"]);sr=finite(d["servo_arm_radius_mm"])
    rod=finite(d["rod_length_mm"]);tol=finite(d["rod_length_tolerance_mm"])
    plane_tol=finite(d["linkage_plane_tolerance_mm"])
    zero=finite(d["servo_zero_deg"]);hz=finite(d["horn_zero_deg"])
    if min(hr,sr,rod)<=0 or min(tol,plane_tol)<0:raise ValueError("invalid lengths")
    rng=d["horn_range_deg"]
    if not isinstance(rng,list) or len(rng)!=2:raise ValueError("horn range [min,max]")
    lo,hi=map(finite,rng)
    if not lo<hi or hi-lo>=360:raise ValueError("invalid horn range")
    angles=d["servo_angles_deg"]
    if not isinstance(angles,list) or len(angles)<3:raise ValueError("at least 3 servo samples")
    angles=[finite(x) for x in angles]
    if any(b<=a for a,b in zip(angles,angles[1:])):raise ValueError("servo angles must increase")
    samples=[];previous=None;ambiguity=False
    for a in angles:
        end=arm(center,sr,zero+a)
        opts=candidates(pivot,hr,end,rod,lo,hi)
        if previous is None:
            chosen=min(opts,key=lambda v:abs(v-hz)) if opts else None
            if len(opts)>1:ambiguity=True
        else:
            chosen=min(opts,key=lambda v:abs(v-previous)) if opts else None
            if len(opts)>1 and abs(abs(opts[0]-previous)-abs(opts[-1]-previous))<1e-5:
                ambiguity=True
        residual=distance(arm(pivot,hr,chosen),end)-rod if chosen is not None else None
        samples.append({"servo_deg":a,"horn_deg":chosen,"rod_residual_mm":residual,
                        "solution_count":len(opts)})
        if chosen is not None:previous=chosen
    valid=all(s["horn_deg"] is not None and abs(s["rod_residual_mm"])<=tol for s in samples)
    jumps=any(abs(b["horn_deg"]-a["horn_deg"])>15 for a,b in zip(samples,samples[1:])
              if a["horn_deg"] is not None and b["horn_deg"] is not None)
    return {"accepted":False,"planar_kinematics_solvable":valid and not ambiguity and not jumps,
            "branch_ambiguous":ambiguity,"discontinuous_samples":jumps,
            "samples":samples,"measured_3d_collisions_verified":False,
            "printed_hinge_integration_verified":False,
            "servo_mount_integration_verified":False,
            "full_3d_throw_verified":False,
            "note":"Planar screening only; physical and 3D CAD gates remain mandatory."}

def main():
    if len(sys.argv)!=3:raise SystemExit("usage: python engineering_v347_linkage_sweep.py input.json output.json")
    inp=Path(sys.argv[1]);out=Path(sys.argv[2])
    result=run(json.loads(inp.read_text(encoding="utf-8")))
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
if __name__=="__main__":main()
