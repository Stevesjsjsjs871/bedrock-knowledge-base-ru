from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.build_catalog import validate_catalog_rows
from tools.validate_repository import validate_json_files, validate_manifest, validate_packs


def manifest(header_uuid: str, module_uuid: str) -> dict:
    return {
        "format_version": 2,
        "header": {
            "name": "Test Pack",
            "uuid": header_uuid,
            "version": [1, 0, 0],
            "min_engine_version": [1, 21, 0],
        },
        "modules": [
            {"type": "resources", "uuid": module_uuid, "version": [1, 0, 0]}
        ],
    }


class RepositoryIntegrityTests(unittest.TestCase):
    def test_empty_catalog_snapshot_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Refusing to overwrite catalog"):
            validate_catalog_rows([])

    def test_catalog_snapshot_missing_an_upstream_is_rejected(self):
        rows = [{"source": "bedrock-wiki"} for _ in range(120)]
        with self.assertRaisesRegex(ValueError, "minecraft-creator"):
            validate_catalog_rows(rows)

    def test_complete_catalog_snapshot_above_minimum_passes(self):
        rows = (
            [{"source": "bedrock-wiki"} for _ in range(60)]
            + [{"source": "minecraft-creator"} for _ in range(60)]
        )
        validate_catalog_rows(rows)

    def test_repository_json_files_parse(self):
        self.assertEqual(validate_json_files(), [])

    def test_valid_manifest_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "packs" / "sample" / "manifest.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(manifest(
                "a70e1d0c-8c7b-4b45-9c13-6f1f7c7a0a31",
                "6d0bb4a9-2f0a-4c3f-8d21-9e8b6b3f4a72",
            )), encoding="utf-8")
            self.assertEqual(validate_manifest(
                path, root, set()
            ), [])

    def test_duplicate_uuids_in_manifest_fail(self):
        duplicate = "a70e1d0c-8c7b-4b45-9c13-6f1f7c7a0a31"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "packs" / "sample" / "manifest.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(manifest(duplicate, duplicate)), encoding="utf-8")
            errors = validate_manifest(path, root, set())
            self.assertTrue(any("duplicate UUID" in error for error in errors))

    def test_pack_directory_without_manifest_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "packs" / "broken").mkdir(parents=True)
            errors, count = validate_packs(root)
            self.assertEqual(count, 1)
            self.assertTrue(any("missing manifest.json" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
