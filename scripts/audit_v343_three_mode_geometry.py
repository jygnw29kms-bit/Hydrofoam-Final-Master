"""Hydrofoam v343: three-mode engineering readiness audit, evidence-only.

Run on Jens-PC in Blender 4.5:
blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend -t 4 --python scripts/audit_v343_three_mode_geometry.py

No CAD or original-reference changes. Geometric checks are screening only.
"""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
ref=root/'reference/FINAL_MASTER_ORIGINAL.jpeg'
expected='a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd'
actual=hashlib.sha256(ref.read_bytes()).hexdigest()
if actual!=expected: raise RuntimeError('Final Master SHA256 mismatch')
objects=[o for o in bpy.data.objects if o.type=='MESH']
def bounds(o):
    p=[o.matrix_world@Vector(c) for c in o.bound_box]
    return [[min(v[i] for v in p) for i in range(3)],[max(v[i] for v in p) for i in range(3)]]
def record(o):
    b=bounds(o)
    return {'name':o.name,'bounds_scene_units':[[round(v,4) for v in row] for row in b],
            'dimensions_scene_units':[round(b[1][i]-b[0][i],4) for i in range(3)]}
def select(*tokens):
    return [o for o in objects if any(t in o.name.lower() for t in tokens)]
foil=select('foil','strut','mast')
skid=select('skid','kufe','runner')
floaters=select('float','pontoon','schwimmer')
pusher=select('prop','motor','pusher')
surfaces=select('elevon','rudder','aileron','elevator')
# No ground-plane or waterline assumption. These are candidate names, not validated parts.
report={
 'version':'v343','reference_sha256':actual,'source_blend':bpy.data.filepath,
 'scene_units':{'system':bpy.context.scene.unit_settings.system,
                'scale_length':bpy.context.scene.unit_settings.scale_length},
 'mesh_count':len(objects),
 'candidate_components':{'foils_and_masts':[record(o) for o in foil],
  'skids':[record(o) for o in skid],'floats':[record(o) for o in floaters],
  'propulsion':[record(o) for o in pusher],
  'control_surfaces':[record(o) for o in surfaces]},
 'land':{'ground_reference_defined':False,'foil_ground_clearance_measured':False,
  'skid_contact_pressure_measured':False,'grass_and_sand_start_verified':False,
  'low_speed_steering_verified':False,'skid_wear_verified':False,'accepted':False},
 'water':{'displacement_vs_mass_verified':False,'sealed_enclosure_tested':False,
  'foil_lift_and_stability_verified':False,'waterline_defined':False,
  'planing_and_foil_transition_tested':False,'accepted':False},
 'air':{'actual_mass_measured':False,'cg_and_static_margin_verified':False,
  'wing_area_and_aero_polars_verified':False,'measured_thrust_available':False,
  'prop_ground_clearance_verified':False,'all_axes_control_authority_verified':False,
  'accepted':False},
 'mechanics':{'full_swept_mesh_collision_test':False,'all_servo_mounts_structurally_integrated':False,
  'all_linkage_joints_verified':False,'rudder_and_elevon_throw_verified':False,'accepted':False},
 'master_fidelity':{'top_view_registered':False,'side_view_registered':False,
  'perspective_registered':False,'accepted':False},
 'accepted':False,
 'notes':['Candidate classification uses object names only; absence is not proof of missing geometry.',
          'Scene units are recorded without assuming millimeters.',
          'No fabricated ground plane, waterline, masses, lift, thrust, or operating test results.',
          'This report does not authorize printing, operation, or flight.']}
out=root/'docs/V343_THREE_MODE_GEOMETRY_READINESS_WIP.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('V343_AUDIT',out,'objects',len(objects),'accepted',False)
