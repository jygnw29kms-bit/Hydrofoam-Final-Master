"""Hydrofoam v381: adversarial regression checks for the v380 three-mode gate.

Run: python scripts/v381_gate_regression.py
No measured data are fabricated; synthetic values exercise software logic only.
"""
import importlib.util
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("gate", ROOT / "v380_three_mode_gate.py")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

def sample():
    return {
        "land": {"mass_kg": 1.5, "measured_static_thrust_N": 25,
                 "measured_start_resistance_N": 10,
                 "foil_ground_clearance_mm": 12,
                 "minimum_observed_foil_clearance_mm": 6,
                 "ground_turn_left_verified": True, "ground_turn_right_verified": True,
                 "hard_ground_start_verified": True, "grass_start_verified": True,
                 "firm_sand_start_verified": True, "skid_wear_acceptable": True},
        "water": {"mass_kg": 1.5, "measured_displacement_litres": 2.2,
                  "waterproof_test_passed": True, "planing_transition_verified": True,
                  "foil_lift_transition_verified": True, "stable_water_turns_verified": True},
        "air": {"mass_kg": 1.5, "wing_area_m2": 0.45,
                "measured_static_thrust_N": 25, "measured_max_current_A": 18,
                "motor_esc_current_limit_A": 30, "measured_cg_mm": 150,
                "approved_cg_min_mm": 140, "approved_cg_max_mm": 160,
                "flight_control_authority_verified": True,
                "aero_stability_verified": True, "structural_load_test_passed": True}
    }

def run():
    count = 0
    def verify(data, mode, check, expected):
        nonlocal count
        result = gate.evaluate(data)["modes"][mode]["checks"][check]
        assert result == expected, (mode, check, expected, result)
        count += 1
    verify({}, "land", "foil_clearance", "UNKNOWN")
    verify({}, "water", "buoyancy_reserve_20pct", "UNKNOWN")
    verify({}, "air", "cg_inside_approved_envelope", "UNKNOWN")
    baseline = sample()
    result = gate.evaluate(baseline)
    assert result["all_screen_checks_pass"] is True
    count += 1
    cases = [
        ("land", "minimum_observed_foil_clearance_mm", 0, "foil_clearance", "FAIL"),
        ("land", "measured_start_resistance_N", 30, "measured_start_force_margin", "FAIL"),
        ("land", "firm_sand_start_verified", False, "firm_sand_start_verified", "FAIL"),
        ("water", "measured_displacement_litres", 1.2, "buoyancy_reserve_20pct", "FAIL"),
        ("water", "waterproof_test_passed", False, "waterproof_test_passed", "FAIL"),
        ("air", "measured_max_current_A", 35, "electrical_current_limit", "FAIL"),
        ("air", "measured_cg_mm", 180, "cg_inside_approved_envelope", "FAIL"),
        ("air", "aero_stability_verified", False, "aero_stability_verified", "FAIL"),
        ("air", "wing_area_m2", 0, "wing_loading_positive", "FAIL"),
        ("air", "measured_static_thrust_N", float("nan"), "static_thrust_positive", "UNKNOWN"),
        ("land", "grass_start_verified", "yes", "grass_start_verified", "UNKNOWN"),
    ]
    for mode, field, value, check, expected in cases:
        data = sample()
        data[mode][field] = value
        verify(data, mode, check, expected)
        assert gate.evaluate(data)["all_screen_checks_pass"] is False
        count += 1
    print(f"v381 regression: {count} synthetic assertions passed; NO physical approval.")

if __name__ == "__main__":
    run()
