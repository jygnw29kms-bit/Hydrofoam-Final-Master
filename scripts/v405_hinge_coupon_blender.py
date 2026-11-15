"""v405: Blender printable hinge/control coupon, not integrated Final Master.
Run: blender -b --python scripts/v405_hinge_coupon_blender.py -- --out OUTPUT_DIR
Units millimetres. Generates distinct solids for fixed leaf, moving leaf, pin,
servo tray and horn; exports STL and Blender scene plus geometric QA JSON.
A coupon is NOT proof of installed servo linkage, load rating or image fidelity.
"""
import bpy, math, json, sys, pathlib, argparse
from mathutils import Vector

def cube(name, center, dims):
    bpy.ops.mesh.primitive_cube_add(size=1, location=tuple(center))
    o=bpy.context.object; o.name=name
    o.dimensions=tuple(dims); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    return o

def cylinder(name, center, radius, depth, vertices=64):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=tuple(center))
    o=bpy.context.object; o.name=name; return o

def boolean(a,b,operation):
    bpy.context.view_layer.objects.active=a
    mod=a.modifiers.new('machined_'+b.name,'BOOLEAN');mod.operation=operation;mod.solver='EXACT';mod.object=b
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(b,do_unlink=True)

def joined(name,objects):
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    objects[0].name=name;return objects[0]

def leaf(name, side, z_positions, clearance):
    base=cube(name+'_plate',(side*12,0,0),(22,24,3))
    knuckles=[]
    for z in z_positions:
        outer=cylinder(name+'_barrel_'+str(z),(0,0,z),3.8,7.6)
        # cylinder axis is Z, bore for 3 mm pin with 0.25 radial clearance
        bore=cylinder('bore',(0,0,z),1.5+clearance,8.2)
        boolean(outer,bore,'DIFFERENCE')
        knuckles.append(outer)
    return joined(name,[base]+knuckles)

def aabb(o):
    return [(min((o.matrix_world@Vector(c))[i] for c in o.bound_box),
             max((o.matrix_world@Vector(c))[i] for c in o.bound_box)) for i in range(3)]

def main():
    p=argparse.ArgumentParser();p.add_argument('--out',required=True)
    args=p.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    out=pathlib.Path(args.out);out.mkdir(parents=True,exist_ok=True)
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    # Hinge knuckles staggered along Z; plates sit in XY. Coupon only.
    fixed=leaf('fixed_leaf',-1,[-8,8],0.25)
    moving=leaf('moving_leaf',1,[0],0.25)
    pin=cylinder('hinge_pin',(0,0,0),1.5,27)
    # Servo tray is a deliberately generic dimensioned coupon, not a chosen servo fit.
    tray=cube('servo_tray_blank',(42,0,0),(35,28,4))
    horn=cube('rudder_horn_blank',(75,0,0),(16,4,20))
    hole=cylinder('horn_pushrod_hole',(80,0,5),1.2,8)
    hole.rotation_euler[0]=math.pi/2
    boolean(horn,hole,'DIFFERENCE')
    solids=[fixed,moving,pin,tray,horn]
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'v405_hinge_coupon.blend'))
    for o in solids:
        bpy.ops.object.select_all(action='DESELECT');o.select_set(True);bpy.context.view_layer.objects.active=o
        bpy.ops.wm.stl_export(filepath=str(out/(o.name+'.stl')),export_selected_objects=True)
    # Rotation clearance analytic envelope: circular pin / bore radial margin,
    # and axial knuckle separation; not full-body collision verification.
    checks={'radial_clearance_mm':0.25,'pin_diameter_mm':3.0,
            'knuckle_gap_mm':0.4,'requested_sweep_deg':[-30,30],
            'surface_sweep_validated':False,
            'servo_fit_validated':False,'full_assembly_collision_validated':False}
    report={'schema':'hydrofoam.v405.coupon','status':'WIP_ONLY',
            'objects':{o.name:{'bounds_mm':aabb(o)} for o in solids},
            'checks':checks,
            'limitations':['Generic test coupon, no original hull integration',
                           'No measured servo dimensions or horn-to-servo rod kinematics',
                           'No independent mesh-manifold, print-fit or dynamic collision test',
                           'No Land/Water/Air operational evidence']}
    (out/'v405_coupon_qa.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
if __name__=='__main__':main()
