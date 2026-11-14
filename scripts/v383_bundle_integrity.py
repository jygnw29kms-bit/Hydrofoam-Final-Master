"""v383: immutable evidence-bundle binding for the three-mode gate.

Binds the exact measurements JSON and evidence index JSON to a manifest.
A manifest is NOT an engineering approval. Run v382 separately.
Usage: python scripts/v383_bundle_integrity.py manifest.json [--selftest]
"""
import hashlib
import json
import pathlib
import sys

MAX_BYTES = 100_000_000
REQUIRED = ("measurements", "evidence_index")

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def verify(manifest_path):
    manifest_path = pathlib.Path(manifest_path).resolve()
    root = manifest_path.parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    issues = {}
    if manifest.get("schema") != "hydrofoam-evidence-bundle-v1":
        issues["schema"] = "invalid_schema"
    paths = set()
    for key in REQUIRED:
        record = manifest.get(key)
        if not isinstance(record, dict):
            issues[key] = "missing_record"
            continue
        name, sha = record.get("path"), record.get("sha256")
        if not isinstance(name, str) or not isinstance(sha, str) or len(sha) != 64:
            issues[key] = "invalid_record"
            continue
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            issues[key] = "missing_or_outside_file"
            continue
        if path == manifest_path or path in paths:
            issues[key] = "duplicate_or_self_reference"
            continue
        paths.add(path)
        if path.stat().st_size > MAX_BYTES:
            issues[key] = "oversized"
            continue
        if digest(path).lower() != sha.lower():
            issues[key] = "hash_mismatch"
            continue
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                issues[key] = "json_object_required"
        except (UnicodeError, json.JSONDecodeError):
            issues[key] = "invalid_json"
    return {"version": "v383", "integrity_pass": not issues, "issues": issues,
            "approval": "NOT_GRANTED", "note": "Integrity is not provenance, test validity, photogrammetry, hinge clearance, or flight safety."}

def selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = pathlib.Path(tmp)
        a, b = root / "measurements.json", root / "evidence.json"
        a.write_text('{"land":{}}', encoding="utf-8")
        b.write_text('{"land":{}}', encoding="utf-8")
        manifest = root / "manifest.json"
        def write_manifest(a_sha=None):
            manifest.write_text(json.dumps({
                "schema": "hydrofoam-evidence-bundle-v1",
                "measurements": {"path": a.name, "sha256": a_sha or digest(a)},
                "evidence_index": {"path": b.name, "sha256": digest(b)}
            }), encoding="utf-8")
        write_manifest()
        assert verify(manifest)["integrity_pass"]
        a.write_text('{"land":{"fake":true}}', encoding="utf-8")
        assert verify(manifest)["issues"]["measurements"] == "hash_mismatch"
        write_manifest()
        assert verify(manifest)["integrity_pass"]
        manifest_data = json.loads(manifest.read_text())
        manifest_data["evidence_index"]["path"] = "../outside.json"
        manifest.write_text(json.dumps(manifest_data))
        assert verify(manifest)["issues"]["evidence_index"] == "missing_or_outside_file"
    print("v383 synthetic integrity tests passed; NO physical approval")

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        selftest()
    elif len(sys.argv) == 2:
        print(json.dumps(verify(sys.argv[1]), indent=2))
    else:
        raise SystemExit("Usage: v383_bundle_integrity.py --selftest | manifest.json")
