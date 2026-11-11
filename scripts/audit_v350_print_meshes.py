"""v350: Blender STL manufacturing gate for Hydrofoam printed modules.

Run: blender -b --python scripts/audit_v350_print_meshes.py -- exports docs/V350_PRINT_MESH_QA_WIP.json
Only verifies mesh topology and geometric extents, not printability under load,
waterproofing, material strength, fit, linkage clearance, or Final-Master fidelity.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
root=Path(args[0]) if args else Path("exports")
dest=Path(args[1]) if len(args)>1 else Path("docs/V350_PRINT_MESH_QA_WIP.json")
results=[]
for file in sorted(root.rglob("*.stl")) if root.exists() else []:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    try:
        bpy.ops.wm.stl_import(filepath=str(file))
        objects=[o for o in bpy.context.scene.objects if o.type=="MESH"]
        if not objects: raise ValueError("no mesh imported")
        for obj in objects:
            bm=bmesh.new()
            bm.from_mesh(obj.data)
            bm.normal_update()
            boundary=sum(1 for e in bm.edges if e.is_boundary)
            nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
            loose=sum(1 for e in bm.edges if e.is_wire)
            degenerate=sum(1 for f in bm.faces if f.calc_area()<=1e-10)
            volume=abs(bm.calc_volume(signed=True)) if bm.faces else 0.0
            dims=[round(float(v),3) for v in obj.dimensions]
            status=(len(bm.faces)>0 and nonmanifold==0 and degenerate==0
                    and volume>1e-6 and all(math.isfinite(v) and v>0 for v in dims))
            results.append({"file":file.as_posix(),"object":obj.name,"vertices":len(bm.verts),
                "faces":len(bm.faces),"boundary_edges":boundary,"nonmanifold_edges":nonmanifold,
                "loose_edges":loose,"degenerate_faces":degenerate,
                "signed_volume_abs_mm3_if_scene_mm":round(volume,3),
                "dimensions_scene_units":dims,"topology_screen_pass":status})
            bm.free()
    except Exception as exc:
        results.append({"file":file.as_posix(),"topology_screen_pass":False,
                        "error":str(exc)})
dest.parent.mkdir(parents=True,exist_ok=True)
report={"version":"v350","accepted":False,"source_directory":str(root),
    "mesh_count":len(results),"topology_screen_pass":bool(results) and all(
        x["topology_screen_pass"] for x in results),
    "parts":results,"limitations":[
        "Manifold mesh does not imply printable tolerances or functional assembly.",
        "No hinge sweep, actuator loads, waterproofing, flight or ground clearance tested.",
        "Absolute millimetre dimensions require validated STL export scale.",
        "This audit does not establish correspondence to FINAL_MASTER_ORIGINAL.jpeg."]}
dest.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(dest,report["topology_screen_pass"],"accepted:",report["accepted"])
