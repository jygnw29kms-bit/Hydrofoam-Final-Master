import bpy,os
r=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(r,'cad','Hydrofoam_Final_Master_v331_HINGE_MOUNT_BRIDGES_WIP.blend'))
for name in ['24 Elevon Left','25 Orange elevon trim Left']:
 o=bpy.data.objects[name];print('VERTICES',name)
 for v in o.data.vertices:print('V',v.index,*(round(t,2) for t in (o.matrix_world@v.co)))
