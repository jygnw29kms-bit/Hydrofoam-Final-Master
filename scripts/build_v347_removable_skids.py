"""v347: printable, replaceable twin skid CAD prototypes (Blender 4.x).

Run in Blender background: blender -b -t 4 --python scripts/build_v347_removable_skids.py
Geometry is standalone and NOT registered to the immutable Final Master.
Units: 1 Blender unit = 1 mm; export uses scale 1.
No holes through the original hull are generated.
"""
import bpy, bmesh, json, hashlib, math
from pathlib import Path
from mathutils import Vector

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'reference/FINAL_MASTER_ORIGINAL.jpeg'
SHA='a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd'
if hashlib.sha256(REF.read_bytes()).hexdigest()!=SHA:
    raise RuntimeError('Final Master checksum mismatch')
# Nominal prototype values, not measurements of the photographed hull.
P={'length_mm':205.0,'width_mm':22.0,'thickness_mm':5.0,
   'end_chamfer_mm':15.0,'end_inset_mm':4.0,
   'mount_hole_diameter_mm':3.4,'mount_hole_spacing_mm':130.0,
   'float_center_y_mm':94.0,'bottom_z_mm':0.0}
assert P['length_mm']>P['mount_hole_spacing_mm']+20
assert P['width_mm']>2*P['end_inset_mm']+P['mount_hole_diameter_mm']
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=0.001
bpy.context.scene.unit_settings.length_unit='MILLIMETERS'
L=P['length_mm']; W=P['width_mm']; T=P['thickness_mm']
C=P['end_chamfer_mm']; I=P['end_inset_mm']
# Plan-view octagon, wide center and tapered ends, extruded as a closed solid.
outline=[(-L/2,-W/2+I),(-L/2+C,-W/2),(L/2-C,-W/2),
         (L/2,-W/2+I),(L/2,W/2-I),(L/2-C,W/2),
         (-L/2+C,W/2),(-L/2,W/2-I)]
verts=[(x,y,z) for z in (0,T) for x,y in outline]
faces=[tuple(range(7,-1,-1)),tuple(range(8,16))]
faces += [(i,(i+1)%8,(i+1)%8+8,i+8) for i in range(8)]
mesh=bpy.data.meshes.new('skid_octagon');mesh.from_pydata(verts,[],faces);mesh.update()
base=bpy.data.objects.new('V347_SKID_BLANK',mesh);bpy.context.collection.objects.link(base)
def activate(o):
    bpy.ops.object.select_all(action='DESELECT');o.select_set(True)
    bpy.context.view_layer.objects.active=o
def bore(obj,x):
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=P['mount_hole_diameter_mm']/2,
                                        depth=T+4,location=(x,0,T/2))
    cutter=bpy.context.object
    activate(obj)
    mod=obj.modifiers.new('THROUGH_BORE','BOOLEAN')
    mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter,do_unlink=True)
for x in (-P['mount_hole_spacing_mm']/2,P['mount_hole_spacing_mm']/2):
    bore(base,x)
# The parts are separate replaceable pads. Attachment to real floats is NOT established.
parts=[]
out=ROOT/'stl/v347';out.mkdir(parents=True,exist_ok=True)
for side,sign in (('LEFT',-1),('RIGHT',1)):
    o=base.copy();o.data=base.data.copy();bpy.context.collection.objects.link(o)
    o.name='V347_'+side+'_REMOVABLE_SKID_WIP'
    o.location=(0,sign*P['float_center_y_mm'],P['bottom_z_mm'])
    activate(o)
    bm=bmesh.new();bm.from_mesh(o.data)
    nonmanifold=sum(not e.is_manifold for e in bm.edges)
    bm.free()
    path=out/(o.name+'.stl')
    bpy.ops.wm.stl_export(filepath=str(path),export_selected_objects=True,
                          apply_modifiers=True,global_scale=1.0)
    parts.append({'object':o.name,'stl':str(path.relative_to(ROOT)),
                  'nonmanifold_edges':nonmanifold,'location_mm':list(o.location)})
bpy.data.objects.remove(base,do_unlink=True)
cad=ROOT/'cad/Hydrofoam_v347_REMOVABLE_SKIDS_WIP.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(cad))
report={'version':'v347','accepted':False,'reference_sha256':SHA,'parameters':P,
        'parts':parts,'cad':str(cad.relative_to(ROOT)),
        'verified_in_script':['nominal left/right geometry','closed mesh topology count','two through bores per skid'],
        'unverified':['master float mating geometry and hole positions','structural screw inserts and load paths',
                      'actual PETG print tolerance','skid wear on grass/sand','foil ground clearance',
                      'land steering and traction','all water and flight performance']}
(ROOT/'docs/V347_REMOVABLE_SKIDS_WIP.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('V347_SKIDS',json.dumps(report))
