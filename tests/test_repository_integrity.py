from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote

from tools.build_catalog import render_catalog_index, render_source_catalog, validate_catalog_rows
from tools.validate_repository import validate_json_files, validate_manifest, validate_packs
from tools.validate_performance_rp import validate_manifest_data

ROOT = Path(__file__).resolve().parents[1]


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
    def test_source_catalog_renders_entries(self):
        rows = [{
            "source": "bedrock-wiki",
            "path": "guide/example.md",
            "title": "Example guide",
            "url": "https://example.test/guide/example.md",
        }]
        rendered = render_source_catalog("bedrock-wiki", rows)
        self.assertIn("# Каталог исходных страниц: Bedrock Wiki", rendered)
        self.assertIn("[Example guide](https://example.test/guide/example.md)", rendered)

    def test_catalog_index_links_to_each_source_catalog(self):
        rows = [
            {"source": "bedrock-wiki"},
            {"source": "minecraft-creator"},
            {"source": "minecraft-creator"},
        ]
        rendered = render_catalog_index(rows)
        self.assertIn("каталоги/КАТАЛОГ_BEDROCK_WIKI.md", rendered)
        self.assertIn("каталоги/КАТАЛОГ_MICROSOFT_CREATOR.md", rendered)
        self.assertIn("Всего страниц: **3**", rendered)

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

    def test_authored_markdown_local_links_resolve(self):
        generated = {
            "КАТАЛОГ_СТАТЕЙ.md",
            "ПОВТОРЫ_И_СВЯЗИ.md",
            "РЕЕСТР_КОМПОНЕНТОВ_СУЩНОСТЕЙ.md",
        }
        markdown_files = sorted(
            path for path in ROOT.rglob("*.md")
            if not any(part in {".git", ".venv", "__pycache__", "sources"} for part in path.relative_to(ROOT).parts)
            and path.name not in generated
        )
        repo_files = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and not any(part in {".git", ".venv", "__pycache__", "sources"} for part in path.relative_to(ROOT).parts)
        }
        link_pattern = re.compile(r"\]\(([^)]+)\)")
        broken = []
        for source in markdown_files:
            text = source.read_text(encoding="utf-8")
            for raw_target in link_pattern.findall(text):
                target = unquote(raw_target.strip().split("#", 1)[0].split("?", 1)[0])
                if not target or target.startswith(("http://", "https://", "mailto:", "tel:")):
                    continue
                candidate = (source.parent / target).resolve()
                try:
                    relative = candidate.relative_to(ROOT.resolve()).as_posix()
                except ValueError:
                    broken.append(f"{source.relative_to(ROOT)} -> outside repository: {raw_target}")
                    continue
                if relative not in repo_files:
                    broken.append(f"{source.relative_to(ROOT)} -> missing: {raw_target}")
        self.assertEqual(broken, [], "\n".join(broken))

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


    def test_performance_rp_manifest_validator_accepts_valid_manifest(self):
        data = manifest(
            "a70e1d0c-8c7b-4b45-9c13-6f1f7c7a0a31",
            "6d0bb4a9-2f0a-4c3f-8d21-9e8b6b3f4a72",
        )
        self.assertEqual(validate_manifest_data(data), [])

    def test_performance_rp_manifest_validator_rejects_non_object_root(self):
        self.assertEqual(
            validate_manifest_data([]),
            ["manifest root must be an object"],
        )

    def test_performance_rp_manifest_validator_rejects_boolean_version_parts(self):
        data = manifest(
            "a70e1d0c-8c7b-4b45-9c13-6f1f7c7a0a31",
            "6d0bb4a9-2f0a-4c3f-8d21-9e8b6b3f4a72",
        )
        data["header"]["version"] = [True, 0, 0]
        errors = validate_manifest_data(data)
        self.assertTrue(any("header.version" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
