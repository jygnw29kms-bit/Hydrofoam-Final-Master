"""v345: measured land-contact and foil-clearance envelope. No acceptance from CAD alone.

Input JSON:
{
 "datum": "description of local coordinate system; z up; mm",
 "surface": "hard|short_grass|firm_sand",
 "ground_contact_points_mm": [[x,y,z], ...],
 "protected_points_mm": {"foil_tip_left":[x,y,z],"foil_tip_right":[x,y,z],"prop_tip_low":[x,y,z]},
 "pitch_deg": [-4,0,4], "roll_deg": [-5,0,5],
 "required_clearance_mm": {"foil_tip_left":5,"foil_tip_right":5,"prop_tip_low":25},
 "measured_ground_compliance_mm": 0
}
Contact points must describe the REAL load-bearing skid configuration, not a bounding box.
"""
import json, math, sys
from pathlib import Path

def vec(p):
 if not isinstance(p,list) or len(p)!=3 or any(type(v) not in (int,float) or not math.isfinite(v) for v in p):
  raise ValueError("coordinates must be finite [x,y,z] lists")
 return tuple(float(v) for v in p)

def rotate(p,pitch,roll):
 x,y,z=p
 a,b=math.radians(pitch),math.radians(roll)
 # rotate around Y (pitch) then X (roll), in local coordinates
 x,z=x*math.cos(a)+z*math.sin(a),-x*math.sin(a)+z*math.cos(a)
 y,z=y*math.cos(b)-z*math.sin(b),y*math.sin(b)+z*math.cos(b)
 return x,y,z

def run(d):
 required=("datum","surface","ground_contact_points_mm","protected_points_mm",
           "pitch_deg","roll_deg","required_clearance_mm","measured_ground_compliance_mm")
 missing=[k for k in required if k not in d]
 if missing:return {"accepted":False,"missing_inputs":missing}
 if d["surface"] not in ("hard","short_grass","firm_sand"):raise ValueError("unknown surface")
 if not isinstance(d["datum"],str) or not d["datum"].strip():raise ValueError("datum description required")
 contacts=[vec(p) for p in d["ground_contact_points_mm"]]
 if len(contacts)<3:raise ValueError("at least three measured contact points required")
 if not isinstance(d["protected_points_mm"],dict) or not d["protected_points_mm"]:
  raise ValueError("protected points required")
 points={k:vec(v) for k,v in d["protected_points_mm"].items()}
 if set(points)!=set(d["required_clearance_mm"]):
  raise ValueError("every protected point needs a clearance limit")
 pitch=d["pitch_deg"];roll=d["roll_deg"]
 if not isinstance(pitch,list) or not pitch or not isinstance(roll,list) or not roll:
  raise ValueError("nonempty sampled attitude grids required")
 compliance=d["measured_ground_compliance_mm"]
 if type(compliance) not in (int,float) or not math.isfinite(compliance) or compliance<0:
  raise ValueError("measured ground compliance must be nonnegative")
 limits=d["required_clearance_mm"]
 for k,v in limits.items():
  if type(v) not in (int,float) or not math.isfinite(v) or v<0:raise ValueError("invalid clearance")
 rows=[]
 for a in pitch:
  for b in roll:
   if type(a) not in (int,float) or type(b) not in (int,float) or not math.isfinite(a) or not math.isfinite(b):
    raise ValueError("invalid attitude")
   ground_z=min(rotate(p,a,b)[2] for p in contacts)
   gaps={k:round(rotate(p,a,b)[2]-ground_z-float(compliance),3) for k,p in points.items()}
   rows.append({"pitch_deg":a,"roll_deg":b,"gaps_mm":gaps,
                "meets_geometric_limits":all(gaps[k]>=limits[k] for k in gaps)})
 worst={k:min(row["gaps_mm"][k] for row in rows) for k in points}
 return {"accepted":False,"geometry_screening_pass":all(r["meets_geometric_limits"] for r in rows),
         "surface":d["surface"],"datum":d["datum"],"samples":rows,"worst_gap_mm":worst,
         "required_clearance_mm":limits,
         "limitations":["rotations about local datum only; no suspension or elastic deformation model",
          "ground modeled as plane through lowest measured contact point",
          "no unsampled attitudes, impact loads, grass snagging or sand rut depth verified",
          "measured ground compliance is an input, not inferred",
          "no propulsion, steering, waterproofing, hydrofoil or flight validation"]}
if __name__=="__main__":
 if len(sys.argv)!=2:raise SystemExit("Usage: python scripts/engineering_v345_land_clearance_envelope.py measured_geometry.json")
 src=Path(sys.argv[1]);out=run(json.loads(src.read_text(encoding="utf-8")))
 dest=src.with_name(src.stem+"_v345_clearance.json")
 dest.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
 print(dest,"geometry_screening_pass:",out.get("geometry_screening_pass"),"accepted:",out["accepted"])
