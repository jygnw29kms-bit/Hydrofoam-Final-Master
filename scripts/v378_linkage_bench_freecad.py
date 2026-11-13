# Hydrofoam v378: parametric hinge + servo linkage bench assembly (WIP)
# Run with FreeCAD Python environment. Separate test fixture, NOT fitted to master hull.
import FreeCAD as App, Part, math, os, json
from FreeCAD import Vector
OUT=os.environ.get("HYDROFOAM_V378_OUT",os.path.join(os.getcwd(),"build","v378"))
os.makedirs(OUT,exist_ok=True)
doc=App.newDocument("Hydrofoam_v378_Linkage_Test")
# Millimetres. Generic fit-test geometry; no master silhouette assumptions.
PIN_D=2.4
RADIAL_CLEARANCE=0.25
BARREL_R=3.8
LEAF_L=38.0
LEAF_W=14.0
LEAF_T=3.2
GAP=0.5
def add(name,shape):
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Shape=shape
    return obj
def cylinder(r,h,x,y,z):
    return Part.makeCylinder(r,h,Vector(x,y,z),Vector(1,0,0))
# Hinge axis along X, at Y=0, Z=BARREL_R
z=BARREL_R
# Fixed leaf extends negative Y, moving leaf positive Y
fixed=Part.makeBox(LEAF_L,LEAF_W,LEAF_T,Vector(0,-LEAF_W,0))
moving=Part.makeBox(LEAF_L,LEAF_W,LEAF_T,Vector(0,0,0))
# Alternating knuckles, with pin bore cut from each barrel
bore=PIN_D/2+RADIAL_CLEARANCE
for x,w in [(0,12),(26,12)]:
    barrel=cylinder(BARREL_R,w,x,0,z).cut(cylinder(bore,w,x,0,z))
    fixed=fixed.fuse(barrel)
barrel=cylinder(BARREL_R,12,13,0,z).cut(cylinder(bore,12,13,0,z))
moving=moving.fuse(barrel)
# clearance between leaf and opposing knuckles is to be measured in sweep tests
fixed=fixed.removeSplitter()
moving=moving.removeSplitter()
pin=cylinder(PIN_D/2,LEAF_L+4,-2,0,z)
add("FixedLeaf",fixed)
add("MovingLeaf",moving)
add("RemovablePin",pin)
# Servo seat is a separate adjustable rectangular test cradle, NOT a specific servo standard.
SERVO_L=24.0; SERVO_W=13.0; SERVO_H=23.0; WALL=3.0; FIT=0.4
outer=Part.makeBox(SERVO_L+2*WALL+FIT,SERVO_W+2*WALL+FIT,12,Vector(5,-49,0))
pocket=Part.makeBox(SERVO_L+FIT,SERVO_W+FIT,12,Vector(5+WALL,-49+WALL,3))
seat=outer.cut(pocket)
add("ServoCradle_FitTest",seat)
# Horn test blank: drill hole geometry sized to test pin, no servo-spline claimed.
horn=Part.makeBox(17,6,3,Vector(12,18,0))
horn=horn.cut(Part.makeCylinder(1.25,3,Vector(15,21,0)))
horn=horn.cut(Part.makeCylinder(1.25,3,Vector(26,21,0)))
add("ControlHorn_Blank",horn)
doc.recompute()
report={"version":"v378","status":"WIP_UNVERIFIED","units":"mm","hinge_pin_diameter":PIN_D,
"radial_clearance":RADIAL_CLEARANCE,"components":[],"tests":{"swept_collision":"NOT_RUN","servo_fit":"NOT_RUN","load_test":"NOT_RUN","print_fit":"NOT_RUN","master_integration":"NOT_RUN"}}
for obj in doc.Objects:
    if not hasattr(obj,"Shape") or obj.Shape.isNull():continue
    sh=obj.Shape
    report["components"].append({"name":obj.Name,"valid":sh.isValid(),"solids":len(sh.Solids),"volume_mm3":round(sh.Volume,3),"bbox_mm":[round(sh.BoundBox.XLength,3),round(sh.BoundBox.YLength,3),round(sh.BoundBox.ZLength,3)]})
    if obj.Name!="RemovablePin":
        import Mesh
        mesh=Mesh.Mesh(sh.tessellate(0.15))
        mesh.write(os.path.join(OUT,obj.Name+".stl"))
doc.saveAs(os.path.join(OUT,"Hydrofoam_v378_Linkage_Test.FCStd"))
with open(os.path.join(OUT,"qa.json"),"w") as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
