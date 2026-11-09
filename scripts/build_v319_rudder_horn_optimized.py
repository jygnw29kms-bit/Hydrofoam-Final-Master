import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v317_CONTROL_LINKAGES_WIP.blend'))
s=bpy.context.scene;horn=bpy.data.objects.get('RUDDER_HORN_PLACEHOLDER');assert horn
# reduce rudder horn lever from 15 to 12.5 model units, keeping hinge-near end as design reference
horn.dimensions=(4,11,14.5);bpy.context.view_layer.objects.active=horn;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
horn.name='RUDDER_HORN_12P5MM_PROTOTYPE'
arm=10;horn_arm=12.5;servo_deg=35;stroke=arm*math.sin(math.radians(servo_deg));angle=math.degrees(math.asin(stroke/horn_arm))
assert angle>25
report={'version':'v319','change':'rudder horn effective lever reduced from 15 to 12.5 mm (geometric placeholder revised)','servo_arm_mm':arm,'rudder_horn_effective_arm_mm':horn_arm,'servo_travel_each_side_deg':servo_deg,'idealized_pushrod_stroke_mm':round(stroke,3),'idealized_rudder_deflection_deg':round(angle,2),'rudder_target_deg':25,'first_order_pass':angle>=25,'limitations':['actual effective lever is not established by mesh dimensions alone','servo horn and rudder horn pin holes not engineered','rod length/angles must be rebuilt for physical geometry','no collision sweep or hinge moment check','not production-ready']}
open(os.path.join(R,'docs','V319_RUDDER_HORN_OPTIMIZATION_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v319'),exist_ok=True);s.render.filepath=os.path.join(R,'renders','v319','rudder_horn_optimized_iso.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v319_RUDDER_HORN_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V319_RUDDER_IDEALIZED_DEGREES',round(angle,3))
