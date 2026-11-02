import bpy, os
ROOT=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'; CAD=os.path.join(ROOT,'cad'); base=os.path.join(CAD,'Hydrofoam_Final_Master_v95_CROWNED_PLANFORM.blend')
vals=[0.70,0.80,0.90]; configs={}; v=212
for fs in vals:
 for ms in vals: configs[v]=(fs,ms); v+=1
body={'MasterPlanform','CenterHull','SponsonL','SponsonR','NoseAccentL','NoseAccentR','StripeL','StripeR','Cube','Cube.001'}; fins={'FinL','FinR','FinAccentL','FinAccentR'}; motor={'Cylinder','Cylinder.001','Cylinder.002','Cylinder.003','Torus','Cube.002','Cube.003'}
for ver,(fs,ms) in configs.items():
 bpy.ops.wm.open_mainfile(filepath=base)
 for o in bpy.context.scene.objects:
  if o.name in body:o.scale.z*=1.16
  elif o.name in fins:o.location.z*=fs;o.scale.z*=fs
  elif o.name in motor:o.location.z*=ms;o.scale.z*=ms
 bpy.ops.wm.save_as_mainfile(filepath=os.path.join(CAD,f'Hydrofoam_Final_Master_v{ver}_V5_SWEEP.blend')); bpy.ops.object.select_all(action='SELECT'); bpy.ops.wm.stl_export(filepath=os.path.join(CAD,f'Hydrofoam_Final_Master_v{ver}_V5_SWEEP.stl'),export_selected_objects=False)
