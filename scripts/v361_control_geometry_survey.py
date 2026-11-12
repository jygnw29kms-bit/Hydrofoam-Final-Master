"""Blender background inventory of real control-part geometry, v361.

Usage: blender -b cad/Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend
       --python scripts/v361_control_geometry_survey.py -- --out docs/v361_geometry_survey_local.json

Read-only geometry audit. No guessed hinge placement, no approval implied.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

KEYWORDS = ("ELEVON", "AILERON", "RUDDER", "HINGE", "SERVO", "HORN", "PUSHROD", "SLEEVE", "PIN", "LINKAGE")

def world_corners(obj):
    return [obj.matrix_world @ Vector(c) for c in obj.bound_box]

def mesh_details(obj):
    mesh = obj.data
    verts = [obj.matrix_world @ v.co for v in mesh.vertices]
    if not verts:
        return {"vertex_count": 0, "error": "empty mesh"}
    mins = [min(v[i] for v in verts) for i in range(3)]
    maxs = [max(v[i] for v in verts) for i in range(3)]
    return {
        "vertex_count": len(verts),
        "edge_count": len(mesh.edges),
        "face_count": len(mesh.polygons),
        "world_aabb_min_m": mins,
        "world_aabb_max_m": maxs,
        "world_aabb_size_m": [maxs[i]-mins[i] for i in range(3)],
        "object_origin_m": list(obj.matrix_world.translation),
        "rotation_euler_rad": list(obj.matrix_world.to_euler()),
        "scale": list(obj.scale),
        "nonmanifold_edge_count": sum(1 for e in mesh.edges if not e.is_manifold) if hasattr(mesh.edges[0], "is_manifold") else None,
        "parent": obj.parent.name if obj.parent else None,
        "modifiers": [{"name": m.name, "type": m.type} for m in obj.modifiers],
    }

def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out":
        raise SystemExit("Expected -- --out PATH")
    result = {"source_blend": bpy.data.filepath, "blender_version": bpy.app.version_string,
              "unit_scale": bpy.context.scene.unit_settings.scale_length,
              "unit_system": bpy.context.scene.unit_settings.system,
              "candidate_count": 0, "candidates": {}, "warnings": [],
              "release_approved": False}
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH" or not any(k in obj.name.upper() for k in KEYWORDS):
            continue
        try:
            result["candidates"][obj.name] = mesh_details(obj)
        except Exception as exc:
            result["warnings"].append({"object": obj.name, "error": str(exc)})
    result["candidate_count"] = len(result["candidates"])
    result["warnings"].append("Bounding boxes alone do not establish clearance, linkage movement, watertightness or printability.")
    out = Path(args[1])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("v361 candidate meshes:", result["candidate_count"], "report:", out)

if __name__ == "__main__":
    main()
