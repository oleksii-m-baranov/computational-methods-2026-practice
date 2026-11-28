"""Перевірка ланцюжка перевірок диспетчера без звернення до моделі."""
import json

from dispatcher import call_tool
from schemas import SCHEMAS

cases = [
    ("Зламаний JSON", "calc_materials", '{"area": 18.5, "coverage_m2": 5.3, "price":'),
    ("Неправильний тип", "calc_materials", '{"area": "вісімнадцять", "coverage_m2": 5.3, "price": 485}'),
    ("Відсутнє обов'язкове поле", "calc_materials", '{"area": 18.5, "coverage_m2": 5.3}'),
    ("Вигадане поле", "material_info", '{"material": "ламінат", "room": "спальня"}'),
    ("Неіснуючий інструмент", "call_master", '{"date": "завтра"}'),
    ("Заборонена дія", "place_order", '{"material": "керамічна плитка", "quantity": 7}'),
    ("Значення немає в довіднику", "material_info", '{"material": "силіконовий герметик"}'),
    ("Значення поза межами", "calc_materials", '{"area": -12, "coverage_m2": 5.3, "price": 485}'),
]

print("=== SCHEMAS[0] ===")
print(json.dumps(SCHEMAS[0], ensure_ascii=False, indent=2))
print("\n=== TEST CHECKS ===")
for label, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{label}] -> level={level} | {text}\n")
