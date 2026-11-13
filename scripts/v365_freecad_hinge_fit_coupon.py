"""Parametric printable hinge coupon for Hydrofoam control-linkage fit trials.

FreeCAD Python macro. Run inside FreeCAD GUI or FreeCADCmd with FreeCAD modules
available. This is a *test coupon*, NOT a fitted/approved aircraft component.
Units: mm. No changes to original Blender assembly or master reference.
"""
import math
import os
from pathlib import Path
import FreeCAD as App
import Part
import Mesh

# Explicit provisional print-fit dimensions; verify against actual v333 mesh,
# hinge pin stock and PETG/P2S print calibration before installation.
PIN_DIAMETER = 2.0
RADIAL_CLEARANCE = 0.25
BARREL_OD = 6.0
BARREL_LENGTH = 7.0
AXIAL_GAP = 0.4
LEAF_LENGTH = 18.0
LEAF_WIDTH = 10.0
LEAF_THICKNESS = 3.0
MOUNT_HOLE = 2.6
MOUNT_EDGE = 5.0

assert BARREL_OD > PIN_DIAMETER + 2 * RADIAL_CLEARANCE + 2.0
assert LEAF_LENGTH > 2 * MOUNT_EDGE
assert AXIAL_GAP > 0

root = Path(os.environ.get("HYDROFOAM_HINGE_OUTPUT", str(Path.home() / "JL1976" / "Hydrofoam_Hinge_Coupon")))
if root.exists() and any(root.iterdir()):
    raise RuntimeError("Output folder is not empty; refusing overwrite: " + str(root))
root.mkdir(parents=True, exist_ok=True)
doc = App.newDocument("Hydrofoam_Hinge_Coupon_WIP")

def leaf(name, z, xshift):
    # Pin axis is Y. Leaves extend in X, with independent barrel stations in Y.
    box = Part.makeBox(LEAF_LENGTH, LEAF_WIDTH, LEAF_THICKNESS,
                       App.Vector(xshift, -LEAF_WIDTH / 2, z - LEAF_THICKNESS / 2))
    barrel = Part.makeCylinder(BARREL_OD / 2, BARREL_LENGTH,
                               App.Vector(0, -BARREL_LENGTH / 2, 0), App.Vector(0, 1, 0))
    bore = Part.makeCylinder(PIN_DIAMETER / 2 + RADIAL_CLEARANCE,
                             BARREL_LENGTH + 2, App.Vector(0, -BARREL_LENGTH / 2 - 1, 0),
                             App.Vector(0, 1, 0))
    shape = box.fuse(barrel).cut(bore).removeSplitter()
    hole = Part.makeCylinder(MOUNT_HOLE / 2, LEAF_THICKNESS + 2,
                             App.Vector(xshift + LEAF_LENGTH - MOUNT_EDGE, 0, z - LEAF_THICKNESS / 2 - 1),
                             App.Vector(0, 0, 1))
    shape = shape.cut(hole).removeSplitter()
    if not shape.isValid():
        raise RuntimeError("Invalid coupon geometry: " + name)
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Shape = shape
    return obj

# Print separately, not in an assembled pose. Fit is evaluated using
# physical pin and test rotation after printing.
fixed = leaf("Fixed_leaf_coupon", 0, 0)
moving = leaf("Moving_leaf_coupon", 0, -LEAF_LENGTH)
moving.Placement.Base = App.Vector(0, 20, 0)
doc.recompute()
for obj in (fixed, moving):
    Mesh.export([obj], str(root / (obj.Name + ".stl")))
doc.saveAs(str(root / "Hydrofoam_Hinge_Coupon_WIP.FCStd"))
(root / "NOT_APPROVED.txt").write_text(
    "Fit coupon only. Dimensions provisional. No kinematic collision, load, fatigue, "
    "servo travel, water seal or final-master photogrammetry approval.\\n",
    encoding="utf-8")
print("WIP hinge coupons written to", root)
