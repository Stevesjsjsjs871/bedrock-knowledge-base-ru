from __future__ import annotations

import json
import re
import unittest
import uuid
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SHADER_DIR = ROOT / "docs" / "ru" / "шейдеры"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "vibrant_visuals_minimal"
FENCE_RE = re.compile(r"(?ms)^(?P<fence>`{3,}|~{3,})(?P<lang>[A-Za-z0-9_-]*)[^\n]*\n(?P<body>.*?)(?P=fence)[ \t]*$")
LINK_RE = re.compile(r"\]\(([^)]+)\)")


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


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
            len(self.shader_files), 12,
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

    def test_fixture_manifest_is_semantically_consistent(self):
        manifest = read_json(FIXTURE_DIR / "manifest.json")
        self.assertEqual(manifest.get("format_version"), 2)
        header = manifest.get("header", {})
        self.assertEqual(header.get("min_engine_version"), [1, 21, 120])
        self.assertIn("pbr", manifest.get("capabilities", []))
        modules = manifest.get("modules", [])
        self.assertTrue(any(module.get("type") == "resources" for module in modules))

        ids = [header.get("uuid"), *(module.get("uuid") for module in modules)]
        parsed = []
        for value in ids:
            self.assertIsInstance(value, str)
            parsed.append(uuid.UUID(value))
        self.assertEqual(len(parsed), len(set(parsed)), "Manifest UUIDs must be unique.")

    def test_fixture_texture_set_obeys_core_schema_constraints(self):
        path = FIXTURE_DIR / "textures" / "blocks" / "stone.texture_set.json"
        texture_set = read_json(path)
        self.assertIn(texture_set.get("format_version"), {"1.16.100", "1.21.30"})
        body = texture_set.get("minecraft:texture_set")
        self.assertIsInstance(body, dict)
        self.assertIn("color", body, "The color layer is required.")

        allowed = {
            "color", "normal", "heightmap",
            "metalness_emissive_roughness",
            "metalness_emissive_roughness_subsurface",
        }
        self.assertEqual(set(body) - allowed, set(), "Unexpected Texture Set properties.")
        self.assertFalse(
            {"normal", "heightmap"}.issubset(body),
            "normal and heightmap are mutually exclusive.",
        )
        self.assertFalse(
            {"metalness_emissive_roughness", "metalness_emissive_roughness_subsurface"}.issubset(body),
            "MER and MERS are mutually exclusive.",
        )
        self.assertIsInstance(body["color"], list)
        self.assertEqual(len(body["color"]), 4)
        self.assertTrue(all(isinstance(x, int) and 0 <= x <= 255 for x in body["color"]))
        if "metalness_emissive_roughness" in body:
            mer = body["metalness_emissive_roughness"]
            self.assertIsInstance(mer, list)
            self.assertEqual(len(mer), 3)
            self.assertTrue(all(isinstance(x, int) and 0 <= x <= 255 for x in mer))


if __name__ == "__main__":
    unittest.main()
