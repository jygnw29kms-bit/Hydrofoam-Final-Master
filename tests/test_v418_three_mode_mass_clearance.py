"""Regression tests for the v417 mass/foil-clearance precheck.

Run: python -m unittest discover -s tests -p 'test_v418_three_mode_mass_clearance.py'
These are synthetic fixtures, not measured Hydrofoam acceptance evidence.
"""
import copy
import importlib.util
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "v417_three_mode_mass_clearance_screen.py"
spec = importlib.util.spec_from_file_location("hydrofoam_v417", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    return {
        "parts": [
            {"name": "left_float", "mass_g": 100, "cg_xyz_mm": [-50, 0, 0]},
            {"name": "right_float", "mass_g": 100, "cg_xyz_mm": [50, 0, 0]},
            {"name": "battery", "mass_g": 200, "cg_xyz_mm": [0, 20, 10]},
        ],
        "max_takeoff_mass_g": 500,
        "modes": {
            "land": {"lowest_foil_z_mm": 40, "ground_contact_z_mm": 10,
                     "surface_obstacle_allowance_mm": {
                         "hard_ground": 0, "short_grass": 15, "firm_sand": 20}},
            "water": {"lowest_foil_z_mm": 0, "ground_contact_z_mm": 0},
            "air": {"lowest_foil_z_mm": 50, "ground_contact_z_mm": 10},
        },
    }


class ThreeModeMassClearanceTests(unittest.TestCase):
    def test_center_of_mass_and_margin(self):
        result = module.screen(fixture())
        self.assertEqual(result["total_mass_g"], 400)
        self.assertEqual(result["cg_xyz_mm"], [0, 10, 5])
        self.assertEqual(result["mass_budget_margin_g"], 100)
        self.assertTrue(result["mass_budget_screen_pass"])
        self.assertTrue(result["modes"]["land"]["geometric_screen_pass"])
        self.assertFalse(result["final_release_authorized"])

    def test_land_requires_positive_clearance_for_every_surface(self):
        data = fixture()
        data["modes"]["land"]["surface_obstacle_allowance_mm"]["firm_sand"] = 30
        result = module.screen(data)
        self.assertEqual(result["modes"]["land"]["foil_clearance_by_surface_mm"]["firm_sand"], 0)
        self.assertFalse(result["modes"]["land"]["geometric_screen_pass"])

    def test_negative_clearance(self):
        data = fixture()
        data["modes"]["land"]["surface_obstacle_allowance_mm"]["short_grass"] = 35
        self.assertLess(module.screen(data)["modes"]["land"]["foil_clearance_by_surface_mm"]["short_grass"], 0)

    def test_overweight_cannot_pass(self):
        data = fixture()
        data["max_takeoff_mass_g"] = 399
        self.assertFalse(module.screen(data)["mass_budget_screen_pass"])

    def test_duplicate_part_rejected(self):
        data = fixture()
        data["parts"].append(copy.deepcopy(data["parts"][0]))
        with self.assertRaises(ValueError):
            module.screen(data)

    def test_missing_mode_rejected(self):
        data = fixture()
        del data["modes"]["air"]
        with self.assertRaises(ValueError):
            module.screen(data)

    def test_missing_surface_rejected(self):
        data = fixture()
        del data["modes"]["land"]["surface_obstacle_allowance_mm"]["firm_sand"]
        with self.assertRaises(ValueError):
            module.screen(data)

    def test_nonfinite_mass_and_cg_rejected(self):
        for field, value in [("mass_g", math.nan), ("mass_g", math.inf),
                             ("mass_g", -1), ("mass_g", True)]:
            with self.subTest(field=field, value=value):
                data = fixture()
                data["parts"][0][field] = value
                with self.assertRaises(ValueError):
                    module.screen(data)
        data = fixture()
        data["parts"][0]["cg_xyz_mm"][1] = math.nan
        with self.assertRaises(ValueError):
            module.screen(data)

    def test_nonfinite_clearance_rejected(self):
        data = fixture()
        data["modes"]["land"]["lowest_foil_z_mm"] = math.inf
        with self.assertRaises(ValueError):
            module.screen(data)

    def test_water_air_are_not_claimed_as_validated(self):
        result = module.screen(fixture())
        self.assertIsNone(result["modes"]["water"]["geometric_screen_pass"])
        self.assertIsNone(result["modes"]["air"]["geometric_screen_pass"])
        self.assertIn("No water sealing, planing or foil lift test", result["limitations"])


if __name__ == "__main__":
    unittest.main()
