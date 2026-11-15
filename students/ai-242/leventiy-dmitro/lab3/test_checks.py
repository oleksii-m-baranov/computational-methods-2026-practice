from dispatcher import call_tool

cases = [
    ("calc_food", '{"weight_kg": 5, "grams_per_kg": 25, "days": 30'),            # зламаний JSON
    ("calc_food", '{"weight_kg": "п\'ять", "grams_per_kg": 25, "days": 30}'),    # неправильний тип
    ("calc_food", '{"weight_kg": 5, "days": 30}'),                               # немає поля
    ("calc_food", '{"weight_kg": 5, "grams_per_kg": 25, "days": 30, "x": 1}'),   # вигадане поле
    ("delete_all", '{}'),                                                        # неіснуючий інструмент
    ("book_vet", '{"date": "п\'ятниця"}'),                                       # заборонена дія
    ("vaccine_info", '{"vaccine": "від сказу та чуми"}'),                        # немає в довіднику
    ("calc_food", '{"weight_kg": 500, "grams_per_kg": 25, "days": 30}'),         # поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {name} {raw}\n           {text}\n")
