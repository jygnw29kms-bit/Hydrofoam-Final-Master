import bpy,os,json,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v325_SPLIT_TWIN_FINS_WIP.blend'))
fin=bpy.data.objects['30 Tail fin Left'];bm=bmesh.new();bm.from_mesh(fin.data)
boundary=[e for e in bm.edges if e.is_boundary];before=len(boundary)
# Attempt conservative topological hole closure, without altering other fin or rudder geometry.
filled=bmesh.ops.holes_fill(bm,edges=boundary,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));after=sum(not e.is_manifold for e in bm.edges)
if after==0:bm.to_mesh(fin.data);fin.data.update()
bm.free()
report={'version':'v327','repair':'attempt boundary-loop cap on v325 left fin','boundary_edges_before':before,'nonmanifold_edges_after_trial':after,'repair_applied':after==0,'note':'A manifold result is not proof of correct cut shape, watertight printing or mechanical integrity','accepted':False,'next':['inspect geometry visually for accidental caps','verify no rudder interference','validate hinge axis and sweep']}
open(os.path.join(R,'docs','V327_LEFT_FIN_REPAIR_QA.json'),'w').write(json.dumps(report,indent=2))
if after==0:
 os.makedirs(os.path.join(R,'renders','v327'),exist_ok=True);bpy.context.scene.render.filepath=os.path.join(R,'renders','v327','repaired_twin_fins_iso.png');bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v327_FIN_REPAIR_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V327_REPAIR',json.dumps(report))
