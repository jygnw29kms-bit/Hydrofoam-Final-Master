import bpy,os,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v314_LID_GROOVE_WIP.blend'))
by={o.name:o for o in bpy.data.objects if o.type=='MESH'};results=[];tol=0.001
for name,left in by.items():
 if 'Left' not in name:continue
 right=by.get(name.replace('Left','Right'))
 if right is None:continue
 a=[left.matrix_world@v.co for v in left.data.vertices];b=[right.matrix_world@v.co for v in right.data.vertices]
 if len(a)!=len(b):results.append({'pair':name,'result':'FAIL_VERTEX_COUNT'});continue
 # Spatial hash with neighbor cells avoids quantization boundary false negatives.
 from mathutils.kdtree import KDTree
 tree=KDTree(len(b))
 for j,v in enumerate(b):tree.insert(v,j)
 tree.balance();dist=[]
 for v in a:
  q=Vector((v.x,-v.y,v.z));_,_,d=tree.find(q);dist.append(d)
 maximum=max(dist) if dist else 0
 results.append({'pair':name,'vertices':len(a),'maximum_mirror_distance':maximum,'result':'PASS' if maximum<=tol else 'FAIL'})
print('PAIRS',len(results),'PASS',sum(x['result']=='PASS' for x in results),'FAIL',sum(x['result']!='PASS' for x in results),'WORST',max(x.get('maximum_mirror_distance',0) for x in results))
open(os.path.join(R,'docs','V315_FULL_MIRROR_VERTEX_QA.json'),'w').write(json.dumps({'axis':'Y=0','tolerance_model_units':tol,'results':results,'limitations':'only named Left/Right mesh pairs; no aerodynamic, watertight or full-scene symmetry proof'},indent=2))
