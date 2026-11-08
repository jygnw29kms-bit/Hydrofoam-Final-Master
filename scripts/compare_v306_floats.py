import trimesh,os,json,numpy as np
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
names=['float_left','float_right']
report={}
for name in names:
 m={}
 for kind,folder in [('previous','v305_clean_p2s_shell_modules'),('new','v306_faceted_float_modules')]:
  m[kind]={}
  for seg in ['front','rear']:
   obj=trimesh.load_mesh(os.path.join(R,'print',folder,name+'_'+seg+'.stl'),force='mesh')
   cut=np.asarray(obj.vertices)[abs(np.asarray(obj.vertices)[:,0]+10)<.001]
   q=np.unique(np.round(cut[:,1:],3),axis=0)
   m[kind][seg]={'volume_mm3':float(obj.volume),'watertight':bool(obj.is_watertight),
    'consistent':bool(obj.is_winding_consistent),'max_axis_mm':float(max(obj.extents)),
    'cut_vertices_3dp':q.tolist(),'cut_count':len(q)}
 old=sum(m['previous'][x]['volume_mm3'] for x in ['front','rear'])
 new=sum(m['new'][x]['volume_mm3'] for x in ['front','rear'])
 a=set(tuple(x) for x in m['new']['front']['cut_vertices_3dp'])
 b=set(tuple(x) for x in m['new']['rear']['cut_vertices_3dp'])
 overlap=len(a&b)
 missing=len(a^b)
 report[name]={'old_mm3':old,'new_mm3':new,'mass_change_pct':100*(new-old)/old,
 'new_front_rear_seam_vertices_shared':overlap,'new_front_rear_seam_vertices_difference':missing,
 'new_both_watertight':all(m['new'][x]['watertight'] for x in ['front','rear']),
 'new_both_consistent':all(m['new'][x]['consistent'] for x in ['front','rear']),
 'new_max_axis_mm':max(m['new'][x]['max_axis_mm'] for x in ['front','rear'])}
 print(name,report[name])
assert all(report[n]['new_both_watertight'] and report[n]['new_both_consistent'] and report[n]['new_max_axis_mm']<256 for n in names)
with open(os.path.join(R,'docs','V306_FACETED_FLOAT_COMPARISON.json'),'w') as f:
 json.dump(report,f,indent=2)
print('V306_COMPARE_DONE')
