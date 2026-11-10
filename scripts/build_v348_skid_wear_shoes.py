"""v348: Parametric replaceable skid wear-shoe CAD, Blender 4.x background.

A sacrificial, screw-retained shoe for land testing on hard ground, short grass
and firm sand. Coordinates are millimetres; dimensions are provisional until
the Final Master float/skid attachment interface is measured. The script does
NOT modify the immutable master, existing assemblies, or README.

Run: blender -b --python scripts/build_v348_skid_wear_shoes.py -- --out exports/v348
Outputs: two mirrored STL shoes, a .blend assembly, JSON geometric QA.
No claims of assembled fit, driving capability or physical abrasion endurance.
"""
import bpy
import bmesh
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

# Provisional shoe dimensions, not dimensions extracted from master.
LENGTH_MM = 145.0
WIDTH_MM = 24.0
THICKNESS_MM = 5.0
END_RADIUS_MM = 12.0
MOUNT_SPACING_MM = 95.0
HOLE_DIAMETER_MM = 3.4
HOLE_OFFSET_Y_MM = 0.0
SIDE_OFFSET_MM = 120.0
CYLINDER_SEGMENTS = 64

def mesh_status(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    loose = sum(1 for e in bm.edges if not e.link_faces)
    nonmanifold = sum(1 for e in bm.edges if not e.is_manifold)
    signed_volume = bm.calc_volume(signed=True)
    bm.free()
    return {"loose_edges": loose, "nonmanifold_edges": nonmanifold,
            "volume_mm3": round(abs(signed_volume), 3),
            "positive_volume": abs(signed_volume) > 1.0}

def apply_modifiers(obj):
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj.select_set(False)

def make_shoe(name, y_position):
    # Flat capsule outline: rounded leading/trailing ends without snag corners.
    r = WIDTH_MM / 2.0
    straight = LENGTH_MM / 2.0 - r
    outline = []
    for cx, a0 in ((straight, -math.pi/2), (-straight, math.pi/2)):
        for i in range(33):
            a = a0 + i * math.pi / 32
            outline.append((cx + r*math.cos(a), r*math.sin(a)))
    vertices = [(x,y,0.0) for x,y in outline]
    n = len(vertices)
    vertices += [(x,y,THICKNESS_MM) for x,y in outline]
    faces = [tuple(reversed(range(n))), tuple(range(n,2*n))]
    for i in range(n):
        j=(i+1)%n
        faces.append((i,j,j+n,i+n))
    mesh=bpy.data.meshes.new(name+"_mesh")
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    obj=bpy.data.objects.new(name,mesh)
    bpy.context.collection.objects.link(obj)
    # Exact bore cuts, through the shoe; drill axes vertical.
    for index, x in enumerate((-MOUNT_SPACING_MM/2, MOUNT_SPACING_MM/2)):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=CYLINDER_SEGMENTS, radius=HOLE_DIAMETER_MM/2,
            depth=THICKNESS_MM+4.0, location=(x,HOLE_OFFSET_Y_MM,THICKNESS_MM/2))
        cutter=bpy.context.object
        cutter.name=name+"_temporary_bore_"+str(index)
        bpy.context.view_layer.objects.active=obj
        modifier=obj.modifiers.new("Through_hole_"+str(index),"BOOLEAN")
        modifier.operation="DIFFERENCE"
        modifier.solver="EXACT"
        modifier.object=cutter
        bpy.ops.object.modifier_apply(modifier=modifier.name)
        bpy.data.objects.remove(cutter,do_unlink=True)
    obj.location.y=y_position
    obj["component"]="replaceable sacrificial land skid shoe"
    obj["mount_hole_spacing_mm"]=MOUNT_SPACING_MM
    obj["nominal_hole_diameter_mm"]=HOLE_DIAMETER_MM
    return obj

def main():
    if "--" not in sys.argv:
        raise SystemExit("Pass -- --out <directory>")
    args=sys.argv[sys.argv.index("--")+1:]
    if len(args)!=2 or args[0]!="--out":
        raise SystemExit("usage: -- --out <directory>")
    out=Path(args[1]).resolve()
    out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    shoes=[make_shoe("LAND_SKID_SHOE_L_WIP",SIDE_OFFSET_MM),
           make_shoe("LAND_SKID_SHOE_R_WIP",-SIDE_OFFSET_MM)]
    qa={"version":"v348","status":"WIP","units":"mm",
        "source":"provisional geometry, not extracted from master",
        "dimensions_mm":{"length":LENGTH_MM,"width":WIDTH_MM,
                         "thickness":THICKNESS_MM,
                         "hole_spacing":MOUNT_SPACING_MM,
                         "hole_diameter":HOLE_DIAMETER_MM},
        "objects":{},"integrated_with_master":False,
        "land_water_air_accepted":False,
        "pending":["Measure actual skid-to-shoe mating surface and revise profile",
                   "Design captive threaded inserts and fastener access",
                   "Check clearance to foils and propeller through full attitude envelope",
                   "Validate material, abrasion, sand and grass tests",
                   "Verify waterproof mounting and no hull penetration"]}
    for shoe in shoes:
        qa["objects"][shoe.name]=mesh_status(shoe)
        bpy.ops.object.select_all(action="DESELECT")
        shoe.select_set(True)
        bpy.context.view_layer.objects.active=shoe
        bpy.ops.wm.stl_export(filepath=str(out/(shoe.name+".stl")),
                             export_selected_objects=True,
                             global_scale=0.001,apply_modifiers=True)
    qa["mesh_screen_pass"]=all(v["nonmanifold_edges"]==0 and
        v["loose_edges"]==0 and v["positive_volume"]
        for v in qa["objects"].values())
    bpy.ops.wm.save_as_mainfile(filepath=str(out/"Hydrofoam_v348_land_skid_shoes_WIP.blend"))
    (out/"V348_LAND_SKID_SHOES_QA_WIP.json").write_text(
        json.dumps(qa,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(qa,indent=2))

if __name__=="__main__":
    main()
