"""v411: configurable FreeCAD control-surface mechanism assembly.
A mechanical prototype only. It never asserts Master-image correspondence or flight approval.
Run inside FreeCAD Python with a reviewed JSON configuration (mm).
"""
import FreeCAD as App
import Part, Mesh
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = Path(sys.argv[-1]) if len(sys.argv)>1 and sys.argv[-1].endswith(".json") else ROOT/"cad"/"v411_mechanism_config.json"
if not CONFIG.exists():
    raise RuntimeError("A reviewed control-surface configuration is required: "+str(CONFIG))
cfg=json.loads(CONFIG.read_text(encoding="utf-8"))
required={"left_aileron","right_aileron","elevator_left","elevator_right","rudder"}
if set(cfg.get("surfaces",{}))!=required:
    raise ValueError("Exactly the five required control surfaces must be configured")
out=ROOT/"cad"/"v411_control_mechanisms"
out.mkdir(parents=True,exist_ok=True)
V=App.Vector
doc=App.newDocument("Hydrofoam_v411_MechanismPrototype")
qa={"version":"v411","classification":"WIP_PROTOTYPE","surfaces":{},"verified_in_airframe":False,
    "image_master_verified":False,"physical_print_verified":False}
def vec(x): return V(*[float(v) for v in x])
def add(name,shape):
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Shape=shape
    if not shape.isValid() or len(shape.Solids)!=1 or shape.Volume<=0:
        raise ValueError("Invalid solid: "+name)
    return obj
def segment(a,b,r):
    d=b-a
    if d.Length<0.01: raise ValueError("Zero-length linkage")
    return Part.makeCylinder(r,d.Length,a,d)
def orient(shape,base,axis,angle):
    s=shape.copy()
    s.rotate(base,axis,angle)
    return s
for name,p in cfg["surfaces"].items():
    # Explicit local frame: hinge along +X; control surface extends toward -Y.
    # Placement is supplied by surveyed geometry, not inferred from a reference photo.
    origin=vec(p["hinge_origin_mm"])
    width=float(p["span_mm"]); chord=float(p["chord_mm"])
    thick=float(p["thickness_mm"]); pin_d=float(p["pin_diameter_mm"])
    clearance=float(p["radial_clearance_mm"])
    arm=float(p["horn_arm_mm"]); servo_arm=float(p["servo_arm_mm"])
    travel=float(p["travel_deg"]); steps=int(p.get("sweep_steps",31))
    if not (width>25 and chord>12 and thick>1 and 1<=pin_d<=6 and
            .15<=clearance<=.8 and arm>5 and servo_arm>4 and 0<travel<=40 and steps>=11):
        raise ValueError("Unreviewed/invalid dimensions: "+name)
    # Fixed mount and movable rudder leaf are separate printable solids.
    fixed=Part.makeBox(width,chord*.18,thick,V(0,0,-thick/2))
    moving=Part.makeBox(width,chord*.75,thick,V(0,-chord*.75,-thick/2))
    outer=pin_d/2+clearance+1.7
    for i in range(5):
        x=width*i/5
        sleeve=Part.makeCylinder(outer,width/5-.5,V(x,0,0),V(1,0,0))
        bore=Part.makeCylinder(pin_d/2+clearance,width/5+.5,V(x-.25,0,0),V(1,0,0))
        if i%2==0: fixed=fixed.fuse(sleeve.cut(bore))
        else: moving=moving.fuse(sleeve.cut(bore))
    # Horn projects below the movable leaf. Hole runs along X.
    horn=Part.makeBox(3.2,6,arm,V(width*.5-1.6,-chord*.35,-arm))
    horn=horn.cut(Part.makeCylinder(1.1,5,V(width*.5-2.5,-chord*.35+3,-arm+3),V(1,0,0)))
    moving=moving.fuse(horn).removeSplitter()
    fixed=fixed.removeSplitter()
    pin=Part.makeCylinder(pin_d/2,width+2,V(-1,0,0),V(1,0,0))
    # Servo tray and servo output pivot are intentionally separate objects.
    servo_pivot=vec(p["servo_pivot_local_mm"])
    tray=Part.makeBox(28,14,3,V(servo_pivot.x-14,servo_pivot.y-7,servo_pivot.z-8))
    arm_end=servo_pivot+V(0,servo_arm,0)
    horn_tip=V(width*.5,-chord*.35+3,-arm+3)
    nominal=(arm_end-horn_tip).Length
    if nominal<5: raise ValueError("Linkage too short")
    parts={"fixed":fixed,"moving":moving,"pin":pin,"servo_tray":tray}
    for part,shape in parts.items():
        shape.translate(origin)
        add(name+"_"+part,shape)
    # Numerical swept volumes: pin and leaf fixed interference and linkage length.
    samples=[]
    for j in range(steps):
        deg=-travel+2*travel*j/(steps-1)
        leaf=orient(moving,V(0,0,0),V(1,0,0),deg)
        tip=V(horn_tip)
        tip.rotate(V(0,0,0),V(1,0,0),deg)
        # This tests a fixed servo arm at neutral; a real servo-angle solver is still required.
        interference=leaf.common(fixed).Volume
        pin_interference=leaf.common(pin).Volume
        rod_length=(arm_end-tip).Length
        samples.append({"rudder_deg":round(deg,4),"fixed_overlap_mm3":interference,
                        "pin_overlap_mm3":pin_interference,
                        "neutral_servo_rod_length_mm":rod_length})
    report={"parts":list(parts),"sweep":samples,"nominal_rod_length_mm":nominal,
            "max_fixed_overlap_mm3":max(x["fixed_overlap_mm3"] for x in samples),
            "max_pin_overlap_mm3":max(x["pin_overlap_mm3"] for x in samples),
            "rod_length_variation_mm":max(abs(x["neutral_servo_rod_length_mm"]-nominal) for x in samples),
            "status":"NOT_ACCEPTED_REQUIRES_SERVO_SOLVER_AND_AIRFRAME_CLEARANCE"}
    qa["surfaces"][name]=report
    for part in parts:
        obj=doc.getObject(name+"_"+part)
        Mesh.export([obj],str(out/(name+"_"+part+".stl")))
doc.recompute()
doc.saveAs(str(out/"control_mechanism_prototype.FCStd"))
(out/"qa.json").write_text(json.dumps(qa,indent=2),encoding="utf-8")
print("v411 prototype generated; NOT mechanically accepted")
