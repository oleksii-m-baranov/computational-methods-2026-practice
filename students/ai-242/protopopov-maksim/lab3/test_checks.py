from dispatcher import call_tool

cases = [
    ("fertilizer_info", '{"plant": "Фікус Бенджаміна"'),                        # зламаний JSON
    ("calc_dose", '{"pot_liters": "три", "dose_ml_per_liter": 5}'),             # неправильний тип
    ("fertilizer_info", '{}'),                                                  # відсутнє обов'язкове поле
    ("fertilizer_info", '{"plant": "Фікус Бенджаміна", "x": 1}'),               # вигадане поле
    ("delete_all", '{}'),                                                       # неіснуючий інструмент
    ("order_fertilizer", '{"plant": "Фікус Бенджаміна", "amount_ml": 50}'),     # заборонена дія
    ("fertilizer_info", '{"plant": "Неіснуюча рослина"}'),                      # значення немає в довіднику
    ("calc_dose", '{"pot_liters": -3, "dose_ml_per_liter": 5}'),                # значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")