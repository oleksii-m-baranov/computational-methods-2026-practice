from dispatcher import call_tool

cases = [
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5'),             # зламаний JSON
    ("calc_calories", '{"minutes": "сорок п\'ять", "weight_kg": 70, "met": 5}'), # неправильний тип
    ("calc_calories", '{"minutes": 45, "weight_kg": 70}'),                      # немає met
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5, "x": 1}'),    # вигадане поле
    ("delete_all", '{}'),                                                       # неіснуючий інструмент
    ("book_session", '{"activity": "йога"}'),                                   # заборонена дія
    ("schedule_info", '{"activity": "плавання"}'),                              # немає в довіднику
    ("calc_calories", '{"minutes": -5, "weight_kg": 70, "met": 5}'),            # поза межами
    ("schedule_info", '{"activity": "йога"}'),                                  # контроль: ok
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")