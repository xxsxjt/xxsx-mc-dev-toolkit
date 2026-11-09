#!/usr/bin/env python3
"""Validate a Minecraft creature package manifest and hashes without executing assets."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_CLASSES = {"npc", "mob", "elite", "boss"}
VALID_ORIGINS = {"original", "user-provided", "third-party"}
VALID_TRI_STATE = {"yes", "no", "unknown"}


def issue(bucket: list[dict], code: str, message: str, path: str = "") -> None:
    bucket.append({"code": code, "path": path, "message": message})


def validate(manifest_path: Path, package_root: Path) -> dict:
    errors: list[dict] = []
    warnings: list[dict] = []
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"valid": False, "errors": [{"code": "manifest-json", "path": str(manifest_path), "message": str(exc)}], "warnings": []}

    if not isinstance(data, dict):
        issue(errors, "manifest-type", "Manifest root must be an object")
        return {"valid": False, "errors": errors, "warnings": warnings}

    creature = data.get("creature")
    if not isinstance(creature, dict):
        issue(errors, "creature-missing", "Missing creature object", "creature")
    else:
        if not creature.get("id"):
            issue(errors, "creature-id", "Creature id is required", "creature.id")
        if creature.get("class") not in VALID_CLASSES:
            issue(errors, "creature-class", "Creature class must be npc, mob, elite, or boss", "creature.class")
        if creature.get("edition") not in {"java", "bedrock", "both"}:
            issue(errors, "edition", "Edition must be java, bedrock, or both", "creature.edition")
        for field in ("minecraft_version", "model_target"):
            if not creature.get(field):
                issue(errors, "creature-field", f"Missing {field}", f"creature.{field}")

    files = data.get("files")
    if not isinstance(files, list) or not files:
        issue(errors, "files-missing", "Manifest must contain a non-empty files array", "files")
        files = []

    for index, entry in enumerate(files):
        prefix = f"files[{index}]"
        if not isinstance(entry, dict):
            issue(errors, "file-entry", "File entry must be an object", prefix)
            continue
        relative = entry.get("path")
        if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            issue(errors, "file-path", "File path must be a non-empty relative path without ..", f"{prefix}.path")
            continue
        target = package_root / relative
        if not target.is_file():
            issue(errors, "file-missing", "Manifest file does not exist", relative)
            continue
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest.lower()):
            issue(errors, "sha256-format", "sha256 must be 64 lowercase hexadecimal characters", f"{prefix}.sha256")
        else:
            actual = hashlib.sha256(target.read_bytes()).hexdigest()
            if actual != digest.lower():
                issue(errors, "sha256-mismatch", f"Expected {digest.lower()}, got {actual}", relative)
        if entry.get("bytes") != target.stat().st_size:
            issue(errors, "byte-count", "Manifest byte count does not match file", relative)

        source = entry.get("source")
        if not isinstance(source, dict):
            issue(errors, "source-missing", "Every file needs a source record", f"{prefix}.source")
            continue
        origin = source.get("origin")
        if origin not in VALID_ORIGINS:
            issue(errors, "origin", "origin must be original, user-provided, or third-party", f"{prefix}.source.origin")
        if origin == "third-party":
            for field in ("source_url", "license_evidence_url", "checked_at"):
                if not source.get(field):
                    issue(errors, "third-party-evidence", f"Third-party source requires {field}", f"{prefix}.source.{field}")
            if source.get("license_id") in {None, "", "NOASSERTION"}:
                issue(errors, "third-party-license", "Third-party source cannot use an unasserted license", f"{prefix}.source.license_id")
        rights = source.get("rights")
        if not isinstance(rights, dict):
            issue(errors, "rights-missing", "Rights must state commercial use, modification, and redistribution", f"{prefix}.source.rights")
        else:
            for field in ("commercial_use", "modify", "redistribute"):
                if rights.get(field) not in VALID_TRI_STATE:
                    issue(errors, "rights-value", f"{field} must be yes, no, or unknown", f"{prefix}.source.rights.{field}")
                elif origin == "third-party" and rights.get(field) != "yes":
                    issue(errors, "third-party-rights", f"Third-party reusable package requires {field}=yes", f"{prefix}.source.rights.{field}")
        if source.get("attribution_required") not in VALID_TRI_STATE:
            issue(errors, "attribution-value", "attribution_required must be yes, no, or unknown", f"{prefix}.source.attribution_required")
        if source.get("notice_required") not in VALID_TRI_STATE:
            issue(errors, "notice-value", "notice_required must be yes, no, or unknown", f"{prefix}.source.notice_required")

        transform = entry.get("transform")
        if not isinstance(transform, dict) or not transform.get("status"):
            issue(errors, "transform-missing", "Every file needs a transformation/status record", f"{prefix}.transform")
        elif transform.get("status") == "runtime_validated" and data.get("checks", {}).get("runtime_render") != "passed":
            issue(warnings, "runtime-claim", "File status says runtime_validated but package runtime_render is not passed", relative)

    checks = data.get("checks")
    if not isinstance(checks, dict):
        issue(warnings, "checks-missing", "No package-level checks were recorded", "checks")
    else:
        for name in ("preview", "target_load", "runtime_render"):
            if checks.get(name) in {None, "", "unconfirmed"}:
                issue(warnings, "check-unconfirmed", f"Package check is not confirmed: {name}", f"checks.{name}")

    return {"valid": not errors, "errors": errors, "warnings": warnings, "file_count": len(files)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("package", type=Path, help="Creature package root")
    parser.add_argument("--manifest", type=Path, default=None, help="Manifest path; defaults to package/creature-manifest.json")
    parser.add_argument("--report", type=Path, default=None, help="Write JSON report to this path")
    args = parser.parse_args()
    package_root = args.package.resolve()
    manifest_path = (args.manifest or package_root / "creature-manifest.json").resolve()
    result = validate(manifest_path, package_root)
    result["package"] = str(package_root)
    result["manifest"] = str(manifest_path)
    rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
