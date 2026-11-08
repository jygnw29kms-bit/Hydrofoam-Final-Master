"""v310 offline-prepared exact vertical ray/triangle mounting survey.

Run on Jens-PC from repository root:
    python scripts/survey_v310_mounting_rays.py

Reads v306 real STL geometry and v307 skid STLs. Does not modify meshes.
Uses vectorized Moller-Trumbore ray intersections without optional rtree/embree.
Results are candidate surface crossings, NOT a structural or watertightness approval.\nThe M3 bore centre is empty by design, so gap estimates use four 2.5 mm\nannular offsets around each bore; this is not a true 3D clearance.
"""
import csv
import json
from pathlib import Path
import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "V310_MOUNTING_RAY_SURVEY.json"
CSV = ROOT / "docs" / "V310_MOUNTING_RAY_SURVEY.csv"
EPS = 1e-8

def vertical_hits(mesh, x, y):
    """All triangle crossings of vertical ray from z=-1000 mm, deduplicated."""
    tri = np.asarray(mesh.triangles, dtype=np.float64)
    origin = np.array([x, y, -1000.0])
    direction = np.array([0.0, 0.0, 1.0])
    e1 = tri[:, 1] - tri[:, 0]
    e2 = tri[:, 2] - tri[:, 0]
    h = np.cross(np.broadcast_to(direction, e2.shape), e2)
    a = np.einsum("ij,ij->i", e1, h)
    valid = np.abs(a) > EPS
    inv = np.zeros_like(a)
    inv[valid] = 1.0 / a[valid]
    s = origin - tri[:, 0]
    u = inv * np.einsum("ij,ij->i", s, h)
    q = np.cross(s, e1)
    v = inv * np.einsum("ij,j->i", q, direction)
    t = inv * np.einsum("ij,ij->i", e2, q)
    mask = valid & (u >= -EPS) & (v >= -EPS) & (u + v <= 1 + EPS) & (t >= 0)
    values = sorted(float(z) for z in (origin[2] + t[mask]))
    distinct = []
    for z in values:
        if not distinct or abs(z - distinct[-1]) > 1e-4:
            distinct.append(z)
    return distinct

def main():
    rows = []
    for side in ("left", "right"):
        cy = -119.0 if side == "left" else 119.0
        for half, xa, xb in (("front", -135.0, -14.0), ("rear", -6.0, 135.0)):
            hull_path = ROOT / "print" / "v306_faceted_float_modules" / f"float_{side}_{half}.stl"
            skid_path = ROOT / "print" / "v307_land_skid_prototypes" / f"land_skid_{side}_{half}.stl"
            hull = trimesh.load_mesh(hull_path, force="mesh")
            skid = trimesh.load_mesh(skid_path, force="mesh")
            for index, x in enumerate((xa + 15, xb - 15), start=1):
                hull_z = vertical_hits(hull, x, cy)
                # The screw axis passes through the 3.3 mm clearance bore.
                # Therefore the skid has NO surface crossing at its exact centre.
                # Probe an annulus outside the bore rather than fabricating a gap.
                offsets = ((2.5, 0), (-2.5, 0), (0, 2.5), (0, -2.5))
                probes = []
                for dx, dy in offsets:
                    hz = vertical_hits(hull, x + dx, cy + dy)
                    sz = vertical_hits(skid, x + dx, cy + dy)
                    probes.append(dict(dx_mm=dx, dy_mm=dy,
                        hull_crossings_z_mm=hz, skid_crossings_z_mm=sz,
                        gap_mm=(min(hz) - max(sz)) if hz and sz else None))
                gaps = [p["gap_mm"] for p in probes if p["gap_mm"] is not None]
                underside = min((min(p["hull_crossings_z_mm"]) for p in probes if p["hull_crossings_z_mm"]), default=None)
                top = max((max(p["skid_crossings_z_mm"]) for p in probes if p["skid_crossings_z_mm"]), default=None)
                gap = min(gaps) if gaps else None
                skid_z = vertical_hits(skid, x, cy)
                rows.append(dict(side=side, half=half, hole=index, x_mm=x, y_mm=cy,
                    hull_crossings_z_mm=hull_z, skid_crossings_z_mm=skid_z,
                    hull_bottom_z_mm=underside, skid_top_z_mm=top,
                    vertical_gap_mm=gap, annulus_probes=probes,
                    valid_annulus_probe_count=len(gaps),
                    bore_axis_skid_crossings_expected_zero=(len(skid_z) == 0),
                    ray_crossings_even=(len(hull_z) % 2 == 0),
                    needs_engineering_review=True))
    OUT.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    with CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "side","half","hole","x_mm","y_mm","hull_bottom_z_mm",
            "skid_top_z_mm","vertical_gap_mm","valid_annulus_probe_count",
            "bore_axis_skid_crossings_expected_zero","ray_crossings_even",
            "needs_engineering_review"])
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row[key] for key in writer.fieldnames})
    assert len(rows) == 8
    assert all(row["valid_annulus_probe_count"] > 0 for row in rows), "Missing surface probes; inspect geometry and screw coordinates"
    for row in rows:
        print(row["side"], row["half"], row["hole"], "vertical gap mm:",
              row["vertical_gap_mm"], "hull crossings:", len(row["hull_crossings_z_mm"]))
    print("V310 survey complete; NOT a mechanical approval.")

if __name__ == "__main__":
    main()
