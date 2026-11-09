"""Hydrofoam v342: fail-closed control hardware proximity and clearance audit.

Execute on Jens-PC only:
blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend -t 4 --python scripts/audit_v342_linkage_clearances.py

This is a geometric screening test, NOT a collision sweep, servo certification,
physical-fit proof, or master-image fidelity acceptance. CAD is never saved.
"""
import bpy
import hashlib
import json
from pathlib import Path
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "reference/FINAL_MASTER_ORIGINAL.jpeg"
EXPECTED = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
actual = hashlib.sha256(MASTER.read_bytes()).hexdigest()
if actual != EXPECTED:
    raise RuntimeError("Immutable Final Master SHA256 mismatch")

def world_bounds(obj):
    pts = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [(min(p[i] for p in pts), max(p[i] for p in pts)) for i in range(3)]

def aabb_gap(a, b):
    aa, bb = world_bounds(a), world_bounds(b)
    return round(sum(max(0.0, aa[i][0] - bb[i][1], bb[i][0] - aa[i][1]) ** 2
                     for i in range(3)) ** 0.5, 4)

def mesh_health(obj):
    import bmesh
    mesh = obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        return {"vertices": len(bm.verts),
                "nonmanifold_edges": sum(not edge.is_manifold for edge in bm.edges)}
    finally:
        bm.free()
        obj.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh_clear()

report = {"version": "v342", "source_blend": bpy.data.filepath,
          "master_sha256_verified": True, "accepted": False,
          "units": "Blender scene units; millimeters only if scene scale is configured accordingly",
          "sides": {}, "blocking": []}
for side in ("Left", "Right"):
    names = {"tray": f"V338_{side}_SERVO_TRAY_WIP",
             "horn": f"V338_{side}_ELEVON_HORN_WIP",
             "rod": f"V339_{side}_ELEVON_PUSHROD_REFERENCE_WIP"}
    objects = {key: bpy.data.objects.get(name) for key, name in names.items()}
    hinges = sorted((o for o in bpy.data.objects
                     if o.name.startswith(f"V337_{side}_") and "KNUCKLE" in o.name),
                    key=lambda o: o.name)
    pins = [o for o in bpy.data.objects
            if o.name.startswith(f"V337_{side}_") and "PIN" in o.name]
    entry = {"present": {k: o is not None for k, o in objects.items()},
             "hinge_knuckle_count": len(hinges), "pin_count": len(pins),
             "mesh_health": {key: mesh_health(obj) for key, obj in objects.items()
                             if obj and obj.type == "MESH"},
             "connection_gaps_aabb": {},
             "moving_parent_verified": False,
             "fixed_parent_verified": False,
             "servo_fasteners_verified": False,
             "rod_end_joints_verified": False,
             "collision_sweep_verified": False}
    if objects["rod"] and objects["horn"]:
        entry["connection_gaps_aabb"]["rod_to_horn"] = aabb_gap(objects["rod"], objects["horn"])
    if objects["rod"] and objects["tray"]:
        entry["connection_gaps_aabb"]["rod_to_tray"] = aabb_gap(objects["rod"], objects["tray"])
    if len(hinges) != 5 or len(pins) != 1 or not all(entry["present"].values()):
        report["blocking"].append(f"{side}: incomplete expected prototype hardware")
    report["sides"][side] = entry
report["blocking"] += [
    "AABB proximity is only a coarse screening metric and does not prove attachment",
    "Actual hinge axes and parent Boolean unions require inspection",
    "Selected servo dimensions, horn output center, screw mounts and clevis geometry unverified",
    "Full angle-by-angle collision and mechanical load tests missing",
    "Original Final Master three-view registration and pixel comparison missing",
    "Land, water and flight operating modes remain untested"
]
out = ROOT / "docs/V342_LINKAGE_CLEARANCE_SCREEN_WIP.json"
out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print("V342_AUDIT", json.dumps(report))
