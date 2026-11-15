"""Regression tests for v413 planar linkage screening.

Run: python -m unittest discover -s tests -p 'test_v413_linkage_solver.py'
These tests do not certify the physical Hydrofoam mechanism.
"""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("v413_linkage_solver", ROOT / "scripts" / "v413_linkage_solver.py")
solver = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(solver)


class LinkageGeometryTests(unittest.TestCase):
    def test_circle_intersections_satisfy_rod_length(self):
        pivot = (5.0, -3.0)
        target = (22.0, 11.0)
        arm, rod = 12.0, 15.0
        angles = solver.servo_solutions(pivot, arm, target, rod)
        self.assertEqual(len(angles), 2)
        for degrees in angles:
            end = (pivot[0] + arm * math.cos(math.radians(degrees)),
                   pivot[1] + arm * math.sin(math.radians(degrees)))
            self.assertAlmostEqual(solver.dist(end, target), rod, places=8)

    def test_disjoint_circles_rejected(self):
        self.assertEqual(solver.servo_solutions((0, 0), 2, (20, 0), 3), [])

    def test_nested_circles_rejected(self):
        self.assertEqual(solver.servo_solutions((0, 0), 2, (1, 0), 8), [])

    def test_wrapped_angle_difference(self):
        self.assertAlmostEqual(abs(solver.angle_difference(-179, 179)), 2)

    def test_nonfinite_point_rejected(self):
        with self.assertRaises(ValueError):
            solver.point({"p": [0, float("nan")]}, "p")

    def test_incomplete_inventory_rejected(self):
        with self.assertRaises(ValueError):
            solver.audit({"surfaces": {"rudder": {}}})

    def test_unreachable_range_is_fail_not_final(self):
        surface = {
            "servo_pivot_yz_mm": [100, 100],
            "horn_tip_neutral_yz_mm": [10, 0],
            "servo_arm_mm": 5,
            "rod_length_mm": 10,
            "rudder_travel_deg": 25,
            "servo_limits_deg": [-90, 90],
        }
        result = solver.solve_surface(surface)
        self.assertEqual(result["status"], "KINEMATIC_SCREEN_FAIL")
        self.assertGreater(result["unreachable_samples"], 0)

    def test_no_physical_certification_claim(self):
        surface = {
            "servo_pivot_yz_mm": [30, 0],
            "horn_tip_neutral_yz_mm": [10, 0],
            "servo_arm_mm": 10,
            "rod_length_mm": 20,
            "rudder_travel_deg": 10,
            "servo_limits_deg": [-180, 180],
        }
        report = solver.audit({"surfaces": {name: dict(surface) for name in solver.REQUIRED}})
        self.assertFalse(report["final_master_image_verified"])
        self.assertFalse(report["integrated_mechanism_verified"])
        self.assertFalse(report["land_water_air_verified"])


if __name__ == "__main__":
    unittest.main()
