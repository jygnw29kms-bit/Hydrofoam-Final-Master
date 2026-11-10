"""v346: static support-polygon screening for three-mode land operation.

No geometric screening constitutes a driving, waterproofing or flight acceptance.
Measured skid contact coordinates and the installed center of mass are mandatory.
Input: JSON with surface, contacts_mm [[x,y,z],...], cg_mm [x,y,z],
pitch_deg [..], roll_deg [..], measured_sinkage_mm, minimum_margin_mm.
Angles rotate body points about the CG; gravity remains world vertical.
The support polygon is the convex hull of the XY contact projections.
"""
import json, math, sys
from pathlib import Path

def point(v):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("finite 3D coordinates required")
    return tuple(map(float,v))

def hull(points):
    p=sorted(set(points))
    if len(p)<3: return []
    def cross(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    lo=[]; hi=[]
    for q in p:
        while len(lo)>1 and cross(lo[-2],lo[-1],q)<=0:lo.pop()
        lo.append(q)
    for q in reversed(p):
        while len(hi)>1 and cross(hi[-2],hi[-1],q)<=0:hi.pop()
        hi.append(q)
    return lo[:-1]+hi[:-1]

def rotate(v,pitch,roll):
    x,y,z=v;a=math.radians(pitch);b=math.radians(roll)
    x,z=x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
    y,z=y*math.cos(b)-z*math.sin(b),y*math.sin(b)+z*math.cos(b)
    return x,y,z

def signed_margin(poly,p):
    if len(poly)<3:return None
    margins=[]
    for a,b in zip(poly,poly[1:]+poly[:1]):
        dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy)
        margins.append((dx*(p[1]-a[1])-dy*(p[0]-a[0]))/length)
    return min(margins)

def run(d):
    keys=("surface","contacts_mm","cg_mm","pitch_deg","roll_deg","measured_sinkage_mm","minimum_margin_mm")
    missing=[k for k in keys if k not in d]
    if missing:return {"accepted":False,"missing_inputs":missing}
    if d["surface"] not in ("hard","short_grass","firm_sand"):raise ValueError("invalid surface")
    contacts=[point(p) for p in d["contacts_mm"]]
    cg=point(d["cg_mm"])
    if len(contacts)<3:raise ValueError("three contacts minimum")
    for key in ("measured_sinkage_mm","minimum_margin_mm"):
        v=d[key]
        if type(v) not in (int,float) or not math.isfinite(v) or v<0:raise ValueError("nonnegative finite "+key+" required")
    for key in ("pitch_deg","roll_deg"):
        if not isinstance(d[key],list) or not d[key]:raise ValueError("nonempty angle samples required")
        if any(type(v) not in (int,float) or not math.isfinite(v) or abs(v)>90 for v in d[key]):raise ValueError("invalid angles")
    rows=[]
    for pitch in d["pitch_deg"]:
        for roll in d["roll_deg"]:
            # Rotate relative CG. A fixed CG projection at (0,0) in this coordinate system.
            projected=[rotate(tuple(p[i]-cg[i] for i in range(3)),pitch,roll) for p in contacts]
            polygon=hull([(p[0],p[1]) for p in projected])
            margin=signed_margin(polygon,(0,0))
            rows.append({"pitch_deg":pitch,"roll_deg":roll,"support_vertices":len(polygon),
                         "cg_margin_mm":None if margin is None else round(margin,3),
                         "screen_pass":margin is not None and margin>=d["minimum_margin_mm"]})
    return {"version":"v346","surface":d["surface"],"accepted":False,
            "geometry_screening_pass":all(r["screen_pass"] for r in rows),
            "worst_cg_margin_mm":min((r["cg_margin_mm"] for r in rows if r["cg_margin_mm"] is not None),default=None),
            "samples":rows,
            "limitations":["all measured contact points assumed to support load; actual active contact set under pitch/roll is not solved",
                           "sinkage is recorded but differential rutting and local soil strength are not modeled",
                           "static 2D projection only: no acceleration, friction, thrust moment, dynamic rollover or steering test",
                           "no land, water or flight operational acceptance"]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v346_support_polygon.py measurements.json")
    src=Path(sys.argv[1]);result=run(json.loads(src.read_text(encoding="utf-8")))
    target=src.with_name(src.stem+"_v346_support.json")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(target,"screen_pass:",result.get("geometry_screening_pass"),"accepted:",result["accepted"])
