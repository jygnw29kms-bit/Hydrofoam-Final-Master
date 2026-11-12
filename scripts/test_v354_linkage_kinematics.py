"""Offline smoke tests for v354 linkage solver; synthetic geometry is NOT Hydrofoam measurements."""
import unittest
from engineering_v354_linkage_kinematics import run

class KinematicsTests(unittest.TestCase):
    def config(self):
        return dict(servo_axis_xy_mm=[0,0],hinge_axis_xy_mm=[20,0],
                    servo_arm_mm=5,rudder_horn_mm=5,rod_length_mm=20,
                    servo_zero_deg=90,rudder_zero_deg=90,
                    servo_angles_deg=[-10,0,10],rudder_limit_deg=90,
                    rod_length_tolerance_mm=0.05)
    def test_valid_linkage(self):
        r=run(self.config())
        self.assertEqual(len(r["samples"]),3)
        self.assertTrue(all(x["reachable"] for x in r["samples"]))
        self.assertTrue(all(x["rod_error_mm"]<=0.05 for x in r["samples"]))
        self.assertFalse(r["accepted"])
    def test_missing_input_fails_closed(self):
        d=self.config();del d["rod_length_mm"]
        self.assertFalse(run(d)["screen_pass"])
    def test_impossible_linkage_fails_closed(self):
        d=self.config();d["rod_length_mm"]=100
        self.assertFalse(run(d)["screen_pass"])
        self.assertTrue(all(not x["reachable"] for x in run(d)["samples"]))
    def test_negative_tolerance_rejected(self):
        d=self.config();d["rod_length_tolerance_mm"]=-1
        with self.assertRaises(ValueError):run(d)
if __name__=="__main__":unittest.main()
