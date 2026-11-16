"""Hydrofoam v419: parametric, removable skid-to-float interface test coupon.

Run inside FreeCAD's Python console or FreeCADCmd. This is a separate
mechanical fit prototype, NOT a reconstruction of the Master hull.
Dimensions are provisional until the original float underside is measured.
Exports are deliberately named WIP. No final acceptance is implied.
"""
import json
import math
from pathlib import Path

import FreeCAD as App
import Part
import MeshPart

# mm; +Z away from ground. Coupon X runs along float.
P = {
    "length": 90.0, "width": 24.0, "skid_thickness": 4.0,
    "mount_height": 8.0, "mount_width": 18.0,
    "bolt_spacing": 56.0, "bolt_diameter": 3.4,
    "counterbore_diameter": 6.5, "counterbore_depth": 2.0,
    "edge_margin_min": 5.0, "tessellation_mm": 0.12,
}
OUT = Path(__file__).resolve().parent.parent / "artifacts" / "v419_skid_coupon"
OUT.mkdir(parents=True, exist_ok=True)

def check(p):
    keys = ("length", "width", "skid_thickness", "mount_height",
            "mount_width", "bolt_spacing", "bolt_diameter",
            "counterbore_diameter", "counterbore_depth")
    if any(not isinstance(p[k], (float, int)) or not math.isfinite(p[k]) or p[k] <= 0 for k in keys):
        raise ValueError("Dimensions must be finite positive millimetres")
    if p["mount_width"] >= p["width"]:
        raise ValueError("Mount must fit within skid width")
    if p["bolt_spacing"] + p["counterbore_diameter"] + 2*p["edge_margin_min"] > p["length"]:
        raise ValueError("Insufficient bolt end margins")
    if p["counterbore_diameter"] <= p["bolt_diameter"]:
        raise ValueError("Counterbore must exceed through-hole")
    if p["counterbore_depth"] >= p["skid_thickness"]:
        raise ValueError("Counterbore breaks through skid")
    if p["bolt_diameter"] + 2*p["edge_margin_min"] > p["mount_width"]:
        raise ValueError("Mount has insufficient side wall")

check(P)
doc = App.newDocument("Hydrofoam_v419_WIP_skid_coupon")
V = App.Vector
skid = Part.makeBox(P["length"], P["width"], P["skid_thickness"],
                    V(-P["length"]/2, -P["width"]/2, 0))
mount = Part.makeBox(P["length"], P["mount_width"], P["mount_height"],
                     V(-P["length"]/2, -P["mount_width"]/2, P["skid_thickness"]))
solid = skid.fuse(mount).removeSplitter()
for x in (-P["bolt_spacing"]/2, P["bolt_spacing"]/2):
    through = Part.makeCylinder(P["bolt_diameter"]/2,
                                P["skid_thickness"]+P["mount_height"]+2,
                                V(x, 0, -1))
    # Heads recessed into the ground-facing skid face.
    recess = Part.makeCylinder(P["counterbore_diameter"]/2,
                               P["counterbore_depth"], V(x, 0, 0))
    solid = solid.cut(through.fuse(recess))
solid = solid.removeSplitter()
if solid.isNull() or not solid.isValid() or len(solid.Solids) != 1:
    raise RuntimeError("Coupon is not a single valid solid")
obj = doc.addObject("PartDesign::Feature", "WIP_SkidMountCoupon")
obj.Shape = solid
for name, val in P.items():
    obj.addProperty("App::PropertyFloat", name, "ProvisionalDimensions")
    setattr(obj, name, val)
doc.recompute()
doc.saveAs(str(OUT / "v419_WIP_skid_mount_coupon.FCStd"))
mesh = MeshPart.meshFromShape(Shape=solid, LinearDeflection=P["tessellation_mm"],
                              AngularDeflection=math.radians(12), Relative=False)
mesh.write(str(OUT / "v419_WIP_skid_mount_coupon.stl"))
report = {
    "status": "WIP_COUPON_NOT_MASTER_GEOMETRY",
    "dimensions_mm": P,
    "solid_valid": solid.isValid(),
    "solid_count": len(solid.Solids),
    "volume_mm3": round(solid.Volume, 3),
    "bounding_box_mm": [round(solid.BoundBox.XLength, 3),
                        round(solid.BoundBox.YLength, 3),
                        round(solid.BoundBox.ZLength, 3)],
    "open_items": [
        "Float underside dimensions and fastening inserts not measured",
        "No load, pull-out, wear, sand, grass or hydrofoil clearance tests",
        "No watertightness or Master-image silhouette acceptance",
        "No material shrinkage or P2S slicer fit verification"
    ],
    "final_release_authorized": False
}
(OUT / "v419_WIP_qa.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
print(json.dumps(report, indent=2))
