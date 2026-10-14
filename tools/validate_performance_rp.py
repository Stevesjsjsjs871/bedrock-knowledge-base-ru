#!/usr/bin/env python3
"""Strictly validate the initial Bedrock Performance Resource Pack manifest."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "Bedrock-Performance-RP"
MANIFEST = PACK / "manifest.json"


def version_triplet(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 3
        and all(isinstance(part, int) and not isinstance(part, bool) and part >= 0 for part in value)
    )


def validate_manifest_data(data: object) -> list[str]:
    """Return validation errors for manifest data, including malformed JSON roots."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["manifest root must be an object"]
    if data.get("format_version") != 2:
        errors.append("expected manifest format_version 2")

    header = data.get("header")
    modules = data.get("modules")
    if not isinstance(header, dict):
        errors.append("header must be an object")
        header = {}
    if not isinstance(header.get("name"), str) or not header["name"].strip():
        errors.append("header.name must be a non-empty string")
    if not version_triplet(header.get("version")):
        errors.append("header.version must be three non-negative integers")
    if not version_triplet(header.get("min_engine_version")):
        errors.append("header.min_engine_version must be three non-negative integers")
    if not isinstance(modules, list) or not modules:
        errors.append("modules must be a non-empty array")
        modules = []

    identifiers: list[tuple[str, object]] = [("header.uuid", header.get("uuid"))]
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            errors.append(f"modules[{index}] must be an object")
            continue
        identifiers.append((f"modules[{index}].uuid", module.get("uuid")))
        if module.get("type") != "resources":
            errors.append(f"modules[{index}].type must be 'resources'")
        if not version_triplet(module.get("version")):
            errors.append(f"modules[{index}].version must be three non-negative integers")

    seen: set[str] = set()
    for label, value in identifiers:
        if not isinstance(value, str):
            errors.append(f"{label} must be a valid UUID string")
            continue
        try:
            normalized = str(UUID(value))
        except (ValueError, AttributeError):
            errors.append(f"{label} must be a valid UUID string")
            continue
        if normalized in seen:
            errors.append(f"duplicate UUID: {value}")
        seen.add(normalized)

    return errors


def main() -> int:
    if not MANIFEST.is_file():
        print(f"FAIL: manifest not found: {MANIFEST.relative_to(ROOT)}", file=sys.stderr)
        return 1

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"FAIL: invalid manifest JSON: {exc}", file=sys.stderr)
        return 1

    errors = validate_manifest_data(data)
    if errors:
        print("FAIL: Performance RP manifest validation found problems:", file=sys.stderr)
        for error in errors:
            print(f" - {error}", file=sys.stderr)
        return 1

    print("OK: manifest JSON, Resource Pack fields, version arrays, and UUID uniqueness")
    print("NOTE: this does not validate Minecraft's version-specific schema or in-game behavior.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
