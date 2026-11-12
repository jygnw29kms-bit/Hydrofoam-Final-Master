"""v351: Build and sweep-test an isolated rudder hinge assembly.

Blender 4.x: blender -b --python scripts/build_v351_rudder_hinge_sweep.py -- exports/v351
This is a manufactured-scale fixture, not integrated with the Final Master.
The actual master rudder hinge axes, servo horn travel and fuselage collisions
must be checked separately before accepting a flight-ready assembly.
"""
import bpy, bmesh, json, math, sys
from pathlib import Path
from mathutils import Matrix
from mathutils.bvhtree import BVHTree

args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
out=Path(args[0]) if args else Path("exports/v351")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=0.001

def block(name,xyz,dims):
    bpy.ops.mesh.primitive_cube_add(size=1,location=xyz)
    obj=bpy.context.object
    obj.name=name
    obj.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return obj

def cylinder(name,xyz,radius,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,location=xyz,radius=radius,depth=depth)
    obj=bpy.context.object
    obj.name=name
    return obj

def boolean(a,b,operation):
    mod=a.modifiers.new("watertight_"+operation,"BOOLEAN")
    mod.operation=operation
    mod.solver="EXACT"
    mod.object=b
    bpy.context.view_layer.objects.active=a
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(b,do_unlink=True)

def make_leaf(name,side):
    # Three alternating knuckles on a 19 mm long hinge axis (Z).
    # The moving leaf is offset from the fixed leaf by a 0.6 mm face gap.
    leaf=block(name,(side*7.5,0,0),(8,3.5,19))
    for z in ((-6.4,6.4) if side<0 else (0,)):
        h=5.4 if side<0 else 6.0
        knuckle=cylinder("knuckle",(0,0,z),3.35,h)
        boolean(leaf,knuckle,"UNION")
    # Bore through entire assembly: 2.7 mm nominal hole for 2.4 mm pin.
    bore=cylinder("pin_clearance",(0,0,0),1.35,23)
    boolean(leaf,bore,"DIFFERENCE")
    return leaf

fixed=make_leaf("v351_fixed_rudder_hinge_WIP",-1)
moving=make_leaf("v351_moving_rudder_hinge_WIP",1)
pin=cylinder("v351_removable_pin_WIP",(0,0,0),1.2,20.0)

def bvh(obj,angle=0):
    bm=bmesh.new()
    bm.from_mesh(obj.data)
    bm.transform(Matrix.Rotation(math.radians(angle),4,"Z") @ obj.matrix_world)
    tree=BVHTree.FromBMesh(bm,epsilon=0)
    bm.free()
    return tree

# BVH overlap can flag intentional contact or near-coplanar interfaces.
# This check excludes the pin, which intentionally occupies the hinge bore.
static=bvh(fixed)
samples=[]
for deg in range(-30,31,2):
    hits=len(static.overlap(bvh(moving,deg)))
    samples.append({"rudder_angle_deg":deg,"overlap_triangle_pairs":hits,
                    "no_detected_mesh_intersection":hits==0})
def mesh_stats(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    result={"vertices":len(bm.verts),"faces":len(bm.faces),
            "nonmanifold_edges":sum(not e.is_manifold for e in bm.edges),
            "volume_scene_units_cubed":abs(bm.calc_volume(signed=True))}
    bm.free()
    return result

for obj in (fixed,moving,pin):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    bpy.ops.wm.stl_export(filepath=str(out/(obj.name+".stl")),export_selected_objects=True,apply_modifiers=True)

bpy.ops.wm.save_as_mainfile(filepath=str(out/"Hydrofoam_v351_rudder_hinge_sweep_WIP.blend"))
report={"version":"v351","status":"WIP_NOT_ACCEPTED","nominal_pin_mm":2.4,
        "bore_mm":2.7,"fixture_axis":"Z","angle_samples":samples,
        "all_sampled_angles_without_detected_intersection":all(x["no_detected_mesh_intersection"] for x in samples),
        "meshes":{o.name:mesh_stats(o) for o in (fixed,moving,pin)},
        "limitations":["Isolated fixture only; not assembled on master rudders.",
                       "BVH triangle overlaps are a geometric screen, not tolerance or load proof.",
                       "No servo mount, horn, linkage, waterproofing or final master fidelity proven.",
                       "Print and physically check bore, axial clearance, strength and full sweep."]}
(out/"V351_RUDDER_HINGE_SWEEP_WIP.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("WIP fixture generated; sampled sweep clear:",report["all_sampled_angles_without_detected_intersection"])
