"""Hydrofoam v387: printable replaceable skid and recessed fastener interface.
FreeCAD macro (run with FreeCAD Python). Standalone engineering coupon, NOT integrated
into the master hull and NOT a land/water/air approval.
All dimensions mm. No edits to reference image or existing geometry.
"""
import os, json
import FreeCAD as App
import Part
import MeshPart

OUT = os.environ.get("HYDROFOAM_V387_OUT", os.path.join(os.getcwd(), "build", "v387"))
os.makedirs(OUT, exist_ok=True)
doc = App.newDocument("Hydrofoam_v387_skid_coupon")
# Coupon 110 x 28, replaceable wear shoe with two countersunk fasteners.
L, W, BASE_H = 110.0, 28.0, 6.0
HOLE_D, HEAD_D, HEAD_DEPTH = 3.4, 6.8, 2.2
FASTENER_X = (18.0, 92.0)
# Mounting plate represents only a separate interface, not the existing float.
plate = Part.makeBox(L, W, BASE_H, App.Vector(0, 0, 0))
for x in FASTENER_X:
    plate = plate.cut(Part.makeCylinder(HOLE_D / 2, BASE_H + 2, App.Vector(x, W / 2, -1)))
    plate = plate.cut(Part.makeCone(HEAD_D / 2, HOLE_D / 2, HEAD_DEPTH,
                                   App.Vector(x, W / 2, BASE_H - HEAD_DEPTH)))
plate = plate.removeSplitter()
# Sacrificial shoe is a separate solid with a continuous wear surface.
SHOE_H, EDGE_R = 3.0, 2.0
shoe = Part.makeBox(L, W, SHOE_H, App.Vector(0, 0, -SHOE_H))
# Rounded underside edges, avoiding fillets on the mechanical mating face.
bottom_edges = [e for e in shoe.Edges if all(v.Point.z < -SHOE_H + 0.001 for v in e.Vertexes)]
if bottom_edges:
    shoe = shoe.makeFillet(EDGE_R, bottom_edges)
shoe = shoe.removeSplitter()
# Through-holes on shoe are necessary for mounting from the ground-facing side;
# recessed fasteners remain protected above the wear surface.
for x in FASTENER_X:
    shoe = shoe.cut(Part.makeCylinder(HOLE_D / 2, SHOE_H + 2, App.Vector(x, W / 2, -SHOE_H - 1)))
shoe = shoe.removeSplitter()
def add_shape(name, shape, color):
    obj = doc.addObject("PartDesign::Feature", name)
    obj.Shape = shape
    obj.ViewObject.ShapeColor = color
    return obj
mount = add_shape("MountingInterface_Coupon", plate, (0.85, 0.85, 0.85))
wear = add_shape("ReplaceableWearShoe_Coupon", shoe, (0.12, 0.12, 0.12))
doc.recompute()
doc.saveAs(os.path.join(OUT, "v387_skid_coupon.FCStd"))
for name, shape in (("mount_interface", plate), ("replaceable_shoe", shoe)):
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=0.12,
                                  AngularDeflection=0.25, Relative=False)
    mesh.write(os.path.join(OUT, "v387_" + name + ".stl"))
qa = {
 "version":"v387", "classification":"STANDALONE_CAD_COUPON_NOT_MASTER_INTEGRATION",
 "approval":"NOT_APPROVED", "dimensions_mm":{"length":L,"width":W,
 "mount_height":BASE_H,"shoe_height":SHOE_H,"hole_diameter":HOLE_D,
 "head_diameter":HEAD_D,"head_recess_depth":HEAD_DEPTH},
 "shapes":[{"name":"mount","valid":plate.isValid(),"solids":len(plate.Solids),
 "volume_mm3":plate.Volume},{"name":"shoe","valid":shoe.isValid(),
 "solids":len(shoe.Solids),"volume_mm3":shoe.Volume}],
 "assembly_intersection_mm3":plate.common(shoe).Volume,
 "limits":["No master float surface or load path validated",
 "No material, fastener pullout, wear or grass/sand test",
 "No verified water sealing, hydrodynamic drag or foil clearance",
 "P2S fit, orientation, tolerances and physical printing not verified"]
}
with open(os.path.join(OUT,"v387_skid_coupon_qa.json"),"w",encoding="utf-8") as f:
    json.dump(qa,f,indent=2)
print(json.dumps(qa,indent=2))
