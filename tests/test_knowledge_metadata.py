from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "knowledge_record.schema.json"


class KnowledgeMetadataSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def test_schema_is_json_schema_2020_12(self):
        self.assertEqual(
            self.schema.get("$schema"),
            "https://json-schema.org/draft/2020-12/schema",
        )
        self.assertEqual(self.schema.get("type"), "object")

    def test_evidence_levels_are_independent(self):
        evidence = self.schema["properties"]["evidence"]["properties"]
        self.assertEqual(
            set(evidence),
            {"documentation", "source_code", "in_game"},
        )
        self.assertIn("confirmed", evidence["documentation"]["enum"])
        self.assertIn("inspected", evidence["source_code"]["enum"])
        self.assertIn("passed", evidence["in_game"]["properties"]["status"]["enum"])
        self.assertIn("not_tested", evidence["in_game"]["properties"]["status"]["enum"])

    def test_game_test_requires_version_platform_and_date_fields(self):
        in_game = self.schema["properties"]["evidence"]["properties"]["in_game"]
        self.assertEqual(
            set(in_game["required"]),
            {"status", "tested_versions", "platform", "tested_on"},
        )

    def test_completed_game_test_requires_version_platform_and_date(self):
        in_game = self.schema["properties"]["evidence"]["properties"]["in_game"]
        condition = in_game["allOf"][0]
        self.assertEqual(
            set(condition["if"]["properties"]["status"]["enum"]),
            {"passed", "failed", "partial"},
        )
        then_properties = condition["then"]["properties"]
        self.assertEqual(then_properties["tested_versions"]["minItems"], 1)
        self.assertEqual(then_properties["platform"]["type"], "string")
        self.assertEqual(then_properties["tested_on"]["type"], "string")

    def test_each_record_requires_sources_and_limitations(self):
        self.assertIn("sources", self.schema["required"])
        self.assertIn("limitations", self.schema["required"])
        self.assertGreaterEqual(self.schema["properties"]["sources"]["minItems"], 1)


if __name__ == "__main__":
    unittest.main()
