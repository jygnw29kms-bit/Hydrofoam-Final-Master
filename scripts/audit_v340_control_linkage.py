"""Hydrofoam v340: offline-safe Blender control-surface linkage QA.

Usage: blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend --python scripts/audit_v340_control_linkage.py
Read-only to CAD. Produces docs/V340_CONTROL_LINKAGE_AUDIT.json.
No mechanical acceptance is inferred from mesh presence.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
objects=list(bpy.data.objects)
report={"version":"v340","source_blend":bpy.data.filepath,"status":"audit_only","accepted":False,"sides":{}}
for side in ("Left","Right"):
    pref="V339_"+side+"_ELEVON_PUSHROD_REFERENCE_WIP"
    rod=bpy.data.objects.get(pref)
    hinge=[o for o in objects if o.name.startswith("V337_"+side) and "KNUCKLE" in o.name]
    servo=bpy.data.objects.get("V338_"+side+"_SERVO_TRAY_WIP")
    horn=bpy.data.objects.get("V338_"+side+"_ELEVON_HORN_WIP")
    result={"rod_exists":rod is not None,"hinge_knuckles":len(hinge),"servo_tray_exists":servo is not None,"horn_exists":horn is not None,
            "mechanical_join_verified":False,"swept_collision_verified":False,"servo_screw_mount_verified":False,
            "linkage_joint_verified":False,"print_fit_verified":False}
    if rod:
        pts=[rod.matrix_world @ Vector(p) for p in rod.bound_box]
        result["rod_bounds_mm"]=[[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i in range(3)]
    report["sides"][side]=result
report["blocking"]=["Master reference image three-view alignment unverified","No verified attachment to original fixed/moving surfaces",
"No actuated collision sweep over commanded angles","Servo hardware specification and torque/load budget absent",
"No ground/water/flight testing"]
path=root/"docs/V340_CONTROL_LINKAGE_AUDIT.json"
path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("V340_AUDIT",json.dumps(report))
