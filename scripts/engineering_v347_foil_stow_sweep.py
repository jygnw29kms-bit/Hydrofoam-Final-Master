"""v347: Foil stow/deploy kinematic clearance gate (millimetres, degrees).

Input JSON: ground_z_mm, grass_height_mm, sinkage_mm, minimum_clearance_mm,
foil_vertices_local_mm (>=3 vertices), pivot_mm, hinge_axis (3-vector),
stowed_angle_deg, deployed_angle_deg, sample_step_deg, landing_pitch_deg,
landing_roll_deg. Rotation of foil vertices about hinge axis uses Rodrigues.
Pitch/roll are applied about aircraft origin to the complete foil.
No operational acceptance is issued from geometry alone.
"""
import json, math, sys
from pathlib import Path

def vec(v):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("finite 3D vector required")
    return tuple(float(x) for x in v)

def scalar(d,key,minimum=None):
    x=d[key]
    if type(x) not in (int,float) or not math.isfinite(x) or (minimum is not None and x<minimum):
        raise ValueError("invalid "+key)
    return float(x)

def rotate(v,axis,deg):
    n=math.sqrt(sum(x*x for x in axis))
    if n<1e-9:raise ValueError("hinge axis must be nonzero")
    k=[x/n for x in axis];t=math.radians(deg);c=math.cos(t);s=math.sin(t)
    cross=(k[1]*v[2]-k[2]*v[1],k[2]*v[0]-k[0]*v[2],k[0]*v[1]-k[1]*v[0])
    dot=sum(k[i]*v[i] for i in range(3))
    return tuple(v[i]*c+cross[i]*s+k[i]*dot*(1-c) for i in range(3))

def attitude(v,pitch,roll):
    x,y,z=v;p=math.radians(pitch);r=math.radians(roll)
    x,z=x*math.cos(p)+z*math.sin(p),-x*math.sin(p)+z*math.cos(p)
    y,z=y*math.cos(r)-z*math.sin(r),y*math.sin(r)+z*math.cos(r)
    return x,y,z

def run(d):
    fields=("ground_z_mm","grass_height_mm","sinkage_mm","minimum_clearance_mm",
            "foil_vertices_local_mm","pivot_mm","hinge_axis","stowed_angle_deg",
            "deployed_angle_deg","sample_step_deg","landing_pitch_deg","landing_roll_deg")
    missing=[k for k in fields if k not in d]
    if missing:return {"version":"v347","accepted":False,"missing_inputs":missing}
    ground=scalar(d,"ground_z_mm")
    grass=scalar(d,"grass_height_mm",0)
    sink=scalar(d,"sinkage_mm",0)
    minimum=scalar(d,"minimum_clearance_mm",0)
    step=scalar(d,"sample_step_deg",0.001)
    if step>30:raise ValueError("sample step too coarse")
    pivot=vec(d["pivot_mm"]);axis=vec(d["hinge_axis"])
    vertices=[vec(p) for p in d["foil_vertices_local_mm"]]
    if len(vertices)<3:raise ValueError("foil needs at least three vertices")
    start=scalar(d,"stowed_angle_deg");end=scalar(d,"deployed_angle_deg")
    if abs(end-start)>360:raise ValueError("travel exceeds full rotation")
    pitch=scalar(d,"landing_pitch_deg");roll=scalar(d,"landing_roll_deg")
    if max(abs(pitch),abs(roll))>45:raise ValueError("attitude outside supported screening")
    count=max(1,math.ceil(abs(end-start)/step))
    if count>7200:raise ValueError("too many samples")
    surface=ground+grass+sink
    rows=[]
    for i in range(count+1):
        angle=start+(end-start)*i/count
        points=[]
        for v in vertices:
            relative=tuple(v[j]-pivot[j] for j in range(3))
            moved=rotate(relative,axis,angle)
            world=tuple(moved[j]+pivot[j] for j in range(3))
            points.append(attitude(world,pitch,roll))
        clearance=min(p[2] for p in points)-surface
        rows.append({"angle_deg":round(angle,5),"minimum_clearance_mm":round(clearance,4)})
    worst=min(rows,key=lambda x:x["minimum_clearance_mm"])
    return {"version":"v347","accepted":False,"stowed_screen_pass":rows[0]["minimum_clearance_mm"]>=minimum,
            "entire_motion_screen_pass":worst["minimum_clearance_mm"]>=minimum,
            "worst_sample":worst,"samples":rows,
            "limitations":["vertices are a supplied envelope, not verified CAD mesh or continuous swept volume",
                           "finite angle sampling can miss collisions between samples",
                           "no collision check with fuselage, skids, actuator, water or linkages",
                           "no servo torque, load, fatigue, print tolerance or real ground test",
                           "deployed foil may intentionally fail land clearance; require interlock and stow for land",
                           "no land/water/air operational acceptance"]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: python scripts/engineering_v347_foil_stow_sweep.py measurements.json")
    source=Path(sys.argv[1])
    result=run(json.loads(source.read_text(encoding="utf-8")))
    dest=source.with_name(source.stem+"_v347_foil_sweep.json")
    dest.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(dest,"stowed:",result.get("stowed_screen_pass"),"accepted:",result["accepted"])
