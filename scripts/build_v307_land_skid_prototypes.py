import bpy,os,math,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v306_FACETED_MASTER_FLOATS.blend'))
# Land-contact skid prototypes are separate replaceable parts, not a revision
# to the immutable visible master hull. Their thickness/clearance requires testing.
coll=bpy.data.collections.new('v307 replaceable PETG land skids WIP')
bpy.context.scene.collection.children.link(coll)
parts=[]
for side in [-1,1]:
 for half,xa,xb in [('front',-135,-14),('rear',-6,135)]:
  # Segmented contact plate with a shallow longitudinal wear rib.
  center=(xa+xb)*.5;length=xb-xa;cy=side*119
  bpy.ops.mesh.primitive_cube_add(size=1,location=(center,cy,-9.3))
  o=bpy.context.object;o.name=f'v307 PETG land skid {"left" if side<0 else "right"} {half}'
  o.dimensions=(length,17,3.2)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  bevel=o.modifiers.new('Edge radii 1.5mm','BEVEL');bevel.width=1.5;bevel.segments=3
  bpy.context.view_layer.objects.active=o;bpy.ops.object.modifier_apply(modifier=bevel.name)
  # Screw bores at both ends, vertical M3 clearance, no invented fastening into hull.
  for xx in [xa+15,xb-15]:
   bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=1.65,depth=12,location=(xx,cy,-9.3))
   cutter=bpy.context.object
   mod=o.modifiers.new('M3 clearance','BOOLEAN');mod.operation='DIFFERENCE';mod.solver='EXACT';mod.object=cutter
   bpy.context.view_layer.objects.active=o
   bpy.ops.object.modifier_apply(modifier=mod.name)
   bpy.data.objects.remove(cutter,do_unlink=True)
  for c in list(o.users_collection):c.objects.unlink(o)
  coll.objects.link(o)
  mat=bpy.data.materials.get('Black PETG skid') or bpy.data.materials.new('Black PETG skid')
  mat.diffuse_color=(.025,.028,.035,1)
  o.data.materials.clear();o.data.materials.append(mat)
  parts.append(o)
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v307_LAND_SKID_PROTOTYPES.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
folder=os.path.join(R,'print','v307_land_skid_prototypes');os.makedirs(folder,exist_ok=True)
for o in parts:
 bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
 name=o.name.replace('v307 PETG land skid ','').replace(' ','_')
 bpy.ops.wm.stl_export(filepath=os.path.join(folder,'land_skid_'+name+'.stl'),export_selected_objects=True)
print('V307_EXPORTED',len(parts))
