# Vibrant Visuals и PBR: современный путь графических паков

Vibrant Visuals — официальный современный графический режим Bedrock. Он использует поддерживаемый движком путь освещения и эффектов; авторы Resource Packs могут настраивать доступные параметры через JSON-конфигурации и описывать материалы через Texture Sets. Это не означает, что любой произвольный шейдерный код можно положить в Resource Pack.

**Основные официальные источники:**
- [Vibrant Visuals Resource Packs](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/vvresourcepacks?view=minecraft-bedrock-stable)
- [Texture Sets: введение](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction?view=minecraft-bedrock-stable)
- [Настройка биомов](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/biomecustomization?view=minecraft-bedrock-stable)
- [Настройка источников света](https://learn.microsoft.com/en-us/minecraft/creator/documents/vibrantvisuals/lightingcustomization?view=minecraft-bedrock-stable)

## Требования к manifest

Официальная документация указывает, что Vibrant Visuals-паку нужна capability `pbr` и `min_engine_version` не ниже `[1, 21, 120]` для описанного в этой статье пути. Пак с capability `raytraced` также активирует Vibrant Visuals, но `pbr` рекомендуется для кроссплатформенных паков.

~~~json
{
  "format_version": 1,
  "header": {
    "name": "Example Visuals",
    "description": "Example resource pack",
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

Это учебный фрагмент: UUID нужно заменить уникальными корректными значениями. Минимальная версия и схема должны проверяться против текущего официального руководства при обновлении игры.

## Texture Sets

Texture Sets описывают, как поверхность реагирует на освещение. Базовый слой `color` обязателен; дополнительные слои могут описывать normal map или heightmap (в одном наборе эти два слоя нельзя одновременно задавать), metalness/emissive/roughness и subsurface scattering в поддерживаемом формате.

- **Color** — цветовая карта; используется и классическим рендером.
- **Normal** — информация о нормалях для рельефного освещения.
- **Heightmap** — высотная карта для поддерживаемых случаев; документация отдельно предупреждает об ограничениях для текстурных объектов вроде предметов.
- **Metalness / Emissive / Roughness** — характеристики металличности, собственного свечения и шероховатости поверхности.
- **Subsurface scattering** — дополнительное свойство материалов, которое поддерживает современный формат Vibrant Visuals.

Не называйте карту нормалей «настоящим рельефом геометрии»: она влияет на освещение поверхности, но не обязана изменять силуэт объекта.

## Какие JSON настраивают вид мира

В официальном наборе Vibrant Visuals описаны отдельные конфигурации, в том числе:

- `lighting/` — направленный свет, окружающее освещение, свет неба и связанные параметры;
- `atmospherics/` — атмосфера и рассеяние света;
- `color_grading/` — цветокоррекция;
- `water/` — вода и связанные визуальные параметры;
- настройки cubemap — окружение/кубическая карта в поддерживаемых сценариях;
- `pbr/` — резервные значения PBR для ресурсов без собственной texture set.

Точные поля, `format_version` и обязательные узлы зависят от конкретной схемы и версии игры. Не копируйте JSON из старого туториала без проверки changelog и текущей схемы.

## Настройка по биомам

Начиная с Bedrock 1.21.90 поддерживаются отдельные конфигурации Vibrant Visuals для биомов. Для этого JSON-настройки связываются с client biome JSON через соответствующие идентификаторы, например `minecraft:lighting_identifier`, `minecraft:atmosphere_identifier`, `minecraft:color_grading_identifier` и `minecraft:water_identifier`.

Начиная с этой модели, встроенные настройки по биомам могут иметь приоритет над глобальными конфигурациями. Если глобальный JSON «не влияет» на конкретный биом, сначала проверьте привязку и приоритет биомной конфигурации, а не только имя файла.

## Отдельно о версиях 26.x

В публичной нумерации с 2026 года используются номера, начинающиеся с `26` (например, 26.0, 26.20). В документации схем и API всё ещё может использоваться форматная запись `1.26.xx`. Это разные контексты нумерации: версия игры и `format_version` JSON нельзя автоматически подменять друг другом.

## Диагностика

1. Убедитесь, что устройство и текущая версия игры поддерживают Vibrant Visuals.
2. Включите именно режим Vibrant Visuals в настройках графики, если он доступен.
3. Проверьте capability `pbr` и `min_engine_version` в manifest.
4. Убедитесь, что texture set и все связанные изображения находятся по правильным путям и имеют ожидаемые размеры/каналы.
5. Проверьте JSON на корректность и соответствие актуальной схеме.
6. При настройке биомов проверьте client biome JSON и идентификаторы конфигураций.
7. Отключите другие визуальные паки и проверьте конфликтующие настройки по одному.
8. Сравните результаты в одном и том же биоме, времени суток и графическом пресете.

**Статус:** материал составлен по Microsoft Learn; примеры manifest схематические, игровой тест не заявляется.
