"""v352: parametric rudder servo mounting coupon for Hydrofoam.

Blender 4.x: blender -b -P scripts/build_v352_rudder_servo_tray.py -- exports/v352
Dimensions are provisional; servo datasheet and mounting measurements required.
Not mounted in the Final Master model. No control-system acceptance implied.
"""
import bpy, json, sys
from pathlib import Path
out=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else Path("exports/v352")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=0.001

def box(name,loc,dims):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o
def cylinder(name,loc,r,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=loc)
    return bpy.context.object
def boolean(a,b,op):
    mod=a.modifiers.new("CAD_"+op,"BOOLEAN")
    mod.operation=op;mod.solver="EXACT";mod.object=b
    bpy.context.view_layer.objects.active=a
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(b,do_unlink=True)
def export(obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.ops.wm.stl_export(filepath=str(out/(obj.name+".stl")),export_selected_objects=True,apply_modifiers=True)
# 23 x 12 x 24 mm servo body is a placeholder, NOT a chosen servo.
# Tray: 3 mm floor, four 3 mm wall strips, screw slots through floor.
body_length=23.0;body_width=12.0
wall=3.0;floor=3.0
for side in ("L","R"):
    xoff=-30 if side=="L" else 30
    tray=box("v352_"+side+"_rudder_servo_tray_WIP",(xoff,0,0),(body_length+2*wall,body_width+2*wall,floor))
    cavity=box("cavity",(xoff,0,2.0),(body_length+0.6,body_width+0.6,5.0))
    # Cavity only removes upper portion of base; floor remains structurally connected.
    # Four walls rise above the base and are unioned to the same print body.
    for y in (-body_width/2-wall/2,body_width/2+wall/2):
        boolean(tray,box("side_wall",(xoff,y,4.5),(body_length+2*wall,wall,9.0)),"UNION")
    for x in (-body_length/2-wall/2,body_length/2+wall/2):
        boolean(tray,box("end_wall",(xoff+x,0,4.5),(wall,body_width+2*wall,9.0)),"UNION")
    for x in (-body_length/2-1.0,body_length/2+1.0):
        for y in (-body_width/2-1.0,body_width/2+1.0):
            hole=cylinder("mount_bore",(xoff+x,y,0),1.1,5.0)
            boolean(tray,hole,"DIFFERENCE")
    export(tray)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"Hydrofoam_v352_rudder_servo_tray_WIP.blend"))
(out/"V352_DESIGN_INTENT_WIP.json").write_text(json.dumps({"status":"WIP_NOT_INSTALLED","servo_envelope_mm":[23,12,24],"nominal_mount_hole_diameter_mm":2.2,"limitations":["No selected servo or measured flange dimensions","Not installed in final master CAD","No linkage load, interference, print or water ingress test"]},indent=2)+"\n",encoding="utf-8")
