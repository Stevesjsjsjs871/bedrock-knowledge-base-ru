#!/usr/bin/env python3
"""Generate a Russian status registry from Microsoft's Entity Component List."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "minecraft-creator" / "creator" / "Reference" / "Content" / "EntityReference" / "Examples" / "ComponentList.md"
OUT = ROOT / "docs" / "ru" / "справочник" / "РЕЕСТР_КОМПОНЕНТОВ_СУЩНОСТЕЙ.md"
UPSTREAM = "https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/Reference/Content/EntityReference/Examples/"

def parse_rows(text):
    rows = []
    pattern = re.compile(r"^\| \[([^\]]+)\]\((EntityComponents/[^)]+\.md)\)\|\s*(.*?)\s*\|$", re.M)
    for name, path, description in pattern.findall(text):
        rows.append((name.strip(), path.strip(), re.sub(r"\s+", " ", description.strip())))
    return rows

CARD_STATUS = {
    "minecraftComponent_health.md": ("Черновик", "КОМПОНЕНТ_HEALTH.md"),
    "minecraftComponent_collision_box.md": ("Черновик", "КОМПОНЕНТ_COLLISION_BOX.md"),
    "minecraftComponent_movement.md": ("Черновик", "КОМПОНЕНТ_MOVEMENT.md"),
    "minecraftComponent_type_family.md": ("Черновик", "КОМПОНЕНТ_TYPE_FAMILY.md"),
}

def render_table(rows, default_status):
    lines = []
    for i, (name, path, description) in enumerate(rows, 1):
        filename = path.rsplit("/", 1)[-1]
        status, card = CARD_STATUS.get(filename, (default_status, None))
        if card:
            status = "[{}](../справочник/{})".format(status, card)
        lines.append("| {} | [{}]({}{}) | {} | {} |".format(
            i, name, UPSTREAM, path, description.replace("|", r"\\|"), status))
    return lines

def main():
    if not SOURCE.exists():
        raise SystemExit("Источник не найден: {}. Сначала выполните python tools/sync_sources.py".format(SOURCE))
    source = SOURCE.read_text(encoding="utf-8", errors="replace")
    marker = "## Internal/Deprecated Components"
    active_text, _, deprecated_text = source.partition(marker)
    active = parse_rows(active_text)
    deprecated = parse_rows(deprecated_text)
    if len(active) < 100:
        raise SystemExit("Слишком мало компонентов ({}): формат источника мог измениться. Файл не перезаписан.".format(len(active)))
    lines = [
        "# Реестр компонентов сущностей Entity Reference", "",
        "> Снимок официального списка Microsoft Learn / GitHub. Активных записей: **{}**; внутренних/устаревших: **{}**. Это реестр работ, а не заявление о полном русском покрытии.".format(len(active), len(deprecated)), "",
        "## Статусы", "",
        "- **Не начато** — русская карточка ещё не подготовлена.",
        "- **Черновик** — объяснение есть, но поля и ограничения не проверены полностью.",
        "- **Сверено с источником** — поля сопоставлены с текущей официальной страницей.",
        "- **Пример проверен** — пример проверен валидатором/схемой; это не равно тесту в игре.",
        "- **Проверено в игре** — воспроизведено на указанной версии Bedrock.",
        "- **Требует проверки** — источник или поведение может быть устаревшим либо неоднозначным.", "",
        "Для каждой полноценной карточки нужно фиксировать идентификатор, назначение, все поля, типы и значения по умолчанию, ограничения версий Stable/Preview, минимальный пример, типичные ошибки и ссылку на источник.", "",
        "## Основной список", "",
        "| № | Компонент из источника | Описание источника | Статус русской карточки |",
        "|---:|---|---|---|",
    ]
    lines += render_table(active, "Не начато")
    lines += ["", "## Внутренние или устаревшие компоненты", "",
        "Они выделены отдельно в первоисточнике. Не рекомендуется использовать их в новых Add-On без самостоятельной проверки поддержки.", "",
        "| № | Идентификатор/название | Описание источника | Статус |", "|---:|---|---|---|"]
    lines += render_table(deprecated, "Требует проверки")
    lines += ["", "## Первоисточники", "",
        "- [Официальный список Entity Components](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/Reference/Content/EntityReference/Examples/ComponentList.md)",
        "- [Entity Reference Stable в Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/?view=minecraft-bedrock-stable)",
        "- [Руководство по компонентам сущностей](https://learn.microsoft.com/en-us/minecraft/creator/documents/entitycomponentsguide?view=minecraft-bedrock-stable)", "",
        "## Обновление", "",
        "Сначала синхронизируйте upstream: python tools/sync_sources.py, затем выполните python tools/build_entity_component_inventory.py. Если структура списка изменилась и найдено менее 100 активных записей, генератор остановится и сохранит прежний реестр.", ""]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print("Generated {}: {} active, {} internal/deprecated.".format(OUT.relative_to(ROOT), len(active), len(deprecated)))

if __name__ == "__main__":
    main()
