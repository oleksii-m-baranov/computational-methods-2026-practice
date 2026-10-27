"""Перевірка кожної перевірки диспетчера окремо, без моделі."""
from dispatcher import call_tool

cases = [
    # (що перевіряємо, інструмент, аргументи так, як їх передає модель)
    ("Зламаний JSON",              "calc_installment", '{"price": 18500, "months": 6, "overpay_percent": 10'),
    ("Неправильний тип",           "calc_installment", '{"price": "дорого", "months": 6, "overpay_percent": 10}'),
    ("Відсутнє обов'язкове поле",  "calc_installment", '{"price": 18500, "months": 6}'),
    ("Вигадане поле",              "calc_installment", '{"price": 18500, "months": 6, "overpay_percent": 10, "x": 1}'),
    ("Неіснуючий інструмент",      "delete_all",       '{}'),
    ("Заборонена дія",             "place_order",      '{"model": "Nexora StudyTab 13"}'),
    ("Значення немає в довіднику", "laptop_info",      '{"model": "PrismCraft Duo 16"}'),
    ("Значення поза межами",       "calc_installment", '{"price": 18500, "months": 0, "overpay_percent": 10}'),
    # додаткові випадки
    ("Вигадана ціна",              "calc_installment", '{"price": 10000, "months": 6, "overpay_percent": 10}'),
    ("Нецілі місяці",              "calc_installment", '{"price": 18500, "months": 6.5, "overpay_percent": 10}'),
    ("Порожній запит",             "search_laptops",   '{"query": ""}'),
    ("Контроль: усе гаразд",       "calc_installment", '{"price": 18500, "months": 6, "overpay_percent": 10}'),
    ("Контроль: регістр назви",    "laptop_info",      '{"model": "nexora studytab 13"}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{title}] {name}({raw})")
    print(f"{level:10} | {text}\n")
