"""Тестування рівнів перевірок без виклику моделі."""

from dispatcher import call_tool


cases = [
    (
        "Зламаний JSON",
        "product_info",
        '{"product": "рис"',
        "syntax",
    ),

    (
        "Неправильний тип",
        "scale_amount",
        '{"amount": "сто", "base_servings": 4, "target_servings": 10}',
        "schema",
    ),

    (
        "Відсутнє обов'язкове поле",
        "product_info",
        '{}',
        "schema",
    ),

    (
        "Вигадане поле",
        "product_info",
        '{"product": "рис", "x": 1}',
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
        "place_order",
        '{"products": "рис"}',
        "permission",
    ),

    (
        "Значення відсутнє в довіднику",
        "product_info",
        '{"product": "кіноа"}',
        "meaning",
    ),

    (
        "Значення поза межами",
        "scale_amount",
        '{"amount": 300, "base_servings": 0, "target_servings": 10}',
        "schema",
    ),
]


passed = 0

for title, name, raw, expected in cases:

    level, message = call_tool(name, raw)

    print(f"\n{'=' * 60}")
    print(f"ТЕСТ: {title}")
    print(f"Виклик: {name}({raw})")
    print(f"Рівень: {level}")
    print(f"Повідомлення: {message}")

    assert level == expected, (
        f"Помилка тесту '{title}': "
        f"очікувався '{expected}', отримано '{level}'"
    )

    passed += 1


print(f"\nУСПІШНО: {passed}/{len(cases)} тестів.")
