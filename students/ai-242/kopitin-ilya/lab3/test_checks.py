from dispatcher import call_tool

cases = [
    ("calc_total", '{"work_price": 400, "part_price": 250, "quantity": 4'),   # Зламаний JSON
    ("calc_total", '{"work_price": "сто", "part_price": 250, "quantity": 4}'),   # Неправильний тип
    ("calc_total", '{"work_price": 400, "part_price": 250}'),   # Відсутнє обов'язкове поле
    ("calc_total", '{"work_price": 400, "part_price": 250, "quantity": 4, "x": 1}'),   # Вигадане поле
    ("delete_all", '{}'),   # Неіснуючий інструмент
    ("book_service", '{"date_time": "завтра о 10:00"}'),   # Заборонена дія
    ("price_info", '{"service": "діагностика електрообладнання"}'),   # Значення немає в довіднику
    ("calc_total", '{"work_price": -400, "part_price": 250, "quantity": 4}'),   # Значення поза межами
    ("price_info", '{"service": "заміни масла"}'),   # Не той відмінок
    ("search_service", '{"query": ""}'),   # Порожній запит
    ("calc_total", '{"work_price": 400, "part_price": 250, "quantity": 4}'),   # Правильний виклик
]

# підписи для таблиці звіту (перші 8 — рядки табл. 2 методички)
LABELS = ["Зламаний JSON", "Неправильний тип", "Відсутнє обов'язкове поле", "Вигадане поле", "Неіснуючий інструмент", "Заборонена дія", "Значення немає в довіднику", "Значення поза межами", "Не той відмінок", "Порожній запит", "Правильний виклик"]


if __name__ == "__main__":
    for name, raw in cases:
        level, text = call_tool(name, raw)
        print(f"{level:10} | {text}\n")
