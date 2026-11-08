"""Conservative vertex-to-surface clearance screening; NOT a structural approval."""
import os,json,glob
import numpy as np
import trimesh
from scipy.spatial import cKDTree
R=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
rows=[]
for side in ('left','right'):
 for half in ('front','rear'):
  skid=os.path.join(R,'print','v307_land_skid_prototypes',f'land_skid_{side}_{half}.stl')
  hull=os.path.join(R,'print','v306_faceted_float_modules',f'float_{side}_{half}.stl')
  a=trimesh.load(skid,force='mesh');b=trimesh.load(hull,force='mesh')
  # Sample surface rather than relying only on bounding boxes; deterministic seed.
  np.random.seed(308)
  sample=b.sample(12000)
  tree=cKDTree(sample)
  dist=tree.query(a.vertices,k=1)[0]
  row=dict(side=side,half=half,skid_z_mm=a.bounds[:,2].tolist(),hull_z_mm=b.bounds[:,2].tolist(),nearest_sample_mm=float(dist.min()),median_sample_mm=float(np.median(dist)),skid_bounds_mm=a.bounds.tolist(),hull_bounds_mm=b.bounds.tolist(),method='sampled surface distance: unsigned, approximate; does not establish interference or screw engagement',mounting_verified=False)
  rows.append(row)
  print(side,half,'nearest sampled mm',round(row['nearest_sample_mm'],3))
out=os.path.join(R,'docs','V308_SKID_INTERFACE_SCREEN.json')
with open(out,'w') as f:json.dump(rows,f,indent=2)
print('V308_SCREEN_COMPLETE',len(rows))
