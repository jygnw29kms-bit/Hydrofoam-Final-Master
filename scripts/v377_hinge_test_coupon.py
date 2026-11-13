"""Hydrofoam v377: parametric printable hinge test assembly, NOT flight-approved.

Run with FreeCAD Python console: exec(open('scripts/v377_hinge_test_coupon.py').read())
All lengths mm. Independent coupon for pin-fit and rotation bench tests.
This does not modify the immutable visual master or existing vehicle geometry.
"""
import math
from pathlib import Path
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parent.parent if "__file__" in globals() else Path.cwd()
OUT = ROOT / "cad" / "v377_hinge_coupon"
OUT.mkdir(parents=True, exist_ok=True)
DOC = App.newDocument("Hydrofoam_v377_Hinge_Coupon")
PIN_D = 2.4
RADIAL_CLEARANCE = 0.25
AXIAL_CLEARANCE = 0.35
KNUCKLE_OD = 6.8
KNUCKLE_LENGTH = 9.0
PLATE_LENGTH = 52.0
PLATE_WIDTH = 17.0
PLATE_THICKNESS = 3.0
AXIS_Y = 0.0
AXIS_Z = 6.5

def cylinder(radius, length, x):
    return Part.makeCylinder(radius, length, App.Vector(x, AXIS_Y, AXIS_Z), App.Vector(1, 0, 0))

def leaf(label, moving):
    # Three alternating fixed knuckles and two moving knuckles.
    shape = Part.makeBox(PLATE_LENGTH, PLATE_WIDTH, PLATE_THICKNESS,
                         App.Vector(-PLATE_LENGTH / 2, 1.2 if moving else -PLATE_WIDTH-1.2, 0))
    segments = [(-17.8, -8.8), (0.0, 9.0)] if moving else [(-26.0, -18.15), (-8.45, -0.35), (9.35, 17.8)]
    for a, b in segments:
        sleeve = cylinder(KNUCKLE_OD/2, b-a, a)
        sleeve = sleeve.cut(cylinder(PIN_D/2+RADIAL_CLEARANCE, b-a, a))
        shape = shape.fuse(sleeve)
        # Tangential web connects knuckle to the appropriate leaf.
        web_y = 0 if moving else -5.0
        web = Part.makeBox(b-a, 5.0, AXIS_Z, App.Vector(a, web_y, 0))
        shape = shape.fuse(web)
    shape = shape.removeSplitter()
    obj = DOC.addObject("PartDesign::Feature", label)
    obj.Shape = shape
    return obj

fixed = leaf("FixedLeaf", False)
moving = leaf("MovingLeaf", True)
pin = DOC.addObject("PartDesign::Feature", "RemovablePin")
pin.Shape = cylinder(PIN_D/2, 53.0, -26.5)
DOC.recompute()
DOC.saveAs(str(OUT / "Hydrofoam_v377_Hinge_Coupon.FCStd"))
for obj in (fixed, moving, pin):
    mesh = MeshPart.meshFromShape(Shape=obj.Shape, LinearDeflection=0.08,
                                  AngularDeflection=math.radians(12), Relative=False)
    mesh.write(str(OUT / (obj.Label + ".stl")))
print("v377 coupon exported:", OUT)
print("PROTOTYPE ONLY: validate fit, swept collisions, material and load experimentally.")
