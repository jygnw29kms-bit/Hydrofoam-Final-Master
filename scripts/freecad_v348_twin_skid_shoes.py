"""Hydrofoam v348: parametric, replaceable twin skid wear shoes (FreeCAD Python).

Run on Jens-PC using FreeCAD Python console:
    exec(open("scripts/freecad_v348_twin_skid_shoes.py", encoding="utf-8").read())
Requires a measured JSON config at docs/v348_skid_measurements.json.
Creates FCStd, STEP and STL only after validation. NO default dimensions,
no change to the external Final-Master silhouette, no operational approval.
Coordinate convention: X forward, Y right, Z upward; millimetres.
"""
import json, math, hashlib
from pathlib import Path
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "reference/FINAL_MASTER_ORIGINAL.jpeg"
EXPECTED = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
CONFIG = ROOT / "docs/v348_skid_measurements.json"
OUT = ROOT / "cad/v348_skid_shoes_WIP"

def positive(d, key):
    value = d[key]
    if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or value <= 0:
        raise ValueError("Measured positive finite value required: " + key)
    return float(value)

def build():
    if hashlib.sha256(MASTER.read_bytes()).hexdigest() != EXPECTED:
        raise RuntimeError("Original Final Master SHA256 mismatch")
    if not CONFIG.exists():
        raise FileNotFoundError("Measured skid geometry required: " + str(CONFIG))
    d = json.loads(CONFIG.read_text(encoding="utf-8"))
    required = ("length_mm", "width_mm", "thickness_mm", "center_y_mm",
                "mount_hole_diameter_mm", "mount_pitch_mm", "end_margin_mm",
                "minimum_wall_mm", "bottom_z_mm")
    if any(k not in d for k in required):
        raise ValueError("Missing measured parameters: " + str([k for k in required if k not in d]))
    length, width, thick, cy, hole, pitch, margin, wall = [positive(d,k) for k in required[:-1]]
    z = d["bottom_z_mm"]
    if not isinstance(z, (float,int)) or isinstance(z,bool) or not math.isfinite(z):
        raise ValueError("bottom_z_mm must be measured and finite")
    if width <= hole + 2*wall or thick < wall or length <= pitch + 2*margin:
        raise ValueError("Insufficient material around holes or beyond mount centers")
    if cy <= width/2: raise ValueError("Left and right skids would overlap centerline")
    if pitch <= hole + 2*wall: raise ValueError("Mount holes too close")
    if d.get("measurements_verified") is not True:
        raise ValueError("measurements_verified must be true after physical CAD measurement")
    # Underside shoes: flat wear surfaces, existing skid footprint only.
    # Two vertical through holes per shoe, no invented external appendages.
    doc = App.newDocument("Hydrofoam_v348_TwinSkidShoes_WIP")
    solids=[]
    for side, sign in (("LEFT",-1),("RIGHT",1)):
        center_y=sign*cy
        block=Part.makeBox(length,width,thick,
                           App.Vector(-length/2,center_y-width/2,z))
        for x in (-pitch/2,pitch/2):
            cutter=Part.makeCylinder(hole/2,thick+2,
                                     App.Vector(x,center_y,z-1))
            block=block.cut(cutter)
        block=block.removeSplitter()
        if not block.isValid() or not block.isClosed() or len(block.Solids)!=1:
            raise RuntimeError(side+" invalid or non-solid mesh precursor")
        obj=doc.addObject("PartDesign::Feature","WearShoe_"+side)
        obj.Label="WIP replaceable skid shoe "+side
        obj.Shape=block
        obj.addProperty("App::PropertyString","Source","Traceability")
        obj.Source="Measured v348 skid configuration; not Final-Master approved"
        solids.append(obj)
    doc.recompute()
    OUT.mkdir(parents=True,exist_ok=True)
    doc.saveAs(str(OUT/"Hydrofoam_v348_TwinSkidShoes_WIP.FCStd"))
    Part.export(solids,str(OUT/"Hydrofoam_v348_TwinSkidShoes_WIP.step"))
    qa={"version":"v348","master_sha256":EXPECTED,"measurements":d,
        "parts":[],"accepted":False,
        "pending":["Compare installed outline to original top/side/perspective",
                   "Verify mounting hole positions against actual float inserts",
                   "Print PETG coupons and measure clearance/fit",
                   "Verify wear, ground contact, foil ground clearance and three-mode tests"]}
    for obj in solids:
        shape=obj.Shape
        qa["parts"].append({"name":obj.Name,"solid_count":len(shape.Solids),
          "is_valid":shape.isValid(),"volume_mm3":shape.Volume,
          "bounding_box_mm":[shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength]})
        mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.08,AngularDeflection=math.radians(12),Relative=False)
        mesh.write(str(OUT/(obj.Name+".stl")))
    (OUT/"V348_SKID_SHOES_QA_WIP.json").write_text(json.dumps(qa,indent=2)+"\n",encoding="utf-8")
    print("Created measured twin skid shoes, WIP ONLY:",OUT)
    return doc

build()
