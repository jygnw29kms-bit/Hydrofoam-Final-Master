from pathlib import Path
import trimesh,json
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
groups={'hull':R/'print'/'v297_hull_modules','wing':R/'print'/'v297_wing_modules'}
pairs=[]
for category,folder in groups.items():
 for front_path in sorted(folder.glob('*_front.stl')):
  rear_path=Path(str(front_path).replace('_front.stl','_rear.stl'))
  assert rear_path.exists()
  front=trimesh.load_mesh(front_path,force='mesh')
  rear=trimesh.load_mesh(rear_path,force='mesh')
  plane=-15 if 'Central_fuselage' in front_path.name else -10
  def seam(m):
   v=m.vertices
   at=v[abs(v[:,0]-plane)<.002]
   return {'count':len(at),'y_min':float(at[:,1].min()),'y_max':float(at[:,1].max()),'z_min':float(at[:,2].min()),'z_max':float(at[:,2].max())}
  a,b=seam(front),seam(rear)
  match=all(abs(a[k]-b[k])<.01 for k in ('y_min','y_max','z_min','z_max'))
  item={'part':front_path.name.replace('_front.stl',''),'category':category,'plane_x_mm':plane,'seam_bounds_match':match,'front_seam':a,'rear_seam':b,'both_watertight':front.is_watertight and rear.is_watertight,'both_consistent':front.is_winding_consistent and rear.is_winding_consistent,'front_dims_mm':front.extents.tolist(),'rear_dims_mm':rear.extents.tolist(),'volume_sum_mm3':float(front.volume+rear.volume)}
  pairs.append(item)
  print(item['part'],'seam_match',match,'closed',item['both_watertight'],'dimensions',front.extents.round(1),rear.extents.round(1))
assert len(pairs)==5
assert all(p['seam_bounds_match'] and p['both_watertight'] and p['both_consistent'] for p in pairs)
out=R/'docs'/'V297_SEAM_VALIDATION.json'
out.write_text(json.dumps({'status':'geometric_seam_check_only','pairs':pairs,'caveats':['No joining features yet','No material or weight validation','No photo fidelity certification','No slicer verification']},indent=2),encoding='utf8')
print('PASS_5_SEAMS',out)
