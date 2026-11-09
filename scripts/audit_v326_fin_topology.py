import bpy,bmesh,os,json
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';report=[]
for version,path in [('v324','Hydrofoam_Final_Master_v324_MOVABLE_RUDDERS_WIP.blend'),('v325','Hydrofoam_Final_Master_v325_SPLIT_TWIN_FINS_WIP.blend')]:
 bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad',path))
 for side in ['Left','Right']:
  o=bpy.data.objects['30 Tail fin '+side];bm=bmesh.new();bm.from_mesh(o.data)
  non=[e for e in bm.edges if not e.is_manifold];boundary=sum(e.is_boundary for e in bm.edges);wire=sum(e.is_wire for e in bm.edges)
  report.append({'version':version,'side':side,'faces':len(bm.faces),'nonmanifold':len(non),'boundary':boundary,'wire':wire,'nonmanifold_edge_centers':[[round(v,2) for v in (e.verts[0].co+e.verts[1].co)/2] for e in non[:25]]});bm.free()
print(json.dumps(report,indent=2))
open(os.path.join(R,'docs','V326_FIN_TOPOLOGY_ROOT_CAUSE.json'),'w').write(json.dumps({'analysis':report,'accepted':False},indent=2))

