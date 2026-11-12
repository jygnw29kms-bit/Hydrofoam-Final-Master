"""v362: Export existing control candidates as isolated, unmodified mesh snapshots.

Run on Jens-PC only:
blender -b cad/Hydrofoam_Final_Master_v333_ELEVON_ARTICULATION_WIP.blend \
  --python scripts/v362_export_control_candidates.py -- \
  --out-dir artifacts/v362_control_candidates_local

No geometry invented. No Blender source saved. The output is WIP inspection
geometry, NOT print-ready STL or a clearance/kinematics certificate.
"""
import bpy
import json
import sys
from pathlib import Path
from mathutils import Vector

KEYWORDS = ("ELEVON", "AILERON", "RUDDER", "HINGE", "SERVO",
            "HORN", "PUSHROD", "SLEEVE", "PIN", "LINKAGE")

def safe_name(name):
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:100]

def triangulated_snapshot(obj, depsgraph):
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh(preserve_all_data_layers=False, depsgraph=depsgraph)
    try:
        mesh.calc_loop_triangles()
        world = obj.matrix_world
        vertices = [world @ v.co for v in mesh.vertices]
        faces = [tuple(t.vertices) for t in mesh.loop_triangles]
        return vertices, faces
    finally:
        evaluated.to_mesh_clear()

def write_ascii_stl(path, name, verts, faces, scale):
    # STL has no units; this exporter explicitly converts Blender meters to mm.
    with path.open("w", encoding="ascii") as f:
        f.write("solid candidate\n")
        for face in faces:
            a, b, c = (verts[i] * scale for i in face)
            normal = (b - a).cross(c - a)
            if normal.length_squared:
                normal.normalize()
            f.write("facet normal %.9g %.9g %.9g\n outer loop\n" % tuple(normal))
            for v in (a, b, c):
                f.write("vertex %.9g %.9g %.9g\n" % tuple(v))
            f.write("endloop\nendfacet\n")
        f.write("endsolid candidate\n")

def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 2 or args[0] != "--out-dir":
        raise SystemExit("Usage: -- --out-dir DIRECTORY")
    if not bpy.data.filepath:
        raise SystemExit("Refusing export: no saved source .blend loaded")
    root = Path(args[1]).resolve()
    if root.exists() and any(root.iterdir()):
        raise SystemExit("Refusing to overwrite nonempty output directory: " + str(root))
    root.mkdir(parents=True, exist_ok=True)
    depsgraph = bpy.context.evaluated_depsgraph_get()
    # Blender world coordinates are converted to millimeters using scene unit scale.
    unit_scale = bpy.context.scene.unit_settings.scale_length
    if not 0 < unit_scale < 100:
        raise SystemExit("Invalid scene unit scale")
    scale = 1000.0 * unit_scale
    report = {"source": bpy.data.filepath, "unit_scale": unit_scale,
              "export_units": "mm", "approval": False, "parts": [], "errors": []}
    seen = set()
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH" or not any(k in obj.name.upper() for k in KEYWORDS):
            continue
        filename = safe_name(obj.name) + ".stl"
        if filename.lower() in seen:
            report["errors"].append({"object": obj.name, "error": "filename collision"})
            continue
        seen.add(filename.lower())
        try:
            verts, faces = triangulated_snapshot(obj, depsgraph)
            if not verts or not faces:
                raise ValueError("empty evaluated mesh")
            write_ascii_stl(root / filename, obj.name, verts, faces, scale)
            mins = [min(v[i] for v in verts) * scale for i in range(3)]
            maxs = [max(v[i] for v in verts) * scale for i in range(3)]
            report["parts"].append({"name": obj.name, "stl": filename,
                                    "vertices": len(verts), "triangles": len(faces),
                                    "bounds_min_mm": mins, "bounds_max_mm": maxs,
                                    "parent": obj.parent.name if obj.parent else None,
                                    "modifiers": [m.type for m in obj.modifiers]})
        except Exception as exc:
            report["errors"].append({"object": obj.name, "error": str(exc)})
    report["limitations"] = [
        "STL snapshots are not printable assembly designs or watertightness evidence.",
        "Object names alone do not prove correct linkage or hinge assignments.",
        "No swept-volume collision, physical servo stroke or flight test performed."
    ]
    (root / "manifest.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("v362 exported", len(report["parts"]), "candidates; errors", len(report["errors"]))
    if report["errors"] or not report["parts"]:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
