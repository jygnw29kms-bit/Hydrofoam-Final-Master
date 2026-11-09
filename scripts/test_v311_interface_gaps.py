"""v311 synthetic interface tests for v310's four offset probes.

Run on Jens-PC: python scripts/test_v311_interface_gaps.py
Tests analytical heights; never labels synthetic geometry as real CAD evidence.
"""
import sys
from pathlib import Path
import numpy as np
import trimesh

sys.path.insert(0, str(Path(__file__).resolve().parent))
from survey_v310_mounting_rays import vertical_hits

OFFSETS = ((2.5, 0), (-2.5, 0), (0, 2.5), (0, -2.5))

def probe_gap(hull, skid, x=0., y=0.):
    gaps = []
    for dx, dy in OFFSETS:
        hz = vertical_hits(hull, x + dx, y + dy)
        sz = vertical_hits(skid, x + dx, y + dy)
        if hz and sz:
            gaps.append(min(hz) - max(sz))
    return gaps

def main():
    # Hull lower face at z=0, skid upper face at z=-3: 3 mm air gap.
    hull = trimesh.creation.box(extents=(30, 30, 4))
    hull.apply_translation((0, 0, 2))
    skid = trimesh.creation.annulus(r_min=1.65, r_max=8, height=2, sections=96)
    skid.apply_translation((0, 0, -4))
    assert vertical_hits(skid, 0, 0) == [], "Bore centre must remain empty"
    gaps = probe_gap(hull, skid)
    assert len(gaps) == 4, f"Expected four annular probes, got {len(gaps)}"
    assert np.allclose(gaps, [3.0] * 4, atol=1e-5), gaps
    # Overlap must be a negative signed vertical separation, not an absolute distance.
    skid.apply_translation((0, 0, 4))
    gaps = probe_gap(hull, skid)
    assert len(gaps) == 4 and np.allclose(gaps, [-1.] * 4, atol=1e-5), gaps
    # Outside the hull there must be no manufactured numerical result.
    assert probe_gap(hull, skid, x=40) == []
    print("V311 synthetic interface regression PASS: gap +3 mm, overlap -1 mm, missing surface")
    print("No real hull survey, mount strength, or watertightness approval implied.")

if __name__ == "__main__":
    main()
