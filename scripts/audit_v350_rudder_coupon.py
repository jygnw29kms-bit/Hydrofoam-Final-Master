"""v350: Blender mesh QA for the printable v349 rudder hinge coupon.

Usage: blender -b exports/v349/Hydrofoam_v349_rudder_hinge_coupon_WIP.blend \
  --python scripts/audit_v350_rudder_coupon.py -- exports/v349
This is a *coupon-only* inspection. No installed control surface is certified.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path

out = Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v349")
out.mkdir(parents=True, exist_ok=True)
expected = ["v349_fixed_knuckle_0","v349_moving_knuckle_1",
            "v349_fixed_knuckle_2","v349_removable_pin_WIP"]
report = {"version":"v350","scope":"rudder_hinge_coupon_only",
          "installed_control_mechanism_accepted":False,
          "final_master_shape_accepted":False,
          "objects":[],"errors":[]}
for name in expected:
    obj=bpy.data.objects.get(name)
    if obj is None or obj.type!="MESH":
        report["errors"].append("missing mesh: "+name)
        continue
    evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    bm=bmesh.new()
    try:
        bm.from_mesh(mesh)
        nonmanifold=sum(not edge.is_manifold for edge in bm.edges)
        volume=abs(bm.calc_volume(signed=True))
        dims=[round(float(v),4) for v in obj.dimensions]
        entry={"name":name,"vertices":len(bm.verts),"faces":len(bm.faces),
               "nonmanifold_edges":nonmanifold,"volume_mm3":round(volume,4),
               "dimensions_mm":dims}
        report["objects"].append(entry)
        if nonmanifold or volume<=0 or not all(math.isfinite(v) and v>0 for v in dims):
            report["errors"].append("invalid mesh: "+name)
    finally:
        bm.free()
        evaluated.to_mesh_clear()
# Coupon knuckle spacing and nominal pin diameter are dimensional checks,
# not a substitute for testing bore clearance or loaded articulation.
knuckles=[bpy.data.objects.get(n) for n in expected[:3]]
if all(knuckles):
    ordered=sorted(knuckles,key=lambda o:o.location.z)
    axial_gaps=[]
    for a,b in zip(ordered,ordered[1:]):
        gap=(b.location.z-b.dimensions.z/2)-(a.location.z+a.dimensions.z/2)
        axial_gaps.append(round(gap,4))
        if gap < 0.2:
            report["errors"].append("insufficient knuckle axial gap")
    report["axial_gaps_mm"]=axial_gaps
report["coupon_mesh_screen_pass"]=not report["errors"]
report["limitations"]=[
    "Independent coupon geometry only; not attached to tail or rudder.",
    "No BVH angular sweep, servo load, horn, pushrod or physical print measurement.",
    "No land/water/air operational validation and no Final Master image comparison."
]
target=out/"v350_rudder_coupon_mesh_QA_WIP.json"
target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(target, "coupon_mesh_screen_pass:", report["coupon_mesh_screen_pass"])
if report["errors"]:
    raise SystemExit(2)
