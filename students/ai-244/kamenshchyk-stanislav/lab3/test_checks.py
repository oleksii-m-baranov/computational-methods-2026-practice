"""Перевірка ланцюжка перевірок диспетчера без моделі (варіант 8)."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON",              "calc_total",     '{"work_price": 400, "part_price": 250, "quantity": 4'),
    ("Неправильний тип",           "calc_total",     '{"work_price": "дорого", "part_price": 250, "quantity": 4}'),
    ("Відсутнє обов'язкове поле",  "calc_total",     '{"work_price": 400, "part_price": 250}'),
    ("Вигадане поле",              "calc_total",     '{"work_price": 400, "part_price": 250, "quantity": 4, "discount": 10}'),
    ("Неіснуючий інструмент",      "delete_history", '{}'),
    ("Заборонена дія",             "book_service",   '{"service": "заміна масла"}'),
    ("Значення немає в довіднику", "price_info",     '{"service": "заміна батареї на електромобілі"}'),
    ("Значення поза межами",       "calc_total",     '{"work_price": 0, "part_price": 250, "quantity": 4}'),
    ("Вигадана ціна деталі",       "calc_total",     '{"work_price": 400, "part_price": 25, "quantity": 4}'),
    ("Коректний виклик",           "calc_total",     '{"work_price": 400, "part_price": 250, "quantity": 4}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{title}] {name}({raw})")
    print(f"{level:10} | {text}\n")
    