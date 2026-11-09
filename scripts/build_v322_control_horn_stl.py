import bpy,os,json,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v320_CONTROL_HORN_BORES_WIP.blend'))
names=['LEFT_AILERON_HORN_PLACEHOLDER','RIGHT_AILERON_HORN_PLACEHOLDER','RUDDER_HORN_12P5MM_PROTOTYPE'];folder=os.path.join(R,'stl','v322_control_horns_WIP');os.makedirs(folder,exist_ok=True)
results=[]
for name in names:
 o=bpy.data.objects[name];bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 # Export via native Blender STL; use_mesh_modifiers ensures actual boolean result is exported.
 p=os.path.join(folder,name+'.stl')
 bpy.ops.wm.stl_export(filepath=p,export_selected_objects=True,apply_modifiers=True)
 bm=bmesh.new();bm.from_mesh(o.data);nonmanifold=sum(not e.is_manifold for e in bm.edges);bm.free()
 results.append({'name':name,'file':os.path.relpath(p,R).replace('\\','/'),'size_bytes':os.path.getsize(p),'nonmanifold_edges':nonmanifold,'dimensions_model_units':[round(float(v),3) for v in o.dimensions]})
report={'version':'v322','section':'01 Ruderanlenkungen','result':'Three STL prototypes exported; NOT PRINT-READY','files':results,'limitations':['STL unit scale not independently calibrated','2.2 bore dimensions not independently measured','no print orientation, strength, tolerances or physical fit','servo travel and collision still untested'],'acceptance':False}
open(os.path.join(R,'docs','V322_CONTROL_HORN_STL_QA.json'),'w').write(json.dumps(report,indent=2));print('V322_EXPORT',json.dumps(results))
