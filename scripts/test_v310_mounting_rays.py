"""Offline unit tests for v310 vertical triangle ray intersections.

Run on Jens-PC: python scripts/test_v310_mounting_rays.py
No source geometry is changed. Synthetic cases verify orientation,
empty screw-axis behavior and crossing deduplication.
"""
import sys
from pathlib import Path
import numpy as np
import trimesh
sys.path.insert(0, str(Path(__file__).resolve().parent))
from survey_v310_mounting_rays import vertical_hits

def check():
    cube = trimesh.creation.box(extents=(20, 20, 4))
    cube.apply_translation((0, 0, 12))
    assert np.allclose(vertical_hits(cube, 0, 0), [10, 14], atol=1e-5)
    assert vertical_hits(cube, 12, 0) == []
    # Winding reversal must not change ray intersections.
    cube.invert()
    assert np.allclose(vertical_hits(cube, 0, 0), [10, 14], atol=1e-5)
    # Boolean-free hollow annulus proxy: screw bore is empty on axis.
    outer = trimesh.creation.annulus(r_min=1.65, r_max=8, height=3.2, sections=64)
    outer.apply_translation((0, 0, -9.3))
    assert vertical_hits(outer, 0, 0) == []
    assert len(vertical_hits(outer, 2.5, 0)) == 2
    print("V310 synthetic ray tests PASS (4 cases); real STL survey still required.")

if __name__ == "__main__":
    check()
