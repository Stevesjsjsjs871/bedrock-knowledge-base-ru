# Bedrock Knowledge Base RU

Единая русскоязычная база знаний по Minecraft: Bedrock Edition Add-Ons. Проект объединяет практические руководства Bedrock Wiki с точным справочником Microsoft Learn, объясняет термины простым языком и сохраняет ссылки на первоисточники.

> Статус: начальная версия энциклопедии. Полный импорт всех страниц, смысловая дедупликация и полный перевод ещё не завершены.

## Начните здесь
- [Карта знаний](docs/ru/КАРТА_ЗНАНИЙ.md)
- [Архитектура Add-On](docs/ru/руководства/АРХИТЕКТУРА_ADDON.md)
- [Behavior Pack и Resource Pack](docs/ru/руководства/BEHAVIOR_PACK_И_RESOURCE_PACK.md)
- [Создание собственной сущности](docs/ru/руководства/СОЗДАНИЕ_СУЩНОСТИ.md)
- [Структура проекта](docs/ru/руководства/СТРУКТУРА_ПРОЕКТА.md)
- [Манифесты, UUID и версии](docs/ru/руководства/МАНИФЕСТЫ_UUID_И_ВЕРСИИ.md)
- [Content Log и диагностика](docs/ru/руководства/CONTENT_LOG_И_ДИАГНОСТИКА.md)
- [Совместимость Stable и Preview](docs/ru/руководства/СОВМЕСТИМОСТЬ_STABLE_PREVIEW.md)
- [Сущности и Entity JSON](docs/ru/руководства/СУЩНОСТИ_ENTITY_JSON.md)
- [Создание собственной сущности](docs/ru/руководства/СОЗДАНИЕ_СУЩНОСТИ.md)
- [Структура проекта](docs/ru/руководства/СТРУКТУРА_ПРОЕКТА.md)
- [Манифесты, UUID и версии](docs/ru/руководства/МАНИФЕСТЫ_UUID_И_ВЕРСИИ.md)
- [Именование файлов и идентификаторов](docs/ru/руководства/СТИЛЬ_ИМЕНОВАНИЯ.md)
- [Компоненты сущностей](docs/ru/руководства/КОМПОНЕНТЫ_СУЩНОСТЕЙ.md)
- [Глоссарий](docs/ru/ГЛОССАРИЙ.md)
- [Объединение повторов](docs/ru/справочник/КАК_ОБЪЕДИНЯТЬ_ПОВТОРЫ.md)
- [Навигация по Entity Reference](docs/ru/справочник/КАТАЛОГ_ENTITY_REFERENCE.md)
- [План полного покрытия](docs/ru/справочник/ПЛАН_ПОЛНОГО_ПОКРЫТИЯ.md)
- [Навигация по Entity Reference](docs/ru/справочник/КАТАЛОГ_ENTITY_REFERENCE.md)

## Источники
- [Bedrock Wiki](https://wiki.bedrock.dev/) · [GitHub](https://github.com/Bedrock-OSS/bedrock-wiki)
- [Microsoft Learn — Entity Reference Stable](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/?view=minecraft-bedrock-stable) · [GitHub](https://github.com/MicrosoftDocs/minecraft-creator)

## Синхронизация источников
Нужны Git и Python 3.10+. Выполните `python tools/sync_sources.py`, затем `python tools/build_catalog.py`. Исходники сохраняются в локальной папке sources; полные копии материалов не публикуются автоматически.

## Принципы
1. Каждая объединённая статья сохраняет ссылки на первоисточники.
2. Не переводить JSON-ключи, идентификаторы компонентов и имена API.
3. Не смешивать Stable и Preview без явной пометки.
4. Машинный поиск находит кандидатов на дубли; смысловое слияние требует проверки.
5. Проверять лицензию конкретного источника перед копированием полного текста, кода или изображений.

## Структура
- `docs/ru/` — русские пояснения и руководства.
- `tools/` — синхронизация и каталогизация.
- `sources/` — локальные upstream-копии для анализа; не коммитятся по умолчанию.

Подробности о правах и атрибуции: [LICENSES_AND_ATTRIBUTION.md](LICENSES_AND_ATTRIBUTION.md).