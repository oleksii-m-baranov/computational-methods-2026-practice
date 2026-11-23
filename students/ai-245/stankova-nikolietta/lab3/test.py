from dispatcher import call_tool

cases = [
    ("fertilizer_info", '{"plant":"Фікус Смарагдовий"'),          # зламаний JSON
    ("calc_dose", '{"pot_liters":"три","dose_ml_per_liter":5}'), # неправильний тип
    ("calc_dose", '{"pot_liters":3}'),                           # немає поля
    ("calc_dose", '{"pot_liters":3,"dose_ml_per_liter":5,"x":1}'), # вигадане поле
    ("delete_all", '{}'),                                        # неіснуючий інструмент
    ("order_fertilizer", '{"plant":"Фікус Смарагдовий"}'),       # заборонена дія
    ("fertilizer_info", '{"plant":"Спатифілум"}'),               # немає в довіднику
    ("calc_dose", '{"pot_liters":500,"dose_ml_per_liter":5}')    # поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)

    print("=" * 80)
    print("Виклик:", name)
    print("Рівень:", level)
    print("Повідомлення:")
    print(text)
    