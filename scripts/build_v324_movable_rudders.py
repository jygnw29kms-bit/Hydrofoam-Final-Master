import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v323_TWIN_RUDDER_LAYOUT_WIP.blend'))
coll=bpy.data.collections.new('V324_MOVABLE_TWIN_RUDDERS_WIP');bpy.context.scene.collection.children.link(coll)
def cube(name,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
def bb(o):
 v=[o.matrix_world@Vector(c) for c in o.bound_box];return [[min(p[i] for p in v),max(p[i] for p in v)] for i in range(3)]
results=[]
for side in ['Left','Right']:
 fin=bpy.data.objects['30 Tail fin '+side];bounds=bb(fin);y=sum(bounds[1])/2;zmin,zmax=bounds[2];xmin,xmax=bounds[0];hinge_x=xmax-19
 # First discrete movable surface: approx rear 18 mm chord, inset from fin top/bottom.
 surface=cube('V324_'+side+'_MOVABLE_RUDDER_WIP',(xmax-9,y,(zmin+zmax)/2),(18,3.2,(zmax-zmin)-16))
 # Hinge axis cylinder, explicitly modeled independently of surface.
 bpy.ops.mesh.primitive_cylinder_add(vertices=24,radius=1.1,depth=(zmax-zmin)-14,location=(hinge_x,y,(zmin+zmax)/2));axis=bpy.context.object;axis.name='V324_'+side+'_HINGE_PIN_REFERENCE'
 for c in list(axis.users_collection):c.objects.unlink(axis)
 coll.objects.link(axis)
 # Represent sweep with duplicate ghost position around pivot (rotation around world Z).
 ghost=surface.copy();ghost.data=surface.data.copy();coll.objects.link(ghost);ghost.name='V324_'+side+'_RUDDER_25DEG_ENVELOPE_REFERENCE';ghost.hide_render=True
 results.append({'side':side,'fin_bounds':[[round(v,2) for v in a] for a in bounds],'rudder_dimensions':[round(v,2) for v in surface.dimensions],'hinge_x':round(hinge_x,2),'note':'separate overlapping reference geometry; fixed fin has NOT been physically cut'})
report={'version':'v324','section':'01','change':'added two discrete rudder surface meshes and independent hinge pin references','rudders':results,'status':'WIP','blocking':['fixed fins still overlap rudder geometry and must be Boolean split','hinge pivot locations not validated against actual airfoil','surface travel and collision envelope not physically animated','servo horns/rods not attached to surfaces','water protection and flight loads unknown'],'accepted':False}
open(os.path.join(R,'docs','V324_MOVABLE_RUDDER_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v324'),exist_ok=True)
bpy.context.scene.render.filepath=os.path.join(R,'renders','v324','movable_rudder_surfaces_iso.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v324_MOVABLE_RUDDERS_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V324_MOVABLE_SURFACES',json.dumps(results))
