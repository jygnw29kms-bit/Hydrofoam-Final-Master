"""v350: audit v349 hinge coupon STL geometry and pin clearances in Blender.

Usage: blender -b --python scripts/audit_v350_hinge_coupon.py -- exports/v349
A coupon is not a validated rudder installation. This check rejects missing,
open or nonmanifold meshes and reports nominal (not measured) clearances.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
folder=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v349")
expected=["v349_fixed_knuckle_0","v349_moving_knuckle_1","v349_fixed_knuckle_2","v349_removable_pin_WIP"]
results=[]
for name in expected:
    path=folder/(name+".stl")
    if not path.is_file():
        results.append({"part":name,"exists":False,"watertight":False,"error":"STL missing"})
        continue
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.wm.stl_import(filepath=str(path))
    objs=list(bpy.context.selected_objects)
    if len(objs)!=1 or objs[0].type!="MESH":
        results.append({"part":name,"exists":True,"watertight":False,"error":"STL must contain one mesh"})
        continue
    mesh=objs[0].data
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bm.normal_update()
    bad_edges=sum(1 for edge in bm.edges if not edge.is_manifold)
    boundary=sum(1 for edge in bm.edges if edge.is_boundary)
    zero_faces=sum(1 for face in bm.faces if face.calc_area()<1e-8)
    volume=abs(bm.calc_volume(signed=True))
    dims=[round(float(v),4) for v in objs[0].dimensions]
    results.append({"part":name,"exists":True,"watertight":bad_edges==0 and zero_faces==0 and volume>0,
                    "nonmanifold_edges":bad_edges,"boundary_edges":boundary,
                    "degenerate_faces":zero_faces,"volume_mm3":round(volume,4),
                    "bounds_mm":dims})
    bm.free()
all_meshes_pass=all(row["watertight"] for row in results)
# Design clearances only. Never claim as-built fit from nominal STL geometry.
pin_diameter_mm=2.4
hole_diameter_mm=2.7
axial_gap_mm=0.35
report={"version":"v350","status":"UNVALIDATED_WIP",
        "mesh_screen_pass":all_meshes_pass,"mechanical_acceptance":False,
        "nominal_diametral_clearance_mm":round(hole_diameter_mm-pin_diameter_mm,4),
        "nominal_radial_clearance_mm":round((hole_diameter_mm-pin_diameter_mm)/2,4),
        "nominal_axial_gap_mm":axial_gap_mm,
        "parts":results,
        "mandatory_next_tests":["print coupon with final filament and P2S profile",
            "measure bore and pin with calipers at several heights",
            "verify free rotation and retention after wet/dry cycling",
            "integrate hinge leaves with actual rudder and fin solids",
            "BVH collision sweep with actual linkage and servo travel",
            "prove structural load path and all LAND/WATER/AIR requirements"]}
folder.mkdir(parents=True,exist_ok=True)
destination=folder/"V350_HINGE_COUPON_MESH_QA_WIP.json"
destination.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(destination,"mesh_screen_pass",all_meshes_pass,"mechanical_acceptance",False)
