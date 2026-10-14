# Texture Set: точная схема, каналы и ошибки

## Область действия

Texture Set — JSON-описание PBR-слоёв для одной текстурной ссылки. Это не шейдерный код и не отдельная геометрия: файл сообщает движку, какие данные поверхности использовать. Ниже приведены правила, сверенные с документацией Microsoft Learn и схемой/примерами Mojang Bedrock Samples.

Источники могут описывать разные версии схемы. В примерах ниже используется `format_version: "1.21.30"`, потому что этот формат указан в официальной справке Texture Sets. Не меняйте версию механически на номер установленной игры.

## Минимальная структура

У набора должен быть слой `color`. Остальные слои необязательны.

```json
{
  "format_version": "1.21.30",
  "minecraft:texture_set": {
    "color": "stone",
    "metalness_emissive_roughness": "stone_mer"
  }
}
```

Это схема-пример: ссылки `stone` и `stone_mer` должны разрешаться в изображения в том же resource pack. Сам JSON не создаёт отсутствующие изображения.

## Слои и формат данных

| Свойство | Назначение | Поддерживаемые данные |
|---|---|---|
| `color` | Базовый цвет | RGB/RGBA-изображение или равномерное значение на 4 канала |
| `normal` | Направления нормалей для мелкого рельефа | 3-канальное изображение; 4-й канал игнорируется |
| `heightmap` | Одноканальная карта высоты | Одноканальное изображение или одно равномерное значение |
| `metalness_emissive_roughness` | MER: металл, эмиссия, шероховатость | RGB-изображение или 3 значения |
| `metalness_emissive_roughness_subsurface` | MERS: MER плюс подповерхностное рассеяние | RGBA-изображение или 4 значения |

Для ссылок на изображения имена слоёв указываются без расширения. Изображение должно существовать в том же паке, что и Texture Set. Официальная справка описывает значения uniform-слоёв в диапазоне 0–255, в том числе в виде числовых массивов или hex-строк для подходящего количества каналов.

## MER и MERS: порядок каналов

Для MER изображение RGB читается так:

- **R (красный)** — Metalness.
- **G (зелёный)** — Emissive.
- **B (синий)** — Roughness.

MERS использует RGBA:

- **R** — Metalness.
- **G** — Emissive.
- **B** — Roughness.
- **A (альфа)** — Subsurface.

Не путайте цветовые каналы MER с обычным изображением цвета. Например, яркий зелёный канал в MER означает высокий вклад эмиссии, а не зелёный оттенок базового материала.

### MER и MERS взаимоисключающие

Не объявляйте в одном Texture Set одновременно `metalness_emissive_roughness` и `metalness_emissive_roughness_subsurface`. Это конфликт слоёв и может сделать Texture Set недействительным.

MERS поддерживается Vibrant Visuals, но не RTX: в RTX subsurface-данные из этого слоя игнорируются. Metalness и subsurface также конкурируют за тип поведения материала: они не работают как независимые максимальные эффекты на одном и том же пикселе. В документации описан выбор доминирующего свойства по большему значению; при равенстве преимущество получает subsurface.

## Normal Map против Height Map

В одном Texture Set нельзя одновременно задавать `normal` и `heightmap`. Выберите один из этих слоёв.

Дополнительное ограничение Vibrant Visuals: heightmap нельзя применять к объектам, использующим текстуры как поверхность, например к предметам; для них следует использовать normal map. Поэтому не переносите настройку heightmap с блока на предмет без проверки.

## Пример с MERS

```json
{
  "format_version": "1.21.30",
  "minecraft:texture_set": {
    "color": "cactus_side",
    "metalness_emissive_roughness_subsurface": "cactus_side_mers",
    "normal": "cactus_side_normal"
  }
}
```

Это структура из официальных примеров Texture Sets. Для запуска в своём паке необходимо добавить соответствующие изображения и проверить, что они находятся в нужной папке и имеют корректные каналы.

## Что делает Texture Set недействительным

Официальная документация перечисляет, в частности, следующие причины:

1. JSON не разбирается или не соответствует схеме.
2. Отсутствует обязательный слой `color`.
3. Одновременно объявлены `normal` и `heightmap`.
4. Одновременно объявлены MER и MERS.
5. Ссылка указывает на отсутствующее или некорректное изображение.
6. Количество каналов не соответствует типу слоя.
7. Heightmap назначен объекту, для которого он не поддерживается.

При недействительном Texture Set игра может записать `CONTENT_ERROR` и не использовать набор. Успешный разбор JSON не гарантирует, что все текстуры найдены или визуальный результат верен.

## Порядок ресурс-паков

- Texture Set может ссылаться только на изображения из того же resource pack.
- Текстура из пака с более высоким приоритетом не подменяет изображение, на которое ссылается Texture Set другого пака.
- Определения Texture Set для одной и той же текстурной ссылки не объединяются по слоям: определение из пака с более высоким приоритетом заменяет определение нижнего пака.

Это важно при диагностике конфликтов: если верхний пак переопределил Texture Set, нельзя ожидать, что его MER автоматически объединится с color/normal из нижнего пака.

## Практическая диагностика

1. Проверьте имя и путь самого Texture Set.
2. Проверьте, что слой `color` существует и корректно ссылается на изображение.
3. Убедитесь, что все ссылки на изображения разрешаются внутри того же пака.
4. Проверьте число каналов и взаимное исключение normal/heightmap и MER/MERS.
5. Оставьте включённым только тестируемый пак, чтобы исключить перекрытие ресурс-стеком.
6. Прочитайте Content Log и найдите `CONTENT_ERROR`.
7. Проверьте результат в игре на целевой версии и устройстве — статический валидатор не способен подтвердить визуальный эффект.

## Источники

- [Texture Set JSON and Introduction to Texture Sets — Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction?view=minecraft-bedrock-stable)
- [Texture Set schema 1.21.30 — Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/visualreference/texture_set.v1.21.30?view=minecraft-bedrock-stable)
- [Mojang Bedrock Samples: Texture Sets documentation](https://github.com/Mojang/bedrock-samples/blob/main/documentation/Texture%20Sets.html)
- [Mojang Bedrock Samples: bedrock texture set](https://github.com/Mojang/bedrock-samples/blob/main/resource_pack/textures/blocks/bedrock.texture_set.json)
- [Vibrant Visuals Resource Packs — Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/vvresourcepacks?view=minecraft-bedrock-stable)

**Статус проверки:** сведения сверены с опубликованной схемой и примерами; файл не заявляется как протестированный внутри запущенной игры.
