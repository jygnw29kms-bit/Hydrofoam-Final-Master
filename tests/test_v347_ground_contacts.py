"""Regression tests for v347 ground-contact screening. Run: python -m unittest discover -s tests -p 'test_v347*.py'"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("v347", ROOT / "scripts" / "engineering_v347_active_ground_contacts.py")
v347 = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(v347)


def sample(**changes):
    data = dict(surface="hard", contacts_mm=[[-50,-40,0],[50,-40,0],[50,40,0],[-50,40,0]],
                cg_mm=[0,0,20], pitch_deg=[0], roll_deg=[0],
                contact_height_tolerance_mm=0, minimum_margin_mm=5)
    data.update(changes)
    return data


class GroundContactTests(unittest.TestCase):
    def test_four_coplanar_supports(self):
        result = v347.run(sample())
        self.assertTrue(result["screen_pass"])
        self.assertFalse(result["accepted"])
        self.assertEqual(result["samples"][0]["active_contact_count"], 4)
        self.assertAlmostEqual(result["samples"][0]["cg_margin_mm"], 40)

    def test_only_two_low_points_fail(self):
        contacts=[[-50,-40,0],[50,-40,0],[50,40,10],[-50,40,10]]
        result=v347.run(sample(contacts_mm=contacts))
        self.assertFalse(result["screen_pass"])
        self.assertEqual(result["samples"][0]["active_contact_count"],2)

    def test_tolerance_can_activate_four(self):
        contacts=[[-50,-40,0],[50,-40,0],[50,40,10],[-50,40,10]]
        result=v347.run(sample(contacts_mm=contacts,contact_height_tolerance_mm=10))
        self.assertTrue(result["screen_pass"])

    def test_cg_outside_support_fails(self):
        result=v347.run(sample(cg_mm=[100,0,20]))
        self.assertFalse(result["screen_pass"])
        self.assertLess(result["samples"][0]["cg_margin_mm"],0)

    def test_collinear_support_fails(self):
        contacts=[[-50,0,0],[0,0,0],[50,0,0]]
        result=v347.run(sample(contacts_mm=contacts))
        self.assertFalse(result["screen_pass"])

    def test_missing_inputs_fail_closed(self):
        result=v347.run({"surface":"hard"})
        self.assertFalse(result["screen_pass"])
        self.assertFalse(result["accepted"])
        self.assertIn("cg_mm",result["missing_inputs"])

    def test_invalid_measurements_rejected(self):
        for changes in ({"contact_height_tolerance_mm":-1},
                        {"minimum_margin_mm":float("nan")},
                        {"pitch_deg":[46]},
                        {"roll_deg":[]},
                        {"surface":"water"},
                        {"contacts_mm":[[0,0,0],[1,0,0]]}):
            with self.subTest(changes=changes):
                with self.assertRaises(ValueError):
                    v347.run(sample(**changes))

    def test_symmetric_roll_samples(self):
        result=v347.run(sample(roll_deg=[-5,0,5],contact_height_tolerance_mm=20))
        self.assertEqual(len(result["samples"]),3)
        self.assertFalse(result["accepted"])


if __name__=="__main__":
    unittest.main()
