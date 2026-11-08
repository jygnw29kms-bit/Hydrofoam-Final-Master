import bpy,os,bmesh
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v303_LIGHTWEIGHT_HULLS.blend'))
outdir=os.path.join(R,'print','v304_p2s_hollow_modules');os.makedirs(outdir,exist_ok=True)
sources=[
 ('01 Master Central fuselage','center',-15.0),
 ('10 Planing float Left','float_left',-10.0),
 ('10 Planing float Right','float_right',-10.0)]
keep=[]
for name,label,cutx in sources:
 base=bpy.data.objects[name]
 for side in ['front','rear']:
  o=base.copy();o.data=base.data.copy();bpy.context.collection.objects.link(o)
  o.name='v304 '+label+' '+side
  xlo,xhi=(-500.,cutx) if side=='front' else (cutx,500.)
  bpy.ops.mesh.primitive_cube_add(size=1,location=((xlo+xhi)/2,0,30))
  cube=bpy.context.object;cube.name='TEMP halfspace cutter'
  cube.dimensions=(xhi-xlo,700,450)
  bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
  mod=o.modifiers.new('P2S modular sealed-section intersection','BOOLEAN')
  mod.operation='INTERSECT';mod.solver='EXACT';mod.object=cube
  bpy.context.view_layer.objects.active=o
  bpy.ops.object.modifier_apply(modifier=mod.name)
  bpy.data.objects.remove(cube,do_unlink=True)
  bm=bmesh.new();bm.from_mesh(o.data)
  bad=sum(1 for e in bm.edges if not e.is_manifold)
  signed=bm.calc_volume(signed=True)
  bm.free()
  bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
  bpy.ops.wm.stl_export(filepath=os.path.join(outdir,label+'_'+side+'.stl'),export_selected_objects=True)
  print('V304_MODULE',label,side,'manifold_errors',bad,'volume',round(signed,3))
  keep.append(o)
for o in list(bpy.data.objects):
 if o not in keep:bpy.data.objects.remove(o,do_unlink=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_v304_P2S_HOLLOW_SHELL_MODULES.blend'))
print('V304_DONE',len(keep))
