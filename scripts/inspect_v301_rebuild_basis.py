import bpy,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v298_CORRECTED_WING_NORMALS.blend'))
for o in sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda ob:ob.name):
 if 'Central' in o.name or 'canopy' in o.name.lower() or 'wing' in o.name.lower() or 'arch' in o.name.lower():
  verts=[o.matrix_world@v.co for v in o.data.vertices]
  if verts:print('CAD_OBJECT',o.name,'bounds',tuple(tuple(round(x,1) for x in row) for row in zip(*[(min(v[i] for v in verts),max(v[i] for v in verts)) for i in range(3)])))
print('MESH_COUNT',len([o for o in bpy.data.objects if o.type=='MESH']))
