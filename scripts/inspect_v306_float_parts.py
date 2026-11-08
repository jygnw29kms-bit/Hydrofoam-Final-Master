import bpy,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v305_P2S_ASSEMBLY.blend'))
for o in bpy.data.objects:
 if o.type=='MESH' and ('float' in o.name.lower() or 'stripe' in o.name.lower() or 'skid' in o.name.lower()):
  print('OBJ',o.name,'verts',len(o.data.vertices),'pos',tuple(round(x,2) for x in o.location))
