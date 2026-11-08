import trimesh,numpy as np
from pathlib import Path
p=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')/'print'/'v304_p2s_hollow_modules'
for fn in ['center_front.stl','float_left_rear.stl']:
 m=trimesh.load_mesh(str(p/fn),force='mesh')
 counts=np.bincount(m.edges_unique_inverse,minlength=len(m.edges_unique))
 print(fn,'broken_edges',len(np.where(counts!=2)[0]),'counts',dict(zip(*np.unique(counts[counts!=2],return_counts=True))),'degenerate',sum(~m.nondegenerate_faces(height=1e-5)))
 for s in m.split(only_watertight=False):
  print('COMPONENT',len(s.faces),s.is_watertight,s.volume)
