"""v389: actual paired hinge, removable pin, servo bracket and 3D sweep coupon.
Standalone engineering coupon ONLY. Not a master-airframe integration or flight clearance.
Run with FreeCAD Python (FreeCADCmd); dimensions in mm. Never modifies reference image.
"""
import os, json, math
import FreeCAD as App
import Part, MeshPart
V=App.Vector
out=os.environ.get("HYDROFOAM_V389_OUT",os.path.join(os.getcwd(),"build","v389"))
os.makedirs(out,exist_ok=True)
doc=App.newDocument("Hydrofoam_v389_paired_hinge")
axis=V(0,1,0)
# Fixed leaf on negative X, moving leaf on positive X; hinge axis through origin.
width=30.0; pin_r=1.2; bore_r=1.45; barrel_r=3.8
fixed=Part.makeBox(30,width,3,V(-30,0,-1.5))
moving=Part.makeBox(30,width,3,V(0,0,-1.5))
def barrel(y0,y1):
    return Part.makeCylinder(barrel_r,y1-y0,V(0,y0,0),axis).cut(
        Part.makeCylinder(bore_r,y1-y0+0.2,V(0,y0-0.1,0),axis))
# Alternating barrels; 0.6 mm nominal axial gaps at each moving interface.
for a,b in [(0,9.4),(20.6,30)]:
    fixed=fixed.fuse(barrel(a,b))
moving=moving.fuse(barrel(10,20))
fixed=fixed.cut(Part.makeCylinder(bore_r,32,V(0,-1,0),axis)).removeSplitter()
moving=moving.cut(Part.makeCylinder(bore_r,32,V(0,-1,0),axis)).removeSplitter()
pin=Part.makeCylinder(pin_r,32,V(0,-1,0),axis)
# Horn integral to moving leaf; rod bore across Y.
horn=Part.makeBox(3,7,15,V(18,11.5,1.5))
horn=horn.cut(Part.makeCylinder(1.1,9,V(19.5,10.5,12),axis))
moving=moving.fuse(horn).removeSplitter()
# Standalone servo cradle, deliberately outside sweep envelope.
servo_len,servo_w,servo_h=23.0,12.5,24.0
cradle=Part.makeBox(31,20.5,15,V(-70,40,0)).cut(
    Part.makeBox(24,13.5,13,V(-66.5,43.5,3)))
# Fastening ears and through holes.
for x in [-65,-44]:
    cradle=cradle.fuse(Part.makeBox(9,8,3,V(x-4.5,32,0)))
    cradle=cradle.cut(Part.makeCylinder(1.7,5,V(x,36,-1)))
cradle=cradle.removeSplitter()
shapes={"fixed_leaf":fixed,"moving_leaf_horn":moving,"removable_pin":pin,"servo_cradle":cradle}
for name,shape in shapes.items():
    obj=doc.addObject("PartDesign::Feature",name);obj.Shape=shape
doc.recompute()
doc.saveAs(os.path.join(out,"v389_paired_hinge_coupon.FCStd"))
for name in ["fixed_leaf","moving_leaf_horn","servo_cradle"]:
    mesh=MeshPart.meshFromShape(Shape=shapes[name],LinearDeflection=0.1,AngularDeflection=0.2,Relative=False)
    mesh.write(os.path.join(out,"v389_"+name+".stl"))
sweep=[]
for angle in range(-35,36,5):
    leaf=moving.copy()
    leaf.rotate(V(0,0,0),axis,angle)
    overlap=leaf.common(fixed).Volume
    pin_overlap=leaf.common(pin).Volume
    sweep.append({"angle_deg":angle,"fixed_leaf_overlap_mm3":round(overlap,5),
                  "pin_overlap_mm3":round(pin_overlap,5)})
# Pin overlap is not expected to be zero if bore/pin are incorrectly modeled.
qa={"version":"v389","status":"STANDALONE_COUPON_NOT_MASTER_INTEGRATED",
    "parts":{n:{"valid":s.isValid(),"solid_count":len(s.Solids),"volume_mm3":s.Volume}
             for n,s in shapes.items()},
    "sweep":sweep,
    "pass_geometric_sweep":all(s["fixed_leaf_overlap_mm3"]<0.01 and s["pin_overlap_mm3"]<0.01 for s in sweep),
    "limits":["no servo/rod actuation installed","no dynamic rod clearance proof",
              "no master geometry alignment","no P2S printed fit validation",
              "no structural loading or land-water-air verification"]}
with open(os.path.join(out,"v389_hinge_qa.json"),"w",encoding="utf-8") as f:
    json.dump(qa,f,indent=2)
print(json.dumps(qa,indent=2))
if not qa["pass_geometric_sweep"] or not all(s.isValid() for s in shapes.values()):
    raise SystemExit("GEOMETRIC_QA_FAILED")
