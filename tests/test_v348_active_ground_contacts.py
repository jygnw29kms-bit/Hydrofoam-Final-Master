"""v348 regression tests for conservative land contact screening.

Run: python -m unittest discover -s tests -p 'test_v348_*.py'
No CAD, road, water or flight acceptance is implied.
"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "land_v347", ROOT / "scripts" / "engineering_v347_active_ground_contacts.py")
land = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(land)


def sample(contacts, pitch=None, roll=None, tolerance=0.01, margin=1):
    return {
        "surface": "hard", "contacts_mm": contacts,
        "cg_mm": [0, 0, 30], "pitch_deg": [0] if pitch is None else pitch,
        "roll_deg": [0] if roll is None else roll,
        "contact_height_tolerance_mm": tolerance, "minimum_margin_mm": margin,
    }


class ActiveContactTests(unittest.TestCase):
    def test_four_coplanar_skid_contacts(self):
        data = sample([[-60,-40,0],[-60,40,0],[60,-40,0],[60,40,0]])
        result = land.run(data)
        self.assertTrue(result["screen_pass"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["samples"][0]["active_contact_count"],4)

    def test_only_two_low_contacts_fail(self):
        points=[[-60,-40,0],[60,-40,0],[-60,40,5],[60,40,5]]
        result=land.run(sample(points))
        self.assertFalse(result["screen_pass"])
        self.assertEqual(result["samples"][0]["active_contact_count"],2)

    def test_single_low_foil_contact_fails(self):
        points=[[-60,-40,0],[60,-40,0],[-60,40,0],[60,40,0],[0,0,-12]]
        result=land.run(sample(points))
        self.assertFalse(result["screen_pass"])
        self.assertEqual(result["samples"][0]["active_contact_count"],1)

    def test_three_collinear_contacts_fail(self):
        points=[[-60,0,0],[0,0,0],[60,0,0]]
        self.assertFalse(land.run(sample(points))["screen_pass"])

    def test_cg_outside_contact_triangle_fails(self):
        points=[[10,10,0],[50,10,0],[10,50,0]]
        self.assertFalse(land.run(sample(points))["screen_pass"])

    def test_tilt_reduces_active_contacts(self):
        points=[[-60,-40,0],[-60,40,0],[60,-40,0],[60,40,0]]
        result=land.run(sample(points,roll=[0,8]))
        self.assertTrue(result["samples"][0]["screen_pass"])
        self.assertFalse(result["samples"][1]["screen_pass"])

    def test_missing_inputs_do_not_pass(self):
        result=land.run({"surface":"hard"})
        self.assertFalse(result["screen_pass"])
        self.assertFalse(result["accepted"])
        self.assertIn("contacts_mm",result["missing_inputs"])

    def test_bad_values_rejected(self):
        with self.assertRaises(ValueError):
            land.run(sample([[0,0,0],[1,0,0],[0,1,0]],roll=[float("nan")]))
        with self.assertRaises(ValueError):
            land.run(sample([[0,0,0],[1,0,0],[0,1,0]],tolerance=-1))


if __name__=="__main__":
    unittest.main()
