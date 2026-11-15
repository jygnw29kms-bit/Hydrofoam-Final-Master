"""v396 replaceable twin-skid interface test assembly (FreeCAD Python).
Engineering coupon only: dimensions are assumptions, not extracted from master image.
Run with FreeCAD Python. Never modify FINAL_MASTER_ORIGINAL.jpeg.
"""
import FreeCAD as App
import Part, Mesh
from FreeCAD import Vector
import os, json, hashlib

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(ROOT,"qa_runs","v396_skid_interface")
os.makedirs(OUT,exist_ok=True)
DOC=App.newDocument("Hydrofoam_v396_TwinSkid_Interface")
# Parametric trial dimensions in mm. Verify against real float geometry before integration.
P={"skid_length":145.0,"skid_width":18.0,"wear_thickness":3.0,
   "receiver_thickness":5.0,"bolt_diameter":3.2,"bolt_pitch":96.0,
   "bolt_end_margin":24.5,"float_center_spacing":230.0,
   "foil_ground_clearance_required":12.0,"foil_retracted_lowest_z":None,
   "ground_contact_z":0.0,"material_density_g_cm3":{"PETG":1.27}}
L=P["skid_length"]; W=P["skid_width"]; t=P["wear_thickness"]
pitch=P["bolt_pitch"]; xholes=[(L-pitch)/2,(L+pitch)/2]
if min(xholes)<P["bolt_end_margin"] or max(xholes)>L-P["bolt_end_margin"]:
    raise ValueError("Hole positions violate end margin")
objects=[]; checks={}; mass_estimate_g=0
for side,y0 in (("Left",-P["float_center_spacing"]/2),("Right",P["float_center_spacing"]/2)):
    # Wear strip is flush at z=0; receiver is above it and can attach to a float.
    strip=Part.makeBox(L,W,t,Vector(0,y0-W/2,0))
    receiver=Part.makeBox(L,W,P["receiver_thickness"],Vector(0,y0-W/2,t))
    for x in xholes:
        bore=Part.makeCylinder(P["bolt_diameter"]/2,t+P["receiver_thickness"],
                             Vector(x,y0,0))
        strip=strip.cut(bore)
        receiver=receiver.cut(bore)
    for label,shape in (("WearStrip",strip),("Receiver",receiver)):
        shape=shape.removeSplitter()
        obj=DOC.addObject("PartDesign::Feature",side+"_"+label)
        obj.Shape=shape
        objects.append(obj)
        valid=shape.isValid() and len(shape.Solids)==1 and shape.Volume>0
        checks[obj.Name]={"valid":valid,"solids":len(shape.Solids),
                          "volume_mm3":shape.Volume,"bounding_box_mm":[
                          shape.BoundBox.XLength,shape.BoundBox.YLength,shape.BoundBox.ZLength]}
        if label=="WearStrip":
            mass_estimate_g+=shape.Volume/1000*P["material_density_g_cm3"]["PETG"]
        if not valid: raise RuntimeError("Invalid solid: "+obj.Name)
        Mesh.export([obj],os.path.join(OUT,obj.Name+".stl"))
    intersection=strip.common(receiver).Volume
    if intersection>1e-6: raise RuntimeError("Wear strip / receiver collision")
    checks[side+"_interface"]={"collision_mm3":intersection,
                                "contact_area_nominal_mm2":L*W-2*3.14159265359*(P["bolt_diameter"]/2)**2}
DOC.recompute()
cad=os.path.join(OUT,"v396_twin_skid_interface.FCStd")
DOC.saveAs(cad)
files={}
for filename in sorted(os.listdir(OUT)):
    if filename.endswith((".stl",".FCStd")):
        path=os.path.join(OUT,filename)
        with open(path,"rb") as f: digest=hashlib.sha256(f.read()).hexdigest()
        files[filename]={"bytes":os.path.getsize(path),"sha256":digest}
report={"status":"WIP_GEOMETRY_ONLY","units":"mm","parameters":P,"checks":checks,
        "estimated_two_PETG_wear_strips_g":mass_estimate_g,"artifacts":files,
        "blocked_gates":["Actual float mating surfaces not measured",
        "No fastener head recess, inserts or torque test",
        "No ground steering or sand/grass traction measurements",
        "Foil retracted lowest z unknown: clearance NOT certified",
        "No abrasion or hydrodynamic testing",
        "No master-image silhouette comparison",
        "Not flight/water/land approved"]}
with open(os.path.join(OUT,"v396_qa.json"),"w",encoding="utf8") as f:
    json.dump(report,f,indent=2)
print(json.dumps(report))
