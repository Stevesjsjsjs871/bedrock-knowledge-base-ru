#!/usr/bin/env python3
"""Refresh a lightweight index of official Mojang Bedrock Samples release archives."""
from __future__ import annotations
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
API = "https://api.github.com/repos/Mojang/bedrock-samples/releases?per_page=100&page={page}"
JSON_OUT = ROOT / "data" / "bedrock_samples_releases.json"
MD_OUT = ROOT / "docs" / "ru" / "справочник" / "КАТАЛОГ_BEDROCK_SAMPLES_ПО_ВЕРСИЯМ.md"
REPO_URL = "https://github.com/Mojang/bedrock-samples"
RELEASES_URL = REPO_URL + "/releases"

def fetch_releases() -> list[dict[str, Any]]:
    releases = []
    page = 1
    while True:
        request = urllib.request.Request(API.format(page=page), headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "bedrock-knowledge-base-ru-release-index",
        })
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
        if not isinstance(batch, list):
            raise ValueError(f"Unexpected GitHub API response on page {page}")
        releases.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return releases

def normalize_release(release: dict[str, Any]) -> dict[str, Any]:
    assets = release.get("assets") or []
    links = {"full": None, "min": None}
    for asset in assets:
        name = str(asset.get("name", ""))
        lower = name.lower()
        kind = "full" if "full" in lower else "min" if "min" in lower else None
        if kind:
            links[kind] = {
                "name": name,
                "url": asset.get("browser_download_url"),
                "size_bytes": asset.get("size"),
                "download_count": asset.get("download_count"),
            }
    return {
        "tag": release.get("tag_name", ""),
        "name": release.get("name") or release.get("tag_name", ""),
        "published_at": release.get("published_at"),
        "is_prerelease": bool(release.get("prerelease")),
        "is_draft": bool(release.get("draft")),
        "html_url": release.get("html_url"),
        "assets": links,
    }

def render_markdown(releases: list[dict[str, Any]], generated_at: str) -> str:
    lines = [
        "# Официальные ZIP-архивы Mojang Bedrock Samples по версиям",
        "",
        f"> Индекс создан автоматически: {generated_at}. Это каталог официальных релизов, а не зеркало ZIP-файлов.",
        "",
        "Источник: [Mojang/bedrock-samples — Releases](" + RELEASES_URL + "). Репозиторий содержит образцы ресурсов и контента Bedrock, а не полный исходный код игрового движка.",
        "",
        "## Какой архив выбрать",
        "",
        "- **full** — полный набор образцов, включая текстуры, модели, звуки и другие бинарные ресурсы; занимает больше места.",
        "- **min** — текстовые образцы (JSON, HTML, Markdown), бинарные файлы исключены; удобен для поиска изменений в схемах и конфигурациях.",
        "- **Stable** — релиз основной версии; **Preview** — предварительная сборка. Не смешивайте их при сравнении.",
        "- ZIP-файлы скачиваются напрямую с GitHub Releases Mojang. Этот репозиторий хранит только индекс и ссылки, не копии архивов.",
        "",
        "## Каталог релизов",
        "",
        "| Версия / tag | Канал | Дата публикации | Full ZIP | Min ZIP | Релиз |",
        "|---|---|---|---|---|---|",
    ]
    for item in releases:
        if item["is_draft"]:
            continue
        channel = "Preview" if item["is_prerelease"] else "Stable"
        date = (item.get("published_at") or "")[:10] or "—"
        full = item["assets"]["full"]
        mini = item["assets"]["min"]
        full_link = f"[ZIP]({full['url']})" if full and full.get("url") else "нет asset"
        min_link = f"[ZIP]({mini['url']})" if mini and mini.get("url") else "нет asset"
        release_link = f"[GitHub]({item['html_url']})" if item.get("html_url") else "—"
        lines.append(f"| [{item['tag']}]({item['html_url']}) | {channel} | {date} | {full_link} | {min_link} | {release_link} |")
    lines.extend([
        "",
        "## Методика сравнения версий",
        "",
        "1. Сначала сравнивайте min ZIP для JSON и текстовых конфигураций; скачивайте full, когда анализ требует текстур, моделей или звуков.",
        "2. Записывайте точный tag релиза и канал (Stable/Preview), а не только номер 26.x.",
        "3. Для каждого изменения сохраняйте путь файла, старую и новую версию, diff, официальный changelog и статус проверки.",
        "4. Отсутствие файла в min архиве не означает, что его нет в полной версии: бинарные файлы там намеренно исключены.",
        "5. Примеры из vanilla samples показывают структуру и ожидаемые ресурсы, но не заменяют документацию схем и не доказывают поддержку конкретного графического эффекта.",
        "",
        "## Лицензии и ограничения",
        "",
        "Перед копированием или перепубликацией ресурсов проверяйте [LICENSE.md в Mojang/bedrock-samples](" + REPO_URL + "/blob/main/LICENSE.md) и уведомления для конкретного файла. Предпочитайте ссылки и собственные diff-анализы вместо повторного размещения полного содержимого архивов.",
        "",
        "Индекс обновляется workflow GitHub Actions вручную или по расписанию. Если GitHub API недоступен, скрипт завершается ошибкой и не заменяет актуальный каталог пустым.",
        "",
    ])
    return "\n".join(lines)

def main() -> None:
    releases = fetch_releases()
    normalized = [normalize_release(release) for release in releases]
    normalized = [item for item in normalized if item["tag"] and not item["is_draft"]]
    if not normalized:
        raise RuntimeError("GitHub API returned no published releases; refusing to overwrite the index.")
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUT.write_text(json.dumps({
        "source": REPO_URL,
        "generated_at": generated_at,
        "releases": normalized,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    MD_OUT.write_text(render_markdown(normalized, generated_at), encoding="utf-8")
    print(f"Indexed {len(normalized)} published releases.")
    print(f"Wrote {JSON_OUT.relative_to(ROOT)} and {MD_OUT.relative_to(ROOT)}.")

if __name__ == "__main__":
    try:
        main()
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError, RuntimeError) as exc:
        print(f"Could not refresh Mojang Bedrock Samples index: {exc}", file=sys.stderr)
        raise SystemExit(1)
