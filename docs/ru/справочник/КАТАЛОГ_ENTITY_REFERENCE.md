# Навигация по Entity Reference

Официальный [Entity Reference Stable](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/?view=minecraft-bedrock-stable) — первоисточник для проверки компонентов, полей и поведения сущностей.

## С чего начинать
- [Список компонентов сущностей](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/Reference/Content/EntityReference/Examples/ComponentList.md) — обзор имён компонентов и кратких описаний.
- [Каталог документации Microsoft](https://github.com/MicrosoftDocs/minecraft-creator/tree/main/creator/Reference/Content/EntityReference) — исходные файлы справочника.
- [Создание новых типов сущностей](https://learn.microsoft.com/en-us/minecraft/creator/documents/introductiontoaddentity?view=minecraft-bedrock-stable) — связанный учебный материал.

## Как использовать справочник
1. Найдите компонент по точному идентификатору, например `minecraft:health`.
2. Откройте отдельную страницу компонента.
3. Проверьте типы полей, значения по умолчанию, ограничения и требования версии.
4. Убедитесь, что компонент подходит к нужному типу сущности и месту в JSON.
5. Если русская статья в этом репозитории расходится с Microsoft Learn, считайте первоисточник главным и откройте issue для исправления.

## Важно
Список компонентов не означает, что каждый компонент применим в любом контексте. Также наличие страницы не гарантирует, что компонент доступен во всех версиях игры. Учитывайте пометки Stable/Preview и версию документации.
