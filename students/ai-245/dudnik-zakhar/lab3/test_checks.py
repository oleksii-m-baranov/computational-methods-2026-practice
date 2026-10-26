from dispatcher import call_tool

cases = [
    ("calc_calories",    '{"minutes": 30, "weight_kg": 70',                    # зламаний JSON
    ),
    ("calc_calories",    '{"minutes": "багато", "weight_kg": 70, "met": 5}',  # неправильний тип
    ),
    ("calc_calories",    '{"minutes": 30, "weight_kg": 70}',                  # відсутнє обов'язкове поле
    ),
    ("search_exercises", '{"query": "спина", "difficulty": "легко"}',          # вигадане поле
    ),
    ("convert_currency", '{"amount": 100}',                                    # неіснуючий інструмент
    ),
    ("book_session",     '{"booking_id": "123"}',                              # заборонена дія
    ),
    ("schedule_info",    '{"title": "підводне поло"}',                         # значення немає в довіднику
    ),
    ("calc_calories",    '{"minutes": 30, "weight_kg": 0, "met": 5}',          # значення поза межами
    ),
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")