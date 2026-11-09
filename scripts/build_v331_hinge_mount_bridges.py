import bpy,os,json,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v330_SYMMETRIC_FIN_CUT_WIP.blend'))
coll=bpy.data.collections.new('V331_HINGE_MOUNT_BRIDGES_WIP');bpy.context.scene.collection.children.link(coll)
def cube(name,loc,dim):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=dim;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 for c in list(o.users_collection):c.objects.unlink(o)
 coll.objects.link(o);return o
def merge(target,source):
 m=target.modifiers.new('V331_STRUCTURAL_BRIDGE_UNION','BOOLEAN');m.operation='UNION';m.solver='EXACT';m.object=source
 bpy.context.view_layer.objects.active=target;bpy.ops.object.modifier_apply(modifier=m.name);bpy.data.objects.remove(source,do_unlink=True)
def bad(o):
 bm=bmesh.new();bm.from_mesh(o.data);n=sum(not e.is_manifold for e in bm.edges);bm.free();return n
results=[]
for side,y in [('Left',-182.5),('Right',182.5)]:
 for idx,z in enumerate([45,56,67,78,89]):
  kind='FIXED_FIN' if idx%2==0 else 'MOVING_RUDDER';sleeve=bpy.data.objects['V328_'+side+'_'+kind+'_HINGE_SLEEVE_'+str(idx)]
  # Web intersects sleeve outer diameter while avoiding its 2.4-unit pin hole.
  # Fixed side extends forward; movable side extends aft to overlap surface near x=202.
  if kind=='FIXED_FIN':loc=(197.8,y,z);dim=(7.2,3.0,6.5)
  else:loc=(204.2,y,z);dim=(7.2,3.0,6.5)
  bridge=cube('TEMP_BRIDGE_'+side+'_'+str(idx),loc,dim);merge(sleeve,bridge)
  results.append({'side':side,'index':idx,'kind':kind,'sleeve_with_bridge_nonmanifold':bad(sleeve),'note':'bridge attached to sleeve only; body union pending'})
qa={'version':'v331','operation':'build and Boolean-union ten radial hinge-to-body bridge tabs into hinge sleeves','results':results,'accepted':False,'blocking':['bridge tabs not yet Boolean-unioned into fin/rudder parent bodies','validate tabs do not block moving surfaces','verify sleeve bore stays open and fits pin','load and print-orientation testing']}
open(os.path.join(R,'docs','V331_HINGE_MOUNT_BRIDGES_QA.json'),'w').write(json.dumps(qa,indent=2))
os.makedirs(os.path.join(R,'renders','v331'),exist_ok=True);bpy.context.scene.render.filepath=os.path.join(R,'renders','v331','hinge_mount_bridges_iso.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v331_HINGE_MOUNT_BRIDGES_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V331_BRIDGES',json.dumps({'count':len(results),'nonmanifold':sum(x['sleeve_with_bridge_nonmanifold'] for x in results)}))
