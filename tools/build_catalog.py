#!/usr/bin/env python3
"""Build an index and duplicate-candidate report from locally synced sources."""
from pathlib import Path
import hashlib
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
OUT = ROOT / "docs" / "ru"
EXTS = {".md", ".mdx", ".yml", ".yaml"}
UPSTREAM = {
    "bedrock-wiki": "https://github.com/Bedrock-OSS/bedrock-wiki/blob/wiki/",
    "minecraft-creator": "https://github.com/MicrosoftDocs/minecraft-creator/blob/main/",
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
        m = re.match(r"^\s*#\s+(.+?)\s*#*\s*$", line)
        if m and m.group(1).strip().lower() not in {"section", "overview"}:
            return m.group(1)
    return path.stem.replace("_", " ").replace("-", " ")

def norm(text):
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"```.*?```|`[^`]*`", " ", text, flags=re.S)
    text = re.sub(r"https?://\S+", " ", text)
    return re.sub(r"[^\w]+", " ", text).strip()

def main():
    rows = []
    for source in UPSTREAM:
        base = SOURCES / source
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in EXTS or ".git" in p.parts:
                continue
            rel = p.relative_to(base).as_posix()
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            rows.append({"source": source, "path": rel, "title": title(text, p),
                         "url": UPSTREAM[source] + rel, "sha": hashlib.sha256(text.encode()).hexdigest(),
                         "norm": norm(text)})
    rows.sort(key=lambda x: (x["source"], x["path"].lower()))
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = ["# Каталог исходных страниц", "", f"Найдено файлов: **{len(rows)}**.", "",
               "Каталог создаётся из локальных копий upstream. Он не означает, что все страницы переведены или редакционно объединены.", ""]
    catalog += [f"- [{r['title']}]({r['url']}) — `{r['source']}/{r['path']}`" for r in rows]
    (OUT / "КАТАЛОГ_СТАТЕЙ.md").write_text("\n".join(catalog) + "\n", encoding="utf-8")
    by_hash, by_title = {}, {}
    for r in rows:
        by_hash.setdefault(r["sha"], []).append(r)
        key = norm(r["title"])
        if key:
            by_title.setdefault(key, []).append(r)
    report = ["# Кандидаты на дубли и связи", "", "Автоматический отчёт. Совпадения требуют проверки: они не являются автоматическим смысловым слиянием.", "", "## Точное совпадение SHA-256", ""]
    exact = [g for g in by_hash.values() if len(g) > 1]
    report += [f"Найдено групп: **{len(exact)}**", ""]
    for i, group in enumerate(exact, 1):
        report += [f"### Группа {i}"] + [f"- [{r['title']}]({r['url']}) — `{r['source']}/{r['path']}`" for r in group] + [""]
    report += ["## Совпадающие нормализованные заголовки", ""]
    titles = [g for g in by_title.values() if len(g) > 1]
    report += [f"Найдено групп: **{len(titles)}**", ""]
    for group in titles:
        report += [f"### {group[0]['title']}"] + [f"- [{r['title']}]({r['url']}) — `{r['source']}/{r['path']}`" for r in group] + [""]
    (OUT / "ПОВТОРЫ_И_СВЯЗИ.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Indexed {len(rows)} files; exact duplicate groups: {len(exact)}; title groups: {len(titles)}")

if __name__ == "__main__":
    main()
