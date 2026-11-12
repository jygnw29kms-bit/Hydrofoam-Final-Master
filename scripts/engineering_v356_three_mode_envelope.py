"""Hydrofoam v356: measured three-mode foil clearance and CG mass budget gate.

Usage: python scripts/engineering_v356_three_mode_envelope.py measurements.json
All dimensions mm, masses grams. This is a conservative design screen only.
No numerical defaults for unknown dimensions; missing evidence always fails.
"""
import json, math, sys
from pathlib import Path

def finite(x, name):
    if type(x) not in (int,float) or not math.isfinite(x):
        raise ValueError(name+" must be finite numeric")
    return float(x)

def vec(x,name):
    if not isinstance(x,list) or len(x)!=3: raise ValueError(name+" needs [x,y,z]")
    return [finite(v,name) for v in x]

def evaluate(d):
    result={"version":"v356","release_accepted":False,"screen_pass":False,"checks":{},"missing":[]}
    needed=["components","land_configurations","flight_cg_limits_mm","maximum_takeoff_mass_g"]
    for k in needed:
        if k not in d:result["missing"].append(k)
    if result["missing"]:return result
    components=d["components"]
    if not isinstance(components,list) or not components:raise ValueError("components required")
    total=0.0; moment=[0.0]*3
    for i,c in enumerate(components):
        mass=finite(c["mass_g"],f"components[{i}].mass_g")
        if mass<=0:raise ValueError("component masses must be positive")
        p=vec(c["cg_mm"],f"components[{i}].cg_mm")
        total+=mass
        for axis in range(3):moment[axis]+=mass*p[axis]
    cg=[v/total for v in moment]
    limits=d["flight_cg_limits_mm"]
    if len(limits)!=3:raise ValueError("flight_cg_limits_mm must have 3 axis ranges")
    within=all(len(pair)==2 and finite(pair[0],"min")<=cg[i]<=finite(pair[1],"max")
               for i,pair in enumerate(limits))
    maxmass=finite(d["maximum_takeoff_mass_g"],"maximum_takeoff_mass_g")
    result["mass"]={"total_g":round(total,3),"cg_mm":[round(v,3) for v in cg],
                    "limit_g":maxmass,"flight_cg_in_limits":within}
    result["checks"]["mass_and_flight_cg"]=total<=maxmass and within
    # Foil and propeller clearances are *measured at worst attitude*, not inferred
    # from a static Blender bounding box or ideal flat runway.
    configurations=d["land_configurations"]
    expected={"hard","short_grass","firm_sand"}
    seen=set()
    for c in configurations:
        name=c["surface"]
        if name not in expected or name in seen:raise ValueError("unexpected or duplicate surface")
        seen.add(name)
        foil=finite(c["minimum_foil_ground_clearance_mm"],"foil clearance")
        prop=finite(c["minimum_propeller_ground_clearance_mm"],"prop clearance")
        grass=finite(c["measured_obstacle_height_mm"],"obstacle")
        sink=finite(c["measured_skid_sinkage_mm"],"sinkage")
        flex=finite(c["measured_maximum_deflection_mm"],"deflection")
        reserve=finite(c["required_clearance_reserve_mm"],"reserve")
        if min(grass,sink,flex,reserve)<0:raise ValueError("nonnegative allowances required")
        effective_foil=foil-grass-sink-flex
        effective_prop=prop-grass-sink-flex
        result["checks"]["land_"+name]=effective_foil>=reserve and effective_prop>=reserve
        result.setdefault("land",{})[name]={"effective_foil_mm":round(effective_foil,3),
            "effective_prop_mm":round(effective_prop,3),"reserve_mm":reserve,
            "screen_pass":result["checks"]["land_"+name]}
    result["missing"]=["land_configuration_"+n for n in sorted(expected-seen)]
    result["screen_pass"]=not result["missing"] and all(result["checks"].values())
    result["limitations"]=["Input must come from measured built hardware in each configuration.",
       "No land traction, waterproofing, foil lift, thrust or flight approval.",
       "No extrapolation of one surface test to other surfaces.",
       "No master-image similarity or rudder collision verification."]
    return result

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python engineering_v356_three_mode_envelope.py measurements.json")
    src=Path(sys.argv[1])
    try:
        output=evaluate(json.loads(src.read_text(encoding="utf-8")))
    except (ValueError,TypeError,KeyError) as exc:
        output={"version":"v356","screen_pass":False,"release_accepted":False,"error":str(exc)}
    dest=src.with_name(src.stem+"_v356_envelope_QA.json")
    dest.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print(dest,"screen_pass:",output["screen_pass"])
    if not output["screen_pass"]:sys.exit(2)
