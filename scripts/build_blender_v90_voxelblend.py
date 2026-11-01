import bpy, os
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad')
bpy.ops.wm.open_mainfile(filepath=os.path.join(CAD,'Hydrofoam_Final_Master_v70_EXACT_PLANFORM.blend'))
# join core white shell only
names=['MasterPlanform','CenterHull','SponsonL','SponsonR']
objs=[bpy.data.objects.get(n) for n in names if bpy.data.objects.get(n)]
bpy.ops.object.select_all(action='DESELECT')
for o in objs:o.select_set(True)
bpy.context.view_layer.objects.active=objs[0]
bpy.ops.object.join(); body=bpy.context.object; body.name='MasterBodyBlend'
# apply modifiers first
for m in list(body.modifiers):
 try:bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=m.name)
 except:pass
# voxel remesh for organic continuous surface
body.data.remesh_voxel_size=1.25
body.data.remesh_voxel_adaptivity=0.0
bpy.context.view_layer.objects.active=body
bpy.ops.object.voxel_remesh()
for p in body.data.polygons:p.use_smooth=True
# gentle smooth modifier
sm=body.modifiers.new('SurfaceSmooth','SMOOTH');sm.factor=0.18;sm.iterations=3
bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=sm.name)
# keep body material white
if not body.data.materials:
    body.data.materials.append(bpy.data.materials.get('Body'))
# save/export
blend=os.path.join(CAD,'Hydrofoam_Final_Master_v90_VOXEL_BLEND.blend');bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.object.select_all(action='SELECT');bpy.ops.wm.stl_export(filepath=os.path.join(CAD,'Hydrofoam_Final_Master_v90_VOXEL_BLEND.stl'),export_selected_objects=False)
print('V90_SAVED')
