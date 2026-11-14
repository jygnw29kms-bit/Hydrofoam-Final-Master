# Hydrofoam v384: parametric printable hinge coupon, independent WIP test geometry.
# Run in FreeCAD Python. This is NOT an integrated aircraft control surface.
import os, json, math
import FreeCAD as App
import Part, Mesh
from FreeCAD import Vector as V

OUT = os.environ.get("HYDROFOAM_V384_OUT", os.path.join(os.getcwd(),"build","v384"))
os.makedirs(OUT, exist_ok=True)
doc=App.newDocument("Hydrofoam_v384_HingeCoupon")
L=42.0; AXIS_Z=4.6; BARREL_R=3.8; PIN_R=1.2
BORE_R=1.48; AXIAL_GAP=0.65; LEAF_T=2.8
# Interleaved knuckles: fixed 0..12 and 29..41; moving 12.65..28.35
# Leaves are positioned below the hinge axis to avoid occupying the barrel bore.
def tube(x, length):
    a=Part.makeCylinder(BARREL_R,length,V(x,0,AXIS_Z),V(1,0,0))
    b=Part.makeCylinder(BORE_R,length,V(x,0,AXIS_Z),V(1,0,0))
    return a.cut(b)
def add(name, shape):
    obj=doc.addObject("PartDesign::Feature",name)
    obj.Shape=shape.removeSplitter()
    return obj
# Webs connect to the knuckles only on their own side of the hinge.
fixed=Part.makeBox(L,13.0,LEAF_T,V(0,-17.0,0))
moving=Part.makeBox(L,13.0,LEAF_T,V(0,4.0,0))
for x, span in [(0,12),(29,12)]:
    fixed=fixed.fuse(tube(x,span))
    fixed=fixed.fuse(Part.makeBox(span,1.4,2.4,V(x,-4.6,1.7)))
mx=12+AXIAL_GAP; ml=17-2*AXIAL_GAP
moving=moving.fuse(tube(mx,ml))
moving=moving.fuse(Part.makeBox(ml,1.4,2.4,V(mx,3.2,1.7)))
pin=Part.makeCylinder(PIN_R,L+4,V(-2,0,AXIS_Z),V(1,0,0))
fixed_obj=add("FixedLeaf",fixed)
moving_obj=add("MovingLeaf",moving)
pin_obj=add("RemovablePin",pin)
# Control horn coupon attached to moving leaf, hole along Z.
horn=Part.makeBox(12,6,3,V(16,12,LEAF_T))
horn=horn.cut(Part.makeCylinder(1.25,3,V(22,15,LEAF_T),V(0,0,1)))
horn_obj=add("HornBlank",horn)
doc.recompute()
results=[]
axis=V(1,0,0); pivot=V(0,0,AXIS_Z)
for angle in range(-35,36,5):
    rot=moving_obj.Shape.copy()
    rot.rotate(pivot,axis,angle)
    # A genuine Boolean sweep, no automatic pass for missing shapes.
    results.append(dict(deg=angle, fixed_overlap_mm3=round(rot.common(fixed_obj.Shape).Volume,6),
                        pin_overlap_mm3=round(rot.common(pin_obj.Shape).Volume,6),
                        shape_valid=bool(rot.isValid())))
components=[]
for obj in (fixed_obj,moving_obj,pin_obj,horn_obj):
    shape=obj.Shape
    components.append(dict(name=obj.Name,valid=bool(shape.isValid()),solids=len(shape.Solids),
                           volume_mm3=round(shape.Volume,3)))
    Mesh.Mesh(shape.tessellate(0.12)).write(os.path.join(OUT,obj.Name+".stl"))
doc.saveAs(os.path.join(OUT,"Hydrofoam_v384_HingeCoupon.FCStd"))
report=dict(version="v384",kind="independent_hinge_coupon",release="NOT_APPROVED",
            dimensions_mm=dict(pin_diameter=2*PIN_R,bore_diameter=2*BORE_R,
                               axial_gap=AXIAL_GAP,leaf_length=L),
            components=components,sweep=results,
            collision_free=all(r["shape_valid"] and r["fixed_overlap_mm3"]<1e-6 and
                               r["pin_overlap_mm3"]<1e-6 for r in results),
            limits=dict(master_fidelity="NOT_TESTED",aircraft_integration="NOT_TESTED",
                        servo_fit="NOT_TESTED",linkage_kinematics="NOT_TESTED",
                        physical_print_fit="NOT_TESTED",land_water_air="NOT_TESTED"))
with open(os.path.join(OUT,"qa.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
