"""v419: FreeCAD solid-level hinge articulation coupon, not an airframe approval.

Run with FreeCAD's Python interpreter: FreeCADCmd scripts/v419_hinge_sweep_coupon.py config.json
Config must contain measured dimensions in mm. No default dimensions are invented.
Outputs FCStd, STL parts and JSON sweep evidence. Local geometry is evaluated
before the common airframe placement, preventing v411's frame-mixing error.
"""
import json, math, sys
from pathlib import Path
import FreeCAD as App
import Part, Mesh

def finite_positive(p, key):
    x=float(p[key])
    if not math.isfinite(x) or x<=0: raise ValueError("invalid "+key)
    return x

def run(config_path):
    cfg=json.loads(Path(config_path).read_text(encoding="utf-8"))
    names={"left_aileron","right_aileron","elevator_left","elevator_right","rudder"}
    if set(cfg.get("surfaces",{}))!=names:
        raise ValueError("five measured surfaces required")
    output=Path(cfg["output_directory"]).resolve()
    if output.exists() and any(output.iterdir()):
        raise ValueError("refusing to overwrite existing output: "+str(output))
    output.mkdir(parents=True,exist_ok=True)
    doc=App.newDocument("Hydrofoam_v419_HingeSweep_WIP")
    report={"classification":"WIP_SOLID_SWEEP_ONLY","master_image_verified":False,
            "integrated_control_mechanisms_verified":False,"surfaces":{}}
    V=App.Vector
    for name,p in cfg["surfaces"].items():
        width=finite_positive(p,"span_mm")
        chord=finite_positive(p,"chord_mm")
        thickness=finite_positive(p,"thickness_mm")
        pin_d=finite_positive(p,"pin_diameter_mm")
        clearance=finite_positive(p,"radial_clearance_mm")
        wall=finite_positive(p,"knuckle_wall_mm")
        travel=finite_positive(p,"travel_deg")
        steps=int(p["sweep_samples"])
        if not (width>20 and chord>10 and thickness>1 and .1<=clearance<=1 and
                0<travel<=45 and 31<=steps<=721 and wall>=1):
            raise ValueError(name+": dimensions outside prototype limits")
        origin=p["hinge_origin_airframe_mm"]
        if len(origin)!=3 or not all(math.isfinite(float(x)) for x in origin):
            raise ValueError(name+": invalid origin")
        o=V(*map(float,origin))
        outer=pin_d/2+clearance+wall
        # Five alternating knuckles with axial gaps. Separate printed bodies.
        pitch=width/5
        axial_gap=finite_positive(p,"axial_gap_mm")
        if axial_gap>=pitch/4: raise ValueError("axial gap too large")
        fixed=Part.makeBox(width,chord*.18,thickness,V(0,outer,-thickness/2))
        moving=Part.makeBox(width,chord*.72,thickness,V(0,-outer-chord*.72,-thickness/2))
        for i in range(5):
            start=i*pitch+axial_gap/2
            length=pitch-axial_gap
            sleeve=Part.makeCylinder(outer,length,V(start,0,0),V(1,0,0))
            bore=Part.makeCylinder(pin_d/2+clearance,length+.2,
                                   V(start-.1,0,0),V(1,0,0))
            sleeve=sleeve.cut(bore)
            # Bridge the knuckle to its own leaf; do not bridge the hinge bore.
            if i%2==0:
                bridge=Part.makeBox(length,outer*.35+0.4,thickness,V(start,outer*.75,-thickness/2))
                fixed=fixed.fuse(sleeve).fuse(bridge)
            else:
                bridge=Part.makeBox(length,outer*.35+0.4,thickness,V(start,-outer-.4,-thickness/2))
                moving=moving.fuse(sleeve).fuse(bridge)
        # Bridges overlap both their knuckle and leaf by positive volume.
        # Face-only contacts may create a compound instead of one printable solid.
        fixed=fixed.removeSplitter()
        moving=moving.removeSplitter()
        pin=Part.makeCylinder(pin_d/2,width+2,V(-1,0,0),V(1,0,0))
        if not all(s.isValid() and len(s.Solids)==1 for s in (fixed,moving,pin)):
            raise ValueError(name+": invalid or disconnected printable solid")
        samples=[]
        for j in range(steps):
            angle=-travel+2*travel*j/(steps-1)
            leaf=moving.copy()
            leaf.rotate(V(0,0,0),V(1,0,0),angle)
            overlap=leaf.common(fixed).Volume
            # The pin is deliberately in contact with the bore: measure
            # penetration volume only, not surface contact.
            pin_penetration=leaf.common(pin).Volume
            samples.append({"angle_deg":round(angle,5),
                            "leaf_fixed_overlap_mm3":round(overlap,7),
                            "leaf_pin_overlap_mm3":round(pin_penetration,7)})
        max_overlap=max(r["leaf_fixed_overlap_mm3"] for r in samples)
        max_pin=max(r["leaf_pin_overlap_mm3"] for r in samples)
        report["surfaces"][name]={"max_fixed_overlap_mm3":max_overlap,
            "max_pin_penetration_mm3":max_pin,
            "status":"COUPON_SWEEP_PASS" if max_overlap<1e-5 and max_pin<1e-5 else "COUPON_SWEEP_FAIL",
            "samples":samples,
            "limitations":["No servo mount, horn or rod in this coupon",
                           "No integration with measured airframe",
                           "No print fit, strength or physical actuation test"]}
        for suffix,shape in (("fixed",fixed),("moving",moving),("pin",pin)):
            placed=shape.copy()
            placed.translate(o)
            obj=doc.addObject("PartDesign::Feature",name+"_"+suffix)
            obj.Shape=placed
            Mesh.export([obj],str(output/(name+"_"+suffix+".stl")))
    doc.recompute()
    doc.saveAs(str(output/"v419_hinge_coupons.FCStd"))
    report["all_coupon_sweeps_pass"]=all(
        r["status"]=="COUPON_SWEEP_PASS" for r in report["surfaces"].values())
    (output/"v419_hinge_qa.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("WIP hinge coupons generated; NO FINAL RELEASE")
    return 0 if report["all_coupon_sweeps_pass"] else 2

if __name__=="__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: FreeCADCmd script.py measured_config.json")
    raise SystemExit(run(sys.argv[1]))
