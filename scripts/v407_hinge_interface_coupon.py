"""v407: FreeCAD hinge and servo mounting interface coupon, WIP only.
Mechanical dimensions are explicit assumptions, not measured aircraft dimensions.
Produces a printable, separated hinge leaf set and a mounting plate.
Run in FreeCAD's Python interpreter; no auto-execution on import.
"""
import json
from pathlib import Path

PIN_D = 2.0
RADIAL_CLEARANCE = 0.25
KNUCKLE_OUTER_D = 6.0
LEAF_THICKNESS = 3.0
LEAF_DEPTH = 14.0
SPAN = 42.0
KNUCKLE_LEN = 8.0
AXIAL_GAP = 0.5
SCREW_D = 2.2
SCREW_PITCH = 20.0

def build():
    import FreeCAD as App
    import Part
    from FreeCAD import Vector as V
    from FreeCAD import Mesh
    output = Path(__file__).resolve().parents[1] / "qa_runs" / "v407_hinge_interface"
    output.mkdir(parents=True, exist_ok=True)
    doc = App.newDocument("v407_hinge_interface")
    bore_d = PIN_D + 2 * RADIAL_CLEARANCE
    axis_y = 0
    axis_z = KNUCKLE_OUTER_D / 2
    def leaf(name, y0, segments):
        plate = Part.makeBox(SPAN, LEAF_DEPTH, LEAF_THICKNESS,
                             V(-SPAN/2, y0, 0))
        for cx in (-SCREW_PITCH/2, SCREW_PITCH/2):
            drill = Part.makeCylinder(SCREW_D/2, LEAF_THICKNESS+2,
                                       V(cx, y0+LEAF_DEPTH/2, -1))
            plate = plate.cut(drill)
        for a,b in segments:
            knuckle = Part.makeCylinder(KNUCKLE_OUTER_D/2, b-a,
                                        V(a, axis_y, axis_z), V(1,0,0))
            bore = Part.makeCylinder(bore_d/2, b-a+2,
                                     V(a-1, axis_y, axis_z), V(1,0,0))
            plate = plate.fuse(knuckle.cut(bore))
        plate = plate.removeSplitter()
        obj = doc.addObject("PartDesign::Feature", name)
        obj.Shape = plate
        return obj
    # Axial intervals deliberately do not overlap.
    # Leaf roots overlap the knuckle volume to form continuous solids.
    left = leaf("FixedLeaf", -LEAF_DEPTH, [(-20,-12), (12,20)])
    right = leaf("MovingLeaf", 0, [(-11.5,-3.5), (3.5,11.5)])
    pin = doc.addObject("PartDesign::Feature", "PinReferenceOnly")
    pin.Shape = Part.makeCylinder(PIN_D/2, 43, V(-21.5,0,axis_z), V(1,0,0))
    # Pin reference is not printed as part of the leaves.
    doc.recompute()
    results = {}
    for obj in (left,right,pin):
        s=obj.Shape
        results[obj.Name] = dict(valid=s.isValid(), solids=len(s.Solids),
                                 volume_mm3=round(s.Volume,3))
        Mesh.export([obj], str(output / (obj.Name+".stl")))
    doc.saveAs(str(output / "v407_hinge_interface.FCStd"))
    # Do not mistake common-volume clearance for a physical range-of-motion test.
    overlap = left.Shape.common(right.Shape).Volume
    pin_overlap = pin.Shape.common(left.Shape).Volume + pin.Shape.common(right.Shape).Volume
    qa = dict(version="v407", status="WIP_ONLY", assumed_dimensions_mm=dict(
        pin_d=PIN_D, radial_clearance=RADIAL_CLEARANCE,
        knuckle_outer_d=KNUCKLE_OUTER_D, axial_gap=AXIAL_GAP),
        objects=results, leaf_intersection_mm3=overlap,
        pin_leaf_intersection_mm3=pin_overlap,
        passed_static_geometry=all(v["valid"] and v["solids"]==1 for v in results.values())
          and overlap < 0.001 and pin_overlap < 0.001,
        limitations=["Not installed in the Final-Master aircraft",
                     "No full-angle moving sweep or servo linkage",
                     "No load test or P2S print tolerance calibration",
                     "No land, water or air acceptance"])
    (output/"v407_hinge_qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
    if not qa["passed_static_geometry"]:
        raise RuntimeError("v407 static geometry audit failed: "+str(qa))
    return qa

if __name__ == "__main__":
    build()
