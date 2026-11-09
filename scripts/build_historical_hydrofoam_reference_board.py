import bpy,os,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
pages=(1,2,3,4,5,9)
for k,n in enumerate(pages):
 path=os.path.join(R,'renders','historical_plan',f'construction_page_{n:02d}.png')
 img=bpy.data.images.load(path,check_existing=True)
 w=210;h=297;x=(k%3-1)*225;y=(1-k//3)*310
 verts=[(x-w/2,y-h/2,0),(x+w/2,y-h/2,0),(x+w/2,y+h/2,0),(x-w/2,y+h/2,0)]
 me=bpy.data.meshes.new(f'Page {n:02d} reference');me.from_pydata(verts,[],[(0,1,2,3)]);me.update()
 obj=bpy.data.objects.new(f'HISTORICAL REFERENCE PAGE {n:02d} (NOT SCALE DRAWING)',me);s.collection.objects.link(obj)
 mat=bpy.data.materials.new(f'Page {n:02d} image');mat.diffuse_color=(1,1,1,1);mat.use_nodes=True
 nodes=mat.node_tree.nodes;nodes.clear();tex=nodes.new('ShaderNodeTexImage');tex.image=img;em=nodes.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1;output=nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(tex.outputs['Color'],em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],output.inputs['Surface']);obj.data.materials.append(mat)
 uv=obj.data.uv_layers.new();uvcoords=((0,0),(1,0),(1,1),(0,1))
 for poly in me.polygons:
  for loop in poly.loop_indices:uv.data[loop].uv=uvcoords[me.loops[loop].vertex_index]
bpy.ops.object.camera_add(location=(0,155,900));cam=bpy.context.object;cam.rotation_euler=(Vector((0,155,0))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=1050;s.camera=cam
s.render.engine='BLENDER_EEVEE_NEXT';s.render.resolution_x=1800;s.render.resolution_y=1250;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.filepath=os.path.join(R,'renders','historical_plan','blender_reference_board.png');s.render.film_transparent=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Historical_Hydrofoam_REFERENCE_BOARD_WIP.blend'))
bpy.ops.render.render(write_still=True)
print('REFERENCE_BOARD_RENDERED')
