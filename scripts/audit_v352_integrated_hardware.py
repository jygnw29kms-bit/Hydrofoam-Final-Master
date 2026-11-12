"""v352: auditable hardware inventory gate for full control assembly.

Run with Blender: blender -b path/to/assembly.blend --python scripts/audit_v352_integrated_hardware.py -- docs/V352_HARDWARE_WIP.json

Requires every elevon and rudder (left/right) to contain real, separate
meshes named by user-defined semantic custom property hydrofoam_role.
A passed inventory is NOT a functional or flight acceptance.
"""
import bpy,json,sys,hashlib
from pathlib import Path
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=1:raise SystemExit("provide report JSON path after --")
out=Path(args[0])
roles=("surface","hinge_fixed","hinge_moving","hinge_pin","servo_mount","servo","horn","pushrod","pushrod_joint")
controls=("elevon_left","elevon_right","rudder_left","rudder_right")
inventory={}
for o in bpy.data.objects:
    group=o.get("hydrofoam_control")
    role=o.get("hydrofoam_role")
    if group or role:
        inventory.setdefault(str(group),{}).setdefault(str(role),[]).append(o.name)
rows=[]
for name in controls:
    found=inventory.get(name,{})
    missing=[role for role in roles if not found.get(role)]
    invalid=[]
    for role,names in found.items():
        for obj_name in names:
            obj=bpy.data.objects[obj_name]
            if obj.type!="MESH" or len(obj.data.polygons)==0:
                invalid.append(obj_name)
    rows.append({"control":name,"missing_roles":missing,"invalid_meshes":invalid,
                 "inventory_complete":not missing and not invalid,
                 "parts":found})
report={"version":"v352","source_blend":bpy.data.filepath,"accepted":False,
        "inventory_complete":all(x["inventory_complete"] for x in rows),
        "controls":rows,"limitations":["Object properties are explicit evidence labels, not verified physical joints.",
          "No collision-free articulation, servo torque, linkage stroke, print-fit, or flight acceptance.",
          "Run BVH sweep and physically test the printed assembly before signoff."]}
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(out,report["inventory_complete"],"accepted",False)
