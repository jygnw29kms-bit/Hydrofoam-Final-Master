import json,os,re
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)));p=os.path.join(R,'docs','V314_LEFT_RIGHT_GEOMETRY_AUDIT.json');d=json.load(open(p));rows=d['candidate_objects'];by={r['name']:r for r in rows};out=[]
for a in rows:
 if 'Left' not in a['name']:continue
 name=a['name'].replace('Left','Right');b=by.get(name)
 if not b:out.append({'left':a['name'],'right':None,'result':'MISSING'});continue
 errors={'x_center_delta':abs(a['center_x']-b['center_x']),'y_mirror_error':abs(a['center_y']+b['center_y']),'z_center_delta':abs(a['center_z']-b['center_z']),'max_bbox_dim_delta':max(abs(x-y) for x,y in zip(a['dimensions'],b['dimensions'])),'vertex_delta':abs(a['vertices']-b['vertices'])}
 out.append({'left':a['name'],'right':name,'errors':errors,'result':'MATCH_BOUNDS' if max(errors.values())<0.02 else 'DIFFERENT'})
print('PAIRS',len(out),'DIFFERENCES',sum(x['result']!='MATCH_BOUNDS' for x in out))
for x in out:
 if x['result']!='MATCH_BOUNDS':print('DIFFERENT',x)
d['symmetry_axis']='y=0 (Left negative y, Right positive y)';d['pair_results']=out;d['warning']='Bounding boxes and vertex counts only, NOT full mirrored mesh correspondence';open(p,'w').write(json.dumps(d,indent=2))
