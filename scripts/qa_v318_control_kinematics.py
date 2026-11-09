import math,json,os
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# First-order small-angle pushrod model; actual linkage axes and collision sweep not yet measured.
servo_arm_mm=10.0;horn_mm=15.0;servo_sweep_deg=35.0
stroke=servo_arm_mm*math.sin(math.radians(servo_sweep_deg))
rudder_angle=math.degrees(math.asin(min(1,stroke/horn_mm)))
checks=[]
for name,required in [('aileron_up',20),('aileron_down',15),('rudder',25)]:
 checks.append({'axis':name,'design_target_deg':required,'idealized_available_deg':round(rudder_angle,2),'idealized_pass':rudder_angle>=required})
report={'version':'v318','study':'preliminary servo linkage travel sizing','servo_arm_mm':servo_arm_mm,'control_horn_mm':horn_mm,'servo_sweep_each_direction_deg':servo_sweep_deg,'estimated_linear_stroke_mm':round(stroke,3),'estimated_surface_deflection_deg':round(rudder_angle,2),'checks':checks,'assumptions':['perfect perpendicular pushrod, no lost motion','identical control horn geometry on aileron and rudder','no servo endpoint restrictions or hinge-offset correction','target deflections are provisional engineering inputs, not flight-proven'],'blockers':['measure actual hinge and horn geometry from CAD','kinematic collision sweep at +/- travel','hinge-moment torque and servo selection','sealed linkage penetration','CG and mode-specific ground/water clearance'],'certification':'NOT VALIDATED'}
p=os.path.join(R,'docs','V318_CONTROL_KINEMATICS_QA.json');open(p,'w').write(json.dumps(report,indent=2));print(json.dumps({'stroke_mm':report['estimated_linear_stroke_mm'],'deflection_deg':report['estimated_surface_deflection_deg'],'checks':checks},indent=2))
