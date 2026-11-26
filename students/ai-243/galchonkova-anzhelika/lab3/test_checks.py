"""Перевірка ланцюжка перевірок без виклику моделі."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON", "calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5'),
    ("Неправильний тип", "calc_dose", '{"pot_liters": "три", "dose_ml_per_liter": 5}'),
    ("Відсутнє обов'язкове поле", "calc_dose", '{"pot_liters": 3}'),
    ("Вигадане поле", "calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5, "extra_field": 1}'),
    ("Неіснуючий інструмент", "water_plant", '{}'),
    ("Заборонена дія", "order_fertilizer", '{"plant": "Фікус Бенджаміна", "liters": 1}'),
    ("Значення немає в довіднику", "fertilizer_info", '{"plant": "фікус"}'),
    ("Значення поза межами", "calc_dose", '{"pot_liters": -3, "dose_ml_per_liter": 5}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    one_line = text.replace("\n", " ")
    print(f"{title:28} | {name}({raw}) | {level:10} | {one_line}")
