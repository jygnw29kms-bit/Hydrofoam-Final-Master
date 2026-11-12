"""Hydrofoam v355: printable adjustable micro-servo tray and control-horn coupon.

Blender 4.2+ background: blender -b -P scripts/build_v355_servo_tray.py
Output is WIP geometry, not installed into master; dimensions require measurement
of the actual servo and local hull clearance before assembly approval.
Units: millimetres. No changes to original reference or README.
"""
import bpy, json, os
from pathlib import Path

root=Path(bpy.path.abspath("//"))
out=root/"cad"/"v355_servo_tray_WIP"
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system="METRIC"
bpy.context.scene.unit_settings.scale_length=0.001

# Adjustable nominal envelope: 23 x 12.5 mm servo body, 2.5 mm wall.
SERVO_L=23.0
SERVO_W=12.5
BODY_CLEARANCE=0.5
WALL=2.5
BASE=3.0
TRAY_HEIGHT=12.0
SCREW_D=2.3
SCREW_X=18.0
SCREW_Y=10.0

def box(name, loc, dims):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.dimensions=dims
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o
def cylinder(name,loc,r,depth):
    bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=r,depth=depth,location=loc)
    return bpy.context.object
def boolean(a,b,operation):
    m=a.modifiers.new("solid_"+operation,"BOOLEAN")
    m.operation=operation;m.solver="EXACT";m.object=b
    bpy.context.view_layer.objects.active=a
    bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.data.objects.remove(b,do_unlink=True)
def export(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active=o
    bpy.ops.wm.stl_export(filepath=str(out/(o.name+".stl")),export_selected_objects=True,apply_modifiers=True)

length=SERVO_L+2*BODY_CLEARANCE+2*WALL
width=SERVO_W+2*BODY_CLEARANCE+2*WALL
tray=box("v355_servo_tray_WIP",(0,0,TRAY_HEIGHT/2),(length,width,TRAY_HEIGHT))
cavity=box("servo_pocket",(0,0,BASE+(TRAY_HEIGHT-BASE+1)/2),
           (SERVO_L+2*BODY_CLEARANCE,SERVO_W+2*BODY_CLEARANCE,TRAY_HEIGHT-BASE+1))
boolean(tray,cavity,"DIFFERENCE")
# Base holes lie under pocket and permit fastening from above before servo insertion.
for x in (-SCREW_X/2,SCREW_X/2):
    for y in (-SCREW_Y/2,SCREW_Y/2):
        bore=cylinder("base_screw",(x,y,BASE/2),SCREW_D/2,BASE+2)
        boolean(tray,bore,"DIFFERENCE")
# Cable exit is a through-wall notch, not an enclosed cable trap.
notch=box("cable_exit",(length/2-WALL/2,0,TRAY_HEIGHT-2),(WALL+2,5,5))
boolean(tray,notch,"DIFFERENCE")
export(tray)

# A separate horn blank with 2.2 mm linkage pin hole. Servo spline interface
# deliberately omitted: must use a verified manufacturer horn.
horn=box("v355_control_horn_blank_WIP",(45,0,2),(16,7,4))
pin=cylinder("horn_linkage_hole",(50,0,2),1.1,8)
boolean(horn,pin,"DIFFERENCE")
export(horn)
bpy.ops.wm.save_as_mainfile(filepath=str(out/"Hydrofoam_v355_servo_tray_WIP.blend"))
report={
 "version":"v355","status":"UNVALIDATED_WIP",
 "servo_body_nominal_mm":[SERVO_L,SERVO_W],
 "body_clearance_each_side_mm":BODY_CLEARANCE,
 "wall_mm":WALL,"base_mm":BASE,"mount_hole_diameter_mm":SCREW_D,
 "limitations":[
  "servo size and mounting screw spacing must be measured",
  "no verified servo horn spline interface",
  "tray not yet located in hull; no master-shape or interference approval",
  "print fit, load testing and complete linkage sweep outstanding"
 ]}
(out/"design_intent.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print("v355 generated",out)
