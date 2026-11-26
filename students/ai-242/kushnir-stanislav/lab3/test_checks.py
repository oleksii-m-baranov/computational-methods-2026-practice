from dispatcher import call_tool

cases = [
    ("calc_installment", '{"price": 27000, "months": 6, "overpay_percent": 10'),   # Зламаний JSON
    ("calc_installment", '{"price": "сто", "months": 6, "overpay_percent": 10}'),   # Неправильний тип
    ("calc_installment", '{"price": 27000, "months": 6}'),   # Відсутнє обов'язкове поле
    ("calc_installment", '{"price": 27000, "months": 6, "overpay_percent": 10, "x": 1}'),   # Вигадане поле
    ("delete_all", '{}'),   # Неіснуючий інструмент
    ("place_order", '{"model": "LearnPad 14"}'),   # Заборонена дія
    ("laptop_info", '{"model": "ColorLab 15"}'),   # Значення немає в довіднику
    ("calc_installment", '{"price": 27000, "months": 0, "overpay_percent": 10}'),   # Значення поза межами
    ("laptop_info", '{"model": "learnpad 14"}'),   # Не та регістрова форма
    ("search_laptops", '{"query": ""}'),   # Порожній запит
    ("laptop_info", '{"model": "ColorLab 15"}'),   # Модель є в корпусі, немає в довіднику
    ("calc_installment", '{"price": 27000, "months": 6, "overpay_percent": 10}'),   # Правильний виклик
]

# підписи для таблиці звіту (перші 8 — рядки табл. 2 методички)
LABELS = ["Зламаний JSON", "Неправильний тип", "Відсутнє обов'язкове поле", "Вигадане поле", "Неіснуючий інструмент", "Заборонена дія", "Значення немає в довіднику", "Значення поза межами", "Не та регістрова форма", "Порожній запит", "Модель є в корпусі, немає в довіднику", "Правильний виклик"]


if __name__ == "__main__":
    for name, raw in cases:
        level, text = call_tool(name, raw)
        print(f"{level:10} | {text}\n")
