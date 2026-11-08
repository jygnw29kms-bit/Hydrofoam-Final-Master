import glob,os,trimesh,json
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
source=60972.00199858343
report={}
for side in ['Left','Right']:
 paths=[os.path.join(R,'print','v298_wing_modules',f'20_Swept_blended_wing_{side}_{end}.stl') for end in ['front','rear']]
 ms=[trimesh.load_mesh(p,force='mesh') for p in paths]
 volumes=[m.volume for m in ms]
 err=abs(sum(volumes)-source)/source
 checks={'watertight':all(m.is_watertight for m in ms),'winding_consistent':all(m.is_winding_consistent for m in ms),
 'axis_p2s_size':all(all(d<256 for d in m.extents) for m in ms),
 'volume_error_relative':err,'volume_pass_1pct':err<.01,'source_mm3':source,'parts_volume_mm3':volumes}
 report[side]=checks
 print(side,'volumes',volumes,'sum',sum(volumes),'source',source,'err_pct',err*100,'checks',checks)
assert all(c['watertight'] and c['winding_consistent'] and c['axis_p2s_size'] and c['volume_pass_1pct'] for c in report.values())
with open(os.path.join(R,'docs','V298_WING_VOLUME_QA.json'),'w') as f:json.dump(report,f,indent=2,default=lambda o:o.item() if hasattr(o,'item') else str(o))
print('V298_ALL_WINGS_PASS')
