"""v400: fail-closed integrated control-surface clearance audit.

Run in Blender's Python with --background --python scripts/v400_control_surface_audit.py
-- <manifest.json>. This is an audit, not an automatic airworthiness approval.

Manifest contains object names and angles in degrees, with per-surface
hinge_origin_m, hinge_axis, moving_objects, fixed_objects, angles_deg,
servo_mount_objects, horn_objects, linkage_objects, and expected_stroke_mm.
All meshes must be actual installed components in the open .blend file.
"""
import bpy, json, sys, math, os
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

def fail(msg):
    raise ValueError(msg)

def world_triangles(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    ev = obj.evaluated_get(deps)
    mesh = ev.to_mesh()
    try:
        mesh.calc_loop_triangles()
        mat = ev.matrix_world
        vertices = [mat @ v.co for v in mesh.vertices]
        triangles = [tuple(p.vertices) for p in mesh.loop_triangles]
        if not triangles: fail("Empty mesh: " + obj.name)
        return vertices, triangles
    finally:
        ev.to_mesh_clear()

def tree(obj):
    vertices, triangles = world_triangles(obj)
    return BVHTree.FromPolygons(vertices, triangles, all_triangles=True, epsilon=0)

def check_names(names, label):
    if not isinstance(names, list) or not names: fail(label + " must be a nonempty list")
    for name in names:
        ob = bpy.data.objects.get(name)
        if ob is None or ob.type != "MESH": fail("Missing mesh: " + str(name))
    return [bpy.data.objects[n] for n in names]

def audit(manifest):
    surfaces = manifest.get("surfaces")
    if not isinstance(surfaces, list) or not surfaces: fail("No surfaces specified")
    expected = set(manifest.get("required_surfaces", []))
    found = set()
    results = []
    for item in surfaces:
        name = item["name"]
        if name in found: fail("Duplicate surface: " + name)
        found.add(name)
        moving = check_names(item["moving_objects"], name + ".moving_objects")
        fixed = check_names(item["fixed_objects"], name + ".fixed_objects")
        mounts = check_names(item["servo_mount_objects"], name + ".servo_mount_objects")
        horns = check_names(item["horn_objects"], name + ".horn_objects")
        linkages = check_names(item["linkage_objects"], name + ".linkage_objects")
        # No fixed part may be omitted merely to suppress a collision.
        if set(item["moving_objects"]) & set(item["fixed_objects"]):
            fail("Moving/fixed overlap in manifest: " + name)
        origin = Vector(item["hinge_origin_m"])
        axis = Vector(item["hinge_axis"]).normalized()
        if axis.length < 0.99: fail("Invalid hinge axis: " + name)
        angles = item["angles_deg"]
        if not angles or 0 not in angles or len(set(angles)) != len(angles):
            fail("Angle sweep must contain 0 and unique samples: " + name)
        if max(angles)-min(angles) < 2: fail("Insufficient sweep: " + name)
        if item.get("expected_stroke_mm", 0) <= 0:
            fail("Missing positive measured servo stroke: " + name)
        original = {ob.name: ob.matrix_world.copy() for ob in moving}
        collisions = []
        try:
            for angle in sorted(angles):
                rot = Matrix.Translation(origin) @ Matrix.Rotation(
                    math.radians(angle), 4, axis) @ Matrix.Translation(-origin)
                for ob in moving: ob.matrix_world = rot @ original[ob.name]
                bpy.context.view_layer.update()
                for m in moving:
                    mt = tree(m)
                    for f in fixed:
                        # BVH triangle contact is conservative; intended hinge
                        # contacts need a documented exclusion, not silent PASS.
                        if mt.overlap(tree(f)):
                            collisions.append({"angle_deg":angle,
                                               "moving":m.name,"fixed":f.name})
        finally:
            for ob in moving: ob.matrix_world = original[ob.name]
            bpy.context.view_layer.update()
        results.append({"name":name,"angles_checked":len(angles),
                        "servo_mounts":len(mounts),"horns":len(horns),
                        "linkages":len(linkages),"collisions":collisions,
                        "pass":not collisions})
    if expected and found != expected:
        fail("Surface inventory mismatch: missing=" + str(sorted(expected-found)) +
             " unexpected=" + str(sorted(found-expected)))
    if not expected: fail("required_surfaces must enumerate all aircraft control surfaces")
    return {"status":"GEOMETRY_PASS_ONLY" if all(r["pass"] for r in results)
            else "GEOMETRY_FAIL", "surfaces":results,
            "limitations":["BVH tests triangle intersections, not swept volume between samples",
                           "No servo motion or linkage articulation is simulated",
                           "No tolerance, bearing load, waterproofing, flight or print validation",
                           "No photographic master comparison performed"]}

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(args) != 1: fail("Supply exactly one manifest path after --")
    path = os.path.abspath(args[0])
    output = os.path.splitext(path)[0] + ".audit.json"
    try:
        with open(path, encoding="utf-8") as f: manifest = json.load(f)
        report = audit(manifest)
    except Exception as exc:
        report = {"status":"FAIL_EXCEPTION","error":str(exc)}
    with open(output,"w",encoding="utf-8") as f:
        json.dump(report,f,indent=2)
    print(json.dumps({"status":report["status"],"report":output}))
    if report["status"] != "GEOMETRY_PASS_ONLY": sys.exit(1)
