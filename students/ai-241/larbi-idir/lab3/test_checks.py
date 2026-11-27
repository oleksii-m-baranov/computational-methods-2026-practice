from dispatcher import call_tool

cases = [
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5'),              # 1. Зламаний JSON
    ("calc_calories", '{"minutes": "сорок", "weight_kg": 70, "met": 5}'),        # 2. Неправильний тип
    ("calc_calories", '{"minutes": 45, "weight_kg": 70}'),                       # 3. Відсутнє обов'язкове поле
    ("calc_calories", '{"minutes": 45, "weight_kg": 70, "met": 5, "x": 1}'),     # 4. Вигадане поле
    ("delete_all", "{}"),                                                        # 5. Неіснуючий інструмент
    ("book_session", '{"activity": "йога"}'),                                    # 6. Заборонена дія
    ("schedule_info", '{"activity": "басейн"}'),                                 # 7. Значення немає в довіднику
    ("calc_calories", '{"minutes": -15, "weight_kg": 70, "met": 5}'),            # 8. Значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")