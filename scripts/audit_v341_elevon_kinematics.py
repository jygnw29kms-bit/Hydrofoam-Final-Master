"""Hydrofoam v341: non-destructive kinematic feasibility gate for both elevons.

Run on Jens-PC:
blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend --python scripts/audit_v341_elevon_kinematics.py
This is an analytical screening test, NOT proof of collision-free motion.
"""
import bpy, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
angles=(-20,-15,-10,-5,0,5,10,15,20)
results={}
for side,sgn in (("Left",-1),("Right",1)):
    hinge_a=Vector((175,sgn*54,28.8))
    hinge_b=Vector((174,sgn*162,28.8))
    axis=(hinge_b-hinge_a).normalized()
    # Provisional points taken from v338/v339 reference scripts.
    # Neither is a verified servo output or actual clevis connection.
    servo=Vector((143,sgn*100,22))
    horn=Vector((183,sgn*100,28.8))
    base=horn-hinge_a
    samples=[]
    for deg in angles:
        from mathutils import Quaternion
        rotated=hinge_a+Quaternion(axis,math.radians(deg)) @ base
        length=(rotated-servo).length
        samples.append({"angle_deg":deg,"required_fixed_endpoint_distance_mm":round(length,3)})
    lengths=[s["required_fixed_endpoint_distance_mm"] for s in samples]
    objects={
        "five_hinge_knuckles":sum(1 for o in bpy.data.objects if o.name.startswith("V337_"+side) and "KNUCKLE" in o.name),
        "servo_tray":bpy.data.objects.get("V338_"+side+"_SERVO_TRAY_WIP") is not None,
        "horn":bpy.data.objects.get("V338_"+side+"_ELEVON_HORN_WIP") is not None,
        "pushrod_reference":bpy.data.objects.get("V339_"+side+"_ELEVON_PUSHROD_REFERENCE_WIP") is not None
    }
    results[side]={"objects":objects,"samples":samples,
        "length_variation_mm":round(max(lengths)-min(lengths),3),
        "kinematic_feasibility":"NOT_VERIFIED",
        "reason":"A rigid pushrod with a stationary servo endpoint cannot vary its length. Servo horn sweep, pivots and linkage joints must be modeled."}
report={"version":"v341","status":"analytical_screening_only","accepted":False,
    "source_blend":bpy.data.filepath,"angles_deg":list(angles),"sides":results,
    "reference_geometry_only":True,
    "blocking":["Provisional hinge axis and endpoints, not verified against original CAD attachment geometry",
                "No actual servo rotation or servo-horn pivot modeled",
                "No swept-volume collision proof, mechanical union, or print-fit measurement",
                "No photographic three-view overlay of immutable Final Master",
                "No land, water or flight physical verification"]}
out=root/"docs/V341_ELEVON_KINEMATIC_FEASIBILITY.json"
out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("V341_KINEMATIC_GATE",json.dumps({"accepted":False,"length_variation_mm":{k:v["length_variation_mm"] for k,v in results.items()}}))
