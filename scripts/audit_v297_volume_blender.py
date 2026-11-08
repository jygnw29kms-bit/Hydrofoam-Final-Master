import bpy,bmesh,json
from pathlib import Path
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
bpy.ops.wm.open_mainfile(filepath=str(R/'cad'/'Hydrofoam_Final_Master_v296_WINGROOT_FAIRINGS.blend'))
mapping={'01_Master_Central_fuselage':'01 Master Central fuselage','10_Planing_float_Left':'10 Planing float Left','10_Planing_float_Right':'10 Planing float Right','20_Swept_blended_wing_Left':'20 Swept blended wing Left','20_Swept_blended_wing_Right':'20 Swept blended wing Right'}
out={}
for key,name in mapping.items():
 bm=bmesh.new();bm.from_mesh(bpy.data.objects[name].data)
 out[key]=abs(bm.calc_volume(signed=True));bm.free()
print('SOURCE_VOLUMES',out)
(R/'docs'/'V297_SOURCE_VOLUMES.json').write_text(json.dumps(out,indent=2))
