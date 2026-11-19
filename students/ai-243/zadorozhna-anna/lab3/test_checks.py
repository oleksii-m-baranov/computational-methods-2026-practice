"""Перевірка ланцюжка перевірок диспетчера (без моделі)."""
from dispatcher import call_tool


cases = [
    # (назва, аргументи, що перевіряємо)
    ("search_recipes", '{"query": сир}',                                          "Зламаний JSON"),
    ("search_recipes", '{"query": 123}',                                          "Неправильний тип"),
    ("search_recipes", '{}',                                                      "Відсутнє обов'язкове поле"),
    ("search_recipes", '{"query": "сир", "x": 1}',                                "Вигадане поле"),
    ("delete_all", '{}',                                                          "Неіснуючий інструмент"),
    ("place_order", '{"product": "рис", "quantity": 1}',                          "Заборонена дія"),
    ("product_info", '{"product": "тунець"}',                                     "Значення немає в довіднику"),
    ("scale_amount", '{"amount": -5, "base_servings": 4, "target_servings": 10}', "Значення поза межами"),
]

for name, raw, label in cases:
    level, text = call_tool(name, raw)
    print(f"━━━ {label} ━━━")
    print(f"  виклик : {name}({raw})")
    print(f"  рівень : {level}")
    print(f"  текст  : {text}")
    print()