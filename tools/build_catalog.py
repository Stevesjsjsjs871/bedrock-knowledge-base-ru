#!/usr/bin/env python3
"""Build compact source catalogs and a duplicate-candidate report."""
from pathlib import Path
import hashlib
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
OUT = ROOT / "docs" / "ru"
CATALOG_DIR = OUT / "каталоги"
EXTS = {".md", ".mdx", ".yml", ".yaml"}
MIN_CATALOG_ROWS = 100
UPSTREAM = {
    "bedrock-wiki": "https://github.com/Bedrock-OSS/bedrock-wiki/blob/wiki/",
    "minecraft-creator": "https://github.com/MicrosoftDocs/minecraft-creator/blob/main/",
}
SOURCE_LABELS = {
    "bedrock-wiki": "Bedrock Wiki",
    "minecraft-creator": "Microsoft Learn / Minecraft Creator",
}
SOURCE_CATALOG_FILES = {
    "bedrock-wiki": "КАТАЛОГ_BEDROCK_WIKI.md",
    "minecraft-creator": "КАТАЛОГ_MICROSOFT_CREATOR.md",
}


def title(text, path):
    # YAML navigation metadata often contains a generic "# section" heading.
    # Prefer an explicit title field for YAML; use the directory name for section files.
    if path.suffix.lower() in {".yml", ".yaml"}:
        for line in text.splitlines()[:80]:
            if line.lstrip().lower().startswith("title:"):
                value = line.split(":", 1)[1].strip().strip("\\\"' ")
                if value:
                    return value
        if path.stem.lower() == "section":
            return f"{path.parent.name} — раздел навигации"
    for line in text.splitlines()[:50]:
        match = re.match(r"^\s*#\s+(.+?)\s*#*\s*$", line)
        if match and match.group(1).strip().lower() not in {"section", "overview"}:
            return match.group(1)
    return path.stem.replace("_", " ").replace("-", " ")


def norm(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"```.*?```|`[^`]*`", " ", text, flags=re.S)
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"[^\w]+", " ", text).strip()


def validate_catalog_rows(rows):
    """Refuse to replace generated catalogs with incomplete/empty source snapshots."""
    if len(rows) < MIN_CATALOG_ROWS:
        raise ValueError(
            f"Refusing to overwrite catalog: found only {len(rows)} source files; "
            f"expected at least {MIN_CATALOG_ROWS}."
        )
    found_sources = {row["source"] for row in rows}
    missing_sources = set(UPSTREAM) - found_sources
    if missing_sources:
        raise ValueError(
            "Refusing to overwrite catalog: no files found for source(s): "
            + ", ".join(sorted(missing_sources))
        )


def render_source_catalog(source, rows):
    label = SOURCE_LABELS[source]
    lines = [
        f"# Каталог исходных страниц: {label}",
        "",
        f"Найдено файлов: **{len(rows)}**.",
        "",
        "Список построен из локальной копии upstream. Наличие страницы в каталоге не означает, что она переведена, проверена или редакционно объединена.",
        "",
    ]
    lines.extend(
        f"- [{row['title']}]({row['url']}) — `{row['source']}/{row['path']}`"
        for row in rows
    )
    return "\\n".join(lines) + "\\n"


def render_catalog_index(rows):
    counts = {source: sum(1 for row in rows if row["source"] == source) for source in UPSTREAM}
    lines = [
        "# Каталог исходных страниц",
        "",
        f"Всего страниц: **{len(rows)}**.",
        "",
        "Каталог разделён по первоисточникам, чтобы главная страница оставалась небольшой. Наличие страницы не означает, что она переведена или проверена.",
        "",
        "## Разделы",
        "",
    ]
    for source in UPSTREAM:
        filename = SOURCE_CATALOG_FILES[source]
        lines.append(f"- [{SOURCE_LABELS[source]}](каталоги/{filename}) — {counts[source]} файлов")
    lines.extend([
        "",
        "## Первоисточники",
        "",
        "- [Bedrock Wiki](https://wiki.bedrock.dev/) · [репозиторий](https://github.com/Bedrock-OSS/bedrock-wiki)",
        "- [Microsoft Learn — Minecraft Creator](https://learn.microsoft.com/minecraft/creator/) · [репозиторий документации](https://github.com/MicrosoftDocs/minecraft-creator)",
        "",
    ])
    return "\\n".join(lines)


def main():
    rows = []
    for source in UPSTREAM:
        base = SOURCES / source
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in EXTS or ".git" in path.parts:
                continue
            relative = path.relative_to(base).as_posix()
            try:
                source_text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rows.append({
                "source": source,
                "path": relative,
                "title": title(source_text, path),
                "url": UPSTREAM[source] + relative,
                "sha": hashlib.sha256(source_text.encode()).hexdigest(),
                "norm": norm(source_text),
            })

    rows.sort(key=lambda row: (row["source"], row["path"].lower()))
    validate_catalog_rows(rows)

    OUT.mkdir(parents=True, exist_ok=True)
    CATALOG_DIR.mkdir(parents=True, exist_ok=True)
    for source in UPSTREAM:
        source_rows = [row for row in rows if row["source"] == source]
        filename = SOURCE_CATALOG_FILES[source]
        (CATALOG_DIR / filename).write_text(
            render_source_catalog(source, source_rows), encoding="utf-8"
        )
    (OUT / "КАТАЛОГ_СТАТЕЙ.md").write_text(
        render_catalog_index(rows), encoding="utf-8"
    )

    by_hash, by_title = {}, {}
    for row in rows:
        by_hash.setdefault(row["sha"], []).append(row)
        key = norm(row["title"])
        if key:
            by_title.setdefault(key, []).append(row)

    report = [
        "# Кандидаты на дубли и связи",
        "",
        "Автоматический отчёт. Совпадения требуют проверки: они не являются автоматическим смысловым слиянием.",
        "",
        "## Точное совпадение SHA-256",
        "",
    ]
    exact = [group for group in by_hash.values() if len(group) > 1]
    report += [f"Найдено групп: **{len(exact)}**", ""]
    for index, group in enumerate(exact, 1):
        report += [f"### Группа {index}"] + [
            f"- [{row['title']}]({row['url']}) — `{row['source']}/{row['path']}`"
            for row in group
        ] + [""]

    report += ["## Совпадающие нормализованные заголовки", ""]
    title_groups = [group for group in by_title.values() if len(group) > 1]
    report += [f"Найдено групп: **{len(title_groups)}**", ""]
    for group in title_groups:
        report += [f"### {group[0]['title']}"] + [
            f"- [{row['title']}]({row['url']}) — `{row['source']}/{row['path']}`"
            for row in group
        ] + [""]

    (OUT / "ПОВТОРЫ_И_СВЯЗИ.md").write_text("\\n".join(report) + "\\n", encoding="utf-8")
    print(
        f"Indexed {len(rows)} files; exact duplicate groups: {len(exact)}; "
        f"title groups: {len(title_groups)}"
    )


if __name__ == "__main__":
    main()
