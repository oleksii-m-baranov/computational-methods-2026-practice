from dispatcher import call_tool

cases = [
    ("calc_price", '{"weight": 15, "price_per_kg": 18, "min_price": 70'),   # Зламаний JSON
    ("calc_price", '{"weight": "сто", "price_per_kg": 18, "min_price": 70}'),   # Неправильний тип
    ("calc_price", '{"weight": 15, "price_per_kg": 18}'),   # Відсутнє обов'язкове поле
    ("calc_price", '{"weight": 15, "price_per_kg": 18, "min_price": 70, "x": 1}'),   # Вигадане поле
    ("delete_all", '{}'),   # Неіснуючий інструмент
    ("cancel_parcel", '{"parcel_id": "UA12345"}'),   # Заборонена дія
    ("tariff_info", '{"city": "Мадрид"}'),   # Значення немає в довіднику
    ("calc_price", '{"weight": 45, "price_per_kg": 18, "min_price": 70}'),   # Значення поза межами
    ("tariff_info", '{"city": "Львова"}'),   # Не той відмінок
    ("search_rules", '{"query": ""}'),   # Порожній запит
    ("calc_price", '{"weight": 15, "price_per_kg": 18, "min_price": 70}'),   # Правильний виклик
]

# підписи для таблиці звіту (перші 8 — рядки табл. 2 методички)
LABELS = ["Зламаний JSON", "Неправильний тип", "Відсутнє обов'язкове поле", "Вигадане поле", "Неіснуючий інструмент", "Заборонена дія", "Значення немає в довіднику", "Значення поза межами", "Не той відмінок", "Порожній запит", "Правильний виклик"]


if __name__ == "__main__":
    for name, raw in cases:
        level, text = call_tool(name, raw)
        print(f"{level:10} | {text}\n")
