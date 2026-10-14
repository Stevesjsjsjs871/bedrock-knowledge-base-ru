from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SHADER_DIR = ROOT / "docs" / "ru" / "шейдеры"
FENCE_RE = re.compile(r"(?ms)^(?P<fence>`{3,}|~{3,})(?P<lang>[A-Za-z0-9_-]*)[^\n]*\n(?P<body>.*?)(?P=fence)[ \t]*$")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


class ShaderDocumentationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shader_files = sorted(SHADER_DIR.glob("*.md"))
        cls.markdown_files = [ROOT / "README.md", *cls.shader_files]
        cls.repo_files = {
            path.relative_to(ROOT).as_posix()
            for path in ROOT.rglob("*")
            if path.is_file() and ".git" not in path.parts
        }

    def test_shader_section_has_expected_articles(self):
        self.assertGreaterEqual(
            len(self.shader_files), 13,
            "Expected the shader overview and technical articles 00–11.",
        )

    def test_json_fenced_examples_are_valid_json(self):
        checked = 0
        errors = []
        for path in self.markdown_files:
            text = path.read_text(encoding="utf-8")
            for index, match in enumerate(FENCE_RE.finditer(text), start=1):
                if match.group("lang").lower() != "json":
                    continue
                checked += 1
                try:
                    json.loads(match.group("body"))
                except json.JSONDecodeError as exc:
                    errors.append(f"{path.relative_to(ROOT)} block {index}: {exc}")
        self.assertGreater(checked, 0, "No fenced JSON examples were found.")
        self.assertEqual(errors, [], "\n".join(errors))

    def test_local_markdown_links_resolve(self):
        broken = []
        for source in self.markdown_files:
            text = source.read_text(encoding="utf-8")
            for raw_target in LINK_RE.findall(text):
                target = unquote(raw_target.strip().split("#", 1)[0].split("?", 1)[0])
                if not target or target.startswith(("http://", "https://", "mailto:")):
                    continue
                candidate = (source.parent / target).resolve()
                try:
                    relative = candidate.relative_to(ROOT.resolve()).as_posix()
                except ValueError:
                    broken.append(f"{source.relative_to(ROOT)} -> outside repository: {raw_target}")
                    continue
                if relative not in self.repo_files:
                    broken.append(f"{source.relative_to(ROOT)} -> missing: {raw_target}")
        self.assertEqual(broken, [], "\n".join(broken))

    def test_water_documentation_uses_current_official_path(self):
        water_doc = (SHADER_DIR / "09_ВОДА_CUBEMAP_ОТРАЖЕНИЯ.md").read_text(encoding="utf-8")
        self.assertIn("/vibrantvisuals/watercustomization?", water_doc)
        self.assertNotIn("/vibrantvisuals/watereffects?", water_doc)

    def test_texture_sets_are_documented_under_textures(self):
        structure_doc = (SHADER_DIR / "07_СТРУКТУРА_VIBRANT_VISUALS_JSON.md").read_text(encoding="utf-8")
        self.assertIn("stone.texture_set.json", structure_doc)
        self.assertIn("не в универсальном каталоге `pbr/`", structure_doc)

    def test_texture_set_reference_covers_schema_constraints(self):
        reference = (SHADER_DIR / "12_СПРАВОЧНИК_СХЕМЫ_TEXTURE_SET.md").read_text(encoding="utf-8")
        for required_rule in (
            "слой `color`",
            "R (красный)",
            "A (альфа)",
            "нельзя одновременно задавать `normal` и `heightmap`",
            "MER и MERS",
            "только на изображения из того же resource pack",
            "CONTENT_ERROR",
        ):
            with self.subTest(rule=required_rule):
                self.assertIn(required_rule, reference)


if __name__ == "__main__":
    unittest.main()
