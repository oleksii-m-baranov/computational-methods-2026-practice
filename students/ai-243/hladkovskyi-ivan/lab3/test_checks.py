"""Перевірка ланцюжка перевірок без моделі: по одному виклику на рядок табл. 2."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON",             "transport_info", '{"route": "Одеса"'),
    ("Неправильний тип",          "calc_budget",    '{"price_per_person": "триста", "people": 3, "extra": 0}'),
    ("Відсутнє поле",             "calc_budget",    '{"price_per_person": 420, "people": 3}'),
    ("Вигадане поле",             "transport_info", '{"route": "Одеса", "date": "субота"}'),
    ("Неіснуючий інструмент",     "delete_all",     '{}'),
    ("Заборонена дія",            "buy_ticket",     '{"route": "Одеса"}'),
    ("Значення не в довіднику",   "transport_info", '{"route": "Кам\'янць-Подільський"}'),
    ("Значення поза межами",      "calc_budget",    '{"price_per_person": 420, "people": -3, "extra": 0}'),
    # контрольні: правильні виклики мають пройти до рівня ok
    ("OK: довідник",              "transport_info", '{"route": "Кам\'янець-Подільський"}'),
    ("OK: калькулятор",           "calc_budget",    '{"price_per_person": 420, "people": 3, "extra": 500}'),
]

for label, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{label}]\n  виклик : {name}({raw})\n  рівень : {level}\n  текст  : {text}\n")
