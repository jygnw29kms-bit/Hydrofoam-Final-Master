"""v393: Conservative tri-mode mass/CG and clearance gate. No invented dimensions.
Usage: python scripts/v393_trim_gate.py measured_inputs.json --output qa_runs/v393_trim.json
All distances in mm, mass g, thrust N. Missing measurements FAIL closed.
"""
import argparse, json, math
from pathlib import Path

def finite(v):
    return isinstance(v,(float,int)) and not isinstance(v,bool) and math.isfinite(v)

def gate(data):
    failures=[]
    parts=data.get("parts",[])
    if not parts: failures.append("Missing measured parts mass ledger")
    total=mx=my=mz=0.
    for i,p in enumerate(parts):
        vals=[p.get(k) for k in ("mass_g","x_mm","y_mm","z_mm")]
        if not all(finite(v) for v in vals) or vals[0]<=0:
            failures.append(f"Part {i} missing/invalid measured mass or CG");continue
        m,x,y,z=vals
        total+=m;mx+=m*x;my+=m*y;mz+=m*z
    cg=[mx/total,my/total,mz/total] if total else None
    envelope=data.get("cg_limits_mm",{})
    if cg:
        for axis,value in zip("xyz",cg):
            bounds=envelope.get(axis)
            if not isinstance(bounds,list) or len(bounds)!=2 or not all(finite(v) for v in bounds) or bounds[0]>bounds[1]:
                failures.append(f"Missing validated {axis} CG envelope")
            elif not bounds[0]<=value<=bounds[1]:failures.append(f"{axis} CG outside approved envelope")
    for mode in ("land","water","air"):
        item=data.get(mode,{})
        if not item.get("test_evidence_id"):
            failures.append(f"{mode}: missing distinct test evidence")
    land=data.get("land",{})
    for terrain in ("hard_ground","short_grass","bearing_sand"):
        if not land.get("surface_tests",{}).get(terrain,{}).get("pass"):
            failures.append(f"land: no passed {terrain} trial")
    for key in ("foil_ground_clearance_mm","prop_ground_clearance_mm"):
        value=land.get(key)
        if not finite(value) or value<=0:failures.append(f"land: {key} not positively measured")
    water=data.get("water",{})
    for key in ("leak_test_pass","planing_test_pass","foil_lift_test_pass"):
        if water.get(key) is not True:failures.append(f"water: {key} not proven")
    air=data.get("air",{})
    for key in ("measured_static_thrust_n","measured_flight_speed_mps","measured_stall_speed_mps"):
        if not finite(air.get(key)) or air[key]<=0:failures.append(f"air: {key} missing")
    if finite(air.get("measured_flight_speed_mps")) and finite(air.get("measured_stall_speed_mps")) and air["measured_flight_speed_mps"]<=air["measured_stall_speed_mps"]:
        failures.append("air: speed not above stall")
    for key in ("controls_verified","aero_stability_verified","flight_test_pass"):
        if air.get(key) is not True:failures.append(f"air: {key} not proven")
    return {"passed":not failures,"total_mass_g":total if total else None,"cg_mm":dict(zip("xyz",cg)) if cg else None,"failures":failures,"scope":"evidence gate, not a simulation or certification"}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("input",type=Path);p.add_argument("--output",type=Path)
    a=p.parse_args()
    result=gate(json.loads(a.input.read_text(encoding="utf-8")))
    text=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text,encoding="utf-8")
    print(text)
    raise SystemExit(0 if result["passed"] else 1)
if __name__=="__main__":main()
