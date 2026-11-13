"""Hydrofoam v380: conservative three-mode engineering gate (stdlib only).

Usage: python scripts/v380_three_mode_gate.py measurements.json
Measurements are REAL test or CAD-derived numbers, not defaults. Missing evidence
is UNKNOWN, never PASS. This is a preliminary screening, not flight certification.
"""
import json, math, pathlib, sys

FIELDS = {
 "land": ["mass_kg", "measured_static_thrust_N", "measured_start_resistance_N",
          "foil_ground_clearance_mm", "minimum_observed_foil_clearance_mm",
          "ground_turn_left_verified", "ground_turn_right_verified",
          "hard_ground_start_verified", "grass_start_verified",
          "firm_sand_start_verified", "skid_wear_acceptable"],
 "water": ["mass_kg", "measured_displacement_litres", "waterproof_test_passed",
           "planing_transition_verified", "foil_lift_transition_verified",
           "stable_water_turns_verified"],
 "air": ["mass_kg", "wing_area_m2", "measured_static_thrust_N",
         "measured_max_current_A", "motor_esc_current_limit_A",
         "measured_cg_mm", "approved_cg_min_mm", "approved_cg_max_mm",
         "flight_control_authority_verified", "aero_stability_verified",
         "structural_load_test_passed"]
}
BOOLEAN = {x for x in sum(FIELDS.values(), []) if x.endswith("_verified") or x.endswith("_passed") or x.endswith("_acceptable")}
def valid(v):
    return isinstance(v, bool) if False else isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
def evaluate(data):
    report={"version":"v380","status":"NOT_APPROVED","modes":{},"limitations":[
        "Static thrust is not in-motion thrust; no flight performance claim",
        "Displacement volume alone does not establish trim or stability",
        "Ground resistance and foil clearance require physical measurements",
        "CAD/bench checks cannot replace land, water, or flight testing"]}
    for mode,fields in FIELDS.items():
        supplied=data.get(mode,{})
        missing=[k for k in fields if k not in supplied or
                 (not isinstance(supplied[k],bool) if k in BOOLEAN else not valid(supplied[k]))]
        checks={}
        def check(name,keys,fn):
            checks[name]="UNKNOWN" if any(k in missing for k in keys) else ("PASS" if fn(supplied) else "FAIL")
        if mode=="land":
            check("measured_start_force_margin",["measured_static_thrust_N","measured_start_resistance_N"],
                  lambda x:x["measured_static_thrust_N"]>x["measured_start_resistance_N"]>0)
            check("foil_clearance",["foil_ground_clearance_mm","minimum_observed_foil_clearance_mm"],
                  lambda x:min(x["foil_ground_clearance_mm"],x["minimum_observed_foil_clearance_mm"])>0)
            for k in ("ground_turn_left_verified","ground_turn_right_verified","hard_ground_start_verified",
                      "grass_start_verified","firm_sand_start_verified","skid_wear_acceptable"):
                check(k,[k],lambda x,k=k:x[k] is True)
        elif mode=="water":
            check("buoyancy_reserve_20pct",["mass_kg","measured_displacement_litres"],
                  lambda x:x["mass_kg"]>0 and x["measured_displacement_litres"]*1.0>=1.2*x["mass_kg"])
            for k in ("waterproof_test_passed","planing_transition_verified","foil_lift_transition_verified",
                      "stable_water_turns_verified"):
                check(k,[k],lambda x,k=k:x[k] is True)
        else:
            check("wing_loading_positive",["mass_kg","wing_area_m2"],
                  lambda x:x["mass_kg"]>0 and x["wing_area_m2"]>0)
            check("static_thrust_positive",["measured_static_thrust_N"],lambda x:x["measured_static_thrust_N"]>0)
            check("electrical_current_limit",["measured_max_current_A","motor_esc_current_limit_A"],
                  lambda x:0<x["measured_max_current_A"]<=x["motor_esc_current_limit_A"])
            check("cg_inside_approved_envelope",["measured_cg_mm","approved_cg_min_mm","approved_cg_max_mm"],
                  lambda x:x["approved_cg_min_mm"]<=x["measured_cg_mm"]<=x["approved_cg_max_mm"])
            for k in ("flight_control_authority_verified","aero_stability_verified","structural_load_test_passed"):
                check(k,[k],lambda x,k=k:x[k] is True)
        report["modes"][mode]={"missing_or_invalid":missing,"checks":checks,
            "status":"PASS_SCREEN" if checks and all(v=="PASS" for v in checks.values()) and not missing else "NOT_APPROVED"}
    report["all_screen_checks_pass"]=all(v["status"]=="PASS_SCREEN" for v in report["modes"].values())
    return report

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("Usage: python scripts/v380_three_mode_gate.py measurements.json")
    source=pathlib.Path(sys.argv[1])
    data=json.loads(source.read_text(encoding="utf-8"))
    print(json.dumps(evaluate(data),indent=2,ensure_ascii=False))
