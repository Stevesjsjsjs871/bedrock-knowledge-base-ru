#!/usr/bin/env python3
"""Validate the minimal Bedrock Performance RP manifest without dependencies."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "packs" / "Bedrock-Performance-RP"
MANIFEST = PACK / "manifest.json"
UUID_RE = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if not MANIFEST.is_file():
        fail(f"manifest not found: {MANIFEST.relative_to(ROOT)}")

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid manifest JSON: {exc}")

    if data.get("format_version") != 2:
        fail("expected manifest format_version 2 for the initial compatibility scaffold")

    header = data.get("header")
    modules = data.get("modules")
    if not isinstance(header, dict):
        fail("header must be an object")
    if not isinstance(modules, list) or not modules:
        fail("modules must be a non-empty array")
    if not isinstance(header.get("version"), list) or len(header["version"]) != 3:
        fail("header.version must be a three-number array")

    ids = [("header.uuid", header.get("uuid"))]
    for index, module in enumerate(modules):
        if not isinstance(module, dict):
            fail(f"modules[{index}] must be an object")
        ids.append((f"modules[{index}].uuid", module.get("uuid")))
        if module.get("type") != "resources":
            fail(f"modules[{index}].type must be 'resources'")
        if not isinstance(module.get("version"), list) or len(module["version"]) != 3:
            fail(f"modules[{index}].version must be a three-number array")

    seen: set[str] = set()
    for label, value in ids:
        if not isinstance(value, str) or not UUID_RE.fullmatch(value):
            fail(f"{label} is not a valid UUID string")
        try:
            normalized = str(UUID(value))
        except ValueError:
            fail(f"{label} is not a valid UUID")
        if normalized in seen:
            fail(f"duplicate UUID: {value}")
        seen.add(normalized)

    print("OK: manifest JSON, basic Resource Pack fields, and UUID uniqueness")
    print("NOTE: this does not validate Minecraft's version-specific schema or in-game behavior.")


if __name__ == "__main__":
    main()
