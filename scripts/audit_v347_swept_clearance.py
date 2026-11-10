"""v347: Blender exact-mesh swept-clearance audit for movable control assemblies.

Run in Blender: blender -b cad/<scene>.blend --python scripts/audit_v347_swept_clearance.py -- --manifest docs/v347_control_sweep_manifest.json
Manifest describes existing scene objects, not invented mechanical geometry. All dimensions are Blender scene units.
An absent object, missing pose, non-mesh geometry, or no collision-free samples FAILS.
Results are geometric screening only: no print tolerance, strength or servo torque acceptance.
"""
import bpy, json, math, sys, hashlib
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

EXPECTED_SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"

def bvh(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        if not mesh or len(mesh.polygons) == 0:
            raise ValueError("empty mesh: " + obj.name)
        verts = [evaluated.matrix_world @ v.co for v in mesh.vertices]
        faces = [tuple(p.vertices) for p in mesh.polygons]
        return BVHTree.FromPolygons(verts, faces, all_triangles=False)
    finally:
        evaluated.to_mesh_clear()

def audit(manifest):
    original = Path("reference/FINAL_MASTER_ORIGINAL.jpeg")
    if not original.exists() or hashlib.sha256(original.read_bytes()).hexdigest() != EXPECTED_SHA:
        raise RuntimeError("immutable original missing or SHA256 mismatch")
    depsgraph = bpy.context.evaluated_depsgraph_get()
    report = {"version":"v347", "master_sha256":EXPECTED_SHA, "controls":[], "accepted":False,
              "limitations":["Mesh BVH overlap does not establish required print clearances.",
                             "No servo torque, linkage strength or physical operating-mode acceptance."]}
    all_ok = True
    for control in manifest["controls"]:
        row = {"name":control["name"],"samples":[],"accepted":False}
        moving_names = control["moving"]
        stationary_names = control["stationary"]
        required = moving_names + stationary_names
        missing = [n for n in required if n not in bpy.data.objects or bpy.data.objects[n].type != "MESH"]
        row["missing_mesh_objects"] = missing
        angles = control["angles_deg"]
        if missing or not angles or not moving_names or not stationary_names:
            all_ok = False
            report["controls"].append(row)
            continue
        axis_name = control["axis_object"]
        if axis_name not in bpy.data.objects:
            row["error"] = "missing axis object"; all_ok = False
            report["controls"].append(row); continue
        axis = bpy.data.objects[axis_name]
        direction = axis.matrix_world.to_3x3() @ __import__("mathutils").Vector((0,0,1))
        direction.normalize()
        pivot = axis.matrix_world.translation.copy()
        originals = {n:bpy.data.objects[n].matrix_world.copy() for n in moving_names}
        try:
            for angle in angles:
                rot = Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(float(angle)),4,direction) @ Matrix.Translation(-pivot)
                for name in moving_names:
                    bpy.data.objects[name].matrix_world = rot @ originals[name]
                bpy.context.view_layer.update()
                depsgraph = bpy.context.evaluated_depsgraph_get()
                hits = []
                for moving in moving_names:
                    moving_bvh = bvh(bpy.data.objects[moving],depsgraph)
                    for fixed in stationary_names:
                        if moving_bvh.overlap(bvh(bpy.data.objects[fixed],depsgraph)):
                            hits.append([moving,fixed])
                row["samples"].append({"angle_deg":angle,"overlap_pairs":hits,"clear":not hits})
        finally:
            for name, matrix in originals.items():
                bpy.data.objects[name].matrix_world = matrix
            bpy.context.view_layer.update()
        row["accepted"] = bool(row["samples"]) and all(s["clear"] for s in row["samples"])
        all_ok &= row["accepted"]
        report["controls"].append(row)
    report["accepted"] = bool(report["controls"]) and all_ok
    return report

def main():
    args = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--manifest":
        raise SystemExit("Usage: -- --manifest path/to/manifest.json")
    manifest = json.loads(Path(args[1]).read_text(encoding="utf-8"))
    report = audit(manifest)
    out = Path("docs/V347_SWEPT_CLEARANCE_WIP.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps({"accepted":report["accepted"],"report":str(out)}))
    if not report["accepted"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
