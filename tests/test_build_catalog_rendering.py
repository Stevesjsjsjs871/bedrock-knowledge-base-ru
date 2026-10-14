import unittest

from tools import build_catalog


class CatalogRenderingTests(unittest.TestCase):
    def test_source_catalog_uses_real_line_breaks(self):
        content = build_catalog.render_source_catalog(
            "bedrock-wiki",
            [{
                "title": "Example",
                "url": "https://example.invalid/example.md",
                "source": "bedrock-wiki",
                "path": "example.md",
            }],
        )
        self.assertIn("\n- [Example]", content)
        self.assertNotIn("\\n", content)

    def test_catalog_index_uses_real_line_breaks(self):
        content = build_catalog.render_catalog_index([
            {"source": "bedrock-wiki"},
            {"source": "minecraft-creator"},
        ])
        self.assertIn("\n## Разделы\n", content)
        self.assertNotIn("\\n", content)


if __name__ == "__main__":
    unittest.main()
