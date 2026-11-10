"""Hydrofoam v344: conservative, input-driven three-mode feasibility gate.

Run: python scripts/audit_v344_three_mode_physics.py --inputs docs/v344_measured_inputs.json
No guessed values, no CAD mutations, no claims of flight safety.
"""
import argparse, json, math
from pathlib import Path

REQUIRED = {
 "mass_kg": "Measured all-up mass including battery, foils and landing hardware",
 "wing_area_m2": "Measured projected lifting wing area",
 "cl_max": "Defensible measured or validated maximum lift coefficient",
 "air_density_kg_m3": "Air density at test conditions",
 "thrust_N": "Measured installed static thrust",
 "ground_drag_hard_N": "Measured rolling/sliding resistance on hard ground",
 "ground_drag_grass_N": "Measured resistance on short grass",
 "ground_drag_sand_N": "Measured resistance on load-bearing sand",
 "foil_area_m2": "Total submerged foil lifting area",
 "foil_cl_operating": "Validated foil lift coefficient at selected speed",
 "water_density_kg_m3": "Water density",
 "foil_speed_m_s": "Foil takeoff target speed",
 "ground_z_mm": "Measured land contact plane in CAD coordinates",
 "lowest_foil_z_mm": "Lowest deployed foil point in same coordinates",
 "lowest_foil_stowed_z_mm": "Lowest stowed foil point in same coordinates",
 "prop_lowest_z_mm": "Lowest rotating propeller sweep point",
 "skid_wear_mm": "Measured skid wear after repeated land tests",
 "skid_wear_limit_mm": "Engineering-approved skid replacement limit",
 "water_displacement_m3": "Measured displacement at allowable waterline",
 "sealed_enclosure_test_pass": "Boolean, documented immersion/spray test",
 "control_sweep_test_pass": "Boolean, exact swept collision and linkage motion test",
 "master_three_view_match_pass": "Boolean, registered photo comparison approval"
}
G=9.80665

def positive(x,key):
 if isinstance(x,bool) or not isinstance(x,(int,float)) or not math.isfinite(x) or x<=0:
  raise ValueError(key+" must be a finite positive number")
 return float(x)

def evaluate(d):
 missing=sorted(set(REQUIRED)-set(d))
 if missing:
  return {"accepted":False,"missing":missing,"required_inputs":REQUIRED,"computed":{}}
 vals={k:positive(d[k],k) for k in REQUIRED if k in d and k not in (
  "ground_z_mm","lowest_foil_z_mm","lowest_foil_stowed_z_mm","prop_lowest_z_mm",
  "sealed_enclosure_test_pass","control_sweep_test_pass","master_three_view_match_pass")}
 for k in ("ground_z_mm","lowest_foil_z_mm","lowest_foil_stowed_z_mm","prop_lowest_z_mm"):
  if isinstance(d[k],bool) or not isinstance(d[k],(int,float)) or not math.isfinite(d[k]):
   raise ValueError(k+" must be a finite number")
 for k in ("sealed_enclosure_test_pass","control_sweep_test_pass","master_three_view_match_pass"):
  if type(d[k]) is not bool: raise ValueError(k+" must be boolean")
 weight=vals["mass_kg"]*G
 stall=math.sqrt(2*weight/(vals["air_density_kg_m3"]*vals["wing_area_m2"]*vals["cl_max"]))
 foil_lift=0.5*vals["water_density_kg_m3"]*vals["foil_speed_m_s"]**2*vals["foil_area_m2"]*vals["foil_cl_operating"]
 land={s: vals["thrust_N"]>vals["ground_drag_"+s+"_N"] for s in ("hard","grass","sand")}
 clear=d["lowest_foil_stowed_z_mm"]-d["ground_z_mm"]
 prop_clear=d["prop_lowest_z_mm"]-d["ground_z_mm"]
 buoyancy=vals["water_density_kg_m3"]*G*vals["water_displacement_m3"]
 checks={"land_resistance_only":all(land.values()),"foil_stowed_above_ground":clear>0,
 "prop_sweep_above_ground":prop_clear>0,"buoyancy_exceeds_weight":buoyancy>weight,
 "foil_lift_exceeds_weight_at_target_speed":foil_lift>=weight,
 "skid_wear_within_limit":vals["skid_wear_mm"]<=vals["skid_wear_limit_mm"],
 "sealed_enclosure_test_pass":d["sealed_enclosure_test_pass"],
 "control_sweep_test_pass":d["control_sweep_test_pass"],
 "master_three_view_match_pass":d["master_three_view_match_pass"]}
 # These necessary screening conditions never prove all-mode functionality.
 return {"accepted":False,"screening_checks":checks,
  "computed":{"weight_N":weight,"estimated_stall_speed_m_s":stall,
   "foil_lift_N":foil_lift,"buoyancy_N":buoyancy,
   "stowed_foil_ground_clearance_mm":clear,"prop_ground_clearance_mm":prop_clear,
   "thrust_to_weight":vals["thrust_N"]/weight,"ground_thrust_exceeds_drag":land},
  "limitations":["No hydrodynamic drag, foil ventilation or stability analysis.",
   "No aircraft static margin, aerodynamic polar, powertrain heat or flight dynamics validation.",
   "No actual terrain acceleration, ground steering or sustained takeoff evidence.",
   "Necessary screening inequalities are not a flight, land or water release."]}

def main():
 p=argparse.ArgumentParser()
 p.add_argument("--inputs",required=True)
 p.add_argument("--output",default="docs/V344_THREE_MODE_PHYSICS_SCREEN_WIP.json")
 a=p.parse_args()
 d=json.loads(Path(a.inputs).read_text(encoding="utf-8"))
 r=evaluate(d)
 out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(r,indent=2,sort_keys=True)+"\\n",encoding="utf-8")
 print(json.dumps({"output":str(out),"accepted":False,"missing":r.get("missing",[])},sort_keys=True))
if __name__=="__main__":main()
