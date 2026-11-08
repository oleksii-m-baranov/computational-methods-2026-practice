"""Перевірка ланцюжка перевірок без моделі."""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dispatcher import call_tool

cases = [
    # Зламаний JSON
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5'),
    # Неправильний тип
    ("calc_calories", '{"minutes": "сорок п\'ять", "weight_kg": 70, "met": 5}'),
    # Відсутнє обов'язкове поле
    ("calc_calories", '{"minutes": 45}'),
    # Вигадане поле
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5, "wear": 1}'),
    # Неіснуючий інструмент
    ("delete_user", '{}'),
    # Заборонена дія
    ("book_session", '{"activity": "йога", "day": "вівторок"}'),
    # Значення немає в довіднику
    ("schedule_info", '{"activity": "бокс"}'),
    # Значення поза межами (межа задана в класі)
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 99}'),
    # Значення немає сенсу для даних (правило в check_meaning)
    ("search_exercises", '{"query": "підбери вправи для плавання й скажи коли басейн"}'),
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")
