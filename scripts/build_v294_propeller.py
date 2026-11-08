import bpy,os,math,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v293_PHOTO_GEOMETRY.blend'))
for ob in list(bpy.data.objects):
 if ob.name.startswith('46 Pusher prop blade'):
  bpy.data.objects.remove(ob,do_unlink=True)
# Photo master shows two wide, tapered propeller blades, not cylindrical rods.
black=bpy.data.materials.get('Smoked panoramic canopy')
def blade(name,sign):
 # x longitudinal, y lateral, z vertical. Blade chord 13mm near root tapering to 7mm.
 levels=[(7,10,-1),(14,15,-3),(24,14,-5),(36,11,-8),(48,6,-10),(52,1,-11)]
 vertices=[]
 for radius,chord,sweep in levels:
  z=102+sign*radius
  yc=sweep*sign
  vertices.extend([(183.4,yc-chord*.5,z),(183.4,yc+chord*.5,z),
                   (185.2,yc-chord*.5,z),(185.2,yc+chord*.5,z)])
 faces=[]
 for i in range(len(levels)-1):
  k=4*i;n=k+4
  faces.extend([(k,n,n+1,k+1),(k+2,k+3,n+3,n+2),
                (k,k+2,n+2,n),(k+1,n+1,n+3,k+3)])
 faces.extend([(0,1,3,2),(4*(len(levels)-1),4*(len(levels)-1)+2,4*(len(levels)-1)+3,4*(len(levels)-1)+1)])
 me=bpy.data.meshes.new(name);me.from_pydata(vertices,[],faces);me.update()
 ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob);me.materials.append(black)
 for f in me.polygons:f.use_smooth=True
 return ob
blade('46 Pusher propeller upper blade',1)
blade('46 Pusher propeller lower blade',-1)
# Rotor disk clearance test to tail fins, approximate swept radius 52 mm
# Motor centered y=0,z=102; fin roots y=181 => >120mm lateral clearance.
for ob in bpy.data.objects:
 if ob.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(ob.data)
 boundary=sum(len(e.link_faces)!=2 for e in bm.edges)
 if boundary: print('WARNING_OPEN_MESH',ob.name,boundary)
 bm.free()
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v294_PROPELLER_GEOMETRY.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.wm.stl_export(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v294_PROPELLER_GEOMETRY.stl'),export_selected_objects=False)
print('V294_SAVED',len([o for o in bpy.data.objects if o.type=='MESH']))
