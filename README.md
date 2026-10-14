# Bedrock Knowledge Base RU

Единая русскоязычная база знаний по Minecraft: Bedrock Edition Add-Ons. Проект объединяет практические руководства Bedrock Wiki с точным справочником Microsoft Learn, объясняет термины простым языком и сохраняет ссылки на первоисточники.

> Статус: начальная версия энциклопедии. Полный импорт всех страниц, смысловая дедупликация и полный перевод ещё не завершены.

## Начните здесь

Выберите маршрут по задаче — полный список материалов остаётся доступен через карту знаний и каталог статей.

### Я только начинаю
- [Карта знаний](docs/ru/КАРТА_ЗНАНИЙ.md) — маршруты по темам.
- [Архитектура Add-On](docs/ru/руководства/АРХИТЕКТУРА_ADDON.md) — что входит в Behavior Pack и Resource Pack.
- [Создание собственной сущности](docs/ru/руководства/СОЗДАНИЕ_СУЩНОСТИ.md) — пошаговый практический пример.

### Создаю Resource Pack или графику
- [Behavior Pack и Resource Pack](docs/ru/руководства/BEHAVIOR_PACK_И_RESOURCE_PACK.md)
- [Текстуры и геометрия](docs/ru/руководства/ТЕКСТУРЫ_И_ГЕОМЕТРИЯ.md)
- [Углублённый раздел шейдеров и Vibrant Visuals](docs/ru/шейдеры/00_КАРТА_РАЗДЕЛА_ШЕЙДЕРЫ_BEDROCK.md)

### Создаю Behavior Pack или Script API
- [Компоненты сущностей](docs/ru/руководства/КОМПОНЕНТЫ_СУЩНОСТЕЙ.md)
- [Molang: основы](docs/ru/руководства/MOLANG_ОСНОВЫ.md)
- [Script API: обзор](docs/ru/руководства/SCRIPTING_API_ОБЗОР.md)
- [Версии Script API](docs/ru/руководства/ВЕРСИИ_SCRIPT_API.md)

### Проверяю JSON, совместимость или ошибки
- [Проверка JSON и схем](docs/ru/руководства/ПРОВЕРКА_JSON_И_СХЕМЫ.md)
- [Content Log и диагностика](docs/ru/руководства/CONTENT_LOG_И_ДИАГНОСТИКА.md)
- [Совместимость Stable и Preview](docs/ru/руководства/СОВМЕСТИМОСТЬ_STABLE_PREVIEW.md)
- [Стандарт доказательности технических утверждений](docs/ru/руководства/СТАНДАРТ_ДОСТОВЕРНОСТИ_ЗНАНИЙ.md)

### Анализирую готовый пак или ищу оптимизацию
- [Шаблон анализа готового пака](docs/ru/справочник/ШАБЛОН_АНАЛИЗА_ПАКА.md)
- [FPS Booster и Lithium FPSbooster — разбор](docs/ru/разборы/АНАЛИЗ_FPS_BOOSTER_И_LITHIUM.md)
- [Каталог статей](docs/ru/КАТАЛОГ_СТАТЕЙ.md)
- [Карта знаний и связи тем](docs/ru/КАРТА_ЗНАНИЙ.md)

## Участие в проекте
- [Правила внесения изменений](CONTRIBUTING.md)

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
### Автоматическая проверка репозитория
GitHub Actions запускает единый набор тестов для каждого push и pull request: [Validate repository](.github/workflows/validate-repository.yml). Локально выполните `python -m unittest discover -s tests -v` и `python tools/validate_repository.py`. Проверки структуры и JSON не заменяют тестирование resource pack в Minecraft.

- [Официальные ZIP-архивы Mojang Bedrock Samples по версиям](docs/ru/справочник/КАТАЛОГ_BEDROCK_SAMPLES.md)

## Разборы сторонних паков
- [FPS Booster v2.4.1 и Lithium FPSbooster v5 — анализ оптимизации](docs/ru/разборы/АНАЛИЗ_FPS_BOOSTER_И_LITHIUM.md)
- [Actions & Stuff 1.1.64 — анализ Resource Pack](docs/ru/разборы/РАЗБОР_ACTIONS_AND_STUFF_RP.md)
- [Realistic Biomes 1.3 — анализ связки Behavior Pack + Resource Pack](docs/ru/разборы/РАЗБОР_REALISTIC_BIOMES_ADDON.md)
- [План чистой реализации механик двух паков](docs/ru/разборы/ПЛАН_ЧИСТОЙ_РЕАЛИЗАЦИИ_МЕХАНИК_ДВУХ_ПАКОВ.md)
- [Собственная реализация EventBus на JavaScript](examples/clean-room/core/event-bus.js)
