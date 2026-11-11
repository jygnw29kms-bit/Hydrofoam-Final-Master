"""v350: validate the actual exported v349 hinge coupon meshes.

Run with Blender 4.x after v349:
 blender -b --python scripts/audit_v350_rudder_coupon_mesh.py -- exports/v349
Never treats a printed coupon or standalone hinge as installed flight hardware.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Vector
root=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v349")
files=sorted(root.glob("v349_*.stl"))
report={"version":"v350","accepted":False,"screen_pass":False,"parts":[],"errors":[]}
expected={"v349_fixed_knuckle_0","v349_moving_knuckle_1","v349_fixed_knuckle_2","v349_removable_pin_WIP"}
names={p.stem for p in files}
if names != expected:
    report["errors"].append("Missing/unexpected STL names: "+str(sorted(expected.symmetric_difference(names))))
for path in files:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.stl_import(filepath=str(path))
    objs=[o for o in bpy.context.selected_objects if o.type=="MESH"]
    if len(objs)!=1:
        report["errors"].append(path.name+": expected exactly one mesh object")
        continue
    obj=objs[0]
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
    boundary=sum(1 for e in bm.edges if e.is_boundary)
    verts=len(bm.verts);faces=len(bm.faces)
    # Connected components detect detached geometry even if every shell is watertight.
    unseen=set(bm.verts)
    components=0
    while unseen:
        components+=1
        stack=[unseen.pop()]
        while stack:
            v=stack.pop()
            for edge in v.link_edges:
                other=edge.other_vert(v)
                if other in unseen:
                    unseen.remove(other)
                    stack.append(other)
    dimensions=[round(float(x),4) for x in obj.dimensions]
    valid=nonmanifold==0 and boundary==0 and components==1 and faces>0
    report["parts"].append({"file":path.name,"vertices":verts,"faces":faces,
                            "nonmanifold_edges":nonmanifold,"boundary_edges":boundary,
                            "connected_components":components,"dimensions_mm":dimensions,
                            "watertight_single_body_screen":valid})
    if not valid:report["errors"].append(path.name+": mesh topology fails")
    bm.free()
report["screen_pass"]=not report["errors"] and len(report["parts"])==4
report["limitations"]=[
    "STL topology alone cannot demonstrate printability or strength.",
    "Nominal pin/hole clearance is not a measured printed fit.",
    "Coupon is not attached to rudder or tail; no hinge throw or collision acceptance.",
    "No LAND/WATER/AIR performance, visual-master match or final acceptance."
]
root.mkdir(parents=True,exist_ok=True)
target=root/"V350_RUDDER_COUPON_MESH_QA_WIP.json"
target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(str(target), "screen_pass:",report["screen_pass"],"accepted:",report["accepted"])
if not report["screen_pass"]:sys.exit(2)
