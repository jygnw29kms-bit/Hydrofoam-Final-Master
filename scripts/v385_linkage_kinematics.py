# Hydrofoam v385: kinematic linkage sizing and swept-clearance design study.
# Independent bench fixture. Not evidence of integrated aircraft controls.
# Pure Python 3; no FreeCAD dependency for analytical geometry.
import argparse, json, math, pathlib

def circle_intersections(a, ra, b, rb):
    dx,dy=b[0]-a[0],b[1]-a[1]
    d=math.hypot(dx,dy)
    if d==0 or d>ra+rb or d<abs(ra-rb): return []
    q=(ra*ra-rb*rb+d*d)/(2*d)
    h=math.sqrt(max(0,ra*ra-q*q))
    x,y=a[0]+q*dx/d,a[1]+q*dy/d
    return [(x-h*dy/d,y+h*dx/d),(x+h*dy/d,y-h*dx/d)]

def solve():
    # All coordinates in mm, planar bench geometry.
    # Hinge at (0,0); horn radius 14; servo shaft at (38,-18).
    hinge=(0.,0.); servo=(38.,-18.); horn_r=14.; arm_r=12.
    neutral_horn=(horn_r,0.)
    candidates=circle_intersections(servo,arm_r,neutral_horn,1e-9)
    # Servo arm neutral chosen pointing toward hinge; linkage length derived.
    servo_neutral=(servo[0]-arm_r,servo[1])
    rod_len=math.dist(neutral_horn,servo_neutral)
    samples=[]
    for deg in range(-35,36,5):
        th=math.radians(deg)
        horn=(horn_r*math.cos(th),horn_r*math.sin(th))
        pts=circle_intersections(servo,arm_r,horn,rod_len)
        if not pts:
            samples.append(dict(rudder_deg=deg,reachable=False));continue
        # Consistent branch, near the neutral servo-arm endpoint.
        p=min(pts,key=lambda p:math.dist(p,servo_neutral))
        servo_deg=math.degrees(math.atan2(p[1]-servo[1],p[0]-servo[0]))
        # Segment-to-origin minimum distance is only a screening metric.
        vx,vy=p[0]-horn[0],p[1]-horn[1]
        t=max(0.,min(1.,-(horn[0]*vx+horn[1]*vy)/(vx*vx+vy*vy)))
        closest=math.hypot(horn[0]+t*vx,horn[1]+t*vy)
        samples.append(dict(rudder_deg=deg,reachable=True,
                            servo_arm_deg=round(servo_deg,3),
                            rod_to_hinge_axis_mm=round(closest,3),
                            horn_x_mm=round(horn[0],3),horn_y_mm=round(horn[1],3)))
    valid=[s for s in samples if s["reachable"]]
    # Geometry does not include actual servo case, skin, mounting screws, or three-dimensional rods.
    return dict(version="v385",classification="ANALYTICAL_BENCH_ONLY",approval="NOT_APPROVED",
        geometry_mm=dict(hinge=hinge,servo_shaft=servo,horn_radius=horn_r,
                         servo_arm_radius=arm_r,rod_center_distance=round(rod_len,4)),
        samples=samples,all_angles_reachable=len(valid)==len(samples),
        servo_sweep_deg=round(max(s["servo_arm_deg"] for s in valid)-min(s["servo_arm_deg"] for s in valid),3) if valid else None,
        minimum_rod_to_hinge_mm=min((s["rod_to_hinge_axis_mm"] for s in valid),default=None),
        limitations=["No actual aircraft hinge/servo coordinates established",
                     "No 3D solid interference or servo torque verification",
                     "No printed tolerance or mechanical fit verification",
                     "No master-image comparison; no land/water/air test"])
if __name__=="__main__":
    ap=argparse.ArgumentParser();ap.add_argument("--output",default="build/v385/linkage_study.json")
    args=ap.parse_args()
    result=solve();out=pathlib.Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="samples"},indent=2))
