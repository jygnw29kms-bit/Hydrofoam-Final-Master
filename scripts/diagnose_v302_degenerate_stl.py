from pathlib import Path
import trimesh
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
p=R/'print'/'v302_shell_prototypes'
for k in ['central_hull_shell.stl','removable_smoked_canopy.stl']:
 m=trimesh.load_mesh(str(p/k),force='mesh')
 n=len(m.faces)
 mask=m.nondegenerate_faces(height=1e-5)
 print(k,'degenerate_removed',n-int(mask.sum()))
 m.update_faces(mask);m.remove_unreferenced_vertices();m.merge_vertices(digits_vertex=6)
 print('AFTER watertight',m.is_watertight,'winding',m.is_winding_consistent,'components',len(m.split(only_watertight=False)),'volume',m.volume)
