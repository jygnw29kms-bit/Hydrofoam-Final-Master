from pathlib import Path
import trimesh
R=Path(r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master')
parts=list((R/'print'/'v293_individual_meshes').glob('*.stl'))
bad=[]
for p in sorted(parts):
 m=trimesh.load_mesh(str(p),force='mesh')
 if not m.is_watertight:bad.append((p.name,len(m.faces),len(m.split(only_watertight=False))))
 print('PART',p.name,'watertight',m.is_watertight,'faces',len(m.faces),'volume',round(m.volume,1))
print('RESULT',len(parts),'TOTAL',len(bad),'BAD',bad)
