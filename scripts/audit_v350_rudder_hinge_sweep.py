"""v350 rudder hinge swept-volume QA, for v349 coupon geometry.

Run inside Blender 4.x:
  blender -b exports/v349/Hydrofoam_v349_rudder_hinge_coupon_WIP.blend \
    --python scripts/audit_v350_rudder_hinge_sweep.py -- exports/v350

The coupon is not a master assembly. A PASS here is not a rudder acceptance.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

out = Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v350")
out.mkdir(parents=True, exist_ok=True)
objects = [o for o in bpy.data.objects if o.type == "MESH"]
fixed = [o for o in objects if "_fixed_knuckle_" in o.name]
moving = [o for o in objects if "_moving_knuckle_" in o.name]
pins = [o for o in objects if "removable_pin" in o.name]
errors = []
if len(fixed) != 2 or len(moving) != 1 or len(pins) != 1:
    errors.append("Expected two fixed knuckles, one moving knuckle and one pin")
def mesh_check(obj):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    boundary=sum(1 for e in bm.edges if e.is_boundary)
    nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
    volume=abs(bm.calc_volume(signed=True))
    bm.free()
    return {"boundary_edges":boundary,"nonmanifold_edges":nonmanifold,"volume_mm3":round(volume,4)}
checks={o.name:mesh_check(o) for o in objects}
for name, c in checks.items():
    if c["nonmanifold_edges"] or c["boundary_edges"] or c["volume_mm3"] <= 0:
        errors.append(name+": not a closed positive-volume mesh")
def bvh(obj, transform):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(transform @ obj.matrix_world)
    tree=BVHTree.FromBMesh(bm, epsilon=0.00001)
    bm.free()
    return tree
samples=[]
if len(fixed)==2 and len(moving)==1:
    fixed_bvhs=[bvh(o,Matrix.Identity(4)) for o in fixed]
    movable=moving[0]
    for deg in range(-30,31,2):
        rotation=Matrix.Rotation(math.radians(deg),4,"Z")
        moving_bvh=bvh(movable,rotation)
        counts=[len(moving_bvh.overlap(tree)) for tree in fixed_bvhs]
        samples.append({"angle_deg":deg,"triangle_overlap_pairs":sum(counts),
                        "collision_free":sum(counts)==0})
    if any(not r["collision_free"] for r in samples):
        errors.append("Moving knuckle intersects fixed knuckles at one or more sampled angles")
else:
    errors.append("Hinge sweep could not be performed")
# The v349 pin is intentionally inserted into the bores and must not be
# tested as a forbidden overlap with the knuckles.
report={
    "version":"v350","subject":"v349 isolated rudder hinge coupon",
    "master_integrated":False,"mechanically_accepted":False,
    "tested_angles_deg":[-30,30],"step_deg":2,
    "geometry_checks":checks,"sweep":samples,"errors":errors,
    "coupon_screen_pass":not errors,
    "limitations":[
        "BVH triangle intersections do not prove print tolerances or physical clearance",
        "No servo, rudder skin, horn or pushrod geometry is part of this coupon",
        "No ground, water or air operation has been tested",
        "No photogrammetric Final Master comparison is performed"
    ]
}
(out/"V350_RUDDER_HINGE_SWEEP_WIP.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps({"coupon_screen_pass":report["coupon_screen_pass"],"errors":errors}))
if errors: raise SystemExit(2)
