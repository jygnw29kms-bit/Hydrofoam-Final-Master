"""Hydrofoam v367: conservative mass/CG audit of the ACTUAL Blender assembly.
Run: blender -b existing.blend --python scripts/v367_mass_cg_gate.py
Set HYDROFOAM_MASS_MANIFEST to a JSON file mapping exact Blender object names
to {"mass_g": number, "mode": "all|land|water|air"}.
No default material densities or fabricated mass values. Read-only .blend.
"""
import bpy, json, os, math
from pathlib import Path
from mathutils import Vector

manifest_path = os.environ.get("HYDROFOAM_MASS_MANIFEST")
output_path = os.environ.get("HYDROFOAM_MASS_REPORT")
if not manifest_path or not output_path:
    raise RuntimeError("Set HYDROFOAM_MASS_MANIFEST and HYDROFOAM_MASS_REPORT explicitly")
manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
if not isinstance(manifest, dict) or not manifest:
    raise ValueError("Manifest must map exact object names to measured masses")
modes = ("land", "water", "air")
objects = {o.name:o for o in bpy.data.objects if o.type == 'MESH'}
errors = []
rows = []
for name, spec in manifest.items():
    obj = objects.get(name)
    if obj is None:
        errors.append("Missing mesh: "+name)
        continue
    if not isinstance(spec, dict) or set(spec) != {"mass_g", "mode"}:
        errors.append("Invalid mass/mode specification: "+name)
        continue
    mass = spec["mass_g"]
    mode = spec["mode"]
    if isinstance(mass, bool) or not isinstance(mass, (int,float)) or not math.isfinite(mass) or mass <= 0:
        errors.append("Mass must be finite and positive: "+name)
        continue
    if mode not in (*modes, "all"):
        errors.append("Unknown mode: "+name)
        continue
    # Object origin is NOT necessarily its center of mass. Use world-space
    # mesh vertex centroid as a geometry proxy and flag it as such.
    if not obj.data.vertices:
        errors.append("Empty mesh: "+name)
        continue
    centroid = sum((obj.matrix_world @ v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
    rows.append({"name":name,"mass_g":mass,"mode":mode,
                 "vertex_centroid_scene_units":list(centroid)})
unaccounted = sorted(set(objects) - set(manifest))
if unaccounted:
    errors.append("Unaccounted mesh objects: "+str(len(unaccounted)))
summaries = {}
for mode in modes:
    selected = [r for r in rows if r["mode"] in ("all",mode)]
    total = sum(r["mass_g"] for r in selected)
    cg = [sum(r["mass_g"]*r["vertex_centroid_scene_units"][axis] for r in selected)/total
          for axis in range(3)] if total else None
    summaries[mode] = {"mass_g":total,"approx_cg_scene_units":cg,
                       "components":len(selected)}
report = {
    "status":"INCOMPLETE" if errors else "GEOMETRY_PROXY_ONLY",
    "scene_length_unit_scale":bpy.context.scene.unit_settings.scale_length,
    "modes":summaries,"components":rows,"errors":errors,
    "unaccounted_mesh_names":unaccounted,
    "limitations":[
        "Mesh vertex centroid is not physical center of mass; measured component CG required",
        "Mass values must be measured externally and supplied explicitly",
        "Does not establish stability, thrust, foil lift, structural strength or flight safety",
        "Land/water/air mode mass is not a performance acceptance",
        "No CAD modifications and no master-image changes"
    ]
}
out = Path(output_path)
if out.exists():
    raise RuntimeError("Refusing to overwrite existing report: "+str(out))
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print("HYDROFOAM_V367",report["status"],str(out))
if errors:
    raise RuntimeError("Incomplete mass inventory: see report")
