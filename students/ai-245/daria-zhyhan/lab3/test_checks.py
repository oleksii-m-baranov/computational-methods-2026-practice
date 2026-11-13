"""Перевірка ланцюжка перевірок диспетчера без виклику моделі."""

from dispatcher import call_tool

cases = [
    ("calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5'),            # 1. Зламаний JSON
    ("calc_dose", '{"pot_liters": "три", "dose_ml_per_liter": 5}'),        # 2. Неправильний тип
    ("calc_dose", '{"pot_liters": 3}'),                                    # 3. Відсутнє обов'язкове поле
    ("calc_dose", '{"pot_liters": 3, "dose_ml_per_liter": 5, "x": 1}'),    # 4. Вигадане поле
    ("delete_all", '{}'),                                                  # 5. Неіснуючий інструмент
    ("order_fertilizer", '{"plant": "Фікус", "amount_ml": 15}'),           # 6. Заборонена дія
    ("fertilizer_info", '{"plant": "Кактус сагуаро"}'),                    # 7. Значення немає в довіднику
    ("calc_dose", '{"pot_liters": -2, "dose_ml_per_liter": 5}'),           # 8. Значення поза межами
]

for name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"{level:10} | {text}\n")