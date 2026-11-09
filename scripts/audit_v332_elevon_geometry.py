import bpy,os,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v331_HINGE_MOUNT_BRIDGES_WIP.blend'))
results=[]
for side in ('Left','Right'):
 o=bpy.data.objects['24 Elevon '+side];pts=[o.matrix_world@v.co for v in o.data.vertices];bounds={k:[round(min(p[i] for p in pts),3),round(max(p[i] for p in pts),3)] for i,k in enumerate('xyz')};results.append({'side':side,'object':o.name,'vertex_count':len(pts),'world_bounds':bounds,'existing_trim_object':'25 Orange elevon trim '+side,'status':'existing independent control surface geometry; articulation and load path not validated'})
qa={'version':'v332','finding':'The Final Master CAD already contains left/right elevon meshes and orange trim meshes; do not replace with invented rectangular elevators','results':results,'next':['identify true swept hinge line from source mesh','design parametric hinge and servo horns on existing elevon surfaces','evaluate symmetric elevator and differential aileron mixing','check clearance and actual print sectioning']}
open(os.path.join(R,'docs','V332_EXISTING_ELEVONS_GEOMETRY.json'),'w').write(json.dumps(qa,indent=2));print('V332_ELEVONS',json.dumps(results))
