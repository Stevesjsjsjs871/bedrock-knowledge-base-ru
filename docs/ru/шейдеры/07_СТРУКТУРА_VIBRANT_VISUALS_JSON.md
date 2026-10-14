# Структура JSON в Vibrant Visuals

## Что именно настраивается

Современный графический путь Bedrock разделяет описание материала и настройки сцены:

- **Texture Set** описывает поверхность конкретной текстуры: металлическость, эмиссию, шероховатость и дополнительные карты.
- **Lighting** управляет глобальным освещением, солнцем/луной, небесным и окружающим светом.
- **Atmospherics** описывает рассеяние света в атмосфере и переходы горизонта.
- **Color grading** отвечает за финальную цветовую обработку и тональное отображение.
- **Water** содержит настройки внешнего вида воды.
- **Cubemap** задаёт кубическую карту окружения в поддерживаемых сценариях.
- **Biome mapping** связывает конфигурации с конкретными биомами.

Названия файлов и структура ниже — ориентир, а не обещание, что любой файл автоматически активируется во всех версиях. Сверяйте структуру с документацией и официальными примерами для целевой версии.

## Типичная структура пакета

~~~text
MyVisualPack/
├── manifest.json
├── textures/
│   ├── blocks/
│   │   └── stone.texture_set.json
│   ├── entity/
│   ├── particle/
│   ├── items/
│   └── ...
├── textures_list.json
├── lighting/
│   └── default_lighting.json
├── atmospherics/
│   └── default_atmospherics.json
├── color_grading/
│   └── default_color_grading.json
├── water/
│   └── water.json
└── cubemaps/
    └── ...
~~~

Это иллюстративная схема по официальной документации: реальные имена файлов и набор каталогов зависят от функций пакета. Texture Set JSON располагается рядом с соответствующей текстурой в подходящем каталоге `textures/`, а не в универсальном каталоге `pbr/`. Не создавайте пустые JSON только ради совпадения со схемой.

## Manifest и capability

Для пакета, использующего Vibrant Visuals PBR-ресурсы, официальная документация указывает capability `pbr` и `min_engine_version` не ниже `[1, 21, 120]`. Ниже приведён сокращённый фрагмент-шаблон с намеренно фиктивными UUID:

~~~json
{
  "format_version": 2,
  "header": {
    "name": "My Visual Pack",
    "description": "Vibrant Visuals resource pack",
    "uuid": "REPLACE-WITH-UNIQUE-UUID",
    "version": [1, 0, 0],
    "min_engine_version": [1, 21, 120]
  },
  "modules": [
    {
      "type": "resources",
      "uuid": "REPLACE-WITH-ANOTHER-UNIQUE-UUID",
      "version": [1, 0, 0]
    }
  ],
  "capabilities": ["pbr"]
}
~~~

**Этот фрагмент не является импортируемым manifest, пока не заменены UUID.** Создайте уникальные UUID для header и каждого module. Для синтаксически корректного примера с настоящими UUID и проверок см. [статический fixture](../../../tests/fixtures/vibrant_visuals_minimal/README.md). Перед использованием проверьте актуальные требования manifest и минимальную версию игры.

## format_version — не номер игры

`format_version` внутри конкретного графического JSON указывает версию схемы, по которой интерпретируется этот файл. Это не обязательно версия установленной игры и не то же самое, что `min_engine_version` в manifest.

В обновлении 26.20 для конфигураций атмосферы и воды используется схема `1.26.20` и обязательные корневые объекты/описания согласно соответствующим схемам. Это не означает, что все JSON в паке нужно массово перевести на `1.26.20`.

## Ограничения Texture Set, которые легко пропустить

По официальной схеме Texture Sets:

- слой `color` обязателен;
- `normal` и `heightmap` нельзя указывать одновременно;
- `metalness_emissive_roughness` (MER) и `metalness_emissive_roughness_subsurface` (MERS) нельзя указывать одновременно;
- uniform-значение `color` задаётся четырьмя значениями каналов, а MER — тремя; значения лежат в диапазоне 0–255;
- если слой ссылается на имя текстуры, файл должен присутствовать в том же resource pack; иначе Texture Set может быть отвергнут.

Texture Set может быть синтаксически корректным JSON и всё равно не соответствовать схеме или ссылаться на отсутствующую текстуру. Официальная документация указывает, что неверный Texture Set не используется, а в Content Log появляется ошибка.

## Идентификаторы и привязки

Идентификаторы конфигураций должны быть уникальными и включать namespace, например `my_pack:default_atmospherics`. Проверяйте, как выбранная конфигурация назначается биому или графическому слою. Файл на диске сам по себе не доказывает, что игра его использует.

## Безопасная последовательность разработки

1. Создайте минимальный resource pack и уникальные UUID.
2. Добавьте только `pbr` capability, если используете соответствующие PBR/Vibrant Visuals assets.
3. Начните с одного проверяемого изменения.
4. Убедитесь, что пакет импортируется и включается.
5. Проверьте Content Log и ошибки JSON.
6. Добавляйте остальные конфигурации по одной.
7. После обновления Bedrock сравните схему и changelog; не считайте старый JSON гарантированно совместимым.

## Частые ошибки

- Перепутаны версия игры и `format_version` конкретной схемы.
- Повторно использованы UUID из чужого примера.
- capability `pbr` отсутствует, хотя пакет рассчитывает на PBR-путь.
- Папка или файл названы не так, как ожидает соответствующая версия.
- Идентификатор конфигурации не совпадает с назначением.
- JSON синтаксически корректен, но использует поле, которого нет в выбранной схеме.
- Пак импортируется, но эффекты не проверены на целевом устройстве.

## Проверка статуса

Записывайте отдельно: **импортирован**, **активирован**, **конфигурация прочитана без ошибок**, **эффект виден**, **проверено на версии и устройстве**. Не объединяйте эти состояния в одно «работает».

## Источники

- [Vibrant Visuals Resource Packs — Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/vvresourcepacks?view=minecraft-bedrock-stable)
- [Texture Set JSON and Introduction to Texture Sets — Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction?view=minecraft-bedrock-stable)
- [Atmospheric Effects — Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/atmosphericscustomization?view=minecraft-bedrock-stable)
- [Minecraft Bedrock 1.26.20 Update Notes for Creators](https://learn.microsoft.com/en-us/minecraft/creator/documents/update1.26.20?view=minecraft-bedrock-stable)

**Статус:** справочник по официальной документации; fixture проверяется автоматически на уровне JSON и базовых правил, но не заявляется как протестированный в игре.
