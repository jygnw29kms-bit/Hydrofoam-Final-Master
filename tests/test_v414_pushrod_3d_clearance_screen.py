"""v414 mathematical regression tests; not a mechanical acceptance."""
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("screen",Path(__file__).resolve().parents[1]/"scripts"/"v414_pushrod_3d_clearance_screen.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ClearanceTests(unittest.TestCase):
    def test_crossing_box(self):
        self.assertAlmostEqual(m.segment_box_distance((-2,0,0),(2,0,0),(-1,-1,-1),(1,1,1)),0)
    def test_offset_box(self):
        self.assertAlmostEqual(m.segment_box_distance((-2,3,0),(2,3,0),(-1,-1,-1),(1,1,1)),2)
    def test_endpoint_nearest(self):
        self.assertAlmostEqual(m.segment_box_distance((3,0,0),(4,0,0),(-1,-1,-1),(1,1,1)),2)
    def test_rotated_horn(self):
        p=m.rotate_axis([1,0,0],[0,0,0],[0,0,2],90)
        self.assertAlmostEqual(p[0],0,places=8)
        self.assertAlmostEqual(p[1],1,places=8)
    def test_no_zero_axis(self):
        with self.assertRaises(ValueError):m.rotate_axis([1,0,0],[0,0,0],[0,0,0],5)
    def test_invalid_inventory(self):
        with self.assertRaises(ValueError):m.audit({"coordinate_frame":"measured_airframe_mm","surfaces":{}})
    def test_false_certification_forbidden(self):
        base={"hinge_origin_mm":[0,0,0],"hinge_axis":[0,0,1],"horn_tip_neutral_mm":[1,0,0],
              "servo_arm_tip_mm":[4,0,0],"rod_radius_mm":0.2,"required_clearance_mm":0.2,
              "travel_deg":20,"obstacles":[{"id":"far","min_mm":[100,100,100],"max_mm":[101,101,101]}]}
        names=["left_aileron","right_aileron","elevator_left","elevator_right","rudder"]
        r=m.audit({"coordinate_frame":"measured_airframe_mm","surfaces":{n:base for n in names}})
        self.assertTrue(r["all_screens_pass"])
        self.assertFalse(r["integrated_mechanism_verified"])
        self.assertFalse(r["final_master_image_verified"])
        self.assertFalse(r["land_water_air_verified"])
if __name__=="__main__":unittest.main()
