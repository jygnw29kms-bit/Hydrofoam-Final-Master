"""v348: printable, dimensioned fork clevis prototypes for BOTH elevon pushrods.

Run in Blender 4.x: blender -b --python scripts/build_v348_clevis_forks.py
Standalone geometry only. Servo spline, pivot alignment, interference, print fit
and control throw are NOT verified. Never label this assembly Final.
"""
import bpy, bmesh, json, math
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
col=bpy.data.collections.new('V348_PRINTABLE_CLEVIS_PROTOTYPES_WIP')
bpy.context.scene.collection.children.link(col)
# millimetres: 2.0 mm pushrod, 2.0 mm clevis pin, PETG prototype clearances
P={'fork_width_mm':8.0,'fork_length_mm':14.0,'fork_height_mm':8.0,
   'slot_width_mm':3.2,'slot_depth_mm':9.0,'pin_diameter_mm':2.0,
   'pin_bore_diameter_mm':2.5,'rod_diameter_mm':2.0,
   'rod_bore_diameter_mm':2.4,'min_wall_mm':2.0}
def cube(name,location,scale):
 bpy.ops.mesh.primitive_cube_add(size=1,location=location)
 o=bpy.context.object;o.name=name;o.dimensions=scale
 bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 return o
def cylinder(name,location,radius,depth,axis='Z'):
 bpy.ops.mesh.primitive_cylinder_add(vertices=96,radius=radius,depth=depth,location=location)
 o=bpy.context.object;o.name=name
 if axis=='X':o.rotation_euler[1]=math.pi/2
 if axis=='Y':o.rotation_euler[0]=math.pi/2
 return o
def subtract(part,cutter):
 bpy.context.view_layer.objects.active=part
 m=part.modifiers.new('machined_void','BOOLEAN');m.operation='DIFFERENCE'
 m.solver='EXACT';m.object=cutter
 bpy.ops.object.modifier_apply(modifier=m.name)
 bpy.data.objects.remove(cutter,do_unlink=True)
def move_collection(o):
 for c in list(o.users_collection):c.objects.unlink(o)
 col.objects.link(o)
report=[]
for side,y in [('Left',-12.0),('Right',12.0)]:
 # Fork axis X, open at positive X. Rear barrel receives the axial pushrod.
 w=P['fork_width_mm'];h=P['fork_height_mm'];length=P['fork_length_mm']
 body=cube('V348_'+side+'_CLEVIS_FORK_WIP',(0,y,0),(length,w,h))
 # slot removes material between two fork ears, open at +X
 slot=cube('slot',(length/2-P['slot_depth_mm']/2+0.5,y,0),
           (P['slot_depth_mm']+1,P['slot_width_mm'],h+2))
 subtract(body,slot)
 # transverse pivot pin goes through both ears in Y
 pin_x=length/2-3.2
 cutter=cylinder('pin_clearance',(pin_x,y,0),P['pin_bore_diameter_mm']/2,w+3,'Y')
 subtract(body,cutter)
 # pushrod bore enters from -X and stops before pivot/slot
 rod=cylinder('pushrod_clearance',(-length/2+2.2,y,0),
              P['rod_bore_diameter_mm']/2,4.6,'X')
 subtract(body,rod)
 move_collection(body)
 bm=bmesh.new();bm.from_mesh(body.data)
 nonmanifold=sum(1 for e in bm.edges if not e.is_manifold)
 bm.free()
 # separate print-ready cylindrical gauge pin, not an integrated locking mechanism
 pin=cylinder('V348_'+side+'_PIN_FIT_GAUGE_WIP',(pin_x,y+9,0),
              P['pin_diameter_mm']/2,w+1.0,'Y')
 move_collection(pin)
 report.append({'side':side,'clevis':body.name,'pin_gauge':pin.name,
                'nonmanifold_edges':nonmanifold,'pin_diametral_clearance_mm':
                 P['pin_bore_diameter_mm']-P['pin_diameter_mm'],
                'fork_ear_thickness_mm':(w-P['slot_width_mm'])/2})
out=root/'stl/v348';out.mkdir(parents=True,exist_ok=True)
for obj in col.objects:
 bpy.ops.object.select_all(action='DESELECT')
 obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.wm.stl_export(filepath=str(out/(obj.name+'.stl')),
                        export_selected_objects=True,apply_modifiers=True)
qa={'version':'v348','accepted':False,'geometry':'two mirrored-destination clevis fork prototypes and fit gauge pins',
    'dimensions':P,'parts':report,
    'blocking_checks':['fork not installed at measured servo or horn pivots',
      'rod retention/threading and pivot pin retention not designed',
      'no union to elevon or wing, no collision-free motion sweep',
      'print-fit and strength not physically measured',
      'master image comparison and land/water/air validation incomplete']}
(root/'docs/V348_CLEVIS_FORK_QA_WIP.json').write_text(json.dumps(qa,indent=2)+'\n',encoding='utf-8')
bpy.ops.wm.save_as_mainfile(filepath=str(root/'cad/Hydrofoam_v348_CLEVIS_FORK_PROTOTYPES_WIP.blend'))
print(json.dumps(qa,indent=2))
