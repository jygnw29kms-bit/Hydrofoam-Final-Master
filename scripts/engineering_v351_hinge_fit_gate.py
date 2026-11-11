"""v351: conservative printed rudder hinge fit and sweep measurement gate.

Usage: python scripts/engineering_v351_hinge_fit_gate.py measurements.json
Requires *measured* PETG/PLA coupon sizes and rudder travel samples. A successful
dimensional screen never certifies a flight-ready linkage or installed rudder.
"""
import json,math,sys
from pathlib import Path

def finite(d,k):
    v=d.get(k)
    if type(v) not in (float,int) or not math.isfinite(v):
        raise ValueError("missing/nonfinite measured value: "+k)
    return float(v)

def run(d):
    keys=["measured_pin_diameter_mm","measured_bore_diameter_mm",
          "measured_axial_gap_left_mm","measured_axial_gap_right_mm",
          "required_min_radial_clearance_mm","required_max_radial_clearance_mm",
          "required_min_axial_gap_mm","required_max_axial_gap_mm",
          "rudder_sweep_samples_deg","rudder_collision_clearance_mm",
          "minimum_required_collision_clearance_mm"]
    missing=[k for k in keys if k not in d]
    if missing:return {"version":"v351","accepted":False,"screen_pass":False,"missing_inputs":missing}
    p=finite(d,"measured_pin_diameter_mm");b=finite(d,"measured_bore_diameter_mm")
    gl=finite(d,"measured_axial_gap_left_mm");gr=finite(d,"measured_axial_gap_right_mm")
    rmin=finite(d,"required_min_radial_clearance_mm");rmax=finite(d,"required_max_radial_clearance_mm")
    amin=finite(d,"required_min_axial_gap_mm");amax=finite(d,"required_max_axial_gap_mm")
    if p<=0 or b<=0 or not(0<=rmin<=rmax) or not(0<=amin<=amax):
        raise ValueError("invalid clearance limits")
    angles=d["rudder_sweep_samples_deg"];dist=d["rudder_collision_clearance_mm"]
    if not isinstance(angles,list) or not isinstance(dist,list) or len(angles)<3 or len(angles)!=len(dist):
        raise ValueError("sweep angles and collision clearances require >=3 paired samples")
    if any(type(a) not in (float,int) or not math.isfinite(a) or abs(a)>90 for a in angles):
        raise ValueError("invalid rudder sweep angles")
    if any(type(x) not in (float,int) or not math.isfinite(x) for x in dist):
        raise ValueError("invalid collision clearance")
    required=finite(d,"minimum_required_collision_clearance_mm")
    if required<0:raise ValueError("minimum collision clearance must be nonnegative")
    radial=(b-p)/2
    checks={"radial_fit":rmin<=radial<=rmax,
            "left_axial_gap":amin<=gl<=amax,
            "right_axial_gap":amin<=gr<=amax,
            "rudder_collision":min(dist)>=required,
            "sweep_includes_zero":any(abs(a)<1e-9 for a in angles),
            "sweep_both_directions":min(angles)<0<max(angles)}
    return {"version":"v351","accepted":False,"screen_pass":all(checks.values()),
            "checks":checks,"measured_radial_clearance_mm":radial,
            "minimum_measured_collision_clearance_mm":min(dist),
            "limitations":["Only sampled angles checked; continuous sweep and loaded servo linkage remain unverified.",
                           "No photographic master match, flight, ground, or water acceptance.",
                           "Source measurement provenance and calibration require independent inspection."]}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v351_hinge_fit_gate.py measurements.json")
    src=Path(sys.argv[1])
    result=run(json.loads(src.read_text(encoding="utf-8")))
    target=src.with_name(src.stem+"_v351_hinge_fit_WIP.json")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(target,"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
