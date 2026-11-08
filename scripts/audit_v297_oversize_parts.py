import bpy,os
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend'))
for o in bpy.data.objects:
 if o.type!='MESH':continue
 points=[o.matrix_world@v.co for v in o.data.vertices]
 if not points:continue
 dims=[max(p[i] for p in points)-min(p[i] for p in points) for i in range(3)]
 if max(dims)>256:print('NEEDS_CUT',o.name,*[round(z,1) for z in dims])
