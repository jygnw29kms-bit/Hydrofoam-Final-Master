"""v394: Deterministic planar servo-horn/linkage kinematics feasibility gate.
Engineering sizing tool, NOT installed flight controls or physical acceptance.
Units: mm, degrees. Input JSON describes measured pivot and horn geometry.
Usage: python scripts/v394_linkage_geometry_gate.py geometry.json --output qa_runs/v394_linkage.json
"""
import argparse
import json
import math
from pathlib import Path

def point(origin, radius, degrees):
    t = math.radians(degrees)
    return (origin[0] + radius * math.cos(t), origin[1] + radius * math.sin(t))

def distance(a, b):
    return math.hypot(a[0]-b[0], a[1]-b[1])

def intersection(a, ar, b, br):
    """Two circles; return both possible horn-tip positions."""
    d = distance(a, b)
    if d < 1e-9 or d > ar+br or d < abs(ar-br):
        return []
    u = ((b[0]-a[0])/d, (b[1]-a[1])/d)
    x = (ar*ar-br*br+d*d)/(2*d)
    h = math.sqrt(max(0.0, ar*ar-x*x))
    p = (a[0]+x*u[0], a[1]+x*u[1])
    return [(p[0]-h*u[1],p[1]+h*u[0]),
            (p[0]+h*u[1],p[1]-h*u[0])]

def angle(p, origin):
    return math.degrees(math.atan2(p[1]-origin[1],p[0]-origin[0]))

def wrap(x):
    return (x+180)%360-180

def evaluate(cfg):
    errors = []
    try:
        servo = tuple(float(v) for v in cfg["servo_pivot_xy_mm"])
        hinge = tuple(float(v) for v in cfg["hinge_pivot_xy_mm"])
        sr = float(cfg["servo_horn_radius_mm"])
        rr = float(cfg["rudder_horn_radius_mm"])
        rod = float(cfg["rod_pin_center_length_mm"])
        neutral_servo = float(cfg["neutral_servo_angle_deg"])
        limits = [float(v) for v in cfg["servo_angle_limits_deg"]]
        step = float(cfg.get("step_deg",1))
        minimum = float(cfg.get("minimum_transmission_angle_deg",15))
        maximum = float(cfg.get("maximum_transmission_angle_deg",165))
        if len(servo)!=2 or len(hinge)!=2 or len(limits)!=2:
            raise ValueError("pivots and limits must be pairs")
        if not all(math.isfinite(v) for v in (*servo,*hinge,sr,rr,rod,neutral_servo,*limits,step,minimum,maximum)):
            raise ValueError("non-finite input")
        if min(sr,rr,rod,step)<=0 or limits[0]>=limits[1] or not (0<minimum<maximum<180):
            raise ValueError("invalid positive lengths, sweep or transmission bounds")
        if not limits[0]<=neutral_servo<=limits[1]:
            raise ValueError("neutral servo angle outside sweep")
    except (KeyError,ValueError,TypeError) as exc:
        return {"passed":False,"failures":["invalid input: "+str(exc)],"samples":[]}
    neutral_tip = point(servo,sr,neutral_servo)
    options = intersection(hinge,rr,neutral_tip,rod)
    if not options:
        return {"passed":False,"failures":["no closed linkage at neutral"],"samples":[]}
    preferred = cfg.get("neutral_rudder_horn_angle_deg")
    if preferred is None:
        return {"passed":False,"failures":["neutral_rudder_horn_angle_deg required to select assembly branch"],"samples":[]}
    preferred = float(preferred)
    tip = min(options,key=lambda p:abs(wrap(angle(p,hinge)-preferred)))
    if abs(wrap(angle(tip,hinge)-preferred))>float(cfg.get("assembly_angle_tolerance_deg",5)):
        errors.append("neutral assembly does not match specified horn angle")
    neutral_angle = angle(tip,hinge)
    samples=[]
    count = math.ceil((limits[1]-limits[0])/step)
    if count>2000:
        return {"passed":False,"failures":["sweep exceeds 2001 samples"],"samples":[]}
    previous = tip
    for i in range(count+1):
        servo_angle = limits[0]+(limits[1]-limits[0])*i/count
        servo_tip = point(servo,sr,servo_angle)
        choices = intersection(hinge,rr,servo_tip,rod)
        if not choices:
            errors.append("linkage cannot close at %.3f deg"%servo_angle)
            continue
        candidate = min(choices,key=lambda p:distance(p,previous))
        if distance(candidate,previous)>rr*0.5:
            errors.append("possible assembly branch jump at %.3f deg"%servo_angle)
        previous = candidate
        rudder_angle = wrap(angle(candidate,hinge)-neutral_angle)
        rod_vec = (servo_tip[0]-candidate[0],servo_tip[1]-candidate[1])
        horn_vec = (candidate[0]-hinge[0],candidate[1]-hinge[1])
        dot = sum(a*b for a,b in zip(rod_vec,horn_vec))/(rod*rr)
        transmission = math.degrees(math.acos(max(-1,min(1,dot))))
        if not minimum<=transmission<=maximum:
            errors.append("poor transmission angle at %.3f deg"%servo_angle)
        samples.append({"servo_deg":round(servo_angle,4),
                        "rudder_deflection_deg":round(rudder_angle,4),
                        "transmission_deg":round(transmission,4),
                        "servo_pin_xy_mm":[round(v,4) for v in servo_tip],
                        "rudder_pin_xy_mm":[round(v,4) for v in candidate]})
    # This is 2D pin-center geometry only. No physical collision or load proof.
    required = cfg.get("required_rudder_deflection_deg")
    if not isinstance(required,list) or len(required)!=2:
        errors.append("required_rudder_deflection_deg [min,max] missing")
    elif samples:
        lo=min(s["rudder_deflection_deg"] for s in samples)
        hi=max(s["rudder_deflection_deg"] for s in samples)
        if lo>float(required[0]) or hi<float(required[1]):
            errors.append("required rudder throw not achieved")
    return {"passed":not errors,"failures":sorted(set(errors)),
            "samples":samples,"neutral_rudder_horn_angle_deg":neutral_angle,
            "scope":"2D linkage feasibility only",
            "unverified":["3D collision with airframe","servo torque and end stops",
                          "hinge loads and tolerances","actual servo installation",
                          "rod stiffness and clevis clearance","print fit and fatigue",
                          "all flight control surfaces integration"]}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("input",type=Path)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    report=evaluate(json.loads(args.input.read_text(encoding="utf-8")))
    output=json.dumps(report,indent=2,ensure_ascii=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output,encoding="utf-8")
    print(output)
    raise SystemExit(0 if report["passed"] else 1)

if __name__=="__main__":
    main()
