from __future__ import annotations

import json
import unittest
from datetime import date
from urllib.parse import urlparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "data" / "knowledge_record.schema.json"
RECORDS_PATH = ROOT / "data" / "knowledge_records.json"


class KnowledgeMetadataSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.records = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))["records"]

    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        cls.records = json.loads(RECORDS_PATH.read_text(encoding="utf-8"))["records"]

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


    def test_seed_records_have_required_fields_and_existing_documents(self):
        self.assertGreaterEqual(len(self.records), 1)
        required = {"document", "claim", "evidence", "sources", "limitations"}
        for record in self.records:
            with self.subTest(document=record.get("document")):
                self.assertTrue(required.issubset(record))
                self.assertTrue((ROOT / record["document"]).is_file())
                self.assertTrue(record["claim"].strip())
                self.assertIsInstance(record["limitations"], list)
                self.assertGreaterEqual(len(record["sources"]), 1)
                if record.get("last_reviewed") is not None:
                    date.fromisoformat(record["last_reviewed"])

    def test_seed_record_statuses_and_source_urls_are_valid(self):
        documentation_statuses = {"not_checked", "confirmed", "contradicted", "not_applicable"}
        source_statuses = {"not_checked", "inspected", "contradicted", "not_applicable"}
        game_statuses = {"not_tested", "passed", "failed", "partial", "not_applicable"}
        source_kinds = {"official_docs", "upstream_code", "community", "experiment"}
        for record in self.records:
            with self.subTest(document=record.get("document")):
                evidence = record["evidence"]
                self.assertIn(evidence["documentation"], documentation_statuses)
                self.assertIn(evidence["source_code"], source_statuses)
                game = evidence["in_game"]
                self.assertIn(game["status"], game_statuses)
                if game["status"] in {"passed", "failed", "partial"}:
                    self.assertGreaterEqual(len(game["tested_versions"]), 1)
                    self.assertTrue(game["platform"])
                    date.fromisoformat(game["tested_on"])
                for source in record["sources"]:
                    self.assertIn(source["kind"], source_kinds)
                    parsed = urlparse(source["url"])
                    self.assertIn(parsed.scheme, {"http", "https"})
                    self.assertTrue(parsed.netloc)
                    if source.get("checked_on") is not None:
                        date.fromisoformat(source["checked_on"])

    def test_seed_records_do_not_claim_unperformed_game_tests(self):
        by_document = {record["document"]: record for record in self.records}
        pack_record = by_document["packs/Bedrock-Performance-RP/README.md"]
        self.assertEqual(pack_record["evidence"]["in_game"]["status"], "not_tested")
        self.assertEqual(pack_record["evidence"]["in_game"]["tested_versions"], [])
        analysis_record = by_document["docs/ru/разборы/АНАЛИЗ_FPS_BOOSTER_И_LITHIUM.md"]
        self.assertEqual(analysis_record["evidence"]["in_game"]["status"], "not_tested")


if __name__ == "__main__":
    unittest.main()
