"""Перевірка ланцюжка перевірок диспетчера."""

from dispatcher import call_tool

cases = [
    # Успішний виклик
    ("calc_food", '{"weight_kg": 5, "grams_per_kg": 25, "days": 30}'),

    # 1. Зламаний JSON
    ("vaccine_info", '{"vaccine": "комплексне"'),

    # 2. Неправильний тип
    ("calc_food", '{"weight_kg": "п’ять", "grams_per_kg": 25, "days": 30}'),

    # 3. Відсутнє обов'язкове поле
    ("calc_food", '{"weight_kg": 5, "days": 30}'),

    # 4. Вигадане поле
    ("search_articles", '{"query": "дряпає меблі", "extra": 1}'),

    # 5. Неіснуючий інструмент
    ("delete_all", '{}'),

    # 6. Заборонена дія
    ("book_vet", '{"date": "п’ятниця"}'),

    # 7. Значення відсутнє в довіднику
    ("vaccine_info", '{"vaccine": "комплексне щеплення"}'),

    # 8. Значення поза межами
    ("calc_food", '{"weight_kg": 45, "grams_per_kg": 25, "days": 14}'),
]

for name, raw in cases:
    level, result = call_tool(name, raw)
    print(f"{name}: {level}")
    print(f"Виклик: {name}({raw})")
    print(f"Повідомлення: {result}\n")
