"""v342: non-destructive mass-property and ground-clearance inventory.

Execute on Jens-PC with the current Blender assembly loaded:
blender -b cad/Hydrofoam_Final_Master_v339_ELEVON_LINKAGE_REFERENCES_WIP.blend --python scripts/audit_v342_mass_clearance.py

This is geometry evidence only. Never equate mesh volume with flight mass,
or a model bounding box with tested ground clearance.
"""
import bpy, json, hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree

root=Path(__file__).resolve().parents[1]
master=root/'reference/FINAL_MASTER_ORIGINAL.jpeg'
expected='a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd'
actual=hashlib.sha256(master.read_bytes()).hexdigest()
if actual!=expected:
    raise RuntimeError('Final-Master reference SHA256 mismatch')

depsgraph=bpy.context.evaluated_depsgraph_get()
items=[]
for obj in bpy.data.objects:
    if obj.type!='MESH' or obj.hide_render:
        continue
    evaluated=obj.evaluated_get(depsgraph)
    mesh=evaluated.to_mesh()
    try:
        coords=[obj.matrix_world @ v.co for v in mesh.vertices]
        if not coords:
            continue
        minimum=[round(min(v[i] for v in coords),3) for i in range(3)]
        maximum=[round(max(v[i] for v in coords),3) for i in range(3)]
        # Volume is recorded only for closed manifold meshes.
        edges={}
        for poly in mesh.polygons:
            for key in poly.edge_keys:
                k=tuple(sorted(key))
                edges[k]=edges.get(k,0)+1
        manifold=bool(edges) and all(n==2 for n in edges.values())
        items.append({'object':obj.name,'vertices':len(coords),
                      'bounds_mm':{'min':minimum,'max':maximum},
                      'closed_edge_manifold':manifold,
                      'volume_mm3':round(abs(mesh.calc_volume()),3) if manifold else None})
    finally:
        evaluated.to_mesh_clear()

# Conservative, explicitly unverified labels for engineering follow-up.
groups={'foils':[],'skids':[],'floats':[],'propulsion':[],'controls':[]}
for item in items:
    n=item['object'].lower()
    for group,terms in {
        'foils':('foil','strut','mast'),
        'skids':('skid','kufe','runner'),
        'floats':('float','pontoon','schwimmer'),
        'propulsion':('motor','prop','pusher'),
        'controls':('elevon','rudder','servo','horn','pushrod','hinge','knuckle')
    }.items():
        if any(t in n for t in terms):
            groups[group].append(item['object'])

report={
    'version':'v342','accepted':False,'master_sha256':actual,
    'source_blend':bpy.data.filepath,'unit_assumption':'Blender coordinates interpreted as mm; verify scene scale',
    'geometry':items,'candidate_groups_by_name':groups,
    'ground_clearance_mm':None,'all_up_mass_g':None,'center_of_gravity_mm':None,
    'foil_stowed_state_verified':False,'propeller_ground_clearance_verified':False,
    'modes':{'land':'NOT TESTED','water':'NOT TESTED','air':'NOT TESTED'},
    'blocking':[
      'Define a measured ground plane and real contact points for each surface',
      'Verify foil deployment and protected/stowed state before clearance calculation',
      'Record material, infill, hardware and electronics mass per component',
      'Calculate weighted center of gravity from measured component masses',
      'Verify propeller disk envelope and all moving-control collision sweeps',
      'Complete original image registration in top, side and perspective',
      'Perform separate land, water and air acceptance tests'
    ]
}
out=root/'docs/V342_MASS_CLEARANCE_INVENTORY_WIP.json'
out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('V342_GEOMETRY_INVENTORY',len(items),'objects; acceptance=false')
