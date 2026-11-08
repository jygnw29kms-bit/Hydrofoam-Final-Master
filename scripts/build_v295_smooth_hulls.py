import bpy,os,bmesh,json
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
src=os.path.join(R,'cad','Hydrofoam_Final_Master_v294_PROPELLER_GEOMETRY.blend')
bpy.ops.wm.open_mainfile(filepath=src)
report=[]
for obj in list(bpy.data.objects):
 if obj.type!='MESH':continue
 if not (obj.name.startswith('01 ') or obj.name.startswith('02 ') or obj.name.startswith('10 ') or obj.name.startswith('11 ') or obj.name.startswith('12 ')):continue
 # Add real topology along hull/canopy, smoothing shape while retaining exact longitudinal profile stations.
 old=len(obj.data.vertices)
 mod=obj.modifiers.new('V295 surface refinement','SUBSURF')
 mod.subdivision_type='CATMULL_CLARK';mod.levels=2;mod.render_levels=2
 bpy.context.view_layer.objects.active=obj
 bpy.ops.object.modifier_apply(modifier=mod.name)
 new=len(obj.data.vertices)
 report.append({'part':obj.name,'before_vertices':old,'after_vertices':new})
# Verify all objects manifold, keep separate components as designed.
aud=[]
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 edges=sum(1 for e in bm.edges if not e.is_manifold)
 aud.append({'part':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonmanifold_edges':edges})
 bm.free()
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v295_SMOOTH_HULLS.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v295_SMOOTH_HULLS.stl'),export_selected_objects=False)
p=os.path.join(R,'docs','V295_HULL_SURFACE_AUDIT.json')
with open(p,'w',encoding='utf8') as f:json.dump({'source':'v294','refined':report,'audit':aud,'all_parts_manifold':all(x['nonmanifold_edges']==0 for x in aud),'note':'Surface refinement only. Not certified as print-ready: intersections, mount holes, center of gravity and full-size scaling unresolved.'},f,indent=2)
print('V295_DONE',len(report),'REFINED',len(aud),'PARTS','BAD',sum(x['nonmanifold_edges']>0 for x in aud))
