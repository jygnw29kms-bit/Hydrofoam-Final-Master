"""v348 exact triangle-intersection motion audit for named Blender mesh pairs.

Run in Blender background with --python scripts/audit_v348_motion_bvh.py -- config.json.
Config is deliberately explicit: no guessed pivot axes, mesh names or attachments.
Coordinates/pivots are Blender scene units. Every sampled pose is restored.
The tool is diagnostic only: intersecting triangles do not detect close clearances,
internal containment, joint strength, bearing fit or physical actuation.
"""
import bpy, bmesh, hashlib, json, math, sys
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "reference/FINAL_MASTER_ORIGINAL.jpeg"
SHA = "a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"

def fail(message):
    raise ValueError(message)

def vec(value, label):
    if not isinstance(value, list) or len(value) != 3 or any(
        type(v) not in (int, float) or not math.isfinite(v) for v in value
    ):
        fail(label + " must be three finite numbers")
    return Vector(value)

def get_mesh(name):
    obj = bpy.data.objects.get(name)
    if obj is None or obj.type != "MESH":
        fail("missing mesh: " + str(name))
    return obj

def bvh(obj):
    deps = bpy.context.evaluated_depsgraph_get()
    evaluated = obj.evaluated_get(deps)
    mesh = evaluated.to_mesh()
    try:
        bm = bmesh.new()
        try:
            bm.from_mesh(mesh)
            bmesh.ops.triangulate(bm, faces=list(bm.faces))
            bm.transform(evaluated.matrix_world)
            return BVHTree.FromBMesh(bm)
        finally:
            bm.free()
    finally:
        evaluated.to_mesh_clear()

def run(cfg):
    if hashlib.sha256(MASTER.read_bytes()).hexdigest() != SHA:
        fail("Final Master checksum mismatch")
    if not isinstance(cfg.get("groups"), list) or not cfg["groups"]:
        fail("config requires nonempty groups")
    if type(cfg.get("step_deg")) not in (int, float) or not 0 < cfg["step_deg"] <= 10:
        fail("step_deg must be in (0,10]")
    report = {"version":"v348", "reference_sha256":SHA,
              "blend":bpy.data.filepath, "groups":[], "accepted":False,
              "limits":["Triangle intersections only, not minimum clearance or containment.",
                        "Sampled angles cannot guarantee collision-free continuous motion.",
                        "Attachment, print fit, servo linkage and real actuation not proven."]}
    for group in cfg["groups"]:
        moving = [get_mesh(n) for n in group["moving"]]
        fixed = [get_mesh(n) for n in group["fixed"]]
        if not moving or not fixed:
            fail("every group requires moving and fixed meshes")
        if set(o.name for o in moving) & set(o.name for o in fixed):
            fail("moving and fixed sets must be disjoint")
        pivot = vec(group["pivot"], "pivot")
        axis = vec(group["axis"], "axis")
        if axis.length < 1e-9:
            fail("zero rotation axis")
        axis.normalize()
        lo, hi = group["range_deg"]
        if not all(type(x) in (int, float) and math.isfinite(x) for x in (lo, hi)) or not -90 <= lo < hi <= 90:
            fail("invalid angle range")
        count = math.ceil((hi-lo)/cfg["step_deg"])
        angles = [lo + (hi-lo)*i/count for i in range(count+1)]
        original = {o.name:o.matrix_world.copy() for o in moving}
        rows = []
        try:
            for angle in angles:
                rotation = (Matrix.Translation(pivot) @
                            Matrix.Rotation(math.radians(angle), 4, axis) @
                            Matrix.Translation(-pivot))
                for obj in moving:
                    obj.matrix_world = rotation @ original[obj.name]
                bpy.context.view_layer.update()
                moving_trees = {o.name:bvh(o) for o in moving}
                fixed_trees = {o.name:bvh(o) for o in fixed}
                hits = []
                for a in moving:
                    for b in fixed:
                        triangles = moving_trees[a.name].overlap(fixed_trees[b.name])
                        if triangles:
                            hits.append({"moving":a.name, "fixed":b.name,
                                         "triangle_pairs":len(triangles)})
                rows.append({"angle_deg":round(angle,5),"intersections":hits})
        finally:
            for obj in moving:
                obj.matrix_world = original[obj.name]
            bpy.context.view_layer.update()
        report["groups"].append({"name":group["name"],"sample_count":len(rows),
                                 "sampled_intersection_free":all(not row["intersections"] for row in rows),
                                 "poses":rows})
    return report

if __name__ == "__main__":
    if "--" not in sys.argv:
        fail("usage: blender -b assembly.blend --python scripts/audit_v348_motion_bvh.py -- config.json")
    cfg_path = Path(sys.argv[sys.argv.index("--")+1])
    config = json.loads(cfg_path.read_text(encoding="utf-8"))
    result = run(config)
    output = ROOT / "docs/V348_EXACT_TRIANGLE_MOTION_WIP.json"
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print("V348", output, "accepted:", result["accepted"])
