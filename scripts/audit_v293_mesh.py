import bpy,bmesh,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.blend'))
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data)
 bad=[e for e in bm.edges if len(e.link_faces)!=2]
 nonzero=len([f for f in bm.faces if f.calc_area()>1e-6])
 print('OBJECT',o.name,'VERT',len(bm.verts),'FACE',len(bm.faces),'OPEN',len(bad),'AREA',nonzero)
 bm.free()
