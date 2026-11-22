from dispatcher import call_tool

cases = [
    ("Зламаний JSON", "calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5'),
    ("Неправильний тип", "calc_dose", '{"pot_liters": "три", "dose_ml_per_liter": 5}'),
    ("Відсутнє обов'язкове поле", "calc_dose", '{"pot_liters": 3}'),
    ("Вигадане поле", "fertilizer_info", '{"plant": "Фікус Бенджаміна", "season": "весна"}'),
    ("Неіснуючий інструмент", "water_plant", '{"plant": "Фікус Бенджаміна"}'),
    ("Заборонена дія", "order_fertilizer", '{"plant": "Фікус Бенджаміна"}'),
    ("Значення немає в довіднику", "fertilizer_info", '{"plant": "фікус"}'),
    ("Значення поза межами", "calc_dose", '{"pot_liters": -5, "dose_ml_per_liter": 5}'),
]

for label, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{label}] -> level={level} | call={name}({raw})")
    print(f"   msg: {text}\n")