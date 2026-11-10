"""Regression checks for v347 active-contact land stability screening.

Run from repository root:
    python -m unittest discover -s tests -p 'test_v348_ground_contacts.py' -v

These are synthetic geometry tests, NOT physical acceptance measurements.
"""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "scripts" / "engineering_v347_active_ground_contacts.py"
spec = importlib.util.spec_from_file_location("ground_contacts_v347", MODULE)
ground = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ground)


def case(contacts, cg=None, pitch=None, roll=None, tolerance=0.01, margin=1.0):
    return {
        "surface": "hard",
        "contacts_mm": contacts,
        "cg_mm": cg if cg is not None else [0, 0, 40],
        "pitch_deg": pitch if pitch is not None else [0],
        "roll_deg": roll if roll is not None else [0],
        "contact_height_tolerance_mm": tolerance,
        "minimum_margin_mm": margin,
    }


class GroundContactRegression(unittest.TestCase):
    def test_level_four_corners_pass(self):
        d = case([[-50,-40,0],[-50,40,0],[50,-40,0],[50,40,0]])
        result = ground.run(d)
        self.assertTrue(result["screen_pass"])
        self.assertFalse(result["accepted"])
        self.assertAlmostEqual(result["samples"][0]["cg_margin_mm"], 40)

    def test_single_low_foil_tip_fails(self):
        d = case([[-50,-40,0],[-50,40,0],[50,-40,0],[50,40,0],[0,0,-5]])
        result = ground.run(d)
        self.assertFalse(result["screen_pass"])
        self.assertEqual(result["samples"][0]["active_contact_count"], 1)

    def test_two_low_skid_corners_fail(self):
        d = case([[-50,-40,-3],[-50,40,-3],[50,-40,0],[50,40,0]])
        result = ground.run(d)
        self.assertFalse(result["screen_pass"])
        self.assertEqual(result["samples"][0]["active_contact_count"], 2)

    def test_cg_outside_triangle_fails(self):
        d = case([[0,0,0],[100,0,0],[0,100,0]],cg=[80,80,40])
        result = ground.run(d)
        self.assertFalse(result["screen_pass"])
        self.assertLess(result["samples"][0]["cg_margin_mm"], 0)

    def test_tolerance_changes_active_contact_set(self):
        points = [[-50,-40,0],[-50,40,0],[50,-40,0.2],[50,40,0.2]]
        tight = ground.run(case(points,tolerance=0.05))
        loose = ground.run(case(points,tolerance=0.25))
        self.assertFalse(tight["screen_pass"])
        self.assertTrue(loose["screen_pass"])

    def test_pitch_can_remove_contacts(self):
        points = [[-50,-40,0],[-50,40,0],[50,-40,0],[50,40,0]]
        result = ground.run(case(points,pitch=[0,10],tolerance=0.01))
        self.assertTrue(result["samples"][0]["screen_pass"])
        self.assertFalse(result["samples"][1]["screen_pass"])
        self.assertFalse(result["screen_pass"])

    def test_missing_inputs_fail_closed(self):
        result = ground.run({"surface":"hard"})
        self.assertFalse(result["accepted"])
        self.assertFalse(result["screen_pass"])
        self.assertIn("contacts_mm", result["missing_inputs"])

    def test_invalid_nonfinite_geometry_rejected(self):
        with self.assertRaises(ValueError):
            ground.run(case([[0,0,0],[100,0,0],[0,100,float("nan")]]))

    def test_negative_tolerance_rejected(self):
        with self.assertRaises(ValueError):
            ground.run(case([[0,0,0],[100,0,0],[0,100,0]],tolerance=-1))


if __name__ == "__main__":
    unittest.main()
