"""v363: Non-destructive hinge/actuator proximity survey from actual Blender meshes.

Run: blender -b cad/Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend \
 --python scripts/v363_control_pair_geometry.py -- --output docs/v363_pair_geometry_local.json

No design approval: nearest mesh-vertex distances are only a coarse screening
metric, NOT true surface clearance, kinematic validation or printability.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

WORDS = ("ELEVON", "AILERON", "RUDDER", "HINGE", "SERVO", "HORN",
         "PUSHROD", "SLEEVE", "PIN", "LINKAGE")
def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--output":
        raise SystemExit("Usage: -- --output PATH")
    if not bpy.data.filepath:
        raise SystemExit("Source .blend must be loaded")
    output = Path(args[1]).resolve()
    if output.exists():
        raise SystemExit("Refusing to overwrite " + str(output))
    scale = 1000 * bpy.context.scene.unit_settings.scale_length
    if not 0 < scale < 100000:
        raise SystemExit("Invalid unit scale")
    deps = bpy.context.evaluated_depsgraph_get()
    entries = []
    for obj in sorted(bpy.data.objects, key=lambda x: x.name):
        if obj.type != "MESH" or not any(w in obj.name.upper() for w in WORDS):
            continue
        ev = obj.evaluated_get(deps)
        mesh = ev.to_mesh()
        try:
            verts = [obj.matrix_world @ v.co for v in mesh.vertices]
            if not verts:
                continue
            low = Vector(tuple(min(v[k] for v in verts) for k in range(3)))
            high = Vector(tuple(max(v[k] for v in verts) for k in range(3)))
            entries.append({"name":obj.name, "parent":obj.parent.name if obj.parent else None,
                "center_mm":[round(x*scale,4) for x in ((low+high)/2)],
                "extent_mm":[round(x*scale,4) for x in (high-low)],
                "bbox_min_mm":[round(x*scale,4) for x in low],
                "bbox_max_mm":[round(x*scale,4) for x in high],
                "vertex_count":len(verts)})
        finally:
            ev.to_mesh_clear()
    pairs = []
    for i,a in enumerate(entries):
        for b in entries[i+1:]:
            # AABB separation is zero when boxes overlap; not a collision proof.
            delta = [max(0.0, a["bbox_min_mm"][k]-b["bbox_max_mm"][k],
                         b["bbox_min_mm"][k]-a["bbox_max_mm"][k]) for k in range(3)]
            gap = sum(x*x for x in delta)**0.5
            if gap <= 25:
                pairs.append({"a":a["name"],"b":b["name"],
                              "aabb_lower_bound_gap_mm":round(gap,4)})
    report = {"source":bpy.data.filepath,"units":"mm","approval":False,
              "parts":entries,"nearby_aabb_pairs":pairs,
              "limitations":["AABB overlap does not imply mesh collision.",
                 "AABB gap is only a lower bound on surface separation.",
                 "No servo motion, pin fits, articulation or print testing performed.",
                 "Object names are not evidence of mechanical integration."]}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    print("v363: parts",len(entries),"candidate pairs",len(pairs),"NO APPROVAL")
if __name__ == "__main__":
    main()
