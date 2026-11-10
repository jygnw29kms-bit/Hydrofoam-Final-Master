"""v348: print-fit hinge coupon for the existing v337 2.4 mm pin system.

Runs with Blender in background: blender -b -P scripts/build_v348_hinge_fit_coupon.py
Produces independent printable coupon STLs, a .blend and a QA JSON.
This is a fit-test coupon, NOT an integrated flight control assembly.
Units are millimetres. No changes to Final Master reference or README.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"stl"/"v348"
OUT.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene
scene.unit_settings.system="METRIC"
scene.unit_settings.scale_length=0.001
scene.unit_settings.length_unit="MILLIMETERS"

def cube(name, center, size):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center)
    obj=bpy.context.object;obj.name=name
    obj.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return obj

def cylinder(name, center, radius, length, vertices=96):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=radius,depth=length,location=center)
    obj=bpy.context.object;obj.name=name
    obj.rotation_euler[0]=math.pi/2
    return obj

def boolean(target,tool,operation):
    bpy.context.view_layer.objects.active=target
    modifier=target.modifiers.new("Exact_"+operation,"BOOLEAN")
    modifier.operation=operation
    modifier.solver="EXACT"
    modifier.object=tool
    bpy.ops.object.modifier_apply(modifier=modifier.name)
    bpy.data.objects.remove(tool,do_unlink=True)

def fuse(a,b):
    boolean(a,b,"UNION")
    return a

def bore(a,b):
    boolean(a,b,"DIFFERENCE")
    return a

def mesh_qa(obj):
    bm=bmesh.new();bm.from_mesh(obj.data)
    bm.normal_update()
    result={"vertices":len(bm.verts),"faces":len(bm.faces),
            "nonmanifold_edges":sum(not e.is_manifold for e in bm.edges),
            "signed_volume_mm3":bm.calc_volume(signed=True)}
    bm.free()
    return result

# Pin 2.4 mm, axial direction Y. Separate coupons at X = +/- 24 mm.
# Hole diameter steps 2.7 / 2.9 / 3.1 mm for PETG calibration.
# Each body is a 16x15x8 mm rectangular foot with a bearing boss on top.
hole_diameters=(2.7,2.9,3.1)
rows=[]
for index,d in enumerate(hole_diameters):
    x=(index-1)*25.0
    body=cube("V348_BearingCoupon_%02d"%(index+1),(x,0,4),(16,15,8))
    boss=cylinder("V348_TemporaryBoss",(x,0,9),4.4,12)
    fuse(body,boss)
    drill=cylinder("V348_TemporaryDrill",(x,0,9),d/2,18)
    bore(body,drill)
    # Through-hole on a nominal 2.4mm pin: radial clearance = (d-2.4)/2.
    qa=mesh_qa(body)
    bpy.ops.object.select_all(action="DESELECT")
    body.select_set(True);bpy.context.view_layer.objects.active=body
    bpy.ops.wm.stl_export(filepath=str(OUT/(body.name+".stl")),export_selected_objects=True,apply_modifiers=True)
    rows.append({"name":body.name,"hole_diameter_mm":d,
                 "nominal_radial_clearance_mm":round((d-2.4)/2,3),
                 "mesh":qa})
pin=cylinder("V348_Pin_Gauge_2p4mm",(0,24,2.4),1.2,38)
pinqa=mesh_qa(pin)
bpy.ops.object.select_all(action="DESELECT");pin.select_set(True)
bpy.context.view_layer.objects.active=pin
bpy.ops.wm.stl_export(filepath=str(OUT/"V348_Pin_Gauge_2p4mm.stl"),export_selected_objects=True,apply_modifiers=True)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/"cad"/"Hydrofoam_v348_HINGE_FIT_COUPONS_WIP.blend"))
report={"version":"v348","status":"WIP print-fit coupon only","pin_diameter_mm":2.4,
        "hole_variants":rows,"pin_mesh":pinqa,
        "all_manifold":all(r["mesh"]["nonmanifold_edges"]==0 for r in rows) and pinqa["nonmanifold_edges"]==0,
        "accepted":False,
        "limitations":["No printed dimensional measurements","No integrated fixed/moving hinge tabs",
                       "No installed servo, horns, pushrods or sweep collision test",
                       "No visual Final Master comparison or three-mode acceptance"]}
(ROOT/"docs"/"V348_HINGE_FIT_COUPON_QA.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
