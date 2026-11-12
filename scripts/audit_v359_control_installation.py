"""Hydrofoam v359: CAD-integrated control-surface interface audit.

Blender background usage:
 blender -b assembled.blend --python scripts/audit_v359_control_installation.py -- report.json

Requires real named objects in the open .blend scene. Does not invent geometry,
does not accept loose printable coupons as installed hardware, and does not
claim physical print or flight acceptance.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

SURFACES = ("aileron_L", "aileron_R", "elevator_L", "elevator_R", "rudder")
PARTS = ("surface", "hinge_fixed", "hinge_moving", "servo_mount", "horn", "pushrod")
# Naming convention: <surface>__<part>. Fixed and moving hinge members must
# be distinct mesh objects, each explicitly associated with the control.
def evaluate():
    records = {}
    all_ok = True
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for name in SURFACES:
        row = {"parts": {}, "issues": []}
        for part in PARTS:
            key = name + "__" + part
            obj = bpy.data.objects.get(key)
            ok = obj is not None and obj.type == "MESH"
            row["parts"][part] = {"present_mesh": ok, "object": key}
            if not ok:
                row["issues"].append("missing installed mesh: " + key)
                continue
            evaluated = obj.evaluated_get(depsgraph)
            mesh = evaluated.to_mesh()
            try:
                row["parts"][part]["vertices"] = len(mesh.vertices)
                row["parts"][part]["polygons"] = len(mesh.polygons)
                if not mesh.polygons:
                    row["issues"].append("empty mesh: " + key)
                # Actual evaluated world-space bounds, not authored dimensions.
                corners = [obj.matrix_world @ Vector(c) for c in obj.bound_box]
                row["parts"][part]["world_bbox_m"] = [
                    [round(min(v[i] for v in corners), 6) for i in range(3)],
                    [round(max(v[i] for v in corners), 6) for i in range(3)],
                ]
            finally:
                evaluated.to_mesh_clear()
        # A moving hinge and surface must be associated with a common moving
        # assembly. Parent relationships are only an assembly sanity check.
        surface = bpy.data.objects.get(name + "__surface")
        moving = bpy.data.objects.get(name + "__hinge_moving")
        if surface and moving and surface.parent != moving and moving.parent != surface:
            row["issues"].append("moving hinge not parented to surface or vice versa")
        # Measured sweep evidence is required, not guessed from a static scene.
        evidence = bpy.data.objects.get(name + "__surface")
        for prop in ("measured_min_deflection_deg", "measured_max_deflection_deg",
                     "sweep_collision_report_sha256"):
            if evidence is None or prop not in evidence:
                row["issues"].append("missing measured evidence: " + prop)
        row["assembly_screen_pass"] = not row["issues"]
        # Even a passing assembly screen is not a physical mechanism approval.
        row["mechanically_accepted"] = False
        records[name] = row
        all_ok &= row["assembly_screen_pass"]
    return {
        "version": "v359",
        "source_blend": bpy.data.filepath,
        "assembly_screen_pass": bool(all_ok),
        "final_master_accepted": False,
        "physical_mechanism_accepted": False,
        "controls": records,
        "limitations": [
            "No volumetric swept collision detection or print-tolerance verification.",
            "Custom properties are evidence references, not independent verification.",
            "No photo-match, water, land or flight approval is inferred."
        ],
    }

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    output = Path(args[0]) if args else Path("reports/v359_control_installation.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evaluate(), indent=2) + "\n", encoding="utf-8")
    print("Wrote", output)
