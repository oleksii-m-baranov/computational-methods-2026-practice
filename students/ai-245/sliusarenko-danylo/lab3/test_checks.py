"""Перевірка ланцюжка перевірок диспетчера на 8 випадках."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON", "calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5'),
    ("Неправильний тип", "calc_calories", '{"minutes": "сорок", "weight_kg": 70, "met": 5}'),
    ("Відсутнє обов'язкове поле", "calc_calories", '{"minutes": 45, "weight_kg": 70}'),
    ("Вигадане поле", "calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5, "extra": 1}'),
    ("Неіснуючий інструмент", "delete_all", '{}'),
    ("Заборонена дія", "book_session", '{"activity": "йога", "weekday": "середа"}'),
    ("Значення немає в довіднику", "schedule_info", '{"activity": "плавання"}'),
    ("Значення поза межами", "calc_calories", '{"minutes": -10, "weight_kg": 70, "met": 5}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"=== {title} ===")
    print(f"Виклик : {name}({raw})")
    print(f"Рівень : {level}")
    print(f"Текст  : {text}\n")