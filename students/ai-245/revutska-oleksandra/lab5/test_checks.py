"""Тестування багаторівневих перевірок диспетчера."""

from dispatcher import call_tool


cases = [
    (
        "Зламаний JSON",
        "search_books",
        '{"query": "фантастика"',
        "syntax",
    ),
    (
        "Неправильний тип",
        "calculate",
        '{"operation": "mul", "a": "п\'ять", "b": 10}',
        "schema",
    ),
    (
        "Відсутнє поле",
        "book_info",
        '{}',
        "schema",
    ),
    (
        "Зайве поле",
        "search_books",
        '{"query": "фантастика", "x": 1}',
        "schema",
    ),
    (
        "Неіснуючий інструмент",
        "delete_all",
        '{}',
        "name",
    ),
    (
        "Заборонена дія",
        "issue_book",
        '{"title": "Зоряний садівник"}',
        "permission",
    ),
    (
        "Невідома книжка",
        "book_info",
        '{"title": "Неіснуюча книжка"}',
        "meaning",
    ),
    (
        "Число поза межами",
        "calculate",
        '{"operation": "mul", "a": 2000000, "b": 5}',
        "schema",
    ),
]


passed = 0

for description, name, raw, expected in cases:
    level, message = call_tool(name, raw)

    success = level == expected

    if success:
        passed += 1

    print("=" * 65)
    print(f"Перевірка: {description}")
    print(f"Інструмент: {name}")
    print(f"Очікуваний рівень: {expected}")
    print(f"Отриманий рівень:  {level}")
    print(f"Статус: {'PASS' if success else 'FAIL'}")
    print(f"Повідомлення: {message}")


print("\n" + "=" * 65)
print(f"РЕЗУЛЬТАТ: {passed}/{len(cases)} перевірок пройдено")

if passed != len(cases):
    raise SystemExit(1)