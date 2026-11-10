"""v348: Blender exact triangle-mesh collision sweep for linked control assemblies.

Run: blender -b <assembly.blend> --python scripts/audit_v348_control_sweep_bvh.py -- --config docs/v348_control_sweep_input.json
Config specifies actual Blender object names and local pivot/axis, not guessed geometry.
Conservative pass: any untested part or missing required actuator is a failure.
This is a geometry test, NOT proof of strength, servo torque, water sealing or flight.
"""
import bpy, bmesh, json, sys, math, hashlib
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

MASTER_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
REQUIRED = ("left_elevon", "right_elevon", "left_rudder", "right_rudder")

def tree(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        bm.transform(evaluated.matrix_world)
        result = BVHTree.FromBMesh(bm, epsilon=0.0)
        bm.free()
        return result
    finally:
        evaluated.to_mesh_clear()

def validate(config):
    master = Path(config["master_image"])
    if not master.is_file() or hashlib.sha256(master.read_bytes()).hexdigest() != MASTER_SHA:
        raise ValueError("Final Master missing or SHA256 mismatch")
    if not isinstance(config.get("controls"), dict):
        raise ValueError("controls object required")
    if not isinstance(config.get("fixed_obstacles"), list) or not config["fixed_obstacles"]:
        raise ValueError("explicit fixed_obstacles list required")
    for name in REQUIRED:
        if name not in config["controls"]:
            raise ValueError("required control missing: " + name)

def sweep(name, data, obstacles, depsgraph):
    moving = data["moving_objects"]
    required = ("hinge", "pin", "servo_mount", "horn", "pushrod")
    missing = [k for k in required if not data.get("hardware", {}).get(k)]
    objects = {}
    for objname in moving + [v for k in required for v in data.get("hardware", {}).get(k, [])]:
        ob = bpy.data.objects.get(objname)
        if ob is None or ob.type != "MESH":
            missing.append("missing mesh: " + objname)
        else:
            objects[objname] = ob
    for item in obstacles:
        if bpy.data.objects.get(item) is None:
            missing.append("missing obstacle: " + item)
    if missing:
        return {"accepted": False, "errors": missing}
    pivot = Vector(data["pivot_world_mm"])
    axis = Vector(data["axis_world"])
    if len(pivot) != 3 or len(axis) != 3 or axis.length < 1e-9:
        raise ValueError("invalid pivot/axis for " + name)
    axis.normalize()
    angles = data.get("angles_deg", [])
    if len(angles) < 3 or min(angles) >= 0 or max(angles) <= 0 or 0 not in angles:
        raise ValueError("angles must include zero and both signed endpoints")
    # Blender object units: coordinates and pivots must use the same scene units.
    # Config name retains mm for traceability, but explicit scale is mandatory.
    pivot *= float(data["millimeter_to_scene_unit"])
    original = {n: ob.matrix_world.copy() for n, ob in objects.items()}
    static = {n: tree(bpy.data.objects[n], depsgraph) for n in obstacles}
    collisions = []
    try:
        for angle in angles:
            rotation = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(angle), 4, axis) @ Matrix.Translation(-pivot)
            for n in moving:
                objects[n].matrix_world = rotation @ original[n]
            bpy.context.view_layer.update()
            for n in moving:
                moving_tree = tree(objects[n], depsgraph)
                for obstacle, fixed_tree in static.items():
                    if n == obstacle:
                        continue
                    overlaps = moving_tree.overlap(fixed_tree)
                    if overlaps:
                        collisions.append({"angle_deg": angle, "moving": n, "obstacle": obstacle, "triangle_pairs": len(overlaps)})
    finally:
        for n, mat in original.items():
            objects[n].matrix_world = mat
        bpy.context.view_layer.update()
    return {"accepted": not collisions, "angles_checked_deg": angles, "collisions": collisions,
            "note": "BVH triangle overlap only; does not test linkage articulation or minimum clearance."}

def main():
    argv = sys.argv
    if "--config" not in argv:
        raise ValueError("pass --config path")
    path = Path(argv[argv.index("--config") + 1])
    config = json.loads(path.read_text(encoding="utf-8"))
    validate(config)
    dg = bpy.context.evaluated_depsgraph_get()
    report = {"schema": "v348", "final_master_sha256": MASTER_SHA, "controls": {}, "accepted": False}
    obstacles = config["fixed_obstacles"]
    for name in REQUIRED:
        report["controls"][name] = sweep(name, config["controls"][name], obstacles, dg)
    report["accepted"] = all(x["accepted"] for x in report["controls"].values())
    output = Path(config.get("report_path", "docs/V348_CONTROL_SWEEP_BVH_WIP.json"))
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"report": str(output), "accepted": report["accepted"]}))
    if not report["accepted"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
