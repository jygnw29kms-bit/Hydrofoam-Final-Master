import bpy,os,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v314_LID_GROOVE_WIP.blend'))
a=bpy.data.objects['11 Orange float leading stripe Left'];b=bpy.data.objects['11 Orange float leading stripe Right']
left=[a.matrix_world@v.co for v in a.data.vertices];right=[b.matrix_world@v.co for v in b.data.vertices]
# for each mirrored vertex nearest right vertex, exact float comparison; collect worst
errors=[]
for i,v in enumerate(left):
 mirror=Vector((v.x,-v.y,v.z));d,j=min(((mirror-w).length,j) for j,w in enumerate(right));errors.append((d,i,j))
errors.sort(reverse=True);print('MAX_DISTANCE',errors[0]);print('TOP10',errors[:10]);print('VERTEX',list(left[errors[0][1]]),list(right[errors[0][2]]))
open(os.path.join(R,'docs','V315_STRIPE_MIRROR_DIAGNOSIS.json'),'w').write(json.dumps({'max_distance_model_units':errors[0][0],'worst_vertex_index_left':errors[0][1],'nearest_vertex_index_right':errors[0][2],'top_10_distances':[e[0] for e in errors[:10]]},indent=2))
