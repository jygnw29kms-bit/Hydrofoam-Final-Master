import bpy, os
root=r"C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master"
bpy.ops.wm.open_mainfile(filepath=os.path.join(root,'cad','Hydrofoam_Final_Master_v91_IDENTITY.blend'))
o=bpy.data.objects.get('Canopy')
if o:
    o.scale.z*=0.88; o.location.z-=1.5; o.scale.x*=1.03
for n in ['FinL','FinR']:
    o=bpy.data.objects.get(n)
    if o:
        o.scale.z*=0.75; o.scale.x*=0.92; o.location.x+=6; o.location.z-=2
for n in ['FinAccentL','FinAccentR','FinOrangeL','FinOrangeR']:
    o=bpy.data.objects.get(n)
    if o:
        o.scale.z*=0.75; o.scale.x*=0.92; o.location.x+=6; o.location.z-=2
for n in ['Cube','Cube.001','Cube.002','Cube.003','Cylinder','Cylinder.001','Cylinder.002','Cylinder.003','Torus']:
    o=bpy.data.objects.get(n)
    if o: o.location.z-=3.0; o.location.x+=1.0
for n in ['PontoonCrestL','PontoonCrestR']:
    o=bpy.data.objects.get(n)
    if o: o.scale.z*=0.90; o.location.z-=0.6
out=os.path.join(root,'cad','Hydrofoam_Final_Master_v94_IDENTITY_REFINE.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(root,'cad','Hydrofoam_Final_Master_v94_IDENTITY_REFINE.stl'),export_selected_objects=False)
print('V94_SAVED')
