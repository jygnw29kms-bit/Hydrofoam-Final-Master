import bpy,os,json
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master';bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v314_LID_GROOVE_WIP.blend'))
s=bpy.context.scene
for o in s.objects:
 if o.type in ('MESH','CURVE'):o.hide_render=False
for name in ['V311_DETACHABLE_FOIL_CASSETTE_PROTOTYPE','V312_WATERTIGHT_ELECTRONICS_POD_PROTOTYPE']:
 c=bpy.data.collections.get(name)
 if c:c.hide_render=True
bpy.ops.object.camera_add();cam=bpy.context.object;cam.data.type='ORTHO';cam.data.ortho_scale=720;cam.data.clip_end=10000;s.camera=cam
s.render.engine='BLENDER_WORKBENCH';s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_cavity=True;s.render.resolution_x=1300;s.render.resolution_y=900;s.render.resolution_percentage=100
os.makedirs(os.path.join(R,'renders','v316'),exist_ok=True)
views={'left':(0,-900,120),'right':(0,900,120),'front':(-900,0,120),'rear':(900,0,120),'top':(0,0,950),'bottom':(0,0,-950)}
for name,location in views.items():
 cam.location=location;cam.rotation_euler=(Vector((0,0,10))-cam.location).to_track_quat('-Z','Y').to_euler();s.render.filepath=os.path.join(R,'renders','v316',name+'_orthographic.png');bpy.ops.render.render(write_still=True);print('RENDER',name)
open(os.path.join(R,'docs','V316_ORTHOGRAPHIC_VIEWS_QA.json'),'w').write(json.dumps({'version':'v316','views':list(views),'camera':'orthographic','status':'six Blender views; silhouette review pending','notes':'detached accessories excluded; no watertight or flight certification'},indent=2))
