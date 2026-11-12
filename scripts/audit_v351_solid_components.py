"""Hydrofoam v351: connected-solid and minimum-wall screening of STL parts.

Blender 4.x: blender -b --python scripts/audit_v351_solid_components.py -- exports docs/V351_SOLID_COMPONENTS_WIP.json
This supplements v350: manifold objects may contain several disconnected shells.
No physical strength, clearance, print-fit or waterproofing approval is implied.
"""
import bpy
import bmesh
import json
import math
import sys
from collections import deque
from pathlib import Path

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
root=Path(args[0]) if args else Path("exports")
destination=Path(args[1]) if len(args)>1 else Path("docs/V351_SOLID_COMPONENTS_WIP.json")
parts=[]
files=sorted(root.rglob("*.stl")) if root.exists() else []
for path in files:
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    try:
        bpy.ops.wm.stl_import(filepath=str(path))
        objects=[obj for obj in bpy.context.scene.objects if obj.type=="MESH"]
        if not objects:
            raise ValueError("STL contained no mesh objects")
        for obj in objects:
            mesh=bmesh.new()
            try:
                mesh.from_mesh(obj.data)
                mesh.verts.ensure_lookup_table()
                seen=set()
                components=[]
                for vertex in mesh.verts:
                    if vertex.index in seen:
                        continue
                    pending=[vertex]
                    seen.add(vertex.index)
                    count=0
                    while pending:
                        current=pending.pop()
                        count+=1
                        for edge in current.link_edges:
                            other=edge.other_vert(current)
                            if other.index not in seen:
                                seen.add(other.index)
                                pending.append(other)
                    components.append(count)
                boundary=sum(not edge.is_manifold for edge in mesh.edges)
                inverted=not mesh.is_valid if hasattr(mesh,"is_valid") else False
                signed_volume=mesh.calc_volume(signed=True) if mesh.faces else 0.0
                dims=[float(v) for v in obj.dimensions]
                # Multiple disconnected closed shells can be legitimate, but
                # for a nominal one-piece printed module they need review.
                screen=(len(components)==1 and boundary==0 and
                        signed_volume>0 and len(mesh.faces)>0 and
                        all(math.isfinite(v) and v>0 for v in dims))
                parts.append({"file":path.as_posix(),"object":obj.name,
                              "connected_shells":len(components),
                              "shell_vertex_counts":sorted(components,reverse=True),
                              "nonmanifold_edges":boundary,
                              "signed_volume_scene_units_cubed":round(signed_volume,5),
                              "dimensions_scene_units":[round(v,4) for v in dims],
                              "single_solid_screen_pass":screen})
            finally:
                mesh.free()
    except Exception as exc:
        parts.append({"file":path.as_posix(),"single_solid_screen_pass":False,
                      "error":str(exc)})
report={"version":"v351","accepted":False,"files_checked":len(files),
        "single_solid_screen_pass":bool(parts) and all(
            p["single_solid_screen_pass"] for p in parts),
        "parts":parts,
        "limitations":["Disconnected shells may be intentionally separate parts; review each failure.",
                       "Mesh topology does not prove minimum wall thickness or structural strength.",
                       "No motion sweep, joint fit, seal integrity, or final-master image match.",
                       "Physical land, water and flight testing remains mandatory."]}
destination.parent.mkdir(parents=True,exist_ok=True)
destination.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(destination,report["single_solid_screen_pass"],"accepted:",report["accepted"])
