"""v406: Parametric servo-tray mounting coupon for FreeCAD 1.1.
NOT a verified servo fit or installed Hydrofoam control assembly.
Run inside FreeCAD Python console or FreeCADCmd with a FreeCAD Python runtime.
Dimensions in mm; change only after measuring the physical servo.
"""
import FreeCAD as App
import Part, json, pathlib
from FreeCAD import Vector

# Deliberately explicit engineering assumptions, not vendor dimensions.
SERVO_BODY=(23.0,12.0,24.0)
BODY_CLEARANCE=0.40
WALL=2.4
FLOOR=3.0
SCREW_D=2.2
HOLE_SPACING=29.0
OUT=pathlib.Path(__file__).resolve().parents[1]/"qa_runs"/"v406_servo_tray"
OUT.mkdir(parents=True,exist_ok=True)
sx,sy,sz=SERVO_BODY
outer_x=max(sx+2*BODY_CLEARANCE+2*WALL,HOLE_SPACING+2*WALL+5)
outer_y=sy+2*BODY_CLEARANCE+2*WALL
base=Part.makeBox(outer_x,outer_y,FLOOR,Vector(-outer_x/2,-outer_y/2,0))
rim=Part.makeBox(outer_x,outer_y,sz*0.55,Vector(-outer_x/2,-outer_y/2,FLOOR))
void=Part.makeBox(sx+2*BODY_CLEARANCE,sy+2*BODY_CLEARANCE,sz*0.55+1,
                  Vector(-(sx+2*BODY_CLEARANCE)/2,-(sy+2*BODY_CLEARANCE)/2,FLOOR))
tray=base.fuse(rim.cut(void)).removeSplitter()
# Through holes are placed in the outer flanges; no unmeasured servo tabs.
for x in (-HOLE_SPACING/2,HOLE_SPACING/2):
    drill=Part.makeCylinder(SCREW_D/2,FLOOR+sz,Vector(x,0,0))
    tray=tray.cut(drill)
tray=tray.removeSplitter()
doc=App.newDocument("v406_servo_tray_coupon")
feature=doc.addObject("PartDesign::Feature","ServoTrayCoupon")
feature.Shape=tray
doc.recompute()
doc.saveAs(str(OUT/"v406_servo_tray_coupon.FCStd"))
Part.export([feature],str(OUT/"v406_servo_tray_coupon.stl"))
report={"version":"v406","status":"WIP_ONLY","shape_valid":tray.isValid(),
 "solid_count":len(tray.Solids),"volume_mm3":tray.Volume,
 "servo_body_assumed_mm":SERVO_BODY,"hole_spacing_assumed_mm":HOLE_SPACING,
 "limitations":["No measured servo or tab geometry","No fastening pull-out test",
 "No linkage motion/collision proof","No Final-Master integration",
 "No land/water/air operational evidence"]}
(OUT/"v406_servo_tray_qa.json").write_text(json.dumps(report,indent=2))
if not tray.isValid() or len(tray.Solids)!=1:
    raise RuntimeError("Servo tray geometry failed")
