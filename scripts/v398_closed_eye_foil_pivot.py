"""v398: revised printable foil-pivot engineering coupon (not a flight/water-approved part).
FreeCAD Python script. All dimensions are provisional and MUST be reconciled to the master floats.
Coordinate X fore/aft, Y span, Z up. Pivot axis Y.
"""
import FreeCAD as App
import Part, Mesh
from FreeCAD import Vector
import os, json, hashlib
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"qa_runs","v398_foil_pivot")
os.makedirs(OUT,exist_ok=True)
P=dict(pivot_z=40.0, pin_d=3.0, radial_gap=0.25, axial_gap=0.5,
       cheek_thick=3.0, boss_width=6.0, boss_radius=6.0,
       mast_len=24.0, mast_width=7.0, mast_depth=5.0,
       foil_span=60.0, foil_chord=12.0, foil_thick=3.0,
       min_stowed_clearance=12.0, angular_step=2)
doc=App.newDocument("Hydrofoam_v398_FoilPivot_Coupon")
pivot=Vector(0,0,P["pivot_z"]); axis=Vector(0,1,0)
hole_r=P["pin_d"]/2+P["radial_gap"]
# A real closed hinge eye: circular boss rather than v397's open-ended mast bore.
boss=Part.makeCylinder(P["boss_radius"],P["boss_width"],Vector(0,-3,P["pivot_z"]),axis)
mast=Part.makeBox(P["mast_width"],P["mast_depth"],P["mast_len"],
                  Vector(-P["mast_width"]/2,-P["mast_depth"]/2,P["pivot_z"]-P["mast_len"]))
foil=Part.makeBox(P["foil_chord"],P["foil_span"],P["foil_thick"],
                  Vector(-P["foil_chord"]/2,-P["foil_span"]/2,
                         P["pivot_z"]-P["mast_len"]-P["foil_thick"]))
moving=boss.fuse(mast).fuse(foil).removeSplitter()
bore=Part.makeCylinder(hole_r,P["boss_width"],Vector(0,-3,P["pivot_z"]),axis)
moving=moving.cut(bore).removeSplitter()
# Cheeks are separate printable solids. Their inside faces sit +/-3.5 mm from mid-plane.
cheeks=[]
for y in (-6.5,3.5):
    block=Part.makeBox(15,P["cheek_thick"],16,Vector(-7.5,y,P["pivot_z"]-8))
    hole=Part.makeCylinder(hole_r,P["cheek_thick"],Vector(0,y,P["pivot_z"]),axis)
    cheeks.append(block.cut(hole).removeSplitter())
pin=Part.makeCylinder(P["pin_d"]/2,16,Vector(0,-8,P["pivot_z"]),axis)
fixed=Part.makeCompound(cheeks)
shapes=dict(CheekLeft=cheeks[0],CheekRight=cheeks[1],FoilMast=moving,PivotPin=pin)
for name,shape in shapes.items():
    if not shape.isValid() or shape.Volume<=0:
        raise RuntimeError("Invalid solid: "+name)
    obj=doc.addObject("PartDesign::Feature",name);obj.Shape=shape
    Mesh.export([obj],os.path.join(OUT,name+".stl"))
doc.recompute()
doc.saveAs(os.path.join(OUT,"v398_foil_pivot.FCStd"))
sweep=[]
for deg in range(0,91,P["angular_step"]):
    part=moving.copy();part.rotate(pivot,axis,deg)
    overlap=sum(part.common(c).Volume for c in cheeks)
    sweep.append(dict(angle_deg=deg,lowest_z_mm=round(part.BoundBox.ZMin,4),
                      cheek_collision_mm3=round(overlap,6)))
# Collision-free is NOT assumed: fail loudly in the report if it isn't true.
# Pin is deliberately omitted from collision check: it occupies the designed bearing clearance.
artifacts={}
for fn in sorted(os.listdir(OUT)):
    if fn.endswith((".stl",".FCStd")):
        data=open(os.path.join(OUT,fn),"rb").read()
        artifacts[fn]=dict(bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
report=dict(status="WIP_MECHANICAL_COUPON_NOT_INTEGRATED",parameters=P,
            closed_boss_valid=moving.isValid(),
            cheek_sweep_clear=all(x["cheek_collision_mm3"]<0.001 for x in sweep),
            stowed_clearance_pass=sweep[-1]["lowest_z_mm"]>=P["min_stowed_clearance"],
            axial_clearance_each_side_mm=P["axial_gap"],
            sweep=sweep,artifacts=artifacts,
            limitations=["Not mounted to master float","No retaining clip or locking mechanism",
                         "No servo, linkage or water seal","No measured material/print tolerances",
                         "Rectangular foil is not a hydrodynamic section",
                         "Not a proof of Land/Water/Air capability or image fidelity"])
with open(os.path.join(OUT,"v398_qa.json"),"w",encoding="utf8") as f:
    json.dump(report,f,indent=2)
print(json.dumps({k:report[k] for k in ("status","cheek_sweep_clear","stowed_clearance_pass")}))
