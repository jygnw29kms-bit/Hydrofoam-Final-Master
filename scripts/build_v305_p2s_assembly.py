import bpy,os
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v303_LIGHTWEIGHT_HULLS.blend'))
white=next(m for m in bpy.data.materials if 'white' in m.name.lower())
remove=[
 '01 Master Central fuselage','10 Planing float Left','10 Planing float Right',
 '20 Swept blended wing Left','20 Swept blended wing Right']
for name in remove:
 obj=bpy.data.objects.get(name)
 assert obj, 'MISSING '+name
 bpy.data.objects.remove(obj,do_unlink=True)
def put(path,name):
 bpy.ops.wm.stl_import(filepath=path)
 ob=bpy.context.object;ob.name=name
 ob.data.materials.append(white)
 return ob
hfolder=os.path.join(R,'print','v305_clean_p2s_shell_modules')
wfolder=os.path.join(R,'print','v298_wing_modules')
for f in ['center_front.stl','center_rear.stl',
 'float_left_front.stl','float_left_rear.stl',
 'float_right_front.stl','float_right_rear.stl']:
 put(os.path.join(hfolder,f),'v305 HOLLOW '+f.replace('.stl',''))
for sign in ['Left','Right']:
 for segment in ['front','rear']:
  f='20_Swept_blended_wing_'+sign+'_'+segment+'.stl'
  put(os.path.join(wfolder,f),'v305 WING '+f.replace('.stl',''))
# save before rendering, preserving editable component organization
out=os.path.join(R,'cad','Hydrofoam_Final_Master_v305_P2S_ASSEMBLY.blend')
bpy.ops.wm.save_as_mainfile(filepath=out)
print('V305_ASSEMBLY_DONE','physical_meshes',len([o for o in bpy.data.objects if o.type=='MESH' and not o.name.startswith('REFERENCE ONLY')]))
