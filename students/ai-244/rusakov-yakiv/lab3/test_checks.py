"""Крок 5: перевірка кожної перевірки диспетчера окремо, без моделі."""
from dispatcher import call_tool

cases = [
    ("Зламаний JSON",              "calc_total",     '{"work_price": 400, "part_price": 250, "quantity": 4'),
    ("Неправильний тип",           "calc_total",     '{"work_price": "чотириста", "part_price": 250, "quantity": 4}'),
    ("Відсутнє обов'язкове поле",  "price_info",     '{}'),
    ("Вигадане поле",              "price_info",     '{"service": "заміна масла", "color": "red"}'),
    ("Неіснуючий інструмент",      "delete_all",     '{}'),
    ("Заборонена дія",             "book_service",   '{"service": "заміна масла"}'),
    ("Значення немає в довіднику", "price_info",     '{"service": "заміна батареї електромобіля"}'),
    ("Значення поза межами",       "calc_total",     '{"work_price": 400, "part_price": 250, "quantity": -4}'),
    ("Ціни не з прайсу (кілька аргументів)", "calc_total", '{"work_price": 500, "part_price": 300, "quantity": 4}'),
    ("Усе гаразд",                 "calc_total",     '{"work_price": 400, "part_price": 250, "quantity": 4}'),
]

for title, name, raw in cases:
    level, text = call_tool(name, raw)
    print(f"[{title}]\n{name}({raw})\n{level:10} | {text}\n")
