import bpy,os,json,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v324_MOVABLE_RUDDERS_WIP.blend'))
report=[]
for side in ['Left','Right']:
 fin=bpy.data.objects['30 Tail fin '+side];rud=bpy.data.objects['V324_'+side+'_MOVABLE_RUDDER_WIP']
 # Exact finite cutter: 0.6 mm clearance in X/Z and full fin thickness in Y.
 bpy.ops.mesh.primitive_cube_add(size=1,location=rud.location);c=bpy.context.object;c.name='TEMP_FIN_RUDDER_CLEARANCE_'+side;c.dimensions=(rud.dimensions.x+1.2,8,rud.dimensions.z+1.2)
 bpy.context.view_layer.objects.active=c;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
 before=len(fin.data.polygons)
 mod=fin.modifiers.new('V325_RUDDER_CLEARANCE','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=c
 bpy.context.view_layer.objects.active=fin;bpy.ops.object.modifier_apply(modifier=mod.name)
 bpy.data.objects.remove(c,do_unlink=True)
 bm=bmesh.new();bm.from_mesh(fin.data);bad=sum(not e.is_manifold for e in bm.edges);bm.free()
 report.append({'side':side,'fixed_fin_faces_before':before,'fixed_fin_faces_after':len(fin.data.polygons),'fixed_fin_nonmanifold_edges':bad,'rudder_clearance_nominal_mm':0.6,'clearance_method':'boolean cube around rectangular prototype surface','limitations':'rudder still rectangular and may not match tapered fin contour'})
assert all(x['fixed_fin_faces_after']!=x['fixed_fin_faces_before'] for x in report),'Boolean had no geometric effect'
qa={'version':'v325','section':'01','operation':'cut physical rudder clearance pockets from both fixed fin meshes','results':report,'accepted':False,'open':['validate real hinge geometry and hinge pin locations','measure actual clearance over +/-25 degree sweep','build shaped control surfaces matching fin taper','rod horn and servo mount integration','structural and printability checks']}
open(os.path.join(R,'docs','V325_SPLIT_TWIN_FINS_QA.json'),'w').write(json.dumps(qa,indent=2))
os.makedirs(os.path.join(R,'renders','v325'),exist_ok=True);bpy.context.scene.render.filepath=os.path.join(R,'renders','v325','twin_fin_clearance_cut_iso.png')
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v325_SPLIT_TWIN_FINS_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V325_CUTS',json.dumps(report))
