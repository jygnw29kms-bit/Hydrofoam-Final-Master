import bpy,os,json,math
from mathutils import Vector
R=r'C:\Users\dezen\Desktop\JL1976\Hydrofoam\Final_Master'
bpy.ops.wm.open_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v312_ELECTRONICS_POD_WIP.blend'))
s=bpy.context.scene;c=bpy.data.collections.get('V312_WATERTIGHT_ELECTRONICS_POD_PROTOTYPE')
for o in list(c.objects):
 if o.name.startswith('SEAL_STRIP_'):bpy.data.objects.remove(o,do_unlink=True)
# replace four disconnected strips with one closed gasket-loop curve, on the same prototype enclosure
m=bpy.data.materials.new('V313 closed-loop gasket prototype');m.diffuse_color=(.04,.07,.08,1)
cv=bpy.data.curves.new('continuous perimeter gasket centerline','CURVE');cv.dimensions='3D';cv.resolution_u=16;cv.bevel_depth=1.2;cv.bevel_resolution=3
sp=cv.splines.new('POLY');pts=[(-69,-37),(69,-37),(69,37),(-69,37)];sp.points.add(len(pts)-1)
for i,(dx,dy) in enumerate(pts):sp.points[i].co=(dx,-340+dy,23,1)
sp.use_cyclic_u=True
o=bpy.data.objects.new('V313_CONTINUOUS_CLOSED_LOOP_GASKET_WIP',cv);c.objects.link(o);cv.materials.append(m)
# Make a separate reusable sealing datum; it is NOT a milled channel and has no verified compression.
report={'version':'v313','status':'closed-loop gasket path modeled, still NOT waterproof','improvement':'replaced four disconnected gasket strips with one cyclic perimeter spline','gasket_centerline_mm_assuming_blender_units':[[dx,dy] for dx,dy in pts],'gasket_nominal_radius':1.2,'unresolved':['actual groove not cut into flange','gasket compression and corner radius unverified','fastener bosses not sealed','cable penetrations missing','pod not fitted to fuselage','no pressure test'],'acceptance':'no waterproof claim until mechanical fit and immersion test'}
open(os.path.join(R,'docs','V313_GASKET_LOOP_QA.json'),'w').write(json.dumps(report,indent=2))
s.render.filepath=os.path.join(R,'renders','v313','continuous_gasket_pod_iso.png');os.makedirs(os.path.dirname(s.render.filepath),exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(R,'cad','Hydrofoam_Final_Master_v313_CONTINUOUS_GASKET_WIP.blend'));bpy.ops.render.render(write_still=True)
print('V313_GASKET_CLOSED',sp.use_cyclic_u)
