"""Hydrofoam v342: reproducible CAD mechanical evidence inventory, NOT a release test.

Run on Jens-PC with Blender 4.5:
blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend -t 4 --python scripts/audit_v342_mechanical_gate.py

Never edits the .blend, README or original reference.
"""
import bpy, hashlib, json, math
from pathlib import Path
from mathutils import Vector

root=Path(__file__).resolve().parents[1]
reference=root/'reference/FINAL_MASTER_ORIGINAL.jpeg'
expected='a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd'
actual=hashlib.sha256(reference.read_bytes()).hexdigest()
if actual!=expected:
    raise RuntimeError('Original Final Master checksum mismatch; audit aborted')

def world_bounds(obj):
    pts=[obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [[round(min(p[i] for p in pts),3) for i in range(3)],
            [round(max(p[i] for p in pts),3) for i in range(3)]]

def overlap(a,b):
    # Axis-aligned overlap is a broad-phase warning, not a collision verdict.
    return [round(max(0,min(a[1][i],b[1][i])-max(a[0][i],b[0][i])),3) for i in range(3)]

objects=[o for o in bpy.data.objects if o.type=='MESH']
roles={'fixed_hinges':[],'moving_hinges':[],'pins':[],'servo_trays':[],'horns':[],'pushrods':[]}
for o in objects:
    name=o.name.upper()
    if 'KNUCKLE' in name:
        roles['moving_hinges' if 'MOVING' in name else 'fixed_hinges'].append(o)
    elif 'ELEVON_PIN' in name: roles['pins'].append(o)
    elif 'SERVO_TRAY' in name: roles['servo_trays'].append(o)
    elif 'ELEVON_HORN' in name: roles['horns'].append(o)
    elif 'PUSHROD' in name: roles['pushrods'].append(o)

parts=[]
for role,group in roles.items():
    for o in group:
        bounds=world_bounds(o)
        parts.append({'name':o.name,'role':role,'bounds_mm':bounds,
                      'dimensions_mm':[round(bounds[1][i]-bounds[0][i],3) for i in range(3)],
                      'visible':not o.hide_render})

# Deliberately reject mere presence as proof of integrated mechanics.
sides={}
for side in ('LEFT','RIGHT'):
    counts={k:sum(side in o.name.upper() for o in v) for k,v in roles.items()}
    present=all(counts[k]>0 for k in ('fixed_hinges','moving_hinges','pins','servo_trays','horns','pushrods'))
    sides[side.lower()]={'counts':counts,'prototype_components_present':present,
        'structural_attachment_verified':False,'servo_hardware_fit_verified':False,
        'linkage_joint_verified':False,'full_motion_sweep_verified':False,
        'print_fit_verified':False,'accepted':False}

# Identify potentially overlapping hardware AABBs for later exact BVH collision checks.
warnings=[]
for i,a in enumerate(parts):
    for b in parts[i+1:]:
        if ('LEFT' in a['name'].upper())!=('LEFT' in b['name'].upper()):continue
        ov=overlap(a['bounds_mm'],b['bounds_mm'])
        if all(x>0 for x in ov):
            warnings.append({'a':a['name'],'b':b['name'],'aabb_overlap_mm':ov,
                             'classification':'BROAD_PHASE_ONLY_NOT_MESH_COLLISION'})
report={'version':'v342','source_blend':bpy.data.filepath,'reference_sha256':actual,
 'units_note':'Bounds labeled mm only if Blender scene uses mm coordinates; verify scene unit scale',
 'scene_unit_scale':bpy.context.scene.unit_settings.scale_length,
 'mesh_count':len(objects),'parts':parts,'sides':sides,
 'potential_aabb_overlaps':warnings,
 'required_evidence':{'master_top_side_perspective_registered':False,
 'rudder_and_all_other_surfaces_audited':False,
 'exact_mesh_collision_sweep':False,'servo_mount_screw_geometry':False,
 'servo_torque_and_pushrod_buckling':False,'mass_and_cg_measured':False,
 'land_tests':False,'water_tests':False,'flight_tests':False},
 'accepted':False,
 'interpretation':'Static object inventory only. AABB overlaps are not proof of mesh intersection; missing overlaps are not proof of clearance during motion. No physical or photographic acceptance.'}
out=root/'docs/V342_MECHANICAL_GATE_WIP.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('V342_GATE',str(out),'parts',len(parts),'accepted',False)
