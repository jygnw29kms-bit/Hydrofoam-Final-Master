"""v348: deterministic regression tests for v347 ground-contact screening.

Run: python scripts/engineering_v348_ground_contact_regression.py
These tests check numerical logic only; they cannot certify ground operation.
"""
import importlib.util
from pathlib import Path

path = Path(__file__).with_name("engineering_v347_active_ground_contacts.py")
spec = importlib.util.spec_from_file_location("ground_v347", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def sample(points, pitch=[0], roll=[0], tol=0.01, margin=0):
    return mod.run({
        "surface": "hard",
        "contacts_mm": points,
        "cg_mm": [0, 0, 20],
        "pitch_deg": pitch,
        "roll_deg": roll,
        "contact_height_tolerance_mm": tol,
        "minimum_margin_mm": margin
    })

def check(label, actual, expected):
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected}, got {actual}")
    print("PASS", label)

# Four coplanar skid points surround the center of gravity.
square = [[-100,-80,0],[100,-80,0],[100,80,0],[-100,80,0]]
r = sample(square, margin=40)
check("level stable square", r["screen_pass"], True)
check("no operational acceptance", r["accepted"], False)
check("all four contacts active", r["samples"][0]["active_contact_count"], 4)

# A single lower foil point must not become a support polygon.
r = sample(square + [[0,0,-10]])
check("single lowest point fails", r["screen_pass"], False)
check("single active point", r["samples"][0]["active_contact_count"], 1)

# Only two lower points cannot form a polygon.
r = sample(square + [[-50,0,-10],[50,0,-10]])
check("two lowest points fail", r["screen_pass"], False)

# A valid polygon that does not surround the CG must fail.
r = sample([[50,50,0],[150,50,0],[100,150,0]])
check("CG outside polygon fails", r["screen_pass"], False)

# An excessively high required margin fails despite stable support.
r = sample(square, margin=90)
check("insufficient support margin fails", r["screen_pass"], False)

# A pitched rigid four-point chassis generally loses two contacts.
r = sample(square, pitch=[10], tol=0.01)
check("pitched rigid chassis fails", r["screen_pass"], False)

# Inputs are mandatory; missing values never pass.
r = mod.run({"surface":"hard"})
check("missing input fails", r["screen_pass"], False)
check("missing input never accepted", r["accepted"], False)

# Refuse non-finite coordinates, including NaN.
try:
    sample([[float("nan"),0,0],[1,0,0],[0,1,0]])
except ValueError:
    print("PASS nonfinite coordinate rejected")
else:
    raise AssertionError("nonfinite coordinate accepted")

print("v348 regression checks complete; NO operational acceptance.")
