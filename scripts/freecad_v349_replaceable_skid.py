"""v349: parametric, removable PETG skid prototype for FreeCAD.

Run in FreeCAD Python console or with FreeCADCmd:
    exec(open('scripts/freecad_v349_replaceable_skid.py', encoding='utf-8').read())

Creates two mirrored, separate solids with recessed screw holes. These are
engineering coupons, NOT Master-image-matched final parts. All dimensions
are provisional and must be replaced by measured CAD mounting interfaces.
No waterfoil or fuselage geometry is changed.
"""
import FreeCAD as App
import Part
from FreeCAD import Vector

# Millimetres. Provisional prototype dimensions, not measured master values.
LENGTH = 145.0
WIDTH = 20.0
THICKNESS = 4.0
END_RADIUS = 8.0
SCREW_DIAMETER = 3.4  # M3 clearance; verify print shrinkage
HEAD_DIAMETER = 6.5
HEAD_DEPTH = 1.7
SCREW_INSET = 22.0
CENTER_SPACING = 155.0  # must be measured against actual float/skid seats

assert LENGTH > 2 * SCREW_INSET > HEAD_DIAMETER
assert WIDTH > HEAD_DIAMETER and THICKNESS > HEAD_DEPTH > 0
assert END_RADIUS <= WIDTH / 2
assert SCREW_DIAMETER < HEAD_DIAMETER

doc = App.newDocument("Hydrofoam_v349_Skid_Prototype_WIP")


def skid(side):
    # XY footprint: rounded ends avoid snagging on grass and sand.
    # Capsule is built by fusing a central box with two cylindrical ends.
    x0 = -LENGTH / 2 + END_RADIUS
    straight = LENGTH - 2 * END_RADIUS
    core = Part.makeBox(straight, WIDTH, THICKNESS,
                        Vector(x0, -WIDTH / 2, 0))
    end1 = Part.makeCylinder(END_RADIUS, THICKNESS,
                             Vector(x0, 0, 0))
    end2 = Part.makeCylinder(END_RADIUS, THICKNESS,
                             Vector(x0 + straight, 0, 0))
    shape = core.fuse(end1).fuse(end2).removeSplitter()
    for x in (-LENGTH / 2 + SCREW_INSET, LENGTH / 2 - SCREW_INSET):
        through = Part.makeCylinder(SCREW_DIAMETER / 2, THICKNESS + 2,
                                    Vector(x, 0, -1))
        counterbore = Part.makeCylinder(HEAD_DIAMETER / 2, HEAD_DEPTH,
                                        Vector(x, 0, THICKNESS - HEAD_DEPTH))
        shape = shape.cut(through).cut(counterbore)
    shape = shape.removeSplitter()
    if not shape.isValid() or len(shape.Solids) != 1:
        raise RuntimeError("Skid must be one valid solid")
    obj = doc.addObject("PartDesign::Feature", "Skid_" + side)
    obj.Label = "WIP removable PETG skid " + side
    obj.Shape = shape
    obj.Placement.Base = Vector(0, CENTER_SPACING / 2 * (1 if side == "L" else -1), 0)
    return obj


left = skid("L")
right = skid("R")
doc.recompute()
import os
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "cad")
os.makedirs(out, exist_ok=True)
doc.saveAs(os.path.join(out, "Hydrofoam_v349_replaceable_skids_WIP.FCStd"))
# Export separate STL for print-orientation experiments. NOT validated P2S profiles.
for obj in (left, right):
    Part.export([obj], os.path.join(out, obj.Name + "_v349_WIP.stl"))
print("v349 prototype exported; verify mating surfaces, fastener retention, PETG wear and foil clearance before use")
