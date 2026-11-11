"""v351: independent hinge clearance test plan, no fabricated acceptance.

Checks nominal pin-to-hole radial gap and fork axial spacing with uncertainty
bands. Provide measured dimensions in JSON, not CAD design nominal values.
Run: python scripts/engineering_v351_hinge_fit_tolerance.py measurements.json
"""
import json,math,sys
from pathlib import Path
def positive(v,key):
    if type(v) not in (int,float) or not math.isfinite(v) or v<=0:
        raise ValueError(key+" must be a positive finite number")
    return float(v)
def run(data):
    required=("pin_diameter_mm","bore_diameter_mm","pin_diameter_uncertainty_mm",
              "bore_diameter_uncertainty_mm","moving_knuckle_height_mm",
              "fork_gap_mm","axial_measurement_uncertainty_mm",
              "minimum_radial_clearance_mm","minimum_axial_clearance_mm")
    missing=[k for k in required if k not in data]
    if missing:
        return {"version":"v351","accepted":False,"screen_pass":False,"missing_inputs":missing}
    v={k:positive(data[k],k) for k in required if k not in
       ("pin_diameter_uncertainty_mm","bore_diameter_uncertainty_mm","axial_measurement_uncertainty_mm",
        "minimum_radial_clearance_mm","minimum_axial_clearance_mm")}
    for k in ("pin_diameter_uncertainty_mm","bore_diameter_uncertainty_mm",
              "axial_measurement_uncertainty_mm","minimum_radial_clearance_mm","minimum_axial_clearance_mm"):
        x=data[k]
        if type(x) not in (int,float) or not math.isfinite(x) or x<0:
            raise ValueError(k+" must be finite and nonnegative")
        v[k]=float(x)
    radial=(v["bore_diameter_mm"]-v["bore_diameter_uncertainty_mm"]-
            v["pin_diameter_mm"]-v["pin_diameter_uncertainty_mm"])/2
    axial=(v["fork_gap_mm"]-v["moving_knuckle_height_mm"]-
           2*v["axial_measurement_uncertainty_mm"])
    passed=radial>=v["minimum_radial_clearance_mm"] and axial>=v["minimum_axial_clearance_mm"]
    return {"version":"v351","accepted":False,"screen_pass":passed,
            "worst_case_radial_clearance_mm":round(radial,4),
            "worst_case_axial_clearance_mm":round(axial,4),
            "limitations":["Measured coupon dimensions only; no loaded articulation or print strength test.",
                           "Installed rudder and servo linkage must be checked independently.",
                           "No flight, water or land acceptance."]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v351_hinge_fit_tolerance.py measurements.json")
    source=Path(sys.argv[1])
    result=run(json.loads(source.read_text(encoding="utf-8")))
    target=source.with_name(source.stem+"_v351_fit_screen.json")
    target.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(target,"screen_pass:",result["screen_pass"],"accepted:",result["accepted"])
