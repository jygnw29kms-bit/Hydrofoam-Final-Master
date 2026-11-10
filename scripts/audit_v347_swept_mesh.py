"""v347 WIP: evaluate moving control-surface mesh collisions in Blender.

Run: blender -b cad/<assembly>.blend --python scripts/audit_v347_swept_mesh.py -- --config docs/v347_sweep_config.json
The JSON config must contain controls: [{name, pivot_object, moving_objects,
fixed_objects, axis_local, angles_deg, clearance_mm}]. All names are exact Blender
object names. Objects are NOT modified in the saved assembly. Requires Blender.
Missing objects, invalid geometry or collision all FAIL CLOSED. This is not
proof of physical servo torque, linkage kinematics, or print tolerances.
"""
import bpy, bmesh, json, sys, math
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

def fail(message):
    raise ValueError(message)

def mesh_world(obj, matrix):
    if obj.type != "MESH":
        fail("non-mesh: " + obj.name)
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    try:
        if not mesh.vertices or not mesh.polygons:
            fail("empty mesh: " + obj.name)
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.transform(matrix)
        bm.normal_update()
        tree = BVHTree.FromBMesh(bm, epsilon=0.0)
        bm.free()
        return tree
    finally:
        evaluated.to_mesh_clear()

def world_matrix_at(obj, pivot, axis, degrees):
    # Rotate whole rigid component around the pivot's local axis in world space.
    origin = pivot.matrix_world.translation
    world_axis = (pivot.matrix_world.to_3x3() @ axis).normalized()
    rotation = Matrix.Rotation(math.radians(degrees), 4, world_axis)
    return Matrix.Translation(origin) @ rotation @ Matrix.Translation(-origin) @ obj.matrix_world

def inspect(config):
    reports = []
    for control in config["controls"]:
        required = ("name", "pivot_object", "moving_objects", "fixed_objects",
                    "axis_local", "angles_deg", "clearance_mm")
        if any(k not in control for k in required):
            fail("missing config field: " + str(control.get("name", "?")))
        names = [control["pivot_object"]] + control["moving_objects"] + control["fixed_objects"]
        missing = sorted(set(names) - set(bpy.data.objects.keys()))
        if missing:
            reports.append({"name":control["name"], "accepted":False, "missing":missing})
            continue
        pivot = bpy.data.objects[control["pivot_object"]]
        axis = Vector(control["axis_local"])
        if len(axis) != 3 or axis.length < 1e-9:
            fail("invalid axis for " + control["name"])
        axis.normalize()
        angles = [float(a) for a in control["angles_deg"]]
        if not angles or not all(math.isfinite(a) for a in angles):
            fail("invalid sweep angles")
        if float(control["clearance_mm"]) < 0:
            fail("negative clearance")
        # The BVH overlap test detects intersections, NOT positive clearance.
        # Therefore clearance_mm > 0 cannot pass without a distance checker.
        collisions = []
        fixed = [(n, mesh_world(bpy.data.objects[n], bpy.data.objects[n].matrix_world))
                 for n in control["fixed_objects"]]
        for angle in angles:
            for name in control["moving_objects"]:
                obj = bpy.data.objects[name]
                moving = mesh_world(obj, world_matrix_at(obj, pivot, axis, angle))
                for fixed_name, fixed_tree in fixed:
                    hits = moving.overlap(fixed_tree)
                    if hits:
                        collisions.append({"angle_deg":angle, "moving":name,
                                           "fixed":fixed_name, "triangle_pairs":len(hits)})
        reports.append({"name":control["name"], "tested_angles_deg":angles,
                        "collisions":collisions,
                        "clearance_verified":False,
                        "accepted":not collisions and float(control["clearance_mm"]) == 0,
                        "warning":"Triangle overlap only; no positive-gap, hinge-pin, servo or linkage acceptance."})
    return {"version":"v347", "assembly":bpy.data.filepath,
            "controls":reports,
            "accepted":bool(reports) and all(r["accepted"] for r in reports),
            "physical_acceptance":False}

def main():
    argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(argv) != 2 or argv[0] != "--config":
        fail("usage: -- --config <json>")
    config = json.loads(Path(argv[1]).read_text(encoding="utf-8"))
    result = inspect(config)
    output = Path("docs/V347_SWEPT_MESH_QA_WIP.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    if not result["accepted"]:
        sys.exit(2)

if __name__ == "__main__":
    main()
