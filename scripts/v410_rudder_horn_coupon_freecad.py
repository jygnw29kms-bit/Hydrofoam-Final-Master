"""Hydrofoam v410: parametric printable rudder horn coupon, NOT flight-approved.
Run with FreeCAD Python console or FreeCADCmd. Units: mm.
Geometry assumptions must be replaced by measured linkage/servo dimensions.
"""
import FreeCAD as App
import Part
import Mesh
import json
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "cad" / "v410_horn_coupon"
OUT.mkdir(parents=True, exist_ok=True)
P = dict(base_width=16.0, base_length=22.0, base_thickness=3.2,
         upright_thickness=3.2, upright_length=12.0, upright_height=17.0,
         hole_diameter=2.0, hole_center_height=13.0,
         mounting_diameter=2.6, mounting_spacing=13.0)
doc = App.newDocument("Hydrofoam_v410_HornCoupon")
V = App.Vector
base = Part.makeBox(P["base_width"], P["base_length"], P["base_thickness"],
                    V(-8,-11,0))
upright = Part.makeBox(P["upright_thickness"], P["upright_length"],
                       P["upright_height"], V(-1.6,-6,3.2))
shape = base.fuse(upright).removeSplitter()
# Linkage pin bore runs along X, perpendicular to upright.
pin = Part.makeCylinder(P["hole_diameter"]/2, 8,
                        V(-4,0,P["hole_center_height"]), V(1,0,0))
shape = shape.cut(pin)
for y in (-P["mounting_spacing"]/2, P["mounting_spacing"]/2):
    bore = Part.makeCylinder(P["mounting_diameter"]/2, 8,
                             V(0,y,-1), V(0,0,1))
    shape = shape.cut(bore)
shape = shape.removeSplitter()
obj = doc.addObject("PartDesign::Feature","HornCoupon")
obj.Shape = shape
doc.recompute()
valid = bool(shape.isValid() and len(shape.Solids)==1 and shape.Volume>0)
report = {"version":"v410","component":"rudder_horn_coupon",
          "units":"mm","parameters":P,"solid_valid":valid,
          "solid_count":len(shape.Solids),"volume_mm3":shape.Volume,
          "status":"GEOMETRY_ONLY_NOT_INTEGRATED",
          "limitations":["assumed dimensions","no structural load test",
                         "no servo/linkage clearance proof",
                         "no complete control-surface assembly"]}
doc.saveAs(str(OUT/"rudder_horn_coupon.FCStd"))
if valid:
    Mesh.export([obj],str(OUT/"rudder_horn_coupon.stl"))
(OUT/"qa.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
if not valid:
    raise RuntimeError("Horn geometry invalid")
