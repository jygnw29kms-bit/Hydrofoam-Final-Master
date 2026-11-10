"""Hydrofoam v344: conservative three-mode feasibility calculations, no invented measurements.
Run: python scripts/engineering_v344_three_mode_budget.py path/to/measured_inputs.json
Writes JSON beside input. Missing measurements fail closed. SI units throughout.
"""
import json, math, sys
from pathlib import Path

FIELDS = {
 "mass_kg": "Measured fully assembled mass including battery, foils, skids",
 "wing_area_m2": "Measured planform area",
 "cl_max": "Validated maximum lift coefficient for the actual airframe",
 "air_density_kg_m3": "Air density at test conditions",
 "measured_static_thrust_N": "Measured pusher thrust with installed battery",
 "rolling_resistance_coefficient": "Measured for each land surface",
 "land_speed_m_s": "Target land speed for resistance estimate",
 "prop_ground_clearance_m": "Measured clearance in worst land attitude",
 "foil_lowest_point_ground_clearance_m": "Measured clearance with foils in land configuration",
 "foil_area_m2": "Submerged lifting foil reference area",
 "foil_cl": "Validated foil lift coefficient at chosen trim",
 "foil_speed_m_s": "Measured foil transition speed",
 "water_density_kg_m3": "Measured or documented local water density",
 "displaced_volume_m3": "Watertight displaced volume at the tested waterline",
 "cg_x_m": "Measured longitudinal CG in a documented datum",
 "neutral_point_x_m": "Validated neutral point using the same datum",
 "mean_aerodynamic_chord_m": "Measured mean aerodynamic chord",
 "skid_contact_area_m2": "Actual load-bearing contact area",
}
def finite_positive(data,key,allow_zero=False):
 v=data.get(key)
 if not isinstance(v,(int,float)) or isinstance(v,bool) or not math.isfinite(v) or (v<0 if allow_zero else v<=0):
  raise ValueError(f"{key}: finite {'nonnegative' if allow_zero else 'positive'} measured value required")
 return float(v)
def run(d):
 required=["mass_kg","wing_area_m2","cl_max","air_density_kg_m3","measured_static_thrust_N",
 "foil_area_m2","foil_cl","foil_speed_m_s","water_density_kg_m3","displaced_volume_m3",
 "cg_x_m","neutral_point_x_m","mean_aerodynamic_chord_m","skid_contact_area_m2"]
 missing=[k for k in required if k not in d]
 if missing: return {"accepted":False,"missing_inputs":missing,"input_guidance":{k:FIELDS[k] for k in missing}}
 x={k:finite_positive(d,k,allow_zero=k in ("cg_x_m","neutral_point_x_m")) for k in required}
 g=9.80665; weight=x["mass_kg"]*g
 # Longitudinal datum direction must be documented; sign alone is not acceptance.
 results={"weight_N":weight,
 "stall_speed_ideal_m_s":math.sqrt(2*weight/(x["air_density_kg_m3"]*x["wing_area_m2"]*x["cl_max"])),
 "static_thrust_to_weight":x["measured_static_thrust_N"]/weight,
 "foil_lift_N":0.5*x["water_density_kg_m3"]*x["foil_speed_m_s"]**2*x["foil_area_m2"]*x["foil_cl"],
 "hydrostatic_buoyancy_N":x["water_density_kg_m3"]*g*x["displaced_volume_m3"],
 "skid_average_contact_pressure_Pa":weight/x["skid_contact_area_m2"],
 "signed_static_margin_fraction":(x["neutral_point_x_m"]-x["cg_x_m"])/x["mean_aerodynamic_chord_m"]}
 surfaces={}
 for name,vals in d.get("land_surfaces",{}).items():
  if not isinstance(vals,dict): raise ValueError("land_surfaces entries must be objects")
  mu=finite_positive(vals,"rolling_resistance_coefficient",allow_zero=True)
  surfaces[name]={"resistance_estimate_N":mu*weight,"thrust_exceeds_simple_resistance":x["measured_static_thrust_N"]>mu*weight}
 results["land_surfaces"]=surfaces
 return {"accepted":False,"calculated_screening_only":results,
 "missing_evidence":["drag polar and takeoff acceleration","flight CG datum and stable pitch margin validation",
 "foil ventilation/cavitation, drag and transition stability","water sealing and flooding test",
 "surface-specific land traction, steering and wear","foil and prop ground-clearance sweep",
 "servo torque, horn geometry, linkages and collision-free full throw",
 "three-view image registration to immutable reference","physical land, water and flight tests"],
 "warning":"Calculated values are not evidence of safe flight or three-mode acceptance."}
if __name__=="__main__":
 if len(sys.argv)!=2: raise SystemExit("Usage: python engineering_v344_three_mode_budget.py measured_inputs.json")
 src=Path(sys.argv[1]);data=json.loads(src.read_text(encoding="utf-8"))
 result=run(data)
 dst=src.with_name(src.stem+"_v344_screening.json")
 dst.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
 print(dst,"accepted:",result["accepted"])
