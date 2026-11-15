"""v412: conservative 3D servo-linkage feasibility preflight (stdlib only).
Input: reviewed v411 config. This is NOT CAD collision or flight approval.
Run: python scripts/v412_servo_linkage_preflight.py cad/v411_mechanism_config.json
"""
import json, math, sys
from pathlib import Path

NAMES={"left_aileron","right_aileron","elevator_left","elevator_right","rudder"}
def vec(a):
    if len(a)!=3 or not all(isinstance(x,(int,float)) and math.isfinite(x) for x in a):
        raise ValueError("finite 3D vector required")
    return tuple(float(x) for x in a)
def rot_x(p,deg):
    a=math.radians(deg); x,y,z=p
    return (x,y*math.cos(a)-z*math.sin(a),y*math.sin(a)+z*math.cos(a))
def norm(a,b):
    return math.sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def solve(p):
    width=float(p["span_mm"]); chord=float(p["chord_mm"])
    horn=float(p["horn_arm_mm"]); servo=float(p["servo_arm_mm"])
    travel=float(p["travel_deg"]); pivot=vec(p["servo_pivot_local_mm"])
    if not all(math.isfinite(x) for x in (width,chord,horn,servo,travel)):
        raise ValueError("nonfinite dimension")
    if not (width>25 and chord>12 and horn>5 and servo>4 and 0<travel<=40):
        raise ValueError("dimensions outside reviewed limits")
    # v411 horn hole center, in hinge-local coordinates, as actually modeled.
    tip=(width/2,-chord*.35+3,-horn+3)
    # v411 servo output rotates about local +X; the arm starts along +Y.
    def end(angle):
        d=rot_x((0,servo,0),angle)
        return tuple(pivot[i]+d[i] for i in range(3))
    rod=norm(end(0),tip)
    if rod<5: raise ValueError("rod shorter than 5 mm")
    samples=[]
    for j in range(41):
        rud=-travel+2*travel*j/40
        target=rot_x(tip,rud)
        # Minimize residual by dense bounded servo scan, then refine around minimum.
        candidates=[(-90+180*k/720) for k in range(721)]
        best=min(candidates,key=lambda a:abs(norm(end(a),target)-rod))
        for step in (0.05,0.005):
            candidates=[best+(k-10)*step for k in range(21) if -90<=best+(k-10)*step<=90]
            best=min(candidates,key=lambda a:abs(norm(end(a),target)-rod))
        residual=abs(norm(end(best),target)-rod)
        samples.append({"rudder_deg":round(rud,3),"servo_deg":round(best,4),"rod_error_mm":round(residual,6)})
    # A fixed rod needs continuous monotone motion. Local minima are not enough:
    # reject jumps, reversal, high residual and servo angles beyond +/-60 degrees.
    angles=[s["servo_deg"] for s in samples]
    diffs=[b-a for a,b in zip(angles,angles[1:])]
    monotone=all(x>=-0.01 for x in diffs) or all(x<=0.01 for x in diffs)
    continuous=max(map(abs,diffs))<=10
    residual=max(s["rod_error_mm"] for s in samples)
    passed=monotone and continuous and residual<=.05 and max(map(abs,angles))<=60
    return {"status":"PRELIMINARY_KINEMATIC_PASS" if passed else "REJECTED",
            "nominal_rod_mm":round(rod,4),"max_rod_error_mm":residual,
            "monotone":monotone,"continuous":continuous,"samples":samples,
            "cad_collision_verified":False,"airframe_integrated":False,
            "servo_mount_verified":False,"print_verified":False}
def main():
    if len(sys.argv)!=2: raise SystemExit("usage: v412_servo_linkage_preflight.py CONFIG.json")
    path=Path(sys.argv[1]); cfg=json.loads(path.read_text(encoding="utf-8"))
    surfaces=cfg.get("surfaces",{})
    if set(surfaces)!=NAMES: raise ValueError("exactly five named control surfaces required")
    results={}
    for name in sorted(NAMES):
        try: results[name]=solve(surfaces[name])
        except (ValueError,KeyError,TypeError,OverflowError) as exc:
            results[name]={"status":"REJECTED","error":str(exc)}
    report={"version":"v412","classification":"WIP_NOT_FINAL",
            "master_image_verified":False,"land_water_air_verified":False,
            "all_kinematics_preliminary_pass":all(x["status"]=="PRELIMINARY_KINEMATIC_PASS" for x in results.values()),
            "mechanical_acceptance":False,"surfaces":results}
    output=path.parent/"v412_linkage_preflight_qa.json"
    output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(str(output))
    return 0 if report["all_kinematics_preliminary_pass"] else 2
if __name__=="__main__": sys.exit(main())
