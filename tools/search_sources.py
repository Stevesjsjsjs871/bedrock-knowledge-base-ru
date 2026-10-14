#!/usr/bin/env python3
"""Search upstream Bedrock documentation by terms, fields, identifiers, and code snippets."""
from __future__ import annotations

import argparse
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
EXTS = {".md", ".mdx", ".yml", ".yaml", ".json", ".js", ".ts"}
SOURCE_LABELS = {
    "bedrock-wiki": "Bedrock Wiki",
    "minecraft-creator": "Microsoft Learn / Minecraft Creator",
    "bedrock-schemas": "Mojang Bedrock Schemas",
}
UPSTREAM = {
    "bedrock-wiki": "https://github.com/Bedrock-OSS/bedrock-wiki/blob/wiki/",
    "minecraft-creator": "https://github.com/MicrosoftDocs/minecraft-creator/blob/main/",
    "bedrock-schemas": "https://github.com/Mojang/bedrock-schemas/blob/main/",
}


def normalize(value: str) -> str:
    return unicodedata.normalize("NFKC", value).casefold()


def tokens(value: str) -> list[str]:
    # Keep Bedrock identifiers and API names such as minecraft:health and @minecraft/server.
    return re.findall(r"[\w@:$./-]+", normalize(value), flags=re.UNICODE)


def title_for(text: str, path: Path) -> str:
    for line in text.splitlines()[:60]:
        heading = re.match(r"^\s*#\s+(.+?)\s*#*\s*$", line)
        if heading:
            return heading.group(1).strip()
        field = re.match(r"^\s*title:\s*[\"']?(.+?)[\"']?\s*$", line, flags=re.I)
        if field:
            return field.group(1).strip()
    return path.stem.replace("_", " ").replace("-", " ")


def source_files(source_filter: str | None = None):
    for source_name in SOURCE_LABELS:
        if source_filter and source_name != source_filter:
            continue
        base = SOURCES / source_name
        if not base.is_dir():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in EXTS and ".git" not in path.parts:
                yield source_name, base, path


def search(query: str, limit: int = 10, source_filter: str | None = None) -> list[dict]:
    query_tokens = list(dict.fromkeys(tokens(query)))
    if not query_tokens:
        return []
    results = []
    for source_name, base, path in source_files(source_filter):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lines = content.splitlines()
        title = title_for(content, path)
        normalized_title = normalize(title)
        normalized_path = normalize(path.as_posix())
        normalized_content = normalize(content)
        present = [term for term in query_tokens if term in normalized_content]
        if not present:
            continue

        title_hits = sum(term in normalized_title for term in query_tokens)
        path_hits = sum(term in normalized_path for term in query_tokens)
        heading_hits = sum(
            1 for line in lines
            if line.lstrip().startswith("#") and any(term in normalize(line) for term in query_tokens)
        )
        # Prefer results containing all query terms, then titles/paths/headings over body-only matches.
        score = len(present) * 10 + title_hits * 12 + path_hits * 8 + min(heading_hits, 5) * 3
        if len(present) == len(query_tokens):
            score += 15

        matching_lines = []
        for index, line in enumerate(lines):
            lower = normalize(line)
            hits = sum(term in lower for term in query_tokens)
            if hits:
                matching_lines.append((hits, index, line.strip()))
        matching_lines.sort(key=lambda item: (-item[0], item[2].startswith("#"), item[1]))
        best = matching_lines[0] if matching_lines else (0, 0, "")
        relative = path.relative_to(base).as_posix()
        url = UPSTREAM[source_name] + relative
        results.append({
            "score": score,
            "source": source_name,
            "source_label": SOURCE_LABELS[source_name],
            "path": relative,
            "title": title,
            "line": best[1] + 1,
            "snippet": best[2][:240],
            "url": url,
            "matched_terms": present,
        })
    results.sort(key=lambda item: (-item["score"], item["source"], item["path"].casefold()))
    return results[:max(1, limit)]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Search local Bedrock Wiki and Microsoft Creator Docs checkouts."
    )
    parser.add_argument("query", nargs="+", help="Words, component ID, JSON field, or API symbol")
    parser.add_argument("--limit", type=int, default=10, help="Maximum results (default: 10)")
    parser.add_argument(
        "--source", choices=sorted(SOURCE_LABELS),
        help="Limit search to one synchronized upstream source",
    )
    args = parser.parse_args()
    query = " ".join(args.query)
    if args.limit < 1:
        parser.error("--limit must be at least 1")
    if not any((SOURCES / name).is_dir() for name in SOURCE_LABELS):
        print("No local sources found. Run: python tools/sync_sources.py", file=sys.stderr)
        return 2

    results = search(query, args.limit, args.source)
    if not results:
        print(f"No matches for: {query}")
        print("Try an exact identifier, a JSON field name, or fewer search terms.")
        return 1

    print(f"Found {len(results)} result(s) for: {query}\n")
    for index, item in enumerate(results, 1):
        print(f"{index}. [{item['source_label']}] {item['title']}")
        print(f"   {item['path']}:{item['line']}  score={item['score']}")
        if item["snippet"]:
            print(f"   {item['snippet']}")
        print(f"   {item['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
