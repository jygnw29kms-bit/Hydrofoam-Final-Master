"""v348: exact sampled rod-to-obstacle clearance screening (millimetres).

Checks a moving pushrod segment against a triangulated *fixed* obstacle mesh
using point-triangle and segment-segment distances. Coordinates must be in a
single shared CAD frame. This is a geometric screening tool, NOT a flight,
printability or mechanical acceptance. The full actuator and horn geometry
still needs BVH collision testing, physical clearances and real servo tests.

Input JSON:
{
 "rod_radius_mm": 1.0, "required_clearance_mm": 0.5,
 "rod_positions": [{"angle_deg": -15, "a_mm": [..], "b_mm": [..]}, ...],
 "obstacles": [{"name":"wing", "triangles_mm": [[[..],[..],[..]], ...]}],
 "required_angles_deg": [-15,0,15]
}
Missing required angles or geometry always fail closed.
"""
import json
import math
import sys
from pathlib import Path

EPS = 1e-12

def vec(p):
    if not isinstance(p, (list,tuple)) or len(p)!=3 or any(type(v) not in (float,int) or not math.isfinite(v) for v in p):
        raise ValueError("3 finite coordinates required")
    return tuple(float(v) for v in p)

def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,k): return tuple(x*k for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def cross(a,b): return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm2(a): return dot(a,a)
def clamp(x): return max(0.,min(1.,x))

def point_segment(p,a,b):
    ab=sub(b,a)
    t=clamp(dot(sub(p,a),ab)/norm2(ab)) if norm2(ab)>EPS else 0.
    return math.sqrt(norm2(sub(p,add(a,mul(ab,t)))))

def segment_segment(a,b,c,d):
    u=sub(b,a);v=sub(d,c);w=sub(a,c)
    A=dot(u,u);B=dot(u,v);C=dot(v,v);D=dot(u,w);E=dot(v,w)
    if A<EPS:return point_segment(a,c,d)
    if C<EPS:return point_segment(c,a,b)
    den=A*C-B*B
    s=clamp((B*E-C*D)/den) if den>EPS else 0.
    t=clamp((B*s+E)/C)
    s=clamp((B*t-D)/A)
    t=clamp((B*s+E)/C)
    return math.sqrt(norm2(sub(add(a,mul(u,s)),add(c,mul(v,t)))))

def point_triangle(p,a,b,c):
    # Ericson closest-point regions, with degenerate fallback.
    ab=sub(b,a);ac=sub(c,a);ap=sub(p,a)
    d1=dot(ab,ap);d2=dot(ac,ap)
    if d1<=0 and d2<=0:return math.sqrt(norm2(ap))
    bp=sub(p,b);d3=dot(ab,bp);d4=dot(ac,bp)
    if d3>=0 and d4<=d3:return math.sqrt(norm2(bp))
    vc=d1*d4-d3*d2
    if vc<=0 and d1>=0 and d3<=0:return point_segment(p,a,b)
    cp=sub(p,c);d5=dot(ab,cp);d6=dot(ac,cp)
    if d6>=0 and d5<=d6:return math.sqrt(norm2(cp))
    vb=d5*d2-d1*d6
    if vb<=0 and d2>=0 and d6<=0:return point_segment(p,a,c)
    va=d3*d6-d5*d4
    if va<=0 and d4-d3>=0 and d5-d6>=0:return point_segment(p,b,c)
    n=cross(ab,ac)
    if norm2(n)<EPS:return min(point_segment(p,a,b),point_segment(p,a,c),point_segment(p,b,c))
    return abs(dot(ap,n))/math.sqrt(norm2(n))

def segment_triangle(a,b,p,q,r):
    direction=sub(b,a);normal=cross(sub(q,p),sub(r,p))
    den=dot(normal,direction)
    if abs(den)>EPS:
        t=dot(normal,sub(p,a))/den
        if 0<=t<=1:
            hit=add(a,mul(direction,t))
            e0=cross(sub(q,p),sub(hit,p))
            e1=cross(sub(r,q),sub(hit,q))
            e2=cross(sub(p,r),sub(hit,r))
            if all(dot(normal,e)>=-1e-9 for e in (e0,e1,e2)):return 0.
    return min(point_triangle(a,p,q,r),point_triangle(b,p,q,r),
               segment_segment(a,b,p,q),segment_segment(a,b,q,r),segment_segment(a,b,r,p))

def run(data):
    required=("rod_radius_mm","required_clearance_mm","rod_positions","obstacles","required_angles_deg")
    missing=[k for k in required if k not in data]
    if missing:return {"accepted":False,"missing_inputs":missing}
    radius=float(data["rod_radius_mm"]);clearance=float(data["required_clearance_mm"])
    if not all(math.isfinite(x) and x>=0 for x in (radius,clearance)):raise ValueError("invalid radii")
    angles=[float(x) for x in data["required_angles_deg"]]
    if not angles or not all(math.isfinite(x) for x in angles):raise ValueError("required angle set empty or invalid")
    poses=data["rod_positions"];obstacles=data["obstacles"]
    if not poses or not obstacles: return {"accepted":False,"reason":"missing pose or obstacle mesh"}
    if any(not o.get("triangles_mm") for o in obstacles):return {"accepted":False,"reason":"empty obstacle mesh"}
    actual=[float(p["angle_deg"]) for p in poses]
    absent=[x for x in angles if not any(abs(x-y)<1e-6 for y in actual)]
    if absent:return {"accepted":False,"missing_angles_deg":absent}
    rows=[]
    for pose in poses:
        a=vec(pose["a_mm"]);b=vec(pose["b_mm"])
        if norm2(sub(a,b))<EPS:raise ValueError("zero-length rod")
        best=(math.inf,None)
        for obstacle in obstacles:
            for triangle in obstacle["triangles_mm"]:
                if len(triangle)!=3:raise ValueError("triangle must have 3 vertices")
                d=segment_triangle(a,b,*[vec(v) for v in triangle])
                if d<best[0]:best=(d,obstacle.get("name","unnamed"))
        margin=best[0]-radius-clearance
        rows.append({"angle_deg":float(pose["angle_deg"]),"nearest_obstacle":best[1],
                     "surface_gap_mm":round(best[0]-radius,6),"margin_mm":round(margin,6),
                     "clearance_pass":margin>=-1e-8})
    return {"accepted":False,"geometric_screen_pass":all(r["clearance_pass"] for r in rows),
            "mechanical_acceptance":False,"physical_validation_required":True,"samples":rows,
            "limitations":["Only sampled rod centreline vs fixed triangles",
                           "No servo-body/horn/hinge collisions",
                           "No continuous sweep guarantee or mechanical-load proof"]}

def main():
    if len(sys.argv)!=3:raise SystemExit("usage: python engineering_v348_rod_mesh_clearance.py input.json output.json")
    result=run(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__":main()
