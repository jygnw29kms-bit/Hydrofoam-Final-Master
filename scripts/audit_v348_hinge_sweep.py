"""v348: fail-closed exact-mesh control-surface clearance sweep (Blender 4.x).

Run on Jens-PC:
 blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend --python scripts/audit_v348_hinge_sweep.py -- --config docs/v348_hinge_sweep_inputs.json

The config must explicitly map each moving surface to its hinge axis and all
fixed/moving linkage parts. No inferred pivots, no fabricated test results.
This checks triangular mesh intersections only, not servo torque, mechanical
attachment, waterproofing, print fit or physical operation.
"""
import bpy, bmesh, hashlib, json, math, sys
from pathlib import Path
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"reference/FINAL_MASTER_ORIGINAL.jpeg"
SHA="a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
if hashlib.sha256(MASTER.read_bytes()).hexdigest()!=SHA:
    raise RuntimeError("Final Master image checksum mismatch")
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=2 or args[0]!="--config":
    raise SystemExit("usage: blender -b scene.blend --python script.py -- --config config.json")
config=json.loads(Path(args[1]).read_text(encoding="utf-8"))
if not config.get("surfaces"):
    raise ValueError("Explicit surfaces, pivots, moving and stationary meshes required")
scene=bpy.context.scene
deps=bpy.context.evaluated_depsgraph_get()

def mesh_bvh(obj, world):
    evaluated=obj.evaluated_get(deps)
    mesh=evaluated.to_mesh()
    try:
        bm=bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm,faces=bm.faces[:])
        bm.transform(world)
        tree=BVHTree.FromBMesh(bm,epsilon=0.000001)
        bm.free()
        return tree
    finally:
        evaluated.to_mesh_clear()

def obj(name):
    o=bpy.data.objects.get(name)
    if o is None or o.type!="MESH":
        raise ValueError("Missing mesh: "+name)
    return o

def vector(v,label):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError(label+" must be three finite numbers")
    return Vector(v)

def rotate_about(pivot,axis,degrees):
    return Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(degrees),4,axis) @ Matrix.Translation(-pivot)

report={"version":"v348","source_blend":bpy.data.filepath,
        "reference_sha256":SHA,"surfaces":[],"accepted":False,
        "limitations":["BVH triangle intersection only; touching/coplanar and near-miss clearance need independent checks.",
                       "Moving pushrods require angle-specific kinematic transforms; no automatic linkage solving.",
                       "No structural attachment, print tolerance, servo load or operational verification."]}
for entry in config["surfaces"]:
    name=entry["name"]
    pivot=vector(entry["hinge_origin_scene"],"hinge_origin_scene")
    axis=vector(entry["hinge_axis_scene"],"hinge_axis_scene")
    if axis.length<1e-9: raise ValueError(name+": zero hinge axis")
    axis.normalize()
    moving=[obj(n) for n in entry["moving_meshes"]]
    fixed=[obj(n) for n in entry["stationary_meshes"]]
    if not moving or not fixed or set(moving)&set(fixed):
        raise ValueError(name+": moving/stationary sets invalid")
    angles=entry["angles_deg"]
    if not isinstance(angles,list) or not angles or any(type(a) not in (int,float) or not math.isfinite(a) or abs(a)>90 for a in angles):
        raise ValueError(name+": invalid sweep angles")
    static=[(o.name,mesh_bvh(o,o.matrix_world.copy())) for o in fixed]
    samples=[]
    for angle in angles:
        rot=rotate_about(pivot,axis,angle)
        hits=[]
        for m in moving:
            moved=mesh_bvh(m,rot @ m.matrix_world)
            for f,tree in static:
                intersections=moved.overlap(tree)
                if intersections:
                    hits.append({"moving":m.name,"fixed":f,"triangle_pair_count":len(intersections)})
        samples.append({"angle_deg":angle,"triangle_intersections":hits,"collision_free":not hits})
    report["surfaces"].append({"name":name,"moving_meshes":[o.name for o in moving],
        "stationary_meshes":[o.name for o in fixed],"samples":samples,
        "mesh_intersection_screen_pass":all(s["collision_free"] for s in samples),
        "mechanical_acceptance":False})
out=ROOT/"docs/V348_HINGE_SWEEP_WIP.json"
out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("V348_HINGE_SWEEP",out,"surfaces",len(report["surfaces"]),"accepted",False)
