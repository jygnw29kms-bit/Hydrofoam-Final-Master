import bpy,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v302_LIGHTWEIGHT_HULLS.blend'))
folder=os.path.join(R,'print','v302_shell_prototypes')
os.makedirs(folder,exist_ok=True)
for name,slug in [
 ('01 Master Central fuselage','central_hull_shell'),
 ('10 Planing float Left','left_float_shell'),
 ('10 Planing float Right','right_float_shell'),
 ('02 Black canopy','removable_smoked_canopy')]:
 obj=bpy.data.objects[name]
 bpy.ops.object.select_all(action='DESELECT')
 obj.select_set(True);bpy.context.view_layer.objects.active=obj
 bpy.ops.wm.stl_export(filepath=os.path.join(folder,slug+'.stl'),export_selected_objects=True)
 print('EXPORTED',slug,len(obj.data.polygons))
print('V302_SHELL_STL_EXPORT_DONE')
