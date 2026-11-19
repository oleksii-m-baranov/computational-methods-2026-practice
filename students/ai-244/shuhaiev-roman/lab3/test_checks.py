"""Перевірка ланцюжка перевірок диспетчера без моделі (табл. 2)."""
import json

from dispatcher import call_tool

cases = [
    ("Зламаний JSON", "calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5'),
    ("Неправильний тип", "calc_calories", '{"minutes": "сорок п\'ять", "weight_kg": 70, "met": 5}'),
    ("Відсутнє обов'язкове поле", "calc_calories", '{"minutes": 45, "weight_kg": 70}'),
    ("Вигадане поле", "schedule_info", '{"activity": "йога", "day": "середа"}'),
    ("Неіснуючий інструмент", "delete_all", '{}'),
    ("Заборонена дія", "book_session", '{"activity": "йога", "weekday": "середа"}'),
    ("Значення немає в довіднику", "schedule_info", '{"activity": "басейн"}'),
    ("Значення поза межами", "calc_calories", '{"minutes": 45, "weight_kg": 700, "met": 5}'),
    ("Не той регістр (зміст)", "schedule_info", '{"activity": "Йога"}'),
    ("Задовгий запит (зміст)", "search_exercises", '{"query": "які є вправи на спину"}'),
    ("Коректний виклик", "calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5}'),
]

import os
os.makedirs("results", exist_ok=True)

rows = []
for what, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{what}\n  {name}({raw})\n  {level:10} | {text}\n")
    rows.append({"what": what, "call": f"{name}({raw})", "level": level, "text": text})

with open("results/test_checks.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
