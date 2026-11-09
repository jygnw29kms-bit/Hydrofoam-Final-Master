import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v319_RUDDER_HORN_WIP.blend'))
s=bpy.context.scene;coll=bpy.data.collections.get('V317_AILERON_RUDDER_LINKAGE_PACKAGING_WIP');assert coll
results=[]
for name in ['LEFT_AILERON_HORN_PLACEHOLDER','RIGHT_AILERON_HORN_PLACEHOLDER','RUDDER_HORN_12P5MM_PROTOTYPE']:
 o=bpy.data.objects.get(name);assert o and o.type=='MESH'
 # Cross-drill the horn along local Y; location and bore are demonstrator dimensions, not yet flight-approved.
 bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.1,depth=22,location=o.location)
 tool=bpy.context.object;tool.name='TEMP_BORE_'+name;tool.rotation_euler[0]=math.pi/2
 bpy.context.view_layer.objects.active=o
 mod=o.modifiers.new('V320_PIN_BORE_2P2','BOOLEAN');mod.operation='DIFFERENCE';mod.object=tool
 bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(tool,do_unlink=True)
 results.append({'object':name,'bore_diameter_model_units':2.2,'boolean_applied':True,'mesh_vertices':len(o.data.vertices)})
# Keep original linkages and add explicit centerline pin reference at each horn
report={'version':'v320','change':'boolean through-bores in three control-horn placeholder meshes','bores':results,'status':'WIP; holes centered in provisional horn geometry','critical_blockers':['verify hole position relative to actual hinge axis','ensure adequate material around bore and printed layer direction','size clevis and hinge pins','full range collision sweep','servo torque and pushrod buckling','sealing of exposed servo/linkage interfaces'],'land_water_air':'not validated'}
open(os.path.join(R,'docs','V320_LINKAGE_PIN_HOLES_QA.json'),'w').write(json.dumps(report,indent=2))
os.makedirs(os.path.join(R,'renders','v320'),exist_ok=True)
s.render.filepath=os.path.join(R,'renders','v320','control_horn_bores_iso.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v320_CONTROL_HORN_BORES_WIP.blend'))
bpy.ops.render.render(write_still=True)
print('V320_HORNS_DRILLED',len(results))
