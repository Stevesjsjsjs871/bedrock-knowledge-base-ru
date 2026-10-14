import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import search_sources


class SearchSourcesTests(unittest.TestCase):
    def test_tokens_preserve_common_bedrock_identifiers(self):
        values = search_sources.tokens("minecraft:health @minecraft/server world.afterEvents")
        self.assertIn("minecraft:health", values)
        self.assertIn("@minecraft/server", values)
        self.assertIn("world.afterevents", values)

    def test_search_ranks_title_and_reports_line_number(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "minecraft-creator"
            base.mkdir()
            source_file = base / "reference.md"
            source_file.write_text(
                "# minecraft:health component\n\nOverview\n\nUse minecraft:health in entity JSON.\n",
                encoding="utf-8",
            )
            with patch.object(search_sources, "SOURCES", root):
                results = search_sources.search("minecraft:health", limit=5)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "minecraft:health component")
        self.assertEqual(results[0]["line"], 5)
        self.assertIn("minecraft:health", results[0]["snippet"])
        self.assertTrue(results[0]["url"].startswith("https://github.com/MicrosoftDocs/"))

    def test_no_match_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            base = root / "bedrock-wiki"
            base.mkdir()
            (base / "one.md").write_text("# No relation\n", encoding="utf-8")
            with patch.object(search_sources, "SOURCES", root):
                self.assertEqual(search_sources.search("minecraft:health", source_filter="bedrock-wiki"), [])


if __name__ == "__main__":
    unittest.main()
