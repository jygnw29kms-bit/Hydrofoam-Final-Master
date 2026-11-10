"""v346 measured pushrod buckling and servo torque gate; engineering screening, never release approval.

Run: python scripts/engineering_v346_linkage_loads.py measurements.json
All lengths mm, force N, torque N*mm, Young's modulus N/mm^2.
The load case must include measured hinge moment, arm lengths, rod geometry, end fixity,
material modulus, and a stated load factor. This cannot validate geometry or motion.
"""
import json, math, sys
from pathlib import Path

FIELDS = ("side", "measured_peak_hinge_moment_Nmm", "horn_effective_arm_mm",
          "servo_effective_arm_mm", "measured_servo_torque_Nmm",
          "rod_unsupported_length_mm", "rod_diameter_mm",
          "rod_young_modulus_N_per_mm2", "end_fixity_factor",
          "design_load_factor", "servo_efficiency", "measured_joint_slop_mm")
def positive(d,k):
    v=d[k]
    if type(v) not in (float,int) or not math.isfinite(v) or v<=0:
        raise ValueError(k+" must be a finite positive measured number")
    return float(v)
def run(d):
    missing=[k for k in FIELDS if k not in d]
    if missing:return {"accepted":False,"missing_inputs":missing}
    if d["side"] not in ("left","right"):raise ValueError("side must be left/right")
    x={k:positive(d,k) for k in FIELDS if k!="side" and k!="measured_joint_slop_mm"}
    slop=d["measured_joint_slop_mm"]
    if type(slop) not in (float,int) or not math.isfinite(slop) or slop<0:
        raise ValueError("measured_joint_slop_mm must be nonnegative")
    if x["servo_efficiency"]>1:raise ValueError("servo_efficiency cannot exceed 1")
    moment=x["measured_peak_hinge_moment_Nmm"]*x["design_load_factor"]
    axial=moment/x["horn_effective_arm_mm"]
    required_servo= axial*x["servo_effective_arm_mm"]/x["servo_efficiency"]
    I=math.pi*x["rod_diameter_mm"]**4/64
    critical=math.pi**2*x["rod_young_modulus_N_per_mm2"]*I/(x["end_fixity_factor"]*x["rod_unsupported_length_mm"])**2
    servo_margin=x["measured_servo_torque_Nmm"]/required_servo
    buckling_margin=critical/axial
    return {"side":d["side"],"accepted":False,"screening_pass":servo_margin>=1 and buckling_margin>=1,
            "design_hinge_moment_Nmm":round(moment,4),
            "rod_axial_force_N":round(axial,4),
            "required_servo_torque_Nmm":round(required_servo,4),
            "euler_critical_compression_N":round(critical,4),
            "servo_margin":round(servo_margin,4),
            "buckling_margin":round(buckling_margin,4),
            "joint_slop_mm":float(slop),
            "limitations":["Euler buckling applies to straight ideal elastic rod, not threaded ends or clevises",
             "tension capacity, cyclic fatigue, fastener shear, hinge friction and impact not assessed",
             "horn moment arm varies with deflection; worst-case sweep must be measured separately",
             "servo torque must be measured at actual voltage, speed and duty cycle",
             "servo thermal endurance, joint retention, collision-free travel and flight loads unverified",
             "both sides, all control surfaces, land-water-air tests and master visual match required"]}
if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("Usage: python scripts/engineering_v346_linkage_loads.py measured.json")
    src=Path(sys.argv[1]);data=json.loads(src.read_text(encoding="utf-8"))
    result=run(data)
    out=src.with_name(src.stem+"_v346_linkage_loads.json")
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(out,"screening_pass",result.get("screening_pass"),"accepted",False)
