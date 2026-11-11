"""Hydrofoam v349: mechanically parameterized rudder hinge knuckle coupon.

Blender 4.x: blender -b --python scripts/build_v349_rudder_hinge_coupon.py -- <output-folder>
Print and measure coupon before integrating it into the master CAD.
This deliberately does not claim installed, collision-free rudders.
"""
import bpy, json, sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v349")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=0.001
def block(name,position,size):
    bpy.ops.mesh.primitive_cube_add(size=1,location=position)
    o=bpy.context.object;o.name=name;o.dimensions=size
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o
def cyl(name,position,radius,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=position)
    o=bpy.context.object;o.name=name
    return o
def boolean(a,b,mode):
    m=a.modifiers.new("solid_"+mode,"BOOLEAN");m.operation=mode;m.solver="EXACT";m.object=b
    bpy.context.view_layer.objects.active=a
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b,do_unlink=True)
def stl(o):
    bpy.ops.object.select_all(action="DESELECT");o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.wm.stl_export(filepath=str(out/(o.name+".stl")),export_selected_objects=True,apply_modifiers=True)
# Hinge axis along Z. 2.4 mm nominal pin; hole includes 0.3 mm diameter clearance.
# Staggered 3-knuckle coupon with 0.35 mm axial gaps, removable pin.
knuckle_height=5.0
axial_gap=0.35
hole_diameter=2.7
outer_diameter=6.5
for i in range(3):
    z=(i-1)*(knuckle_height+axial_gap)
    side="fixed" if i%2==0 else "moving"
    ring=cyl("v349_"+side+"_knuckle_"+str(i),(0,0,z),outer_diameter/2,knuckle_height)
    bore=cyl("bore",(0,0,z),hole_diameter/2,knuckle_height+2)
    boolean(ring,bore,"DIFFERENCE")
    # Tangential flange with actual boolean union, not disconnected mesh shells.
    flange=block("flange",(5.0,0,z),(5.0,4.0,knuckle_height))
    boolean(ring,flange,"UNION")
    stl(ring)
pin=cyl("v349_removable_pin_WIP",(0,0,0),1.2,3*knuckle_height+2*axial_gap+2)
stl(pin)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"Hydrofoam_v349_rudder_hinge_coupon_WIP.blend"))
(out/"design_intent.json").write_text(json.dumps({"version":"v349","status":"UNVALIDATED_WIP","nominal_pin_diameter_mm":2.4,"hole_diameter_mm":hole_diameter,"axial_gap_mm":axial_gap,"knuckle_height_mm":knuckle_height,"limitations":["coupon only; not integrated into master geometry","print tolerance and physical movement untested","rudder angular collision envelope untested"]},indent=2)+"\n",encoding="utf-8")
