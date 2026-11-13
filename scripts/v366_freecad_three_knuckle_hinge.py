"""Hydrofoam v366: parametric three-knuckle hinge mechanism prototype.
Run with FreeCAD Python (FreeCADCmd or GUI). Units mm. WIP, not flight approved.
The two leaves have alternating barrel stations along the Y hinge axis.
No change to the master reference, v333 Blender geometry or README.
"""
import os, json, math
from pathlib import Path
import FreeCAD as App
import Part
import Mesh

PIN_D = 2.0
BORE_RADIAL_CLEARANCE = 0.22
BARREL_OD = 6.0
KNUCKLE_LENGTH = 6.0
AXIAL_CLEARANCE = 0.35
LEAF_SPAN = 19.0
LEAF_THICK = 2.8
LEAF_HALF_WIDTH = 10.0
MOUNT_HOLE_D = 2.6
TEST_ANGLES_DEG = list(range(-35, 36, 5))
# In the installed assembly the hinge center is the origin and axis is +Y.
# Station layout: fixed [-9.35,-3.35] and [3.35,9.35];
# moving [-3.0,3.0]. Axial gap 0.35 mm each side.
stations_fixed = [-9.35, 3.35]
stations_moving = [-3.0]
axis = App.Vector(0, 1, 0)
origin = App.Vector(0, 0, 0)
r_bore = PIN_D / 2 + BORE_RADIAL_CLEARANCE

if BARREL_OD / 2 - r_bore < 1.4:
    raise ValueError("Insufficient barrel wall")
if abs(stations_fixed[0] + KNUCKLE_LENGTH + AXIAL_CLEARANCE - stations_moving[0]) > 1e-8:
    raise ValueError("Station gap mismatch")
if abs(stations_moving[0] + KNUCKLE_LENGTH + AXIAL_CLEARANCE - stations_fixed[1]) > 1e-8:
    raise ValueError("Station gap mismatch")

def knuckle(y):
    outer = Part.makeCylinder(BARREL_OD / 2, KNUCKLE_LENGTH, App.Vector(0,y,0), axis)
    bore = Part.makeCylinder(r_bore, KNUCKLE_LENGTH+0.2, App.Vector(0,y-0.1,0), axis)
    return outer.cut(bore)

def leaf(moving):
    # Leaves extend away from hinge axis on opposite sides.
    x0 = -LEAF_SPAN if moving else 0.0
    plate = Part.makeBox(LEAF_SPAN, 2*LEAF_HALF_WIDTH, LEAF_THICK,
                         App.Vector(x0,-LEAF_HALF_WIDTH,-LEAF_THICK/2))
    # Plate and knuckle have real radial overlap, avoiding disconnected solids.
    for y in (stations_moving if moving else stations_fixed):
        plate = plate.fuse(knuckle(y))
    # Through holes in Z for fastening to existing control surfaces.
    hole_x = -LEAF_SPAN+5 if moving else LEAF_SPAN-5
    for y in (-6.0,6.0):
        cutter = Part.makeCylinder(MOUNT_HOLE_D/2, LEAF_THICK+2,
                    App.Vector(hole_x,y,-LEAF_THICK/2-1), App.Vector(0,0,1))
        plate = plate.cut(cutter)
    # Through-bore is cut again through plate overlap, so the pin can pass.
    bore = Part.makeCylinder(r_bore, 2*LEAF_HALF_WIDTH+2,
                            App.Vector(0,-LEAF_HALF_WIDTH-1,0), axis)
    return plate.cut(bore).removeSplitter()

fixed = leaf(False)
moving = leaf(True)
pin = Part.makeCylinder(PIN_D/2, 2*LEAF_HALF_WIDTH+1,
                        App.Vector(0,-LEAF_HALF_WIDTH-0.5,0), axis)
for name, shape in (("fixed",fixed),("moving",moving),("pin",pin)):
    if not shape.isValid():
        raise RuntimeError(name+" invalid BREP")
    if len(shape.Solids)!=1:
        raise RuntimeError(name+" is not one connected solid")

# BREP common-volume test is a conservative interference indicator. 
# Tangencies, mesh print tolerances and real bending are not certified.
sweep=[]
for angle in TEST_ANGLES_DEG:
    moved=moving.copy()
    moved.rotate(origin,axis,angle)
    overlap=fixed.common(moved).Volume
    pin_overlap=moved.common(pin).Volume
    sweep.append(dict(angle_deg=angle,leaf_overlap_mm3=round(overlap,6),
                      moving_pin_overlap_mm3=round(pin_overlap,6)))
# Leaves overlap in the 0-degree pose due to their plates meeting at x=0
# only at an ideal boundary. Any nonzero intersection is a blocker.
passes = all(s["leaf_overlap_mm3"] < 1e-5 and s["moving_pin_overlap_mm3"] < 1e-5 for s in sweep)
out=Path(os.environ.get("HYDROFOAM_V366_OUTPUT",str(Path.home()/"JL1976"/"Hydrofoam_v366_WIP")))
if out.exists() and any(out.iterdir()):
    raise RuntimeError("Refusing to overwrite nonempty output: "+str(out))
out.mkdir(parents=True,exist_ok=True)
doc=App.newDocument("Hydrofoam_v366_Hinge_WIP")
for name,shape in (("Fixed_leaf",fixed),("Moving_leaf",moving),("Pin_reference",pin)):
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Shape=shape
    Mesh.export([obj],str(out/(name+".stl")))
doc.recompute()
doc.saveAs(str(out/"Hydrofoam_v366_Hinge_WIP.FCStd"))
report={"status":"PASS_GEOMETRIC_SWEEP_ONLY" if passes else "FAIL_INTERFERENCE",
        "angles":sweep,"units":"mm","pin_diameter_mm":PIN_D,
        "bore_radial_clearance_mm":BORE_RADIAL_CLEARANCE,
        "axial_clearance_mm":AXIAL_CLEARANCE,
        "limitations":["Standalone provisional hinge, not fitted to v333",
        "No servo mount, horn, linkage, load, fatigue or P2S print acceptance",
        "No master-photo comparison or land/water/air certification"]}
(out/"v366_sweep_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({"output":str(out),"result":report["status"]}))
if not passes:
    raise RuntimeError("Hinge sweep interference: see JSON report")
