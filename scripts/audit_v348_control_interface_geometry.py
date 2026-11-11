"""v348: Extract measured control-interface geometry from a real Blender assembly.

Run inside Blender: blender -b cad/<actual WIP>.blend --python scripts/audit_v348_control_interface_geometry.py -- --output docs/V348_CONTROL_INTERFACE_MEASURED_WIP.json

This is an INVENTORY and dimensional evidence, never a mechanical acceptance.
Coordinates are transformed into world space; dimensions use Blender scene units
and are converted to mm via scene.unit_settings.scale_length.
No geometry is generated and no missing hinge or servo is assumed to exist.
"""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

KEYWORDS = {
    "hinge": ("hinge", "knuckle", "scharnier"),
    "pin": ("pin", "stift", "axle"),
    "servo_mount": ("servo", "tray", "halter"),
    "horn": ("horn", "ruderhorn"),
    "pushrod": ("pushrod", "linkage", "gestaenge", "rod"),
    "control_surface": ("elevon", "aileron", "rudder", "elevator", "ruder"),
}
SIDES = {"left": ("left", "_l", ".l", "port"),
         "right": ("right", "_r", ".r", "starboard")}
EXPECTED = ("hinge", "pin", "servo_mount", "horn", "pushrod", "control_surface")


def side_of(name):
    low = name.lower()
    matches = [side for side, aliases in SIDES.items()
               if any(alias in low for alias in aliases)]
    return matches[0] if len(matches) == 1 else "unclassified"


def role_of(name):
    low = name.lower()
    for role in ("pushrod", "servo_mount", "horn", "pin", "hinge", "control_surface"):
        if any(word in low for word in KEYWORDS[role]):
            return role
    return None


def mesh_evidence(obj, mm):
    mesh = obj.data
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        nonmanifold = sum(not e.is_manifold for e in bm.edges)
        loose = sum(e.is_wire for e in bm.edges)
        bounds = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
        minima = [min(v[i] for v in bounds) * mm for i in range(3)]
        maxima = [max(v[i] for v in bounds) * mm for i in range(3)]
        return {
            "vertices": len(mesh.vertices),
            "faces": len(mesh.polygons),
            "nonmanifold_edges": nonmanifold,
            "loose_edges": loose,
            "world_bbox_min_mm": [round(v, 4) for v in minima],
            "world_bbox_max_mm": [round(v, 4) for v in maxima],
            "world_bbox_size_mm": [round(b-a, 4) for a, b in zip(minima, maxima)],
            "watertight_mesh_screen": nonmanifold == 0 and loose == 0 and len(mesh.polygons) > 0,
        }
    finally:
        bm.free()


def run():
    if not bpy.data.filepath:
        raise RuntimeError("A saved source .blend is required")
    scale = bpy.context.scene.unit_settings.scale_length
    if not math.isfinite(scale) or scale <= 0:
        raise RuntimeError("Invalid Blender scene unit scale")
    mm = 1000.0 * scale
    inventory = []
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH":
            continue
        role = role_of(obj.name)
        if role is None:
            continue
        inventory.append({
            "name": obj.name,
            "role": role,
            "side": side_of(obj.name),
            "parent": obj.parent.name if obj.parent else None,
            "dimensions": mesh_evidence(obj, mm),
        })
    by_side = {}
    for side in SIDES:
        found = {entry["role"] for entry in inventory if entry["side"] == side}
        by_side[side] = {
            "found_roles": sorted(found),
            "missing_roles": sorted(set(EXPECTED) - found),
        }
    return {
        "version": "v348",
        "source_blend": bpy.data.filepath,
        "scene_scale_length": scale,
        "inventory": inventory,
        "by_side": by_side,
        "acceptance": {
            "final_master_photo_match": False,
            "integrated_hinges_verified": False,
            "collision_free_full_throw_verified": False,
            "land_water_air_verified": False,
        },
        "limitations": [
            "Names are only heuristics; unclassified parts need manual CAD review.",
            "Watertight individual meshes do not prove fused load-bearing interfaces.",
            "Bounding boxes do not prove fit, collisions, hinge axes or linkage travel.",
            "No final-master pixel comparison, physical test or printable fit validation.",
        ],
    }


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(argv) != 2 or argv[0] != "--output":
        raise SystemExit("Expected -- --output docs/V348_CONTROL_INTERFACE_MEASURED_WIP.json")
    result = run()
    output = Path(argv[1])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    print("v348 measured", len(result["inventory"]), "mesh parts; final acceptance: FALSE")
