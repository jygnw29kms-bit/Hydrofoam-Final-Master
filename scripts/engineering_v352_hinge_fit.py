"""v352: fail-closed hinge/pin clearance and printable-wall engineering screen.

Input JSON: {"hinges":[{"name":"left_rudder","pin_diameter_mm":2.4,
"bore_diameter_mm":2.7,"outer_diameter_mm":6.5,"knuckle_length_mm":5,
"axial_gap_mm":0.35,"pin_engagement_mm":15,"stack_length_mm":15.7,
"minimum_radial_wall_mm":1.5,"minimum_axial_gap_mm":0.2,
"maximum_axial_gap_mm":0.6,"minimum_diametral_clearance_mm":0.2,
"maximum_diametral_clearance_mm":0.5}]}
Run: python scripts/engineering_v352_hinge_fit.py input.json
This is a nominal dimensional check, not a print, fatigue, servo or movement
acceptance. It never approves any missing or non-finite measurement.
"""
import json,math,sys
from pathlib import Path
FIELDS=("pin_diameter_mm","bore_diameter_mm","outer_diameter_mm",
        "knuckle_length_mm","axial_gap_mm","pin_engagement_mm",
        "stack_length_mm","minimum_radial_wall_mm","minimum_axial_gap_mm",
        "maximum_axial_gap_mm","minimum_diametral_clearance_mm",
        "maximum_diametral_clearance_mm")
def check(hinge):
    name=hinge.get("name","unnamed")
    missing=[k for k in FIELDS if k not in hinge]
    if missing:return {"name":name,"screen_pass":False,"missing":missing}
    v={}
    for k in FIELDS:
        x=hinge[k]
        if type(x) not in (int,float) or not math.isfinite(x) or x<0:
            return {"name":name,"screen_pass":False,"error":"invalid "+k}
        v[k]=float(x)
    diameter_clearance=v["bore_diameter_mm"]-v["pin_diameter_mm"]
    radial_wall=(v["outer_diameter_mm"]-v["bore_diameter_mm"])/2
    gap=v["axial_gap_mm"]
    checks={
        "positive_pin_and_knuckle":v["pin_diameter_mm"]>0 and v["knuckle_length_mm"]>0,
        "diametral_fit":v["minimum_diametral_clearance_mm"]<=diameter_clearance<=v["maximum_diametral_clearance_mm"],
        "radial_wall":radial_wall>=v["minimum_radial_wall_mm"],
        "axial_gap":v["minimum_axial_gap_mm"]<=gap<=v["maximum_axial_gap_mm"],
        "engagement":v["pin_engagement_mm"]>=v["stack_length_mm"]
    }
    return {"name":name,"screen_pass":all(checks.values()),"checks":checks,
            "nominal_diametral_clearance_mm":round(diameter_clearance,4),
            "nominal_radial_wall_mm":round(radial_wall,4)}
def run(data):
    hinges=data.get("hinges")
    if not isinstance(hinges,list) or not hinges:
        return {"version":"v352","accepted":False,"screen_pass":False,"error":"nonempty hinges array required"}
    results=[check(h) if isinstance(h,dict) else {"screen_pass":False,"error":"hinge must be object"} for h in hinges]
    return {"version":"v352","accepted":False,"screen_pass":all(x["screen_pass"] for x in results),
            "hinges":results,"limitations":["Nominal dimensions only; print and measure PLA/PETG coupons.",
            "No verification of coaxiality, dynamic sweep, pin retention or fatigue.",
            "No linkage, servo or flight/land/water approval."]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v352_hinge_fit.py input.json")
    source=Path(sys.argv[1]);report=run(json.loads(source.read_text(encoding="utf-8")))
    dest=source.with_name(source.stem+"_v352_hinge_fit.json")
    dest.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(dest,report["screen_pass"])
    if not report["screen_pass"]:raise SystemExit(2)
