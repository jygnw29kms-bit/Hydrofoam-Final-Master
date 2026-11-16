"""WIP FreeCAD printable servo-mount / horn interface coupons.

This is a dimensional interface fixture, NOT an integrated airframe or flight approval.
Every dimension and placement comes from measured JSON. No default dimensions.
Run with FreeCAD Python: FreeCADCmd scripts/v422_servo_interface_coupons_freecad.py measured.json
"""
import json
import math
import sys
from pathlib import Path
import FreeCAD as App
import Part
import Mesh

NAMES = {"left_aileron", "right_aileron", "elevator_left", "elevator_right", "rudder"}

def positive(p, key):
    v = float(p[key])
    if not math.isfinite(v) or v <= 0:
        raise ValueError("invalid " + key)
    return v

def run(config_file):
    cfg = json.loads(Path(config_file).read_text(encoding="utf-8"))
    if set(cfg["surfaces"]) != NAMES:
        raise ValueError("all five measured control surfaces required")
    out = Path(cfg["output_directory"]).resolve()
    if out.exists() and any(out.iterdir()):
        raise ValueError("output directory must be empty; no overwrite")
    # Validate all five surfaces before creating any files.
    specs = {}
    for name, p in cfg["surfaces"].items():
        keys = ("servo_width_mm", "servo_length_mm", "servo_height_mm",
                "servo_clearance_mm", "wall_mm", "base_mm",
                "mount_hole_diameter_mm", "mount_hole_spacing_mm",
                "mount_hole_edge_offset_mm", "horn_length_mm",
                "horn_width_mm", "horn_thickness_mm",
                "horn_pivot_hole_mm", "horn_pushrod_hole_mm",
                "horn_pushrod_offset_mm")
        d = {k: positive(p, k) for k in keys}
        if d["servo_clearance_mm"] > 1.5 or d["wall_mm"] < 1.2 or d["base_mm"] < 1.2:
            raise ValueError(name + ": unsafe prototype wall/clearance")
        if d["mount_hole_spacing_mm"] >= d["servo_length_mm"]:
            raise ValueError(name + ": mounting-hole spacing exceeds servo length")
        if d["mount_hole_edge_offset_mm"] < d["mount_hole_diameter_mm"] / 2 + 0.8:
            raise ValueError(name + ": insufficient mounting-hole edge ligament")
        if d["horn_pushrod_offset_mm"] + d["horn_pushrod_hole_mm"] / 2 + 0.8 >= d["horn_length_mm"]:
            raise ValueError(name + ": pushrod hole breaches horn end")
        if d["horn_width_mm"] <= max(d["horn_pivot_hole_mm"], d["horn_pushrod_hole_mm"]) + 1.6:
            raise ValueError(name + ": horn ligament too thin")
        origin = p["origin_airframe_mm"]
        if len(origin) != 3 or not all(math.isfinite(float(x)) for x in origin):
            raise ValueError(name + ": invalid placement")
        specs[name] = (d, App.Vector(*map(float, origin)))
    out.mkdir(parents=True, exist_ok=True)
    doc = App.newDocument("Hydrofoam_v422_ServoInterfaces_WIP")
    report = {"classification": "WIP_INTERFACE_COUPONS_NOT_INTEGRATED",
              "master_image_verified": False,
              "integrated_control_mechanisms_verified": False,
              "surfaces": {}}
    V = App.Vector
    for name, (d, origin) in specs.items():
        w = d["servo_width_mm"]
        length = d["servo_length_mm"]
        height = d["servo_height_mm"]
        c = d["servo_clearance_mm"]
        wall = d["wall_mm"]
        base = d["base_mm"]
        outer_w = w + 2 * (wall + c)
        outer_l = length + 2 * (wall + c)
        # Open-top four-wall servo cradle, with a full bottom.
        cradle = Part.makeBox(outer_l, outer_w, height + base, V(0, 0, 0))
        cavity = Part.makeBox(length + 2*c, w + 2*c, height + 1,
                              V(wall, wall, base))
        cradle = cradle.cut(cavity)
        # Two mounting holes through base, symmetric about its centreline.
        spacing = d["mount_hole_spacing_mm"]
        hole_d = d["mount_hole_diameter_mm"]
        for x in ((outer_l-spacing)/2, (outer_l+spacing)/2):
            hole = Part.makeCylinder(hole_d/2, base+2, V(x, outer_w/2, -1))
            cradle = cradle.cut(hole)
        # Horn is a separate printable flat test coupon, not attached to the servo.
        hl = d["horn_length_mm"]
        hw = d["horn_width_mm"]
        ht = d["horn_thickness_mm"]
        horn = Part.makeBox(hl, hw, ht, V(0, 0, 0))
        pivot_x = hw/2
        for x, dia in ((pivot_x, d["horn_pivot_hole_mm"]),
                       (d["horn_pushrod_offset_mm"], d["horn_pushrod_hole_mm"])):
            horn = horn.cut(Part.makeCylinder(dia/2, ht+2, V(x, hw/2, -1)))
        if d["horn_pushrod_offset_mm"] <= pivot_x + (
                d["horn_pivot_hole_mm"] + d["horn_pushrod_hole_mm"])/2 + 0.8:
            raise ValueError(name + ": horn holes intersect")
        cradle = cradle.removeSplitter()
        horn = horn.removeSplitter()
        if not all(s.isValid() and len(s.Solids) == 1 for s in (cradle, horn)):
            raise ValueError(name + ": invalid or disconnected solid")
        for label, shape, offset in (
                ("cradle", cradle, V(0,0,0)),
                ("horn", horn, V(outer_l+5,0,0))):
            placed = shape.copy()
            placed.translate(origin + offset)
            obj = doc.addObject("PartDesign::Feature", name + "_" + label)
            obj.Shape = placed
            Mesh.export([obj], str(out / (name + "_" + label + ".stl")))
        report["surfaces"][name] = {
            "cradle_volume_mm3": cradle.Volume,
            "horn_volume_mm3": horn.Volume,
            "status": "PRINTABLE_SOLID_GEOMETRY_ONLY",
            "limitations": ["Servo retention, screw pattern and spline fit not validated",
                            "No actual horn-to-rudder linkage or swept collision test",
                            "No mechanical strength, print tolerance or physical test"]}
    doc.recompute()
    doc.saveAs(str(out / "v422_servo_interface_coupons.FCStd"))
    (out / "v422_servo_interface_qa.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("WIP servo interface coupons generated; NOT INTEGRATED OR FINAL")
    return 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: FreeCADCmd script.py measured.json")
    raise SystemExit(run(sys.argv[1]))
