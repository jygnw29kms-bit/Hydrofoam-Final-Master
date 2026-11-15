"""Regression checks for v414 exact segment/AABB distance and sweep semantics.

Run: python -m unittest discover -s tests -p 'test_v415_geometry_regressions.py'
These synthetic tests do not validate the measured Hydrofoam airframe.
"""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "v414_geometry", ROOT / "scripts" / "v414_pushrod_3d_clearance_screen.py"
)
geom = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(geom)


class SegmentBoxGeometryTests(unittest.TestCase):
    def distance(self, p, q, lo=(0, 0, 0), hi=(1, 1, 1)):
        return geom.segment_box_distance(p, q, lo, hi)

    def test_segment_crosses_box(self):
        self.assertAlmostEqual(self.distance((-2, .5, .5), (3, .5, .5)), 0)

    def test_segment_fully_inside_box(self):
        self.assertAlmostEqual(self.distance((.2, .2, .2), (.8, .8, .8)), 0)

    def test_parallel_offset_segment(self):
        self.assertAlmostEqual(self.distance((-1, 2, .5), (2, 2, .5)), 1)

    def test_corner_distance(self):
        self.assertAlmostEqual(self.distance((2, 2, 2), (3, 3, 3)), math.sqrt(3))

    def test_zero_length_segment(self):
        self.assertAlmostEqual(self.distance((2, .5, .5), (2, .5, .5)), 1)

    def test_reversing_endpoints_is_symmetric(self):
        p, q = (-2, 3, .2), (2, -1, 2)
        self.assertAlmostEqual(self.distance(p, q), self.distance(q, p), places=12)

    def test_inverted_box_rejected(self):
        with self.assertRaises(ValueError):
            self.distance((0, 0, 0), (1, 1, 1), (2, 0, 0), (1, 1, 1))

    def test_rotation_about_offset_hinge(self):
        p = geom.rotate_axis([2, 1, 0], [1, 1, 0], [0, 0, 2], 90)
        for got, expected in zip(p, (1, 2, 0)):
            self.assertAlmostEqual(got, expected, places=12)

    def test_zero_axis_rejected(self):
        with self.assertRaises(ValueError):
            geom.rotate_axis([1, 0, 0], [0, 0, 0], [0, 0, 0], 15)

    def test_nonfinite_coordinates_rejected(self):
        with self.assertRaises(ValueError):
            self.distance((float("nan"), 0, 0), (1, 1, 1))


if __name__ == "__main__":
    unittest.main()
