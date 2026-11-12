"""v364: Blender mesh topology audit for existing control-system candidates.

Run after opening the v333 Blender assembly:
 blender -b cad/Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend --python scripts/v364_control_mesh_topology.py -- --output docs/v364_control_topology_local.json

Read-only: does not modify meshes or the source .blend. Reports disconnected
islands, non-manifold boundaries and degenerate faces. These are screening
metrics, NOT proof of printability, motion clearance or assembly.
"""
import argparse
import json
import sys
from pathlib import Path

import bpy
import bmesh

KEYWORDS = ("ELEVON", "AILERON", "RUDDER", "HINGE", "SERVO",
            "HORN", "PUSHROD", "SLEEVE", "PIN", "LINKAGE")

def topology(mesh):
    bm = bmesh.new()
    try:
        bm.from_mesh(mesh)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        remaining = set(bm.verts)
        islands = []
        while remaining:
            seed = remaining.pop()
            stack = [seed]
            size = 1
            while stack:
                v = stack.pop()
                for e in v.link_edges:
                    n = e.other_vert(v)
                    if n in remaining:
                        remaining.remove(n)
                        stack.append(n)
                        size += 1
            islands.append(size)
        return {
            "vertices": len(bm.verts),
            "edges": len(bm.edges),
            "faces": len(bm.faces),
            "connected_components": len(islands),
            "component_vertex_counts": sorted(islands, reverse=True),
            "boundary_edges": sum(e.is_boundary for e in bm.edges),
            "wire_edges": sum(e.is_wire for e in bm.edges),
            "non_manifold_edges": sum(not e.is_manifold for e in bm.edges),
            "degenerate_faces": sum(f.calc_area() <= 1e-12 for f in bm.faces),
        }
    finally:
        bm.free()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    opts = parser.parse_args(args)
    if not bpy.data.filepath:
        raise SystemExit("Load an actual .blend assembly first")
    target = Path(opts.output).resolve()
    if target.exists():
        raise SystemExit("Refusing overwrite: " + str(target))
    deps = bpy.context.evaluated_depsgraph_get()
    parts = []
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH" or not any(w in obj.name.upper() for w in KEYWORDS):
            continue
        evaluated = obj.evaluated_get(deps)
        mesh = evaluated.to_mesh()
        try:
            data = topology(mesh)
            data["name"] = obj.name
            data["parent"] = obj.parent.name if obj.parent else None
            data["negative_determinant"] = obj.matrix_world.determinant() < 0
            data["scale"] = [float(x) for x in obj.scale]
            data["closed_two_manifold_candidate"] = (
                data["faces"] > 0 and data["non_manifold_edges"] == 0
                and data["degenerate_faces"] == 0
            )
            parts.append(data)
        finally:
            evaluated.to_mesh_clear()
    result = {
        "source": bpy.data.filepath,
        "approval": False,
        "candidate_count": len(parts),
        "parts": parts,
        "limitations": [
            "Closed manifold is not sufficient for printable thickness, tolerances or fit.",
            "Disconnected islands can be intentional but require manual assembly review.",
            "No kinematic sweep, physical load or water-tightness test is performed.",
            "Evaluated mesh geometry is inspected; source assembly remains untouched."
        ]
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("v364 topology candidates:", len(parts), "approval: NO")

if __name__ == "__main__":
    main()
