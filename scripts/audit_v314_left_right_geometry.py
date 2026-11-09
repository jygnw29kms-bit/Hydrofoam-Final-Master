import bpy,os,json,collections
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v314_LID_GROOVE_WIP.blend'))
objects=[o for o in bpy.data.objects if o.type=='MESH' and o.visible_get() and not o.name.startswith(('POD_','REMOVABLE_LID','M3_','V313_'))]
# Quantify symmetry around X=0 using mirrored mesh world-space bounding boxes and name-based matching.
rows=[]
for o in objects:
 n=o.name.lower()
 if any(s in n for s in ['port','starboard','left','right','links','rechts','float','schwimm','pontoon']):
  pts=[o.matrix_world @ Vector(c) for c in o.bound_box];mi=[min(p[i] for p in pts) for i in range(3)];ma=[max(p[i] for p in pts) for i in range(3)]
  rows.append({'name':o.name,'center_x':round((mi[0]+ma[0])/2,3),'center_y':round((mi[1]+ma[1])/2,3),'center_z':round((mi[2]+ma[2])/2,3),'dimensions':[round(ma[i]-mi[i],3) for i in range(3)],'vertices':len(o.data.vertices)})
print('CANDIDATES',len(rows));print(json.dumps(rows[:90],indent=2))
open(os.path.join(R,'docs','V314_LEFT_RIGHT_GEOMETRY_AUDIT.json'),'w').write(json.dumps({'source':'v314 Blender geometry','symmetry_axis':'x=0 assumed, must verify','candidate_objects':rows,'warning':'name and bounding box audit; not a surface-to-surface symmetry proof'},indent=2))
