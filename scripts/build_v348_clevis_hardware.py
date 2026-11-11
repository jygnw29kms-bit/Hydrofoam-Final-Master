"""v348: printable symmetric clevis ends and removable pin hardware for v339 pushrods.

Blender background: blender -b -P scripts/build_v348_clevis_hardware.py
All coordinates are provisional. Parts are separate, NOT accepted as installed linkages.
"""
import bpy, bmesh, json, math
from mathutils import Vector
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend"
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
COL = bpy.data.collections.new("V348_CLEVIS_PIN_HARDWARE_WIP")
bpy.context.scene.collection.children.link(COL)
OUT = ROOT / "stl/v348"
OUT.mkdir(parents=True, exist_ok=True)
records = []

def move_to_collection(obj):
    for c in tuple(obj.users_collection):
        c.objects.unlink(obj)
    COL.objects.link(obj)
    return obj

def cylinder(name, radius, depth, location, axis=(0,0,1), vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location)
    o = bpy.context.object
    o.name = name
    o.rotation_mode = "QUATERNION"
    o.rotation_quaternion = Vector((0,0,1)).rotation_difference(Vector(axis).normalized())
    return move_to_collection(o)

def cube(name, scale, location):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    o = bpy.context.object
    o.name = name
    o.dimensions = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return move_to_collection(o)

def boolean(target, cutter, op):
    bpy.context.view_layer.objects.active = target
    mod = target.modifiers.new("V348_" + op, "BOOLEAN")
    mod.operation = op
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)

def manifold(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bad = sum(not e.is_manifold for e in bm.edges)
    bm.free()
    return bad

# Each clevis is a U-shaped monolithic fork, printed separately from its pin.
# Dimensions are prototypes, not calibrated against installed servos.
FORK_WIDTH = 8.0
FORK_LENGTH = 12.0
FORK_HEIGHT = 8.0
SLOT_WIDTH = 3.2
PIN_DIAMETER = 2.0
PIN_HOLE_DIAMETER = 2.4
PIN_LENGTH = 10.0
for side, sign in (("Left",-1),("Right",1)):
    for end, x in (("SERVO",143.0),("ELEVON",183.0)):
        y = sign * 100.0
        z = 22.0 if end == "SERVO" else 28.8
        fork = cube("V348_%s_%s_CLEVIS_FORK_WIP" % (side,end),
                    (FORK_LENGTH,FORK_WIDTH,FORK_HEIGHT),(x,y,z))
        # Slot opens on +X; leave 3 mm closed material at -X end.
        slot = cube("V348_TEMP_SLOT",(FORK_LENGTH-3.0,SLOT_WIDTH,FORK_HEIGHT+2.0),
                    (x+1.5,y,z))
        boolean(fork,slot,"DIFFERENCE")
        bore = cylinder("V348_TEMP_BORE",PIN_HOLE_DIAMETER/2,
                        FORK_WIDTH+2,(x+2,y,z),axis=(0,1,0))
        boolean(fork,bore,"DIFFERENCE")
        pin = cylinder("V348_%s_%s_CLEVIS_PIN_WIP" % (side,end),
                       PIN_DIAMETER/2,PIN_LENGTH,(x+2,y,z),axis=(0,1,0))
        # Pins deliberately separate; a retention method remains to be designed.
        records.append(dict(side=side,end=end,fork=fork.name,pin=pin.name,
                            fork_nonmanifold_edges=manifold(fork),
                            pin_nonmanifold_edges=manifold(pin),
                            nominal_radial_clearance_mm=(PIN_HOLE_DIAMETER-PIN_DIAMETER)/2,
                            status="uninstalled prototype"))
for o in COL.objects:
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.wm.stl_export(filepath=str(OUT/(o.name+".stl")),
                          export_selected_objects=True,apply_modifiers=True)
result = {
    "version":"v348", "accepted":False, "records":records,
    "blockers":[
        "forks and pins are separate, not mounted to servo arm or elevon horn",
        "no retained pin ends or axial securing hardware",
        "fork socket and rod thread interface not constructed",
        "linkage length and control throws not solved",
        "no exact swept collision check or load/print test",
        "original Final Master visual comparison not proven",
        "land, water and flight modes not tested"
    ]
}
(ROOT/"docs/V348_CLEVIS_HARDWARE_WIP.json").write_text(
    json.dumps(result,indent=2)+"\n",encoding="utf-8")
bpy.ops.wm.save_as_mainfile(filepath=str(
    ROOT/"cad/Hydrofoam_Final_Master_v348_CLEVIS_HARDWARE_WIP.blend"))
print("V348",json.dumps(result))
