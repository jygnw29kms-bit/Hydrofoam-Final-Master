"""v347 WIP: parametric, replaceable left/right skid wear shoes for land mode.

Run in FreeCAD's Python console or FreeCADCmd:
    exec(open("scripts/freecad_v347_skid_wear_shoes.py", encoding="utf-8").read())

Coordinates in mm. +X forward, +/-Y sides, +Z up.
These are *separate prototype parts*, not fitted to the master hull.
Measured hull mounting coordinates, contact pressures, sand/grass testing,
foil ground clearance and retention loads are still required.
"""
import json
from pathlib import Path

import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "cad" / "v347_skid_shoes_WIP"
OUT.mkdir(parents=True, exist_ok=True)

# Engineering prototype dimensions, NOT master-derived measurements.
LENGTH = 115.0
WIDTH = 19.0
THICKNESS = 4.0
NOSE_RISE = 7.0
NOSE_LENGTH = 24.0
SLOT_LENGTH = 9.0
SLOT_WIDTH = 3.6
SLOT_X = (-30.0, 30.0)
SIDE_OFFSET = 83.0  # placeholder only; replace with measured float datum
assert LENGTH > 2 * max(abs(x) for x in SLOT_X) + SLOT_LENGTH
assert NOSE_LENGTH < LENGTH / 2
assert THICKNESS > 0 and SLOT_WIDTH < WIDTH

doc = App.newDocument("Hydrofoam_v347_WIP_SkidShoes")

def capsule_slot(x, y):
    r = SLOT_WIDTH / 2.0
    straight = SLOT_LENGTH - SLOT_WIDTH
    # Shape constructed in XY, then extruded fully through the shoe.
    box = Part.makeBox(straight, SLOT_WIDTH, THICKNESS + 4,
                       App.Vector(x - straight / 2, y - r, -2))
    a = Part.makeCylinder(r, THICKNESS + 4,
                          App.Vector(x - straight / 2, y, -2))
    b = Part.makeCylinder(r, THICKNESS + 4,
                          App.Vector(x + straight / 2, y, -2))
    return box.fuse(a).fuse(b)

def shoe(side):
    # A raised nose, not a low overhang: five-sided longitudinal section.
    # The contact plane is z=0, so the forward tip cannot dig in.
    x0 = -LENGTH / 2
    x1 = LENGTH / 2 - NOSE_LENGTH
    x2 = LENGTH / 2
    pts = [(x0, 0), (x1, 0), (x2, NOSE_RISE),
           (x2, NOSE_RISE + THICKNESS),
           (x1, THICKNESS), (x0, THICKNESS)]
    edges = []
    for i, (x,z) in enumerate(pts):
        nx,nz = pts[(i+1) % len(pts)]
        edges.append(Part.makeLine(App.Vector(x, -WIDTH/2, z),
                                   App.Vector(nx, -WIDTH/2, nz)))
    shape = Part.Face(Part.Wire(edges)).extrude(App.Vector(0, WIDTH, 0))
    for x in SLOT_X:
        shape = shape.cut(capsule_slot(x, 0))
    shape = shape.removeSplitter()
    if shape.isNull() or not shape.isValid() or len(shape.Solids) != 1:
        raise RuntimeError("Invalid shoe solid: " + side)
    if not shape.isClosed():
        raise RuntimeError("Shoe not watertight: " + side)
    obj = doc.addObject("PartDesign::Feature", "SkidWear_" + side)
    obj.Label = "WIP replaceable skid wear shoe " + side
    obj.Shape = shape
    obj.Placement.Base.y = SIDE_OFFSET * (1 if side == "R" else -1)
    obj.addProperty("App::PropertyString", "Status", "QA")
    obj.Status = "WIP, mounting geometry not verified against master"
    return obj

parts = [shoe("L"), shoe("R")]
doc.recompute()
doc.saveAs(str(OUT / "Hydrofoam_v347_skid_shoes_WIP.FCStd"))
rows = []
for obj in parts:
    # Export shape in local print orientation; no 83 mm assembly offset.
    shape = obj.Shape.copy()
    shape.translate(App.Vector(0, -obj.Placement.Base.y, 0))
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.12,
                                  AngularDeflection=0.20, Relative=False)
    path = OUT / (obj.Name + "_WIP.stl")
    mesh.write(str(path))
    rows.append({"part": obj.Name, "stl": path.name,
                 "solid_count": len(shape.Solids), "closed": shape.isClosed(),
                 "volume_mm3": round(shape.Volume, 2),
                 "bbox_mm": [round(shape.BoundBox.XLength, 2),
                             round(shape.BoundBox.YLength, 2),
                             round(shape.BoundBox.ZLength, 2)]})
qa = {"version": "v347", "status": "WIP_NOT_ACCEPTED",
      "mode": "land", "parts": rows,
      "geometry_inputs_are_measured": False,
      "checks_pending": ["float surface fit and screw retention",
                         "foil/prop clearance at pitch and roll",
                         "PETG layer direction and creep",
                         "sand abrasion and skid wear",
                         "grass drag, hard-ground steering and acceleration",
                         "hydrodynamic impact and sealing after installation",
                         "three-mode vehicle testing"],
      "master_image_modified": False}
(OUT / "V347_SKID_WEAR_SHOE_QA_WIP.json").write_text(
    json.dumps(qa, indent=2) + "\n", encoding="utf-8")
print("v347 WIP shoe CAD/STL and QA exported:", OUT)
