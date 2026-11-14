"""v382: evidence-backed approval wrapper for v380. Never approves on assertions alone.

Usage: python scripts/v382_evidence_gate.py measurements.json evidence.json
Evidence schema: {"land": {"hard_ground_start_verified": {"path": "...", "sha256": "...", "method": "physical_test"}}, ...}
Each required field needs an independently hashed local evidence file. This gate does not
certify aircraft safety; physical review and photo/hinge gates remain separate.
"""
import hashlib
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("v380", HERE / "v380_three_mode_gate.py")
v380 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v380)
METHODS = {"physical_test", "calibrated_measurement", "cad_measurement", "engineering_review"}
PHYSICAL = {
    "land": {"measured_static_thrust_N", "measured_start_resistance_N", "minimum_observed_foil_clearance_mm",
             "ground_turn_left_verified", "ground_turn_right_verified", "hard_ground_start_verified",
             "grass_start_verified", "firm_sand_start_verified", "skid_wear_acceptable"},
    "water": {"measured_displacement_litres", "waterproof_test_passed", "planing_transition_verified",
              "foil_lift_transition_verified", "stable_water_turns_verified"},
    "air": {"measured_static_thrust_N", "measured_max_current_A",
            "flight_control_authority_verified", "structural_load_test_passed"},
}
def evaluate(measurements, evidence, root):
    screen = v380.evaluate(measurements)
    issues = {}
    root = pathlib.Path(root).resolve()
    for mode, fields in v380.FIELDS.items():
        mode_issues = {}
        for field in fields:
            record = evidence.get(mode, {}).get(field)
            if not isinstance(record, dict):
                mode_issues[field] = "missing_evidence_record"
                continue
            path, digest, method = record.get("path"), record.get("sha256"), record.get("method")
            if not isinstance(path, str) or not isinstance(digest, str) or method not in METHODS:
                mode_issues[field] = "invalid_record"
                continue
            if field in PHYSICAL.get(mode, set()) and method not in {"physical_test", "calibrated_measurement"}:
                mode_issues[field] = "physical_evidence_required"
                continue
            candidate = (root / path).resolve()
            if not candidate.is_relative_to(root) or not candidate.is_file():
                mode_issues[field] = "missing_or_outside_evidence_file"
                continue
            if candidate.stat().st_size > 100_000_000:
                mode_issues[field] = "evidence_file_too_large"
                continue
            actual = hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual.lower() != digest.lower():
                mode_issues[field] = "hash_mismatch"
        issues[mode] = mode_issues
    return {"version": "v382", "screen": screen,
            "evidence_issues": issues,
            "evidence_complete": all(not v for v in issues.values()),
            "status": "REVIEW_REQUIRED",
            "note": "Even complete records do not prove photo fidelity, integrated hinge travel, or safe flight."}

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        root = pathlib.Path(temp)
        (root / "proof.txt").write_text("test", encoding="utf-8")
        digest = hashlib.sha256(b"test").hexdigest()
        record = {"path": "proof.txt", "sha256": digest, "method": "physical_test"}
        data = {"land": {"hard_ground_start_verified": True}}
        result = evaluate(data, {"land": {"hard_ground_start_verified": record}}, root)
        assert "hard_ground_start_verified" not in result["evidence_issues"]["land"]
        assert not result["evidence_complete"]
        record["sha256"] = "0" * 64
        result = evaluate(data, {"land": {"hard_ground_start_verified": record}}, root)
        assert result["evidence_issues"]["land"]["hard_ground_start_verified"] == "hash_mismatch"
        record["sha256"] = digest
        record["method"] = "cad_measurement"
        result = evaluate(data, {"land": {"hard_ground_start_verified": record}}, root)
        assert result["evidence_issues"]["land"]["hard_ground_start_verified"] == "physical_evidence_required"
    print("v382 synthetic evidence regression passed; NO physical approval")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        selftest()
    elif len(sys.argv) == 3:
        source = pathlib.Path(sys.argv[1]).resolve()
        evidence = pathlib.Path(sys.argv[2]).resolve()
        print(json.dumps(evaluate(json.loads(source.read_text(encoding="utf-8")),
                                  json.loads(evidence.read_text(encoding="utf-8")),
                                  evidence.parent), indent=2))
    else:
        raise SystemExit("Usage: v382_evidence_gate.py --selftest | measurements.json evidence.json")
