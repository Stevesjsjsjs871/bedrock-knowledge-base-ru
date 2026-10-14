from __future__ import annotations
import unittest
from tools.sync_bedrock_samples_releases import normalize_release, render_markdown

class BedrockSamplesReleaseIndexTests(unittest.TestCase):
    def test_normalizes_release_and_archive_links(self):
        release = {
            "tag_name": "v1.26.50.4",
            "name": "Minecraft Bedrock Samples v1.26.50.4",
            "published_at": "2026-09-15T10:00:00Z",
            "prerelease": False,
            "draft": False,
            "html_url": "https://github.com/Mojang/bedrock-samples/releases/tag/v1.26.50.4",
            "assets": [
                {"name": "bedrock-samples-full.zip", "browser_download_url": "https://example.test/full.zip", "size": 123, "download_count": 5},
                {"name": "bedrock-samples-min.zip", "browser_download_url": "https://example.test/min.zip", "size": 45, "download_count": 3},
            ],
        }
        result = normalize_release(release)
        self.assertEqual(result["tag"], "v1.26.50.4")
        self.assertFalse(result["is_prerelease"])
        self.assertEqual(result["assets"]["full"]["url"], "https://example.test/full.zip")
        self.assertEqual(result["assets"]["min"]["size_bytes"], 45)

    def test_markdown_distinguishes_channels_and_missing_assets(self):
        releases = [
            normalize_release({
                "tag_name": "v1.26.50.4", "published_at": "2026-09-15T10:00:00Z",
                "prerelease": False, "draft": False, "html_url": "https://example.test/stable",
                "assets": [{"name": "full.zip", "browser_download_url": "https://example.test/full.zip"}],
            }),
            normalize_release({
                "tag_name": "v1.26.60.28-preview", "published_at": "2026-09-25T10:00:00Z",
                "prerelease": True, "draft": False, "html_url": "https://example.test/preview",
                "assets": [],
            }),
        ]
        markdown = render_markdown(releases, "2026-10-14T00:00:00+00:00")
        self.assertIn("Stable", markdown)
        self.assertIn("Preview", markdown)
        self.assertIn("https://example.test/full.zip", markdown)
        self.assertIn("нет asset", markdown)
        self.assertIn("не полный исходный код игрового движка", markdown)

if __name__ == "__main__":
    unittest.main()
