"""v351 Blender BVH swept-motion clearance audit for actual installed rudder/elevon assemblies.

Usage:
 blender -b cad/ASSEMBLY.blend --python scripts/audit_v351_control_sweep.py -- config.json
Configuration (millimetres and degrees):
 {
   "controls": [{
      "name":"left_rudder",
      "moving_objects":["actual_rudder","actual_horn"],
      "fixed_objects":["actual_fin","actual_servo_mount","actual_hinge_brackets"],
      "hinge_axis_point_mm":[0,0,0],
      "hinge_axis_direction":[0,0,1],
      "minimum_deg":-25,"maximum_deg":25,"step_deg":1
   }]
 }
This checks triangle intersections at sampled poses; it does not prove continuous
clearance between samples, strength, servo torque or printability. Never accept
a missing mesh as a pass. Separate hardware and contact verification required.
"""
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

def point(v):
    if not isinstance(v,list) or len(v)!=3 or any(type(x) not in (int,float) or not math.isfinite(x) for x in v):
        raise ValueError("expected finite three-vector")
    return Vector(v)

def mesh_bvh(obj, matrix):
    deps=bpy.context.evaluated_depsgraph_get()
    evaluated=obj.evaluated_get(deps)
    mesh=evaluated.to_mesh()
    try:
        vertices=[matrix @ v.co for v in mesh.vertices]
        mesh.calc_loop_triangles()
        triangles=[tuple(t.vertices) for t in mesh.loop_triangles]
        if not triangles: raise ValueError("empty mesh: "+obj.name)
        return BVHTree.FromPolygons(vertices,triangles,all_triangles=True,epsilon=0.000001)
    finally:
        evaluated.to_mesh_clear()

def run(config):
    reports=[]
    for control in config.get("controls",[]):
        name=control["name"]
        moving=control["moving_objects"]
        fixed=control["fixed_objects"]
        if not moving or not fixed: raise ValueError(name+": missing moving/fixed objects")
        names=moving+fixed
        if len(set(names))!=len(names): raise ValueError(name+": duplicate object across groups")
        objects=[]
        for n in names:
            o=bpy.data.objects.get(n)
            if o is None or o.type!="MESH": raise ValueError(name+": missing mesh "+n)
            objects.append(o)
        pivot=point(control["hinge_axis_point_mm"])
        axis=point(control["hinge_axis_direction"])
        if axis.length<1e-9: raise ValueError(name+": zero hinge axis")
        axis.normalize()
        lo=float(control["minimum_deg"]);hi=float(control["maximum_deg"])
        step=float(control["step_deg"])
        if not all(math.isfinite(v) for v in (lo,hi,step)) or step<=0 or hi<lo or hi-lo>360:
            raise ValueError(name+": invalid sweep")
        # Config coordinates are mm; Blender native object coordinates are scene units.
        mm_to_scene=0.001/bpy.context.scene.unit_settings.scale_length
        pivot*=mm_to_scene
        stationary=[(n,mesh_bvh(bpy.data.objects[n],bpy.data.objects[n].matrix_world.copy())) for n in fixed]
        hits=[]
        count=int(math.ceil((hi-lo)/step))
        angles=[lo+min(i*step,hi-lo) for i in range(count+1)]
        if angles[-1]<hi: angles.append(hi)
        for angle in angles:
            rotation=Matrix.Translation(pivot) @ Matrix.Rotation(math.radians(angle),4,axis) @ Matrix.Translation(-pivot)
            for n in moving:
                obj=bpy.data.objects[n]
                moving_bvh=mesh_bvh(obj,rotation @ obj.matrix_world)
                for other,static_bvh in stationary:
                    overlaps=moving_bvh.overlap(static_bvh)
                    if overlaps:
                        hits.append({"angle_deg":round(angle,5),"moving":n,"fixed":other,"triangle_pair_count":len(overlaps)})
        reports.append({"name":name,"sampled_angles":len(angles),"intersection_free_at_samples":not hits,
                        "intersections":hits[:100],"truncated_hits":max(0,len(hits)-100)})
    return {"version":"v351","accepted":False,"sampled_mesh_intersection_screen_pass":bool(reports) and all(r["intersection_free_at_samples"] for r in reports),
            "controls":reports,"limitations":["Mesh triangle overlap at discrete poses only; no continuous swept-volume guarantee.",
            "Adjacent hinge components may intentionally touch; exclude only documented intended contact pairs.",
            "Does not verify pushrod travel, servo torque, printability, watertightness, or physical operation.",
            "No acceptance without measured hardware and original-master image comparison."]}

if __name__=="__main__":
    if "--" not in sys.argv: raise SystemExit("pass -- config.json")
    path=Path(sys.argv[sys.argv.index("--")+1])
    result=run(json.loads(path.read_text(encoding="utf-8")))
    output=path.with_name(path.stem+"_v351_control_sweep_WIP.json")
    output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(output,result["sampled_mesh_intersection_screen_pass"])
