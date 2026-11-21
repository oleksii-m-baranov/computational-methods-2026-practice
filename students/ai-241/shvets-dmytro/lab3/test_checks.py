"""Перевірка кожної перевірки диспетчера окремо, без моделі (табл. 2)."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON",              "scale_amount",   '{"amount": 300, "base_servings": 4, "target_servings": 10'),
    ("Неправильний тип",           "scale_amount",   '{"amount": "триста", "base_servings": 4, "target_servings": 10}'),
    ("Відсутнє обов'язкове поле",  "scale_amount",   '{"amount": 300, "base_servings": 4}'),
    ("Вигадане поле",              "product_info",   '{"product": "рис", "unit": "кг"}'),
    ("Неіснуючий інструмент",      "delete_all",     '{}'),
    ("Заборонена дія",             "place_order",    '{"items": "рис, курка"}'),
    ("Значення немає в довіднику", "product_info",   '{"product": "ваніль"}'),
    ("Значення поза межами",       "scale_amount",   '{"amount": 300, "base_servings": 0, "target_servings": 10}'),
    # додаткові випадки
    ("Порожній запит (межа в класі)", "search_recipes", '{"query": ""}'),
    ("Запит із 3+ слів",           "search_recipes", '{"query": "стейк з тунця"}'),
    ("Помилка в назві продукту",   "product_info",   '{"product": "рису"}'),
    ("Усе гаразд",                 "scale_amount",   '{"amount": 300, "base_servings": 4, "target_servings": 10}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{title}]\n  виклик : {name}({raw})\n  рівень : {level}\n  текст  : {text}\n")
