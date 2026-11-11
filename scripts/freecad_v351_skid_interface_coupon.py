"""Hydrofoam v351: FreeCAD replaceable skid interface coupon, NOT master geometry.

Run in FreeCAD's Python console or FreeCADCmd:
    exec(open("scripts/freecad_v351_skid_interface_coupon.py", encoding="utf-8").read())

Builds a manufacturable PETG wear shoe, captive-nut carrier and clearance
coupon with actual boolean cuts. Dimensions are explicit *test dimensions*,
not inferred from the final-master photograph. Fit the actual float underside
before integrating. Outputs STEP, STL, FCStd and machine-readable checks.
"""
import json
from pathlib import Path
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parent.parent if "__file__" in globals() else Path.cwd()
OUT = ROOT / "exports" / "v351_skid_coupon_WIP"
OUT.mkdir(parents=True, exist_ok=True)
DOC = App.newDocument("Hydrofoam_v351_skid_interface_WIP")
V = App.Vector

# Prototype sizes [mm]; NOT an assertion about actual float dimensions.
length = 110.0
width = 20.0
shoe_thickness = 3.2
carrier_thickness = 5.0
carrier_width = 14.0
bolt_pitch = 76.0
bolt_clearance_d = 3.4
head_counterbore_d = 6.2
head_counterbore_depth = 1.4
nut_af = 5.7
nut_depth = 2.6
edge_margin = (length-bolt_pitch)/2
assert edge_margin > head_counterbore_d
assert carrier_thickness > nut_depth
assert shoe_thickness > head_counterbore_depth

def cylinder(radius, height, x, y, z):
    return Part.makeCylinder(radius, height, V(x,y,z))

# Flat wear-shoe blank. Fore/aft shaping is intentionally deferred until
# the underside is measured: this coupon must not invent float contours.
shoe = Part.makeBox(length,width,shoe_thickness,V(-length/2,-width/2,0))
for x in (-bolt_pitch/2,bolt_pitch/2):
    shoe = shoe.cut(cylinder(bolt_clearance_d/2,shoe_thickness+2,x,0,-1))
    shoe = shoe.cut(cylinder(head_counterbore_d/2,head_counterbore_depth+0.01,
                             x,0,0))
shoe = shoe.removeSplitter()

# Carrier with actual through holes and hexagonal nut pockets on upper face.
carrier = Part.makeBox(length,carrier_width,carrier_thickness,
                       V(-length/2,-carrier_width/2,shoe_thickness))
for x in (-bolt_pitch/2,bolt_pitch/2):
    carrier = carrier.cut(cylinder(bolt_clearance_d/2,carrier_thickness+2,
                                  x,0,shoe_thickness-1))
    # Hexagonal prism: across-flats nut dimension, plus provisional 0.3mm clearance.
    import math
    across_flats = nut_af+0.3
    circumradius = across_flats/math.sqrt(3)
    verts = [V(x+circumradius*math.cos(math.pi/6+i*math.pi/3),
               circumradius*math.sin(math.pi/6+i*math.pi/3),
               shoe_thickness+carrier_thickness-nut_depth)
             for i in range(6)]
    verts.append(verts[0])
    hexface = Part.Face(Part.Wire(Part.makePolygon(verts).Edges))
    carrier = carrier.cut(hexface.extrude(V(0,0,nut_depth+0.1)))
carrier = carrier.removeSplitter()

def add(name, shape, color):
    obj=DOC.addObject("PartDesign::Feature",name)
    obj.Shape=shape
    obj.ViewObject.ShapeColor=color
    return obj

shoe_obj=add("Replaceable_PETG_Wear_Shoe_WIP",shoe,(0.12,0.12,0.13))
carrier_obj=add("Captive_Nut_Carrier_WIP",carrier,(0.9,0.42,0.12))
DOC.recompute()

checks={}
for name,shape in (("shoe",shoe),("carrier",carrier)):
    checks[name]={"valid":shape.isValid(),
                  "closed":shape.isClosed(),
                  "solids":len(shape.Solids),
                  "volume_mm3":round(shape.Volume,3),
                  "bounds_mm":[round(shape.BoundBox.XLength,3),
                               round(shape.BoundBox.YLength,3),
                               round(shape.BoundBox.ZLength,3)]}
    if not shape.isValid() or not shape.isClosed() or len(shape.Solids)!=1:
        raise RuntimeError(name+" is not a valid single closed solid")
    Part.export([shoe_obj if name=="shoe" else carrier_obj],
                str(OUT/(name+"_WIP.step")))
    mesh=MeshPart.meshFromShape(Shape=shape,LinearDeflection=0.12,
                                AngularDeflection=0.35,Relative=False)
    mesh.write(str(OUT/(name+"_WIP.stl")))

DOC.saveAs(str(OUT/"Hydrofoam_v351_skid_interface_coupon_WIP.FCStd"))
report={"version":"v351","status":"UNVALIDATED_WIP","prototype_only":True,
        "dimensions_mm":{"length":length,"width":width,
        "shoe_thickness":shoe_thickness,"carrier_thickness":carrier_thickness,
        "bolt_pitch":bolt_pitch,"bolt_clearance_d":bolt_clearance_d,
        "counterbore_d":head_counterbore_d,"nut_across_flats_nominal":nut_af},
        "geometry_checks":checks,
        "unverified":["fit to actual Final Master float underside",
        "fastener head clearance and nut retention","print shrinkage",
        "ground wear on hard surface, grass and firm sand",
        "hydrodynamic drag and seal integrity",
        "foil clearance in every ground attitude",
        "mass and flight CG impact"]}
(OUT/"V351_SKID_INTERFACE_QA_WIP.json").write_text(
    json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("v351 WIP artifacts:",OUT)
