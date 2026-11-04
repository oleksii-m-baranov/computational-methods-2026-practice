from dispatcher import call_tool

cases = [
    ("calc_dose", '{"pot_liters": 5, "dose_ml_per_liter": 2'),           # зламаний JSON
    ("calc_dose", '{"pot_liters": "п\'ять", "dose_ml_per_liter": 2}'),    # неправильний тип
    ("calc_dose", '{"pot_liters": 5}'),                                  # немає поля
    ("calc_dose", '{"pot_liters": 5, "dose_ml_per_liter": 2, "x": 1}'),  # вигадане поле
    ("water_plants", '{}'),                                              # неіснуючий інструмент
    ("order_fertilizer", '{"plant": "фікус"}'),                          # заборонена дія
    ("fertilizer_info", '{"plant": "баобаб"}'),                          # значення немає в довіднику
    ("calc_dose", '{"pot_liters": -5, "dose_ml_per_liter": 2}'),         # значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")