"""Hydrofoam v368: evidence-gated three-mode engineering calculator.

Pure Python 3, no Blender/FreeCAD dependency. Never substitutes simulation for
physical qualification. Usage: python scripts/v368_three_mode_gate.py input.json report.json
All input values are measured or explicitly sourced, SI units throughout.
"""
import json, math, sys
from pathlib import Path

REQUIRED = {
 "common": ["mass_kg", "gravity_m_s2", "thrust_static_n", "prop_clearance_land_m",
            "foil_clearance_land_m", "cg_x_m", "cg_y_m", "wing_area_m2",
            "air_density_kg_m3", "cl_max", "flight_speed_m_s"],
 "land": ["normal_load_n", "friction_coefficient_hard", "friction_coefficient_grass",
          "friction_coefficient_sand", "skid_contact_area_m2", "sand_bearing_capacity_pa",
          "steering_test_pass", "skid_wear_test_pass"],
 "water": ["displaced_volume_m3", "water_density_kg_m3", "foil_area_m2",
           "foil_cl_at_speed", "foil_speed_m_s", "foil_depth_m",
           "waterproof_test_pass", "foil_transition_test_pass"],
 "air": ["flight_cg_min_x_m", "flight_cg_max_x_m", "control_sweep_pass",
         "static_thrust_test_pass", "flight_stability_test_pass"]
}
def positive(x, name, zero=False):
    if isinstance(x, bool) or not isinstance(x, (int,float)) or not math.isfinite(x) or (x < 0 if zero else x <= 0):
        raise ValueError(f"{name}: expected finite {'nonnegative' if zero else 'positive'} number")
    return float(x)
def main(src, dest):
    data=json.loads(Path(src).read_text(encoding="utf-8"))
    missing=[f"{section}.{key}" for section,keys in REQUIRED.items() for key in keys if key not in data.get(section,{})]
    result={"version":"v368", "status":"NOT_APPROVED", "missing_inputs":missing,
            "evidence_note":"Analytical screening only; physical land/water/flight tests and CAD integration are mandatory.",
            "checks":{}, "metrics":{}}
    if missing:
        Path(dest).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        return 2
    c,l,w,a=(data[k] for k in ("common","land","water","air"))
    for section in ("common","land","water","air"):
        for k,v in data[section].items():
            if isinstance(v,bool): continue
            positive(v,f"{section}.{k}",zero=k in ("cg_x_m","cg_y_m","foil_clearance_land_m","prop_clearance_land_m","flight_cg_min_x_m","flight_cg_max_x_m"))
    weight=c["mass_kg"]*c["gravity_m_s2"]
    stall=math.sqrt(2*weight/(c["air_density_kg_m3"]*c["wing_area_m2"]*c["cl_max"]))
    buoyancy=w["water_density_kg_m3"]*c["gravity_m_s2"]*w["displaced_volume_m3"]
    foil_lift=0.5*w["water_density_kg_m3"]*w["foil_speed_m_s"]**2*w["foil_area_m2"]*w["foil_cl_at_speed"]
    result["metrics"]={"weight_n":weight,"estimated_stall_speed_m_s":stall,
      "buoyancy_n":buoyancy,"foil_lift_at_speed_n":foil_lift,
      "sand_pressure_pa":l["normal_load_n"]/l["skid_contact_area_m2"],
      "land_start_margin_n":{surface:c["thrust_static_n"]-l["normal_load_n"]*l["friction_coefficient_"+surface] for surface in ("hard","grass","sand")}}
    checks=result["checks"]
    checks["land_start_all_surfaces"]=all(v>0 for v in result["metrics"]["land_start_margin_n"].values())
    checks["sand_bearing"]=result["metrics"]["sand_pressure_pa"]<=l["sand_bearing_capacity_pa"]
    checks["land_foil_clearance"]=c["foil_clearance_land_m"]>0
    checks["land_prop_clearance"]=c["prop_clearance_land_m"]>0
    checks["land_steering"]=l["steering_test_pass"] is True
    checks["skid_wear"]=l["skid_wear_test_pass"] is True
    checks["water_static_buoyancy"]=buoyancy>weight
    checks["foil_lift_screen"]=foil_lift>=weight
    checks["waterproof"]=w["waterproof_test_pass"] is True
    checks["foil_transition"]=w["foil_transition_test_pass"] is True
    checks["flight_speed_above_stall"]=c["flight_speed_m_s"]>stall
    checks["flight_cg_envelope"]=a["flight_cg_min_x_m"]<=c["cg_x_m"]<=a["flight_cg_max_x_m"]
    checks["control_sweep"]=a["control_sweep_pass"] is True
    checks["thrust_test"]=a["static_thrust_test_pass"] is True
    checks["flight_stability"]=a["flight_stability_test_pass"] is True
    result["screening_pass"]=all(checks.values())
    result["status"]="SCREENING_PASS_NOT_FINAL" if result["screening_pass"] else "NOT_APPROVED"
    result["limitations"]=["Static friction estimate does not model dynamic rolling, grass entanglement or sand sinkage.",
       "Foil lift estimate ignores drag, ventilation, pitch stability and strut interference.",
       "Stall estimate ignores Reynolds effects, trim, induced drag and structural loads.",
       "Photogrammetry, hinge collision sweeps, servo force, print fit and flight trials are separate mandatory gates."]
    Path(dest).write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return 0 if result["screening_pass"] else 1
if __name__=="__main__":
    if len(sys.argv)!=3:
        print("usage: python v368_three_mode_gate.py measurements.json report.json",file=sys.stderr)
        sys.exit(64)
    try: sys.exit(main(sys.argv[1],sys.argv[2]))
    except (ValueError,KeyError,ZeroDivisionError) as exc:
        print(f"invalid measurement data: {exc}",file=sys.stderr)
        sys.exit(65)
