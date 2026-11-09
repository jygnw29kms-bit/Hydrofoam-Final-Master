import bpy,os,json,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v327_FIN_REPAIR_WIP.blend'))
coll=bpy.data.collections.new('V328_TWIN_RUDDER_HINGE_KNUCKLES_WIP');bpy.context.scene.collection.children.link(coll)
def cylinder(name,loc,radius,depth):
 bpy.ops.mesh.primitive_cylinder_add(vertices=32,radius=radius,depth=depth,location=loc);o=bpy.context.object;o.name=name
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
out=[]
for side,y in [('Left',-182.5),('Right',182.5)]:
 # v324 rudder x center 211, z 71; v325 fixed fin split at x~201.4.
 # Hinge-pin references on the split edge; alternate 3 fixed and 2 movable knuckles.
 hx=201.0;zlist=[45,56,67,78,89];parts=[]
 for idx,z in enumerate(zlist):
  label='FIXED_FIN' if idx%2==0 else 'MOVING_RUDDER'
  sleeve=cylinder('V328_'+side+'_'+label+'_HINGE_SLEEVE_'+str(idx),(hx,y,z),2.7,7.5)
  bore=cylinder('TEMP_PIN_BORE',(hx,y,z),1.2,9.0)
  m=sleeve.modifiers.new('PIN_CLEARANCE_2P4','BOOLEAN');m.operation='DIFFERENCE';m.solver='EXACT';m.object=bore
  bpy.context.view_layer.objects.active=sleeve;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(bore,do_unlink=True)
  bm=bmesh.new();bm.from_mesh(sleeve.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
  parts.append({'z':z,'mount_side':label,'nonmanifold_edges':bad})
 cylinder('V328_'+side+'_HINGE_PIN_REFERENCE',(hx,y,67),1.05,55)
 out.append({'side':side,'hinge_x':hx,'hinge_y':y,'knuckles':parts,'note':'Sleeves and pins are standalone geometries, not fused to fin/rudder surfaces'})
qa={'version':'v328','section':'01','change':'five alternating annular hinge sleeves and pin reference per rudder','results':out,'accepted':False,'open':['connect sleeves structurally to their assigned fin/rudder bodies','check hinge axis alignment and moving clearances','measure true 3D servo rod movement and collision','pin material, axial retention and tolerances need definition']}
open(os.path.join(R,'docs','V328_RUDDER_HINGE_QA.json'),'w').write(json.dumps(qa,indent=2))
os.makedirs(os.path.join(R,'renders','v328'),exist_ok=True);bpy.context.scene.render.filepath=os.path.join(R,'renders','v328','twin_rudder_hinge_knuckles_iso.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v328_RUDDER_HINGES_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V328_HINGES',json.dumps(out))
