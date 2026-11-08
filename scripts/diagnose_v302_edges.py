import numpy as np,trimesh
m=trimesh.load_mesh(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master\print\v302_shell_prototypes\central_hull_shell.stl',force='mesh')
counts=np.bincount(m.edges_unique_inverse,minlength=len(m.edges_unique))
for i in np.where(counts!=2)[0]:
 idx=m.edges_unique[i]
 print('BROKEN',i,'edge_count',counts[i],'verts',m.vertices[idx].round(5))
