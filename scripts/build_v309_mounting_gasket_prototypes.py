import bpy,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v308_CONFORMAL_LAND_SKIDS.blend'))
folder=os.path.join(R,'print','v309_mounting_gasket_prototypes');os.makedirs(folder,exist_ok=True)
mat=bpy.data.materials.get('v309 flexible gasket WIP') or bpy.data.materials.new('v309 flexible gasket WIP');mat.diffuse_color=(.09,.11,.12,1)
parts=[]
for side in ('left','right'):
 cy=-119 if side=='left' else 119
 for half,xa,xb in (('front',-135,-14),('rear',-6,135)):
  hull=bpy.data.objects['v305 HOLLOW float_'+side+'_'+half]
  bvh=BVHTree.FromObject(hull,bpy.context.evaluated_depsgraph_get())
  for idx,x in enumerate((xa+15,xb-15),1):
   hit,normal,face,dist=bvh.ray_cast(Vector((x,cy,-150)),Vector((0,0,1)),250)
   if hit is None:raise RuntimeError('missing hull '+str((side,half,idx)))
   # Annular gasket at screw point; planar prototype, NOT conformal or leak-tight yet.
   z=float(hit.z)-0.30
   bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=5,depth=.50,location=(x,cy,z))
   obj=bpy.context.object;obj.name=f'v309 GASKET WIP {side} {half} {idx}'
   bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=1.65,depth=3,location=(x,cy,z))
   cut=bpy.context.object
   mod=obj.modifiers.new('M3 bore','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cut
   bpy.context.view_layer.objects.active=obj;bpy.ops.object.modifier_apply(modifier=mod.name)
   bpy.data.objects.remove(cut,do_unlink=True)
   obj.data.materials.append(mat)
   bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);bpy.context.view_layer.objects.active=obj
   bpy.ops.wm.stl_export(filepath=os.path.join(folder,f'gasket_{side}_{half}_{idx}.stl'),export_selected_objects=True)
   parts.append(obj)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v309_GASKET_WIP.blend'))
print('V309_GASKETS_EXPORTED',len(parts))
