"""v351: static rudder hinge axial envelope and pin length planning.

Pure Python 3; does not claim that rudder controls are installed or safe.
Input is measured dimensions, not guesses. Run:
 python scripts/engineering_v351_hinge_stack.py dimensions.json
"""
import json, math, sys
from pathlib import Path

def finite(x, name, positive=True):
    if type(x) not in (float,int) or not math.isfinite(x) or (positive and x<=0):
        raise ValueError(name+" must be finite and "+("positive" if positive else "numeric"))
    return float(x)

def evaluate(d):
    required=("knuckle_heights_mm","axial_gaps_mm","pin_length_mm",
              "pin_diameter_mm","measured_bore_diameters_mm",
              "minimum_axial_gap_mm","minimum_radial_clearance_mm")
    missing=[k for k in required if k not in d]
    if missing:
        return {"version":"v351","accepted":False,"missing_inputs":missing}
    heights=[finite(v,"knuckle height") for v in d["knuckle_heights_mm"]]
    gaps=[finite(v,"axial gap",False) for v in d["axial_gaps_mm"]]
    bores=[finite(v,"bore") for v in d["measured_bore_diameters_mm"]]
    if len(heights)<3 or len(gaps)!=len(heights)-1 or len(bores)!=len(heights):
        raise ValueError("expected 3+ knuckles, one less gap, one bore per knuckle")
    pin=finite(d["pin_length_mm"],"pin length")
    pin_d=finite(d["pin_diameter_mm"],"pin diameter")
    min_gap=finite(d["minimum_axial_gap_mm"],"minimum gap",False)
    min_rad=finite(d["minimum_radial_clearance_mm"],"minimum radial clearance",False)
    stack=sum(heights)+sum(gaps)
    axial=[g>=min_gap for g in gaps]
    radial=[(b-pin_d)/2>=min_rad for b in bores]
    checks={"pin_covers_stack":pin>=stack,"all_axial_gaps":all(axial),
            "all_radial_clearances":all(radial),"no_negative_gaps":all(g>=0 for g in gaps)}
    return {"version":"v351","accepted":False,"coupon_dimensional_screen_pass":all(checks.values()),
            "stack_height_mm":round(stack,4),"pin_overhang_mm":round(pin-stack,4),
            "radial_clearances_mm":[round((b-pin_d)/2,4) for b in bores],
            "checks":checks,"limitations":["Requires real measured bore and pin diameters.",
            "No bending, shear, print orientation or retention check.",
            "No installed rudder, servo or linkage travel verification.",
            "No Final Master image conformity or three-mode acceptance."]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v351_hinge_stack.py dimensions.json")
    source=Path(sys.argv[1])
    result=evaluate(json.loads(source.read_text(encoding="utf-8")))
    dest=source.with_name(source.stem+"_v351_hinge_stack.json")
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(dest)
