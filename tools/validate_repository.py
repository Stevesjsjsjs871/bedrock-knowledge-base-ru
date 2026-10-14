#!/usr/bin/env python3
"""Validate repository JSON files and basic manifests for owned Bedrock packs.

This is a structural guard, not a replacement for version-specific schemas or
loading the pack in Minecraft.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED_DIRS = {".git", ".venv", "__pycache__", "sources"}


def json_files(root: Path = ROOT) -> list[Path]:
    return sorted(
        path for path in root.rglob("*.json")
        if not any(part in EXCLUDED_DIRS for part in path.relative_to(root).parts)
    )


def validate_json_files(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    for path in json_files(root):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return errors


def version_triplet(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(part, int) and not isinstance(part, bool) and part >= 0 for part in value)
    )


def validate_manifest(path: Path, root: Path, seen_uuids: set[str]) -> list[str]:
    errors: list[str] = []
    relative = path.relative_to(root)
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"{relative}: cannot parse manifest: {exc}"]

    if not isinstance(manifest, dict):
        return [f"{relative}: manifest root must be an object"]
    if manifest.get("format_version") != 2:
        errors.append(f"{relative}: expected manifest format_version 2")

    header = manifest.get("header")
    modules = manifest.get("modules")
    if not isinstance(header, dict):
        errors.append(f"{relative}: header must be an object")
        header = {}
    if not isinstance(header.get("name"), str) or not header["name"].strip():
        errors.append(f"{relative}: header.name must be a non-empty string")
    if not version_triplet(header.get("version")):
        errors.append(f"{relative}: header.version must be three non-negative integers")
    if not version_triplet(header.get("min_engine_version")):
        errors.append(f"{relative}: header.min_engine_version must be three non-negative integers")
    if not isinstance(modules, list) or not modules:
        errors.append(f"{relative}: modules must be a non-empty array")
        modules = []

    identifiers: list[tuple[str, object]] = [("header.uuid", header.get("uuid"))]
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            errors.append(f"{relative}: modules[{index}] must be an object")
            continue
        identifiers.append((f"modules[{index}].uuid", module.get("uuid")))
        if module.get("type") not in {"resources", "data", "client_data", "interface", "script", "world_template"}:
            errors.append(f"{relative}: modules[{index}].type is missing or unsupported")
        if not version_triplet(module.get("version")):
            errors.append(f"{relative}: modules[{index}].version must be three non-negative integers")

    local_seen: set[str] = set()
    for label, value in identifiers:
        try:
            normalized = str(UUID(value)) if isinstance(value, str) else ""
        except (ValueError, AttributeError):
            normalized = ""
        if not normalized:
            errors.append(f"{relative}: {label} must be a valid UUID")
            continue
        if normalized in local_seen:
            errors.append(f"{relative}: duplicate UUID inside manifest: {value}")
        if normalized in seen_uuids:
            errors.append(f"{relative}: UUID is already used by another pack: {value}")
        local_seen.add(normalized)
        seen_uuids.add(normalized)

    return errors


def validate_packs(root: Path = ROOT) -> tuple[list[str], int]:
    packs_dir = root / "packs"
    if not packs_dir.is_dir():
        return [], 0

    errors: list[str] = []
    pack_dirs = sorted(path for path in packs_dir.iterdir() if path.is_dir())
    seen_uuids: set[str] = set()
    for pack_dir in pack_dirs:
        manifest = pack_dir / "manifest.json"
        if not manifest.is_file():
            errors.append(f"{manifest.relative_to(root)}: missing manifest.json")
            continue
        errors.extend(validate_manifest(manifest, root, seen_uuids))
    return errors, len(pack_dirs)


def main() -> int:
    json_errors = validate_json_files()
    pack_errors, pack_count = validate_packs()
    errors = json_errors + pack_errors
    if errors:
        print("FAIL: repository validation found problems:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print(f"OK: parsed {len(json_files())} repository JSON files.")
    if pack_count:
        print(f"OK: validated manifests for {pack_count} pack directories.")
    else:
        print("NOTE: no packs/ directory found; pack-manifest checks will run when packs are added.")
    print("NOTE: structural validation does not prove version-specific compatibility or in-game behavior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
