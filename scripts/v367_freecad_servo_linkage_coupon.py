"""Hydrofoam v367: parametric servo-to-rudder linkage assembly coupon.
Standalone FreeCAD construction prototype, NOT installed in v333 and NOT approved.
Units: mm. Creates real BREP components, exports individual STLs and a sweep report.
"""
import os, json, math
from pathlib import Path
import FreeCAD as App
import Part, Mesh

# Coupon dimensions are provisional, not measurements from the master model.
SERVO_BODY=(23.0,12.0,24.0)
SERVO_CLEARANCE=0.5
TRAY_WALL=2.5
TRAY_FLOOR=2.4
HORN_RADIUS=12.0
HORN_THICK=3.0
LINK_PIN_D=2.0
ROD_D=2.5
PIVOT_DISTANCE=55.0
RUDDER_ARM=14.0
ANGLES=range(-30,31,5)
V=App.Vector

def cylinder(r,h,p,d=V(0,0,1)):
    return Part.makeCylinder(r,h,p,d)

# Servo tray with a positive retention lip and two through-fastener holes.
sx,sy,sz=SERVO_BODY
outer=Part.makeBox(sx+2*(TRAY_WALL+SERVO_CLEARANCE),
                   sy+2*(TRAY_WALL+SERVO_CLEARANCE),sz/2+TRAY_FLOOR,V(0,0,0))
cavity=Part.makeBox(sx+2*SERVO_CLEARANCE,sy+2*SERVO_CLEARANCE,sz/2+1,
                    V(TRAY_WALL,TRAY_WALL,TRAY_FLOOR))
tray=outer.cut(cavity)
for x in (TRAY_WALL/2, outer.BoundBox.XLength-TRAY_WALL/2):
    tray=tray.cut(cylinder(1.25,TRAY_FLOOR+2,V(x,outer.BoundBox.YLength/2,-1)))
tray=tray.removeSplitter()

# Independent horn and control horn; pins are separate replaceable components.
servo_horn=cylinder(4.5,HORN_THICK,V(0,0,0)).fuse(
    Part.makeBox(HORN_RADIUS,5,HORN_THICK,V(0,-2.5,0)))
servo_horn=servo_horn.cut(cylinder(1.2,HORN_THICK+2,V(0,0,-1)))
servo_horn=servo_horn.cut(cylinder(LINK_PIN_D/2+0.2,HORN_THICK+2,V(HORN_RADIUS,0,-1))).removeSplitter()
rudder_horn=Part.makeBox(RUDDER_ARM+5,5,HORN_THICK,V(-2.5,-2.5,0))
rudder_horn=rudder_horn.fuse(cylinder(3.5,HORN_THICK,V(0,0,0)))
rudder_horn=rudder_horn.cut(cylinder(1.2,HORN_THICK+2,V(0,0,-1)))
rudder_horn=rudder_horn.cut(cylinder(LINK_PIN_D/2+0.2,HORN_THICK+2,V(RUDDER_ARM,0,-1))).removeSplitter()

# A single fixed-length rod cannot be asserted to fit arbitrary horn angles.
# Solve a planar four-bar configuration using two circle intersections.
def intersection(a,ra,b,rb):
    dx,dy=b[0]-a[0],b[1]-a[1]
    d=math.hypot(dx,dy)
    if d>ra+rb or d<abs(ra-rb) or d<1e-9: return None
    u=(ra*ra-rb*rb+d*d)/(2*d)
    h=math.sqrt(max(0,ra*ra-u*u))
    px,py=a[0]+u*dx/d,a[1]+u*dy/d
    return [(px-h*dy/d,py+h*dx/d),(px+h*dy/d,py-h*dx/d)]

# Rudder pivot at x=PIVOT_DISTANCE. Link rod length defined at neutral.
neutral_a=(HORN_RADIUS,0)
neutral_b=(PIVOT_DISTANCE-RUDDER_ARM,0)
rod_length=math.dist(neutral_a,neutral_b)
sweep=[]
previous=(PIVOT_DISTANCE-RUDDER_ARM,0)
for angle in ANGLES:
    rad=math.radians(angle)
    a=(HORN_RADIUS*math.cos(rad),HORN_RADIUS*math.sin(rad))
    choices=intersection(a,rod_length,(PIVOT_DISTANCE,0),RUDDER_ARM)
    if choices is None:
        sweep.append(dict(servo_deg=angle,valid=False,reason="no planar linkage solution"))
        continue
    b=min(choices,key=lambda p: math.dist(p,previous))
    previous=b
    rudder_deg=math.degrees(math.atan2(b[1],b[0]-PIVOT_DISTANCE))
    sweep.append(dict(servo_deg=angle,rudder_deg=round(rudder_deg,3),
                      valid=True,rod_length_mm=round(math.dist(a,b),5)))
# Rod is printed as a sizing coupon only; actual articulated end joints remain unresolved.
rod=cylinder(ROD_D/2,rod_length,V(0,0,0),V(1,0,0))
parts={"Servo_tray_WIP":tray,"Servo_horn_WIP":servo_horn,
       "Rudder_horn_WIP":rudder_horn,"Rod_blank_WIP":rod}
geometry_ok=all(s.isValid() and len(s.Solids)==1 for s in parts.values())
out=Path(os.environ.get("HYDROFOAM_V367_OUTPUT",str(Path.home()/"JL1976"/"Hydrofoam_v367_WIP")))
if out.exists() and any(out.iterdir()):
    raise RuntimeError("Refusing to overwrite nonempty output: "+str(out))
out.mkdir(parents=True,exist_ok=True)
doc=App.newDocument("Hydrofoam_v367_Linkage_Coupon_WIP")
for name,shape in parts.items():
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Shape=shape
    Mesh.export([obj],str(out/(name+".stl")))
doc.recompute()
doc.saveAs(str(out/"Hydrofoam_v367_Linkage_Coupon_WIP.FCStd"))
report={"status":"PROTOTYPE_ONLY","geometry_valid":geometry_ok,
        "kinematic_solutions_all":all(p["valid"] for p in sweep),
        "rod_length_mm":rod_length,"sweep":sweep,
        "not_verified":["Installed geometry in v333","Real servo dimensions and torque",
        "Rod end joints and clearance","Collision against airframe",
        "Printing tolerance, loads and fatigue","Flight, land and water operation",
        "Master photo fidelity"]}
(out/"v367_linkage_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
print(json.dumps({"output":str(out),"status":report["status"]}))
if not geometry_ok or not report["kinematic_solutions_all"]:
    raise RuntimeError("Coupon validation failed; inspect report")
