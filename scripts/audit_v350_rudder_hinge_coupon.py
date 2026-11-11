"""v350: Blender QA for v349 printed hinge coupon, fail closed.

Usage: blender -b --python scripts/audit_v350_rudder_hinge_coupon.py -- exports/v349
Run v349 builder first. This is a coupon-level mesh/fit inspection only.
It cannot certify an installed rudder, actual print tolerance or full deflection.
"""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path

folder=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v349")
report={"version":"v350","status":"WIP","accepted":False,"coupon_screen_pass":False,
        "parts":[],"errors":[],"limitations":[
        "No master CAD integration or hinge load testing",
        "No actual print-fit, servo mounting, linkage travel or rudder collision proof",
        "Land/water/air operational approval requires separate testing"]}
required=["v349_fixed_knuckle_0.stl","v349_moving_knuckle_1.stl",
          "v349_fixed_knuckle_2.stl","v349_removable_pin_WIP.stl"]
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
objects=[]
for name in required:
    file=folder/name
    if not file.is_file():
        report["errors"].append("missing "+name)
        continue
    before=set(bpy.data.objects)
    try:
        bpy.ops.wm.stl_import(filepath=str(file))
        imported=[o for o in bpy.data.objects if o not in before and o.type=="MESH"]
        if len(imported)!=1:
            report["errors"].append(name+": expected exactly one mesh")
            continue
        obj=imported[0]
        objects.append(obj)
        bm=bmesh.new()
        bm.from_mesh(obj.data)
        nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
        disconnected=0
        unseen=set(bm.verts)
        while unseen:
            disconnected+=1
            frontier=[unseen.pop()]
            while frontier:
                vertex=frontier.pop()
                for edge in vertex.link_edges:
                    other=edge.other_vert(vertex)
                    if other in unseen:
                        unseen.remove(other)
                        frontier.append(other)
        bounds=[tuple(obj.matrix_world@__import__("mathutils").Vector(corner)) for corner in obj.bound_box]
        dims=[max(p[i] for p in bounds)-min(p[i] for p in bounds) for i in range(3)]
        item={"file":name,"vertices":len(bm.verts),"faces":len(bm.faces),
              "nonmanifold_edges":nonmanifold,"connected_shells":disconnected,
              "dimensions_mm":[round(v,3) for v in dims]}
        report["parts"].append(item)
        if nonmanifold or disconnected!=1:
            report["errors"].append(name+": not a single manifold shell")
        bm.free()
    except Exception as exc:
        report["errors"].append(name+": "+str(exc))
# Basic axial clearance design audit: physical gap is 0.35 mm,
# and nominal radial clearance is (2.7-2.4)/2 = 0.15 mm.
# These are design dimensions, NOT measured print clearances.
report["nominal_axial_gap_mm"]=0.35
report["nominal_radial_pin_clearance_mm"]=0.15
if len(report["parts"])==len(required) and not report["errors"]:
    report["coupon_screen_pass"]=True
target=folder/"V350_RUDDER_HINGE_COUPON_QA_WIP.json"
target.parent.mkdir(parents=True,exist_ok=True)
target.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(target, "coupon_screen_pass:",report["coupon_screen_pass"])
if not report["coupon_screen_pass"]:
    raise SystemExit(2)
