"""v351: fail-closed build inventory for the Hydrofoam Final Master.

Run from repository root: python scripts/audit_v351_build_inventory.py
This is a repository-level readiness audit, not a model certification.
No master image is modified. No WIP file is promoted to Final.
"""
from pathlib import Path
import hashlib, json, re

ROOT=Path(__file__).resolve().parents[1]
MASTER=ROOT/"reference/FINAL_MASTER_ORIGINAL.jpeg"
EXPECTED="a4d3199bae23965fbd9e3c7f761e8e55e2911e5634889f670fea32a92b7007fd"
def files(pattern):
    return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob(pattern) if p.is_file())
sha=hashlib.sha256(MASTER.read_bytes()).hexdigest() if MASTER.is_file() else None
cad=files("cad/*.blend")+files("cad/*.FCStd")
stls=files("**/*.stl")
renders=files("renders/**/*.png")
scripts=files("scripts/*.py")
checks={
    "original_image_sha256":sha==EXPECTED,
    "cad_source_present":bool(cad),
    "stl_artifacts_present":bool(stls),
    "real_cad_renders_present":bool(renders),
    "three_view_pixel_registration_approved":False,
    "all_control_hinges_installed_and_deflection_approved":False,
    "land_tests_approved":False,
    "water_tests_approved":False,
    "flight_tests_approved":False,
}
report={"version":"v351","accepted":False,"checks":checks,
        "master_sha256":sha,"expected_sha256":EXPECTED,
        "inventory":{"cad":cad,"stl_count":len(stls),"render_count":len(renders),
                     "script_count":len(scripts)},
        "limitations":["File presence does not prove printability, physical integrity or flight safety.",
                       "Image alignment must be documented against the immutable master.",
                       "Physical control deflection and three-mode tests remain mandatory."]}
dest=ROOT/"docs/V351_BUILD_INVENTORY_WIP.json"
dest.parent.mkdir(parents=True,exist_ok=True)
dest.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(dest.relative_to(ROOT),json.dumps(checks,indent=2))
if not checks["original_image_sha256"]:
    raise SystemExit("Master image missing or checksum mismatch")
