"""v397: FreeCAD retractable foil pivot coupon. NOT integrated or approved.
Coordinate system: X fore-aft, Y span, Z upward; ground is Z=0.
Run in FreeCAD Python; exports actual solids and angle sweep QA.
"""
import FreeCAD as App
import Part, Mesh
from FreeCAD import Vector
import os, json, math, hashlib
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"qa_runs","v397_foil_pivot")
os.makedirs(OUT,exist_ok=True)
P={"pivot_z_mm":35.0,"mast_length_mm":24.0,"mast_width_mm":8.0,
   "mast_thickness_mm":5.0,"foil_span_mm":75.0,"foil_chord_mm":12.0,
   "foil_thickness_mm":3.0,"pin_diameter_mm":3.0,
   "pin_clearance_radial_mm":0.25,"required_ground_clearance_mm":12.0,
   "angle_deployed_deg":0,"angle_stowed_deg":90,"step_deg":5}
doc=App.newDocument("Hydrofoam_v397_FoilPivot_Coupon")
# Hinge is transverse Y axis; mast starts at pivot and extends downward.
pin=Part.makeCylinder(P["pin_diameter_mm"]/2,20,Vector(0,-10,P["pivot_z_mm"]),Vector(0,1,0))
# Separate stationary hinge cheek blocks, separated by mast and free to rotate.
cheeks=[]
for y in (-8,5):
    cheek=Part.makeBox(14,3,14,Vector(-7,y,P["pivot_z_mm"]-7))
    hole=Part.makeCylinder(P["pin_diameter_mm"]/2+P["pin_clearance_radial_mm"],3,Vector(0,y,P["pivot_z_mm"]),Vector(0,1,0))
    cheeks.append(cheek.cut(hole).removeSplitter())
mast=Part.makeBox(P["mast_width_mm"],P["mast_thickness_mm"],P["mast_length_mm"],
                  Vector(-P["mast_width_mm"]/2,-P["mast_thickness_mm"]/2,
                         P["pivot_z_mm"]-P["mast_length_mm"]))
hole=Part.makeCylinder(P["pin_diameter_mm"]/2+P["pin_clearance_radial_mm"],
                       P["mast_thickness_mm"],Vector(0,-P["mast_thickness_mm"]/2,P["pivot_z_mm"]),Vector(0,1,0))
mast=mast.cut(hole)
foil=Part.makeBox(P["foil_chord_mm"],P["foil_span_mm"],P["foil_thickness_mm"],
                  Vector(-P["foil_chord_mm"]/2,-P["foil_span_mm"]/2,
                         P["pivot_z_mm"]-P["mast_length_mm"]-P["foil_thickness_mm"]))
moving=mast.fuse(foil).removeSplitter()
fixed=cheeks[0].fuse(cheeks[1]).removeSplitter()
objects=[]
for name,shape in (("StationaryCheeks",fixed),("PivotPin",pin),("FoilAndMast",moving)):
    if not shape.isValid() or shape.Volume<=0: raise RuntimeError(name+" invalid")
    obj=doc.addObject("PartDesign::Feature",name); obj.Shape=shape; objects.append(obj)
    Mesh.export([obj],os.path.join(OUT,name+".stl"))
doc.recompute();doc.saveAs(os.path.join(OUT,"v397_foil_pivot.FCStd"))
sweep=[]
for angle in range(P["angle_deployed_deg"],P["angle_stowed_deg"]+1,P["step_deg"]):
    moved=moving.copy()
    moved.rotate(Vector(0,0,P["pivot_z_mm"]),Vector(0,1,0),angle)
    collision=moved.common(fixed).Volume
    # The pin is intentionally inside the clearance bore; test against cheeks/mast separately.
    sweep.append({"angle_deg":angle,"lowest_z_mm":round(moved.BoundBox.ZMin,4),
                  "ground_clearance_pass":moved.BoundBox.ZMin>=P["required_ground_clearance_mm"],
                  "cheek_intersection_mm3":round(collision,6)})
files={}
for fn in sorted(os.listdir(OUT)):
    if fn.endswith((".stl",".FCStd")):
        path=os.path.join(OUT,fn)
        with open(path,"rb") as f: files[fn]={"bytes":os.path.getsize(path),"sha256":hashlib.sha256(f.read()).hexdigest()}
report={"status":"WIP_COUPON_ONLY","parameters":P,"sweep":sweep,
 "sweep_collision_free":all(s["cheek_intersection_mm3"]<0.001 for s in sweep),
 "stowed_clearance_pass":sweep[-1]["ground_clearance_pass"],
 "artifacts":files,
 "limitations":["Rectangular foil is a mechanical placeholder, NOT a hydrodynamic section",
 "No locking mechanism or servo actuation yet","No mounting to master float",
 "No hydrodynamic loads, material stress, fatigue or water sealing verified",
 "Pin retention, printer tolerances and physical motion untested",
 "Deployed foil is expected to violate ground clearance: must stow for land",
 "Not proof of Land/Water/Air operation or Final-Master fidelity"]}
with open(os.path.join(OUT,"v397_qa.json"),"w",encoding="utf8") as f:json.dump(report,f,indent=2)
print(json.dumps({"status":report["status"],"sweep_collision_free":report["sweep_collision_free"],"stowed_clearance_pass":report["stowed_clearance_pass"]}))
