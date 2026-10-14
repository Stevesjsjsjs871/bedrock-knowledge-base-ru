# Сущности и Entity JSON

## Что это
Entity JSON описывает идентификатор сущности и данные, из которых игра собирает её поведение. Доступные поля зависят от формата и версии Minecraft Bedrock.

## Основные разделы
- `description`: идентификатор и метаданные определения.
- `components`: компоненты базового состояния.
- `component_groups`: наборы компонентов для альтернативных состояний.
- `events`: именованные реакции, способные переключать группы или выполнять поддерживаемые действия.

## Схематичный пример
```json
{
  "format_version": "1.20.0",
  "minecraft:entity": {
    "description": {
      "identifier": "example:scout",
      "is_spawnable": true,
      "is_summonable": true
    },
    "components": {
      "minecraft:health": { "value": 20, "max": 20 }
    },
    "events": {}
  }
}
```
Пример иллюстрирует форму данных, но не гарантирует совместимость со всеми версиями. Сверяйте поля с [официальным Entity Reference Stable](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/?view=minecraft-bedrock-stable).

## Частые ошибки
- Неверный namespace или опечатка в идентификаторе.
- Неправильный тип поля.
- Компонент находится не в той секции.
- Используется поле, отсутствующее в выбранной версии.
- Stable и Preview смешаны без маркировки.

Источники: https://github.com/MicrosoftDocs/minecraft-creator/tree/main/creator/Reference/Content/EntityReference и https://wiki.bedrock.dev/